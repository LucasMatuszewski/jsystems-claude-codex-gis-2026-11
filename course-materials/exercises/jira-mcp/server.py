"""Lokalny snapshot odpowiedzi Jira API. Brak sieci i narzędzi zapisu."""
try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    from mcp.server import MCPServer as FastMCP
from mcp.types import ToolAnnotations

from jira_read import OfflineReader, flatten_adf, format_comments, format_issue

snapshot = OfflineReader()
TICKETS = snapshot.tickets
mcp = FastMCP('jira-jobs')
READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)


def ticket_by_key(key: str) -> dict:
    return snapshot.get_issue(key)


@mcp.tool(annotations=READ_ONLY)
def search_tickets(query: str, status: str | None = None) -> str:
    """Szukaj wszystkich słów także w komentarzach, kluczach i hierarchii.

    Puste query zwraca wszystkie klucze. Status to dokładna nazwa, nie JQL.
    """
    return '\n'.join(f'{i["key"]} | {i["fields"]["status"]["name"]} | {i["fields"]["summary"]}' for i in snapshot.search_text(query, status)) or 'Brak zgłoszeń.'


@mcp.tool(annotations=READ_ONLY)
def get_ticket(key: str) -> str:
    """Pokaż opis, rodzica, bezpośrednie dzieci i powiązania, bez normalizacji."""
    return format_issue(snapshot.get_issue(key), snapshot.children(key))


@mcp.tool(annotations=READ_ONLY)
def list_comments(key: str) -> str:
    """Pełna treść komentarzy od najstarszego, z ID, datą i autorem technicznym."""
    return format_comments(snapshot.comments(key))


if __name__ == '__main__':
    mcp.run(transport='stdio')
