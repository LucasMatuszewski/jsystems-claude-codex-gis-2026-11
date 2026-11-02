# Ćwiczenie: Agenci w Twojej codziennej pracy z danymi (SQL, Pandas, Spark, Elasticsearch, legacy)

> Samodzielne ćwiczenie (na sali, jeśli starczy czasu, lub jako praca domowa po kursie).
> Nie wymaga web-devu ani TypeScriptu. Wybierz JEDEN wariant najbliższy Twojej codziennej
> pracy. Każdy wariant ćwiczy te same koncepcje kursu - kontekst (`AGENTS.md`), pętlę
> weryfikacji, uprawnienia, skills, tryb headless - tylko na TWOICH narzędziach.
>
> **Zasada bezpieczeństwa (obowiązkowa):** nigdy nie podłączaj agenta do produkcyjnej bazy.
> Pracujemy na danych syntetycznych lub kopii. Docelowo w pracy: osobny użytkownik DB
> **read-only** + reguły deny w `/permissions` (np. deny na `psql.*DROP`, `DELETE`, `UPDATE`).

## Setup wspólny (5 min)

1. Nowy folder poza repo kursowym, np. `~/data-agent-lab`, w nim `git init` (agent = commituj często).
2. Uruchom `claude` i poproś o utworzenie `AGENTS.md` dla tego folderu - podaj: Twój dialekt SQL / wersje narzędzi, konwencje nazewnicze, zasadę "tylko SELECT na bazach", zasadę "każdy wynik analizy weryfikuj drugim, niezależnym zapytaniem".
3. Dane ćwiczeniowe (wariant A-D korzysta z tego samego zbioru) - **opcja A (zalecana): gotowy zbiór z repo kursu** `course-materials/exercise-data/` (sklep elektroniczny: ~5000 zamówień, 24 miesiące, reklamacje, 4 ukryte wzorce + karty produktów `kb/` do RAG; szczegóły w tamtejszym README):

```bash
python3 <repo>/course-materials/exercise-data/load-sqlite.py
```

lub `node load-sqlite.mjs` (wbudowane `node:sqlite`), a dla Javy `load-h2.sql` (H2 + CSVREAD). Powstaje `lab.db` w bieżącym katalogu. Wzorce do końcowej weryfikacji: `exercise-data/hidden-patterns.md` (SPOILER - nie czytaj przed analizą).

**Opcja B:** wygeneruj własne dane agentem:

```text
Generate a synthetic e-commerce dataset for analytics exercises. Create:
1. schema.sql - DDL for tables: products (id, name, category, price, supplier), customers (id, name, country, created_at), orders (id, customer_id, order_date, status), order_items (order_id, product_id, quantity, unit_price), complaints (id, order_id, product_id, reason_category, created_at, resolved_at, decision).
2. CSV files with realistic data: ~200 products, ~1000 customers, ~8000 orders over 24 months, ~600 complaints.
3. Hide 3 non-obvious patterns in the data (e.g. one supplier with rising complaint rate, a seasonal sales spike, one country with high order-cancellation rate) and write them to hidden-patterns.md - I will check later whether analysis finds them.
4. load.py - a script that creates lab.db (SQLite) and imports the CSVs. Run it and verify row counts with SELECT COUNT(*).
```

---

## Wariant A - SQL (Postgres / Oracle / MS SQL Server / SQLite)

Kolejne prompty (każdy = osobne zadanie, po każdym ZWERYFIKUJ wynik samodzielnie - to Twoja rola eksperta):

```text
Explore lab.db: list tables, row counts, and describe relationships. Generate an entity-relationship diagram as Mermaid in docs/erd.md. Add a short data dictionary (column -> meaning).
```

```text
Analysis task: find the top 5 products by complaint rate (complaints per units sold), monthly complaint trend per category, and average time-to-resolution per decision type. For EVERY result: show the SQL, run it, then verify it with a second, differently-constructed query (e.g. different join order or a window function) and compare results. Save the report to docs/analysis-report.md.
```

```text
Take the 3 heaviest queries from docs/analysis-report.md and optimize them: show EXPLAIN QUERY PLAN before and after, propose indexes, create them, and measure the difference. Document in docs/optimization.md.
```

**Migracja dialektów** (dla osób z Oracle / MS SQL - wklej własny, zanonimizowany fragment):

```text
Here is an Oracle PL/SQL procedure [or T-SQL stored procedure]: <PASTE>. 
1. Explain step by step what it does (business logic, edge cases).
2. Translate it to PostgreSQL (PL/pgSQL). List every dialect difference you had to handle (data types, NVL/ISNULL, sequences, ROWNUM/TOP, MERGE, error handling).
3. Write a test script that runs both versions against equivalent sample data and compares outputs row by row.
```

Sprawdzenie końcowe: porównaj wnioski agenta z `hidden-patterns.md`. Znalazł wszystkie 3 wzorce? Które przegapił i dlaczego (za mało danych w kontekście? złe zapytanie?).

## Wariant B - Pandas / Python

```text
Load the CSVs from this folder into Pandas. Do a data-quality audit: missing values, duplicates, dtype problems, outliers, referential integrity between the files. Write findings to docs/dq-report.md, then write clean.py that fixes the issues (document every decision) and produces cleaned parquet files.
```

```text
TDD on data: write pytest tests FIRST for a function monthly_complaint_rate(category) -> DataFrame (edge cases: empty month, category with zero sales, complaint without matching order). Then implement it in analysis.py. Run tests, show them failing first, then passing.
```

```text
Build report.py that generates a monthly management report (charts with matplotlib saved to reports/) answering: sales trend per category, complaint-rate ranking, anomaly detection month-over-month. Find the 3 hidden patterns in this dataset and describe them.
```

## Wariant C - Spark / Scala

Na VM może zabraknąć zasobów - ten wariant najlepiej lokalnie lub jako praca domowa (`pip install pyspark`).

```text
Convert analysis.py (Pandas) to a PySpark job spark_job.py: same results, but written for scale - explain every choice (broadcast join vs shuffle, partitioning by order_date, caching). Run it locally on the CSVs and compare outputs with the Pandas version.
```

```text
Here is a legacy Scala Spark job from my team: <PASTE anonymized>. Document what it does (inputs, outputs, transformations as a Mermaid flow), point out performance smells (shuffles, UDFs that could be native functions, skew risks), and propose a refactoring plan with the 3 highest-impact changes first.
```

## Wariant D - Elasticsearch

Bez lokalnego ES - ćwiczymy "na sucho" na mappingach (agent i tak musi rozumieć Query DSL):

```text
Create mappings.json for an index of the complaints data (proper types: keyword vs text, dates, nested order items). Then translate these natural-language questions into Elasticsearch Query DSL (aggregations included) and explain each: (1) complaint count per category per month in 2026, (2) top suppliers by complaint rate, (3) full-text search "screen flicker" in complaint reasons filtered to laptops, (4) percentile of time-to-resolution. Validate every query is syntactically correct against mappings.json.
```

Masz dostęp do testowego klastra? Poproś agenta o skrypt curl/Python, który tworzy indeks, ładuje CSV przez bulk API i wykonuje zapytania naprawdę.

## Wariant E - Legacy code (Delphi / C# / stary Java)

Zobacz też istniejący przykład: `Legacy-Code-JFTP-modernization.md`. Wklej własny, zanonimizowany moduł (100-500 linii):

```text
Here is a legacy Delphi unit [or C# class]: <PASTE>.
1. Document it: purpose, public API, side effects, hidden business rules, a Mermaid sequence diagram of the main flow.
2. Write characterization tests (golden-master style): given these example inputs, capture current outputs as the expected baseline - in the legacy language if testable, otherwise as a table of input->output in docs/characterization.md.
3. Propose a migration plan to <C#/.NET 8 / Java 21>: order of extraction, risks, what must NOT change.
```

---

## Bonus - baza wiedzy / RAG (sqlite-vec)

W `course-materials/exercise-data/kb/` jest 12 kart produktów (specyfikacje + "znane problemy",
celowo skorelowane z danymi w `complaints` - np. bateria Nexon X15). Gotowy prompt na tool
`search_kb` z embeddingami w SQLite (rozszerzenie `sqlite-vec`) znajdziesz w
`exercise-data/README.md`. Dla Javy: FTS w H2 albo PGVector/Elasticsearch.

---

## Co przećwiczyłeś (mapowanie na moduły kursu)

- `AGENTS.md` z konwencjami DB = context engineering (moduł 1.3)
- "Zweryfikuj drugim zapytaniem", EXPLAIN przed/po = pętla weryfikacji, TDD (moduł 2.4, 3.2)
- Read-only, deny rules, dane syntetyczne = uprawnienia i bezpieczeństwo (moduł 1.2)
- Powtarzalny styl SQL-review? Zrób z tego **skill** (moduł 2.2)
- Raport dzienny: `claude -p "Wygeneruj raport z lab.db do reports/$(date +%F).md"` w cronie/Jenkinsie = headless CI/CD (moduł 3.3)
