"""Read-only Jira Cloud CLI. Run with: uv run --with httpx jira_read.py --help."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
from dataclasses import dataclass, field
import os
import re
import sys
from urllib.parse import urlsplit



@dataclass(frozen=True)
class Settings:
    base_url: str
    email: str = field(repr=False)
    token: str = field(repr=False)

    @classmethod
    def from_env(cls, env=None):
        env = os.environ if env is None else env
        required = ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
        missing = [name for name in required if not env.get(name, "").strip()]
        if missing:
            raise ValueError("Missing environment variables: " + ", ".join(missing))
        base = env["JIRA_BASE_URL"].rstrip("/")
        try:
            url = urlsplit(base)
            port = url.port
        except ValueError:
            raise ValueError("Invalid JIRA_BASE_URL") from None
        site = bool(re.fullmatch(r"[a-zA-Z0-9-]+\.atlassian\.net", url.hostname or ""))
        gateway = url.hostname == "api.atlassian.com" and bool(re.fullmatch(r"/ex/jira/[a-zA-Z0-9-]+", url.path))
        if url.scheme != "https" or url.username or url.password or url.query or url.fragment or port not in (None, 443) or not (gateway or (site and not url.path)):
            raise ValueError("Invalid JIRA_BASE_URL: use an HTTPS Atlassian site or scoped Jira gateway")
        cloud_id = env.get("JIRA_CLOUD_ID", "").strip()
        if cloud_id:
            if not re.fullmatch(r"[a-zA-Z0-9-]+", cloud_id):
                raise ValueError("Invalid JIRA_CLOUD_ID")
            base = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        return cls(base, env["JIRA_EMAIL"], env["JIRA_API_TOKEN"])


def flatten_adf(node):
    """Keep paragraph boundaries, cards and link destinations without importing MCP."""
    if not node:
        return ""
    if isinstance(node, str):
        return node
    kind = node.get("type")
    if kind == "text":
        text = node.get("text", "")
        for mark in node.get("marks", []):
            href = mark.get("attrs", {}).get("href")
            if mark.get("type") == "link" and href and href != text:
                text += f" ({href})"
        return text
    if kind == "hardBreak":
        return "\n"
    if kind in {"inlineCard", "blockCard"}:
        return node.get("attrs", {}).get("url", "")
    text = "".join(flatten_adf(child) for child in node.get("content", []))
    return text.rstrip("\n") + "\n" if kind in {"paragraph", "heading", "listItem", "tableRow", "codeBlock", "blockquote"} else text


def issue_key(key):
    key = key.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*-[0-9]+", key):
        raise ValueError("Invalid issue key")
    return key


class JiraReader:
    def __init__(self, settings, *, transport=None):
        import httpx  # Optional for offline CLI/MCP; required only by live mode.
        self.http = httpx.Client(base_url=settings.base_url + "/", auth=httpx.BasicAuth(settings.email, settings.token), headers={"Accept": "application/json"}, timeout=30, follow_redirects=False, transport=transport)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.http.close()

    def request(self, method, path, **kwargs):
        if method != "GET" or not re.fullmatch(r"/rest/api/3/(search/jql|issue/[A-Z][A-Z0-9_]*-[0-9]+(?:/comment)?)", path):
            raise ValueError("Read-only client refuses this method or endpoint")
        return self._send(method, path, **kwargs)

    def _send(self, method, path, **kwargs):
        import httpx
        try:
            response = self.http.request(method, path.lstrip("/"), **kwargs)
        except httpx.HTTPError:
            raise ValueError("Jira connection failed; check network and JIRA_BASE_URL") from None
        if not response.is_success:
            hint = " Check token scopes and product/project access." if response.status_code in (401, 403) else ""
            if response.status_code == 429:
                hint = " Rate limit reached; wait before a manual retry."
            raise ValueError(f"Jira HTTP {response.status_code}.{hint}")
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            raise ValueError("Jira returned invalid JSON") from None

    def search(self, jql, fields="summary,status,labels"):
        params = {"jql": jql, "maxResults": 100, "fields": fields}
        result, seen = [], set()
        while True:
            page = self.request("GET", "/rest/api/3/search/jql", params=params)
            result.extend(page["issues"])
            token = page.get("nextPageToken")
            if page.get("isLast") is True or not token:
                return result
            if token in seen:
                raise ValueError("Jira pagination repeated nextPageToken")
            seen.add(token)
            params["nextPageToken"] = token

    def get_issue(self, key):
        return self.request("GET", f"/rest/api/3/issue/{issue_key(key)}", params={"fields": "summary,description,status,created,labels,issuelinks,project,issuetype,parent,subtasks"})

    def comments(self, key):
        result, start = [], 0
        while True:
            page = self.request("GET", f"/rest/api/3/issue/{issue_key(key)}/comment", params={"startAt": start, "maxResults": 100, "orderBy": "created"})
            items = page["comments"]
            result.extend(items)
            start += len(items)
            if start >= page["total"]:
                return result
            if not items:
                raise ValueError("Jira comment pagination stopped before total")


def format_issue(issue, children=None):
    fields = issue["fields"]
    lines = [issue["key"], "Tytuł: " + fields.get("summary", ""), "Status: " + fields.get("status", {}).get("name", ""), "Utworzono: " + fields.get("created", ""), "Etykiety: " + ", ".join(fields.get("labels", [])), "Opis:", flatten_adf(fields.get("description")).strip(), "Powiązania:"]
    parent = (fields.get("parent") or {}).get("key", "Brak")
    children = fields.get("subtasks", []) if children is None else children
    lines[-1:-1] = ["Typ: " + fields.get("issuetype", {}).get("name", ""), "Rodzic: " + parent, "Dzieci: " + (", ".join(child["key"] for child in children) or "Brak")]
    for link in fields.get("issuelinks", []):
        direction = "outward" if "outwardIssue" in link else "inward"
        lines.append(f'{link["type"].get(direction, link["type"].get("name", ""))}: {link[direction + "Issue"]["key"]}')
    return "\n".join(lines)


def format_comments(comments):
    return "\n\n".join(f'{c["id"]} | {c["created"]} | {c.get("author", {}).get("displayName", "")}\n{flatten_adf(c["body"]).strip()}' for c in comments) or "Brak komentarzy."



DATA_PATH = Path(__file__).resolve().parents[2] / "exercise-data/jira-jobs/tickets.json"


class OfflineReader:
    """Read a captured search response. A deliberately bounded JQL subset."""
    def __init__(self, path=DATA_PATH):
        self.tickets = json.loads(Path(path).read_text(encoding="utf-8"))["issues"]
        self.by_key = {issue["key"]: issue for issue in self.tickets}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get_issue(self, key):
        key = issue_key(key)
        if key not in self.by_key:
            raise ValueError(f"Nie znaleziono zgłoszenia: {key}")
        return deepcopy(self.by_key[key])

    def children(self, key):
        return [issue for issue in self.tickets if (issue["fields"].get("parent") or {}).get("key") == issue_key(key)]

    def comments(self, key):
        return sorted(self.get_issue(key)["fields"].get("comment", {}).get("comments", []), key=lambda c: (c["created"], c["id"]))

    def search_text(self, query, status=None):
        return [issue for issue in self.tickets if (not status or issue["fields"]["status"]["name"].casefold() == status.casefold()) and all(word in (format_issue(issue, self.children(issue["key"])) + " " + format_comments(self.comments(issue["key"]))).casefold() for word in query.casefold().split())]

    def search(self, jql, fields="summary,status,labels"):
        # Reject unsupported syntax rather than silently widening the selection.
        order = re.search(r"\s+ORDER\s+BY\s+key(?:\s+(ASC|DESC))?\s*$", jql, re.I)
        expression = jql[:order.start()].strip() if order else jql.strip()
        clauses = []
        value_pattern = r'(?P<value>"[^"\\]*"|\'[^\'\\]*\'|[A-Za-z0-9_.:-]+)'
        clause_pattern = re.compile(r"(?P<field>project|labels|status|issuetype|parent|key|text)\s*(?P<op>=|~)\s*" + value_pattern, re.I)
        while expression:
            match = clause_pattern.match(expression)
            if not match:
                raise ValueError("Offline JQL: supported fields project, labels, status, issuetype, parent, key (=), text (~), AND and ORDER BY key")
            field_name, operator, value = match["field"].lower(), match["op"], match["value"].strip("\'\"")
            if (field_name == "text") != (operator == "~"):
                raise ValueError("Offline JQL: text requires ~; other fields require =")
            clauses.append((field_name, value.casefold()))
            expression = expression[match.end():].strip()
            if expression:
                conjunction = re.match(r"AND\s+", expression, re.I)
                if not conjunction or not expression[conjunction.end():].strip():
                    raise ValueError("Offline JQL: only AND combinations are supported")
                expression = expression[conjunction.end():].strip()
        if not clauses:
            raise ValueError("Offline JQL: empty query; use project = TEST")
        result = self.tickets
        for name, value in clauses:
            def matches(issue):
                f = issue["fields"]
                if name == "text":
                    return value in (format_issue(issue, self.children(issue["key"])) + " " + format_comments(self.comments(issue["key"]))).casefold()
                actual = {"project": f.get("project", {}).get("key", ""), "status": f.get("status", {}).get("name", ""), "issuetype": f.get("issuetype", {}).get("name", ""), "parent": (f.get("parent") or {}).get("key", ""), "key": issue["key"], "labels": f.get("labels", [])}[name]
                return value in [label.casefold() for label in actual] if isinstance(actual, list) else actual.casefold() == value
            result = [issue for issue in result if matches(issue)]
        return sorted(result, key=lambda i: int(i["key"].rsplit("-", 1)[1]), reverse=bool(order and (order[1] or "").upper() == "DESC")) if order else result


def main(argv=None, *, env=None, transport=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Read the sanitized local snapshot, without credentials or network")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("search").add_argument("jql")
    for command in ("get", "comments"):
        sub.add_parser(command).add_argument("key")
    args = parser.parse_args(argv)
    try:
        environment = os.environ if env is None else env
        offline = args.offline or environment.get("JIRA_OFFLINE") == "1"
        api = OfflineReader() if offline else JiraReader(Settings.from_env(environment), transport=transport)
        with api:
            if args.command == "search":
                issues = api.search(args.jql)
                print("\n".join(f'{i["key"]} | {i["fields"].get("status", {}).get("name", "")} | {i["fields"]["summary"]}' for i in issues))
                print(f"Liczba zgłoszeń: {len(issues)}")
            elif args.command == "get":
                print(format_issue(api.get_issue(args.key), api.children(args.key) if offline else None))
            else:
                print(format_comments(api.comments(args.key)))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as error:
        # Do not echo response bodies, URLs, environment values or exception chains.
        print(str(error) if isinstance(error, ValueError) else "Unexpected Jira response shape", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
