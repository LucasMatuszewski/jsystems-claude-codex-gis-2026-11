# Ten sam snapshot w Databricks

W M2 odczytasz tabele we wspólnym workspace prowadzącego, podobnie jak dane w hurtowni. Prowadzący przekazuje host, token SQL i warehouse w czacie Zoom. Osobiste konto Databricks Free Edition jest opcjonalne i nie jest potrzebne; samo założenie konta nie kopiuje tabel. Przy awarii Databricks kontynuuj na [lokalnych plikach](README.md).

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

## Odczytaj pięć wierszy przez CLI

Pracuj w PowerShell w katalogu głównym repozytorium. Zainstaluj aktualny CLI (nie stary pakiet Python `databricks-cli`):

```powershell
winget install Databricks.DatabricksCLI
```

Po instalacji otwórz nowy PowerShell w katalogu repozytorium. Ustaw dane z czatu samodzielnie w terminalu; nie wklejaj tokenu do rozmowy z agentem, pliku ani Git. Host to adres HTTPS bez końcowego `/`.

```powershell
$env:DATABRICKS_HOST="<z czatu>"
```

```powershell
$env:DATABRICKS_TOKEN="<z czatu>"
```

```powershell
$env:DATABRICKS_SQL_WAREHOUSE_ID="97c455ee6fb1fcb9"
```

To identyfikator warehouse ćwiczenia; użyj innego tylko wtedy, gdy prowadzący poda zmianę.

```powershell
databricks version
```

```powershell
databricks current-user me
```

Sukces potwierdza uwierzytelnienie wspólnego tokenu, nie osobiste konto uczestnika. Nie przekazuj agentowi pełnej odpowiedzi z danymi tożsamości. Sprawdzaj tylko obecność zmiennych, nigdy ich wartości; nie uruchamiaj `databricks auth env`.

Przygotuj plik żądania bez sekretów. Kodowanie ASCII wystarcza dla tego zapytania i omija różnicę BOM między Windows PowerShell a PowerShell 7:

```powershell
New-Item -ItemType Directory -Force course-materials/exercise-data/map-qa/data
```

```powershell
@{warehouse_id=$env:DATABRICKS_SQL_WAREHOUSE_ID;statement='SELECT photo_id, source, heading FROM workspace.map_qa.photos ORDER BY photo_id LIMIT 5';wait_timeout='10s';on_wait_timeout='CONTINUE';disposition='INLINE';format='JSON_ARRAY'} | ConvertTo-Json | Set-Content -Encoding ascii course-materials/exercise-data/map-qa/data/databricks-five.json
```

```powershell
$statement = databricks api post /api/2.0/sql/statements --json '@course-materials/exercise-data/map-qa/data/databricks-five.json' | ConvertFrom-Json
```

```powershell
$statement.status
```

Jeśli stan to `SUCCEEDED`, odczytaj pięć wierszy:

```powershell
$statement.result.data_array
```

Jeśli stan to `PENDING` albo `RUNNING`, odpytaj **to samo** zapytanie, bez ponownego POST:

```powershell
$statement = databricks api get "/api/2.0/sql/statements/$($statement.statement_id)" | ConvertFrom-Json
```

Powtórz odczyt statusu, a po `SUCCEEDED` pokaż wiersze. `FAILED` lub `CANCELED` to błąd, nie pusty wynik. Nie ponawiaj automatycznie zapytania, które może nadal działać. Pierwszy odczyt może uruchomić zatrzymany warehouse; stan oczekiwania nie jest sam w sobie błędem.

**Alternatywa Python z `requests`:** zamiast `databricks api post` wyślij ten sam plik JSON przez REST. Nie uruchamiaj tego POST ponownie tylko po to, aby odebrać poprzedni wynik.

```powershell
uv run --python 3.12 --with requests python -c "import json,os,requests; body=json.load(open('course-materials/exercise-data/map-qa/data/databricks-five.json')); r=requests.post(os.environ['DATABRICKS_HOST'].rstrip('/')+'/api/2.0/sql/statements',headers={'Authorization':'Bearer '+os.environ['DATABRICKS_TOKEN']},json=body,timeout=40); r.raise_for_status(); print(json.dumps(r.json()))"
```

Jeśli wynik Pythona ma stan `PENDING` lub `RUNNING`, wykonaj GET dla zwróconego `statement_id`; nie wysyłaj SQL ponownie. Do dalszych kontroli służy też gotowy `query_databricks.py`, który korzysta z REST i biblioteki standardowej oraz sam odpytuje ten sam identyfikator.

**Sprawdź liczności:** tym samym klientem odczytaj pięć tabel i porównaj wynik z profilem plików:

```powershell
uv run --python 3.12 course-materials/exercise-data/map-qa/query_databricks.py --statement "SELECT 'osm_roads' AS source, count(*) AS rows FROM workspace.map_qa.osm_roads UNION ALL SELECT 'overture_segments', count(*) FROM workspace.map_qa.overture_segments UNION ALL SELECT 'photos', count(*) FROM workspace.map_qa.photos UNION ALL SELECT 'photo_road_links', count(*) FROM workspace.map_qa.photo_road_links UNION ALL SELECT 'traffic_signs', count(*) FROM workspace.map_qa.traffic_signs"
```

W ćwiczeniu wykonuj tylko `SELECT`. Token ma zakres API `sql` (BI Tools); sam zakres nie ogranicza SQL do odczytu, bo nadal obowiązują uprawnienia właściciela tokenu. Nie twórz tabel, schematów ani zasobów. Nie potrzebujesz `all-apis` ani zakresu `authentication`.

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

To rozszerzenie po odczycie CLI/REST, nie warunek wykonania M2. Wspólny token z samym zakresem `sql` nie obejmuje tego endpointu i otrzymuje HTTP 403. Przejdź dalej tylko z osobnym dostępem do Unity Gateway, w osobnym PowerShell ze zmiennymi dla tego dostępu; nie poszerzaj wspólnego tokenu SQL. Endpoint SQL MCP ma postać `${DATABRICKS_HOST}/ai-gateway/mcp-services/system.ai.dbsql`. Udostępnia narzędzia `execute_sql` i `poll_sql_result`. Nowy endpoint wymaga odpowiedniej konfiguracji Unity Gateway i uprawnień workspace. Starszy `/api/2.0/mcp/sql` jest osobną ścieżką zależną od ustawień Managed MCP Servers; nie traktuj HTTP 200 jako sukcesu, jeśli odpowiedź JSON-RPC zawiera błąd.

Najpierw skonfiguruj MCP w osobnym projekcie testowym, uruchamiając polecenie w jego katalogu. Poniższe polecenie zachowuje w konfiguracji odwołanie do zmiennej tokenu, a nie jej wartość. Nie zastępuj pojedynczych cudzysłowów przy nagłówku podwójnymi:

```powershell
claude mcp add --scope project --transport http map-qa "$env:DATABRICKS_HOST/ai-gateway/mcp-services/system.ai.dbsql" --header 'Authorization: Bearer ${DATABRICKS_TOKEN}'
```

Uruchom nową sesję Claude Code z tego samego PowerShell, aby odziedziczyła zmienne. Sprawdź `/mcp`, zatwierdź wyłącznie ten serwer i poproś:

~~~text
Użyj wyłącznie MCP map-qa. Odczytaj SELECT count(*) AS photos FROM workspace.map_qa.photos. Nie modyfikuj danych ani schematów. Jeśli execute_sql zwróci stan PENDING albo RUNNING, użyj poll_sql_result dla tego samego statement_id. Podaj stan, schemat i wynik. Nie wyświetlaj tokenów ani konfiguracji uwierzytelniania.
~~~

Po zatwierdzeniu serwera sprawdź rzeczywisty wynik zapytania, nie sam status połączenia. Jeśli endpoint odrzuca token SQL, zostań przy CLI/REST; nie poszerzaj zakresu wspólnego tokenu. MCP może dopuszczać zapis - uprawnienia i zakres zadania nadal obowiązują.

Źródła: [instalacja CLI na Windows](https://learn.microsoft.com/azure/databricks/dev-tools/cli/install), [zakresy tokenów](https://docs.databricks.com/aws/en/dev-tools/auth/pat#scoped-personal-access-tokens), [SQL Statement Execution API](https://docs.databricks.com/aws/en/dev-tools/sql-execution-tutorial), [funkcje przestrzenne](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-st-geospatial-functions), [Databricks SQL MCP](https://docs.databricks.com/aws/en/agents/mcp-tools/databricks-sql), [zmienne w konfiguracji MCP Claude Code](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json).
