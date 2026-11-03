> Przykład startowy do ćwiczenia map QA (Python + dane GIS). Analogiczne prompty dla innych stosów: ADR-generation-typescript-vercel-ai-sdk.md, ADR-generation-java-openai-sdk-angular-material.md

/write-adr create ADR documents based on @docs/PRD.md and @reports/map-qa/profile.md

Zbadaj, jak zrealizować funkcje z PRD w Pythonie 3.12 (uv, pytest), i porównaj te opcje. Dla każdej pary podaj kompromisy i rekomendację dla tego PRD:
- obliczenia przestrzenne: DuckDB spatial https://duckdb.org/docs/stable/core_extensions/spatial/overview kontra GeoPandas + Shapely + pyproj https://geopandas.org/en/stable/docs.html
- źródło danych: lokalne GeoParquet kontra tabele Databricks przez SQL Statement Execution API https://docs.databricks.com/aws/en/dev-tools/sql-execution-tutorial albo Databricks CLI; MCP opcjonalnie
- model decyzyjny: `openai/gpt-6-luna-decisions` https://openrouter.ai/openai/gpt-6-luna-decisions kontra `typesafe/jev-1.14` (cena, opóźnienie, typy pytań, praca ze zdjęciami)
- klient: oficjalny OpenRouter SDK (`client.alpha.decisions.create`) kontra surowy `POST https://openrouter.ai/api/alpha/decisions`; nie używaj natywnego klienta OpenAI
- wynik: raport Markdown + HTML (szablon Jinja2 albo czysty Python), a jeśli dashboard jest w PRD: Streamlit https://docs.streamlit.io kontra PySide6 https://doc.qt.io/qtforpython-6/

Przeczytaj każdy link przed decyzją. Użyj Context7 MCP albo dokumentacji u źródła, żeby mieć AKTUALNE API: nie polegaj na danych treningowych, przypnij wersje bibliotek.

Opisz w ADR:
- jak normalizujemy `maxspeed` i `speed_limits` bez gubienia surowych tagów i reguł `when`/`between`,
- CRS do metrów (EPSG:2180) i sposób łączenia zdjęcia z drogą: odległość, kierunek kamery, remisy, drogi serwisowe,
- kontrakt modelu decyzyjnego: pytania, dozwolone odpowiedzi, co trafia do `state` (tylko zdjęcie i neutralny tekst), próg abstencji, timeout, limit zapytań i kosztu, cache, brak automatycznych ponowień,
- strategię testów: testy przed kodem, mock API tylko z zapisanej prawdziwej odpowiedzi, na koniec każdego etapu rzeczywiste uruchomienie CLI na danych.

Klucz `OPENROUTER_API_KEY` jest w zmiennych środowiskowych; nie odczytuj go i nie wypisuj. Zadaj najwyżej 5 pytań o moje decyzje, poczekaj na odpowiedzi, potem zapisz ADR po polsku w `docs/ADR/`. Nie pisz kodu.
