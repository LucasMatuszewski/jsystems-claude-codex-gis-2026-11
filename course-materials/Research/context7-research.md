# Context7: up-to-date documentation for AI coding agents

> What Context7 is, how it works, how to connect it in Claude Code, Codex CLI, Copilot CLI and Cursor, the CLI option, pricing and limits, and when it beats web search. All facts verified 2026-10-01 against context7.com and the [upstash/context7](https://github.com/upstash/context7) repo. **Updated 2026-10-02:** added self-hosting and air-gapped options.

## What it is

- **Context7** is a documentation service by **Upstash** that serves current, version-specific library docs to LLMs and AI code editors. It solves the two classic failure modes: **hallucinated APIs** that do not exist and **outdated training data** (models trained on year-old library versions).
- How it works: Upstash's private **crawling and parsing engine** indexes public library documentation. Each library gets an ID such as `/vercel/next.js` or `/mongodb/docs`. The agent resolves a library name to this ID, then fetches focused, version-matched **doc snippets and code examples** for its exact task. Snippets come straight from the official sources, not from model memory.
- Distributed in two ways:
  - **MCP server** (remote `https://mcp.context7.com/mcp`, or locally via npm package `@upstash/context7-mcp`),
  - **CLI + skill**: the npm package `ctx7` installs a skill that teaches the agent to fetch docs through CLI commands, no MCP required.
- Two MCP tools: **`resolve-library-id`** (library name + query, returns ranked candidate IDs) and **`query-docs`** (library ID + task description, returns doc snippets). You can skip resolution by writing the ID directly in the prompt, e.g. "use library /vercel/next.js for docs".
- Very popular: ~62.6k stars on GitHub as of 2026-10-01.

## Connecting it to your tools

Quickest path for all tools: `npx ctx7 setup` (auto-detects the environment, handles OAuth, generates an API key). Requires Node.js 18+. Undo with `npx ctx7 remove`.

| Tool | Auto setup | Manual method (verified 2026-10-01) |
| :-- | :-- | :-- |
| **Claude Code** | `npx ctx7 setup --claude` | `claude mcp add --scope user --header "Authorization: Bearer YOUR_API_KEY" --transport http context7 https://mcp.context7.com/mcp` ([MCP docs](https://code.claude.com/docs/en/mcp)) |
| **Codex CLI** | `npx ctx7 setup --codex` | `codex mcp add context7 -- npx -y @upstash/context7-mcp`; or remote server in `config.toml` with `url = "https://mcp.context7.com/mcp"`; also available as a Codex plugin: `codex plugin marketplace add upstash/context7` |
| **GitHub Copilot CLI** | `npx ctx7 setup --copilot` | edit `~/.copilot/mcp-config.json` and add an `mcpServers.context7` entry with `"type": "http"`, the URL above and an `Authorization` header |
| **Cursor** | `npx ctx7 setup --cursor` | edit `~/.cursor/mcp.json` (or per-project `.cursor/mcp.json`), add `mcpServers.context7` with the URL above |

- **Anonymous access**: the remote MCP server works without any API key, at a **lower shared rate limit**; long agent sessions may hit 429 errors. Exact anonymous quota is not officially documented (community reports ~200 requests; UNCONFIRMED).
- **API key** (recommended, free): create one in the [Context7 dashboard](https://context7.com/dashboard) and pass it as `Authorization: Bearer YOUR_API_KEY`.
- The local npm variant for any MCP client: `npx -y @upstash/context7-mcp`.

## The ctx7 CLI

- `npx ctx7 setup` - one-command configuration for the supported agents; per-agent flags (npm README, checked 2026-10-02): `--claude`, `--cursor`, `--opencode`, `--codex`, `--copilot`, `--vscode`, `--devin`.
- `ctx7 library <name> <query>` - search, the CLI equivalent of `resolve-library-id`.
- `ctx7 docs <libraryId> <query>` - fetch docs, the equivalent of `query-docs`.
- Useful when a tool has no MCP support yet, or when you want docs fetched by a script instead of a live MCP connection.

## Pricing and limits

From [context7.com/plans](https://context7.com/plans), verified 2026-10-01:

| Plan | Price | Included API calls |
| :-- | :-- | :-- |
| **Free** | $0 | 1,000 per month |
| **Pro** | $10 per seat / month | 2,000 per seat / month |
| **Enterprise** | custom | custom - defined per contract, re-check the plans page before quoting |

- On Free you are **blocked at the monthly cap** (plus 20 bonus calls per day while blocked). Paid-plan overage terms (e.g. per-1,000-call pricing) are set by the current plans page and contracts - do not assume fixed numbers across plans; Enterprise in particular negotiates its own included volume and overage.
- **Private repository parsing** (adding private docs to the index) costs $5 per 1M tokens.
- Quotas are per seat, not pooled; search API calls count the same as doc calls.

## When to use what

- **Context7 first** for any library/API docs, code generation, setup or configuration steps: it returns version-specific official snippets without leaving the editor, and works even when documentation sites block scrapers. The recommended agent rule from the README: always use Context7 for library docs without being asked.
- **Built-in docs tools** (editor hover docs, built-in `/docs`-style features) are fine for quick signature checks of already-installed packages, but they usually show only the locally installed version and lack worked examples.
- **Web search** still wins for release notes, blog posts, changelogs, GitHub issues and anything newer than Context7's latest crawl. Combine: Context7 for API usage, web search for "what changed in this release".

## Known limitations

- **Coverage gaps**: not every library is indexed; you can request or contribute one via [context7.com/add-library](https://context7.com/add-library).
- **Private and internal repos** are not in the public index; adding them requires paid private repo parsing or the self-hosted Enterprise deployment.
- **Community-contributed content**: Context7 states it cannot guarantee the accuracy, completeness or security of all indexed documentation; report wrong snippets from the site.
- **Quota walls**: anonymous use hits shared limits quickly; heavy agent sessions should run with a free API key.
- A **version mismatch** can still occur if you pin no library ID: let the agent resolve the ID, or write it explicitly in the prompt/`AGENTS.md`.

## Self-hosting and air-gapped use (added 2026-10-02)

**Short answer:** only the client side of Context7 is open source. The repo is MIT-licensed, but its README states that the **API backend, documentation parser and crawler are private**. You can run the MCP server yourself, but it still calls `https://context7.com/api` by default, and the public library index is not downloadable. Full on-premises Context7 exists only as the paid **Enterprise** offering.

| Goal | Possible with the public repo? |
| :-- | :-- |
| Run the MCP server process locally | Yes, but it still calls Context7's hosted API |
| Run the whole Context7 platform on premises | No, backend, parser and crawler are private |
| Use Context7's existing public library index offline | No, no export or download exists |
| Serve your own docs offline with no Enterprise licence | Yes, if you build or pick your own backend (options below) |

### What the open-source repo contains

- `packages/mcp` (MCP server with `resolve-library-id` and `query-docs`), `packages/cli` (`ctx7`), `packages/sdk` (TypeScript API client), plus OpenCode, pi.dev and Vercel AI SDK integrations. TypeScript, Node.js, pnpm monorepo.
- Build and run the MCP server from source:

  ```bash
  pnpm install
  pnpm --filter @upstash/context7-mcp build
  pnpm --filter @upstash/context7-mcp start
  ```

- Backend URL hook: `packages/mcp/src/lib/constants.ts` reads `CONTEXT7_API_URL` and falls back to `https://context7.com/api`. The `ctx7` CLI can also be pointed at a custom deployment URL. These are **connection settings only**; something compatible has to answer at that URL.

### Option A: your own backend behind the open-source Context7 client

Choose this if agents must keep the familiar `resolve-library-id` / `query-docs` tools and the `ctx7` skill. The MCP client calls two endpoints (`packages/mcp/src/lib/api.ts`, checked 2026-10-02):

| Endpoint | Query params | Response |
| :-- | :-- | :-- |
| `GET /v2/libs/search` | `libraryName`, `query` | JSON with a `results` array (optional `error`) |
| `GET /v2/context` | `libraryId`, `query` | JSON with `data` and `outcome`, or plain-text docs |

The client also handles `401`, `404` and `429` responses and the `X-Context7-Auth-Prompt` response header. This is an internal contract, not a documented public API: derive the exact response types from the TypeScript sources and pin the client version you test against, because upstream can change it at any time.

What you have to build to make it work offline:

1. **Source mirror:** pick your source set yourself, e.g. cloned Git repos of the libraries you use, offline mirrors of documentation sites, exported internal wikis (Confluence, Notion) and OpenAPI specs or `llms.txt` files. In an air-gapped network, fetch them on a connected staging machine and bring them in through your approved transfer process.
2. **Parser and chunker:** Markdown, MDX, reStructuredText, plain text and notebooks, split into snippets that keep their code examples.
3. **Index and retrieval:** full-text search (e.g. SQLite FTS5 or PostgreSQL full-text) works without any model. Semantic search is optional and needs a **locally hosted** embedding model (e.g. via Ollama) plus a vector store such as pgvector.
4. **Library catalogue and versions:** stable IDs in the `/org/project` format with per-version indexes, so `resolve-library-id` can rank candidates. Hosted Context7 uses an LLM to rank search results; offline you can use plain text ranking or a local model.
5. **Refresh pipeline:** a scheduled re-import when new docs arrive, plus auth and rate limiting if several teams share the server.
6. **Offline packaging:** no `npx` downloads at runtime. Vendor the built MCP server as a Docker image, or serve the npm packages from an internal registry (Verdaccio, Nexus).

### Option B: a fully open-source docs server (recommended for air-gapped use)

[arabold/docs-mcp-server](https://github.com/arabold/docs-mcp-server) already implements most of Option A and needs no Context7 code. From its README (checked 2026-10-02):

- MIT licence, ~1.8k stars.
- Indexes websites, GitHub repositories, local folders, zip archives, and npm and PyPI packages.
- Runs entirely on your own machine. Embeddings are **optional**: full-text search works without them, and Ollama is among the supported providers for local embeddings.
- Runs via Docker, Node.js (`npx`) or embedded mode, with a web UI on `localhost:6280`.

In an air-gapped network, prefer local folders and zip archives prepared on the staging machine over live scraping. Verify the current feature list and release before rolling it out, because this is a third-party project.

**Recommendation:** use Option B for an air-gapped environment with your own data. Choose Option A only if keeping the Context7 tool names and the `ctx7` skill unchanged is worth building and maintaining a custom backend. If you need Context7's own catalogue, use the hosted service or ask Upstash about Enterprise on premises.

## Sources

- [Context7 GitHub repo (upstash/context7)](https://github.com/upstash/context7), README: tools, CLI commands, setup, server URL, checked 2026-10-01
- [Context7 plans and pricing](https://context7.com/plans), plan table and overage rules, checked 2026-10-01
- [Context7 install page](https://context7.com/install), `npx ctx7 setup` flags per agent, checked 2026-10-01
- [Context7 MCP clients reference](https://context7.com/docs/resources/all-clients), per-tool manual configs and anonymous access notes, checked 2026-10-01
- [Context7 README disclaimer](https://github.com/upstash/context7/blob/master/README.md) and [MIT license](https://github.com/upstash/context7/blob/master/LICENSE), private backend/parser/crawler, checked 2026-10-02
- [MCP API client](https://github.com/upstash/context7/blob/master/packages/mcp/src/lib/api.ts) and [API URL config](https://github.com/upstash/context7/blob/master/packages/mcp/src/lib/constants.ts), endpoints and `CONTEXT7_API_URL`, checked 2026-10-02
- [Adding libraries](https://github.com/upstash/context7/blob/master/docs/adding-libraries.mdx) and [Enterprise overview](https://github.com/upstash/context7/blob/master/docs/enterprise.mdx), ingestion sources and on-premises offering, checked 2026-10-02
- [arabold/docs-mcp-server](https://github.com/arabold/docs-mcp-server), open-source self-hosted alternative, checked 2026-10-02
- [skills.sh](https://skills.sh) and [vercel-labs/skills](https://github.com/vercel-labs/skills), separate skills-installer ecosystem (installs skills, not Context7 plugins), checked 2026-10-01
