# PRD prompt: Mapa i uzgadnianie danych o ładowarkach EV

**Jak użyć:** uruchom zainstalowany skill `write-prd` (`claude` -> `/write-prd`) i wklej cały poniższy prompt jako opis produktu. Możesz też wkleić go bezpośrednio i pozwolić skillowi się aktywować. Odpowiedz na pytania skilla. Wynik zapisz jako `docs/PRD.md`.

---

Przygotuj PRD produktu "Mapa ładowarek i luk pokrycia". Analityk GIS porównuje OpenStreetMap i Overture Maps, żeby zbudować sprawdzalny wykaz fizycznych lokalizacji ładowania oraz wskazać fragmenty głównych dróg bez pobliskiej stacji. Liczba gniazd nie jest liczbą lokalizacji. Brak rekordu na mapie oznacza lukę w danych, nie dowód braku infrastruktury.

## Użytkownicy i dane

- Analityk GIS/ETL chce porównać kompletność źródeł i odtworzyć każdą transformację.
- Redaktor danych rozstrzyga niepewne pary i koryguje klasy dostępności.
- Osoba planująca infrastrukturę ogląda pokrycie dróg i jakość danych, bez obietnicy bieżącej dostępności ładowarki.
- Obszar: województwo łódzkie; MVP zaczyna od bbox Łodzi `19.25,51.65,19.65,51.90` (west,south,east,north), identycznego dla obu źródeł. Rozszerzenie granic wymaga świadomego pobrania danych.
- OSM przez [Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API): wszystkie typy obiektów z `amenity=charging_station`, pełne tagi, identyfikator typu i obiektu. Główne drogi pobierz osobnym zapytaniem `highway=motorway|trunk|primary` w tym samym obszarze; zachowaj geometrię linii.
- [Overture Places](https://docs.overturemaps.org/getting-data/duckdb/): najnowsze wydanie z katalogu STAC, z zapisaną wersją, bbox i kategoriami ładowania. Nie zakładaj identycznej taksonomii ani jednego rekordu na fizyczne miejsce.
- Skrypty startowe: `course-materials/exercise-data/real/download_osm_chargers.py` i `download_overture_places.py`. Nie zapewniają dróg ani kontekstu sąsiednich POI: ich pobranie z OSM/Overture w zakresie bbox jest osobnym zadaniem wynikającym z PRD.

## Przepływ i funkcje

1. Użytkownik wybiera obszar i wersje danych, uruchamia import oraz widzi liczniki wejść i odrzuceń z przyczyną.
2. Python + DuckDB normalizują nazwy, adresy i kategorie. Kod oblicza odległości w metrach w odpowiednim CRS oraz wyznacza pary kandydatów, bez iloczynu kartezjańskiego całych zbiorów.
3. Jev ocenia semantykę par; kod stosuje progi i reguły konfliktów. Wybór jednego rekordu kanonicznego i końcowe scalenie należą do kodu. Wielu kandydatów i sprzeczne dane kierują parę do weryfikacji, bez automatycznego łączenia całej sieci przez jeden podobny rekord.
4. Dashboard pokazuje osobno warstwy OSM, Overture, scalone miejsca i główne drogi, filtry operatora/dostępności/mocy, tabelę par oraz panel surowych pól obu rekordów.
5. Kod wyznacza odcinki dróg poza uzgodnionym promieniem od stacji. PRD ma rozstrzygnąć próg i metrykę: w MVP odległość geometryczna, nie czas dojazdu. Wyłączone/prywatne stacje nie wypełniają publicznego pokrycia. Nieznaną dostępność pokaż oddzielnie.
6. Redaktor zatwierdza/odrzuca parę lub odracza ją do `human_review`, a wynik można wyeksportować wraz z ID źródłowymi i raportem jakości.

## Jev: dokładny kontrakt wejść i wyników

- Pytanie Noul: "Czy te dwa rekordy opisują tę samą fizyczną lokalizację ładowania?" Wejście: dla obu rekordów nazwa, operator/brand, network, pola adresu, tagi gniazd i mocy; dodatkowo odległość w metrach obliczona przez kod. Wynik: prawdopodobieństwo `true`/`false`. Kod mapuje je progami na `same_site`, `different_site` albo `human_review`; model nie wyznacza odległości ani nie scala rekordów.
- Pytanie Choice: "Kto może korzystać z tej ładowarki?" Dokładnie cztery opcje: `public`, `customers_only`, `private`, `unknown`. Wejście: nazwa, operator, brand, nazwy i kategorie najbliższych POI wyznaczonych przez kod oraz tagi obiektu INNE niż `access`. Nie przekazuj `access` także w zagnieżdżonym JSON, opisie ani cechach pochodnych. Wynik zawiera opcję i prawdopodobieństwa czterech klas.
- `unknown` oznacza brak podstaw do klasyfikacji; `abstain` jest odrębną decyzją kodu przy wyniku poniżej progu, a błąd API to `model_unavailable`. Żaden z tych stanów nie staje się `public`.

## Ewaluacja i jakość

- Zbiór etykiet dostępności to rekordy OSM MAJĄCE tag `access`. Ukryj tag przed Jev, zachowaj go oddzielnie do oceny. Jawna mapa etykiet: `yes` -> `public`, `customers` -> `customers_only`, `private`/`no` -> `private`; pozostałe wartości do ręcznej interpretacji lub osobno jako nieobsługiwane, bez automatycznej etykiety `unknown`.
- Podziel dane na zbiór do doboru progu i testowy według fizycznych lokalizacji. Sąsiadujące duplikaty nie mogą trafić do obu części. Raportuj accuracy ogółem i per klasę, liczebności, macierz pomyłek, coverage po abstencji i błędy na odrzuconych przypadkach. Mała lub nieobecna klasa nie daje wiarygodnej oceny: pokaż jej licznik i ograniczenie.
- Dobierz próg abstencji na zbiorze walidacyjnym, pokaż zależność jakości od pokrycia. Etykiety OSM mogą być błędne lub nieaktualne; ręcznie sprawdź próbkę. Dopasowania Noul oceniaj na osobno oznaczonych pozytywnych i negatywnych parach, mierząc precision/recall i błędne scalenia.
- Kontrole kodu: unikalność `(osm_type, osm_id)` i ID Overture, CRS i poprawność geometrii, bbox, brak współrzędnych, puste nazwy/adresy, nieznane jednostki mocy, sprzeczne tagi, zachowanie pełnych tagów i identyfikatorów po scaleniu.
- Kryteria akceptacji mają objąć: to samo miejsce w dwóch źródłach, różne stacje obok siebie, brak nazwy, sprzeczny operator, brak `access`, niejednoznaczny model, zerowy wynik pobrania i niedostępne API. Uzgodnij cel jakości zamiast deklarować niezmierzone 95%.

## Poza zakresem

Status ładowarki na żywo, płatności, nawigacja, optymalizacja tras, prognoza popytu, edycja OSM, automatyczna publikacja scaleń, przetwarzanie całej Polski, logowanie i dane firmowe.

## Wspólne ograniczenia

- To lokalne MVP dla jednego obszaru, uruchamiane na Windows 11 i Linux przez Python 3.12 + uv, bez Dockera, WSL i Hyper-V. Pipeline Python + DuckDB przygotowuje dane i agregaty; dashboard korzysta z jego wyników.
- Dashboard WWW ma mapę MapLibre GL JS z kaflami OpenFreeMap, bez klucza API (np. styl `https://tiles.openfreemap.org/styles/liberty`). Atrybucje "© OpenStreetMap contributors", OpenFreeMap i OpenMapTiles pozostają widoczne. Dodaj atrybucje warstw tematycznych.
- Styl wizualny aplikacji weź z tokenów i zasobów utworzonych podczas kursu w `assets/`, a jeśli istnieje, także z `docs/design-guidelines.md`. Nie wymyślaj nowego brandingu; brak tokenów zgłoś jako pytanie.
- Wejścia pozostają tylko do odczytu. Zapisuj oddzielnie wyniki, raport jakości i decyzje użytkownika. Błąd pobrania, pusty zbiór i brak wartości to różne stany, nigdy poprawne zera.
- Korzystamy tylko z publicznych danych wskazanych poniżej. Do zewnętrznych modeli wysyłamy wyłącznie jawnie wymienione pola; bez kluczy, prywatnych danych i całej bazy. Klucz OpenRouter pozostaje po stronie backendu.
- Jev by TypeSafe przez OpenRouter jest modelem decyzji semantycznych. PRD opisuje typy pytań i zamknięte wyniki, a aktualny identyfikator modelu, zgodność transportu z Noul/Choice i format API trzeba sprawdzić przed integracją. Brak obsługi lub awaria daje jawny stan niedostępności, nigdy wymyślony wynik. Nie wywołuj płatnego API podczas tworzenia PRD.
- Utrwalaj wersję danych, obszar, datę pobrania, konfigurację reguł, wersję modelu i pytania oraz wynik i prawdopodobieństwa. Ponowne przetworzenie tych samych wejść nie tworzy nowych duplikatów; decyzje człowieka mają trwały ślad.

Przygotuj funkcjonalne PRD: problem, użytkownicy, główny przepływ, historie użytkownika, mierzalne kryteria akceptacji, błędy i puste stany, jakość danych, ewaluacja, zakres MVP i poza zakresem oraz założenia i pytania. Użyj zainstalowanego `write-prd`, nie przepisuj jego metodyki. Szczegóły architektury pozostaw do osobnego ADR. Zapisz wynik po polsku w `docs/PRD.md`; nie implementuj jeszcze aplikacji. Jeśli ten plik istnieje, najpierw ustal z użytkownikiem, czy opis dotyczy aktualnego produktu.
