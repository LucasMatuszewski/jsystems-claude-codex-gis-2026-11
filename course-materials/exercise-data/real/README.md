# Publiczne dane GIS do ćwiczeń

Cztery downloadery pobierają małe wycinki prawdziwych, publicznych danych do porównania z [danymi syntetycznymi](../gis/). Nie wymagają konta ani klucza API, Docker, WSL lub Hyper-V. Uruchamiaj z katalogu głównego repozytorium, w PowerShell lub terminalu Linux. Potrzebne są uv, Python 3.12 i dostęp do internetu.

Wyniki trafiają do `course-materials/exercise-data/real/data/`, niezależnie od bieżącego katalogu. Folder jest ignorowany przez Git; pobranych danych nie dodawaj do commita. Każdy skrypt wypisuje liczby rekordów, czas i rozmiary plików oraz zapisuje te same informacje w `*_run.json`. `--out` zmienia katalog wynikowy, a `--timeout` ustawia czas oczekiwania HTTP w sekundach. Ponowne uruchomienie zastępuje pliki danego źródła.

## Polecenia PowerShell

Skrypty OSM i GIOŚ używają biblioteki standardowej Pythona. Overture i GTFS wymagają DuckDB; poniżej wersja użyta w sprawdzeniu.

```powershell
uv run --python 3.12 python course-materials/exercise-data/real/download_osm_chargers.py
uv run --python 3.12 --with duckdb==1.5.6 python course-materials/exercise-data/real/download_overture_places.py
uv run --python 3.12 --with duckdb==1.5.6 python course-materials/exercise-data/real/download_overture_places.py --ev-only
uv run --python 3.12 --with duckdb==1.5.6 python course-materials/exercise-data/real/download_gtfs.py
uv run --python 3.12 python course-materials/exercise-data/real/download_gios_air.py
```

Oba źródła miejsc mają domyślnie ten sam bbox Łodzi: `19.25,51.65,19.65,51.90`, czyli west,south,east,north w WGS84. Przykłady zmiany zakresu i wersji:

```powershell
uv run --python 3.12 python course-materials/exercise-data/real/download_osm_chargers.py --bbox "19.35,51.72,19.52,51.82"
uv run --python 3.12 --with duckdb==1.5.6 python course-materials/exercise-data/real/download_overture_places.py --bbox "19.35,51.72,19.52,51.82" --release 2026-10-21.0 --ev-only
uv run --python 3.12 python course-materials/exercise-data/real/download_gios_air.py --stations 295 296 10058 --sensors-per-station 2
```

Opcje wszystkich skryptów: dopisz `--help`. Zapytania OSM/GIOŚ/GTFS mają do trzech prób przy błędach przejściowych i limitach API. Nie uruchamiaj wielu kopii naraz ani nie zwiększaj od razu obszaru do całej Polski.

## Co otrzymujesz

- **OSM:** Overpass `amenity=charging_station`, punkty oraz środki obiektów typu way/relation. `osm_chargers.geojson` i `osm_chargers.csv` zachowują wszystkie tagi w polu `tags` (obiekt JSON / tekst JSON) oraz tożsamość `(osm_type, osm_id)`. CSV jest UTF-8 z BOM. Środek obiektu nie zastępuje jego pełnej geometrii. HTTP ma identyfikujący User-Agent, timeout i retry; odpowiedź z komunikatem o niepełnym wyniku jest błędem.
- **Overture:** DuckDB z `httpfs` i `spatial` czyta publiczne S3 z filtrem bbox i zapisuje GeoParquet `overture_places.parquet`. Najnowszą wersję wybiera pole `latest` z [oficjalnego katalogu STAC](https://stac.overturemaps.org/catalog.json), a `--release` ją przypina. Ścieżka: `s3://overturemaps-us-west-2/release/<release>/theme=places/type=place/*`. `--ev-only` zapisuje osobny `overture_ev_places.parquet`; obsługuje `taxonomy` w schemacie 2.0 i `categories` w starszym schemacie. Filtr obejmuje `ev_charging_station`, `electric_vehicle_charging_station` i `charging_station`, także kategorie alternatywne. Zerowy wynik jest możliwy i jest raportowany. Zachowane są pola źródeł i licencji. DuckDB korzysta z czterech wątków i limitu pamięci 2 GB; cache rozszerzeń jest w `data/.duckdb_extensions/`.
- **GTFS Łodzi:** oficjalne [dane transportowe UM Łódź](https://otwarte.miasto.lodz.pl/transport_komunikacja/) i [archiwum ZIP](https://otwarte.miasto.lodz.pl/wp-content/uploads/2025/06/GTFS.zip). Skrypt zapisuje `gtfs.zip`, rozpakowuje pliki do `gtfs/` i ładuje `stops.txt` do tabeli `stops` w `gtfs.duckdb`. Wszystkie kolumny pozostają tekstowe, żeby zachować zera wiodące ID; do analiz rzutuj współrzędne jawnie. Wypisuje liczbę przystanków i błędnych współrzędnych. Do częstości kursów zaimportuj również pozostałe rozpakowane pliki i obsłuż kalendarze. `--url` pozwala podać inny publiczny feed; rozpakowywane są tylko płaskie archiwa GTFS, bez ścieżek wychodzących poza folder.
- **GIOŚ:** aktualne endpointy `/pjp-api/v1/rest/`, JSON-LD i paginacja do 500 rekordów na stronę. `gios_stations.json/csv` zawierają listę stacji z WGS84; `gios_measurements.json` zachowuje dane i metadane stanowisk, a `gios_latest.csv` ostatnią niepustą wartość z okna udostępnianego przez API. Domyślnie trzy stacje Łodzi: 295, 296, 10058, do dwóch stanowisk na stację. To nie jest pełna historia ani pełny monitoring wszystkich substancji. Czas pomiaru pozostaje lokalny (CET/CEST), czas pobrania jest UTC. Jednostka API to µg/m³, także dla CO. Null nie staje się zerem; `no_recent_value` oznacza brak wartości. Kod błędu `API-ERR-100003` dla pomiarów manualnych daje status `manual_sensor_unavailable`; pozostałe błędy przerywają pobranie.

Downloadery dostarczają wejścia, nie gotową aplikację. Drogi, szerszy zestaw POI, granice i dane ludności wymagają osobnych importów zgodnie z [wybranym PRD](../../Prompt%20examples/PRD-ideas-overview.md).

## Rzeczywiste pobrania

Sprawdzenie sieciowe: **2.11.2026, Linux**, Python 3.12, uv 0.11.7, DuckDB 1.5.6. Nie wykonano próby na Windows. Wszystkie cztery skrypty uruchomiono na rzeczywistych źródłach. Czas pochodzi z pomiaru wewnątrz skryptu, bez instalowania pakietów przez uv; wartości zależą od daty, cache i sieci.

| Źródło / wariant | Czas | Rekordy | Rozmiary plików wynikowych |
|---|---:|---|---|
| OSM, domyślny bbox | 41,60 s | 50 ładowarek | GeoJSON 25 497 B; CSV 10 162 B |
| Overture Places, `2026-10-21.0` | 23,41 s | 32 768 miejsc | GeoParquet 3 821 886 B |
| Overture, ten sam bbox i wydanie, `--ev-only` | 21,73 s | 90 miejsc | GeoParquet 22 747 B |
| GTFS Łodzi | 7,63 s | 2393 przystanki; 0 błędnych współrzędnych | ZIP 11 742 814 B; DuckDB 798 720 B; `stops.txt` 163 933 B; wszystkie wyniki 90 212 898 B |
| GIOŚ, ustawienia domyślne | 6,76 s | 287 stacji; 6 stanowisk; 300 pomiarów; 6 ostatnich niepustych wartości | Stacje JSON 107 999 B; CSV 18 376 B; pomiary JSON 40 999 B; ostatnie CSV 418 B |
| GIOŚ, `--stations 302`, osobny katalog | 2,11 s | 287 stacji; 2 stanowiska manualne; 0 pomiarów bieżących | Stacje JSON 107 999 B; CSV 18 376 B; pomiary JSON 1577 B; ostatnie CSV 174 B |

Rozmiary nie obejmują `*_run.json` ani cache rozszerzeń. Rozmiar pliku DuckDB może się zmieniać po kolejnych importach tej samej liczby przystanków.

Pierwszy test GIOŚ ze stacją 302 ujawnił HTTP 400 dla stanowisk manualnych. Skrypt obsługuje teraz ten konkretny kod i zachowuje informację o niedostępności zamiast przerywać pozostałe pomiary. Serwer rozszerzeń DuckDB zwracał HTTP 403 w izolowanym sandboxie; pobranie poza sandboxem z dostępem sieciowym i oba warianty Overture zadziałały. Przy podobnym błędzie sprawdź dostęp do `extensions.duckdb.org` oraz publicznego S3, nie dodawaj klucza AWS do publicznego źródła.

## Testy lokalne

```powershell
uv run --python 3.12 python -m unittest discover -s course-materials/exercise-data/real -p "test_*.py" -v
```

Testy bez sieci sprawdzają poprawność bbox, zachowanie tagów i współrzędnych OSM, pusty wynik, wybór ostatniego pomiaru z obsługą null/zera, rozpoznanie konkretnego błędu stanowiska manualnego i bezpieczne rozpakowanie ZIP. Rzeczywiste pobrania z tabeli są osobnymi próbami integracyjnymi; testy lokalne ich nie zastępują.

## Licencje i atrybucja

- **OSM:** [ODbL 1.0 i zasady atrybucji](https://www.openstreetmap.org/copyright). W mapie oraz eksportach zachowaj "© OpenStreetMap contributors" z linkiem do źródła/licencji. Przy udostępnianiu pochodnej bazy sprawdź obowiązki ODbL.
- **Overture:** [licencje i atrybucje według tematu oraz dostawcy](https://docs.overturemaps.org/attribution/). Places zawiera źródła m.in. CDLA Permissive 2.0, Apache 2.0 oraz CC0; nie przypisuj automatycznie jednej licencji całemu wycinkowi. Zachowaj `sources`, wskazanie Overture Maps Foundation i wymagane noty dostawców, w tym NOTICE, jeśli dotyczy. Inne tematy, np. transportation, mają inne warunki, w tym ODbL.
- **GTFS:** dane UM Łódź/ZDiT, źródło wskazane wyżej. Strona pobierania nie wskazuje jednoznacznie standardowej licencji dla tego ZIP; nie zakładaj CC0. Zachowaj oznaczenie dostawcy, datę pobrania i informacje z `agency.txt`/`feed_info.txt`; warunki redystrybucji sprawdź u publikującego.
- **GIOŚ:** użycie API oznacza akceptację [regulaminu i zasad portalu](https://powietrze.gios.gov.pl/pjp/content/api). Wskaż wyraźnie źródło "Główny Inspektorat Ochrony Środowiska", czas pomiaru i pobrania. Dane bieżące nie są na bieżąco weryfikowane i mogą ulec korekcie. Nie traktuj braków jako zer ani flag anomalii jako oficjalnych alertów.
- **Podkład mapowy:** [OpenFreeMap](https://openfreemap.org/quick_start/) nie wymaga klucza API. Przy MapLibre GL JS zachowaj widoczne atrybucje OpenFreeMap, OpenMapTiles i OpenStreetMap; licencja podkładu nie zastępuje licencji warstw danych.
