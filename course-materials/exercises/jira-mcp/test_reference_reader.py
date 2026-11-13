"""Read references from the actual offline snapshot; no API response mocks."""
import pytest

import jira_read as reader


def test_list_search_and_get_confluence_pages():
    with reader.OfflineReader() as api:
        assert len(api.search_pages('')) == 5
        hits = api.search_pages('KONWENCJE parametrów')
        assert '220135425' in [p['id'] for p in hits]
        assert api.search_pages('brak-nieistniejącej-frazy') == []
        page = api.get_page('220135425')
        assert page['parentId'] == '220102657'
        assert page['body']['storage']['value']
        assert api.search_pages('TEST-99')
        page['title'] = 'changed'
        assert api.get_page('220135425')['title'] != 'changed'


@pytest.mark.parametrize('page_id', ['999999', '../../tickets.json', 'https://example.invalid'])
def test_invalid_or_missing_page_id(page_id):
    with reader.OfflineReader() as api, pytest.raises(ValueError):
        api.get_page(page_id)


def test_reference_cli_offline_and_env(capsys):
    assert reader.main(['--offline', 'pages', 'konwencje'], env={}) == 0
    assert '220135425' in capsys.readouterr().out
    assert reader.main(['page', '220135425'], env={'JIRA_OFFLINE': '1'}) == 0
    text = capsys.readouterr().out
    assert 'Konwencje parametrów' in text and 'TEST-1' in text
    assert 'course-site.atlassian.net' in text
    assert reader.main(['--offline', 'page', '999999'], env={}) == 1
    assert 'Nie znaleziono strony' in capsys.readouterr().err


def test_reference_cli_rejects_live_without_request_or_credentials(capsys):
    for args in [['pages'], ['page','220135425'], ['prs'], ['pr','1']]:
        assert reader.main(args, env={}) == 1
        assert 'offline' in capsys.readouterr().err


def test_ticket_metadata_visible_for_calendar_conflicts(capsys):
    assert reader.main(['--offline', 'get', 'TEST-6'], env={}) == 0
    text = capsys.readouterr().out
    assert 'Medium' in text and '2026-11-19' in text and '2026-11-17' in text


def test_pr_reader_keeps_rest_resources_and_searches_all_evidence():
    with reader.OfflineReader() as api:
        prs = api.list_prs()
        assert len(prs) == 10
        pr = api.get_pr(1)
        assert isinstance(pr['pr']['commits'], int)
        assert isinstance(pr['commits'], list) and pr['commits'][0]['commit']['message']
        assert isinstance(pr['pr']['comments'], int)
        assert pr['review_comments'][0]['id'] == 4559055426
        for query, number in [('test-12-osm-wk46', 3), ('TEST-18', 4), ('TSET-15', 5), ('zasłoniętego TEST-29', 1), ('2026.10 sl-461.yaml', 10)]:
            assert number in [item['pr']['number'] for item in api.list_prs(query)]
        assert api.list_prs('nieistniejąca-fraza-xyz') == []
        pr['pr']['title'] = 'changed'
        assert api.get_pr(1)['pr']['title'] != 'changed'


@pytest.mark.parametrize('number', ['9999', '../../tickets.json', '0', '-1', '1.0'])
def test_invalid_or_missing_pr(number):
    with reader.OfflineReader() as api, pytest.raises(ValueError):
        api.get_pr(number)


def test_pr_cli_exposes_commits_review_comments_and_diff(capsys):
    assert reader.main(['--offline', 'prs'], env={}) == 0
    assert 'Liczba PR: 10' in capsys.readouterr().out
    assert reader.main(['--offline', 'pr', '10'], env={}) == 0
    text = capsys.readouterr().out
    assert '2026.10' in text and 'jobs/sl-461.yaml' in text and '4559055746' in text
    assert '1f2f109e' in text
    assert reader.main(['--offline', 'pr', '9999'], env={}) == 1
    assert 'Nie znaleziono PR' in capsys.readouterr().err
