# Zdjęcia znaków i atrybuty dróg

Dane wejściowe do [ćwiczenia kontroli mapy](../../exercises/map-qa-decisions/). Zacznij od plików już obecnych w repozytorium. Syntetyczne obrazy, etykiety i drogi można czytać offline bez instalowania pakietów; ich regeneracja i analiza wymagają zależności. Wywołania modelu wymagają internetu i skonfigurowanego klucza.

| Ścieżka | Co zawiera |
|---|---|
| `synthetic/` | 25 oryginalnych rysunków PNG, `labels.csv` i `synthetic_roads.geojson`. Wymyślone współrzędne i atrybuty, CC0. Etykiety są wejściem do własnej kontroli wyniku. |
| `osm/osm_roads.geojson` | Mały rzeczywisty snapshot dróg Łodzi, EPSG:4326. Zachowane `osm_id`, `highway`, `maxspeed`, węzły i pełne `tags`. ODbL. |
| `osm/osm_roads_run.json` | Data, źródło, bbox, liczniki i metadane pobrania snapshotu. Rejestr opisuje także pliki surowe, których nie dołączamy do repozytorium. |
| `labels_reviewed.csv` | Przypięty manifest Commons: źródła, adresy pobrania, autorzy, licencje, SHA-256 i wstępne etykiety. Zdjęć Commons nie ma w Git. |
| `download_sign_images.py` | Pobiera obrazy Commons/Panoramax albo regeneruje rysunki. `--manifest` odtwarza przypięty zbiór i sprawdza hashe. |
| `download_osm_segments.py` | Pobiera drogi z Overpass lub jawnie wybranego głównego API OSM. To ścieżka odświeżenia, nie warunek rozpoczęcia ćwiczenia. |
| `download_common.py` | Wspólne narzędzia HTTP, maksymalnie trzy próby pobrania, User-Agent, zapis CSV/JSON i metadanych. Nie uruchamiaj go osobno. |
| `ATTRIBUTION.md` | Licencje, źródła i atrybucja obrazów oraz danych. Zachowaj je w eksportach. |

## Polecenia PowerShell

Z katalogu głównego repozytorium przejdź do danych:

```powershell
Set-Location course-materials/exercise-data/map-qa
```

Pomoc downloaderów:

```powershell
uv run --python 3.12 download_sign_images.py --help
```

```powershell
uv run --python 3.12 download_osm_segments.py --help
```

Odtwórz przypięte 24 zdjęcia Commons do ignorowanego katalogu. Skrypt zachowa cały manifest, w tym rekord wyłączony z oceny. Niezgodny SHA-256 przerywa pobranie; nie zastępuj go nowym hashem bez ponownej oceny obrazu.

```powershell
uv run --python 3.12 download_sign_images.py --manifest labels_reviewed.csv --limit 24 --out data/commons
```

Opcjonalnie odtwórz syntetyczne dane w osobnym katalogu, bez nadpisywania wejść:

```powershell
uv run --python 3.12 download_sign_images.py --source synthetic --limit 25 --out data/synthetic-regenerated
```

Opcjonalne odświeżenie rzeczywistych dróg, do osobnego katalogu:

```powershell
uv run --python 3.12 download_osm_segments.py --source osm-api --bbox "19.445,51.775,19.455,51.785" --out data/osm-refresh
```

Opcjonalna próbka zdjęć z pozycjami kamer z Panoramax, do badania geometrii połączeń:

```powershell
uv run --python 3.12 download_sign_images.py --source panoramax --bbox "19.445,51.775,19.455,51.785" --limit 5 --out data/panoramax
```

Każdy downloader zapisuje `labels.csv` lub GeoJSON, atrybucję i `*_run.json`. Używa `pathlib`, bez ścieżek Linux i bez WSL. Parametry `--out` i `--timeout` znajdziesz w pomocy. `--source overpass` jest alternatywą odświeżenia; przy niedostępnym serwerze pracuj na dołączonym snapshocie. Nie uruchamiaj wielu pobrań jednocześnie. Wróć do katalogu głównego przed promptami M1-M7.

```powershell
Set-Location ../../..
```

## Jak interpretować dane

- Rysunki i drogi syntetyczne są jednym spójnym zestawem do sprawdzania kodu. Nie są obserwacjami OSM. Nie przenoś ich etykiet na snapshot Łodzi.
- Commons służy do oceny odczytu zdjęcia. `category_speed_hint` jest wskazówką kategorii, a nie prawdą wzorcową. `observed_speed` i `label_status` zawierają wstępny przegląd; obejrzyj obrazy samodzielnie. `ambiguous_excluded` wyklucz z mianownika accuracy z jawnym licznikiem. Brak etykiety nie oznacza klasy `none`.
- Zdjęcia Commons często nie mają współrzędnych lub pochodzą z innych miast. Nie wymuszaj ich dopasowania do Łodzi. Pozycja zdjęcia to pozycja kamery, nie znaku. Panoramax nie gwarantuje adnotacji znaków.
- Najbliższa droga może być drogą serwisową, przeciwną jezdnią albo innym poziomem. Sam dystans nie potwierdza przypisania znaku. Wynik to kandydat do kontroli, nie dowód błędu mapy.
- `maxspeed` może być puste, `PL:urban`, `none`, listą lub wartością z jednostką. Zachowaj oryginał i osobny status normalizacji. `maxspeed:conditional`, `maxspeed:forward` i `maxspeed:backward` są w `tags`; bez czasu i kierunku nie sprowadzaj ich do bezwarunkowej liczby.
- GeoJSON ma współrzędne WGS84, EPSG:4326. Dystans licz dopiero po transformacji obu warstw do EPSG:2180. Stopnie nie są metrami.
- Zachowaj datę zdjęcia i snapshotu. Znak mógł się zmienić. Nie usuwaj niewygodnych rekordów, tylko zapisuj przyczynę wyłączenia.

Licencje obrazu i bazy są niezależne. [Pełna atrybucja](ATTRIBUTION.md) obowiązuje również w raporcie HTML, miniaturach i udostępnianych eksportach.
