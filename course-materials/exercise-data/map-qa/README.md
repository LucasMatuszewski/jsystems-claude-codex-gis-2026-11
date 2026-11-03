# Rzeczywiste dane do kontroli mapy

Dane wejściowe do [ćwiczenia M1-M7](../../exercises/map-qa-decisions/README.md): Kraków i najbliższe okolice, bbox WGS84 `19.80,49.95,20.15,50.15`. Podstawowe warstwy i manifest `photos.csv` dotyczą tego obszaru. Dodatkowy zestaw `signs/` może obejmować inne obszary Polski; sprawdź pole `area` w jego manifeście. Zachowane całe drogi przecinające bbox mogą wychodzić poza jego granice. Pliki wejściowe są tylko do odczytu; raporty zapisuj w `reports/map-qa/`, a pobrania i cache w `course-materials/exercise-data/map-qa/data/` (katalog ignorowany przez Git).

| Źródło | Zawartość snapshotu | Data i licencja |
|---|---|---|
| OpenStreetMap przez Geofabrik | 99 768 dróg potencjalnie przejezdnych, geometria, pełne `tags`, `node_ids`, początkowy i końcowy węzeł | Ekstrakt małopolskiego do `2026-11-01T21:21:36Z`, ODbL 1.0 |
| Overture Maps, transportation | 85 405 segmentów drogowych, GERS `id`, klasa, reguły prędkości i nawierzchni, źródła i konektory | Wydanie `2026-10-21.0`, ODbL 1.0 |
| Panoramax i Mapillary | 561 zdjęć: 461 Panoramax i 100 Mapillary, współrzędne aparatu, heading, data, autor, licencja i hashe | Daty poszczególnych zdjęć w manifeście, CC BY-SA 4.0 |
| Mapillary, metadane pochodne | 1730 obiektów ograniczeń prędkości oraz detekcje dla 20 zdjęć | Daty `first_seen_at` i `last_seen_at` w danych, publikacja metadanych jako ODbL 1.0 |

To wycinek roboczy, a nie pełna inwentaryzacja miasta. Zdjęcia obejmują różne części obszaru i różne sekwencje. Zdjęcia Mapillary pochodzą z powiązań ze znakami ograniczeń, więc ta część próbki jest obciążona wyborem. W danych są drogi szybkiego ruchu, ulice miejskie i lokalne, dojazdy, parkingi, nieutwardzony dojazd do skrzyżowania oraz kadry terenów zielonych. Profil zdjęć wykonaj samodzielnie; bliska droga z tagiem `track` nie dowodzi, że kadr przedstawia drogę gruntową.

## Trzy sposoby dostępu do danych

W M2 obowiązkowo odczytaj pliki i Databricks; Mapillary, Panoramax i Overture przez sieć sprawdź, jeśli masz czas. Pliki są punktem odniesienia i pozwalają kontynuować bez dostępu do chmury. Polecenia wykonuj w PowerShell z katalogu głównego repozytorium, chyba że sekcja podaje inaczej.

| Dostęp | Co odczytasz | Co jest potrzebne |
|---|---|---|
| Pliki | GeoParquet OSM/Overture, manifest, zdjęcia i ich atrybucje | Klon repozytorium i uv |
| Databricks | Te same dane w pięciu tabelach `workspace.map_qa` | Wspólny token SQL i host z czatu; identyfikator warehouse w [DATABRICKS.md](DATABRICKS.md) |
| API / publiczny bucket | Metadane zdjęć Mapillary i Panoramax, segmenty Overture | Token Mapillary; Panoramax i Overture bez logowania |

### 1. Pliki: eksport gotowy do analizy

Uruchom profil z [Szybkiego startu](../../exercises/map-qa-decisions/README.md#szybki-start), a następnie sprawdź GeoPandas i transformację do metrów:

```powershell
uv run --python 3.12 --with geopandas==1.2.0 --with pyarrow==23.0.1 python -c "import geopandas as gpd; r=gpd.read_parquet('course-materials/exercise-data/map-qa/osm_roads.parquet'); print(len(r), r.crs, r.geometry.is_valid.all(), r.to_crs(2180).crs)"
```

Obejrzyj manifest `photos.csv` i jedno zdjęcie z `offline/`. Polecenie pokazuje liczność, CRS, poprawność geometrii i docelowy EPSG:2180. Nie zmienia wejść.

### 2. Databricks: wspólne tabele

Prowadzący podaje w czacie Zoom jeden wspólny token z zakresem `sql` (BI Tools) i host. Identyfikator SQL warehouse znajdziesz w [DATABRICKS.md](DATABRICKS.md). Osobiste konto Free Edition jest opcjonalne i nie jest potrzebne. W [instrukcji Databricks](DATABRICKS.md#odczytaj-pięć-wierszy-przez-cli) zainstaluj CLI, ustaw zmienne i odczytaj pięć wierszy `workspace.map_qa.photos` przez SQL Statement Execution API. Następnie porównaj liczności tabel z profilem plików.

Jeśli Databricks jest niedostępny, wykonaj te same kontrole na lokalnych GeoParquet i CSV.

### 3. API: mały odczyt źródłowy (jeśli masz czas)

**Mapillary.** Prowadzący udostępnia w czacie wspólny token odczytu. Ustaw go sam w terminalu, nie w rozmowie z agentem ani w pliku repozytorium:

```powershell
$env:MAPILLARY_TOKEN="<z czatu>"
```

Odczytaj metadane jednego obrazu obecnego w manifeście; token jest w nagłówku, nie w URL:

```powershell
Invoke-RestMethod -Uri 'https://graph.mapillary.com/134880168567523?fields=id,captured_at,computed_geometry' -Headers @{Authorization="OAuth $env:MAPILLARY_TOKEN"} | Select-Object id,captured_at,computed_geometry
```

Jeśli Mapillary jest niedostępne albo adresy zdjęć wygasły, użyj manifestu i fotografii z `offline/`.

**Panoramax.** Bez konta pobierz pięć metadanych fotografii z obszaru ćwiczenia:

```powershell
Invoke-RestMethod -Uri 'https://api.panoramax.xyz/api/search?bbox=19.80,49.95,20.15,50.15&limit=5' | Select-Object -ExpandProperty features | Select-Object id,geometry
```

To świeży odczyt API, więc lista może różnić się od przypiętego manifestu. Nie podmieniaj nim wejść ćwiczenia.

**Overture przez DuckDB.** Odczytaj pięć dróg z publicznego bucketu, używając adresów dwóch partycji z `sources.json` i filtra obszaru. Bez konta AWS i bez klucza:

```powershell
uv run --python 3.12 --with duckdb==1.5.6 python -c "import duckdb,json; c=duckdb.connect(); c.execute('INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs'); urls=json.load(open('course-materials/exercise-data/map-qa/sources.json'))['overture']['source_urls']; print(c.execute('SELECT id, class FROM read_parquet(?) WHERE subtype=? AND bbox.xmin<=? AND bbox.xmax>=? AND bbox.ymin<=? AND bbox.ymax>=? LIMIT 5', [urls,'road',20.15,19.80,50.15,49.95]).fetchall())"
```

DuckDB wykonuje odczyty zakresowe; limit wierszy nie oznacza limitu pięciu żądań sieciowych. Nie pobieraj całego globalnego zbioru. Przy awarii publicznego źródła użyj `overture_segments.parquet`.

Dokumentacja: [Panoramax API](https://api.panoramax.xyz/api/docs/swagger), [Mapillary API](https://www.mapillary.com/developer/api-documentation/), [Overture i DuckDB](https://docs.overturemaps.org/getting-data/duckdb/).

## Pliki

| Plik | Rola |
|---|---|
| `osm_roads.parquet` | GeoParquet, około 10,3 MB. `osm_id` to identyfikator całego OSM way. Osobne kolumny najważniejszych tagów i kompletny JSON `tags`. |
| `osm_roads_sample.geojson` | Mała próbka do obejrzenia w edytorze lub narzędziu GIS. Pełna analiza korzysta z GeoParquet. |
| `overture_segments.parquet` | GeoParquet, około 13,4 MB. Zagnieżdżone listy i struktury pozostają typowane, w tym `speed_limits`, `road_surface`, `sources`, `connectors`. |
| `photos.csv` | Manifest wszystkich zdjęć: `photo_id`, URL, pozycja, heading, data, sequence, autor, licencja, SHA-256 źródła i miniatury, rozmiary, przekształcenie. |
| `photo_road_links.csv` | Kandydat OSM i Overture dla zdjęcia, dystans, lokalny bearing, różnica kierunku, liczba alternatyw i flagi. Nie zawiera werdyktów o błędach mapy. |
| `traffic_signs.geojson` | Wybrane klasy `regulatory--maximum-speed-limit-...--g1`, pozycja znaku przewidywana przez Mapillary, daty i źródłowe `image_ids`. To ograniczona próbka API, nie kompletny rejestr znaków. |
| `mapillary_detections.json.gz` | Skompresowany JSON źródłowych detekcji dla części fotografii. Wynik detektora nie zastępuje ręcznej etykiety. |
| `offline/` | 40 obejrzanych miniatur do rozpoczęcia pracy bez pobierania zdjęć; `ATTRIBUTION.csv` zawiera atrybucje. |
| `reference_labels.csv` | Etykiety referencyjne do pomiaru jakości odczytu obrazu. 100 obejrzanych zdjęć, opis zasad poniżej. |
| `sources.json` | Obszar, daty, filtry, reguły przygotowania połączeń, dokładne rozmiary i hashe danych. |
| `DATABRICKS.md`, `query_databricks.py` | Odczyt tabel przez CLI/REST w M2; MCP jako rozszerzenie. |
| `profile.sql`, `profile_data.py` | Zapytania profilujące, bez rozwiązania ćwiczenia. |
| `download_photos.py` | Odtwarzanie zdjęć z manifestu, wznowienie i kontrola dwóch hashy. |
| `refresh_sources.py`, `refresh_mapillary_urls.py` | Nowe wycinki map i odświeżenie wygasających adresów obrazów. |

OSM zawiera `motorway`, `trunk`, `primary`, `secondary`, `tertiary` i ich `*_link`, `residential`, `living_street`, `unclassified`, `service`, `track`, `road`, `busway`. To filtr potencjalnych dróg, a nie potwierdzenie dostępu dla samochodu. `access` i `motor_vehicle` pozostają do sprawdzenia. Dane Overture są przefiltrowane do `subtype=road`; listę wykluczonych klas pieszych i rowerowych znajdziesz w `sources.json`. Różna segmentacja i filtry oznaczają, że same liczby obiektów nie mierzą zgodności źródeł.

## Połączenia i układy współrzędnych

OSM ma EPSG:4326, a Overture OGC:CRS84. W obu plikach współrzędne geometrii to długość i szerokość geograficzna. Przed liczeniem dystansu przelicz obie strony na EPSG:2180. Stopnie nie są metrami.

Dostarczone połączenia wybierają kandydatów w promieniu 25 m od aparatu. Ranking uwzględnia dystans i zgodność heading z lokalną styczną drogi; pełna reguła i rozstrzygnięcie remisów są w `sources.json`. `bearing_diff` ma zakres 0-90 stopni, bo uwzględnia oba kierunki geometrii. `directed_bearing_diff` zachowuje różnicę względem kolejności węzłów. Kierunek patrzenia nie musi być kierunkiem jazdy.

Dopasowanie Overture najpierw korzysta z rzeczywistej referencji do OSM z pola `record_id` w liście `sources` segmentu Overture, np. `w123@4`, oraz dystansu. Gdy jej brak, możliwe jest dopasowanie przestrzenne oznaczone `spatial_fallback`. Sprawdź `candidate_flags`: alternatywne drogi, dostęp ograniczony, droga serwisowa, dokładność GPS, nieznany kierunek lub panorama mogą wymagać abstencji. `is_panorama` jest jedynie heurystyką proporcji obrazu; pełny kadr panoramy nie przedstawia jednego kierunku.

Nie przyjmuj tych połączeń jako wzorca. Bliski dojazd, przeciwna jezdnia, wiadukt lub błędna pozycja aparatu mogą dać zły wynik. Pozycja aparatu nie jest pozycją znaku. Brak dopasowania jest stanem danych, nie dowodem błędu mapy.

`heading=0.0` jest poprawną wartością kierunku północnego, nie znacznikiem braku. W sprawdzonych rekordach Panoramax źródłowe `view:azimuth` także wynosi 0. Brak kierunku w `photos.csv` jest zapisany jako puste pole (po wczytaniu może być NULL/NaN); nie zamieniaj go na zero. Kierunek pochodzi z metadanych źródła, a jego zgodność z kadrem wymaga kontroli.

`node_ids` odpowiadają kolejnym wierzchołkom geometrii OSM. Zachowano całe źródłowe ways, aby nie tworzyć sztucznych końców sieci. `boundary_crossing` oznacza wyjście geometrii poza bbox. Nawet wtedy stopień węzła liczony w wycinku może pomijać drogę leżącą poza obszarem; most/tunel wymaga osobnego rozpatrzenia.

## Dalsza praca z plikami (opcjonalnie)

Z katalogu głównego repozytorium przejdź do danych:

```powershell
Set-Location course-materials/exercise-data/map-qa
```

Uruchom zapytania DuckDB z `profile.sql`. Pierwsza instalacja rozszerzenia spatial wymaga internetu; same dane są lokalne.

```powershell
uv run --python 3.12 profile_data.py
```

Sprawdź GeoPandas i przeliczenie do metrów:

```powershell
uv run --python 3.12 --with geopandas==1.2.0 --with pyarrow==23.0.1 python -c "import geopandas as gpd; r=gpd.read_parquet('osm_roads.parquet'); print(len(r), r.crs, r.geometry.is_valid.all(), r.to_crs(2180).crs)"
```

Rozpocznij od części offline. Downloader kopiuje zgodne pliki z `offline/`, a pozostałe pobiera. Zapisuje tylko do `data/photos/`; nie nadpisuje wejść.

```powershell
uv run --python 3.12 download_photos.py --limit 10
```

Pobierz cały przypięty zestaw, jeśli potrzebujesz szerszej próbki:

```powershell
uv run --python 3.12 download_photos.py
```

Sprawdź kompletność i hashe dostępnych zdjęć bez pobierania. Kod zakończenia 1 oznacza brakujące pliki; 2 oznacza błąd.

```powershell
uv run --python 3.12 download_photos.py --verify-only
```

Ponowne pobranie pomija pliki z poprawnym SHA-256. Niezgodny istniejący plik zatrzymuje pracę; przenieś go do osobnego katalogu do sprawdzenia. Nie zastępuj przypiętego hasha nowym bez ponownej oceny źródła. Panoramax jest pobierany jako SD i skalowany do maksymalnie 1024 px z Pillow 12.0.0; źródło i wynik mają osobne hashe. Mapillary używa niezmodyfikowanej `thumb_1024_url`. Zachowaj wersję Pillow; inna biblioteka JPEG może zmienić bajty przeskalowanego obrazu. Windows nie wymaga narzędzi konwersji OSM do pracy z dołączonym GeoParquet.

Adresy miniatur Mapillary mogą wygasnąć. Użyj wspólnego `MAPILLARY_TOKEN` ustawionego wcześniej w terminalu i odśwież adresy do osobnego manifestu. Nie wklejaj wartości tokenu do agenta ani pliku. Brak dostępu nie blokuje części offline.

```powershell
uv run --python 3.12 refresh_mapillary_urls.py --out data/photos-refreshed.csv
```

```powershell
uv run --python 3.12 download_photos.py --manifest data/photos-refreshed.csv
```

Odśwież drogi OSM i Overture do nowego katalogu. Pobranie PBF to około 203 MB; odczyt Overture korzysta z żądań zakresowych do dwóch większych partycji. Zarezerwuj kilka minut i co najmniej 2 GB wolnego miejsca na konwersję; czas zależy od łącza i maszyny. Skrypt pobiera aktualny PBF małopolskiego, konwertuje go przez pyosmium i GeoPandas oraz usuwa własny PBF po konwersji. DuckDB czyta przez HTTPS tylko partycje Overture przecinające obszar, z filtrem bbox. To ścieżka działająca przez uv bez WSL i conda; dołączone pliki pozwalają ją pominąć.

```powershell
uv run --python 3.12 refresh_sources.py --out data/refreshed
```

Pomoc i opcje małego wycinka, jednego źródła oraz własnego `--pbf`:

```powershell
uv run --python 3.12 refresh_sources.py --help
```

Nowe wydanie może zmienić atrybuty i identyfikatory. Nie łącz go bez sprawdzenia ze starym `photo_road_links.csv`. Ponownie wykonaj profil i własne dopasowanie. Skrypt nie rozwiązuje kontroli konfliktów ani łączenia zdjęć.

Wróć do katalogu głównego przed promptami ćwiczenia:

```powershell
Set-Location ../../..
```

## Pytania o zdjęcie i dane mapowe

| Pytanie | Co porównujesz po stronie mapy | Ograniczenie | Etykiety do accuracy |
|---|---|---|---|
| Rodzina klasy drogi | OSM `highway`, Overture `class` | Wygląd drogi sam nie ustala jej klasy funkcjonalnej. | Brak |
| Paved/unpaved | OSM `surface`, Overture `road_surface` | Reguły mogą dotyczyć tylko części segmentu. | `surface` |
| Skrzyżowanie widoczne | Topologia `node_ids`, Overture `connectors` | Węzeł nie dowodzi widoczności; liczy się poziom i kadr. | `junction_visible` |
| Znak ograniczenia i wartość | OSM `maxspeed:*`, Overture `speed_limits`, Mapillary `object_value` | Kierunek, odcinek obowiązywania, strefa i data wymagają kontroli. | Tylko wartość: `speed_limit_value` |
| Pasy w kierunku patrzenia | OSM `lanes`, `lanes:forward`, `lanes:backward` | `lanes` często oznacza sumę obu kierunków; panorama wymaga wyboru perspektywy. | Brak |
| Chodnik | OSM `sidewalk*` | Brak tagu pozostaje nieznany. | Brak |
| Oświetlenie | OSM `lit` | Widoczna lampa nie dowodzi działania instalacji. | `street_lighting_visible` |

`maxspeed` może być puste, tekstowe, wielokrotne albo z jednostką. Zachowaj surowe `maxspeed:*` w OSM oraz pola `when` i `between` reguł Overture; nie sprowadzaj ich do pierwszej liczby. Overture korzysta częściowo ze starszego OSM: w `sources` znajdziesz daty i wersje źródeł. Rozbieżność między snapshotami nie jest automatycznie błędem.

## Etykiety referencyjne do pomiaru jakości

Etykiety przygotował agent AI Codex na podstawie oglądu zdjęć; nie są w całości zweryfikowane przez człowieka. Traktuj je jako roboczą referencję. Każda niezgodność wymaga ręcznego obejrzenia zdjęcia przez człowieka.

`reference_labels.csv` opisuje widoczne cechy 100 obejrzanych zdjęć, bez werdyktów o mapie. Dla 80 zdjęć Panoramax oceniono nawierzchnię, widoczne skrzyżowanie i lampy uliczne. Dla 20 zdjęć Mapillary oceniono te same trzy pytania oraz odczyt wartości znaku. Nie każde zdjęcie ma pewną etykietę każdego pytania. Rodzina drogi, pasy, chodnik i osobne pytanie o samą widoczność znaku nie mają tu etykiet do accuracy; ich rozkłady i decyzje można przeglądać ręcznie, bez wymyślania wyników jakości.

Każdy wiersz zawiera `question`, `label`, `status`, metodę, osobę lub narzędzie oceniające i datę. `certain` dopuszcza wiersz do pomiaru danego pytania, `uncertain` oznacza wyłączenie z jawnym licznikiem. Pustej lub niepewnej etykiety nie zamieniaj na `no` ani `none`. W odczycie prędkości `none` oznacza brak widocznego znaku liczbowego, `unknown` niepewny odczyt. Nie przekazuj tych etykiet, detekcji ani atrybutów mapy do modelu oceniającego obraz.

Paved obejmuje asfalt, beton i kostkę. Skrzyżowanie oznacza widoczne połączenie lub rozdzielenie dróg dla pojazdów, nie samo przejście dla pieszych ani wiadukt. Oświetlenie oznacza rozpoznawalną oprawę lampy ulicznej w kadrze; sam słup energetyczny nie wystarcza. Przy wątpliwości zachowaj `unknown`. Obejrzyj sporne przykłady i zapisz korektę etykiety z powodem.

To mała próbka z nierównym rozkładem klas, bez gwarancji każdej nawierzchni i sceny. Dziel ją po `sequence`, nie po sąsiednich klatkach. Progi ustal przed końcową próbą. Nie wyciągaj wniosków o kalibracji lub przewadze modelu z kilku zdjęć.

[Licencje i atrybucja](ATTRIBUTION.md) obowiązują także w raportach, miniaturach i eksportach.

Dostęp do tych samych danych w chmurze opisuje [instrukcja Databricks](DATABRICKS.md). Osobiste konto nie jest wymagane.

## Zdjęcia znaków do M5 i M6: `signs/`

To osobny, celowo dobrany zestaw prawdziwych zdjęć z Polski, z przewagą Krakowa. Obejmuje czytelne okrągłe znaki ograniczenia prędkości B-33 oraz trudne negatywy: inne znaki zakazu, koniec ograniczenia, strefę i kadry bez widocznego ograniczenia. Rozkład nie reprezentuje częstości znaków na drogach. Nie zastępuje podstawowego manifestu `photos.csv` ani tabel Databricks.

| Plik | Znaczenie |
|---|---|
| `signs/signs.csv` | Identyfikator zdjęcia, obszar, współrzędne aparatu, data, kierunek aparatu, autor, sekwencja, licencja, link do źródła, detekcja Mapillary i hashe |
| `signs/photos/<photo_id>.jpg` | Pełny kadr, najdłuższy bok do 1600 px |
| `signs/crops/<photo_id>.jpg` | Wycinek prawdziwego zdjęcia wokół detekcji z marginesem; dla kadru bez znaku cały obraz |
| `signs/labels.csv` | Roboczy odczyt wycinka, status, metoda, oceniający i uwagi; wejście wyłącznie dla ewaluatora |
| `signs/nearest_osm.csv` | Kandydat drogi OSM, dystans, różnica kierunku, surowe tagi prędkości, daty, źródło i flagi dopasowania |
| `signs/build_signs.py` | Weryfikacja offline oraz odtworzenie brakujących zdjęć i wycinków z Mapillary |

Etykiety powstały przez odczyt agenta i niezależny odczyt ponumerowanych wycinków przez drugi model, GLM-5.3-Flash. To **robocza referencja, nie ground truth**. `certain` oznacza zgodność obu odczytów, a nie pewność terenową. Rozbieżności pozostają `uncertain` z uwagą. Wartość liczbowa dotyczy widocznego B-33 w wycinku; `none` oznacza brak takiego znaku, również przy widocznej liczbie na znaku strefy lub końca ograniczenia. `unreadable` oznacza, że wartości nie da się wiarygodnie odczytać. Negatyw dotyczy wycinka, więc w innym miejscu pełnego kadru może występować znak prędkości. `mapillary_value` jest wynikiem detektora dostawcy, a nie etykietą referencyjną. `mapillary_feature_id` wskazuje obiekt użyty do znalezienia zdjęcia, a `mapillary_detection_id` wybraną detekcję w obrazie. Wycinek obejmuje największą detekcję zgodnej klasy w kadrze; nie potwierdza tożsamości konkretnego znaku w 3D. Puste identyfikatory obiektu są poprawne dla kadrów pobranych z sekwencji i negatywów znalezionych bezpośrednio w detekcjach.

Do modelu w M6 wysyłaj tylko neutralny tekst pytania i bajty wycinka. Etykiety, identyfikatory, nazwy plików, wartości Mapillary i atrybuty OSM pozostają poza `state`. Porównanie z mapą następuje po odczycie. Zgodność liczby na zdjęciu z `maxspeed` nie rozstrzyga poprawności mapy: daty mogą się różnić, znak może dotyczyć innej jezdni, a kierunek aparatu nie jest kierunkiem jazdy.

Dopasowanie OSM używa metrycznego EPSG:2180 i metody z `photo_road_links.csv`: lokalny kierunek drogi w otoczeniu +/-5 m od rzutu aparatu, odległość kątowa względem obu kierunków drogi oraz ranking `distance_m + heading_diff_deg/9`. Przy braku kierunku składnik kierunkowy wynosi 5 m; remisy rozstrzyga dystans i identyfikator OSM. Podstawowy promień to 25 m, awaryjny 100 m; kandydat spoza 25 m ma flagę. Poza wycinkiem Krakowa źródłem jest oficjalne API OSM (`source=osm_api`): pobrano mały bbox i wybrano kandydatów do 150 m. Overpass zwracał HTTP 502 lub przekraczał timeout; nie podstawiano pustych odpowiedzi ani wymyślonych tagów. Alternatywy o wyniku różniącym się o mniej niż 2 m oznaczono jako niejednoznaczne. To kandydaci do przeglądu. Daty `osm_timestamp` dotyczą wersji drogi, a `osm_snapshot_timestamp` daty źródłowego snapshotu. API OSM nie podaje daty repliki: dla `osm_api` pole snapshotu jest puste, a czas pobrania zapisano osobno w `context_retrieved_at`. Tagi kierunkowe są względem kolejności węzłów OSM.

Weryfikacja wszystkich hashy, spójności identyfikatorów i limitu rozmiaru, bez tokenu i bez sieci:

```powershell
uv run --python 3.12 course-materials/exercise-data/map-qa/signs/build_signs.py --verify-only
```

Odtworzenie brakujących plików wymaga `MAPILLARY_TOKEN` w środowisku; skrypt odświeża `thumb_2048_url` przez Graph API. Nie wypisuj tokenu ani nie zapisuj go w repozytorium.

```powershell
uv run --python 3.12 course-materials/exercise-data/map-qa/signs/build_signs.py
```

`source_sha256` identyfikuje pobraną miniaturę przed transformacją, `sha256` pełny kadr po skalowaniu, a `crop_sha256` wycinek. `crop_bbox_px` to `[left, top, right, bottom]` w pikselach miniatury źródłowej, z początkiem w lewym górnym rogu, prawą i dolną granicą wyłączną. Detekcje są zdekodowane z base64/MVT z zachowaniem osi Y obrazu. Kadry zapisano jako JPEG quality 82, wycinki quality 92, Pillow 12.0.0. Zmianami są wyłącznie skalowanie, wycięcie i ponowny zapis JPEG. Zmiana miniatury u dostawcy lub biblioteki JPEG zatrzyma odtwarzanie na niezgodnym hashu; istniejące niespójne pliki nie są nadpisywane. Etykiety i kontekst OSM są przypiętym snapshotem, skrypt nie przelicza ich przy odtwarzaniu zdjęć.
