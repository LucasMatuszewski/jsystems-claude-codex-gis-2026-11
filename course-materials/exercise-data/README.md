# Exercise data: sklep elektroniczny (zamówienia, reklamacje, karty produktów)

Gotowy, deterministyczny zbiór danych do ćwiczeń z DB / BI / BE i do modułu analitycznego
aplikacji kursowej. Spójny z domeną aplikacji (zwroty/reklamacje elektroniki): te same
kategorie sprzętu, decyzje `ai/human`, karty produktów urządzeń, które klient może zgłosić.

## Zawartość

| Plik | Co to jest |
|---|---|
| `csv/*.csv` | 5 tabel: products (60), customers (800), orders (~5000, 24 miesiące), order_items (~6900), complaints (~435) |
| `schema.sql` | DDL (SQLite/ANSI). Celowo BEZ indeksów - ich dodanie to część ćwiczenia z optymalizacji |
| `load-sqlite.py` | `python3 load-sqlite.py` -> tworzy `lab.db` w bieżącym katalogu (czysty Python, bez zależności) |
| `load-sqlite.mjs` | `node load-sqlite.mjs` -> to samo przez wbudowane `node:sqlite` (Node 22.5+, bez npm install) |
| `load-h2.sql` | Wariant dla Javy: H2 + `CSVREAD` (uruchom z tego katalogu, instrukcja w komentarzu pliku) |
| `kb/*.md` | 12 kart produktów (specyfikacja, gwarancja, ZNANE PROBLEMY) - baza wiedzy do ćwiczeń RAG |
| `generate.py` | Generator (seed=42, deterministyczny). CSV są w repo - regeneruj tylko po zmianie logiki |

## Szybki start

```bash
python3 load-sqlite.py
```

```bash
node load-sqlite.mjs
```

Java/H2: patrz `load-h2.sql`. Inne bazy (Postgres/Oracle/MSSQL): wykonaj `schema.sql`
(drobne poprawki typów zrobi za Ciebie agent) i zaimportuj CSV swoim klientem - albo po
prostu poproś agenta: "load the CSVs from this folder into my local Postgres, adapt schema.sql".

Ćwiczenia, które korzystają z tych danych: `../Prompt examples/Data-work-agent-exercises-SQL-Pandas-Spark.md`
oraz moduł analityczny aplikacji: `../Prompt examples/PRD-analytics-SQL-module-returns-app.md`.

## Baza wiedzy `kb/` + wektory (sqlite-vec)

Karty produktów w `kb/` są zaprojektowane pod rozszerzenie RAG aplikacji kursowej: klient
zgłasza reklamację "Nexon X15, bateria pada po pół roku", a agent - zanim podejmie decyzję -
odpytuje bazę wiedzy i trafia na sekcję "Znane problemy" tej karty (celowo skorelowaną
z danymi w `complaints`!).

Wariant prosty (wystarcza przy 12 dokumentach): wczytaj całe `kb/*.md` do kontekstu lub
zrób tool `search_kb` na LIKE/FTS5. Wariant wektorowy - przykładowy prompt:

```text
Extend the app with a knowledge-base tool. Load the kb/*.md files, chunk them per section,
embed the chunks (use an embedding model via OpenRouter) and store vectors in SQLite using
the sqlite-vec extension (research current usage via Context7/web). Add a search_kb(query)
tool to the chat agent: embed the query, return top-3 chunks with file names. The complaint
decision prompt must cite the "Znane problemy" section when relevant.
```

Java: analogicznie H2 nie ma wektorów - użyj PGVector/Elasticsearch albo po prostu FTS.

## Zasady

- **Nigdy nie podłączaj agenta do produkcyjnej bazy** - to jest właśnie bezpieczna piaskownica.
- `lab.db` NIE commitujemy (jest w .gitignore) - odtwarzasz go loaderem w kilka sekund.
- Dane są syntetyczne; nazwy firm, produktów i osób są fikcyjne.
