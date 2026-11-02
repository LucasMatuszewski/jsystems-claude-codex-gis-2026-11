# PRD prompt: Monitorowanie jakości powietrza

**Jak użyć:** uruchom zainstalowany skill `write-prd` (`claude` -> `/write-prd`) i wklej cały poniższy prompt jako opis produktu. Możesz też wkleić go bezpośrednio i pozwolić skillowi się aktywować. Odpowiedz na pytania skilla. Wynik zapisz jako `docs/PRD.md`.

---

Przygotuj PRD produktu "Mapa pomiarów jakości powietrza". Analityk porównuje stacje GIOŚ i szeregi pomiarowe, żeby wykrywać braki, opóźnione dane i nietypowe wartości wymagające weryfikacji. Numeryczne wykrywanie anomalii należy do kodu i statystyki, nie do modelu językowego.

## Użytkownicy i dane

- Inżynier ETL sprawdza kompletność i świeżość pobrania oraz odtwarza raport.
- Analityk środowiskowy porównuje stacje i weryfikuje flagi anomalii.
- Odbiorca dashboardu ogląda pomiary z oznaczeniem źródła i ograniczeń, bez porady medycznej.
- Publiczne [API GIOŚ](https://powietrze.gios.gov.pl/pjp/content/api), [dokumentacja OpenAPI](https://api.gios.gov.pl/pjp-api/swagger-ui/index.html), wersja `/pjp-api/v1/rest/`: `station/findAll`, `station/sensors/{stationId}` i `data/getData/{idSensor}`. Obsłuż JSON-LD i paginację. Nie opieraj się na wycofanych endpointach bez `v1`.
- Skrypt `course-materials/exercise-data/real/download_gios_air.py` pobiera stacje i ostatnie pomiary dla kilku stacji, domyślnie w Łodzi. To punkt startu; dłuższa historia wymaga kolejnych snapshotów lub oficjalnego archiwum, z osobno ustalonym zakresem.
- Zachowaj ID stacji i stanowiska, współrzędne, nazwę, miejscowość, kod zanieczyszczenia, jednostkę, lokalny czas pomiaru i UTC pobrania. Wszystkie pomiary API są w µg/m³, także CO; nie porównuj ich bez konwersji z widokiem podającym mg/m³. Dane bieżące mogą być nieweryfikowane i później skorygowane.

## Funkcje i przepływ

1. Użytkownik wybiera kilka stacji, zanieczyszczenie i okno czasu. Pipeline Python + DuckDB pobiera i normalizuje dane z ograniczeniem liczby żądań, retry i jawnym raportem braków.
2. Dashboard WWW pokazuje mapę stacji, panel ostatniego dostępnego pomiaru z jego rzeczywistym czasem oraz wykres szeregu. Filtry obejmują stację, substancję i okres. Pusta wartość pozostaje luką, a nie zerem lub interpolacją udającą pomiar.
3. Kod oznacza braki, duplikaty, opóźnione pomiary, niemożliwe wartości i odchylenia statystyczne, np. względem mediany oraz MAD w oknie. PRD ma ustalić minimum obserwacji i postępowanie przy MAD=0. Przy zbyt krótkim szeregu pokaż `insufficient_data`.
4. Porównanie sąsiednich stacji dotyczy tej samej substancji, jednostki i okna czasowego; kod oblicza odległość i dobiera sąsiadów. Brak sąsiada jest odrębnym stanem, nie dowodem awarii. Flaga anomalii nie oznacza automatycznego usunięcia ani korekty pomiaru.
5. Analityk ogląda dowody flagi, próg i wartości referencyjne, oznacza `confirmed_issue`, `valid_event` albo `needs_review` i eksportuje raport. Zachowaj oryginalne dane.
6. Mapa i raport pokazują atrybucję GIOŚ, datę pobrania, status weryfikacji danych i informację, że to narzędzie analityczne, a nie oficjalny system ostrzegania.

## Opcjonalny Jev: wyłącznie semantyka tekstu

Jev by TypeSafe przez OpenRouter jest rozszerzeniem opcjonalnym, wyłączonym w MVP. Przykład: przypisanie typu otoczenia stacji na podstawie publicznej nazwy stacji, opisu lokalizacji i metadanych tekstowych GIOŚ, o ile takie opisy rzeczywiście istnieją. Wejście nie zawiera serii pomiarów, wartości liczbowych, sąsiednich odczytów ani oczekiwanej etykiety. Sama nazwa ulicy często nie wystarcza.

Choice ma stałe odpowiedzi `traffic`, `industrial`, `urban_background`, `rural_background`, `unknown`. Definicje klas i semantyka `unknown` muszą być zapisane; wynik to klasa i prawdopodobieństwa. Kod stosuje próg abstencji i nadaje stan `human_review` przy niepewności. Model nie diagnozuje czujnika, nie ustala progów zdrowotnych i nie wykonuje numerycznej detekcji anomalii.

Jeśli rozszerzenie zostanie wybrane, etykiety referencyjne pochodzą z niezależnej oficjalnej klasyfikacji stacji (ukrytej przed modelem) lub ręcznej anotacji jawnych opisów. Podział na walidację i test jest po stacji, bez przecieku tej samej nazwy. Mierz accuracy per klasę, liczebności, macierz pomyłek i coverage po abstencji; oceniaj także przypadki z niepełnym tekstem. Bez opisów i etykiet pomiń moduł zamiast dorabiać dane. Awaria modelu nie przerywa raportu pomiarowego.

## Kontrole i akceptacja

- Walidacja kodu: ID, współrzędne, schemat JSON-LD i kompletność stron, jednostki, null, powtórzenia `(sensor_id, czas)`, stare odczyty, lokalna strefa czasu i zmiana czasu, brak danych stanowisk manualnych w bieżącym API, niespójne okna sąsiednich stacji.
- Sprawdź: stały szereg, pojedynczy skok, długą lukę, MAD=0, wszystkie wartości null, brak sąsiada, dwie jednostki, błąd HTTP i korektę tego samego odczytu przy kolejnym pobraniu. Osobno testuj reguły liczbowe na jawnych kontrolowanych seriach i import na realnej próbce API.
- Zaproponuj mierzalne kryteria dla oznaczania flag i ręcznie sprawdzonych przypadków. Nie deklaruj czułości detektora na realnych zdarzeniach bez etykiet. Flagi mają pokazywać regułę i dowód, nie generowane uzasadnienie AI.

## Poza zakresem

Porady zdrowotne, oficjalne alerty smogowe, predykcja pogody i stężeń, kalibracja urządzeń, automatyczna korekta pomiarów, zastępowanie statystyki przez AI, całodobowy serwis produkcyjny i dane prywatne.

## Wspólne ograniczenia

- To lokalne MVP dla jednego obszaru, uruchamiane na Windows 11 i Linux przez Python 3.12 + uv, bez Dockera, WSL i Hyper-V. Pipeline Python + DuckDB przygotowuje dane i agregaty; dashboard korzysta z jego wyników.
- Dashboard WWW ma mapę MapLibre GL JS z kaflami OpenFreeMap, bez klucza API (np. styl `https://tiles.openfreemap.org/styles/liberty`). Atrybucje "© OpenStreetMap contributors", OpenFreeMap i OpenMapTiles pozostają widoczne. Dodaj atrybucje warstw tematycznych.
- Styl wizualny aplikacji weź z tokenów i zasobów utworzonych podczas kursu w `assets/`, a jeśli istnieje, także z `docs/design-guidelines.md`. Nie wymyślaj nowego brandingu; brak tokenów zgłoś jako pytanie.
- Wejścia pozostają tylko do odczytu. Zapisuj oddzielnie wyniki, raport jakości i decyzje użytkownika. Błąd pobrania, pusty zbiór i brak wartości to różne stany, nigdy poprawne zera.
- Korzystamy tylko z publicznych danych wskazanych poniżej. Do zewnętrznych modeli wysyłamy wyłącznie jawnie wymienione pola; bez kluczy, prywatnych danych i całej bazy. Klucz OpenRouter pozostaje po stronie backendu.
- Jev by TypeSafe przez OpenRouter jest modelem decyzji semantycznych. PRD opisuje typy pytań i zamknięte wyniki, a aktualny identyfikator modelu, zgodność transportu z Noul/Choice i format API trzeba sprawdzić przed integracją. Brak obsługi lub awaria daje jawny stan niedostępności, nigdy wymyślony wynik. Nie wywołuj płatnego API podczas tworzenia PRD.
- Utrwalaj wersję danych, obszar, datę pobrania, konfigurację reguł, wersję modelu i pytania oraz wynik i prawdopodobieństwa. Ponowne przetworzenie tych samych wejść nie tworzy nowych duplikatów; decyzje człowieka mają trwały ślad.

Przygotuj funkcjonalne PRD: problem, użytkownicy, główny przepływ, historie użytkownika, mierzalne kryteria akceptacji, błędy i puste stany, jakość danych, ewaluacja, zakres MVP i poza zakresem oraz założenia i pytania. Użyj zainstalowanego `write-prd`, nie przepisuj jego metodyki. Szczegóły architektury pozostaw do osobnego ADR. Zapisz wynik po polsku w `docs/PRD.md`; nie implementuj jeszcze aplikacji. Jeśli ten plik istnieje, najpierw ustal z użytkownikiem, czy opis dotyczy aktualnego produktu.
