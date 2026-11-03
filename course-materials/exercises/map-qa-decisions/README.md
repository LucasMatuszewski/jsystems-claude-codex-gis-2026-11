# Kontrola mapy na rzeczywistych drogach i zdjęciach

Zbudujesz narzędzie dla analityka map QA. Połączysz drogi OpenStreetMap, segmenty Overture Maps i fotografie uliczne Krakowa z okolicami. Narzędzie ma wskazywać kandydatów wymagających sprawdzenia: rozbieżności atrybutów między mapami, brakujące dane, niepewne dopasowania oraz różnice między tym, co widać na zdjęciu, a zapisem mapy. Ostateczną ocenę podejmuje człowiek.

Model decyzyjny odpowiada na zamknięte pytania o obraz i zwraca prawdopodobieństwa. Kod normalizuje dane, dopasowuje drogi, stosuje progi i zapisuje raport. Zdjęcie nie jest dowodem wszystkich atrybutów drogi, a OSM i Overture nie są niezależnymi pomiarami: część Overture pochodzi z OSM.

## Punkt startowy

Pracuj w PowerShell na przygotowanej maszynie Windows, w `D:\jsystems-claude-codex-gis-2026-11`. Potrzebujesz Git, uv, Pythona 3.12, Claude Code i Codex CLI. WSL, Docker i konto Databricks nie są potrzebne do ścieżki lokalnej. Kod aplikacji, testy, PRD i ADR powstają podczas ćwiczenia.

```powershell
Set-Location D:\jsystems-claude-codex-gis-2026-11
```

```powershell
git status --short
```

[Pakiet danych](../../exercise-data/map-qa/README.md) zawiera rzeczywiste GeoParquet, manifest zdjęć, połączenia i część fotografii do rozpoczęcia offline. Pozostałe zdjęcia pobierzesz z manifestu. Syntetyczne rysunki są tylko małą pomocą do testów jednostkowych. Nie używaj ich jako obserwacji rzeczywistego terenu.

Jeśli masz już `docs/PRD.md`, porównaj go z nowym zadaniem i uzgodnij zmianę. Nie nadpisuj poprzedniej pracy. Przed zmianą agenta zakończ jego narzędzia, sprawdź diff i zapisz stan. Jeden agent edytuje dany plik w danej chwili.

**Agenci:** M1 Claude Code, M2 Codex, M3 Claude Code, M4-M5 Codex, M6 Claude Code, M7 Codex i Claude Code. M4-M5 pozostają w jednym narzędziu, aby przejść od planu do pierwszego etapu TDD.

**Budżet:** M1-M5 nie potrzebują płatnego API. `OPENROUTER_API_KEY` jest zmienną środowiskową przygotowanej VM. Sprawdzaj tylko obecność, nigdy wartość. W M6 najpierw jedno zdjęcie, następnie najwyżej 25 prób Luna i te same 5 zdjęć na Jev, w przydzielonej części wspólnego budżetu. Pierwsze wywołanie i błędy liczą się do limitu. Wyłącz retry również w SDK. Brak kosztu w odpowiedzi oznacza brak pomiaru, a nie zero.

## M1. PRD ze skillem

**Cel:** uzgodnić zachowanie narzędzia przed implementacją. **Agent: Claude Code.**

Sprawdź `/skills`, a jeśli wersja nie ma tej komendy, menu `/`. Wybierz `write-prd` albo poproś o użycie skilla po nazwie. W Codexie użyj `/skills` lub `$write-prd`. Instalacja skilli w `.agents/skills` nie jest częścią zwykłego klonu. Jeśli ich brakuje, użyj przygotowanego na VM zestawu lub uzgodnij instalację z prowadzącym; nie zastępuj instrukcji skilla zgadywaną treścią.

**Prompt do skopiowania:**

~~~text
Użyj zainstalowanego skilla write-prd. Przygotowujemy narzędzie dla analityka map QA, który kontroluje atrybuty i topologię dróg na podstawie publicznych danych Krakowa z okolicami. Przeczytaj AGENTS.md, README.md oraz course-materials/exercise-data/map-qa/README.md i course-materials/exercise-data/map-qa/sources.json. Nie czytaj innych materiałów kursowych. Sprawdź, czy istnieje docs/PRD.md; jeśli tak, porównaj zakres i zaproponuj korektę zamiast go zastępować.

Wejścia to osm_roads.parquet z pełnymi tagami i node_ids, overture_segments.parquet z GERS, regułami atrybutów i źródłami OSM, photos.csv, photo_road_links.csv i rzeczywiste zdjęcia. Analityk chce profilować dane, sprawdzić dopasowanie zdjęcia do właściwej drogi, porównać prędkość, nawierzchnię i klasę między mapami, a potem porównać wybrane cechy ze zdjęć. Interesują go także brakujące węzły skrzyżowań i podejrzane końce sieci. Współrzędne aparatu nie są pozycją znaku. Źródła mają różne daty, część tagów jest pusta, a kierunkowe i warunkowe ograniczenia trzeba zachować.

Na zdjęciu chcemy badać rodzinę klasy drogi, nawierzchnię, widoczne skrzyżowanie, znak ograniczenia i jego wartość, pasy w kierunku patrzenia, chodnik i oświetlenie. Nie wszystkie te pytania muszą wejść do pierwszego zakresu. Brak widoczności nie znaczy nieobecności. Wyniki to kandydaci do przeglądu, z dowodami, datami, odległością, niepewnością i licencjami; nie są automatyczną korektą mapy. Nie obiecuj, że próbka zawiera potwierdzony błąd.

Zanim napiszesz PRD, zadaj pytania o brakujące decyzje i poczekaj na moje odpowiedzi. Ustal użytkownika i jego kolejny krok po raporcie, zakres pierwszej wersji, wybór pytań, obsługę braku danych, sposób ręcznego przeglądu i limity kosztu. Zapytaj, czy chcę dodać prosty dashboard w Streamlit lub PySide6; jest opcjonalny. Nie wybieraj go za mnie. Nie przechodź do ADR ani kodu. Po odpowiedziach zapisz uzgodniony docs/PRD.md po polsku, mimo domyślnego języka skilla, z mierzalnymi kryteriami akceptacji i wyraźnym zakresem poza pierwszą wersją. Zatrzymaj się do przeglądu dokumentu.
~~~

**Twoja kontrola:** agent rzeczywiście pyta i czeka. Sprawdź, czy PRD rozróżnia niezgodność źródeł, niepewne dopasowanie i potwierdzony błąd. **Jeśli utkniesz:** wybierz na początek raport CLI i dwa atrybuty. **Rozszerzenie:** dodaj wymaganie kolejki przeglądu w prostym dashboardzie.

## M2. Profil trzech źródeł i połączeń

**Cel:** sprawdzić dane przed projektowaniem pipeline'u. **Agent: Codex.**

Najpierw uruchom lokalne polecenia z [README danych](../../exercise-data/map-qa/README.md), następnie przeczytaj i wykonaj zapytania w `profile.sql`. Zapytania opisują wejścia, nie wyliczają listy konfliktów.

**Prompt do skopiowania:**

~~~text
Przeczytaj AGENTS.md, uzgodniony docs/PRD.md oraz course-materials/exercise-data/map-qa/README.md, sources.json, photos.csv i photo_road_links.csv. Wolno czytać wskazany katalog danych kursowych; nie przeglądaj reszty course-materials/. Nie zmieniaj wejść ani nie wywołuj modelu.

Przygotuj i uruchom profil rzeczywistych osm_roads.parquet, overture_segments.parquet i zdjęć z photos.csv, a także ich połączeń. Wyniki zapisz do reports/map-qa/profile.md. Zapisz polecenia, wersje bibliotek, hashe wejść oraz liczniki wszystkich źródeł. Sprawdź CRS, typy i poprawność geometrii, duplikaty identyfikatorów i relacje kluczy. Zmierz kompletność highway, maxspeed i maxspeed:*, surface, lanes, oneway, lit, sidewalk*, junction, name i ref, z uwzględnieniem pełnego tags. W Overture sprawdź class, speed_limits, road_surface, sources i odcinki obowiązywania between. Nie sprowadzaj list reguł do pierwszego elementu.

Sprawdź liczbę i udział zdjęć z dopasowaniem, rozkład dystansów w metrach, zgodność kierunku, kandydatów alternatywnych, brak heading i raportowaną dokładność GPS. Porównaj relację źródłową OSM z dopasowaniem wyłącznie przestrzennym; nie nazywaj obu potwierdzonym utożsamieniem drogi. OSM way i Overture segment mają różną segmentację, więc nie porównuj samych liczników jako miary jakości.

Obejrzyj rozproszoną próbkę zdjęć: miasto, skrzyżowania, drogi lokalne, serwisowe, tereny zielone i drogi szybkiego ruchu, o ile są dostępne. Zapisz zaobserwowany przekrój scen i braki. Nie wywodź widocznego typu sceny wyłącznie z highway najbliższej drogi. Sprawdź licencję, autora, datę i hash każdego pliku. Opisz, czego ten profil nie dowodzi. Pokaż mi kilka przykładów połączeń w danych i zaczekaj przed implementacją pipeline'u.
~~~

**Twoja kontrola:** policz samodzielnie kilka wierszy przez DuckDB; sprawdź na obrazie jeden niepewny join. **Jeśli utkniesz:** zacznij od gotowych GeoParquet i części offline. **Rozszerzenie:** zapisz profil jako powtarzalne polecenie z testem niezmienności wejść.

**Opcjonalnie, Databricks:** osobiste konto Free Edition nie jest wymagane. Jeśli masz dostęp do przygotowanego workspace, skorzystaj z [instrukcji CLI, REST i MCP](../../exercise-data/map-qa/DATABRICKS.md) i wyślij agentowi dodatkowy prompt:

~~~text
Przeczytaj course-materials/exercise-data/map-qa/DATABRICKS.md. Sprawdź wersję dostępnego CLI i obecność zmiennych dostępowych bez wyświetlania wartości. Odczytaj tabele workspace.map_qa.osm_roads, overture_segments, photos, photo_road_links i traffic_signs przez databricks api lub query_databricks.py. Porównaj liczności i typy z lokalnym snapshotem oraz wykonaj trzy opisane kontrole ST_*. Zapisz wyniki i dokładne polecenia w reports/map-qa/profile.md. Nie zapisuj tokenów, nie zmieniaj danych i nie twórz schematów. Jeśli nie masz dostępu, jawnie opisz brak i pozostań przy plikach lokalnych.
~~~

## M3. AGENTS.md

**Cel:** sprawić, żeby świeża sesja przestrzegała zasad bez ponownego dyktowania. **Agent: Claude Code.**

**Prompt do skopiowania:**

~~~text
Przeczytaj istniejące AGENTS.md, CLAUDE.md, docs/PRD.md i course-materials/exercise-data/map-qa/README.md. Uzgodnij zasady dla tego pipeline'u w AGENTS.md, zachowując działające instrukcje repozytorium i zakaz samodzielnego czytania pozostałych materiałów. CLAUDE.md ma importować @AGENTS.md, bez drugiej kopii reguł. Nie zmieniaj kodu aplikacji ani danych.

Uwzględnij: surowe dane i dołączone snapshoty są tylko do odczytu; pobrania i wyniki trafiają do osobnych katalogów; Python 3.12 i uv; dystanse dopiero po transformacji obu warstw do EPSG:2180; nigdy nie wyświetlaj ani nie zapisuj OPENROUTER_API_KEY i nie czytaj plików z sekretami; zachowuj ODbL i licencję/atrybucję każdego obrazu; pytaj przed usunięciem rekordów, a wyłączenia opisuj przyczyną; oddziel fakty od założeń; płatne API tylko na małej jawnej próbce, z limitem żądań, bez automatycznych retry i z rejestrem kosztów. Dane syntetyczne nie stają się OSM, a none, unknown, abstain i model_unavailable nie są jednym stanem. Nowe funkcje implementuj dopiero po napisaniu testów.

Pokaż diff i wskaż kolizje z istniejącymi zasadami zamiast usuwać je po cichu. Daj mi krótkie zadanie do uruchomienia w świeżej sesji, które sprawdzi stosowanie zasad bez powtarzania ich w prompcie.
~~~

**Twoja kontrola:** otwórz świeżą sesję w tym samym katalogu i wklej:

~~~text
Na podstawie docs/PRD.md i raportu reports/map-qa/profile.md zaproponuj kolejny mały krok. Sprawdź, jakie wejścia są dostępne i gdzie zapiszesz wynik. Nie wdrażaj jeszcze kolejnego etapu.
~~~

Sprawdź, czy agent sam odczytał instrukcje, zachował dane i zaproponował metry w odpowiednim CRS, jeśli planuje dystanse. Samo powtórzenie zasad nie jest dowodem: obejrzyj komendy, ścieżki i diff.

**Jeśli utkniesz:** jeśli świeża sesja ignoruje plik, sprawdź katalog roboczy, zaufanie do repozytorium i zakres plików instrukcji. Nie doklejaj całego AGENTS.md do każdej rozmowy.

**Rozszerzenie:** na podstawie [przykładów hooków](../../hooks-example/) przygotuj Claude Code `PreToolUse`, który blokuje zapis do dołączonych danych. Dopasuj obsługę ścieżek i narzędzi do Windows; sprawdź blokadę na osobnej próbnej kopii i dozwolony zapis raportu. Deklaracja w AGENTS.md sama nie jest blokadą systemową.


## M4. ADR i pełny plan implementacji

**Cel:** wybrać architekturę i podzielić wdrożenie na sprawdzalne etapy. **Agent: Codex.**

**Prompt ADR do skopiowania:**

~~~text
Użyj zainstalowanego skilla write-adr. Przeczytaj AGENTS.md, docs/PRD.md i reports/map-qa/profile.md oraz schematy wskazanych wejść map-qa. Pracuj nad dokumentem architektury, nie kodem. Rozstrzygnij ze mną brakujące decyzje, a ADR zapisz po polsku w docs/ADR/, mimo domyślnego języka skilla.

Rozważ Python 3.12 i uv, pandas, GeoPandas/Shapely/pyproj, DuckDB spatial i pytest. Zapisz sprawdzone dokumentacje i wersje, używając Context7 albo źródeł oficjalnych. Wybierz dostęp do danych: lokalne GeoParquet jako ścieżkę dostępną od początku albo tabele Databricks przez zweryfikowane CLI/REST/MCP, jeśli rzeczywiście mamy je udostępnione. Konto osobiste i chmura pozostają opcjonalne. Nie deklaruj działającego połączenia bez próby.

Jeśli dashboard wszedł do PRD, porównaj Streamlit z PySide6 pod kątem uruchomienia na Windows, dystrybucji i przeglądu zdjęć oraz mapy. Jeśli nie wszedł, pozostaw go poza implementacją. Wybierz jeden transport Decisions: oficjalny SDK OpenRouter albo openai SDK jako klient HTTP kontraktu OpenRouter. Native OpenAI Decisions ma inny kontrakt; nie mieszaj ich. Bibliotek i metod nie wybieraj z pamięci.

Zapisz granice normalizacji atrybutów, CRS i metry, listę dopuszczalnych dróg i access, dopasowanie po odległości i lokalnym bearing, remisy, przeciwne jezdnie, mosty/tunele, różne daty i reguły kierunkowe/warunkowe. Połączenia dostarczone w danych to kandydaci wejściowi, które nasz pipeline ma sprawdzić, nie rozwiązanie ani prawda terenowa. Ustal reprezentację missing/unknown/uncertain/abstain/model_unavailable. Zdefiniuj, które reguły Overture da się porównać z tagami OSM i jak zachować pozostałe.

Oddziel moduł odczytu zdjęć od mapy i etykiet referencyjnych. Zaprojektuj wersjonowanie pytań, cache po hashu obrazu/modelu/pytań, próg abstencji, limit wszystkich prób HTTP i kosztu, timeout oraz zero automatycznych retry. Licencje i atrybucje muszą przejść do eksportów. Uwzględnij testy jednostkowe, integracyjne i rzeczywiste uruchomienie CLI, a dla wybranego UI także ręczny przepływ i zrzuty. Mock API wolno dodać dopiero z bezpiecznego rzeczywistego capture. Zakończ na ADR i pokaż dokument do przeglądu.
~~~

Po zatwierdzeniu ADR włącz plan mode, np. `/plan` w Codexie. Następny prompt jest wyłącznie do planowania:

~~~text
Przeczytaj AGENTS.md, uzgodniony docs/PRD.md, docs/ADR/, reports/map-qa/profile.md i aktualne pliki app/. Przygotuj pełny plan implementacji do docs/plan.md. Nie implementuj, nie uruchamiaj płatnego API i nie deleguj pracy podczas planowania. Jeśli czegoś brakuje do pierwszego etapu, zadaj konkretne pytanie i poczekaj na odpowiedź.

Zaproponuj kolejne małe etapy: kontrakty wejść i normalizacja, przeliczenie CRS i dopasowanie zdjęcia po dystansie oraz bearing, porównanie atrybutów OSM/Overture z ich segmentacją, kandydaci i raport, adapter modelu, mała ewaluacja oraz opcjonalny dashboard wyłącznie z PRD. Kontrole topologii umieść tylko w uzgodnionym zakresie. Wskaż zależności między etapami i jedną pierwszą czynność.

Dla każdego etapu podaj cel, wejścia, pliki do utworzenia/zmiany, właściciela, zależności, kryteria PRD, testy przed kodem, oczekiwaną przyczynę Red, minimalne Green i zakres Refactor. Warunek zakończenia ma opisywać obserwowalny wynik i zawierać testy, uruchomienie rzeczywistego CLI oraz ręczne sprawdzenie. Rozdziel sprawdzenie importów/kompilacji, uruchomienie testów z liczbą odkrytych/pominiętych i start aplikacji. Zaplanuj małą próbkę przed pełnym snapshotem, nie zakładaj przetwarzania wszystkich zdjęć przez API.

Dodaj macierz zadanie -> pliki -> zależności -> weryfikacja. Wskaż ryzyka danych, brakujące decyzje i miejsca wymagające dowodu z rzeczywistej odpowiedzi API. Zachowaj możliwość wznowienia po każdym etapie; commit po zweryfikowanym kroku, bez nadpisywania cudzych zmian. Jeśli proponujesz późniejszą delegację, uzasadnij ją i rozdziel pliki; samo planowanie niczego nie uruchamia.

Jeśli plan mode nie pozwala zapisać pliku, pokaż pełną treść planu i zaczekaj na akceptację. Po wyjściu z tego trybu zapisz zatwierdzony dokument. Zakończ przed kodowaniem.
~~~

**Twoja kontrola:** rozumiesz pierwszy etap i potrafisz rozpoznać jego zakończenie. **Jeśli utkniesz:** ogranicz etap do jednego kontraktu wejścia i jego testów. **Rozszerzenie:** zamień tę sesję planowania w skill do tworzenia planów. Użyj `skill-creator`, oddziel reguły ogólne od danych projektu, zapisz źródło skilla w repozytorium, a jego test wykonaj w nowej sesji na innym małym zadaniu. Instaluj dopiero uzgodnioną wersję.

## M5. Rzeczywisty pipeline, testy przed kodem

**Cel:** wdrażać po jednym etapie planu bez płatnego modelu. **Agent: Codex.**

**Prompt do skopiowania:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md i reports/map-qa/profile.md. Wykonaj wyłącznie pierwszy zatwierdzony etap planu w app/. Korzystaj z rzeczywistych plików course-materials/exercise-data/map-qa/: osm_roads.parquet, overture_segments.parquet, photos.csv i photo_road_links.csv. Małe wejścia syntetyczne wolno utworzyć do testów jednostkowych; nie zastępują rzeczywistego uruchomienia. Nie zmieniaj wejść i nie wywołuj modelu.

Najpierw napisz pytest wynikające z PRD i ADR. Uruchom je, pokaż odkrycie i Red z oczekiwanej przyczyny, dopiero potem implementuj minimum. Dla normalizacji sprawdź liczby i jednostki, brak tagu, PL:urban, none, wartości wielokrotne oraz kierunkowe i warunkowe, zachowując surowe dane. Dla Overture testuj wiele reguł speed_limits/road_surface i ich between oraz when; nie porównuj pierwszej reguły do całej drogi.

Dla etapu łączenia testuj EPSG:4326 -> EPSG:2180 obu warstw, znany dystans w metrach, dwa bliskie odcinki, lokalny bearing, zawijanie 359/1 stopni, odwróconą geometrię, oneway=-1, brak kierunku, brak drogi w promieniu, remis, service/access i różny poziom. Kierunek patrzenia aparatu nie musi być kierunkiem jazdy. Odróżnij dopasowanie przez referencję źródłową OSM od dopasowania przestrzennego Overture. Zweryfikuj wejściowe photo_road_links zamiast uznać je za wzorzec.

Porównanie map ma rozróżniać brak atrybutu, nieporównywalne reguły i rozbieżność. Wydanie Overture może zawierać starszy OSM. Raportuj kandydatów z identyfikatorami, datami, surowymi wartościami i powodem; nie wydawaj automatycznych werdyktów o błędzie mapy. W kontroli topologii, jeśli jest w tym etapie, użyj node_ids i nie traktuj granicy wycinka ani mostu jako dowodu braku skrzyżowania. Nie dodawaj kolejnych etapów bez przeglądu bieżącego.

Po Green uruchom cały zestaw testów zakresu, wykonaj Refactor przy zielonych testach i uruchom rzeczywisty CLI najpierw na małej próbce, potem na snapshotach. Zachowaj wynik w reports/map-qa/. Każdy rekord ma status; rozłączne liczniki przetworzeń i wyłączeń sumują się do wejścia. Pokaż osobno testy, start, ręczne sprawdzenie wybranych rekordów i hashe wejść przed/po. Zero kandydatów jest dopuszczalne. Zatrzymaj się do przeglądu pierwszego etapu.
~~~

**Twoja kontrola:** obejrzyj przypadek bliskich dróg i sprawdź ręcznie atrybuty obu źródeł. Test dystansu ma wykrywać użycie stopni zamiast metrów. **Jeśli utkniesz:** wróć do jednego testu i jednego rekordu. **Rozszerzenie:** dodaj kontrolowaną mutację obliczania bearing i pokaż, że test ją wykrywa, po czym ją cofnij.

## M6. Model decyzyjny na zdjęciach

**Cel:** zmierzyć odczyt obrazu i abstencję bez mieszania tego z jakością joinu. **Agent: Claude Code.**

Dokumentacja: [żądanie Decisions](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request), [obrazy w state](https://openrouter.ai/docs/guides/community/multimodal-decisions), [oficjalny SDK Python](https://openrouter.ai/docs/client-sdks/python/sdks/decisions/README). Dwie ścieżki poniżej wysyłają ten sam kontrakt OpenRouter. Natywne `client.decisions.create()` z OpenAI SDK ma inny kontrakt i nie jest zamiennikiem.

**Prompt do skopiowania:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md, dotychczasowy kod i course-materials/exercise-data/map-qa/README.md. Wykonaj tylko etap odczytu zdjęć i ewaluacji. Klucz OPENROUTER_API_KEY jest już w środowisku; sprawdź jedynie jego obecność, nigdy wartość. Nie czytaj .env ani plików sekretów. Bez klucza lub budżetu przygotuj lokalną walidację kontraktu i oznacz brak pomiaru, nie udawaj odpowiedzi API.

Dodaj wrapper zgodny z ADR: openai/gpt-6-luna-decisions przez https://openrouter.ai/api/alpha/decisions, zestaw kilku pytań z PRD: Choice rodziny klasy drogi (motorway/trunk, primary-secondary-tertiary, residential/living_street, service, track, unclassified/inne, unknown), Choice nawierzchni paved/unpaved/unknown, Noul widocznego skrzyżowania, znaku ograniczenia, chodnika i oświetlenia oraz Choice liczby pasów w kierunku patrzenia (1/2/3+/unknown). Dla znaku dodaj odczyt wartości z uzgodnioną listą liczb i osobnymi none/unknown; nie ograniczaj go bez sprawdzenia danych do 30/50/70/90. Oddziel unknown z oceny obrazu od źródłowej klasy unknown w Overture. Wybierz tylko pytania uzgodnione w PRD. Score czytelności pozostaje opcjonalny. Obraz wyślij jako base64 data URL w image_url w state obok zwykłego tekstu. Nie przekazuj labels, kategorii, nazwy pliku, atrybutów mapy, traffic_signs.geojson ani mapillary_detections.json.gz. none oznacza brak widocznego znaku liczbowego, unknown znak nieczytelny lub wartość spoza listy; błąd API ma osobny stan; dla trudnych przykładów zachowaj prawdopodobieństwa i abstencję. Obsłuż orientację i rozmiar obrazu zgodnie z wymaganiami obu modeli. Nie loguj base64, klucza ani nagłówka Authorization.

Poniższy przykład znaku pokazuje strukturę kontraktu i szeroki katalog liczb. Uzgodnij listę wartości z PRD i profilem źródeł przed pomiarem; nie przenoś etykiety konkretnego zdjęcia do pytania. Dostosuj pytania do zatwierdzonego zestawu; nie jest pełnym schematem ewaluacji. MIME ustal z rzeczywistych bajtów pliku: image/jpeg dla JPEG, image/png dla PNG. Referencja kontraktu OpenRouter: body ma model, state i questions jako obiekt pytań. Przykładowy kształt, który uzupełnisz zgodnie z wybraną biblioteką i aktualną dokumentacją:
{
  "model": "openai/gpt-6-luna-decisions",
  "state": ["Oceń wyłącznie widoczne cechy zdjęcia.", {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,BASE64_OBRAZU"}}],
  "questions": {
    "speed": {"type": "choice", "instructions": "Odczytaj najbardziej widoczny znak ograniczenia. Wybierz none, gdy nie ma widocznego znaku liczbowego. Wybierz unknown, gdy znak jest nieczytelny albo ma wartość spoza uzgodnionej listy; pomiń tablice informacyjne.", "criteria": {"5": "Czytelne 5 km/h", "10": "Czytelne 10 km/h", "15": "Czytelne 15 km/h", "20": "Czytelne 20 km/h", "25": "Czytelne 25 km/h", "30": "Czytelne 30 km/h", "40": "Czytelne 40 km/h", "50": "Czytelne 50 km/h", "60": "Czytelne 60 km/h", "70": "Czytelne 70 km/h", "80": "Czytelne 80 km/h", "90": "Czytelne 90 km/h", "100": "Czytelne 100 km/h", "110": "Czytelne 110 km/h", "120": "Czytelne 120 km/h", "130": "Czytelne 130 km/h", "140": "Czytelne 140 km/h", "none": "Brak widocznego znaku liczbowego", "unknown": "Znak nieczytelny lub wartość spoza listy"}},
    "sign_visible": {"type": "noul", "instructions": "Czy widoczny jest znak ograniczenia prędkości, także gdy cyfry są nieczytelne?"},
    "legibility": {"type": "score", "instructions": "Oceń czytelność cyfr najbardziej widocznego znaku ograniczenia prędkości.", "criteria": ["Brak znaku", "Znak widoczny, cyfry nieczytelne", "Cyfry czytelne"]}
  }
}

Ścieżka A, oficjalny openrouter SDK: from openrouter import OpenRouter; client.alpha.decisions.create(model=body["model"], state=body["state"], questions=body["questions"]). Ustaw jawnie timeout_ms=40000 i brak retry, np. RetryConfig("none", BackoffStrategy(100, 100, 1, 100), False) z openrouter.utils jako retry_config konstruktora. Zweryfikuj sygnatury dla przypiętej wersji; punktem odniesienia jest openrouter==1.3.107.
Ścieżka B, openai SDK jako transport HTTP: from openai import OpenAI; klient z api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1", max_retries=0 i timeout=40; wywołanie client.post("https://openrouter.ai/api/alpha/decisions", body=body, cast_to=dict). Punktem odniesienia jest openai==3.42.1. Nie przekazuj tego body do client.decisions.create(). To dwie alternatywy, wdrażaj wybraną w ADR.
Odpowiedź OpenRouter ma answers jako obiekt: answers.speed.probabilities jest mapą klasa -> prawdopodobieństwo, Noul zwraca noul, Score zwraca score. Zweryfikuj pełne pola rzeczywistej odpowiedzi, nie zgaduj nazw usage. Rozkład Choice nie jest generowanym uzasadnieniem. Score 0-2 nie jest prawdopodobieństwem.

Zacznij od testów lokalnej walidacji, limitu, cache i reguł abstencji bez fikcyjnego mocka odpowiedzi API. Zanim zrobisz mock endpointu, wykonaj jeden rzeczywisty request na publicznym lub syntetycznym obrazie w przyznanym limicie. Zachowaj status, bezpieczne nagłówki bez sekretów, treść odpowiedzi, datę, endpoint i wersję SDK. Dopiero z tego capture utwórz fixture testową. Pierwsza próba jest częścią limitu, nie dodatkiem. Limit obejmuje wszystkie próby HTTP, także nieudane: najwyżej 25 Luna i 5 Jev, łącznie najwyżej 30, albo mniej według przydziału grupy. Wyłącz retry również wewnątrz SDK; błąd lub timeout to model_unavailable i jawny wpis, bez automatycznej ponownej opłaty. Kod stosuje ustalone progi Choice/Noul/Score, nie model. Nieznana prędkość drogi pozostaje osobnym stanem.

Najpierw pokaż manifest próby i maksymalną liczbę żądań. Uruchom najwyżej 25 unikalnych obrazów na Luna i te same 5 na typesafe/jev-1.14, sekwencyjnie i tylko w przyznanej części wspólnego limitu. Wybierz po jednym czytelnym przykładzie każdej dostępnej klasy, a brak klasy zgłoś. Dobierz wspólną piątkę tak, aby każde mierzone pytanie miało przykład z dostępną pewną etykietą; sprawdź to przed pierwszym żądaniem. Jeśli próg kosztu nie został uzgodniony, zapytaj przed płatnym uruchomieniem. Nie zmieniaj zdjęć ani pytań między porównywanymi modelami. Zapisuj model zwrócony przez API, wersję pytań, hash obrazu, latencję, input/output tokens i koszt raportowany przez API; rozróżnij koszt OpenRouter i ewentualny koszt upstream BYOK oraz brak wartości. Nie dodawaj pełnej kolekcji zdjęć do Git; cache i capture trzymaj w ignorowanym course-materials/exercise-data/map-qa/data/ bez sekretów.

Zbuduj tabelę accuracy przed abstencją, accuracy na przyjętych odpowiedziach, coverage, liczby abstencji i błędów API, tokenów, kosztu i latencji dla każdego modelu. Pokaż mianowniki i wyłączenia uncertain, nie traktuj pustej etykiety jako none. Oceń każde dostępne pytanie oddzielnie względem etykiet referencyjnych do pomiaru jakości w reference_labels.csv. To etykiety widocznych cech, bez werdyktów o mapie. Odczytaj instrukcję etykiet i metodę. Rekordy uncertain wyłącz z metryki danego pytania z jawnym mianownikiem; nie usuwaj przez to innych pewnych etykiet obrazu. Pokaż mi niezgodności i próbkę zgodności do ręcznego przeglądu. Podziel próbkę według sequence, aby sąsiednie klatki nie trafiały jednocześnie do doboru progów i końcowego testu. Brak pozytywnych przykładów zgłoś zamiast deklarować jakość danej klasy. Progi ustalamy przed końcowym pomiarem, nie dopasowujemy ich do wyniku testu. Pięć obrazów nie uzasadnia wniosku o kalibracji ani przewadze modelu. Uruchom testy i rzeczywisty CLI, zapisz komendy i wyniki. Nie edytuj OSM i nie generuj jeszcze UI.
~~~

**Wynik i Twoja kontrola:** obejrzyj jedno zdjęcie, jego pełny rozkład i decyzję kodu. Sprawdź, że suma prób obejmuje także pierwsze wywołanie, a ponowne uruchomienie używa cache. Porównaj oba modele na tej samej piątce zdjęć, bez dopisywania metryk w razie braku dostępu. Rysunki testują mechanikę; rzeczywiste fotografie służą do pomiaru cech wizualnych. Nie mieszaj ich w jedną accuracy i nie używaj atrybutu mapy jako etykiety zdjęcia.

**Jeśli utkniesz:** przy HTTP 401/402/429 lub timeoutcie zatrzymaj płatną pętlę, zachowaj bezpieczny kod błędu i kontynuuj raport na zapisanych odpowiedziach lub etykietach z wyraźnym opisem źródła. Nie zmieniaj modelu na wariant czatowy i nie powtarzaj żądań automatycznie.

**Rozszerzenie:** narysuj tabelę progów na zapisanych rozkładach, bez nowych wywołań. Wyjaśnij różnicę między confidence modelu, selective accuracy i coverage.


## M7. Raport i podział pracy

**Cel:** przedstawić dowody analitykowi i porównać dwa niezależne review. **Agent prowadzący: Codex; recenzenci: subagent Claude Code i Codex.**

**Prompt do skopiowania, Codex:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md oraz dotychczasowe wyniki reports/map-qa/. Po testach przygotuj generator raportu Markdown i statycznego HTML z zapisanych wyników, bez nowych wywołań API. Raport ma zawierać tabelę kandydatów do przeglądu, źródłowe i znormalizowane atrybuty OSM oraz Overture, odczyty cech zdjęcia, rozkład prawdopodobieństw, decyzję kodu, dystans i CRS, miniatury ze źródłem/autorem/licencją oraz liczniki wyłączeń. Oddziel OSM od Overture i obserwacji fotograficznych, testy syntetyczne od danych terenowych, etykiety od predykcji, abstencję od niedostępnego modelu. Zero kandydatów jest dopuszczalnym wynikiem. Podaj ograniczenia: pozycja kamery, service road, kierunek, czas i warunkowe ograniczenia oraz niepewne etykiety i odmienne daty źródeł.

Raport otwiera się lokalnie bez serwera, z poprawnymi względnymi ścieżkami do miniatur. Escape HTML z tagów/nazw/autorów, nie wstawiaj niezaufanego tekstu jako kodu. Nie osadzaj klucza ani payloadów base64. Sprawdź testy generatora i rzeczywiste uruchomienie CLI. Podaj komendę oraz ścieżki raportów, otwórz HTML i sprawdź obrazy, linki, polskie znaki, liczby i atrybucje. Pokaż diff. Nie wykonuj automatycznych edycji mapy i zatrzymaj się przed kolejnym etapem.
~~~

**Twoja kontrola:** otwórz HTML w przeglądarce i ręcznie sprawdź jeden wiersz od zdjęcia przez drogę do wyniku. Porównaj liczniki Markdown z HTML i danymi. Zapisz zrzut raportu oraz komendę generowania.

Teraz zatrzymaj pisanie w repozytorium i uruchom dwa review tego samego niezmienianego diffu. W Claude Code zleć subagentowi:

~~~text
Zleć jednemu subagentowi review obecnego diffu pipeline'u map QA. Przekaż mu docs/PRD.md, docs/ADR/, docs/plan.md, zmienione pliki i ścieżki wyników. Ma wyłącznie czytać, bez edycji i bez płatnego API. Sprawdza CRS i dystanse, normalizację, wyłączenia i ich liczniki, brak przecieku etykiet do modelu, kontrakt Decisions, retry, cache/budżet, progi i abstencję, atrybucję oraz escape HTML. Każdy problem zgłasza jako plik i linia, skutek, dowód oraz sposób sprawdzenia. Odróżnia błąd od sugestii. Zwróć wyniki i zużycie tokenów, jeśli narzędzie je udostępnia; brak metryki oznacz jako nieudostępnioną, nie szacuj jej z długości tekstu.
~~~

W Codexie użyj `/review` i wybierz niezatwierdzone zmiany z tego samego diffu. Jeśli całość jest już zatwierdzona, porównaj z uzgodnionym commitem sprzed M5. Alternatywa headless w PowerShell:

```powershell
codex exec 'Zrób wyłącznie review niezatwierdzonego diffu pipeline map QA względem docs/PRD.md, docs/ADR/ i docs/plan.md. Nie zmieniaj plików i nie wywołuj API. Sprawdź CRS, maxspeed, liczniki, przeciek etykiet, kontrakt Decisions, retry, cache, abstencję, licencje i escape HTML. Zgłoś plik, linię, skutek i dowód każdego błędu.'
```

Przed każdym review zapisz `git diff` i identyfikator bazowego commita; jeśli w międzyczasie zrobiłeś commit, użyj tego samego zakresu commitów w obu review. Wspólny katalog nie służy do równoległego edytowania tych samych plików. Sprawdź `/context` w Claude Code i `/status` w Codexie; porównuj zużycie tokenów tylko wtedy, gdy oba pomiary wykonano tą samą metodą; brakujące metryki oznacz jako brak pomiaru. [Codex: review i komendy](https://developers.openai.com/codex/cli/slash-commands).

**Wynik:** raport i tabela porównania uwag: błąd, agent, dowód, Twoja decyzja, poprawka, ponowne sprawdzenie. Wybierz jedną potwierdzoną uwagę, dodaj test wykrywający problem i dopiero potem popraw kod. Przeczytaj diff i wykonaj sprawdzenie CLI ponownie.

**Jeśli utkniesz:** jeśli agent recenzuje tylko opisy, wskaż konkretny zakres Git i pliki. Nie uznawaj ogólnej pochwały ani kodu wyjścia za dowód jakości. Jeśli nie ma subagentów w danym koncie, zrób niezależny przegląd w nowej sesji Claude Code i oznacz różnicę wykonania.

**Rozszerzenie:** opisz powtarzalne generowanie raportu jako projektowy skill, z wejściami, komendą, limitami, kontrolą licencji i sprawdzeniem w świeżej sesji. Nie dopisuj całej logiki generatora do instrukcji skilla.


## Co dalej

- Dodaj dashboard dopiero po uzgodnieniu PRD i ADR.
- Przekaż potwierdzone ustalenia do osobnej kolejki przeglądu.
- Uruchom jedno ograniczone zadanie headless z logiem i sprawdzeniem wyniku.
