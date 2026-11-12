"""Testy kontraktu narzędzi na syntetycznym, lokalnym zbiorze."""

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def server():
    path = Path(__file__).with_name("server.py")
    spec = importlib.util.spec_from_file_location("jira_jobs_server", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_discovery_is_complete(server):
    lines = server.search_tickets("").splitlines()
    assert len(lines) == 36
    assert lines[0].startswith("MAPJOB-101 |")
    assert lines[-1].startswith("MAPJOB-136 |")


@pytest.mark.parametrize("query,key", [
    ("PILOT-ZEFIR MAPJOB-105", "MAPJOB-105"),
    ("OSTATECZNE POTWIERDZENIE MAPJOB-106", "MAPJOB-106"),
])
def test_search_matches_comments_and_all_words_case_insensitively(server, query, key):
    result = server.search_tickets(query)
    assert result.startswith(f"{key} |")
    assert len(result.splitlines()) == 1


def test_status_filter_is_exact_and_case_insensitive(server):
    result = server.search_tickets("", status="in progress")
    assert result
    assert all(" | In Progress | " in line for line in result.splitlines())
    assert server.search_tickets("", status="progress") == "Brak zgłoszeń."


def test_search_unknown_returns_explicit_message(server):
    assert server.search_tickets("nieistniejący-fioletowy-tunel") == "Brak zgłoszeń."


def test_get_ticket_preserves_raw_values_and_metadata(server):
    text = server.get_ticket("mapjob-102")
    for value in ("MAPJOB-102", "regoin", "PL-MZ", "26.11", "2026-11-02", "map-data"):
        assert value in text
    assert '"type": "doc"' not in text


def test_adf_rich_content_keeps_boundaries_and_link_text(server):
    adf = {"type": "doc", "content": [
        {"type": "heading", "content": [{"type": "text", "text": "Obszar"}]},
        {"type": "bulletList", "content": [
            {"type": "listItem", "content": [
                {"type": "paragraph", "content": [
                    {"type": "text", "text": "PL"}, {"type": "hardBreak"},
                    {"type": "text", "text": "drogi"}]}]}]},
        {"type": "paragraph", "content": [
            {"type": "inlineCard", "attrs": {"url": "https://example.invalid/spec"}}]},
    ]}
    assert server.flatten_adf(adf).strip() == "Obszar\nPL\ndrogi\nhttps://example.invalid/spec"
    assert server.flatten_adf(None) == ""


def test_get_ticket_exposes_explicit_links(server):
    assert "MAPJOB-108" in server.get_ticket("MAPJOB-107")


def test_comments_preserve_override_and_chronology(server):
    text = server.list_comments("MAPJOB-106")
    assert text.index("10601") < text.index("10602")
    assert "2026.10" in text
    assert "2026.11" in text
    assert "Zespół wydań" in text
    assert "2026-11-05T12:00:00.000+0000" in text


def test_empty_comments(server):
    assert server.list_comments("MAPJOB-101") == "Brak komentarzy."


@pytest.mark.parametrize("tool", ["get_ticket", "list_comments"])
@pytest.mark.parametrize("key", ["MAPJOB-999", "../../tickets.json"])
def test_unknown_ticket_is_not_a_path(server, tool, key):
    with pytest.raises(ValueError, match="Nie znaleziono zgłoszenia"):
        getattr(server, tool)(key)


def test_data_shape_and_adf():
    path = Path(__file__).resolve().parents[2] / "exercise-data/jira-jobs/tickets.json"
    response = json.loads(path.read_text(encoding="utf-8"))
    assert response["total"] == len(response["issues"]) == 36
    assert len({issue["key"] for issue in response["issues"]}) == 36
    for issue in response["issues"]:
        fields = issue["fields"]
        assert issue["key"].startswith("MAPJOB-")
        assert fields["description"]["type"] == "doc"
        assert fields["description"]["version"] == 1
        assert fields["summary"] and fields["status"]["name"]
        assert isinstance(fields["labels"], list)
        assert fields["created"]
        assert isinstance(fields["issuelinks"], list)
        comments = fields["comment"]
        assert comments["total"] == len(comments["comments"])
        assert all(c["body"]["type"] == "doc" for c in comments["comments"])
