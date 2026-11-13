# Raport kontroli mapy: atrybuty dróg OSM i Overture (Kraków)

> Odczyt zdjęcia jest predykcją modelu, a nie weryfikacją terenową. Rozbieżność źródeł nie oznacza automatycznie błędu mapy.

Krótkie podsumowanie: `summary.html` w tym samym katalogu.

### Słowniczek

- **Tier 1**: model decyzyjny (openai/gpt-6-luna-decisions) zwraca zamkniętą odpowiedź z prawdopodobieństwem każdej opcji; odpowiedź z max(p) ≥ progu T1 jest przyjmowana (\`answered\`).
- **Tier 2**: ogólny LLM (openai/gpt-6-luna, rozumowanie medium) dostaje ten sam obraz i tylko pytania, przy których tier 1 był niepewny albo odpowiedział \`unknown\`; sam ocenia pewność (high/medium/low). Przyjmowane jest tylko \`high\` (\`answered_tier2\`).
- **Model porównawczy**: typesafe/jev-1.14 odpowiada na te same pytania dla 5 obrazów, tylko na poziomie tier 1, żeby porównać dwa modele decyzyjne.
- **abstain**: żaden poziom nie dał pewnej odpowiedzi; pozycja trafia do kolejki ręcznej.
- **model_unavailable**: błąd API, timeout albo niepoprawna odpowiedź; nigdy nie jest zamieniany na odpowiedź. Po pierwszym błędzie kolejne płatne wywołania są wstrzymane.
- **not_run_budget_or_error**: pytanie nie zostało wysłane, bo skończył się limit żądań lub kosztu albo wcześniej wystąpił błąd.
- **agree / disagree**: OSM i Overture mają po jednej bezwarunkowej wartości dla całego odcinka; są zgodne lub różne. Zgodność oznacza zgodność snapshotów (Overture w 99% pochodzi z OSM).
- **missing_osm / missing_overture**: brak tagu lub reguły po danej stronie; brak nigdy nie jest liczony jako 0.
- **not_comparable**: wartości nie da się uczciwie porównać: reguła warunkowa, kierunkowa, dotyczy części odcinka (\`between\`), limit tylko typem (np. PL:urban) albo nieznana wartość.
- **ambiguous_link**: połączenie zdjęcia z drogą jest niepewne (np. kilku podobnych kandydatów); para trafia do kolejki ręcznej i nie dostaje agree/disagree.
- **Etykieta referencyjna**: Etykiety referencyjne przygotowały agenty AI: zdjęcia ulic oznaczył Codex, a wycinki znaków to zgodny odczyt dwóch modeli (Codex i GLM-5.3-Flash). Etykiety nie zostały zweryfikowane przez człowieka, więc accuracy oznacza zgodność z roboczą referencją AI, a nie poprawność terenową.

## 1. Nagłówek

- Data uruchomienia: 2026-11-13T00:39:15+00:00 (identyfikator: `20261113T003915Z-cef01d`)
- Data wygenerowania raportu: 2026-11-13
- Źródło danych: pliki lokalne
- Snapshot OSM: 2026-11-01; wydanie Overture: 2026-10-21.0

### Tabele wejściowe

| Tabela | Wiersze | statement_id |
|---|---:|---|
| osm_roads | 99768 | – |
| overture_segments | 85405 | – |
| photos | 561 | – |
| photo_road_links | 561 | – |
| signs | 119 | – |
| signs_nearest_osm | 119 | – |

### Hashe plików wejściowych (sha256)

| Plik | sha256 | Zgodność z sources.json |
|---|---|---|
| sources.json | `29133842006f84c90a94291d267fab95d58509c2721db097b213370ab9e7e50b` | brak wzorca |
| osm_roads.parquet | `b429a97aef4e9e9f6c9cf760081a215eeb14cdc97b678812730a318b0e61d32b` | exact |
| overture_segments.parquet | `cf4ee780992cfab94eeda799ef6aa6ee67c86539d14aef572e937b35b8259760` | exact |
| photos.csv | `9cc6b79f5fc147a774e43fb685db61b5bc3e2e2d15c38daa4cf665ba6e657e9c` | lf_normalized |
| photo_road_links.csv | `d71d0857ae0ffc3eeae395a67d2f9ea2bcb869e1fab44c222d2755e60e70763b` | lf_normalized |
| signs/signs.csv | `a3d3f29fa676c44e6be684abb9d3ea6f91bd439c81e4a373596a4de29e5a6c2f` | brak wzorca |
| signs/nearest_osm.csv | `52baf1291906a5e86344198aea18bec724b38a5877a4a041e336a38df3e1dea3` | brak wzorca |
| reference_labels.csv | `67a3259d39801078a144ffb8088d15f882dbc16f6cba27a249f83d2a7d420d83` | brak wzorca |
| signs/labels.csv | `a25b37d9d65dd824413cfe1d6d9b797e951d179f3e87b89dd75789959046ca32` | brak wzorca |
| data/photos/panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35.jpg | `20f9aa36e93d762df897d8b7c594eed327664f8fd945e7e8d802aaaee79f5d25` | brak wzorca |
| data/photos/panoramax_c429dd85-f700-4095-b670-90b3bb617875.jpg | `5dc09e9240fecb85db1b878ded339941067afa219a98b9da4b5c61d633bce598` | brak wzorca |
| data/photos/panoramax_3c683354-2386-456b-9955-31268ecb5213.jpg | `88269b6775044e2ec16139285d0e90c068abc33674610d9d43eadf819a6465bf` | brak wzorca |
| data/photos/panoramax_9bc04785-ce54-4104-8114-bc3b7155f6e9.jpg | `92367db5365dd8340616f003cd649b8bdede44800fa2c26305932121309e3e26` | brak wzorca |
| data/photos/panoramax_66200c29-f302-4a7c-940b-dc11ad3d5322.jpg | `56d79fb571bf718f42fda46e7d7204a1daf05d619c66c5fbfef4ef45fb68724b` | brak wzorca |
| data/photos/panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928.jpg | `7b57d5a279e7abc76976d4cd3beff0c30ba44bd3089281d074fd4b48fc099bc9` | brak wzorca |
| data/photos/panoramax_12f760a9-5f52-4092-be47-47b2481ceed8.jpg | `1217d0547de54bce7584ccd0c9b1c0dc38fcc18c6876a3daa8bf475d60c04e51` | brak wzorca |
| data/photos/panoramax_90d265a8-5897-4e57-a2e3-698444eb64af.jpg | `5e1d45c32f5a1ab4311e9f0a962fa0e4ebea7531b53053c11494d5e4d314ad4d` | brak wzorca |
| data/photos/panoramax_b35a913d-cbc1-48d5-95bb-140a77cc2f1f.jpg | `d3f460a49525319f86e12fb637482a9310df32e1944f1e0dbbf517c7f64ffb7f` | brak wzorca |
| data/photos/panoramax_7f42b279-bd01-492b-bddb-ba2e14a606be.jpg | `1ce916cda344f6790ec6bc4721addbfb22055f0b302848f2843ec16e64c5e7fd` | brak wzorca |
| data/photos/panoramax_2b72cfab-b9f8-49db-8278-cbaa3a8fc8ff.jpg | `f2af382a5831f3c38dd4a17031b34de775aaabeaa16cab02ed921d699647e5d4` | brak wzorca |
| data/photos/panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc.jpg | `25a4eaf55ade8b02e2eda624863478258880d1a69e18d069a2188ef8e4a8bed2` | brak wzorca |
| data/photos/panoramax_b57e68f4-1d4f-4208-82fa-4b36294deb2c.jpg | `9b4744f8f4db2eee93309291ed34bc99b5bcb6868a48ce04385737d863e7bb39` | brak wzorca |
| data/photos/panoramax_7952c236-c745-4200-b72d-59b04381f790.jpg | `6c015a5da6a0c6d0df60b6afb85677298d436760c323c7d7ef8cd5dbec74ddb7` | brak wzorca |
| data/photos/panoramax_8734e4cf-4a2f-414e-b750-c0519374dd0a.jpg | `9e13f4da62ff18f3097d738c3deb5c5d167f8321f27ef00f9cddc7fc47d87b2d` | brak wzorca |
| signs/crops/mapillary_3501212013437933.jpg | `48f5900e128a4404a23422305c31ab0369759194b0460659cc883de59e364d65` | brak wzorca |
| signs/crops/mapillary_374349654072798.jpg | `aa1db923d2c5fa1ddacc9bdb083bb492fafc1d347e0be220221d4d11a0fc6b4a` | brak wzorca |
| signs/crops/mapillary_557443477317070.jpg | `ea17587bbbb04bb8358b1d88551d981c9c2275859ac4eaf5b918ecc513484037` | brak wzorca |
| signs/crops/mapillary_318047947631010.jpg | `9b98bb556e9b1962734c6513aa1a17b5d58955094f62cf41863e2fd386e38671` | brak wzorca |
| signs/crops/mapillary_1035052394661534.jpg | `818fb0e7f39b0b0bc9b306fcc347b92dc58f6eebb990b22480b08fb64cf312c1` | brak wzorca |
| signs/crops/mapillary_1029602998981114.jpg | `dd3ddfb2405db7756af572a9cde7cca7e9f26a1b21481e16bf59fe1faabf4823` | brak wzorca |
| signs/crops/mapillary_512030746965559.jpg | `f1b63cc1ec5245a52763524f853d730d2ed2f088a4ce8b16067c6b224ce3686e` | brak wzorca |
| signs/crops/mapillary_962672327639677.jpg | `b8ef2cde19f43e974bf6d2ddac14b9187b21082acbb196ab3c9e88e7a27366b0` | brak wzorca |
| signs/crops/mapillary_1152877773579493.jpg | `06afe8e674989c55659771f9af8ce275cce3c17b8e61ec19cd72bd6868766be8` | brak wzorca |
| signs/crops/mapillary_2601761200243412.jpg | `4a1aa299c9752a4ae25a6f2fdd55d8bcd0d0498a6e0ff26d1edd010fbe5c64bd` | brak wzorca |

### Konfiguracja

| Ustawienie | Wartość |
|---|---|
| source | files |
| output_dir | reports\\map-qa |
| model_reading | True |
| max_images | 25 |
| max_requests | 100 |
| max_cost_usd | 1.0 |
| tier1_model | openai/gpt-6-luna-decisions |
| compare_model | typesafe/jev-1.14 |
| tier2_model | openai/gpt-6-luna |
| t1_threshold | 0.8 |
| t1_threshold_compare | 0.8 |
| tier2_accept | high |
| timeout_s | 40 |
| question_set_version | qs-v1 |
| seed | 42 |

## 2. Podsumowanie

- Zdjęcia: 561; pary zdjęcie–droga: 558; zdjęcia bez kandydata: 3
- Status połączeń: `ambiguous` 65; `no_candidate` 3; `ok` 493

### Statusy porównania (na parę i atrybut; suma dla atrybutu = liczba par)

| Atrybut | Status | Opis | Liczba |
|---|---|---|---:|
| `speed` | `agree` | zgodne | 391 |
| `speed` | `disagree` | rozbieżne | 2 |
| `speed` | `missing_osm` | brak w OSM | 14 |
| `speed` | `missing_overture` | brak w Overture | 0 |
| `speed` | `not_comparable` | nieporównywalne | 86 |
| `speed` | `ambiguous_link` | niepewne połączenie | 65 |
| `surface` | `agree` | zgodne | 486 |
| `surface` | `disagree` | rozbieżne | 0 |
| `surface` | `missing_osm` | brak w OSM | 3 |
| `surface` | `missing_overture` | brak w Overture | 0 |
| `surface` | `not_comparable` | nieporównywalne | 4 |
| `surface` | `ambiguous_link` | niepewne połączenie | 65 |

Zgodność OSM–Overture to zgodność snapshotów (Overture w 99% pochodzi z OSM), a nie potwierdzenie poprawności.

### Statusy per droga (`osm_way_id`)

Liczba dróg z co najmniej jednym zdjęciem: 230. Tabela pokazuje drogi z więcej niż jednym zdjęciem (112).

| osm_way_id | Zdjęcia | Prędkość | Nawierzchnia |
|---:|---:|---|---|
| 224904420 | 55 | agree 55 | agree 55 |
| 19801635 | 27 | agree 27 | agree 27 |
| 255959691 | 22 | agree 22 | agree 22 |
| 224933520 | 12 | agree 12 | agree 12 |
| 224930848 | 9 | agree 8, ambiguous_link 1 | agree 8, ambiguous_link 1 |
| 1528881369 | 9 | agree 9 | agree 9 |
| 886738504 | 8 | not_comparable 8 | agree 8 |
| 224904418 | 7 | agree 7 | agree 7 |
| 277973487 | 7 | agree 6, ambiguous_link 1 | agree 6, ambiguous_link 1 |
| 224814473 | 6 | agree 6 | agree 6 |
| 224814475 | 6 | agree 6 | agree 6 |
| 346304716 | 6 | agree 6 | agree 6 |
| 648056850 | 6 | agree 6 | agree 6 |
| 1232329075 | 6 | ambiguous_link 6 | ambiguous_link 6 |
| 1544043039 | 6 | ambiguous_link 6 | ambiguous_link 6 |
| 75233260 | 5 | not_comparable 5 | agree 5 |
| 224928186 | 5 | agree 5 | agree 5 |
| 346304298 | 5 | agree 2, ambiguous_link 3 | agree 2, ambiguous_link 3 |
| 431783000 | 5 | agree 5 | agree 5 |
| 431783005 | 5 | agree 5 | agree 5 |
| 431783017 | 5 | agree 5 | agree 5 |
| 648167637 | 5 | agree 4, ambiguous_link 1 | agree 4, ambiguous_link 1 |
| 19801715 | 4 | agree 4 | agree 4 |
| 224928189 | 4 | agree 4 | agree 4 |
| 346302165 | 4 | agree 3, ambiguous_link 1 | agree 3, ambiguous_link 1 |
| 554959810 | 4 | not_comparable 4 | agree 4 |
| 928798075 | 4 | agree 4 | agree 4 |
| 928798141 | 4 | agree 4 | agree 4 |
| 1206241891 | 4 | agree 4 | agree 4 |
| 1416953488 | 4 | not_comparable 4 | agree 4 |
| 20192486 | 3 | agree 3 | agree 3 |
| 22765563 | 3 | agree 3 | agree 3 |
| 26432962 | 3 | agree 3 | agree 3 |
| 62827236 | 3 | ambiguous_link 1, not_comparable 2 | agree 2, ambiguous_link 1 |
| 184234823 | 3 | agree 3 | agree 3 |
| 224804652 | 3 | agree 3 | agree 3 |
| 224928188 | 3 | agree 3 | agree 3 |
| 312565747 | 3 | agree 3 | agree 3 |
| 453815970 | 3 | agree 3 | agree 3 |
| 648056847 | 3 | agree 3 | agree 3 |
| 741997695 | 3 | agree 1, ambiguous_link 2 | agree 1, ambiguous_link 2 |
| 798376719 | 3 | not_comparable 3 | agree 3 |
| 886690955 | 3 | agree 3 | agree 3 |
| 1206241059 | 3 | not_comparable 3 | agree 3 |
| 1212676722 | 3 | ambiguous_link 3 | ambiguous_link 3 |
| 1416953493 | 3 | ambiguous_link 1, missing_osm 2 | agree 2, ambiguous_link 1 |
| 1421878189 | 3 | agree 3 | agree 3 |
| 4757978 | 2 | agree 2 | agree 2 |
| 20192624 | 2 | agree 2 | agree 2 |
| 22939418 | 2 | agree 2 | agree 2 |
| 24557421 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 25042175 | 2 | agree 2 | agree 2 |
| 25156656 | 2 | agree 2 | agree 2 |
| 26302267 | 2 | agree 2 | agree 2 |
| 31876773 | 2 | ambiguous_link 2 | ambiguous_link 2 |
| 42289812 | 2 | missing_osm 2 | agree 2 |
| 71942595 | 2 | agree 2 | agree 2 |
| 74887291 | 2 | agree 2 | agree 2 |
| 93576413 | 2 | missing_osm 2 | agree 2 |
| 93576795 | 2 | missing_osm 2 | agree 2 |
| 95943483 | 2 | agree 2 | agree 2 |
| 107637016 | 2 | agree 2 | agree 2 |
| 116896207 | 2 | agree 2 | agree 2 |
| 127052516 | 2 | ambiguous_link 1, not_comparable 1 | agree 1, ambiguous_link 1 |
| 127905157 | 2 | not_comparable 2 | agree 2 |
| 162844467 | 2 | agree 2 | agree 2 |
| 174531243 | 2 | agree 2 | agree 2 |
| 187014751 | 2 | agree 2 | agree 2 |
| 188660834 | 2 | agree 2 | agree 2 |
| 207394293 | 2 | not_comparable 2 | agree 2 |
| 224604345 | 2 | ambiguous_link 1, not_comparable 1 | agree 1, ambiguous_link 1 |
| 224604348 | 2 | agree 2 | agree 2 |
| 224867537 | 2 | agree 2 | agree 2 |
| 224870485 | 2 | agree 2 | agree 2 |
| 224870487 | 2 | agree 2 | agree 2 |
| 224904414 | 2 | agree 2 | agree 2 |
| 224933518 | 2 | agree 2 | agree 2 |
| 237284260 | 2 | missing_osm 2 | agree 2 |
| 345738511 | 2 | not_comparable 2 | agree 2 |
| 364882602 | 2 | agree 2 | agree 2 |
| 376942759 | 2 | ambiguous_link 1, missing_osm 1 | agree 1, ambiguous_link 1 |
| 402185154 | 2 | agree 2 | agree 2 |
| 415389038 | 2 | not_comparable 2 | not_comparable 2 |
| 453815971 | 2 | agree 2 | agree 2 |
| 461095410 | 2 | agree 2 | agree 2 |
| 553075598 | 2 | not_comparable 2 | agree 2 |
| 566097541 | 2 | not_comparable 2 | agree 2 |
| 580591250 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 598412910 | 2 | disagree 2 | agree 2 |
| 645042637 | 2 | not_comparable 2 | agree 2 |
| 648167636 | 2 | agree 2 | agree 2 |
| 759687117 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 793471788 | 2 | agree 2 | agree 2 |
| 860389162 | 2 | not_comparable 2 | agree 2 |
| 878860212 | 2 | agree 2 | agree 2 |
| 911436916 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 1085834204 | 2 | agree 2 | agree 2 |
| 1096510287 | 2 | not_comparable 2 | agree 2 |
| 1096510288 | 2 | not_comparable 2 | agree 2 |
| 1096510289 | 2 | not_comparable 2 | agree 2 |
| 1096511436 | 2 | not_comparable 2 | agree 2 |
| 1206240642 | 2 | ambiguous_link 1, not_comparable 1 | agree 1, ambiguous_link 1 |
| 1206240643 | 2 | not_comparable 2 | agree 2 |
| 1206276880 | 2 | not_comparable 2 | agree 2 |
| 1206278491 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 1227959523 | 2 | agree 2 | agree 2 |
| 1303332150 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 1303332151 | 2 | ambiguous_link 1, not_comparable 1 | agree 1, ambiguous_link 1 |
| 1340862610 | 2 | agree 2 | agree 2 |
| 1353158955 | 2 | ambiguous_link 2 | ambiguous_link 2 |
| 1417718040 | 2 | agree 1, ambiguous_link 1 | agree 1, ambiguous_link 1 |
| 1562739372 | 2 | not_comparable 2 | agree 2 |

### Kompletność atrybutów

| Źródło | Atrybut | Populacja | Z wartością | Mianownik | % |
|---|---|---|---:|---:|---:|
| osm | maxspeed* | wszystkie drogi | 17963 | 99768 | 18.0% |
| osm | maxspeed* | drogi ze zdjęciem | 219 | 230 | 95.2% |
| osm | surface | wszystkie drogi | 39566 | 99768 | 39.7% |
| osm | surface | drogi ze zdjęciem | 226 | 230 | 98.3% |
| osm | lit | wszystkie drogi | 15589 | 99768 | 15.6% |
| osm | lit | drogi ze zdjęciem | 97 | 230 | 42.2% |
| osm | lanes | wszystkie drogi | 11279 | 99768 | 11.3% |
| osm | lanes | drogi ze zdjęciem | 208 | 230 | 90.4% |
| osm | sidewalk* | wszystkie drogi | 12640 | 99768 | 12.7% |
| osm | sidewalk* | drogi ze zdjęciem | 105 | 230 | 45.7% |
| overture | speed_limits | wszystkie drogi | 12847 | 85405 | 15.0% |
| overture | speed_limits | drogi ze zdjęciem | 127 | 139 | 91.4% |
| overture | road_surface | wszystkie drogi | 32108 | 85405 | 37.6% |
| overture | road_surface | drogi ze zdjęciem | 136 | 139 | 97.8% |

### Odczyt modelem

- Żądania w tym uruchomieniu: 0 (limit 100); koszt: 0 USD (limit 1.00 USD)
- Koszt wszystkich odpowiedzi użytych w raporcie (łącznie z odpowiedziami z cache): 0.0049 USD; openai/gpt-6-luna 0.0019, openai/gpt-6-luna-decisions 0.0024, typesafe/jev-1.14 0.0006- Odpowiedzi z cache: 43; suma historyczna w ledgerze: 72 żądań, 0.0076 USD
- W tym uruchomieniu nie wykonano nowych żądań (licznik żądań = 0).

| Pytanie | Decyzja | Opis | Liczba |
|---|---|---|---:|
| `surface` | `answered` | odpowiedź tier 1 | 15 |
| `surface` | `answered_tier2` | odpowiedź tier 2 | 0 |
| `surface` | `abstain` | abstencja (kolejka ręczna) | 0 |
| `surface` | `model_unavailable` | model niedostępny | 0 |
| `surface` | `not_run_budget_or_error` | nie uruchomiono (limit lub błąd) | 0 |
| `junction_visible` | `answered` | odpowiedź tier 1 | 13 |
| `junction_visible` | `answered_tier2` | odpowiedź tier 2 | 0 |
| `junction_visible` | `abstain` | abstencja (kolejka ręczna) | 2 |
| `junction_visible` | `model_unavailable` | model niedostępny | 0 |
| `junction_visible` | `not_run_budget_or_error` | nie uruchomiono (limit lub błąd) | 0 |
| `street_lighting_visible` | `answered` | odpowiedź tier 1 | 11 |
| `street_lighting_visible` | `answered_tier2` | odpowiedź tier 2 | 3 |
| `street_lighting_visible` | `abstain` | abstencja (kolejka ręczna) | 1 |
| `street_lighting_visible` | `model_unavailable` | model niedostępny | 0 |
| `street_lighting_visible` | `not_run_budget_or_error` | nie uruchomiono (limit lub błąd) | 0 |
| `speed_limit_value` | `answered` | odpowiedź tier 1 | 2 |
| `speed_limit_value` | `answered_tier2` | odpowiedź tier 2 | 6 |
| `speed_limit_value` | `abstain` | abstencja (kolejka ręczna) | 2 |
| `speed_limit_value` | `model_unavailable` | model niedostępny | 0 |
| `speed_limit_value` | `not_run_budget_or_error` | nie uruchomiono (limit lub błąd) | 0 |

| Model | Poziom | Pytanie | Żądania | Koszt [USD] | Z cache |
|---|---|---|---:|---:|---:|
| openai/gpt-6-luna | tier2 | junction_visible | 0 | 0.0000 | 2 |
| openai/gpt-6-luna | tier2 | speed_limit_value | 0 | 0.0000 | 8 |
| openai/gpt-6-luna | tier2 | street_lighting_visible | 0 | 0.0000 | 4 |
| openai/gpt-6-luna-decisions | tier1 | junction_visible | 0 | 0.0000 | 15 |
| openai/gpt-6-luna-decisions | tier1 | speed_limit_value | 0 | 0.0000 | 10 |
| openai/gpt-6-luna-decisions | tier1 | street_lighting_visible | 0 | 0.0000 | 15 |
| openai/gpt-6-luna-decisions | tier1 | surface | 0 | 0.0000 | 15 |
| typesafe/jev-1.14 | compare | junction_visible | 0 | 0.0000 | 3 |
| typesafe/jev-1.14 | compare | speed_limit_value | 0 | 0.0000 | 2 |
| typesafe/jev-1.14 | compare | street_lighting_visible | 0 | 0.0000 | 3 |
| typesafe/jev-1.14 | compare | surface | 0 | 0.0000 | 3 |

## 3. Kandydaci do przeglądu

Pary ze statusem `disagree`, `missing_*`, `not_comparable` lub `ambiguous_link`. Dystans w metrach, liczony w EPSG:2180.

### Ograniczenie prędkości: rozbieżne (`speed` / `disagree`): 2

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| panoramax_2995ca7e-714d-439d-9aab-a06b555f0d73 | 598412910 | 5d3395bb-3e07-4f4b-90a1-663508523d2b | 1.55 | maxspeed=100; maxspeed:bus=70 | {"max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.181806521, 1.0], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus"]}} | – | delta_kmh=50 | – | [miniatura](thumbs/panoramax_2995ca7e-714d-439d-9aab-a06b555f0d73.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_81e3f01a-e9e8-4339-b4f6-8120f27eaa6f | 598412910 | b4c619ab-a19e-47ea-9bbf-444881e9a09c | 3.33 | maxspeed=100; maxspeed:bus=70 | {"max_speed": {"unit": "km/h", "value": 50}}; {"max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus"]}} | – | delta_kmh=50 | – | [miniatura](thumbs/panoramax_81e3f01a-e9e8-4339-b4f6-8120f27eaa6f.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |

### Ograniczenie prędkości: brak w OSM (`speed` / `missing_osm`): 14

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| mapillary_1003606477244774 | 93576795 | 5f14044e-fc26-4380-8e74-83e92e56ea4f | 2.59 | – | – | – | no_osm_speed | – | [miniatura](thumbs/mapillary_1003606477244774.jpg); Grzesiekk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1393481265317315 | 42289812 | 09d2c3a7-a134-4e5b-bf22-179f0b7929e8 | 4.55 | – | – | – | no_osm_speed | – | [miniatura](thumbs/mapillary_1393481265317315.jpg); st1, Mapillary, CC-BY-SA-4.0 |
| mapillary_1842605739645573 | 42289812 | 09d2c3a7-a134-4e5b-bf22-179f0b7929e8 | 4.39 | – | – | – | no_osm_speed | – | [miniatura](thumbs/mapillary_1842605739645573.jpg); st1, Mapillary, CC-BY-SA-4.0 |
| mapillary_212616641510518 | 93576413 | ee609914-39cf-439e-aa85-c1132c16f361 | 1.32 | – | – | – | no_osm_speed | boundary_crossing | [miniatura](thumbs/mapillary_212616641510518.jpg); Grzesiekk, Mapillary, CC-BY-SA-4.0 |
| mapillary_224324516912032 | 93576413 | ee609914-39cf-439e-aa85-c1132c16f361 | 0.97 | – | – | – | no_osm_speed | boundary_crossing | [miniatura](thumbs/mapillary_224324516912032.jpg); Grzesiekk, Mapillary, CC-BY-SA-4.0 |
| mapillary_519455719068271 | 237284260 | c8cdc0f5-3a0d-4663-9a8d-762326fede2a | 13.72 | – | – | – | no_osm_speed | service_or_restricted | [miniatura](thumbs/mapillary_519455719068271.jpg); mik007, Mapillary, CC-BY-SA-4.0 |
| mapillary_640597110322444 | 237284260 | c8cdc0f5-3a0d-4663-9a8d-762326fede2a | 18.75 | – | – | – | no_osm_speed | poor_heading_alignment, service_or_restricted | [miniatura](thumbs/mapillary_640597110322444.jpg); ekeshkekesh, Mapillary, CC-BY-SA-4.0 |
| mapillary_6870106683018723 | 93576795 | 5f14044e-fc26-4380-8e74-83e92e56ea4f | 1.96 | – | – | – | no_osm_speed | – | [miniatura](thumbs/mapillary_6870106683018723.jpg); Grzesiekk, Mapillary, CC-BY-SA-4.0 |
| panoramax_30f08d1e-fe31-42d9-b042-607f5237d9ff | 1200858206 | d5824a89-6f63-4f2f-b0bb-0ed6865f3073 | 5.45 | – | – | – | no_osm_speed | service_or_restricted | [miniatura](thumbs/panoramax_30f08d1e-fe31-42d9-b042-607f5237d9ff.jpg); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_a7549660-666d-488e-baf3-da6e8fc3ec1c | 376942759 | 5a3a1758-8f05-4a64-8669-2324eeb44d5f | 2.92 | – | – | – | no_osm_speed | service_or_restricted | [miniatura](thumbs/panoramax_a7549660-666d-488e-baf3-da6e8fc3ec1c.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_aceb35b9-f936-4e90-8f06-8c7ad26eaee9 | 1442019083 | 21addaad-ffc9-40c7-8c8d-4e091311ccfd | 10.87 | – | – | – | no_osm_speed | service_or_restricted | [miniatura](thumbs/panoramax_aceb35b9-f936-4e90-8f06-8c7ad26eaee9.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_bebb9895-d14c-4a06-8ea7-cad7740f7764 | 137367264 | 5370bf93-8afd-436b-a3ef-8ab02d1004ab | 2.03 | – | – | – | no_osm_speed | poor_heading_alignment, service_or_restricted | Miniatura niedostępna (metadane źródła (API Panoramax): https://api.panoramax.xyz/api/collections/dffbd42c-e039-4124-81ae-ef5dcb67071d/items/bebb9895-d14c-4a06-8ea7-cad7740f7764); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_c1f8fab6-6f78-428c-a71d-765e1dd42c6a | 1416953493 | d08628d6-5fc5-4bee-8d12-59f0fc380f52 | 3.86 | – | – | – | no_osm_speed | – | [miniatura](thumbs/panoramax_c1f8fab6-6f78-428c-a71d-765e1dd42c6a.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_cfb8e8d4-6ad6-40b3-925e-82f34b3accba | 1416953493 | a04366e6-608e-48ca-b380-e99db77a7901 | 9.62 | – | – | – | no_osm_speed | – | [miniatura](thumbs/panoramax_cfb8e8d4-6ad6-40b3-925e-82f34b3accba.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |

### Ograniczenie prędkości: brak w Overture (`speed` / `missing_overture`): 0

Brak kandydatów (0).

### Ograniczenie prędkości: nieporównywalne (`speed` / `not_comparable`): 86

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| mapillary_1058045142243853 | 62827236 | ee3df361-b8b4-45a7-9788-90e67979738e | 0.57 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"between": [0.0, 0.11885873], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.11885873, 0.217176545], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.217176545, 0.550570159], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.550570159, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.0, 0.11885873], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.11885873, 0.217176545], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.550570159, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/mapillary_1058045142243853.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1080932238035806 | 687695011 | 3e2f0886-2f7a-4ee6-a86d-a663bb69fe71 | 1.13 | maxspeed=50; source:maxspeed=PL:urban | {"between": [0.0, 0.616427718], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.616427718, 1.0], "max_speed": {"unit": "km/h", "value": 40}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/mapillary_1080932238035806.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1237130608489136 | 557114409 | 4e084795-6ce9-4452-b65f-aaec7d3c0150 | 0.90 | maxspeed:backward=70; maxspeed:forward=50; source:maxspeed=sign | {"between": [0.0, 0.077742754], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.077742754, 0.814772815], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.977989716, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | osm:directional_differs | – | [miniatura](thumbs/mapillary_1237130608489136.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1435689471736379 | 415389038 | 4603b5a2-39ac-467e-9649-9c6d3000c509 | 3.40 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.255205349], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.255205349, 0.764456374], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764456374, 0.843520295], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.929497155, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1435689471736379.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1579175039923177 | 345738511 | 675829f3-1b1b-4682-aedf-265561667457 | 5.01 | maxspeed=30; source:maxspeed=sign | {"between": [0.07042085, 0.382507716], "max_speed": {"unit": "km/h", "value": 30}}; {"between": [0.839556532, 1.0], "max_speed": {"unit": "km/h", "value": 30}}; {"between": [0.0, 0.07042085], "max_speed": {"unit": "km/h", "value": 30}, "when": {"heading": "backward"}}; {"between": [0.0, 0.07042085], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}}; {"between": [0.382507716, 0.839556532], "max_speed": {"unit": "km/h", "value": 30}, "when": {"heading": "backward"}}; {"between": [0.382507716, 0.839556532], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1579175039923177.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1646871825800345 | 224604345 | b5c6ecae-209e-4437-b13d-d9b8004084c8 | 4.07 | maxspeed=90 | {"between": [0.0, 0.621463223], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.621463223, 1.0], "max_speed": {"unit": "km/h", "value": 90}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1646871825800345.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_1681793919659739 | 127052516 | e6875857-2d94-419b-9dd9-87b7904d3c5d | 2.78 | maxspeed=50; maxspeed:type=sign; source:maxspeed=PL:urban | {"between": [0.0, 0.337038167], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.337038167, 1.0], "max_speed": {"unit": "km/h", "value": 70}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1681793919659739.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_1703614410947032 | 645042637 | 29fd1419-7545-4fcb-866f-112a334fbd87 | 0.10 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.896136742], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.896136742, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1703614410947032.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1970607046823232 | 345738511 | 675829f3-1b1b-4682-aedf-265561667457 | 5.25 | maxspeed=30; source:maxspeed=sign | {"between": [0.07042085, 0.382507716], "max_speed": {"unit": "km/h", "value": 30}}; {"between": [0.839556532, 1.0], "max_speed": {"unit": "km/h", "value": 30}}; {"between": [0.0, 0.07042085], "max_speed": {"unit": "km/h", "value": 30}, "when": {"heading": "backward"}}; {"between": [0.0, 0.07042085], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}}; {"between": [0.382507716, 0.839556532], "max_speed": {"unit": "km/h", "value": 30}, "when": {"heading": "backward"}}; {"between": [0.382507716, 0.839556532], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1970607046823232.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_238748672088703 | 62827236 | ee3df361-b8b4-45a7-9788-90e67979738e | 0.32 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"between": [0.0, 0.11885873], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.11885873, 0.217176545], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.217176545, 0.550570159], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.550570159, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.0, 0.11885873], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.11885873, 0.217176545], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.550570159, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/mapillary_238748672088703.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_27611377485196534 | 1424754317 | 4e084795-6ce9-4452-b65f-aaec7d3c0150 | 1.22 | maxspeed=50; source:maxspeed=PL:urban | {"between": [0.0, 0.077742754], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.077742754, 0.814772815], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.977989716, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_27611377485196534.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_28658384260521108 | 24329784 | 3e2f0886-2f7a-4ee6-a86d-a663bb69fe71 | 0.01 | maxspeed=50; source:maxspeed=PL:urban | {"between": [0.0, 0.616427718], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.616427718, 1.0], "max_speed": {"unit": "km/h", "value": 40}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/mapillary_28658384260521108.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_302171341502933 | 741771283 | f61ec7a4-a427-4277-a958-1add986ae0ac | 2.09 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.100643035], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.100643035, 1.0], "max_speed": {"unit": "km/h", "value": 70}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_302171341502933.jpg); richlv, Mapillary, CC-BY-SA-4.0 |
| mapillary_336757954741755 | 351973878 | edeb7d09-d540-4033-9187-93600d016876 | 3.66 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.397923212], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.690653404, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.397923212, 0.513370812], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.397923212, 0.513370812], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}}; {"between": [0.513370812, 0.690653404], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "backward"}}; {"between": [0.513370812, 0.690653404], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward"}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_336757954741755.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| mapillary_365733204843645 | 553075598 | cb469da2-76d3-4274-a4f3-30ba7009967d | 0.24 | maxspeed:backward=40; maxspeed:forward=50; source:maxspeed:backward=sign; source:maxspeed:forward=PL:urban | {"max_speed": {"unit": "km/h", "value": 40}, "when": {"heading": "backward"}}; {"max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | osm:directional_differs | – | [miniatura](thumbs/mapillary_365733204843645.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| mapillary_3773145916147480 | 860389162 | 7f3e5c64-57c6-44e0-a910-2049035c5e5e | 0.11 | maxspeed=40; source:maxspeed=sign | {"between": [0.0, 0.154207565], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.154207565, 1.0], "max_speed": {"unit": "km/h", "value": 40}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_3773145916147480.jpg); ekeshkekesh, Mapillary, CC-BY-SA-4.0 |
| mapillary_407737842319790 | 1416953488 | 8c58d133-967c-4128-8a11-28cd85f296a6 | 15.15 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.093246103], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.093246103, 0.224310745], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.224310745, 0.38980586], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_407737842319790.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_4527360787479920 | 415389038 | 4603b5a2-39ac-467e-9649-9c6d3000c509 | 3.58 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.255205349], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.255205349, 0.764456374], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764456374, 0.843520295], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.929497155, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_4527360787479920.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_561878881446051 | 553075598 | cb469da2-76d3-4274-a4f3-30ba7009967d | 1.70 | maxspeed:backward=40; maxspeed:forward=50; source:maxspeed:backward=sign; source:maxspeed:forward=PL:urban | {"max_speed": {"unit": "km/h", "value": 40}, "when": {"heading": "backward"}}; {"max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | osm:directional_differs | – | [miniatura](thumbs/mapillary_561878881446051.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| mapillary_648504628272254 | 566097541 | 4b333dda-2927-4f9c-a7d1-fd671c8c8888 | 1.39 | maxspeed=90; maxspeed:bus=70; maxspeed:trailer=70; source:maxspeed=PL:rural | {"between": [0.285341701, 0.602033876], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.760948352, 0.921868901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.975052145, 1.0], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.0, 0.285341701], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.0, 0.285341701], "max_speed": {"unit": "km/h", "value": 90}, "when": {"heading": "forward"}}; {"between": [0.602033876, 0.760948352], "max_speed": {"unit": "km/h", "value": 90}, "when": {"heading": "backward"}}; {"between": [0.602033876, 0.760948352], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward"}}; {"between": [0.921868901, 0.975052145], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.921868901, 0.975052145], "max_speed": {"unit": "km/h", "value": 90}, "when": {"heading": "forward"}}; {"between": [0.0, 0.285341701], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward", "mode": ["bus"]}}; {"between": [0.602033876, 0.760948352], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward", "mode": ["bus"]}}; {"between": [0.921868901, 0.975052145], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward", "mode": ["bus"]}}; {"between": [0.285341701, 0.602033876], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus"]}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_648504628272254.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_761982104509850 | 1286180666 | 324b91b6-1c37-407c-ac60-07b8a37d8a3c | 11.54 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.076105928], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.076105928, 1.0], "max_speed": {"unit": "km/h", "value": 70}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_761982104509850.jpg); ekeshkekesh, Mapillary, CC-BY-SA-4.0 |
| mapillary_763388231046401 | 860389162 | 7f3e5c64-57c6-44e0-a910-2049035c5e5e | 0.17 | maxspeed=40; source:maxspeed=sign | {"between": [0.0, 0.154207565], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.154207565, 1.0], "max_speed": {"unit": "km/h", "value": 40}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_763388231046401.jpg); ekeshkekesh, Mapillary, CC-BY-SA-4.0 |
| mapillary_787823830587862 | 566097541 | 4b333dda-2927-4f9c-a7d1-fd671c8c8888 | 2.14 | maxspeed=90; maxspeed:bus=70; maxspeed:trailer=70; source:maxspeed=PL:rural | {"between": [0.285341701, 0.602033876], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.760948352, 0.921868901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.975052145, 1.0], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.0, 0.285341701], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.0, 0.285341701], "max_speed": {"unit": "km/h", "value": 90}, "when": {"heading": "forward"}}; {"between": [0.602033876, 0.760948352], "max_speed": {"unit": "km/h", "value": 90}, "when": {"heading": "backward"}}; {"between": [0.602033876, 0.760948352], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward"}}; {"between": [0.921868901, 0.975052145], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.921868901, 0.975052145], "max_speed": {"unit": "km/h", "value": 90}, "when": {"heading": "forward"}}; {"between": [0.0, 0.285341701], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward", "mode": ["bus"]}}; {"between": [0.602033876, 0.760948352], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward", "mode": ["bus"]}}; {"between": [0.921868901, 0.975052145], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward", "mode": ["bus"]}}; {"between": [0.285341701, 0.602033876], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus"]}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_787823830587862.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_789245484246735 | 645042637 | 29fd1419-7545-4fcb-866f-112a334fbd87 | 0.24 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.896136742], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.896136742, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_789245484246735.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_810131513353436 | 1416953488 | 8c58d133-967c-4128-8a11-28cd85f296a6 | 3.20 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.093246103], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.093246103, 0.224310745], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.224310745, 0.38980586], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/mapillary_810131513353436.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_891542184735652 | 741769884 | edeb7d09-d540-4033-9187-93600d016876 | 3.37 | maxspeed:backward=70; maxspeed:forward=50; source:maxspeed:backward=sign; source:maxspeed:forward=sign | {"between": [0.0, 0.397923212], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.690653404, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.397923212, 0.513370812], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.397923212, 0.513370812], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}}; {"between": [0.513370812, 0.690653404], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "backward"}}; {"between": [0.513370812, 0.690653404], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "forward"}} | – | osm:directional_differs | – | [miniatura](thumbs/mapillary_891542184735652.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| panoramax_0033f5e2-ff37-497b-b27d-10c5b78ac11c | 1364317403 | 8c58d133-967c-4128-8a11-28cd85f296a6 | 15.72 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.093246103], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.093246103, 0.224310745], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.224310745, 0.38980586], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_0033f5e2-ff37-497b-b27d-10c5b78ac11c.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_06d0eb23-792f-4b03-b183-60f57ee6bc9a | 1562739372 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 0.22 | maxspeed=60; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_06d0eb23-792f-4b03-b183-60f57ee6bc9a.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_07c242ac-a021-4f94-8ab3-4a0f2077467c | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.05 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_07c242ac-a021-4f94-8ab3-4a0f2077467c.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_0802dbfa-9c21-451a-a936-1964cc8022f0 | 207328248 | ac627881-faa9-40fd-b327-01491f174192 | 1.47 | maxspeed=60; source:maxspeed=sign | {"between": [0.0, 0.209770218], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.209770218, 1.0], "max_speed": {"unit": "km/h", "value": 60}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_0802dbfa-9c21-451a-a936-1964cc8022f0.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_0a08092d-eef1-4f57-bc97-7dc0008e4e4b | 1096510288 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.08 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_0a08092d-eef1-4f57-bc97-7dc0008e4e4b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_0a6b4cd8-442c-42d5-b6fc-8ad81b0ad600 | 1206276880 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 3.19 | maxspeed=50; source:maxspeed=sign | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_0a6b4cd8-442c-42d5-b6fc-8ad81b0ad600.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_0b82df8e-5134-4862-af8e-4fbe8cff6bd7 | 1562739372 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.13 | maxspeed=60; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_0b82df8e-5134-4862-af8e-4fbe8cff6bd7.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_11b644cd-d95f-445a-ade6-f73ea72a5c96 | 1096511436 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 3.23 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_11b644cd-d95f-445a-ade6-f73ea72a5c96.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_14841522-0f0f-41a0-b0e4-2fad8bfa80cf | 1303332151 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.75 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_14841522-0f0f-41a0-b0e4-2fad8bfa80cf.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_1c3b133f-3be2-48dc-96b5-49fb2a39988f | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.62 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_1c3b133f-3be2-48dc-96b5-49fb2a39988f.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_1d8190e3-2885-4286-ac03-971028a82360 | 1206241059 | 0cd98d09-b8c6-4fb2-9048-b8dade2d9bd7 | 1.61 | maxspeed=70; maxspeed:bus=70; maxspeed:hgv=70; maxspeed:trailer=70; source:maxspeed=sign | {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.148569456, 0.731635771], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.731635771, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.148569456, 0.654989832], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_1d8190e3-2885-4286-ac03-971028a82360.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_1e930646-ec7a-4ccc-bf18-4b96c490fc0f | 554959810 | e7ecf031-8c3b-4676-aefa-4160855b3fc0 | 2.42 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.760582754, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_1e930646-ec7a-4ccc-bf18-4b96c490fc0f.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_1f9b3f6a-fc69-41cf-abe8-a4fe716c7ee9 | 1206241634 | 0cd98d09-b8c6-4fb2-9048-b8dade2d9bd7 | 1.80 | maxspeed=50; source:maxspeed=sign | {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.148569456, 0.731635771], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.731635771, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.148569456, 0.654989832], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_1f9b3f6a-fc69-41cf-abe8-a4fe716c7ee9.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_23742894-3ba7-4635-8af0-994c7bd015c2 | 1206241059 | 0cd98d09-b8c6-4fb2-9048-b8dade2d9bd7 | 1.90 | maxspeed=70; maxspeed:bus=70; maxspeed:hgv=70; maxspeed:trailer=70; source:maxspeed=sign | {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.148569456, 0.731635771], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.731635771, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.148569456, 0.654989832], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_23742894-3ba7-4635-8af0-994c7bd015c2.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_23ee61cc-20ca-43a1-9039-77ba37b03949 | 1096510288 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.14 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_23ee61cc-20ca-43a1-9039-77ba37b03949.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_252e644a-52b7-43c8-a694-3f70c1629e2c | 116896145 | c3140cd6-5b79-48ed-9506-f91fc06a95f7 | 1.49 | maxspeed=70 | {"between": [0.0, 0.727500035], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.727500035, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_252e644a-52b7-43c8-a694-3f70c1629e2c.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_2551fe85-40fb-4b99-bf96-98f629f8f26f | 554959810 | e7ecf031-8c3b-4676-aefa-4160855b3fc0 | 3.58 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.760582754, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_2551fe85-40fb-4b99-bf96-98f629f8f26f.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_2c8db345-8ae1-4211-a527-06e37ab0cecd | 1096510287 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 0.51 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_2c8db345-8ae1-4211-a527-06e37ab0cecd.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_3286d143-b3c8-4deb-8ba9-5b15d204f067 | 75233260 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 2.75 | maxspeed=70 | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_3286d143-b3c8-4deb-8ba9-5b15d204f067.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | 1249392085 | 42d83458-1681-4d35-91b9-dd23fdefc8d4 | 2.91 | maxspeed=120; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=sign | {"between": [0.0, 0.591049451], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.591049451, 0.778131362], "max_speed": {"unit": "km/h", "value": 120}}; {"between": [0.778131362, 1.0], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.0, 0.778131362], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.870441515, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | surface: paved (tier 1, p=1.00); junction_visible: abstain (tier 2, pewność=medium); street_lighting_visible: yes (tier 1, p=1.00) | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_3c683354-2386-456b-9955-31268ecb5213.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_3fe1f9f1-cabf-4c38-9dc1-2661b3a1ede5 | 224805042 | 42d83458-1681-4d35-91b9-dd23fdefc8d4 | 6.17 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"between": [0.0, 0.591049451], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.591049451, 0.778131362], "max_speed": {"unit": "km/h", "value": 120}}; {"between": [0.778131362, 1.0], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.0, 0.778131362], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.870441515, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_3fe1f9f1-cabf-4c38-9dc1-2661b3a1ede5.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_43b3be2d-d9c7-46e4-b111-550f0bddb018 | 19793220 | 972ece99-4bd6-429e-a39f-cbf6d3fe2907 | 2.65 | maxspeed=70 | {"between": [0.0, 0.27881809], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.27881809, 0.745789285], "max_speed": {"unit": "km/h", "value": 80}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_43b3be2d-d9c7-46e4-b111-550f0bddb018.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_46991b1a-b231-4e5b-95ce-67e991790396 | 1096510287 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.08 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_46991b1a-b231-4e5b-95ce-67e991790396.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_4aeab510-9633-4b67-85c3-90a2b433cda3 | 127905157 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.71 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_4aeab510-9633-4b67-85c3-90a2b433cda3.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_4af8e1ae-6cf6-4a92-8866-c05c70ebdf8a | 798376719 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 3.29 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_4af8e1ae-6cf6-4a92-8866-c05c70ebdf8a.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_4da48c88-66a9-46a8-a376-a8086374af61 | 1562739371 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 2.37 | maxspeed=70; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; maxspeed:type=sign; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_4da48c88-66a9-46a8-a376-a8086374af61.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_537091d0-0166-4bc9-bf74-d30e0c441aec | 1411974229 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 3.95 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_537091d0-0166-4bc9-bf74-d30e0c441aec.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_54d02246-e7c2-4be1-9cb7-5cbe6c16c0cb | 1096510289 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 2.25 | maxspeed=60; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_54d02246-e7c2-4be1-9cb7-5cbe6c16c0cb.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5c2eb3c5-9a5b-4f86-baf9-a05da5777db6 | 1206241059 | 0cd98d09-b8c6-4fb2-9048-b8dade2d9bd7 | 2.26 | maxspeed=70; maxspeed:bus=70; maxspeed:hgv=70; maxspeed:trailer=70; source:maxspeed=sign | {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.148569456, 0.731635771], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.731635771, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.148569456, 0.654989832], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_5c2eb3c5-9a5b-4f86-baf9-a05da5777db6.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5ff7b8a8-3536-4c1a-a08f-cebc01c485db | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.90 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_5ff7b8a8-3536-4c1a-a08f-cebc01c485db.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_655a862c-9080-4852-92ec-ff8f118c0770 | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.99 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_655a862c-9080-4852-92ec-ff8f118c0770.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_677d9abe-ba65-470a-b270-7b2717abc97b | 75233260 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 4.44 | maxspeed=70 | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_677d9abe-ba65-470a-b270-7b2717abc97b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_708e0c67-c751-47ab-8847-56401d4ed943 | 75233260 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 3.55 | maxspeed=70 | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_708e0c67-c751-47ab-8847-56401d4ed943.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_70d38abf-5bc9-41be-808f-b4e491fb1175 | 1206240643 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.56 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; maxspeed:type=PL:rural; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_70d38abf-5bc9-41be-808f-b4e491fb1175.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_7b1be8bb-0ede-4d56-8849-4a0589679726 | 207394293 | 972ece99-4bd6-429e-a39f-cbf6d3fe2907 | 2.39 | maxspeed=80; source:maxspeed=sign | {"between": [0.0, 0.27881809], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.27881809, 0.745789285], "max_speed": {"unit": "km/h", "value": 80}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_7b1be8bb-0ede-4d56-8849-4a0589679726.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_8a63d337-6401-4013-90a3-746690e43864 | 224805041 | 42d83458-1681-4d35-91b9-dd23fdefc8d4 | 4.55 | maxspeed=90; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=sign | {"between": [0.0, 0.591049451], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.591049451, 0.778131362], "max_speed": {"unit": "km/h", "value": 120}}; {"between": [0.778131362, 1.0], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.0, 0.778131362], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.870441515, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_8a63d337-6401-4013-90a3-746690e43864.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_8d283928-39b1-4e3c-b997-74a981f8c02d | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.95 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_8d283928-39b1-4e3c-b997-74a981f8c02d.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_92b83193-b23d-40a6-adb2-11175f808ca5 | 1206240642 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.69 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_92b83193-b23d-40a6-adb2-11175f808ca5.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9542100d-c5c9-4761-8300-7647bf8ad7e3 | 554959810 | e7ecf031-8c3b-4676-aefa-4160855b3fc0 | 2.17 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.760582754, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_9542100d-c5c9-4761-8300-7647bf8ad7e3.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_97414dde-ec16-4e8d-aa6b-437c1e88630b | 75233260 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 4.65 | maxspeed=70 | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_97414dde-ec16-4e8d-aa6b-437c1e88630b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9b4f24ec-da3f-4e95-abcd-3395f7056038 | 1096510289 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 2.29 | maxspeed=60; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_9b4f24ec-da3f-4e95-abcd-3395f7056038.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9f8bf2d0-fe3f-49ba-ab48-f1b772f77785 | 1451073161 | 45a24b24-2b5f-4b29-afdc-df01833bcb11 | 0.64 | maxspeed=50 | {"between": [0.0, 0.263875319], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.263875319, 0.809663258], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.809663258, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.263875319], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_9f8bf2d0-fe3f-49ba-ab48-f1b772f77785.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a1dd9a95-de57-40fc-8005-0f8f6fdade48 | 648056833 | c3140cd6-5b79-48ed-9506-f91fc06a95f7 | 1.58 | maxspeed=50 | {"between": [0.0, 0.727500035], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.727500035, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_a1dd9a95-de57-40fc-8005-0f8f6fdade48.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a2a6cd69-97dd-4d56-b4a3-e1a99a96849a | 1206240643 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.84 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; maxspeed:type=PL:rural; source:maxspeed=sign | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_a2a6cd69-97dd-4d56-b4a3-e1a99a96849a.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_aa9e6cba-d76a-44b8-8696-42916cc5ba19 | 75233260 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 3.58 | maxspeed=70 | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_aa9e6cba-d76a-44b8-8696-42916cc5ba19.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_b1b4d39f-2d55-4a10-bb27-cac9e2570637 | 230205761 | b82cd68d-cd64-4210-ad38-5cf328deefcf | 11.72 | maxspeed=70 | {"between": [0.0, 0.557967111], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.557967111, 1.0], "max_speed": {"unit": "km/h", "value": 70}} | – | overture:partial_between | boundary_crossing | [miniatura](thumbs/panoramax_b1b4d39f-2d55-4a10-bb27-cac9e2570637.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_b42cc326-6612-498d-b3e0-fd1d3e31d42a | 1096511436 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 3.74 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_b42cc326-6612-498d-b3e0-fd1d3e31d42a.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_bb8dc849-4685-47b4-9a2a-aafcddd1391e | 1416953488 | 8c58d133-967c-4128-8a11-28cd85f296a6 | 17.61 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.093246103], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.093246103, 0.224310745], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.224310745, 0.38980586], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_bb8dc849-4685-47b4-9a2a-aafcddd1391e.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_befa3932-b7c5-4edb-8e0a-c3b0a38fa629 | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.77 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_befa3932-b7c5-4edb-8e0a-c3b0a38fa629.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_bf443dd8-4718-4a21-ac40-e7dc7d5c1a78 | 19793298 | 972ece99-4bd6-429e-a39f-cbf6d3fe2907 | 3.99 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"between": [0.0, 0.27881809], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.27881809, 0.745789285], "max_speed": {"unit": "km/h", "value": 80}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_bf443dd8-4718-4a21-ac40-e7dc7d5c1a78.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_cf4cdc9a-43e7-4d1e-ada8-c9b88c1dda64 | 1416953488 | 8c58d133-967c-4128-8a11-28cd85f296a6 | 14.10 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.093246103], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.093246103, 0.224310745], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.224310745, 0.38980586], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.38980586, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_cf4cdc9a-43e7-4d1e-ada8-c9b88c1dda64.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_d798da2c-d7a5-4706-85af-62aa96cccfd0 | 554959810 | e7ecf031-8c3b-4676-aefa-4160855b3fc0 | 1.73 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.760582754, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.0, 0.760582754], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_d798da2c-d7a5-4706-85af-62aa96cccfd0.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_db11998f-dbd1-43f7-973b-d639077628f7 | 1532448825 | 45a24b24-2b5f-4b29-afdc-df01833bcb11 | 0.71 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.263875319], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.263875319, 0.809663258], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.809663258, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.263875319], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_db11998f-dbd1-43f7-973b-d639077628f7.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_e2ea00fe-aa6a-47d3-9977-932784f2bc81 | 1206276880 | ce8d65d3-edb8-42f4-9790-c33c6a046a51 | 2.00 | maxspeed=50; source:maxspeed=sign | {"between": [0.0, 0.764916663], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.764916663, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_e2ea00fe-aa6a-47d3-9977-932784f2bc81.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_e334478b-fe9b-4dbc-8449-47989581af0b | 127905157 | 24603b72-6495-43c9-856a-ef1a9f6f355a | 1.10 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.294586652], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.294586652, 0.716791901], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.716791901, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.32478399], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_e334478b-fe9b-4dbc-8449-47989581af0b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_e46de472-8625-448a-92df-2a087df9b725 | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.64 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_e46de472-8625-448a-92df-2a087df9b725.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_ee60b57f-3fa2-4e2a-9d64-210210913fd5 | 207394293 | 972ece99-4bd6-429e-a39f-cbf6d3fe2907 | 1.98 | maxspeed=80; source:maxspeed=sign | {"between": [0.0, 0.27881809], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.27881809, 0.745789285], "max_speed": {"unit": "km/h", "value": 80}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.745789285, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | grade_separated | [miniatura](thumbs/panoramax_ee60b57f-3fa2-4e2a-9d64-210210913fd5.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_f7f686ef-2710-43d5-be4f-a298e77e8d15 | 798376719 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.25 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_f7f686ef-2710-43d5-be4f-a298e77e8d15.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_fbb57295-b245-4186-8918-c095381ebc74 | 886738504 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.52 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_fbb57295-b245-4186-8918-c095381ebc74.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_fe79152a-8daa-41fd-bc76-5a0597d048d9 | 798376719 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 0.90 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | overture:partial_between | – | [miniatura](thumbs/panoramax_fe79152a-8daa-41fd-bc76-5a0597d048d9.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |

### Ograniczenie prędkości: niepewne połączenie (`speed` / `ambiguous_link`): 65

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| mapillary_1035956805919091 | 759687117 | c4485df2-5b60-457b-8ccd-23d1a58a9ff2 | 2.06 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1035956805919091.jpg); dedronek, Mapillary, CC-BY-SA-4.0 |
| mapillary_1272924134777707 | 365763145 | bc7867bc-e73f-452f-8607-a98ca8d41e6e | 1.90 | maxspeed=70; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 70}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1272924134777707.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_134880168567523 | 189507191 | 8a6fa5e2-320e-41b6-9263-6b1bfc3323da | 3.79 | – | – | – | ambiguous_candidates | service_or_restricted, ambiguous_candidates | [miniatura](thumbs/mapillary_134880168567523.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| mapillary_1431142590793546 | 741997695 | 2e9ada7c-b7e3-4ab4-8f70-48a85bd8f41d | 3.26 | maxspeed=60; maxspeed:bus=50; maxspeed:hgv=50; maxspeed:trailer=50; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.51085044, 1.0], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1431142590793546.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1997026677603618 | 1383045274 | 4e084795-6ce9-4452-b65f-aaec7d3c0150 | 0.85 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.077742754], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.077742754, 0.814772815], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.977989716, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1997026677603618.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_2015339122671085 | 127052516 | e6875857-2d94-419b-9dd9-87b7904d3c5d | 2.27 | maxspeed=50; maxspeed:type=sign; source:maxspeed=PL:urban | {"between": [0.0, 0.337038167], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.337038167, 1.0], "max_speed": {"unit": "km/h", "value": 70}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_2015339122671085.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_221453741046411 | 31876770 | dc961120-c6e6-432f-a27f-f44971af71ac | 3.89 | maxspeed=140; maxspeed:bus=80; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 110}, "when": {"during": "Mo-Fr06:00-18:00"}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/mapillary_221453741046411.jpg); IMC1964, Mapillary, CC-BY-SA-4.0 |
| mapillary_277454594020064 | 1353158955 | 7b7edc68-12c7-429b-a4c3-25ddebae7643 | 1.48 | maxspeed=30; source:maxspeed=PL:zone30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/mapillary_277454594020064.jpg); richlv, Mapillary, CC-BY-SA-4.0 |
| mapillary_299240679484422 | 741997695 | 2e9ada7c-b7e3-4ab4-8f70-48a85bd8f41d | 2.41 | maxspeed=60; maxspeed:bus=50; maxspeed:hgv=50; maxspeed:trailer=50; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.51085044, 1.0], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_299240679484422.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_367864708173840 | 556155666 | 4e084795-6ce9-4452-b65f-aaec7d3c0150 | 22.17 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.077742754], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.077742754, 0.814772815], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.977989716, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 70}, "when": {"heading": "backward"}}; {"between": [0.814772815, 0.977989716], "max_speed": {"unit": "km/h", "value": 50}, "when": {"heading": "forward"}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_367864708173840.jpg); dasza, Mapillary, CC-BY-SA-4.0 |
| mapillary_371658141807714 | 126376304 | 2e39e1c9-fcff-4c64-bbf3-d55d1260c3fc | 5.01 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_371658141807714.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_7005141349517162 | 224604345 | c164bc05-18fe-4968-a498-9745a590c774 | 3.97 | maxspeed=90 | {"between": [0.0, 0.832682242], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.832682242, 1.0], "max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_7005141349517162.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_782161737673142 | 78164498 | 1061a75b-2405-4354-b3a5-5a93b6b2cd88 | 0.56 | maxspeed=60; maxspeed:bus=50; maxspeed:hgv=50; maxspeed:trailer=50; source:maxspeed=sign | {"between": [0.0, 0.672734664], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.672734664, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.672734664], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus"]}}; {"between": [0.0, 0.931951744], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_782161737673142.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_868352877047402 | 1353158955 | 7b7edc68-12c7-429b-a4c3-25ddebae7643 | 0.49 | maxspeed=30; source:maxspeed=PL:zone30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/mapillary_868352877047402.jpg); richlv, Mapillary, CC-BY-SA-4.0 |
| mapillary_910184740862133 | 31876773 | 3cde2655-a4be-4e41-bfec-f9d5b3a083e3 | 3.92 | maxspeed=140; maxspeed:bus=80; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 110}, "when": {"during": "Mo-Fr06:00-18:00"}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_910184740862133.jpg); IMC1964, Mapillary, CC-BY-SA-4.0 |
| panoramax_0977d119-1935-48e0-bf03-6ac088e2cd41 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | – | – | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_0977d119-1935-48e0-bf03-6ac088e2cd41.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_0f839710-50b6-48b4-8afe-7e6ae20da27a | 1212676722 | a8b47b73-a022-478b-a75a-a25bd4aaaad7 | 6.98 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | missing_heading, suspect_position, ambiguous_candidates | [miniatura](thumbs/panoramax_0f839710-50b6-48b4-8afe-7e6ae20da27a.jpg); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_1efcb856-4847-425c-a47d-3d1c31fa648a | 346302165 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.76 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_1efcb856-4847-425c-a47d-3d1c31fa648a.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_1ff3699b-f2b5-40a7-8a66-8836ea654e2b | 225017402 | d4121463-9043-41cc-9c7c-12308f82547a | 5.46 | maxspeed=70; maxspeed:bus=50; maxspeed:hgv=50; maxspeed:trailer=50; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.0, 0.781788576], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_1ff3699b-f2b5-40a7-8a66-8836ea654e2b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_202d5311-2029-4ab6-a423-6091ed3d8eec | 31876773 | 3cde2655-a4be-4e41-bfec-f9d5b3a083e3 | 4.67 | maxspeed=140; maxspeed:bus=80; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 110}, "when": {"during": "Mo-Fr06:00-18:00"}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_202d5311-2029-4ab6-a423-6091ed3d8eec.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_21f577a5-fe8a-45ad-b02d-539942ca6459 | 346304298 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.72 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_21f577a5-fe8a-45ad-b02d-539942ca6459.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_241a71ed-e2c8-4312-8749-c1d4a5d57e3b | 648056842 | eae8c71a-be3e-482a-9791-d1de9ef5a9d7 | 3.89 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_241a71ed-e2c8-4312-8749-c1d4a5d57e3b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_26cd5194-47da-4ca4-8226-0c667d9eb743 | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_26cd5194-47da-4ca4-8226-0c667d9eb743.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_3058ba14-df88-464c-8d9e-6dc52a598075 | 346304298 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.22 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_3058ba14-df88-464c-8d9e-6dc52a598075.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_32463975-040c-4359-8528-5224dfd5db4c | 277973487 | 34f1ff24-0846-4a1f-85de-13736a017fa6 | 5.33 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"max_speed": {"unit": "km/h", "value": 100}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_32463975-040c-4359-8528-5224dfd5db4c.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_406cf0b4-d562-49c4-9d18-0c517770bf76 | 580591250 | 734ae0e3-ea48-4734-bbe7-a99af242f953 | 3.02 | maxspeed=90; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"max_speed": {"unit": "km/h", "value": 90}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_406cf0b4-d562-49c4-9d18-0c517770bf76.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_439b49e9-a37d-4343-8d23-66fc3befab51 | 225017397 | a1117813-7f94-489c-9dd0-c1c2b47f3f3b | 6.23 | maxspeed=70; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 70}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_439b49e9-a37d-4343-8d23-66fc3befab51.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_44c8b039-ae2e-4d6f-aa8a-255976a5062c | 24557421 | bdaa409a-35e9-4a1a-ac1c-840031c2bd0f | 0.30 | maxspeed=140; maxspeed:bus=80; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 110}, "when": {"during": "Mo-Fr06:00-18:00"}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_44c8b039-ae2e-4d6f-aa8a-255976a5062c.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_461b7fdb-1a70-48aa-9930-3f1085c1012b | 184187766 | e59279f8-2ad4-4fab-9324-362eae831b82 | 1.55 | maxspeed=50 | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_461b7fdb-1a70-48aa-9930-3f1085c1012b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5039911d-c916-4a94-80b0-674a121c2559 | 1303332151 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.58 | maxspeed=100; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:rural | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_5039911d-c916-4a94-80b0-674a121c2559.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5121517f-2b5a-4664-abd6-e738bfa028bc | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_5121517f-2b5a-4664-abd6-e738bfa028bc.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_546dd6da-e343-4399-b6cb-1f77bd365608 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | – | – | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_546dd6da-e343-4399-b6cb-1f77bd365608.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_58c5c3b6-135d-4cc7-9caf-f84f541b5e45 | 911436916 | 9ca26163-65fc-42fe-abb1-72d0172f337b | 2.76 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_58c5c3b6-135d-4cc7-9caf-f84f541b5e45.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5b96b83c-f318-47f6-b298-52d5f25d7523 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | – | – | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_5b96b83c-f318-47f6-b298-52d5f25d7523.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_5c501d68-11d1-4948-9cde-1cc00fb19184 | 1212676722 | a8b47b73-a022-478b-a75a-a25bd4aaaad7 | 6.98 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | missing_heading, suspect_position, ambiguous_candidates | Miniatura niedostępna (metadane źródła (API Panoramax): https://api.panoramax.xyz/api/collections/ff20ab76-1056-417f-9f40-db7f83e19541/items/5c501d68-11d1-4948-9cde-1cc00fb19184); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_675a3b84-b4b3-4f9a-857e-b68cc7f56b53 | 707241599 | 893002c6-279b-47e9-84eb-91d055a9a039 | 11.68 | maxspeed=30; source:maxspeed=PL:zone30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_675a3b84-b4b3-4f9a-857e-b68cc7f56b53.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_6b954856-0de9-4822-ab21-7fab59a39438 | 1206278491 | 91a3813e-b4d8-4f3d-9287-efc82d2125f4 | 6.45 | maxspeed=70; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 70}} | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/panoramax_6b954856-0de9-4822-ab21-7fab59a39438.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_6c9660cc-b284-4ac9-af52-a0ac3279b47a | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_6c9660cc-b284-4ac9-af52-a0ac3279b47a.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_6df4614b-d6ba-4b90-bffc-6fc37fb8473b | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | – | – | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_6df4614b-d6ba-4b90-bffc-6fc37fb8473b.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_71a6dcec-6eb6-4b1f-99b5-bf60ad652dcb | 1303332150 | c502c27f-8617-4eca-8899-8164d799cd7d | 2.67 | maxspeed=60; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 60}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_71a6dcec-6eb6-4b1f-99b5-bf60ad652dcb.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_71e7d283-563f-47a7-bda7-a31232661356 | 22939337 | 49c13178-8d59-4dc8-bfbd-0c6d85599f51 | 3.07 | maxspeed=140; maxspeed:bus=80; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 110}, "when": {"during": "Mo-Fr06:00-18:00"}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_71e7d283-563f-47a7-bda7-a31232661356.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_738826f7-75b5-4aee-993c-3017b4dba463 | 757727251 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.72 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/panoramax_738826f7-75b5-4aee-993c-3017b4dba463.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_7d4f858e-6c8e-4fb3-ad7d-135a96e1502b | 1206241635 | 0cd98d09-b8c6-4fb2-9048-b8dade2d9bd7 | 1.65 | maxspeed=70 | {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.148569456, 0.731635771], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.731635771, 1.0], "max_speed": {"unit": "km/h", "value": 50}}; {"between": [0.0, 0.148569456], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.148569456, 0.654989832], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_7d4f858e-6c8e-4fb3-ad7d-135a96e1502b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_879f7ab1-1d21-4531-a1b3-27a016fa6756 | 1416953493 | d08628d6-5fc5-4bee-8d12-59f0fc380f52 | 6.12 | – | – | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_879f7ab1-1d21-4531-a1b3-27a016fa6756.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_8b3fed61-d335-48b6-b13b-690fef695cf9 | 24557417 | 6a22e106-5221-4744-a963-1afc233cedd5 | 8.77 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_8b3fed61-d335-48b6-b13b-690fef695cf9.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_8b83f403-bc61-43e5-a6fa-78dd40c1a74c | 62827236 | ee3df361-b8b4-45a7-9788-90e67979738e | 2.22 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"between": [0.0, 0.11885873], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.11885873, 0.217176545], "max_speed": {"unit": "km/h", "value": 90}}; {"between": [0.217176545, 0.550570159], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.550570159, 1.0], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.0, 0.11885873], "max_speed": {"unit": "km/h", "value": 50}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.11885873, 0.217176545], "max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus", "hgv"]}}; {"between": [0.550570159, 1.0], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_8b83f403-bc61-43e5-a6fa-78dd40c1a74c.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9704c1e9-6deb-4748-bfae-e948c91f8c92 | 25379551 | ae458e8b-b0bc-410b-8187-0375fa278c88 | 3.35 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"between": [0.0, 0.087405996], "max_speed": {"unit": "km/h", "value": 140}}; {"between": [0.087405996, 0.325669821], "max_speed": {"unit": "km/h", "value": 80}}; {"between": [0.325669821, 1.0], "max_speed": {"unit": "km/h", "value": 60}}; {"between": [0.0, 0.087405996], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_9704c1e9-6deb-4748-bfae-e948c91f8c92.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9db8522f-1672-4006-8bed-5011c969cc62 | 91682913 | bb23bc6e-4a45-49d7-9b51-40f2e98cbca8 | 1.20 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_9db8522f-1672-4006-8bed-5011c969cc62.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a021aeee-c44e-4a41-bca3-3336f6b9a3ba | 1206240642 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.74 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_a021aeee-c44e-4a41-bca3-3336f6b9a3ba.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | 648167637 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.43 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | surface: paved (tier 1, p=1.00); junction_visible: no (tier 1, p=1.00); street_lighting_visible: no (tier 2, pewność=high) | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a626e4e9-ea64-4c8a-b129-37ef5995b5d7 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | – | – | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_a626e4e9-ea64-4c8a-b129-37ef5995b5d7.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_adbcad0a-5782-4bc7-8995-5e5f3f89d509 | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/panoramax_adbcad0a-5782-4bc7-8995-5e5f3f89d509.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_b4cd73eb-c048-4629-b9f1-2fa6937ac86d | 564607399 | 7fbcb826-f3ba-4685-9d1d-77de179fb272 | 16.30 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_b4cd73eb-c048-4629-b9f1-2fa6937ac86d.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_b5d99ca5-3b82-4698-b4c1-a580ea12972d | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_b5d99ca5-3b82-4698-b4c1-a580ea12972d.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_b6171ab9-d2d3-41fd-8cf6-470df74ef5ef | 648056837 | b4c619ab-a19e-47ea-9bbf-444881e9a09c | 1.81 | maxspeed=50; maxspeed:bus=70 | {"max_speed": {"unit": "km/h", "value": 50}}; {"max_speed": {"unit": "km/h", "value": 70}, "when": {"mode": ["bus"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_b6171ab9-d2d3-41fd-8cf6-470df74ef5ef.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_b8b83b0f-0d16-4795-b98b-9c4e58fed95d | 886738505 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.72 | maxspeed=70 | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_b8b83b0f-0d16-4795-b98b-9c4e58fed95d.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_cd62fe50-118e-492d-a726-94de38612c82 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | – | – | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_cd62fe50-118e-492d-a726-94de38612c82.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_d34046cf-658e-4a1c-ad91-d6e48e87325f | 1212676722 | a8b47b73-a022-478b-a75a-a25bd4aaaad7 | 6.98 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | missing_heading, suspect_position, ambiguous_candidates | Miniatura niedostępna (metadane źródła (API Panoramax): https://api.panoramax.xyz/api/collections/ff20ab76-1056-417f-9f40-db7f83e19541/items/d34046cf-658e-4a1c-ad91-d6e48e87325f); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_d6c3fd67-20be-4500-977f-70e009fa9896 | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | maxspeed=30 | {"max_speed": {"unit": "km/h", "value": 30}} | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_d6c3fd67-20be-4500-977f-70e009fa9896.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_db47ca55-a248-4186-ab7c-0e3f783628d5 | 1417718040 | eae8c71a-be3e-482a-9791-d1de9ef5a9d7 | 3.17 | maxspeed=50; source:maxspeed=PL:urban | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_db47ca55-a248-4186-ab7c-0e3f783628d5.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_e8328031-11bd-4dd2-ba76-e60565de577e | 346304298 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.34 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_e8328031-11bd-4dd2-ba76-e60565de577e.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_ed527853-1ea2-4382-bfe1-937cbb9e172b | 376942759 | 5a3a1758-8f05-4a64-8669-2324eeb44d5f | 4.49 | – | – | – | ambiguous_candidates | service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_ed527853-1ea2-4382-bfe1-937cbb9e172b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_f0339c3f-3c1d-400f-bbcc-33d755a23899 | 224930848 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.18 | maxspeed=140; maxspeed:bus=80; maxspeed:hgv=80; maxspeed:trailer=80; source:maxspeed=PL:motorway | {"max_speed": {"unit": "km/h", "value": 140}}; {"max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_f0339c3f-3c1d-400f-bbcc-33d755a23899.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_f493cc83-b216-44bb-a42f-13a45107ef15 | 1356445147 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 3.79 | maxspeed=70; source:maxspeed=sign | {"between": [0.0, 0.132383764], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 100}}; {"between": [0.214892515, 1.0], "max_speed": {"unit": "km/h", "value": 70}}; {"between": [0.132383764, 0.214892515], "max_speed": {"unit": "km/h", "value": 80}, "when": {"mode": ["bus", "hgv"]}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_f493cc83-b216-44bb-a42f-13a45107ef15.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_ff98b44d-a948-4f7a-9c54-e21ae0338b6b | 168350637 | f47b44d0-ac3d-49f4-b672-7756b3c62bd3 | 0.28 | maxspeed=50; source:maxspeed=sign | {"max_speed": {"unit": "km/h", "value": 50}} | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_ff98b44d-a948-4f7a-9c54-e21ae0338b6b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |

### Nawierzchnia: rozbieżne (`surface` / `disagree`): 0

Brak kandydatów (0).

### Nawierzchnia: brak w OSM (`surface` / `missing_osm`): 3

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| mapillary_891542184735652 | 741769884 | edeb7d09-d540-4033-9187-93600d016876 | 3.37 | – | paved | – | no_osm_surface | – | [miniatura](thumbs/mapillary_891542184735652.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| panoramax_aceb35b9-f936-4e90-8f06-8c7ad26eaee9 | 1442019083 | 21addaad-ffc9-40c7-8c8d-4e091311ccfd | 10.87 | – | – | – | no_osm_surface | service_or_restricted | [miniatura](thumbs/panoramax_aceb35b9-f936-4e90-8f06-8c7ad26eaee9.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_bebb9895-d14c-4a06-8ea7-cad7740f7764 | 137367264 | 5370bf93-8afd-436b-a3ef-8ab02d1004ab | 2.03 | – | – | – | no_osm_surface | poor_heading_alignment, service_or_restricted | Miniatura niedostępna (metadane źródła (API Panoramax): https://api.panoramax.xyz/api/collections/dffbd42c-e039-4124-81ae-ef5dcb67071d/items/bebb9895-d14c-4a06-8ea7-cad7740f7764); p4n-pics, Panoramax, CC-BY-SA-4.0 |

### Nawierzchnia: brak w Overture (`surface` / `missing_overture`): 0

Brak kandydatów (0).

### Nawierzchnia: nieporównywalne (`surface` / `not_comparable`): 4

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| mapillary_1435689471736379 | 415389038 | 4603b5a2-39ac-467e-9649-9c6d3000c509 | 3.40 | surface=asphalt | paved | – | overture:partial_between | – | [miniatura](thumbs/mapillary_1435689471736379.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_336757954741755 | 351973878 | edeb7d09-d540-4033-9187-93600d016876 | 3.66 | surface=asphalt | paved | – | overture:partial_between | – | [miniatura](thumbs/mapillary_336757954741755.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| mapillary_4527360787479920 | 415389038 | 4603b5a2-39ac-467e-9649-9c6d3000c509 | 3.58 | surface=asphalt | paved | – | overture:partial_between | – | [miniatura](thumbs/mapillary_4527360787479920.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| panoramax_30f08d1e-fe31-42d9-b042-607f5237d9ff | 1200858206 | d5824a89-6f63-4f2f-b0bb-0ed6865f3073 | 5.45 | surface=paving_stones | paving_stones | – | overture:partial_between | service_or_restricted | [miniatura](thumbs/panoramax_30f08d1e-fe31-42d9-b042-607f5237d9ff.jpg); p4n-pics, Panoramax, CC-BY-SA-4.0 |

### Nawierzchnia: niepewne połączenie (`surface` / `ambiguous_link`): 65

| Zdjęcie | OSM | Overture | Dystans [m] | OSM (surowe) | Overture (surowe) | Odczyt zdjęcia (predykcja) | Powód | Flagi | Miniatura |
|---|---:|---|---:|---|---|---|---|---|---|
| mapillary_1035956805919091 | 759687117 | c4485df2-5b60-457b-8ccd-23d1a58a9ff2 | 2.06 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1035956805919091.jpg); dedronek, Mapillary, CC-BY-SA-4.0 |
| mapillary_1272924134777707 | 365763145 | bc7867bc-e73f-452f-8607-a98ca8d41e6e | 1.90 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1272924134777707.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_134880168567523 | 189507191 | 8a6fa5e2-320e-41b6-9263-6b1bfc3323da | 3.79 | – | – | – | ambiguous_candidates | service_or_restricted, ambiguous_candidates | [miniatura](thumbs/mapillary_134880168567523.jpg); czadzik, Mapillary, CC-BY-SA-4.0 |
| mapillary_1431142590793546 | 741997695 | 2e9ada7c-b7e3-4ab4-8f70-48a85bd8f41d | 3.26 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1431142590793546.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_1997026677603618 | 1383045274 | 4e084795-6ce9-4452-b65f-aaec7d3c0150 | 0.85 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_1997026677603618.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_2015339122671085 | 127052516 | e6875857-2d94-419b-9dd9-87b7904d3c5d | 2.27 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_2015339122671085.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_221453741046411 | 31876770 | dc961120-c6e6-432f-a27f-f44971af71ac | 3.89 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/mapillary_221453741046411.jpg); IMC1964, Mapillary, CC-BY-SA-4.0 |
| mapillary_277454594020064 | 1353158955 | 7b7edc68-12c7-429b-a4c3-25ddebae7643 | 1.48 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/mapillary_277454594020064.jpg); richlv, Mapillary, CC-BY-SA-4.0 |
| mapillary_299240679484422 | 741997695 | 2e9ada7c-b7e3-4ab4-8f70-48a85bd8f41d | 2.41 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_299240679484422.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_367864708173840 | 556155666 | 4e084795-6ce9-4452-b65f-aaec7d3c0150 | 22.17 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_367864708173840.jpg); dasza, Mapillary, CC-BY-SA-4.0 |
| mapillary_371658141807714 | 126376304 | 2e39e1c9-fcff-4c64-bbf3-d55d1260c3fc | 5.01 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_371658141807714.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_7005141349517162 | 224604345 | c164bc05-18fe-4968-a498-9745a590c774 | 3.97 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_7005141349517162.jpg); edc22, Mapillary, CC-BY-SA-4.0 |
| mapillary_782161737673142 | 78164498 | 1061a75b-2405-4354-b3a5-5a93b6b2cd88 | 0.56 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_782161737673142.jpg); jswk, Mapillary, CC-BY-SA-4.0 |
| mapillary_868352877047402 | 1353158955 | 7b7edc68-12c7-429b-a4c3-25ddebae7643 | 0.49 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/mapillary_868352877047402.jpg); richlv, Mapillary, CC-BY-SA-4.0 |
| mapillary_910184740862133 | 31876773 | 3cde2655-a4be-4e41-bfec-f9d5b3a083e3 | 3.92 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/mapillary_910184740862133.jpg); IMC1964, Mapillary, CC-BY-SA-4.0 |
| panoramax_0977d119-1935-48e0-bf03-6ac088e2cd41 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | surface=paving_stones | paving_stones | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_0977d119-1935-48e0-bf03-6ac088e2cd41.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_0f839710-50b6-48b4-8afe-7e6ae20da27a | 1212676722 | a8b47b73-a022-478b-a75a-a25bd4aaaad7 | 6.98 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, suspect_position, ambiguous_candidates | [miniatura](thumbs/panoramax_0f839710-50b6-48b4-8afe-7e6ae20da27a.jpg); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_1efcb856-4847-425c-a47d-3d1c31fa648a | 346302165 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.76 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_1efcb856-4847-425c-a47d-3d1c31fa648a.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_1ff3699b-f2b5-40a7-8a66-8836ea654e2b | 225017402 | d4121463-9043-41cc-9c7c-12308f82547a | 5.46 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_1ff3699b-f2b5-40a7-8a66-8836ea654e2b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_202d5311-2029-4ab6-a423-6091ed3d8eec | 31876773 | 3cde2655-a4be-4e41-bfec-f9d5b3a083e3 | 4.67 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_202d5311-2029-4ab6-a423-6091ed3d8eec.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_21f577a5-fe8a-45ad-b02d-539942ca6459 | 346304298 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.72 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_21f577a5-fe8a-45ad-b02d-539942ca6459.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_241a71ed-e2c8-4312-8749-c1d4a5d57e3b | 648056842 | eae8c71a-be3e-482a-9791-d1de9ef5a9d7 | 3.89 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_241a71ed-e2c8-4312-8749-c1d4a5d57e3b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_26cd5194-47da-4ca4-8226-0c667d9eb743 | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_26cd5194-47da-4ca4-8226-0c667d9eb743.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_3058ba14-df88-464c-8d9e-6dc52a598075 | 346304298 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.22 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_3058ba14-df88-464c-8d9e-6dc52a598075.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_32463975-040c-4359-8528-5224dfd5db4c | 277973487 | 34f1ff24-0846-4a1f-85de-13736a017fa6 | 5.33 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_32463975-040c-4359-8528-5224dfd5db4c.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_406cf0b4-d562-49c4-9d18-0c517770bf76 | 580591250 | 734ae0e3-ea48-4734-bbe7-a99af242f953 | 3.02 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_406cf0b4-d562-49c4-9d18-0c517770bf76.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_439b49e9-a37d-4343-8d23-66fc3befab51 | 225017397 | a1117813-7f94-489c-9dd0-c1c2b47f3f3b | 6.23 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_439b49e9-a37d-4343-8d23-66fc3befab51.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_44c8b039-ae2e-4d6f-aa8a-255976a5062c | 24557421 | bdaa409a-35e9-4a1a-ac1c-840031c2bd0f | 0.30 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_44c8b039-ae2e-4d6f-aa8a-255976a5062c.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_461b7fdb-1a70-48aa-9930-3f1085c1012b | 184187766 | e59279f8-2ad4-4fab-9324-362eae831b82 | 1.55 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_461b7fdb-1a70-48aa-9930-3f1085c1012b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5039911d-c916-4a94-80b0-674a121c2559 | 1303332151 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 2.58 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_5039911d-c916-4a94-80b0-674a121c2559.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5121517f-2b5a-4664-abd6-e738bfa028bc | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_5121517f-2b5a-4664-abd6-e738bfa028bc.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_546dd6da-e343-4399-b6cb-1f77bd365608 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | surface=paving_stones | paving_stones | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_546dd6da-e343-4399-b6cb-1f77bd365608.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_58c5c3b6-135d-4cc7-9caf-f84f541b5e45 | 911436916 | 9ca26163-65fc-42fe-abb1-72d0172f337b | 2.76 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_58c5c3b6-135d-4cc7-9caf-f84f541b5e45.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_5b96b83c-f318-47f6-b298-52d5f25d7523 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | surface=paving_stones | paving_stones | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_5b96b83c-f318-47f6-b298-52d5f25d7523.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_5c501d68-11d1-4948-9cde-1cc00fb19184 | 1212676722 | a8b47b73-a022-478b-a75a-a25bd4aaaad7 | 6.98 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, suspect_position, ambiguous_candidates | Miniatura niedostępna (metadane źródła (API Panoramax): https://api.panoramax.xyz/api/collections/ff20ab76-1056-417f-9f40-db7f83e19541/items/5c501d68-11d1-4948-9cde-1cc00fb19184); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_675a3b84-b4b3-4f9a-857e-b68cc7f56b53 | 707241599 | 893002c6-279b-47e9-84eb-91d055a9a039 | 11.68 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_675a3b84-b4b3-4f9a-857e-b68cc7f56b53.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_6b954856-0de9-4822-ab21-7fab59a39438 | 1206278491 | 91a3813e-b4d8-4f3d-9287-efc82d2125f4 | 6.45 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/panoramax_6b954856-0de9-4822-ab21-7fab59a39438.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_6c9660cc-b284-4ac9-af52-a0ac3279b47a | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_6c9660cc-b284-4ac9-af52-a0ac3279b47a.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_6df4614b-d6ba-4b90-bffc-6fc37fb8473b | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | surface=paving_stones | paving_stones | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_6df4614b-d6ba-4b90-bffc-6fc37fb8473b.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_71a6dcec-6eb6-4b1f-99b5-bf60ad652dcb | 1303332150 | c502c27f-8617-4eca-8899-8164d799cd7d | 2.67 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_71a6dcec-6eb6-4b1f-99b5-bf60ad652dcb.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_71e7d283-563f-47a7-bda7-a31232661356 | 22939337 | 49c13178-8d59-4dc8-bfbd-0c6d85599f51 | 3.07 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_71e7d283-563f-47a7-bda7-a31232661356.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_738826f7-75b5-4aee-993c-3017b4dba463 | 757727251 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.72 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/panoramax_738826f7-75b5-4aee-993c-3017b4dba463.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_7d4f858e-6c8e-4fb3-ad7d-135a96e1502b | 1206241635 | 0cd98d09-b8c6-4fb2-9048-b8dade2d9bd7 | 1.65 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_7d4f858e-6c8e-4fb3-ad7d-135a96e1502b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_879f7ab1-1d21-4531-a1b3-27a016fa6756 | 1416953493 | d08628d6-5fc5-4bee-8d12-59f0fc380f52 | 6.12 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_879f7ab1-1d21-4531-a1b3-27a016fa6756.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_8b3fed61-d335-48b6-b13b-690fef695cf9 | 24557417 | 6a22e106-5221-4744-a963-1afc233cedd5 | 8.77 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_8b3fed61-d335-48b6-b13b-690fef695cf9.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_8b83f403-bc61-43e5-a6fa-78dd40c1a74c | 62827236 | ee3df361-b8b4-45a7-9788-90e67979738e | 2.22 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_8b83f403-bc61-43e5-a6fa-78dd40c1a74c.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9704c1e9-6deb-4748-bfae-e948c91f8c92 | 25379551 | ae458e8b-b0bc-410b-8187-0375fa278c88 | 3.35 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_9704c1e9-6deb-4748-bfae-e948c91f8c92.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_9db8522f-1672-4006-8bed-5011c969cc62 | 91682913 | bb23bc6e-4a45-49d7-9b51-40f2e98cbca8 | 1.20 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_9db8522f-1672-4006-8bed-5011c969cc62.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a021aeee-c44e-4a41-bca3-3336f6b9a3ba | 1206240642 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.74 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_a021aeee-c44e-4a41-bca3-3336f6b9a3ba.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | 648167637 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.43 | surface=asphalt | paved | surface: paved (tier 1, p=1.00); junction_visible: no (tier 1, p=1.00); street_lighting_visible: no (tier 2, pewność=high) | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_a626e4e9-ea64-4c8a-b129-37ef5995b5d7 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | surface=paving_stones | paving_stones | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_a626e4e9-ea64-4c8a-b129-37ef5995b5d7.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_adbcad0a-5782-4bc7-8995-5e5f3f89d509 | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, ambiguous_candidates | [miniatura](thumbs/panoramax_adbcad0a-5782-4bc7-8995-5e5f3f89d509.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_b4cd73eb-c048-4629-b9f1-2fa6937ac86d | 564607399 | 7fbcb826-f3ba-4685-9d1d-77de179fb272 | 16.30 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_b4cd73eb-c048-4629-b9f1-2fa6937ac86d.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_b5d99ca5-3b82-4698-b4c1-a580ea12972d | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_b5d99ca5-3b82-4698-b4c1-a580ea12972d.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_b6171ab9-d2d3-41fd-8cf6-470df74ef5ef | 648056837 | b4c619ab-a19e-47ea-9bbf-444881e9a09c | 1.81 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_b6171ab9-d2d3-41fd-8cf6-470df74ef5ef.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_b8b83b0f-0d16-4795-b98b-9c4e58fed95d | 886738505 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 1.72 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_b8b83b0f-0d16-4795-b98b-9c4e58fed95d.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_cd62fe50-118e-492d-a726-94de38612c82 | 1232329075 | 4b5d8203-a794-4b4e-814c-613167b4b8e2 | 13.51 | surface=paving_stones | paving_stones | – | ambiguous_candidates | missing_heading, service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_cd62fe50-118e-492d-a726-94de38612c82.jpg); mapcomplete, Piotr Wicijowski, Panoramax, CC-BY-SA-4.0 |
| panoramax_d34046cf-658e-4a1c-ad91-d6e48e87325f | 1212676722 | a8b47b73-a022-478b-a75a-a25bd4aaaad7 | 6.98 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, suspect_position, ambiguous_candidates | Miniatura niedostępna (metadane źródła (API Panoramax): https://api.panoramax.xyz/api/collections/ff20ab76-1056-417f-9f40-db7f83e19541/items/d34046cf-658e-4a1c-ad91-d6e48e87325f); p4n-pics, Panoramax, CC-BY-SA-4.0 |
| panoramax_d6c3fd67-20be-4500-977f-70e009fa9896 | 1544043039 | c96002ee-c237-49b1-ab03-6fb5c6c7e746 | 15.65 | surface=asphalt | paved | – | ambiguous_candidates | missing_heading, ambiguous_candidates | [miniatura](thumbs/panoramax_d6c3fd67-20be-4500-977f-70e009fa9896.jpg); mapcomplete, fluffycupcakes, Panoramax, CC-BY-SA-4.0 |
| panoramax_db47ca55-a248-4186-ab7c-0e3f783628d5 | 1417718040 | eae8c71a-be3e-482a-9791-d1de9ef5a9d7 | 3.17 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_db47ca55-a248-4186-ab7c-0e3f783628d5.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_e8328031-11bd-4dd2-ba76-e60565de577e | 346304298 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.34 | surface=asphalt | paved | – | ambiguous_candidates | grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_e8328031-11bd-4dd2-ba76-e60565de577e.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_ed527853-1ea2-4382-bfe1-937cbb9e172b | 376942759 | 5a3a1758-8f05-4a64-8669-2324eeb44d5f | 4.49 | surface=dirt | dirt | – | ambiguous_candidates | service_or_restricted, ambiguous_candidates | [miniatura](thumbs/panoramax_ed527853-1ea2-4382-bfe1-937cbb9e172b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_f0339c3f-3c1d-400f-bbcc-33d755a23899 | 224930848 | 1784fc12-65fa-44b2-b225-87d81dfc9334 | 5.18 | surface=asphalt | paved | – | ambiguous_candidates | poor_heading_alignment, grade_separated, ambiguous_candidates | [miniatura](thumbs/panoramax_f0339c3f-3c1d-400f-bbcc-33d755a23899.jpg); czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_f493cc83-b216-44bb-a42f-13a45107ef15 | 1356445147 | d87efc5e-795b-44f9-b7ca-b00890a63b2f | 3.79 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_f493cc83-b216-44bb-a42f-13a45107ef15.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |
| panoramax_ff98b44d-a948-4f7a-9c54-e21ae0338b6b | 168350637 | f47b44d0-ac3d-49f4-b672-7756b3c62bd3 | 0.28 | surface=asphalt | paved | – | ambiguous_candidates | ambiguous_candidates | [miniatura](thumbs/panoramax_ff98b44d-a948-4f7a-9c54-e21ae0338b6b.jpg); czecko, czecko, Panoramax, CC-BY-SA-4.0 |

## 4. Kolejka ręczna

### Niepewne połączenia (`ambiguous_link`): 65

| Zdjęcie | Dotyczy | Powód |
|---|---|---|
| mapillary_1035956805919091 | speed, surface | ambiguous_candidates |
| mapillary_1272924134777707 | speed, surface | ambiguous_candidates |
| mapillary_134880168567523 | speed, surface | ambiguous_candidates |
| mapillary_1431142590793546 | speed, surface | ambiguous_candidates |
| mapillary_1997026677603618 | speed, surface | ambiguous_candidates |
| mapillary_2015339122671085 | speed, surface | ambiguous_candidates |
| mapillary_221453741046411 | speed, surface | ambiguous_candidates |
| mapillary_277454594020064 | speed, surface | ambiguous_candidates |
| mapillary_299240679484422 | speed, surface | ambiguous_candidates |
| mapillary_367864708173840 | speed, surface | ambiguous_candidates |
| mapillary_371658141807714 | speed, surface | ambiguous_candidates |
| mapillary_7005141349517162 | speed, surface | ambiguous_candidates |
| mapillary_782161737673142 | speed, surface | ambiguous_candidates |
| mapillary_868352877047402 | speed, surface | ambiguous_candidates |
| mapillary_910184740862133 | speed, surface | ambiguous_candidates |
| panoramax_0977d119-1935-48e0-bf03-6ac088e2cd41 | speed, surface | ambiguous_candidates |
| panoramax_0f839710-50b6-48b4-8afe-7e6ae20da27a | speed, surface | ambiguous_candidates |
| panoramax_1efcb856-4847-425c-a47d-3d1c31fa648a | speed, surface | ambiguous_candidates |
| panoramax_1ff3699b-f2b5-40a7-8a66-8836ea654e2b | speed, surface | ambiguous_candidates |
| panoramax_202d5311-2029-4ab6-a423-6091ed3d8eec | speed, surface | ambiguous_candidates |
| panoramax_21f577a5-fe8a-45ad-b02d-539942ca6459 | speed, surface | ambiguous_candidates |
| panoramax_241a71ed-e2c8-4312-8749-c1d4a5d57e3b | speed, surface | ambiguous_candidates |
| panoramax_26cd5194-47da-4ca4-8226-0c667d9eb743 | speed, surface | ambiguous_candidates |
| panoramax_3058ba14-df88-464c-8d9e-6dc52a598075 | speed, surface | ambiguous_candidates |
| panoramax_32463975-040c-4359-8528-5224dfd5db4c | speed, surface | ambiguous_candidates |
| panoramax_406cf0b4-d562-49c4-9d18-0c517770bf76 | speed, surface | ambiguous_candidates |
| panoramax_439b49e9-a37d-4343-8d23-66fc3befab51 | speed, surface | ambiguous_candidates |
| panoramax_44c8b039-ae2e-4d6f-aa8a-255976a5062c | speed, surface | ambiguous_candidates |
| panoramax_461b7fdb-1a70-48aa-9930-3f1085c1012b | speed, surface | ambiguous_candidates |
| panoramax_5039911d-c916-4a94-80b0-674a121c2559 | speed, surface | ambiguous_candidates |
| panoramax_5121517f-2b5a-4664-abd6-e738bfa028bc | speed, surface | ambiguous_candidates |
| panoramax_546dd6da-e343-4399-b6cb-1f77bd365608 | speed, surface | ambiguous_candidates |
| panoramax_58c5c3b6-135d-4cc7-9caf-f84f541b5e45 | speed, surface | ambiguous_candidates |
| panoramax_5b96b83c-f318-47f6-b298-52d5f25d7523 | speed, surface | ambiguous_candidates |
| panoramax_5c501d68-11d1-4948-9cde-1cc00fb19184 | speed, surface | ambiguous_candidates |
| panoramax_675a3b84-b4b3-4f9a-857e-b68cc7f56b53 | speed, surface | ambiguous_candidates |
| panoramax_6b954856-0de9-4822-ab21-7fab59a39438 | speed, surface | ambiguous_candidates |
| panoramax_6c9660cc-b284-4ac9-af52-a0ac3279b47a | speed, surface | ambiguous_candidates |
| panoramax_6df4614b-d6ba-4b90-bffc-6fc37fb8473b | speed, surface | ambiguous_candidates |
| panoramax_71a6dcec-6eb6-4b1f-99b5-bf60ad652dcb | speed, surface | ambiguous_candidates |
| panoramax_71e7d283-563f-47a7-bda7-a31232661356 | speed, surface | ambiguous_candidates |
| panoramax_738826f7-75b5-4aee-993c-3017b4dba463 | speed, surface | ambiguous_candidates |
| panoramax_7d4f858e-6c8e-4fb3-ad7d-135a96e1502b | speed, surface | ambiguous_candidates |
| panoramax_879f7ab1-1d21-4531-a1b3-27a016fa6756 | speed, surface | ambiguous_candidates |
| panoramax_8b3fed61-d335-48b6-b13b-690fef695cf9 | speed, surface | ambiguous_candidates |
| panoramax_8b83f403-bc61-43e5-a6fa-78dd40c1a74c | speed, surface | ambiguous_candidates |
| panoramax_9704c1e9-6deb-4748-bfae-e948c91f8c92 | speed, surface | ambiguous_candidates |
| panoramax_9db8522f-1672-4006-8bed-5011c969cc62 | speed, surface | ambiguous_candidates |
| panoramax_a021aeee-c44e-4a41-bca3-3336f6b9a3ba | speed, surface | ambiguous_candidates |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | speed, surface | ambiguous_candidates |
| panoramax_a626e4e9-ea64-4c8a-b129-37ef5995b5d7 | speed, surface | ambiguous_candidates |
| panoramax_adbcad0a-5782-4bc7-8995-5e5f3f89d509 | speed, surface | ambiguous_candidates |
| panoramax_b4cd73eb-c048-4629-b9f1-2fa6937ac86d | speed, surface | ambiguous_candidates |
| panoramax_b5d99ca5-3b82-4698-b4c1-a580ea12972d | speed, surface | ambiguous_candidates |
| panoramax_b6171ab9-d2d3-41fd-8cf6-470df74ef5ef | speed, surface | ambiguous_candidates |
| panoramax_b8b83b0f-0d16-4795-b98b-9c4e58fed95d | speed, surface | ambiguous_candidates |
| panoramax_cd62fe50-118e-492d-a726-94de38612c82 | speed, surface | ambiguous_candidates |
| panoramax_d34046cf-658e-4a1c-ad91-d6e48e87325f | speed, surface | ambiguous_candidates |
| panoramax_d6c3fd67-20be-4500-977f-70e009fa9896 | speed, surface | ambiguous_candidates |
| panoramax_db47ca55-a248-4186-ab7c-0e3f783628d5 | speed, surface | ambiguous_candidates |
| panoramax_e8328031-11bd-4dd2-ba76-e60565de577e | speed, surface | ambiguous_candidates |
| panoramax_ed527853-1ea2-4382-bfe1-937cbb9e172b | speed, surface | ambiguous_candidates |
| panoramax_f0339c3f-3c1d-400f-bbcc-33d755a23899 | speed, surface | ambiguous_candidates |
| panoramax_f493cc83-b216-44bb-a42f-13a45107ef15 | speed, surface | ambiguous_candidates |
| panoramax_ff98b44d-a948-4f7a-9c54-e21ae0338b6b | speed, surface | ambiguous_candidates |

### Odczyt modelem: abstencje i `model_unavailable`

Pozycje: 5

| Rodzaj | Zdjęcie | Pytanie | Powód |
|---|---|---|---|
| `abstain` | panoramax_3c683354-2386-456b-9955-31268ecb5213 | junction_visible | tier2_certainty_medium |
| `abstain` | panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | junction_visible | tier2_certainty_medium |
| `abstain` | panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | street_lighting_visible | tier2_certainty_low |
| `abstain` | mapillary_374349654072798 | speed_limit_value | tier2_certainty_medium |
| `abstain` | mapillary_962672327639677 | speed_limit_value | tier2_certainty_low |

## 5. Ewaluacja modelu

Progi (zamrożone przy potwierdzeniu): t1_threshold=0.8; t1_threshold_compare=0.8; tier2_accept=high. Wersja pytań: `qs-v1`. Pewność tier 2 to samoocena modelu, nie skalibrowane prawdopodobieństwo.

Próbka: obrazy=25; zdjęcia ulic=15; wycinki znaków=10; brak pliku (zastąpione)=0; obraz poza zakresem=0; podzbiór porównawczy=5.

#### Predykcje (osobno: odpowiedzi, abstencje, etykiety, `model_unavailable`)

| Zdjęcie | Rodzaj | Pytanie | Decyzja | Predykcja | Tier | Model | p (tier 1) | Pewność (tier 2) | Tier 1 przed eskalacją | Powód | Etykieta referencyjna |
|---|---|---|---|---|---:|---|---:|---|---|---|---|
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.98 | – | no (0.98) | – | no (certain) |
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 1.00 | – | yes (1.00) | – | yes (certain) |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.95 | – | no (0.95) | – | yes (certain) |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 1.00 | – | yes (1.00) | – | yes (certain) |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | photo | `junction_visible` | `abstain` | – | 2 | openai/gpt-6-luna | 0.68 | medium | yes (0.68) | tier2_certainty_medium | yes (certain) |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 1.00 | – | yes (1.00) | – | yes (certain) |
| panoramax_9bc04785-ce54-4104-8114-bc3b7155f6e9 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_9bc04785-ce54-4104-8114-bc3b7155f6e9 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | yes (certain) |
| panoramax_9bc04785-ce54-4104-8114-bc3b7155f6e9 | photo | `street_lighting_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.95 | – | no (0.95) | – | unknown (uncertain) |
| panoramax_66200c29-f302-4a7c-940b-dc11ad3d5322 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_66200c29-f302-4a7c-940b-dc11ad3d5322 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | no (certain) |
| panoramax_66200c29-f302-4a7c-940b-dc11ad3d5322 | photo | `street_lighting_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.94 | – | no (0.94) | – | no (certain) |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 1.00 | – | no (1.00) | – | no (certain) |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | photo | `street_lighting_visible` | `answered_tier2` | no | 2 | openai/gpt-6-luna | 0.77 | high | no (0.77) | – | no (certain) |
| panoramax_12f760a9-5f52-4092-be47-47b2481ceed8 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_12f760a9-5f52-4092-be47-47b2481ceed8 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | no (certain) |
| panoramax_12f760a9-5f52-4092-be47-47b2481ceed8 | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 1.00 | – | yes (1.00) | – | yes (certain) |
| panoramax_90d265a8-5897-4e57-a2e3-698444eb64af | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_90d265a8-5897-4e57-a2e3-698444eb64af | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 1.00 | – | no (1.00) | – | no (certain) |
| panoramax_90d265a8-5897-4e57-a2e3-698444eb64af | photo | `street_lighting_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.94 | – | no (0.94) | – | no (certain) |
| panoramax_b35a913d-cbc1-48d5-95bb-140a77cc2f1f | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_b35a913d-cbc1-48d5-95bb-140a77cc2f1f | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 1.00 | – | no (1.00) | – | no (certain) |
| panoramax_b35a913d-cbc1-48d5-95bb-140a77cc2f1f | photo | `street_lighting_visible` | `answered_tier2` | yes | 2 | openai/gpt-6-luna | 0.71 | high | yes (0.71) | – | yes (certain) |
| panoramax_7f42b279-bd01-492b-bddb-ba2e14a606be | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_7f42b279-bd01-492b-bddb-ba2e14a606be | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | no (certain) |
| panoramax_7f42b279-bd01-492b-bddb-ba2e14a606be | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 1.00 | – | yes (1.00) | – | yes (certain) |
| panoramax_2b72cfab-b9f8-49db-8278-cbaa3a8fc8ff | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_2b72cfab-b9f8-49db-8278-cbaa3a8fc8ff | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.88 | – | no (0.88) | – | no (certain) |
| panoramax_2b72cfab-b9f8-49db-8278-cbaa3a8fc8ff | photo | `street_lighting_visible` | `answered_tier2` | no | 2 | openai/gpt-6-luna | 0.71 | high | no (0.71) | – | no (certain) |
| panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | photo | `junction_visible` | `abstain` | – | 2 | openai/gpt-6-luna | 0.60 | medium | no (0.60) | tier2_certainty_medium | yes (certain) |
| panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | photo | `street_lighting_visible` | `abstain` | – | 2 | openai/gpt-6-luna | 0.53 | low | yes (0.53) | tier2_certainty_low | yes (certain) |
| panoramax_b57e68f4-1d4f-4208-82fa-4b36294deb2c | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_b57e68f4-1d4f-4208-82fa-4b36294deb2c | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | no (certain) |
| panoramax_b57e68f4-1d4f-4208-82fa-4b36294deb2c | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 1.00 | – | yes (1.00) | – | no (certain) |
| panoramax_7952c236-c745-4200-b72d-59b04381f790 | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_7952c236-c745-4200-b72d-59b04381f790 | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | no (certain) |
| panoramax_7952c236-c745-4200-b72d-59b04381f790 | photo | `street_lighting_visible` | `answered` | yes | 1 | openai/gpt-6-luna-decisions | 0.99 | – | yes (0.99) | – | yes (certain) |
| panoramax_8734e4cf-4a2f-414e-b750-c0519374dd0a | photo | `surface` | `answered` | paved | 1 | openai/gpt-6-luna-decisions | 1.00 | – | paved (1.00) | – | paved (certain) |
| panoramax_8734e4cf-4a2f-414e-b750-c0519374dd0a | photo | `junction_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 0.99 | – | no (0.99) | – | no (certain) |
| panoramax_8734e4cf-4a2f-414e-b750-c0519374dd0a | photo | `street_lighting_visible` | `answered` | no | 1 | openai/gpt-6-luna-decisions | 1.00 | – | no (1.00) | – | yes (certain) |
| mapillary_3501212013437933 | sign_crop | `speed_limit_value` | `answered` | none | 1 | openai/gpt-6-luna-decisions | 0.98 | – | none (0.98) | – | none (certain) |
| mapillary_374349654072798 | sign_crop | `speed_limit_value` | `abstain` | – | 2 | openai/gpt-6-luna | 0.17 | medium | 60 (0.17) | tier2_certainty_medium | 80 (certain) |
| mapillary_557443477317070 | sign_crop | `speed_limit_value` | `answered_tier2` | 120 | 2 | openai/gpt-6-luna | 0.22 | high | 60 (0.22) | – | 120 (certain) |
| mapillary_318047947631010 | sign_crop | `speed_limit_value` | `answered_tier2` | none | 2 | openai/gpt-6-luna | 0.66 | high | none (0.66) | – | none (certain) |
| mapillary_1035052394661534 | sign_crop | `speed_limit_value` | `answered_tier2` | none | 2 | openai/gpt-6-luna | 0.50 | high | unreadable (0.50) | – | none (certain) |
| mapillary_1029602998981114 | sign_crop | `speed_limit_value` | `answered_tier2` | 50 | 2 | openai/gpt-6-luna | 0.45 | high | 60 (0.45) | – | 50 (certain) |
| mapillary_512030746965559 | sign_crop | `speed_limit_value` | `answered` | 40 | 1 | openai/gpt-6-luna-decisions | 0.96 | – | 40 (0.96) | – | 40 (certain) |
| mapillary_962672327639677 | sign_crop | `speed_limit_value` | `abstain` | – | 2 | openai/gpt-6-luna | 0.40 | low | none (0.40) | tier2_certainty_low | none (certain) |
| mapillary_1152877773579493 | sign_crop | `speed_limit_value` | `answered_tier2` | 110 | 2 | openai/gpt-6-luna | 0.12 | high | 15 (0.12) | – | 110 (certain) |
| mapillary_2601761200243412 | sign_crop | `speed_limit_value` | `answered_tier2` | 110 | 2 | openai/gpt-6-luna | 0.17 | high | 15 (0.17) | – | 110 (certain) |

#### Metryki względem etykiet referencyjnych (tylko `certain`)

> Etykiety referencyjne przygotowały agenty AI: zdjęcia ulic oznaczył Codex, a wycinki znaków to zgodny odczyt dwóch modeli (Codex i GLM-5.3-Flash). Etykiety nie zostały zweryfikowane przez człowieka, więc accuracy oznacza zgodność z roboczą referencją AI, a nie poprawność terenową.

| Pytanie | Model | Poziom | Oceniane | Poprawne | Odpowiedzi | Abstencje | Niedostępne | Nie uruchomiono | Wykluczone `uncertain` | Accuracy (wszystkie) | Pokrycie | Accuracy po abstencji |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `surface` | openai/gpt-6-luna-decisions | tier 1 | 15 | 15 | 15 | 0 | 0 | 0 | 0 | 100.0% (15/15) | 100.0% (15/15) | 100.0% (15/15) |
| `surface` | openai/gpt-6-luna | tier 2 (tylko eskalowane) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | nieokreślone | nieokreślone | nieokreślone |
| `surface` | openai/gpt-6-luna-decisions → gpt-6-luna | końcowa (tier 1 + tier 2) | 15 | 15 | 15 | 0 | 0 | 0 | 0 | 100.0% (15/15) | 100.0% (15/15) | 100.0% (15/15) |
| `surface` | typesafe/jev-1.14 | tier 1 (porównanie, 5 obrazów) | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 100.0% (3/3) | 100.0% (3/3) | 100.0% (3/3) |
| `junction_visible` | openai/gpt-6-luna-decisions | tier 1 | 15 | 11 | 13 | 2 | 0 | 0 | 0 | 73.3% (11/15) | 86.7% (13/15) | 84.6% (11/13) |
| `junction_visible` | openai/gpt-6-luna | tier 2 (tylko eskalowane) | 2 | 0 | 0 | 2 | 0 | 0 | 0 | 0.0% (0/2) | 0.0% (0/2) | nieokreślone |
| `junction_visible` | openai/gpt-6-luna-decisions → gpt-6-luna | końcowa (tier 1 + tier 2) | 15 | 11 | 13 | 2 | 0 | 0 | 0 | 73.3% (11/15) | 86.7% (13/15) | 84.6% (11/13) |
| `junction_visible` | typesafe/jev-1.14 | tier 1 (porównanie, 5 obrazów) | 3 | 1 | 1 | 2 | 0 | 0 | 0 | 33.3% (1/3) | 33.3% (1/3) | 100.0% (1/1) |
| `street_lighting_visible` | openai/gpt-6-luna-decisions | tier 1 | 14 | 8 | 10 | 4 | 0 | 0 | 1 | 57.1% (8/14) | 71.4% (10/14) | 80.0% (8/10) |
| `street_lighting_visible` | openai/gpt-6-luna | tier 2 (tylko eskalowane) | 4 | 3 | 3 | 1 | 0 | 0 | 0 | 75.0% (3/4) | 75.0% (3/4) | 100.0% (3/3) |
| `street_lighting_visible` | openai/gpt-6-luna-decisions → gpt-6-luna | końcowa (tier 1 + tier 2) | 14 | 11 | 13 | 1 | 0 | 0 | 1 | 78.6% (11/14) | 92.9% (13/14) | 84.6% (11/13) |
| `street_lighting_visible` | typesafe/jev-1.14 | tier 1 (porównanie, 5 obrazów) | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 100.0% (3/3) | 100.0% (3/3) | 100.0% (3/3) |
| `speed_limit_value` | openai/gpt-6-luna-decisions | tier 1 | 10 | 2 | 2 | 8 | 0 | 0 | 0 | 20.0% (2/10) | 20.0% (2/10) | 100.0% (2/2) |
| `speed_limit_value` | openai/gpt-6-luna | tier 2 (tylko eskalowane) | 8 | 6 | 6 | 2 | 0 | 0 | 0 | 75.0% (6/8) | 75.0% (6/8) | 100.0% (6/6) |
| `speed_limit_value` | openai/gpt-6-luna-decisions → gpt-6-luna | końcowa (tier 1 + tier 2) | 10 | 8 | 8 | 2 | 0 | 0 | 0 | 80.0% (8/10) | 80.0% (8/10) | 100.0% (8/8) |
| `speed_limit_value` | typesafe/jev-1.14 | tier 1 (porównanie, 5 obrazów) | 2 | 1 | 1 | 1 | 0 | 0 | 0 | 50.0% (1/2) | 50.0% (1/2) | 100.0% (1/1) |

#### Porównanie modeli decyzyjnych na 5 obrazach (tier 1, bez eskalacji)

- Pary obraz–pytanie: 11
- Zgodne odpowiedzi: 10/11
- Średnia \|Δ max(p)\|: 0.170
- Uwaga: prawdopodobieństwa różnych modeli nie są wprost porównywalne; mała próbka, bez wniosków o kalibracji

| Zdjęcie | Pytanie | Luna | p Luna | Jev | p Jev | Zgodne | Δ max(p) |
|---|---|---|---:|---|---:|---|---:|
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | `surface` | paved | 1.00 | paved | 1.00 | tak | 0.00 |
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | `junction_visible` | no | 0.98 | no | 0.90 | tak | 0.08 |
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | `street_lighting_visible` | yes | 1.00 | yes | 0.94 | tak | 0.06 |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | `surface` | paved | 1.00 | paved | 1.00 | tak | 0.00 |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | `junction_visible` | no | 0.95 | no | 0.75 | tak | 0.20 |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | `street_lighting_visible` | yes | 1.00 | yes | 0.97 | tak | 0.03 |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | `surface` | paved | 1.00 | paved | 1.00 | tak | 0.00 |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | `junction_visible` | yes | 0.68 | yes | 0.52 | tak | 0.16 |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | `street_lighting_visible` | yes | 1.00 | yes | 0.99 | tak | 0.01 |
| mapillary_3501212013437933 | `speed_limit_value` | none | 0.98 | none | 0.48 | tak | 0.50 |
| mapillary_374349654072798 | `speed_limit_value` | 60 | 0.17 | 80 | 1.00 | nie | 0.83 |

#### Odczyt zdjęcia obok wartości mapy (zestawienie, nie werdykt)

| Zdjęcie | Pytanie | Predykcja | Decyzja | Wartości mapy | Uwaga |
|---|---|---|---|---|---|
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_94b5031d-61fd-4b81-ae3f-b9695b085e35 | `street_lighting_visible` | yes | `answered` | OSM lit=yes (yes) | OSM: zgodne |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_c429dd85-f700-4095-b670-90b3bb617875 | `street_lighting_visible` | yes | `answered` | OSM lit=– (missing) | OSM: brak wartości |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_3c683354-2386-456b-9955-31268ecb5213 | `street_lighting_visible` | yes | `answered` | OSM lit=no (no) | OSM: różne |
| panoramax_9bc04785-ce54-4104-8114-bc3b7155f6e9 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_9bc04785-ce54-4104-8114-bc3b7155f6e9 | `street_lighting_visible` | no | `answered` | OSM lit=yes (yes) | OSM: różne |
| panoramax_66200c29-f302-4a7c-940b-dc11ad3d5322 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_66200c29-f302-4a7c-940b-dc11ad3d5322 | `street_lighting_visible` | no | `answered` | OSM lit=no (no) | OSM: zgodne |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | nie porównano: niepewne połączenie (ambiguous_link) |
| panoramax_a208c9ca-21d9-451b-8d78-848a9e8bc928 | `street_lighting_visible` | no | `answered_tier2` | OSM lit=no (no) | nie porównano: niepewne połączenie (ambiguous_link) |
| panoramax_12f760a9-5f52-4092-be47-47b2481ceed8 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_12f760a9-5f52-4092-be47-47b2481ceed8 | `street_lighting_visible` | yes | `answered` | OSM lit=yes (yes) | OSM: zgodne |
| panoramax_90d265a8-5897-4e57-a2e3-698444eb64af | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_90d265a8-5897-4e57-a2e3-698444eb64af | `street_lighting_visible` | no | `answered` | OSM lit=– (missing) | OSM: brak wartości |
| panoramax_b35a913d-cbc1-48d5-95bb-140a77cc2f1f | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_b35a913d-cbc1-48d5-95bb-140a77cc2f1f | `street_lighting_visible` | yes | `answered_tier2` | OSM lit=yes (yes) | OSM: zgodne |
| panoramax_7f42b279-bd01-492b-bddb-ba2e14a606be | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_7f42b279-bd01-492b-bddb-ba2e14a606be | `street_lighting_visible` | yes | `answered` | OSM lit=yes (yes) | OSM: zgodne |
| panoramax_2b72cfab-b9f8-49db-8278-cbaa3a8fc8ff | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_2b72cfab-b9f8-49db-8278-cbaa3a8fc8ff | `street_lighting_visible` | no | `answered_tier2` | OSM lit=no (no) | OSM: zgodne |
| panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_ebb50ed6-3cb1-488c-b907-dc233aae92bc | `street_lighting_visible` | – | `abstain` | OSM lit=yes (yes) | nie porównano: brak odpowiedzi modelu (abstain) |
| panoramax_b57e68f4-1d4f-4208-82fa-4b36294deb2c | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_b57e68f4-1d4f-4208-82fa-4b36294deb2c | `street_lighting_visible` | yes | `answered` | OSM lit=yes (yes) | OSM: zgodne |
| panoramax_7952c236-c745-4200-b72d-59b04381f790 | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_7952c236-c745-4200-b72d-59b04381f790 | `street_lighting_visible` | yes | `answered` | OSM lit=– (missing) | OSM: brak wartości |
| panoramax_8734e4cf-4a2f-414e-b750-c0519374dd0a | `surface` | paved | `answered` | OSM surface=asphalt (paved); Overture=paved (paved) | OSM: zgodne; Overture: zgodne |
| panoramax_8734e4cf-4a2f-414e-b750-c0519374dd0a | `street_lighting_visible` | no | `answered` | OSM lit=– (missing) | OSM: brak wartości |
| mapillary_3501212013437933 | `speed_limit_value` | none | `answered` | OSM maxspeed=20; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=– | odczyt: brak znaku B-33 w wycinku |
| mapillary_374349654072798 | `speed_limit_value` | – | `abstain` | OSM maxspeed=140; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); Mapillary=80 | nie porównano: brak odpowiedzi modelu (abstain) |
| mapillary_557443477317070 | `speed_limit_value` | 120 | `answered_tier2` | OSM maxspeed=120; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=120 | OSM: zgodne; Mapillary: zgodne |
| mapillary_318047947631010 | `speed_limit_value` | none | `answered_tier2` | OSM maxspeed=50; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=– | odczyt: brak znaku B-33 w wycinku |
| mapillary_1035052394661534 | `speed_limit_value` | none | `answered_tier2` | OSM maxspeed=60; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=– | odczyt: brak znaku B-33 w wycinku |
| mapillary_1029602998981114 | `speed_limit_value` | 50 | `answered_tier2` | OSM maxspeed=50; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=50 | OSM: zgodne; Mapillary: zgodne |
| mapillary_512030746965559 | `speed_limit_value` | 40 | `answered` | OSM maxspeed=–; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=40 | OSM: brak wartości; Mapillary: zgodne |
| mapillary_962672327639677 | `speed_limit_value` | – | `abstain` | OSM maxspeed=–; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=–; Mapillary=– | nie porównano: brak odpowiedzi modelu (abstain) |
| mapillary_1152877773579493 | `speed_limit_value` | 110 | `answered_tier2` | OSM maxspeed=140; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); Mapillary=110 | OSM: różne; Mapillary: zgodne |
| mapillary_2601761200243412 | `speed_limit_value` | 110 | `answered_tier2` | OSM maxspeed=140; maxspeed:forward=–; maxspeed:backward=–; maxspeed:conditional=110 @ (Mo-Fr 06:00-18:00); Mapillary=110 | OSM: różne; Mapillary: zgodne |

## 6. Ograniczenia i atrybucja

- Odczyt zdjęcia jest predykcją modelu, a nie weryfikacją terenową. Rozbieżność źródeł nie oznacza automatycznie błędu mapy.
- Etykiety referencyjne są roboczą referencją przygotowaną przez agentów AI (znaki: dwa modele), a nie prawdą terenową.
- Daty źródeł się różnią: OSM 2026-11-01, Overture 2026-10-21.0, zdjęcia z różnych lat (część sprzed 2024 r.).
- Połączenia zdjęcie–droga to kandydaci z `photo_road_links.csv`, a nie pewne przypisanie. Kierunek kamery nie jest kierunkiem jazdy, a pozycja aparatu nie jest pozycją znaku.
- Zdjęcia: licencja CC BY-SA 4.0; autor i źródło podane przy każdej miniaturze.
- © OpenStreetMap contributors, ODbL 1.0
- Overture Maps Foundation, ODbL 1.0 (release 2026-10-21.0)
- Mapillary – metadane pochodne, ODbL 1.0
