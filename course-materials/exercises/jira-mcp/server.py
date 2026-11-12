"""Lokalne, syntetyczne zgłoszenia. Brak sieci i narzędzi zapisu."""

import json
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    # SDK 2 zmienił nazwę FastMCP; narzędzia i stdio działają tak samo.
    from mcp.server import MCPServer as FastMCP

from mcp.types import ToolAnnotations

DATA_PATH = Path(__file__).resolve().parents[2] / "exercise-data/jira-jobs/tickets.json"
TICKETS = json.loads(DATA_PATH.read_text(encoding="utf-8"))["issues"]
mcp = FastMCP("jira-jobs")
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)


def flatten_adf(node: dict | None) -> str:
    """Spłaszcz ADF, zachowując tekst, adresy kart i granice akapitów."""
    if not node:
        return ""
    kind = node.get("type")
    if kind == "text":
        return node.get("text", "")
    if kind == "hardBreak":
        return "\n"
    if kind == "inlineCard":
        return node.get("attrs", {}).get("url", "")
    text = "".join(flatten_adf(child) for child in node.get("content", []))
    if kind in {"paragraph", "heading", "listItem", "tableRow"}:
        return text.rstrip("\n") + "\n"
    return text


def ticket_by_key(key: str) -> dict:
    for ticket in TICKETS:
        if ticket["key"] == key.strip().upper():
            return ticket
    raise ValueError(f"Nie znaleziono zgłoszenia: {key}")


@mcp.tool(annotations=READ_ONLY)
def search_tickets(query: str, status: str | None = None) -> str:
    """Szukaj wszystkich słów bez rozróżniania liter, także w komentarzach.

    Puste query zwraca wszystkie klucze. Status to dokładna nazwa, nie JQL.
    Wynik zawiera klucz, status i tytuł; szczegóły pobierz osobnymi narzędziami.
    """
    matches = []
    for ticket in TICKETS:
        fields = ticket["fields"]
        if status and fields["status"]["name"].casefold() != status.casefold():
            continue
        haystack = " ".join([
            get_ticket(ticket["key"]), list_comments(ticket["key"])
        ]).casefold()
        if all(word in haystack for word in query.casefold().split()):
            matches.append(f'{ticket["key"]} | {fields["status"]["name"]} | {fields["summary"]}')
    return "\n".join(matches) or "Brak zgłoszeń."


@mcp.tool(annotations=READ_ONLY)
def get_ticket(key: str) -> str:
    """Zwróć opis i metadane bez normalizacji. Komentarze: list_comments."""
    ticket = ticket_by_key(key)
    fields = ticket["fields"]
    lines = [ticket["key"], f'Tytuł: {fields["summary"]}',
             f'Status: {fields["status"]["name"]}', f'Utworzono: {fields["created"]}',
             f'Etykiety: {", ".join(fields["labels"])}',
             "Opis:", flatten_adf(fields["description"]).strip(), "Powiązania:"]
    for link in fields["issuelinks"]:
        direction = "outward" if "outwardIssue" in link else "inward"
        lines.append(f'{link["type"][direction]}: {link[direction + "Issue"]["key"]}')
    if not fields["issuelinks"]:
        lines.append("Brak powiązań strukturalnych.")
    return "\n".join(lines)


@mcp.tool(annotations=READ_ONLY)
def list_comments(key: str) -> str:
    """Zwróć pełną treść komentarzy od najstarszego, z ID, datą i zespołem."""
    comments = ticket_by_key(key)["fields"]["comment"]["comments"]
    ordered = sorted(comments, key=lambda c: (c["created"], c["id"]))
    return "\n\n".join(
        f'{c["id"]} | {c["created"]} | {c["author"]["displayName"]}\n'
        f'{flatten_adf(c["body"]).strip()}' for c in ordered
    ) or "Brak komentarzy."


if __name__ == "__main__":
    mcp.run(transport="stdio")
