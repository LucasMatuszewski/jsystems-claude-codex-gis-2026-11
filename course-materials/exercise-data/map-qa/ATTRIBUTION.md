# Źródła, licencje i atrybucja

Licencje danych i fotografii są niezależne od kodu aplikacji. Zachowaj źródła, daty i atrybucje także przy eksporcie raportu.

## OpenStreetMap

**OpenStreetMap contributors, ODbL 1.0.** Źródło: [Geofabrik, małopolskie](https://download.geofabrik.de/europe/poland/malopolskie.html), ekstrakt do `2026-11-01T21:21:36Z`. Zasady i tekst licencji: [OSM copyright](https://www.openstreetmap.org/copyright) i [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).

Przekształcenie: wybór całych dróg przecinających bbox, filtr highway opisany w `sources.json`, GeoParquet oraz mała próbka GeoJSON. Pełne tagi i identyfikatory węzłów pozostają zachowane. `osm_roads.parquet` i `osm_roads_sample.geojson` są danymi OSM, nie CC0. Wyniki stanowiące pochodną bazę danych wymagają rozpatrzenia warunków ODbL, w tym udostępnienia bazy na tych warunkach.

## Overture Maps

**Overture Maps Foundation i dostawcy wskazani w `sources`, transportation, ODbL 1.0.** [Dokumentacja transportation](https://docs.overturemaps.org/guides/transportation/), [katalog wydania](https://stac.overturemaps.org/2026-10-21.0/catalog.json), [licencje Overture](https://docs.overturemaps.org/attribution/).

Wydanie `2026-10-21.0`. Wycinek `subtype=road` wybrano filtrem bbox z publicznych GeoParquet S3, ograniczając klasy i kolumny zgodnie z `sources.json`. Geometrie segmentów, GERS i źródłowe referencje pozostają bez zmiany. Zachowano `sources`, aby móc odtworzyć dostawcę, licencję i wersję konkretnego obiektu. Nie przypisuj całości wyłącznie jednemu dostawcy.

## Panoramax

Każda fotografia ma w `photos.csv`: autora (`author`), identyfikator (`photo_id`), źródłowy adres (`source_url`), datę, licencję i jej URL. Miniatury w `offline/` mają te same wpisy w `offline/ATTRIBUTION.csv`.

W tym snapshocie fotografie Panoramax mają **CC BY-SA 4.0** według metadanych poszczególnych obiektów. Źródło: [publiczne API Panoramax](https://api.panoramax.xyz/api), [zasady API](https://docs.panoramax.fr/backend/api/api/), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Nie zakładaj tej samej licencji dla innych instancji lub przyszłych pobrań.

Przekształcenie naszych miniatur: orientacja EXIF, najdłuższy bok maksymalnie 1024 px, JPEG quality 85, usunięcie EXIF. Oryginalny i końcowy SHA-256 są osobnymi polami manifestu. Podpis fotografii w raporcie ma wskazywać autora, identyfikator, link do źródła, CC BY-SA 4.0 oraz to przeskalowanie. Nie zmieniaj informacji o autorstwie po pobraniu.

## Mapillary

Zdjęcia: **CC BY-SA 4.0**, autor i link do obrazu są w każdym wierszu manifestu. Wykorzystano niezmodyfikowane obrazy `thumb_1024_url`. Zasady: [Mapillary CC BY-SA](https://help.mapillary.com/hc/en-us/articles/115001770409-CC-BY-SA-license-for-open-data), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Podpis w raporcie: autor z `author`, identyfikator Mapillary, aktywny `source_url`, nazwa licencji i jej link. Adres pobrania miniatury może wygasnąć; identyfikator i link do strony pozostają podstawą atrybucji.

Metadane pochodne znaków i detekcji w `traffic_signs.geojson` oraz `mapillary_detections.json.gz` udostępniamy publicznie jako **ODbL 1.0**, zgodnie z [zezwoleniem Mapillary na publikowanie pochodnych metadanych dla społeczności](https://help.mapillary.com/hc/en-us/articles/115001777705-OpenStreetMap-compatibility). Źródło: Mapillary. Zachowaj identyfikatory, daty obserwacji i źródłowe referencje obrazów. Zezwolenie na metadane nie zmienia licencji zdjęć. Detekcje i przewidywane pozycje znaków są danymi źródłowymi modelu dostawcy, nie potwierdzeniem błędu OSM.

## Pozostałe dane

`photo_road_links.csv` i `reference_labels.csv` są udostępnione jako **ODbL 1.0**, z zachowaniem atrybucji powiązanych źródeł. Połączenia opisują kandydatów przestrzennych; etykiety referencyjne opisują oglądane kadry. Żaden z tych plików nie zawiera werdyktów o poprawności mapy.

Trzy oryginalne rysunki i odpowiadające im wymyślone drogi w `synthetic/`: **CC0 1.0**, autor generatora wskazany w `synthetic/labels.csv`. [CC0](https://creativecommons.org/publicdomain/zero/1.0/). Nie przenoś tej licencji na rzeczywiste drogi lub fotografie.
