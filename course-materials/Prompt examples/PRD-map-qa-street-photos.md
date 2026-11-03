# PRD prompt: kontrola atrybutów mapy ze zdjęć ulic

**Jak użyć:** uruchom skill `write-prd` (`claude` -> `/write-prd`) i wklej poniższy opis produktu. To przykład startowy: zmień go pod swoją pracę (inny atrybut, inne źródło, inny odbiorca raportu), odpowiedz na pytania skilla i zapisz wynik jako `docs/PRD.md`.

---

Tworzymy proof of concept (PoC) narzędzia **"Map Attribute QA Copilot"**. Analityk jakości danych mapowych chce szybciej znajdować miejsca, w których atrybuty dróg na mapie mogą nie zgadzać się z tym, co widać w terenie, i przekazywać do ręcznej weryfikacji tylko sensowne przypadki.

Dane wejściowe są w `course-materials/exercise-data/map-qa/` (opis w README tego katalogu):
- drogi OpenStreetMap (pełne tagi, m.in. `highway`, `maxspeed`, `surface`, `lanes`, `lit`, `sidewalk`),
- segmenty Overture Maps (`speed_limits`, `road_surface`, źródła i daty),
- prawdziwe zdjęcia ulic i znaków z Mapillary i Panoramax z pozycją, kierunkiem kamery i atrybucją,
- wykryte przez Mapillary znaki ograniczenia prędkości,
- te same tabele w Databricks (`workspace.map_qa`), dostępne przez CLI lub REST.

Przebieg pracy użytkownika:
- Analityk wybiera obszar (bbox) i atrybuty do kontroli w pierwszej wersji (np. ograniczenie prędkości i nawierzchnia).
- System wczytuje dane z plików albo z Databricks i pokazuje profil: liczby rekordów, kompletność tagów, odrzucone rekordy z przyczyną.
- Kod łączy każde zdjęcie z najbliższą drogą z uwzględnieniem odległości w metrach (EPSG:2180) i kierunku kamery. Niepewne połączenia (dwie drogi blisko, skrzyżowanie, droga serwisowa) są oznaczone, a nie ukryte.
- Kod porównuje atrybuty OSM i Overture i wyznacza kandydatów rozbieżności. Rozbieżność źródeł nie jest automatycznie błędem mapy: źródła mają różne daty, a Overture częściowo pochodzi z OSM.
- Model decyzyjny (OpenRouter, `openai/gpt-6-luna-decisions`, porównawczo `typesafe/jev-1.14`) dostaje tylko zdjęcie i neutralne pytanie zamknięte, np. "Jaka wartość jest na znaku ograniczenia prędkości?" (lista wartości + `brak znaku`) albo "Czy nawierzchnia jest utwardzona?". Model nie widzi tagów mapy ani etykiet. Kod stosuje próg pewności; poniżej progu wynik to `abstain`, a błąd API to `model_unavailable`.
- Kod zestawia odczyt ze zdjęcia z mapą i tworzy raport Markdown i HTML: kandydat, miniatura zdjęcia z atrybucją, wartość na mapie, odczyt modelu z prawdopodobieństwem, powód skierowania do człowieka. Raport jest dla człowieka, który podejmuje decyzję o poprawce.
- Każde wywołanie modelu ma limit liczby zapytań i kosztu na uruchomienie, cache po hashu obrazu i pytania oraz zapis kosztu w logu.
- Opcjonalnie (do dodania później):
  - prosty dashboard z mapą, listą kandydatów i przyciskami "potwierdź / odrzuć / do sprawdzenia" w Streamlit albo PySide6,
  - zapis decyzji analityka i eksport poprawek jako zadań (np. Jira),
  - kolejne atrybuty: liczba pasów, oświetlenie, chodnik, skrzyżowania i topologia.

Ewaluacja: część zdjęć ma etykiety referencyjne przygotowane przez agenta i drugi model. To robocza referencja, nie prawda terenowa. PRD ma określić, jak mierzymy trafność modelu (tylko etykiety pewne, z jawnymi mianownikami), jaki odsetek abstencji akceptujemy i ile może kosztować jedno uruchomienie.

Osobny dokument ADR opisze architekturę i wybór technologii; ten PRD skupia się na funkcjach, zachowaniu systemu, wynikach i kryteriach akceptacji.
