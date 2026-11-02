# Ładowarki EV: dane przestrzenne, decyzje Jev i ocena jakości

To rekomendowane ćwiczenie dla osób pracujących z danymi GIS. Budujesz aplikację z Claude Code i Codexem: rozpoznajesz dane, uzgadniasz PRD, zlecasz implementację z testami, sprawdzasz wyniki i robisz review. W repozytorium są instrukcje i prompty, a rozwiązanie piszesz podczas zajęć.

Wynik: powtarzalny pipeline Python + DuckDB oraz dashboard z mapą ładowarek OSM i Overture, tabelą kandydatów do scalenia, wynikami Jev i kolejką ręcznej weryfikacji. Model ocenia semantykę; kod oblicza odległości, stosuje progi i zapisuje decyzje.

Pracuj na Windows 11 lub Linux, z Pythonem 3.12 i uv, bez Dockera, WSL i Hyper-V. Używamy publicznych danych i klucza OpenRouter po stronie backendu. Nie używamy danych firmowych ani prywatnych. Trening na Modal jest osobnym, opcjonalnym rozszerzeniem.

## Źródła i licencje

- [OpenStreetMap](https://www.openstreetmap.org/copyright), pobierane przez [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API): amenity=charging_station, pełne tagi i tożsamość (osm_type, osm_id). Licencja ODbL 1.0; pokaż atrybucję "© OpenStreetMap contributors" i sprawdź obowiązki przed udostępnieniem pochodnej bazy. Współrzędne środka way/relation nie są pełną geometrią.
- [Overture Places](https://docs.overturemaps.org/guides/places/), publiczne GeoParquet: nazwy, kategorie, identyfikatory i geometria. Zapisz wydanie z [katalogu STAC](https://stac.overturemaps.org/catalog.json) oraz sources każdego rekordu. [Licencje Overture](https://docs.overturemaps.org/attribution/) obejmują zależnie od źródła m.in. CDLA Permissive 2.0 i Apache 2.0; nie przypisuj jednej licencji wszystkim warstwom.
- [Downloadery i ich instrukcja](../../exercise-data/real/README.md) dają punkt startowy dla tego samego bbox Łodzi. Nie pobierają dróg ani całego kontekstu sąsiadów. Kontekst wymaga także zwykłych POI, nie samego --ev-only.
- [Jev: indeks dokumentacji](https://docs.typesafe.ai/llms.txt), [tutorial OpenRouter](https://openrouter.ai/docs/guides/community/jev-tutorial), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul). Sprawdź aktualny kontrakt przed implementacją. Jev ma endpoint decyzji, a nie standardowe Chat Completions.

Surowe pobrania zachowaj tylko do odczytu w ignorowanym katalogu danych. Zapisz źródło, zakres, czas pobrania, wydanie, licencje i sumy kontrolne. Publiczne nie oznacza pozbawione ograniczeń licencyjnych.

## Co ocenia Jev, a co robi kod

| Ocena | Wejście modelu | Zamknięty wynik | Decyzja kodu |
|---|---|---|---|
| Choice: kto może korzystać z ładowarki? | name, operator, brand, network, fee, opening_hours, tagi gniazd i mocy; nazwy i kategorie maksymalnie 3 najbliższych POI w 100 m | public, customers_only, private, unknown i prawdopodobieństwa | Przy niskim największym prawdopodobieństwie abstain; osobno model_unavailable przy błędzie |
| Noul: czy para opisuje tę samą fizyczną lokalizację ładowania? | Pola obu rekordów, adresy i operator, jeśli istnieją, oraz odległość obliczona przez kod | Prawdopodobieństwo odpowiedzi "tak" | Osobne progi na same_site, different_site, human_review; dopiero potem reguły scalenia |

Unknown jest odpowiedzią modelu o braku podstaw. Abstain jest decyzją kodu o niewystarczającym prawdopodobieństwie. Błąd API jest błędem, nigdy odpowiedzią public lub "nie". Pole confidence opisuje koncentrację rozkładu; do ćwiczenia progów użyj max(probabilities), nie zakładaj równoważności tych wartości.

Kod odpowiada za CRS i jednostki, dystans, przestrzenne ograniczenie kandydatów, rozstrzyganie wielu dopasowań, progi, zapis audytu oraz eksport. Odległość poniżej 150 m i identyczny operator nie dowodzą, że to samo miejsce. Model nie dostaje całej bazy ani nie wykonuje automatycznych edycji OSM.

## Budżet i zasady eksperymentu

- Zacznij od 3 próbnych rekordów, potem od próby warstwowej do 60 rekordów oraz najwyżej 12 par Noul. Próbne wywołania też wchodzą do budżetu. Nie uruchamiaj płatnych wywołań podczas samego tworzenia PRD.
- Limit całego eksperymentu OpenRouter: mniej niż 1 USD. Ustaw limit klucza/konta i niezależny licznik w wrapperze, z rezerwacją kosztu przed wywołaniem. Ogranicz długość wejścia, liczbę prób i współbieżność. Brak informacji o koszcie nie oznacza darmowego wywołania.
- Zapisuj żądanie bez nagłówka autoryzacji, odpowiedź, model ze snapshotem, wersję pytania, tokeny, koszt, czas i błędy. Cache po skrócie wejścia oraz wersji pytania zapobiega ponownemu płaceniu przy ewaluacji progów.
- Wysyłaj wyłącznie jawny zestaw cech. Access i etykieta nie mogą trafić do modelu przez JSON, nazwę pliku, opis, log włączony do kontekstu ani cechy pochodne. Klucza nie wypisuj i nie dodawaj do Git.
- Nie uruchamiaj Overpass równolegle na wszystkich stanowiskach. Najpierw mały bbox; większe pobranie wykonuje jedna osoba i udostępnia lokalnie zgodnie z licencją. HTTP 429/502/504 wymaga ograniczonego retry z przerwą, a nie pętli bez limitu.

## 0. Uzgodnij zakres i kontrakt

Pełny punkt startowy: [prompt PRD dla mapy ładowarek](../../Prompt%20examples/PRD-ev-charging-map-conflation.md). Poniższy prompt wklej do Claude Code. Pytania o zakres rozstrzygnij przed implementacją.

~~~text
Budujemy podczas kursu aplikację GIS opisaną w course-materials/exercises/ev-chargers-jev/README.md. Przeczytaj ten plik, AGENTS.md, README.md i course-materials/Prompt examples/PRD-ev-charging-map-conflation.md. Nie czytaj innych materiałów kursowych bez potrzeby wynikającej z mojego polecenia. Sprawdź stan repozytorium i istniejące docs/PRD.md oraz ADR, jeśli są. Nie nadpisuj uzgodnionego produktu. Użyj write-prd, jeśli skill jest dostępny, i uzgodnij ze mną zakres. Zapisz po polsku docs/PRD.md z kryteriami akceptacji, błędami i pustymi stanami. Rozdziel mały obszar dashboardu od większego zbioru do ewaluacji etykiet. MVP nie obejmuje pokrycia dróg ani statusu ładowarek na żywo; te elementy pozostaw jako rozszerzenia. Uwzględnij Choice, Noul, unknown, abstain, model_unavailable, brak wycieku access oraz budżet poniżej 1 USD. Nie pisz jeszcze kodu i nie wywołuj płatnego API.
~~~

## 1. Pobierz i opisz dane

Prompt do Codexa po zatwierdzeniu zakresu:

~~~text
Przeczytaj AGENTS.md, uzgodnione docs/PRD.md, course-materials/exercise-data/real/README.md i skrypty download_osm_chargers.py oraz download_overture_places.py z tego katalogu. Sprawdź --help narzędzi. Przygotuj krótki plan importu, następnie dodaj testy przed kodem i zaimplementuj import zgodny z PRD. Zacznij od bbox Łodzi 19.25,51.65,19.65,51.90 dla OSM i Overture. OSM pobierz przez Overpass z identyfikującym User-Agent, timeoutem i maksymalnie trzema próbami z przerwą; wykryj niepełną odpowiedź z remark. Zachowaj node/way/relation, pełne tagi i rozróżniaj środek od geometrii. Overture przypnij do wydania odczytanego z oficjalnego STAC, sprawdź rzeczywisty schemat i taksonomię. Pobierz osobno ładowarki oraz wszystkie POI potrzebne jako kontekst sąsiedztwa. Nie dodawaj surowych danych do Git i nie modyfikuj oryginałów. Zapisz manifest źródeł, licencji, bbox, wydania, daty, rozmiarów, liczników i sum kontrolnych. Zero rekordów, błąd sieci i brak pola to odrębne przypadki. Jeśli etykiet jest za mało, pokaż liczby i zaproponuj pojedyncze pobranie dla Polski przez trenera; nie rozszerzaj obszaru samoczynnie. Uruchom testy i rzeczywisty import, pokaż komendy oraz wyniki.
~~~

Nie oczekuj 60 etykiet z małego bbox. Ogólnopolski zbiór ewaluacyjny może być osobnym plikiem, a mapa nadal pokazywać tylko Łódź.

## 2. Zbadaj dane w DuckDB

~~~text
Przeczytaj docs/PRD.md i manifest pobrań. Użyj DuckDB ze spatial do eksploracji rzeczywistych lokalnych plików. Zanim napiszesz SQL, sprawdź wersję i DESCRIBE, nie zakładaj starego schematu Overture categories zamiast taxonomy. Policz wejścia, unikalne ID, puste nazwy, rozkład kategorii, wartości access oraz obecność operator, brand, name, fee i dowolnego socket:*. Sprawdź poprawność geometrii i zasięg. Dla Polski przelicz punkty z WGS84 do EPSG:2180 z jawną kolejnością osi; testem sprawdź odległość znanej pary, a nie tylko typ wyniku. Oblicz maksymalnie 3 najbliższe Overture POI w 100 m od każdej ładowarki. Najpierw ogranicz przestrzennie kandydatów, potem sortuj po odległości; nie twórz iloczynu całych zbiorów. Brak sąsiada pozostaje pustą listą. Zapisz SQL, raport liczników i czas wykonania. Nie wywołuj modelu.
~~~

## 3. Zbuduj etykiety i bezpieczne cechy

~~~text
Zaimplementuj po testach przygotowanie zbioru ewaluacyjnego zgodnie z docs/PRD.md. Etykietuj tylko OSM mające access: yes -> public, customers -> customers_only, private lub no -> private. Pozostałe wartości policz osobno i pozostaw bez etykiety; nie zamieniaj ich na unknown. Zachowaj mapowanie w raporcie. Przygotuj powtarzalną próbę warstwową do 60 rekordów, docelowo po 20 z każdej z trzech klas. Nie powielaj rekordów, by wypełnić brakującą klasę. Grupuj fizyczne lokalizacje przed podziałem na walidację i test, np. konserwatywnie łącząc obiekty w promieniu 150 m. Ta sama grupa nie może trafić do obu części. Dopiero potem próbkuj w ramach klas. Osobno zapisz etykiety i cechy. Cechy buduj przez allowlist: name, operator, brand, network, fee, opening_hours, gniazda i moc oraz nazwy i kategorie maksymalnie trzech sąsiadów z DuckDB w 100 m. Dodaj test, który wykrywa obecność access i etykiety na dowolnym poziomie żądania modelu. Nie przekazuj ścieżek plików z etykietami. Zapisz liczby klas, grup, braków kontekstu i podziałów. Nie wywołuj jeszcze API.
~~~

## 4. Zbuduj wrapper Jev

~~~text
Zaimplementuj po testach backendowy wrapper Jev. Przeczytaj https://docs.typesafe.ai/llms.txt oraz https://openrouter.ai/docs/guides/community/jev-tutorial i odpowiednią referencję endpointu decyzji. Użyj typesafe-ai, jeśli skill jest dostępny. Zweryfikuj aktualny model i kontrakt; nie używaj Chat Completions i nie zgaduj schematu. Klucz pobierz wyłącznie z OPENROUTER_API_KEY, bez wypisywania. Choice pyta "Who is allowed to use this EV charging station?" i ma cztery opcje: public - dowolny kierowca, także odpłatnie; customers_only - tylko klienci lub goście gospodarza; private - mieszkańcy, pracownicy, flota lub osoby upoważnione; unknown - dostarczone dane nie rozstrzygają. Wyślij wyłącznie cechy z allowlist, bez access, etykiety i całej bazy. Waliduj typ odpowiedzi, komplet opcji, zakres i sumę prawdopodobieństw. Dodaj timeout, ograniczone retry liczone do budżetu, trwały cache i licznik kosztu z rezerwacją przed każdym wywołaniem. Domyślne limity: 3 próby kontrolne, do 60 rekordów, do 12 par, mniej niż 1 USD łącznie. Gdy koszt nie jest zwrócony, zachowaj konserwatywną rezerwację. API error daje model_unavailable, nigdy sztuczne prawdopodobieństwa. Najpierw pokaż rzeczywistą bezpieczną odpowiedź wraz ze statusem i nagłówkami bez autoryzacji; dopiero z niej wyprowadź fixture, jeśli potrzebna. Następnie wykonaj 3 kontrolne wywołania i sprawdź ręcznie pola. Zapisz request bez sekretu, pełną odpowiedź, snapshot modelu, tokeny, koszt i czas.
~~~

## 5. Oceń Choice i zbadaj abstencję

~~~text
Na zatwierdzonym zbiorze wykonaj najwyżej 60 ocen Choice, korzystając z cache i pozostałego budżetu. Nie zmieniaj pytania po obejrzeniu testu. Oddziel walidację od testu i zachowaj rozłączne grupy lokalizacji. Policz accuracy, precision, recall i support każdej klasy oraz macierz pomyłek: wiersze to etykieta OSM, kolumny to przewidywanie, również unknown. Pokaż majority baseline i ograniczenie próby warstwowej: ogólna accuracy nie opisuje częstości klas w Polsce. Dla max(probabilities) porównaj progi 0, 0.5, 0.6, 0.7, 0.8, 0.9 i 0.95: liczba przyjętych, coverage, selective accuracy i błędy wśród odrzuconych. Puste przyjęcia mają accuracy nieokreślone, a nie 100%. Dobierz próg wyłącznie na walidacji według uzgodnionego celu i minimalnego coverage, zamroź go i dopiero potem oceń na teście. Jeśli żaden próg nie spełnia celu, napisz to wprost. Unknown nie jest abstencją. OSM access to słaba, czasem nieaktualna etykieta, nie zweryfikowana prawda terenowa. Ręcznie obejrzyj kilka pomyłek i przypadków bez nazwy. Zapisz raport, rozkłady, czasy, koszty i ograniczenia; nie obiecuj 95% jakości.
~~~

Zmiana progu działa na zapisanych prawdopodobieństwach i nie wymaga następnych wywołań API.

## 6. Wygeneruj pary i użyj Noul

~~~text
Po testach dodaj generowanie kandydatów OSM x Overture EV w odległości do 150 m, obliczonej w metrach przez kod. Zachowaj wszystkie kandydatury i odległości oraz odrzuć iloczyn całych zbiorów. Próbę do 12 par wybierz tak, by obejmowała bliskie i dalsze punkty, brak nazwy, różne nazwy operatora i wielu kandydatów. Noul pyta "Do these two records describe the same physical EV charging site?". Przekaż tylko potrzebne publiczne pola obu rekordów i obliczoną odległość; model nie mierzy dystansu. Użyj wrappera z tym samym budżetem. Zapisz prawdopodobieństwo tak, bez zmiany go na etykietę wzorcową. Ręcznie oznacz oddzielny zestaw pozytywnych i negatywnych par na podstawie udokumentowanych dowodów albo wykorzystaj identyczny identyfikator lokalizacji, jeśli faktycznie występuje w obu źródłach. Sama zgodność operatora, bliskość i odpowiedź Jev nie są prawdą wzorcową. Gdy nie masz wiarygodnych etykiet, pokaż przykłady i brak podstaw do policzenia jakości zamiast wymyślać precision/recall. Progi startowe 0.3 i 0.7 są hipotezą do walidacji: poniżej different_site, powyżej same_site, pomiędzy human_review. Automatyczne scalenie wymaga dodatkowo reguł konfliktów i wielu kandydatów; nie łącz całej sieci przechodnio przez jedno podobieństwo.
~~~

## 7. Podłącz dashboard i zrób review

~~~text
Przeczytaj docs/PRD.md, właściwe ADR i uzgodnione assets oraz docs/design-guidelines.md, jeśli istnieją. Po testach podłącz zapisane wyniki pipeline'u do dashboardu, bez wywołań Jev z przeglądarki. Pokaż warstwy OSM i Overture, tabelę par, nazwy/operatorów, dystans w metrach, rozkład Choice, Noul i decyzję kodu. Dodaj filtry źródła, operatora, public/customers_only/private/unknown, abstain i model_unavailable oraz przyciski zatwierdzenia, odrzucenia i odroczenia pary z trwałym śladem. Zmiana progu korzysta z cache. Przy błędzie API pokaż stan niedostępności; nie przedstawiaj go jako publicznej ładowarki. Nie przedstawiaj braku access jako potwierdzonej dostępności. Mapa MapLibre GL JS z OpenFreeMap musi zachować widoczne atrybucje podkładu oraz danych. Nie dodawaj statusu ładowarki na żywo ani pokrycia dróg. Uruchom rzeczywistą aplikację, przejdź import -> wyniki -> filtr -> para -> decyzja -> ponowne otwarcie i eksport. Sprawdź konsolę, polskie teksty, atrybucję i zgodność z uzgodnionym wyglądem; zapisz zrzuty ekranów. Osobno podaj wyniki testów, uruchomienia i ręcznego QA.
~~~

Prompt do drugiego agenta jako recenzenta:

~~~text
Zrób review zmian względem docs/PRD.md i właściwych ADR. Nie zmieniaj kodu. Sprawdź wyciek access i klucza, CRS i metry, kompletność pobrań, rozłączność grup między walidacją i testem, dobór progu bez podglądania testu, rozróżnienie unknown/abstain/model_unavailable, trwałość cache i budżetu, wiele kandydatur oraz licencje. Sprawdź, czy testy obejmują realne błędy, a wyniki raportu wynikają z zapisanych danych. Zgłoś konkretne problemy z plikiem, linią, skutkiem i sposobem sprawdzenia. Nie uznawaj samego przejścia testów za dowód działania aplikacji.
~~~

## Wyniki referencyjne i interpretacja

Pomiar z 2 listopada 2026, Overture 2026-10-21.0, Jev typesafe/jev-1.13-20260917. Poniższe zaokrąglenia są punktem odniesienia dla odtworzenia eksperymentu, nie kryteriami akceptacji ani obietnicą jakości na innym wydaniu danych.

| Pomiar | Wynik referencyjny |
|---|---|
| OSM, obszar administracyjny Polski | Około 3000 ładowarek; około 700 z access, około 680 z obsługiwanymi etykietami |
| Obecność tagów OSM | operator około 2000, brand około 400, name około 350, fee około 950, dowolny socket:* około 800 |
| Overture, bbox 14.07,49.0,24.15,54.85 | Około 1.6 mln wszystkich POI i 3100-3200 POI EV; bbox zawiera także fragmenty sąsiednich krajów |
| Etykiety po mapowaniu | Około 410 public, 50 customers_only i 220 private |
| Próba Choice | 60 rekordów: po 20 na klasę; walidacja i test po 30, rozłączne grupy lokalizacji |
| Accuracy bez abstencji | 20% walidacja, 30% test; stała klasa na zbalansowanej próbie daje około 33% |
| Odpowiedź unknown | Około 65% wszystkich odpowiedzi; unknown nie ma wzorcowej etykiety w tym zbiorze |
| Próg 0.7 na zapisanych rozkładach | Walidacja: około 57% coverage i 24% selective accuracy; test: około 77% i 30% |
| Próg 0.9 | Walidacja: około 30% coverage i 11% selective accuracy; test: około 47% i 21% |
| Pary Noul | Około 1200 kandydatur dla całego OSM i 19 dla próby 60 OSM w 150 m; 12 przykładów, prawdopodobieństwa około 0.3-0.9, bez zweryfikowanej prawdy wzorcowej |
| Czas i koszt OpenRouter | Ewaluacja około 25 s; 71 rzeczywistych żądań: 59 Choice łącznie z próbą kontrolną i 12 Noul; powtarzające się stany korzystały z cache; około 42 tys. tokenów wejścia; API zwróciło koszt 0 USD, konserwatywna rezerwacja 0.71 USD |

**Wniosek do ćwiczenia:** z tych cech często nie da się ustalić prawa dostępu. Żaden z badanych progów na walidacji nie osiągnął celu 80% selective accuracy przy minimum 25% coverage. Nie włączaj automatycznego przypisywania dostępności. Wyższy próg nie poprawił automatycznie jakości, bo model bywa pewny odpowiedzi unknown. To użyteczny wynik negatywny: zmierz ograniczenia, pokaż kolejkę weryfikacji i zdecyduj, jakie dodatkowe dowody są potrzebne. Nie poprawiaj raportu przez usunięcie trudnych rekordów.

Każda klasa ma tylko 10 przykładów w każdym podzbiorze. Dla testu recall public wyniósł 70%, customers_only 20%, private 0%; precision odpowiednio około 88%, 100% i nieokreślone przy braku przewidywań private (w agregacji numerycznej można raportować 0 z jawnym opisem). Liczba 100% dotyczy zaledwie dwóch przewidywań customers_only. Podgląd tabeli progów na teście jest analizą opisową po zamrożeniu decyzji o braku wdrożenia, nie doborem progu.

Zwrócone 0 USD jest obserwacją konkretnej odpowiedzi API, nie obietnicą darmowego Jev. Zapisuj tokeny i sprawdzaj bieżący cennik oraz panel rozliczeń. Przykłady Noul pokazują różne wyniki także dla kilku kandydatów jednej stacji; nie zastępują oceny precision/recall na ręcznych etykietach.

## 8. Opcjonalnie: wytrenuj mały klasyfikator na Modal

To osobne zadanie: nazwa POI -> kategoria Overture, a nie dostępność ładowarki ani dopasowanie par. Nie porównuj jego accuracy bezpośrednio z accuracy Choice dostępności.

1. Załóż konto na [modal.com](https://modal.com/) i wybierz Starter. [Cennik](https://modal.com/pricing) sprawdzony 2 listopada 2026 podaje brak opłaty miesięcznej i 30 USD miesięcznie na compute. Sprawdź aktualne warunki, pozostały limit oraz budżet workspace przed treningiem; kredyty nie oznaczają nieograniczonego użycia. Aktualna dokumentacja wymaga ważnej metody płatności do użycia GPU. Jeśli nie chcesz jej dodawać, pomiń uruchomienie treningu. Możesz przygotować i sprawdzić zbiór bez GPU; wynik treningu nie jest wymagany do ukończenia ćwiczenia.
2. Zainstaluj CLI w PowerShell przy działającym uv i Pythonie 3.12. Nie potrzebujesz lokalnej karty NVIDIA. Logowanie otworzy przeglądarkę; nie wklejaj tokenu do promptu.

~~~powershell
$env:PYTHONUTF8="1"
uv venv --python 3.12
uv pip install modal
uv run modal setup
uv run modal profile current
~~~

3. Jeśli projekt ma już środowisko, uzgodnij z agentem instalację w jego zależnościach zamiast zastępować konfigurację. Sprawdź uv run modal --help i [instrukcję instalacji](https://modal.com/docs/guide).
4. Ustal limit pojedynczego treningu, np. 900 sekund na L4, i limit wydatków workspace. GPU L4 w sprawdzonym cenniku kosztuje 0.000222 USD/s, czyli około 0.13 USD za 10 minut samego GPU; CPU, RAM, przechowywanie i pozostałe zasoby są dodatkowo płatne. Pomiar czasu treningu nie jest rachunkiem końcowym.

Prompt przygotowania danych:

~~~text
Dodaj opcjonalny eksperyment nazwa POI -> główna kategoria Overture, oddzielony od pipeline'u EV. Po testach napisz prepare_poi_training_data.py. Użyj pobranych publicznych POI z Polski lub kilku miast, zapisz źródło i wydanie. Sprawdź rzeczywiste pola kategorii. Usuń puste nazwy, normalizuj Unicode i wielkość liter, usuń duplikaty nazw przed podziałem; nazwy z konfliktowymi kategoriami odrzuć i policz. Wybierz np. 8 kategorii z co najmniej 200 unikalnymi nazwami każda i zbalansuj do tej liczby, ale pokaż faktyczne liczby zamiast tworzyć brakujące rekordy. Zrób powtarzalny podział 80/10/10 na train/validation/test bez przecieku tej samej znormalizowanej nazwy; dodatkowo sprawdź powtarzające się marki. Wejściem ma być tylko nazwa, nie kategoria ani cechy ją kodujące. Zapisz JSONL lub Parquet, słownik klas, liczniki odrzuceń, rozmiary i test rozłączności. Nie wysyłaj jeszcze danych do chmury.
~~~

Prompt treningu:

~~~text
Najpierw przeczytaj bieżące oficjalne dokumenty Modal o funkcjach GPU, Image i Volume oraz dokumentację użytej wersji Transformers. Sprawdź uv run modal --help i uv run modal profile current bez wypisywania tokenów. Po testach przygotuj modal_train_classifier.py: mały wielojęzyczny encoder, np. distilbert/distilbert-base-multilingual-cased, z głowicą kategorii; jeden trening na L4, jedna epoka, timeout najwyżej 900 s, stały seed i przypięte zależności. Użyj Volume na dane i checkpoint, local_entrypoint do uploadu publicznego zestawu i wywołania funkcji. Nie deployuj endpointu. Podaj komendę uruchomienia oraz oszacowanie GPU, CPU i RAM; trening uruchom tylko na skonfigurowanym profilu w uzgodnionym budżecie. Walidacja służy do strojenia, test tylko do końcowej oceny. Zapisz accuracy, macro-F1, liczby klas, macierz pomyłek, czas, model, wersje i szacunek kosztu oddzielnie od kosztu z panelu. Po zakończeniu sprawdź, że aplikacja nie działa dalej. Jeśli profil jest niedostępny lub build/trening zawiedzie, zachowaj log i oznacz eksperyment jako nieprzetestowany lub nieudany, bez wymyślania metryk. Porównanie z Jev ma sens wyłącznie na identycznym zadaniu nazwa -> kategoria i tym samym holdoucie, w ramach pozostałego budżetu.
~~~

## Co oddajesz

- PRD i decyzje zakresowe, manifest wejść, powtarzalne komendy oraz pipeline z testami.
- Raport rzeczywistych liczników i jakości, macierze pomyłek, coverage przy progach, wersję pytań/modelu, koszty i ograniczenia.
- Dashboard z kolejką weryfikacji, zapisanymi decyzjami i dowodami ręcznego QA; brak kluczy i surowych baz w Git.
- Dla Modal, jeśli wybrany: manifest datasetu, podział, wynik lub dokładny błąd oraz sprawdzenie zakończenia aplikacji.
