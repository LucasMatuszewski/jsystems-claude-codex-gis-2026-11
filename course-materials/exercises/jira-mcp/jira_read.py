"""Read-only Jira Cloud CLI. Run with: uv run --with httpx jira_read.py --help."""

import argparse
from dataclasses import dataclass, field
import os
import re
import sys
from urllib.parse import urlsplit

import httpx


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
    return text.rstrip("\n") + "\n" if kind in {"paragraph", "heading", "listItem", "tableRow"} else text


def issue_key(key):
    key = key.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*-[0-9]+", key):
        raise ValueError("Invalid issue key")
    return key


class JiraReader:
    def __init__(self, settings, *, transport=None):
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
        return self.request("GET", f"/rest/api/3/issue/{issue_key(key)}", params={"fields": "summary,description,status,created,labels,issuelinks,project"})

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


def format_issue(issue):
    fields = issue["fields"]
    lines = [issue["key"], "Tytuł: " + fields.get("summary", ""), "Status: " + fields.get("status", {}).get("name", ""), "Utworzono: " + fields.get("created", ""), "Etykiety: " + ", ".join(fields.get("labels", [])), "Opis:", flatten_adf(fields.get("description")).strip(), "Powiązania:"]
    for link in fields.get("issuelinks", []):
        direction = "outward" if "outwardIssue" in link else "inward"
        lines.append(f'{link["type"].get(direction, link["type"].get("name", ""))}: {link[direction + "Issue"]["key"]}')
    return "\n".join(lines)


def format_comments(comments):
    return "\n\n".join(f'{c["id"]} | {c["created"]} | {c.get("author", {}).get("displayName", "")}\n{flatten_adf(c["body"]).strip()}' for c in comments) or "Brak komentarzy."


def main(argv=None, *, env=None, transport=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("search").add_argument("jql")
    for command in ("get", "comments"):
        sub.add_parser(command).add_argument("key")
    args = parser.parse_args(argv)
    try:
        with JiraReader(Settings.from_env(env), transport=transport) as api:
            if args.command == "search":
                issues = api.search(args.jql)
                print("\n".join(f'{i["key"]} | {i["fields"].get("status", {}).get("name", "")} | {i["fields"]["summary"]}' for i in issues))
                print(f"Liczba zgłoszeń: {len(issues)}")
            elif args.command == "get":
                print(format_issue(api.get_issue(args.key)))
            else:
                print(format_comments(api.comments(args.key)))
        return 0
    except (ValueError, KeyError, TypeError) as error:
        # Do not echo response bodies, URLs, environment values or exception chains.
        print(str(error) if isinstance(error, ValueError) else "Unexpected Jira response shape", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
