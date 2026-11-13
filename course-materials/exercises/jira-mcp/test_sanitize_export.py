"""Sanitization and Markdown/ADF regression tests using invented identities."""
import copy
import json

import pytest

import sanitize_export as sanitizer


def test_scrubs_nested_identities_and_embedded_values_without_mutating_input():
    cloud = '12345678-1234-1234-1234-123456789abc'
    user = {'accountId': 'private-id-123', 'displayName': 'Private Person', 'emailAddress': 'person@example.invalid', 'avatarUrls': {'48x48': 'https://avatar.invalid/private'}, 'timeZone': 'Europe/Warsaw'}
    raw = {'issues': [{'key': 'TEST-1', 'self': f'https://edukey.atlassian.net/rest/api/3/issue/1', 'fields': {'creator': user, 'reporter': copy.deepcopy(user), 'description': 'Contact Private Person private-id-123 person@example.invalid', 'comment': {'comments': [{'body': {'type': 'doc', 'version': 1, 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': r'\[1, 2\]'}]}]}}]}, 'project': {'key': 'TEST', 'name': 'Edukey Internal'}, 'customfield_10000': f'https://api.atlassian.com/ex/jira/{cloud}/rest/api/3/issue/1', 'created': '2026-11-13T08:00:00.000+0000'}}], 'isLast': True}
    original = copy.deepcopy(raw)
    clean = sanitizer.sanitize(raw)
    text = json.dumps(clean)
    for value in ('Private Person', 'private-id-123', 'person@example.invalid', cloud, 'edukey'):
        assert value not in text.lower()
    assert raw == original and clean['isLast'] is True
    fields = clean['issues'][0]['fields']
    assert fields['creator']['accountId'] == fields['reporter']['accountId'] == '712020:course-user-1'
    assert fields['creator']['displayName'] == 'Analityk (kurs)'
    assert fields['creator']['timeZone'] == 'Europe/Warsaw'
    assert 'emailAddress' not in fields['creator']
    assert set(fields['creator']['avatarUrls'].values()) == {'https://example.invalid/avatar.png'}
    assert fields['comment']['comments'][0]['body']['content'][0]['content'][0]['text'] == '[1, 2]'
    assert fields['created'] == original['issues'][0]['fields']['created']


def walk(node):
    yield node
    for child in node.get('content', []):
        yield from walk(child)


def test_markdown_to_adf_preserves_tables_code_lists_and_inline_marks():
    md = '# Zakres\n\n| Parametr | Wartość |\n| --- | --- |\n| bbox | [1, 2, 3, 4] |\n\n- **roads** i *poi* oraz `delta`\n- drugi\n\n1. validation\n2. export\n\n```yaml\nrelease: 2026.11\n```'
    adf = sanitizer.markdown_to_adf(md)
    assert adf['type'] == 'doc' and adf['version'] == 1
    nodes = list(walk(adf))
    assert {'heading', 'table', 'tableHeader', 'tableCell', 'bulletList', 'orderedList', 'codeBlock'} <= {n['type'] for n in nodes}
    assert next(n for n in nodes if n['type'] == 'codeBlock')['attrs']['language'] == 'yaml'
    assert {'strong', 'em', 'code'} <= {m['type'] for n in nodes for m in n.get('marks', [])}
    assert '[1, 2, 3, 4]' in json.dumps(adf)
    assert sanitizer.markdown_to_adf(md.replace('\n', r'\n')) == adf


def test_already_adf_is_preserved_and_sanitization_is_idempotent():
    raw = {'issues': [{'fields': {'description': {'type': 'doc', 'version': 1, 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': 'unchanged'}]}]}}}]}
    assert sanitizer.sanitize(raw) == raw
    assert sanitizer.sanitize(sanitizer.sanitize(raw)) == raw


def test_connector_markdown_comments_are_rest_v3_adf():
    raw = {'issues': [{'fields': {'comment': {'comments': [{'id': '1', 'body': r'**Analyst:** bbox \[1, 2, 3, 4\]'}]}}}]}
    clean = sanitizer.sanitize(raw)
    body = clean['issues'][0]['fields']['comment']['comments'][0]['body']
    assert body['type'] == 'doc' and body['version'] == 1
    assert any(n.get('text') == 'Analyst:' and n.get('marks') == [{'type': 'strong'}] for n in walk(body))
    assert r'\[' not in json.dumps(body)


def test_underscores_inside_identifiers_are_not_emphasis():
    adf = sanitizer.markdown_to_adf('speed_limits and output_path, *review* and _approved_.')
    texts = ''.join(n.get('text', '') for n in walk(adf))
    assert 'speed_limits and output_path' in texts
    assert sum(m['type'] == 'em' for n in walk(adf) for m in n.get('marks', [])) == 2
