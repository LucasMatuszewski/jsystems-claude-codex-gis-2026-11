# Opcjonalnie: ten sam snapshot w Databricks

Ścieżka lokalna z GeoParquet pozostaje podstawą ćwiczenia. Databricks wybierz, jeśli masz dostęp do workspace z przygotowanymi tabelami albo zaimportujesz publiczne pliki do własnego środowiska. Osobiste konto Databricks Free Edition jest opcjonalne; samo utworzenie konta nie kopiuje tabel. Nie potrzebujesz środowiska firmowego ani danych firmowych.

## Tabele i geometria

| Tabela | Wiersze | Istotne pola |
|---|---:|---|
| `workspace.map_qa.osm_roads` | 99 768 | `osm_id`, `highway`, pełne `tags`, `node_ids`, `geometry` |
| `workspace.map_qa.overture_segments` | 85 405 | GERS `id`, `class`, `speed_limits`, `road_surface`, `sources`, `geometry` |
| `workspace.map_qa.photos` | 561 | `photo_id`, `longitude`, `latitude`, `heading`, data i atrybucja |
| `workspace.map_qa.photo_road_links` | 561 | wejściowi kandydaci połączeń, dystans i flagi |
| `workspace.map_qa.traffic_signs` | 1730 | `id`, `object_value`, daty, `image_ids`, `geometry` |

Pliki źródłowe są w volume `/Volumes/workspace/map_qa/inputs/`. Tabele zachowują geometrie jako **BINARY WKB**, nie jako gotowy typ GEOMETRY. W SQL twórz geometrię przez `ST_GeomFromWKB(geometry, 4326)`. Dla zdjęć użyj `ST_Point(longitude, latitude, 4326)`, a dystans licz dopiero po `ST_Transform(..., 2180)`. Listy i struktury Overture pozostają zagnieżdżone. Metadane GeoParquet nie zastępują jawnego SRID w wyrażeniu SQL.

Licencje, daty i zasady atrybucji są takie same jak w [pakiecie lokalnym](README.md) i [ATTRIBUTION.md](ATTRIBUTION.md). Rozbieżności źródeł nadal wymagają przeglądu człowieka.

## Dostęp z terminala agenta

Claude Code i Codex mogą uruchamiać ten sam CLI lub skrypt REST. Potrzebujesz zmiennych `DATABRICKS_HOST` i `DATABRICKS_TOKEN`, ustawionych poza repozytorium. `DATABRICKS_HOST` to URL HTTPS workspace bez końcowego `/`. Sprawdzaj wyłącznie obecność zmiennych, nie wartości. Nie czytaj plików z sekretami i nie uruchamiaj `databricks auth env`, bo może wyświetlić token.

Opisane polecenia sprawdzono z **Databricks CLI 1.23.0**. Jeśli nie masz CLI, użyj [oficjalnej instrukcji instalacji](https://docs.databricks.com/aws/en/dev-tools/cli/install); na Windows wybierz wariant opisany dla tego systemu. Nie instaluj starego pakietu Python `databricks-cli` zamiast aktualnego programu.

```powershell
databricks version
```

```powershell
databricks api post --help
```

```powershell
databricks api get /api/2.0/sql/warehouses
```

Przejdź z katalogu głównego repozytorium do danych:

```powershell
Set-Location course-materials/exercise-data/map-qa
```

Najprostszy odczyt przez Python i SQL Statement Execution REST API:

```powershell
uv run --python 3.12 query_databricks.py --statement "SELECT count(*) AS photos FROM workspace.map_qa.photos"
```

Skrypt korzysta z biblioteki standardowej, wysyła `POST /api/2.0/sql/statements` i odpytuje status przez `GET /api/2.0/sql/statements/{statement_id}`. Jeśli nie podasz `--warehouse` ani `DATABRICKS_SQL_WAREHOUSE_ID`, wybierze pierwszy dostępny warehouse. Na workspace z kilkoma zasobami wskaż właściwy jawnie. Wysłanie SQL do zatrzymanego warehouse może go uruchomić. Używaj małych zapytań, a przy pobieraniu wierszy dodaj `LIMIT`.

Skrypt zwraca status, schemat i wiersze w formacie JSON_ARRAY. Nie zapisuje tokenu. Upłynięcie czasu oczekiwania klienta nie oznacza anulowania SQL; zachowaj `statement_id` i sprawdź status, zamiast ponownie wysyłać zapytanie.

Ten sam odczyt przez CLI: przygotuj JSON zawierający wyłącznie zapytanie i identyfikator warehouse.

```powershell
uv run --python 3.12 query_databricks.py --request-file data/databricks-query.json
```

```powershell
$statement = databricks api post /api/2.0/sql/statements --json "@data/databricks-query.json" | ConvertFrom-Json
```

```powershell
databricks api get "/api/2.0/sql/statements/$($statement.statement_id)"
```

Jeżeli stan jest `PENDING` albo `RUNNING`, odpytaj ten sam identyfikator ponownie. Nie wykonuj ponownie POST tylko po to, aby uzyskać wynik. Nazwa `data/` w tych komendach oznacza ignorowany katalog wewnątrz `course-materials/exercise-data/map-qa/`.

## Kontrole przestrzenne

W SQL Editor albo przez `query_databricks.py --statement` wykonaj osobno te zapytania. Kontrolują dane wejściowe, nie znajdują błędów atrybutów mapy.

Poprawność geometrii OSM i Overture:

```sql
SELECT 'osm' AS source, count(*) AS rows, count_if(NOT ST_IsValid(ST_GeomFromWKB(geometry,4326))) AS invalid FROM workspace.map_qa.osm_roads UNION ALL SELECT 'overture', count(*), count_if(NOT ST_IsValid(ST_GeomFromWKB(geometry,4326))) FROM workspace.map_qa.overture_segments;
```

Ponowne obliczenie dystansu dla dostarczonych kandydatów połączeń:

```sql
SELECT count(*) AS checked, round(max(abs(ST_Distance(ST_Transform(ST_Point(p.longitude,p.latitude,4326),2180),ST_Transform(ST_GeomFromWKB(r.geometry,4326),2180))-l.distance_m)),6) AS max_difference_m FROM workspace.map_qa.photos p JOIN workspace.map_qa.photo_road_links l USING(photo_id) JOIN workspace.map_qa.osm_roads r ON r.osm_id=l.osm_way_id;
```

Pokrycie obszaru przez aparaty obu źródeł:

```sql
SELECT source, count(*) AS photos, count_if(ST_Intersects(ST_GeomFromText('POLYGON((19.8 49.95,20.15 49.95,20.15 50.15,19.8 50.15,19.8 49.95))',4326),ST_Point(longitude,latitude,4326))) AS inside_bbox FROM workspace.map_qa.photos GROUP BY source ORDER BY source;
```

## Managed MCP w Claude Code

Dostępny endpoint SQL MCP ma postać `${DATABRICKS_HOST}/ai-gateway/mcp-services/system.ai.dbsql`. Udostępnia narzędzia `execute_sql` i `poll_sql_result`. Nowy endpoint wymaga odpowiedniej konfiguracji Unity Gateway i uprawnień workspace. Starszy `/api/2.0/mcp/sql` jest osobną ścieżką zależną od ustawień Managed MCP Servers; nie traktuj HTTP 200 jako sukcesu, jeśli odpowiedź JSON-RPC zawiera błąd.

Najpierw skonfiguruj MCP w osobnym projekcie testowym. Poniższe polecenie zachowuje w konfiguracji odwołanie do zmiennej tokenu, a nie jej wartość. Nie zastępuj pojedynczych cudzysłowów przy nagłówku podwójnymi:

```powershell
claude mcp add --scope project --transport http map-qa "$env:DATABRICKS_HOST/ai-gateway/mcp-services/system.ai.dbsql" --header 'Authorization: Bearer ${DATABRICKS_TOKEN}'
```

W sesji Claude Code sprawdź `/mcp`, zatwierdź wyłącznie ten serwer i poproś:

~~~text
Użyj wyłącznie MCP map-qa. Odczytaj SELECT count(*) AS photos FROM workspace.map_qa.photos. Nie modyfikuj danych ani schematów. Jeśli execute_sql zwróci stan PENDING albo RUNNING, użyj poll_sql_result dla tego samego statement_id. Podaj stan, schemat i wynik. Nie wyświetlaj tokenów ani konfiguracji uwierzytelniania.
~~~

Po zatwierdzeniu serwera sprawdź rzeczywisty wynik zapytania, nie sam status połączenia. MCP może dopuszczać zapis - uprawnienia i zakres zadania nadal obowiązują.

Źródła: [SQL Statement Execution API](https://docs.databricks.com/aws/en/dev-tools/sql-execution-tutorial), [funkcje przestrzenne](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-st-geospatial-functions), [Databricks SQL MCP](https://docs.databricks.com/aws/en/agents/mcp-tools/databricks-sql), [zmienne w konfiguracji MCP Claude Code](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json).
