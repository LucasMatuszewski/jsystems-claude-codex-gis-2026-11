# PRD prompt: Porównanie POI i kolejka weryfikacji na mapie

**Jak użyć:** uruchom zainstalowany skill `write-prd` (`claude` -> `/write-prd`) i wklej cały poniższy prompt jako opis produktu. Możesz też wkleić go bezpośrednio i pozwolić skillowi się aktywować. Odpowiedz na pytania skilla. Wynik zapisz jako `docs/PRD.md`.

---

Przygotuj PRD produktu "Przegląd jakości POI" dla jednego miasta, Łodzi. Zespoły GIS dostają dwa wykazy miejsc o różnych kategoriach, pisowni nazw i granularności. Celem jest wspólny słownik kategorii, lista potencjalnych duplikatów i ręczna weryfikacja na mapie, bez utraty pochodzenia pól.

## Użytkownicy i źródła

- Inżynier danych uruchamia powtarzalny import i rozlicza liczbę rekordów na każdym etapie.
- Redaktor mapy porównuje pary, koryguje kategorię i rozstrzyga duplikaty.
- Analityk jakości porównuje źródła według kategorii i obszaru oraz sprawdza wyniki modelu.
- [Overture Places](https://docs.overturemaps.org/getting-data/duckdb/) z publicznego bucketu, wydanie z katalogu STAC i bbox `19.25,51.65,19.65,51.90`; użyj `course-materials/exercise-data/real/download_overture_places.py` bez filtra EV.
- OSM przez [Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API) z tego samego bbox: punkty, linie i relacje z `amenity`, `shop`, `tourism`, `leisure` lub `office`. Pobierz pełne tagi oraz środki obiektów dla mapy; nie traktuj tego jako pełnej geometrii. Skrypt ładowarek jest osobnym ćwiczeniem, nie importerem wszystkich POI: przewidź rozszerzony importer.
- Nie zakładaj, że dwa źródła są niezależne albo że OSM jest nieomylną prawdą odniesienia. Wersje źródeł i licencje muszą pozostać widoczne.

## Funkcje i przepływ

1. Import Python + DuckDB normalizuje nazwy/adresy i rejestruje braki. Użytkownik ogląda podsumowanie: liczba POI, kategorii, błędów i odrzuceń.
2. Crosswalk mapuje obie taksonomie na stały słownik MVP: `food_drink`, `retail`, `accommodation`, `healthcare`, `education`, `transport`, `recreation`, `public_services`, `other`. PRD ma opisać znaczenie i granice każdej klasy, np. sklep medyczny a przychodnia.
3. Kod obsługuje jednoznaczne mapowania słownikowe. Jev rozstrzyga pozostałe przypadki i zwraca wynik w tym samym słowniku. `other` oznacza znaną kategorię poza słownikiem, a nie techniczny błąd lub niskie prawdopodobieństwo.
4. Kod wyszukuje pary kandydatów w ustalonym promieniu, oblicza odległość i prezentuje je obok siebie. Model dostarcza ocenę, a kod wybiera ścieżkę `same_place`, `different_place` lub `human_review`; końcowe scalenie wymaga określonej reguły lub zgody redaktora.
5. Dashboard ma mapę źródeł i par, filtry kategorii i statusu, kolejkę posortowaną według niepewności, szczegóły porównywanych pól oraz akcje "To samo miejsce", "Różne miejsca", "Odłóż" i korektę kategorii. Po akcji widać autora, czas i poprzednią decyzję.
6. Eksport obejmuje POI, kategorię wspólną, źródłowe ID, decyzję, prawdopodobieństwa i osobny plik nierozstrzygniętych rekordów. Nie nadpisuj danych źródłowych.

## Jev: wejścia, zamknięte odpowiedzi i sterowanie w kodzie

- Choice kategorii otrzymuje tylko nazwę miejsca i oryginalne kategorie z danego źródła. Zwraca jedną z dziewięciu klas słownika i rozkład prawdopodobieństw. Nie otrzymuje etykiety referencyjnej ani decyzji człowieka. Przy pustym wejściu kod kieruje do `human_review` bez wywołania modelu.
- Noul duplikatu pyta: "Czy rekord A i rekord B opisują to samo fizyczne miejsce?" Otrzymuje nazwy, oryginalne kategorie, adresy, jawne publiczne marki/operatorów i odległość wyliczoną przez kod. Wynik to prawdopodobieństwo `true`/`false`; ID służą tylko do audytu poza oceną semantyczną.
- Progi akceptacji/odrzucenia i pasmo `human_review` są konfiguracją kodu. Brak kandydata, kilku równie dobrych kandydatów, niepewność, awaria modelu i konflikt z wcześniejszą decyzją człowieka mają oddzielne stany. API nie może samodzielnie zatwierdzać scaleń.

## Ewaluacja i kontrole jakości

- Przygotuj słabo etykietowany zbiór rekordów, dla których OSM i Overture zgadzają się co do kategorii po niezależnym deterministycznym crosswalku. Połącz je najpierw po silnych przesłankach, np. zgodnym adresie i publicznym identyfikatorze, z kontrolą odległości; nie używaj oceny badanego Jev do tworzenia etykiet.
- Ręcznie sprawdź próbkę zgodności oraz osobno pary niezgodne, różne i niepewne. Sama zgodność źródeł faworyzuje łatwe przypadki i nie jest dowodem poprawności. Nie ucz i nie oceniaj na tej samej lokalizacji; wydziel walidację progów oraz test.
- Dla kategorii raportuj accuracy per klasa i ogółem, macro-F1, macierz pomyłek i liczebności. Dla Noul raportuj precision/recall dla prawdziwych i fałszywych par, koszt fałszywego scalenia oraz coverage i jakość po abstencji. Wskaż klasy bez wystarczających etykiet.
- Kod sprawdza: ID i ich powtarzalność, geometrię/CRS/bbox, kolejność współrzędnych, brak nazwy, nieznane kategorie, duplikaty w ramach jednego źródła i rekordy spoza obszaru. Raport ma rozliczać każde wejście jako poprawne, odrzucone albo do weryfikacji.
- Scenariusze akceptacji: ta sama placówka z inną pisownią, oddziały jednej sieci na sąsiednich ulicach, dwa podmioty pod jednym adresem, POI bez kategorii, konflikt człowieka z modelem, pusty zbiór, ponowny import i niedostępność OpenRouter. Cele liczbowe jakości i limit rozmiaru MVP ustal po policzeniu danych.

## Poza zakresem

Edycja źródeł publicznych, globalna taksonomia, trenowanie modelu, automatyczne rozstrzyganie wszystkich konfliktów, harmonogram produkcyjny, dane firmowe, pełny system ról i aplikacja mobilna.

## Wspólne ograniczenia

- To lokalne MVP dla jednego obszaru, uruchamiane na Windows 11 i Linux przez Python 3.12 + uv, bez Docker, WSL i Hyper-V. Pipeline Python + DuckDB przygotowuje dane i agregaty; dashboard korzysta z jego wyników.
- Dashboard WWW ma mapę MapLibre GL JS z kaflami OpenFreeMap, bez klucza API (np. styl `https://tiles.openfreemap.org/styles/liberty`). Atrybucje "© OpenStreetMap contributors", OpenFreeMap i OpenMapTiles pozostają widoczne. Dodaj atrybucje warstw tematycznych.
- Styl wizualny aplikacji weź z tokenów i zasobów utworzonych podczas kursu w `assets/`, a jeśli istnieje, także z `docs/design-guidelines.md`. Nie wymyślaj nowego brandingu; brak tokenów zgłoś jako pytanie.
- Wejścia pozostają tylko do odczytu. Zapisuj oddzielnie wyniki, raport jakości i decyzje użytkownika. Błąd pobrania, pusty zbiór i brak wartości to różne stany, nigdy poprawne zera.
- Korzystamy tylko z publicznych danych wskazanych poniżej. Do zewnętrznych modeli wysyłamy wyłącznie jawnie wymienione pola; bez kluczy, prywatnych danych i całej bazy. Klucz OpenRouter pozostaje po stronie backendu.
- Jev by TypeSafe przez OpenRouter jest modelem decyzji semantycznych. PRD opisuje typy pytań i zamknięte wyniki, a aktualny identyfikator modelu, zgodność transportu z Noul/Choice i format API trzeba sprawdzić przed integracją. Brak obsługi lub awaria daje jawny stan niedostępności, nigdy wymyślony wynik. Nie wywołuj płatnego API podczas tworzenia PRD.
- Utrwalaj wersję danych, obszar, datę pobrania, konfigurację reguł, wersję modelu i pytania oraz wynik i prawdopodobieństwa. Ponowne przetworzenie tych samych wejść nie tworzy nowych duplikatów; decyzje człowieka mają trwały ślad.

Przygotuj funkcjonalne PRD: problem, użytkownicy, główny przepływ, historie użytkownika, mierzalne kryteria akceptacji, błędy i puste stany, jakość danych, ewaluacja, zakres MVP i poza zakresem oraz założenia i pytania. Użyj zainstalowanego `write-prd`, nie przepisuj jego metodyki. Szczegóły architektury pozostaw do osobnego ADR. Zapisz wynik po polsku w `docs/PRD.md`; nie implementuj jeszcze aplikacji. Jeśli ten plik istnieje, najpierw ustal z użytkownikiem, czy opis dotyczy aktualnego produktu.
