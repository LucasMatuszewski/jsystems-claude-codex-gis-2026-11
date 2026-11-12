# Zlecenia przetwarzania danych mapowych

To syntetyczny, lokalny zbiór 36 zgłoszeń MAPJOB-101 do MAPJOB-136. Zespoły zamawiają w nich przetwarzanie dróg, POI, ograniczeń prędkości i adresów. Nie ma tu prawdziwych osób, firm, kont ani danych z organizacji. Nazwy obszarów roboczych są fikcyjne; kody krajów i regionów służą do ćwiczenia kontroli parametrów. Nie potrzebujesz konta Jira ani tokenu.

Pracujesz na dwóch plikach: `tickets.json` zawiera surowe zgłoszenia, a `job-params.schema.json` określa format wyniku ekstrakcji. Traktuj oba jako wejścia tylko do odczytu. [Ćwiczenie MCP](../../exercises/jira-mcp/README.md) prowadzi od połączenia serwera do raportu problemów. Pipeline uruchamiasz dopiero po ręcznym zatwierdzeniu parametrów, poza tym ćwiczeniem.

## Mapa pól wejściowych

`tickets.json` ma kształt odpowiedzi wyszukiwania Jira Cloud REST API v3: `startAt`, `maxResults`, `total`, `issues`. To kompletna lokalna strona danych, a nie połączenie z API. Nie odtwarza wszystkich pól i mechanizmów uprawnień Jira.

| Ścieżka | Znaczenie |
|---|---|
| `issues[].key` | Klucz zgłoszenia |
| `issues[].fields.summary` | Krótki tytuł, który nie musi być unikalny |
| `issues[].fields.description` | Opis jako Atlassian Document Format: `type: doc`, `version: 1`, `content` |
| `issues[].fields.status.name` | To Do, In Progress albo Done |
| `issues[].fields.labels` | Etykiety pomocnicze; mogą być nieaktualne |
| `issues[].fields.created` | Data utworzenia w ISO 8601 |
| `issues[].fields.issuelinks` | Jawne powiązania z kierunkiem `inwardIssue` lub `outwardIssue` |
| `issues[].fields.comment.comments[]` | Komentarze z `id`, `created`, `updated`, zespołem autora i `body` w ADF |

Opis i komentarze mogą używać polskich albo angielskich nazw parametrów. Błędy i sprzeczności są celowe: literówki, powtórzone zlecenia, identyczne tytuły dla różnych obszarów lub warstw, brak pola, poprawki w komentarzach oraz podejrzana kolejność współrzędnych. Sama wzmianka o innym kluczu nie tworzy `issuelinks`. Status Done nie wyklucza zgłoszenia z ekstrakcji.

## Docelowe parametry

Wynik `params.json` jest tablicą. Zachowujesz jeden obiekt na każdy klucz, także dla duplikatów; powtórzenia opisujesz osobno. Każdy obiekt zawiera `ticket_key`, dziewięć poniższych pól i `unknown_reasons`.

| Pole | Oczekiwana wartość |
|---|---|
| `country_code` | Dwuliterowy kod kraju, np. PL |
| `region_code` | Kod regionu, np. PL-14; nie zamieniaj nieznanych aliasów bez dowodu |
| `spatial_scope` | Obiekt obszaru administracyjnego albo bbox |
| `layer` | `roads`, `poi`, `speed_limits`, `addresses` |
| `data_release` | Wydanie w formacie `YYYY.MM` |
| `processing_step` | `ingest`, `conflation`, `validation`, `export` |
| `output_format` | `GeoParquet`, `GeoJSON`, `CSV`, `GPKG` |
| `deadline` | Rzeczywista data kalendarzowa `YYYY-MM-DD` |
| `requester_team` | Nazwa zespołu zamawiającego, nie domyślnie autora komentarza |

Obszar nazwany zapisujesz jako `{"kind":"admin_area","name":"Sektor R-01"}`. Bbox zapisujesz jako `{"kind":"bbox","coordinates":[20.8,51.8,21.4,52.4],"crs":"EPSG:4326"}`. Kolejność to `[west,south,east,north]`, czyli długość, szerokość, długość, szerokość geograficzna. Dla tego zbioru west < east i south < north. Schema sprawdza liczbę i zakres współrzędnych; walidator powinien dodatkowo sprawdzić ich kolejność. Zgodność obszaru z krajem wymaga oceny danych, nie tylko sprawdzenia zakresu - zamienione lat/lon mogą nadal mieścić się w dozwolonych przedziałach.

Wolno ujednolicić wielkość liter znanych formatów i przekształcić jednoznaczną datę słowną. Wartości z literówką lub nieznanym skrótem poprawiaj tylko z potwierdzeniem w tym samym zgłoszeniu. Jawna zatwierdzona korekta w komentarzu ma pierwszeństwo przed wcześniejszą wartością; sam późniejszy czas nie zamienia propozycji w decyzję. Nie kopiuj parametrów z podobnego zlecenia.

Nieznany lub nierozstrzygnięty parametr ma wartość `null`. Dodaj wtedy powód pod jego nazwą w `unknown_reasons`, np. `{"data_release":"Brak wydania w opisie i komentarzach"}`. Dla kompletnych rekordów użyj `{}`. Jeśli nie da się ustalić całego obszaru, `spatial_scope` ma być `null`, a nie obiektem z wymyślonymi współrzędnymi. Schema wymaga powodu dla każdego `null`; nie potrafi ocenić, czy powód jest prawdziwy.

Walidacja JSON Schema Draft 2020-12 wymaga sprawdzania formatów dat, np. `Draft202012Validator(..., format_checker=FormatChecker())` w bibliotece `jsonschema`. Osobno sprawdź komplet 36 różnych kluczy, zgodność każdego pola z dowodem oraz problemy opisane w `issues.md`.
