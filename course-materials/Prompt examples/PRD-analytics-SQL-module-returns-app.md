# PRD prompt: Moduł Analityczny SQL dla aplikacji kursowej

> UWAGA: to opcjonalny przyklad-zalazek, jak PRD-electronics-returns-complains-app.md.
> NIE nadpisuje decyzji grupy - rozszerza aplikacje zbudowana w dniu 1-2 o backend z danymi,
> SQL i analize danych. Zaprojektowany dla grup, ktore na co dzien pracuja z bazami danych
> (Postgres, Oracle, MS SQL Server), Pandas, Spark czy Elasticsearch, a nie z web-devem.
>
> **Jak uzyc:** uruchom skill `write-prd` i wklej ponizszy prompt jako opis produktu
> (`claude` -> `/write-prd` lub po prostu wklej prompt i pozwol skillowi sie aktywowac).
> Skill zada pytania doprecyzowujace - odpowiadamy wspolnie z grupa. Wynik zapisujemy jako
> `docs/PRD-analytics.md` (osobny plik, nie nadpisujemy `docs/PRD.md`).
> Nastepnie `write-adr` -> nowy ADR (wybor bazy, strategia text-to-SQL, guardrails).
>
> **Dydaktyka (dla trenera):** uczestnicy nie musza znac TypeScriptu - kod pisze agent.
> Ich rola jest to, w czym sa ekspertami: weryfikacja schematu, poprawnosci SQL i wynikow.
> To dokladnie ten podzial pracy czlowiek-agent, ktory stosuja potem we wlasnym stacku.

---

You are a product manager and system analyst. Your task is to prepare a PRD for a new feature module called **"Returns Analytics"** — an extension of the existing "Hardware Service Decision Copilot" application (see `docs/PRD.md` for the base app). The module adds a real database, SQL-based analytics, and data-analysis capabilities to the AI agent.

## Feature description

**1. Database with historical data (seed)**
- A relational database (SQLite by default for zero-setup; the ADR may choose PostgreSQL) with the schema of the provided dataset (`exercise-data/schema.sql`): `products` (category, price, supplier), `customers` (country), `orders` (status), `order_items`, and `complaints` (type return/complaint, reason category, decision, decision_source ai/human, created_at, resolved_at).
- Seed data is PROVIDED in the repo: `course-materials/exercise-data/csv/` (~5000 orders over 24 months, complaints, 4 documented hidden patterns - see `exercise-data/README.md` and the loaders there: Python, Node `node:sqlite`, H2 for Java). The seed step of this module imports those CSVs; do not generate new data.
- Every new decision made by the existing copilot chat is INSERTed into `complaints`, so the app starts producing its own data.

**2. Agent tool: `query_database` (text-to-SQL with guardrails)**
- The chat agent gets a new tool that executes SQL against the database and returns rows.
- The LLM generates the SQL itself; the database schema (DDL + short column descriptions) is injected into the system prompt.
- Hard guardrails enforced in code, not in the prompt: read-only connection; single `SELECT` statements only (reject DDL/DML/multiple statements); enforced row limit (e.g. `LIMIT 200` appended if missing); query timeout; every executed query is written to an audit log with timestamp and originating chat session.
- On SQL error, the agent receives the database error message and may retry up to 2 times (self-correction loop).

**3. Analytics in the chat**
- A user (support manager persona) can ask analytics questions in natural language, in Polish, e.g.: "Ile reklamacji w kategorii laptopy było w ostatnim kwartale i jaki procent zakończył się uznaniem?", "Który produkt ma najwyższy wskaźnik zwrotów?", "Pokaż trend miesięczny reklamacji vs zwrotów w 2026."
- The agent answers with: a short natural-language summary, the resulting data as a formatted table in the chat, and (optional, nice-to-have) a simple chart.
- The agent must show the executed SQL on demand ("pokaż zapytanie") for transparency and verification.
- When the question is ambiguous (e.g. "ostatnio"), the agent asks a clarifying question instead of guessing the date range.

**4. Optional extension: product knowledge base (nice-to-have, may be deferred)**
- The repo provides 12 product spec sheets in `exercise-data/kb/*.md` (specs, warranty terms, KNOWN ISSUES - intentionally correlated with the complaints data, e.g. the Nexon X15 battery defect).
- A `search_kb` tool lets the agent consult these sheets before making a complaint decision; the decision must cite the "Znane problemy" section when relevant.
- Implementation options for the ADR: full-context injection (12 docs fit), keyword/FTS search, or vector search with the `sqlite-vec` SQLite extension (embeddings via OpenRouter).

**5. Out of scope for this module (list explicitly in the PRD)**
- BI dashboards, scheduled reports UI, user authentication/roles, write-access from chat, connecting to any external/production database.

A separate ADR will cover technology choices (database engine, driver, migration/seed tooling, text-to-SQL strategy vs. predefined parameterized queries, testing strategy for SQL correctness). Focus this PRD on functionality, behavior, guardrails, and UX.

---

## Krok 2: ADR prompt (po zatwierdzeniu PRD, analogicznie do ADR-generation-typescript-vercel-ai-sdk.md)

```text
/write-adr create an ADR for the Returns Analytics module based on @docs/PRD-analytics.md, extending the existing app (see @docs/ADR/).

Research (use Context7 MCP /vercel/ai for CURRENT docs, do not rely on training data):
- Tool calling in Vercel AI SDK (tool() + streamText) for the query_database tool
- SQLite driver choice for our stack: node:sqlite vs better-sqlite3 - recommend one
- How to enforce guardrails in CODE, not prompt: read-only connection, single-SELECT validation, LIMIT injection, timeout, audit log
- Seed strategy: deterministic synthetic data generator with documented hidden patterns
- Testing strategy: unit tests for the SQL guard, integration test for the tool loop with a mocked LLM, E2E for one analytics question AND one blocked DROP TABLE attempt
```

---

## Notatki dla uczestników (rozszerzenia po kursie)

- **Twój stack zamiast TS:** ten sam PRD można zaimplementować w Java/Spring (H2 + `exercise-data/load-h2.sql`, JdbcTemplate + Spring AI tool calling), C#/.NET (Dapper/EF + function calling), Python (SQLAlchemy). PRD celowo nie narzuca stacku.
- **Twoja baza:** podmień SQLite na Postgres/Oracle/MS SQL w ADR - guardrails (read-only user, SELECT-only, limit, timeout) pozostają identyczne i to one są esencją ćwiczenia.
- **Moduł 3.1 (worktrees):** naturalny podział na 3 równoległe strumienie: BE = schemat + seed + tool `query_database`, FE = rendering tabel/SQL w czacie, QA = testy E2E pytań analitycznych (w tym: czy agent ODMAWIA wykonania `DROP TABLE`).
- **Moduł 3.3 (headless):** raport dzienny przez `claude -p "Podsumuj wczorajsze reklamacje z bazy i zapisz raport do reports/YYYY-MM-DD.md"` w cronie/Jenkinsie.
