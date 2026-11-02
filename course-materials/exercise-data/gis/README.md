# Dane do ćwiczeń: syntetyczne dane mapowe

Fikcyjne miasto w centralnej Polsce (prostokąt ok. 51,70-51,83 N, 19,35-19,60 E). Dane są w całości wygenerowane: nazwy, punkty i drogi nie opisują rzeczywistych obiektów. Pliki w `raw/` są surowe i zawierają błędy typowe dla danych z wielu źródeł. Traktuj je jako tylko do odczytu: pipeline zapisuje wyniki w osobnym katalogu.

| Plik | Zawartość | Kolumny |
|---|---|---|
| `raw/places_raw.csv` | punkty POI (restauracje, stacje paliw, ładowarki, przystanki i inne) | `place_id, name, category, lat, lon, confidence, source, updated_at` |
| `raw/roads_raw.geojson` | odcinki dróg (LineString, EPSG:4326) | `segment_id, class, speed_limit_kmh, oneway` |
| `raw/districts.geojson` | dzielnice (Polygon, EPSG:4326) | `district_id, name, population` |
| `raw/field_inspections_epsg2180.csv` | wyniki inspekcji terenowych, współrzędne w układzie PUWG 1992 (EPSG:2180) | `inspection_id, x, y, result, inspected_on` |

`confidence` to pewność źródła w skali 0-1. `x` to współrzędna wschodnia, `y` północna.

## Szybki start

```powershell
uv init --bare
uv add pandas geopandas shapely pyproj duckdb pytest
uv run python -c "import geopandas as gpd; print(gpd.read_file('course-materials/exercise-data/gis/raw/districts.geojson').head())"
```

DuckDB czyta te pliki bezpośrednio (rozszerzenie `spatial`):

```sql
INSTALL spatial; LOAD spatial;
SELECT category, count(*) FROM read_csv_auto('course-materials/exercise-data/gis/raw/places_raw.csv') GROUP BY ALL ORDER BY 2 DESC;
SELECT * FROM ST_Read('course-materials/exercise-data/gis/raw/districts.geojson');
```

Zanim agent zacznie poprawiać dane, niech najpierw opisze, co w nich znalazł, i poda liczby. Każdą liczbę da się sprawdzić prostym zapytaniem: to jest test, czy agent nie zgaduje.
