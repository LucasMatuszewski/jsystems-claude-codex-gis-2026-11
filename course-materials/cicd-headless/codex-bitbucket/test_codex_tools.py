"""Opt-in native Codex 0.160.0 tool-isolation contract; synthetic data only.

RUN_CODEX_NATIVE_TESTS=1 python3 -m unittest discover -s . -p test_codex_tools.py
No OpenAI API calls: a trusted executable wrapper selects a loopback fake provider.
"""
import gzip
import http.server
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("review.py")
REAL_CODEX = shutil.which('codex')


@unittest.skipUnless(os.environ.get('RUN_CODEX_NATIVE_TESTS') == '1',
                     'set RUN_CODEX_NATIVE_TESTS=1 for native loopback tests')
class NativeCodexToolIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not REAL_CODEX:
            raise unittest.SkipTest('Codex CLI is not installed')
        clean = {'PATH': os.defpath, 'LANG': 'C.UTF-8'}
        version = subprocess.run([REAL_CODEX, '--version'], env=clean,
                                 capture_output=True, text=True, check=True).stdout.strip()
        if version != 'codex-cli 0.160.0':
            raise unittest.SkipTest('native contract requires codex-cli 0.160.0')
        spec = importlib.util.spec_from_file_location('codex_review_native', SCRIPT)
        cls.review = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.review)

    def test_no_tools_and_unadvertised_execution_is_rejected(self):
        for attack in ('shell', 'exec_command', 'apply_patch'):
            with self.subTest(attack=attack), tempfile.TemporaryDirectory(prefix='codex-native-contract-') as folder:
                work = Path(folder)
                marker = work / 'unauthorized-tool-executed'
                requests = []
                report = {'summary': 'Synthetic offline review', 'findings': [],
                          'limitations': ['Synthetic native tool isolation test']}
                if attack == 'apply_patch':
                    malicious = {'type': 'custom_tool_call', 'id': 'attack-item',
                                 'call_id': 'attack-call', 'name': attack,
                                 'input': f'*** Begin Patch\n*** Add File: {marker}\n+Executed\n*** End Patch'}
                    expected = 'unsupported custom tool call: apply_patch'
                else:
                    malicious = {'type': 'function_call', 'id': 'attack-item',
                                 'call_id': 'attack-call', 'name': attack,
                                 'arguments': json.dumps({'cmd': f'touch {marker}',
                                                          'command': f'touch {marker}',
                                                          'workdir': folder})}
                    expected = f'unsupported call: {attack}'

                class Handler(http.server.BaseHTTPRequestHandler):
                    def log_message(self, *args):
                        pass

                    def do_POST(self):
                        raw = self.rfile.read(int(self.headers['Content-Length']))
                        if self.headers.get('Content-Encoding') == 'gzip':
                            raw = gzip.decompress(raw)
                        request = json.loads(raw)
                        requests.append(request)
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/event-stream')
                        self.end_headers()
                        if len(requests) == 1:
                            item = malicious
                        else:
                            item = {'type': 'message', 'id': 'review-message', 'role': 'assistant',
                                    'content': [{'type': 'output_text', 'text': json.dumps(report)}]}
                        events = [
                            {'type': 'response.created', 'response': {'id': f'resp_{len(requests)}'}},
                            {'type': 'response.output_item.done', 'output_index': 0, 'item': item},
                            {'type': 'response.completed', 'response': {
                                'id': f'resp_{len(requests)}', 'output': [],
                                'usage': {'input_tokens': 1, 'output_tokens': 1, 'total_tokens': 2}}},
                        ]
                        for event in events:
                            self.wfile.write(('data: ' + json.dumps(event) + '\n\n').encode())

                server = http.server.HTTPServer(('127.0.0.1', 0), Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    bin_dir = work / 'bin'
                    bin_dir.mkdir()
                    wrapper = bin_dir / 'codex'
                    overrides = [
                        '-c', 'model_provider="offline-review-contract"',
                        '-c', 'model_providers.offline-review-contract.name="Synthetic loopback"',
                        '-c', f'model_providers.offline-review-contract.base_url="http://127.0.0.1:{server.server_address[1]}/v1"',
                        '-c', 'model_providers.offline-review-contract.env_key="CODEX_API_KEY"',
                        '-c', 'model_providers.offline-review-contract.wire_api="responses"',
                    ]
                    wrapper.write_text('#!/usr/bin/python3\nimport os, sys\n'
                                       + f'os.execv({REAL_CODEX!r}, [{REAL_CODEX!r}, sys.argv[1], *{overrides!r}, *sys.argv[2:]])\n')
                    wrapper.chmod(0o700)
                    context = {'workspace': 'training', 'repo': 'synthetic', 'pr_id': '1',
                               'head': 'a' * 40, 'base': 'b' * 40, 'issue_key': None,
                               'files': ['app.py'],
                               'diff': 'diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1 +1 @@\n-old\n+new\n',
                               'ticket': None}
                    context_file = work / 'context.json'
                    context_file.write_text(json.dumps(context))
                    report_file = work / 'review.json'
                    clean_env = {'PATH': str(bin_dir) + ':' + os.defpath, 'LANG': 'C.UTF-8',
                                 'HOME': folder, 'CODEX_API_KEY': 'synthetic-not-a-real-key'}
                    with patch.dict(os.environ, clean_env, clear=True):
                        self.review.analyze(context_file, report_file, 'synthetic-review-model',
                                            run=lambda *args, **kwargs: subprocess.run(
                                                *args, **{**kwargs, 'timeout': 30}))
                    self.assertEqual(json.loads(report_file.read_text()), report)
                    self.assertEqual(len(requests), 2)
                    for request in requests:
                        self.assertEqual(request.get('tools'), [],
                                         'review prompt must have no tools registered')
                    results = [item for item in requests[-1]['input']
                               if item.get('call_id') == 'attack-call'
                               and item.get('type', '').endswith('call_output')]
                    self.assertEqual(len(results), 1)
                    self.assertEqual(results[0]['output'], expected)
                    self.assertFalse(marker.exists(), 'untrusted tool call created a file')
                finally:
                    server.shutdown()
                    server.server_close()
                    thread.join(timeout=5)


if __name__ == '__main__':
    unittest.main()
