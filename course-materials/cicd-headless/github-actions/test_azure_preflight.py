"""Exercise the actual workflow preflight with synthetic credentials and a fake gh."""
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

WORKFLOW = Path(__file__).with_name('pr-agent-azure-review.yml')


def preflight_script():
    lines = WORKFLOW.read_text().splitlines()
    start = lines.index('        run: |') + 1
    end = start
    while end < len(lines) and (not lines[end].strip() or lines[end].startswith('          ')):
        end += 1
    return textwrap.dedent('\n'.join(lines[start:end]))


class AzurePreflightContracts(unittest.TestCase):
    def run_preflight(self, overrides=None, metadata='open\ttraining/demo\tfalse'):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            gh = root / 'gh'
            gh.write_text('#!/bin/bash\nprintf called > "$FAKE_GH_CALLED"\nif [[ "$2" == */permission ]]; then printf "%s\\n" "$FAKE_PERMISSION"; else printf "%s\\n" "$FAKE_METADATA"; fi\n')
            gh.chmod(0o700)
            env = {'PATH': str(root) + ':' + os.defpath,
                   'OPENAI__KEY': 'synthetic-never-log-this-key',
                   'OPENAI__API_BASE': 'https://training.openai.azure.com',
                   'OPENAI__DEPLOYMENT_ID': 'training-luna', 'CONFIG__MODEL': 'gpt-6-luna',
                   'CONFIG__MAX_MODEL_TOKENS': '250000',
                   'PR_NUMBER': '7', 'GITHUB_REPOSITORY': 'training/demo',
                   'GITHUB_OUTPUT': str(root / 'output'), 'FAKE_METADATA': metadata,
                   'FAKE_GH_CALLED': str(root / 'called'), 'FAKE_PERMISSION': 'write',
                   'GITHUB_EVENT_NAME': 'workflow_dispatch', 'COMMENT_LOGIN': 'reviewer'}
            env.update(overrides or {})
            result = subprocess.run(['bash', '-c', preflight_script()], env=env,
                                    text=True, capture_output=True)
            called = (root / 'called').exists()
            output = (root / 'output').read_text() if (root / 'output').exists() else ''
            self.assertNotIn('synthetic-never-log-this-key', result.stdout + result.stderr + output)
            return result, called, output

    def test_missing_credentials_and_variables_fail_before_any_api_request(self):
        for name in ('OPENAI__KEY', 'OPENAI__API_BASE', 'OPENAI__DEPLOYMENT_ID', 'CONFIG__MODEL'):
            with self.subTest(name=name):
                result, called, output = self.run_preflight({name: ''})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('::error::Set Actions', result.stderr)
                self.assertFalse(called)
                self.assertEqual(output, '')

    def test_invalid_endpoint_and_pr_number_fail_before_any_api_request(self):
        for overrides in ({'OPENAI__API_BASE': 'https://training.openai.azure.com/openai/v1'},
                          {'OPENAI__API_BASE': 'https://attacker.invalid'},
                          {'PR_NUMBER': '7; echo injected'}):
            with self.subTest(overrides=overrides):
                result, called, _ = self.run_preflight(overrides)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(called)

    def test_token_budget_must_be_a_number_within_the_model_context_window(self):
        for value in ('1050001', '9999999', '999', 'lots', ''):
            with self.subTest(value=value):
                result, called, _ = self.run_preflight({'CONFIG__MAX_MODEL_TOKENS': value})
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(called)
        for value in ('32000', '250000', '1050000'):
            result, _, _ = self.run_preflight({'CONFIG__MAX_MODEL_TOKENS': value})
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_comment_commands_require_current_write_maintain_or_admin_permission(self):
        for permission in ('read', 'triage', 'none'):
            with self.subTest(permission=permission):
                result, _, output = self.run_preflight({
                    'GITHUB_EVENT_NAME': 'issue_comment', 'FAKE_PERMISSION': permission})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('permission', result.stderr)
                self.assertEqual(output, '')
        for permission in ('write', 'maintain', 'admin'):
            result, _, _ = self.run_preflight({
                'GITHUB_EVENT_NAME': 'issue_comment', 'FAKE_PERMISSION': permission})
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_only_open_non_draft_same_repository_prs_produce_a_url(self):
        for metadata in ('closed\ttraining/demo\tfalse', 'open\tfork/demo\tfalse',
                         'open\ttraining/demo\ttrue'):
            with self.subTest(metadata=metadata):
                result, called, output = self.run_preflight(metadata=metadata)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(called)
                self.assertEqual(output, '')
        result, called, output = self.run_preflight()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(called)
        self.assertEqual(output, 'pr_url=https://github.com/training/demo/pull/7\n')


if __name__ == '__main__':
    unittest.main()
