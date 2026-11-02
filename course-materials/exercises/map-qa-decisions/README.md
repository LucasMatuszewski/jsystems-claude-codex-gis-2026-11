# Kontrola atrybutów mapy ze zdjęć: Luna Decisions + pipeline

Zbudujesz powtarzalny proces, który znajduje kandydatów na konflikt między zdjęciem znaku a atrybutem drogi. Nauczysz się prowadzić agentów od PRD i rozpoznania danych przez zasady repozytorium, ADR, plan i TDD do pomiaru modelu oraz wzajemnego review.

Aplikacja pomaga analitykowi map QA porównać odczyt znaku ze zdjęcia z atrybutem przypisanego odcinka drogi. Model decyzyjny odpowiada na zamknięte pytania o zdjęcie i zwraca prawdopodobieństwa. Kod odpowiada za łączenie danych, progi, abstencję i raport Markdown + HTML, a człowiek ocenia kandydatów na konflikt.

Dlaczego mierzymy zamiast ufać odpowiedzi? [RoadBench](https://arxiv.org/html/2511.18011v1) pokazuje ograniczenia modeli w liczeniu pasów i rozpoznawaniu typu drogi. [Ewaluacja Braintrust](https://www.braintrust.dev/evals/decision-models-aerial-image-classification) porównuje modele decyzyjne na 2000 obrazów lotniczych: zamknięte klasy pozwalają tanio mierzyć jakość, lecz część klas pozostaje trudna. To inne zadanie niż odczyt znaków; jakości i kalibracji prawdopodobieństw na naszych zdjęciach nie znamy przed pomiarem. [Decisions OpenRouter](https://openrouter.ai/docs/guides/community/multimodal-decisions) zwraca typowane wyniki, a nie uzasadnienie generowane w czacie.

## Punkt startowy

Pracuj w PowerShell na przygotowanej maszynie Windows, w `D:\jsystems-claude-codex-gis-2026-11`. Potrzebujesz Git, uv, Pythona 3.12, Claude Code i Codex CLI. Docker ani WSL nie są potrzebne. Repozytorium zawiera dane i downloadery; kod pipeline'u, testy i dokumenty aplikacji tworzysz samodzielnie w kolejnych etapach.

```powershell
Set-Location D:\jsystems-claude-codex-gis-2026-11
```

```powershell
git status --short
```

Nie nadpisuj wcześniejszej pracy. Jeśli masz już `docs/PRD.md`, M1 ma uzgodnić zmianę zakresu i zapisać korektę, a nie zastąpić dokument bez porównania. Przed przełączeniem agentów zakończ bieżące narzędzia i zapisz zmiany. Jeden agent pisze w danym pliku w danej chwili.

Wejścia są opisane w [README danych](../../exercise-data/map-qa/README.md): `synthetic/` do sprawdzania pipeline'u offline, `osm/` jako rzeczywisty snapshot oraz `labels_reviewed.csv` do pobrania Commons. To dwa różne zadania: ocena odczytu fotografii i kontrola połączenia z drogą. Nie zakładaj, że Commons pasuje geograficznie do Łodzi lub że próbka rzeczywista zawiera błąd mapy.

**Koszt pod kontrolą:** klucz `OPENROUTER_API_KEY` jest już zmienną środowiskową na VM, wspólną dla grupy i z ograniczonym budżetem. Nie wyświetlaj go, nie wklejaj do agenta, nie zapisuj do plików. M1-M5 działają bez płatnego API. W M6 jedna osoba wykonuje najwyżej 25 odczytów Luna i porównanie na tych samych 5 obrazach z Jev; cała grupa nie uruchamia naraz pełnych prób. Zacznij od jednego zdjęcia, sprawdź zapis tokenów i kosztu, potem kontynuuj w uzgodnionej części wspólnego limitu. Timeout może oznaczać naliczone wywołanie: wyłącz automatyczne retry, także w SDK. Brak kosztu w odpowiedzi to brak danych, nie zero.

**Agenci:** M1 Claude Code, M2 Codex, M3 Claude Code, M4 Codex, M5 Codex, M6 Claude Code, M7 Codex i Claude Code. Zmieniamy prowadzącego między etapami; M4-M5 pozostają w Codexie, żeby przejść od planu do pierwszego wdrożenia. Przed każdym promptem sprawdź katalog i dostępne pliki. W promptach ścieżki są względem katalogu głównego repozytorium.

## M1. PRD ze skillem

**Cel:** opisać wynik pracy analityka i sprawdzalne wymagania przed wyborem implementacji. **Agent: Claude Code.**

W Claude Code sprawdź `/skills`; jeśli ta wersja nie ma tej komendy, wpisz `/`, aby zobaczyć dostępne komendy i skille. Obejrzyj instrukcję `write-prd`; wywołaj `/write-prd` lub poproś o użycie skilla po nazwie. W Codexie odpowiednikiem jest `/skills` lub wybór po wpisaniu `$`, np. `$write-prd`. Skille instalowane w projekcie trafiają do `.agents/skills`; zwykły klon Git ich nie zawiera. Jeśli `write-prd` nie ma na liście, uruchom w katalogu repozytorium poniższe polecenie i otwórz agenta ponownie. Nie pozwalaj agentowi wymyślać treści skilla.

```powershell
npx --yes skills@latest add EdukeyTeam/agent-toolbox --skill '*'
```

**Prompt do skopiowania:**

~~~text
Użyj zainstalowanego skilla write-prd do utworzenia lub uzgodnionej aktualizacji docs/PRD.md po polsku. Przeczytaj AGENTS.md, README.md i course-materials/exercise-data/map-qa/README.md. Wolno Ci przeczytać dane i instrukcję tego ćwiczenia; nie przeszukuj pozostałej biblioteki kursowej. Jeśli PRD już istnieje, pokaż różnicę zakresu i zachowaj uzgodnione wymagania oraz rejestr korekt. Nie pisz jeszcze kodu ani ADR.

Brief produktu: użytkownik to analityk map QA, który chce dostać kolejkę kandydatów na konflikt znaku z mapą wraz z dowodem do ręcznej oceny. Wejście to odcinki dróg OSM z atrybutami, zdjęcia znaków z opcjonalnymi współrzędnymi oraz etykiety do pomiaru jakości. Osobny zestaw syntetyczny pozwala sprawdzić pipeline bez API. Wyjście to lista kandydatów, odczyty i prawdopodobieństwa, jawne przyczyny wyłączeń oraz raport Markdown i HTML z miniaturami, źródłami i licencjami. Model czyta wyłącznie zdjęcie, a kod kontroluje przypisanie drogi, progi i abstencję. Konflikt to kandydat do przeglądu, nigdy automatyczna poprawka mapy. Braki danych, nieczytelny znak i niedostępny model muszą być rozróżnialne. Poza zakresem: aplikacja UI, dane firmowe, automatyczne edycje OSM oraz wnioskowanie o znaku na podstawie znanej prędkości drogi. Nie obiecuj konfliktów w próbce rzeczywistej.

Zadaj wymagane przez skill pytania o nierozstrzygnięte wymagania, bez ponownego pytania o podane fakty. Poczekaj na moje odpowiedzi. Zapisz mierzalne kryteria akceptacji, w tym obsługę braków współrzędnych, nieznanej prędkości i brak sieci. Wskaż dwa wymagania, które mam przeczytać i samodzielnie zmienić. Nie wybieraj za mnie wartości progów i zakresu dopuszczalnych dróg. Po mojej korekcie zaktualizuj PRD i rejestr korekt z datą, identyfikatorem, poprzednim ustaleniem, zmianą i powodem. Zakończ na dokumencie.
~~~

**Wynik i Twoja kontrola:** otwórz `docs/PRD.md`, zmień dwa wymagania i poproś o ich zapisanie. Sprawdź, czy da się niezależnie ocenić spełnienie każdego z nich. Potwierdź poprawność dokumentu przed kodowaniem.

**Jeśli utkniesz:** gdy agent zaczyna implementować, przerwij i poproś wyłącznie o wymagania oraz pytania ze skilla. Nie akceptuj wygenerowanej aplikacji zamiast PRD.

**Rozszerzenie:** dopisz osobny scenariusz analityka, który otrzymuje zero kandydatów, ale nadal musi wiedzieć, ile rekordów wyłączono i dlaczego.

## M2. Dane i rozpoznanie

**Cel:** zweryfikować fakty o wejściach, zanim agent zaproponuje reguły. **Agent: Codex.**

Skorzystaj z poleceń z [README danych](../../exercise-data/map-qa/README.md), jeśli chcesz pobrać Commons. Bez sieci nadal masz rysunki, etykiety i snapshot. Używaj osobnego katalogu pobrań, nie nadpisuj plików dołączonych do repozytorium.

**Prompt do skopiowania:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md i course-materials/exercise-data/map-qa/README.md. W tym zadaniu wolno Ci czytać course-materials/exercise-data/map-qa/ i ten opis ćwiczenia, bez przeszukiwania reszty materiałów. Nie zmieniaj wejść. Sprawdź --help obu downloaderów i obecność zależności, zanim zaproponujesz polecenia. Jeśli jest sieć, pobierz przypięte Commons według README, z weryfikacją SHA-256. Brak sieci nie blokuje analizy syntetycznych danych i snapshotu OSM.

Utwórz app/profile_map_qa.py i zapisz raport faktów do reports/map-qa/profile.md. Użyj uv i Pythona 3.12, dopasowując się do istniejącej konfiguracji projektu zamiast inicjalizować ją ponownie. Raport ma wskazywać: źródło i CRS każdej warstwy, liczbę dróg według highway, liczbę i udział wyłącznie numerycznego maxspeed, puste i nietypowe wartości, obecność tagów kierunkowych i warunkowych, obrazy według observed_speed i label_status, brakujące/błędne współrzędne, licencje i dostępność plików. Oddziel ustalone fakty od wniosków i założeń. Nie interpretuj PL:urban jako zweryfikowanego odczytu ze zdjęcia. Nie drukuj żadnych zmiennych środowiskowych.

Dla każdej liczby podaj plik, pole i sposób obliczenia. Zaproponuj dwie krótkie kwerendy DuckDB do niezależnego sprawdzenia. Uruchom skrypt na dołączonych wejściach, pokaż dokładną komendę i wynik, sprawdź, że ich hashe nie zmieniły się. Nie twórz jeszcze detektora konfliktów ani wrappera modelu.
~~~

**Twoja kontrola:** z katalogu głównego uruchom te dwie niezależne kwerendy PowerShell. Pierwsza porównuje liczby według klasy drogi; druga sprawdza licznik liczbowego `maxspeed`. Wzorzec `uv run --with duckdb` zapewnia zależność bez globalnej instalacji. Pierwsze `INSTALL spatial` wymaga sieci albo obecnego już cache rozszerzenia.

```powershell
uv run --python 3.12 --with duckdb==1.5.6 python -c "import duckdb; c=duckdb.connect(); c.execute('INSTALL spatial; LOAD spatial'); p='course-materials/exercise-data/map-qa/osm/osm_roads.geojson'; print(c.execute('SELECT highway, count(*) AS n FROM ST_Read(?) GROUP BY highway ORDER BY n DESC, highway', [p]).fetchall())"
```

```powershell
uv run --python 3.12 --with duckdb==1.5.6 python -c "import duckdb; c=duckdb.connect(); c.execute('INSTALL spatial; LOAD spatial'); p='course-materials/exercise-data/map-qa/osm/osm_roads.geojson'; print(c.execute('SELECT count(*) AS all_roads, count(*) FILTER (WHERE regexp_full_match(coalesce(maxspeed, ?), ?)) AS numeric_maxspeed FROM ST_Read(?)', ['', '[0-9]+', p]).fetchall())"
```

W Claude Code porównaj `/context` przed i po dołączeniu dużego pliku. `/compact` kompresuje rozmowę; wcześniej zapisz ustalenia w PRD i planie. Przy pustym polu wpisywania `Esc Esc` lub `/rewind` pozwala wrócić do wcześniejszego punktu, ale nie zastępuje Git i nie cofa wszystkich efektów poleceń zewnętrznych. `/resume` wraca do sesji. W Codexie użyj `/status` do sprawdzenia sesji, kontekstu i limitów oraz `/resume` do wznowienia. [Claude Code: tryb interaktywny](https://code.claude.com/docs/en/interactive-mode), [Codex: komendy](https://developers.openai.com/codex/cli/slash-commands).

**Wynik:** profil danych i dwie liczby samodzielnie potwierdzone kwerendami. Nie dopisuj do raportu spodziewanego wyniku bez uruchomienia.

**Jeśli utkniesz:** przy błędzie rozszerzenia sprawdź dostęp do serwera rozszerzeń, nie zmieniaj zapytania na zmyślony wynik. Profil możesz wykonać GeoPandas, a kontrolę DuckDB oznaczyć jako zablokowaną do czasu naprawy dostępu. Przy niedostępnym Commons przejdź dalej na danych dołączonych do repozytorium.

**Rozszerzenie:** porównaj profil snapshotu z osobno pobranym odświeżeniem i opisz, czy różnica oznacza zmianę danych, czy błąd kodu.

## M3. AGENTS.md

**Cel:** sprawić, żeby świeża sesja przestrzegała zasad bez ponownego dyktowania. **Agent: Claude Code.**

**Prompt do skopiowania:**

~~~text
Przeczytaj istniejące AGENTS.md, CLAUDE.md, docs/PRD.md i course-materials/exercise-data/map-qa/README.md. Uzgodnij zasady dla tego pipeline'u w AGENTS.md, zachowując działające instrukcje repozytorium i zakaz samodzielnego czytania pozostałych materiałów. CLAUDE.md ma importować @AGENTS.md, bez drugiej kopii reguł. Nie zmieniaj kodu aplikacji ani danych.

Uwzględnij: surowe dane i dołączone snapshoty są tylko do odczytu; pobrania i wyniki trafiają do osobnych katalogów; Python 3.12 i uv; dystanse dopiero po transformacji obu warstw do EPSG:2180; nigdy nie wyświetlaj ani nie zapisuj OPENROUTER_API_KEY i nie czytaj plików z sekretami; zachowuj ODbL i licencję/atrybucję każdego obrazu; pytaj przed usunięciem rekordów, a wyłączenia opisuj przyczyną; oddziel fakty od założeń; płatne API tylko na małej jawnej próbce, z limitem żądań, bez automatycznych retry i z rejestrem kosztów. Dane syntetyczne nie stają się OSM, a none, unknown, abstain i model_unavailable nie są jednym stanem. Nowe funkcje powstają metodą testy najpierw.

Pokaż diff i wskaż kolizje z istniejącymi zasadami zamiast usuwać je po cichu. Daj mi krótkie zadanie do uruchomienia w świeżej sesji, które sprawdzi stosowanie zasad bez powtarzania ich w prompcie.
~~~

**Twoja kontrola:** otwórz świeżą sesję w tym samym katalogu i wklej:

~~~text
Na podstawie docs/PRD.md i raportu reports/map-qa/profile.md zaproponuj kolejny mały krok. Sprawdź, jakie wejścia są dostępne i gdzie zapiszesz wynik. Nie wdrażaj jeszcze kolejnego etapu.
~~~

Sprawdź, czy agent sam odczytał instrukcje, zachował dane i zaproponował metry w odpowiednim CRS, jeśli planuje dystanse. Samo powtórzenie zasad nie jest dowodem: obejrzyj komendy, ścieżki i diff.

**Jeśli utkniesz:** jeśli świeża sesja ignoruje plik, sprawdź katalog roboczy, zaufanie do repozytorium i zakres plików instrukcji. Nie doklejaj całego AGENTS.md do każdej rozmowy.

**Rozszerzenie:** na podstawie [przykładów hooków](../../hooks-example/) przygotuj Claude Code `PreToolUse`, który blokuje zapis do dołączonych danych. Dopasuj obsługę ścieżek i narzędzi do Windows; sprawdź blokadę na osobnej próbnej kopii i dozwolony zapis raportu. Deklaracja w AGENTS.md sama nie jest blokadą systemową.

## M4. ADR i plan

**Cel:** rozstrzygnąć wybór narzędzi i kontrakty przed implementacją. **Agent: Codex.**

Wywołaj `$write-adr`. Poproś o polski dokument; instrukcja języka w prompcie ma pierwszeństwo przed domyślnym językiem skilla.

**Prompt do skopiowania:**

~~~text
$write-adr
Na podstawie docs/PRD.md, AGENTS.md, reports/map-qa/profile.md i course-materials/exercise-data/map-qa/README.md użyj skilla write-adr, aby zapisać ADR po polsku w docs/ADR/. Przeczytaj istniejące ADR przed dodaniem kolejnego numeru. Nie pisz kodu. Zapytaj mnie tylko o decyzje, które pozostają nierozstrzygnięte i zmieniają architekturę.

Rozważ i porównaj: Python 3.12 + uv; DuckDB spatial kontra GeoPandas dla filtrowania i przestrzennego nearest join; oficjalny pakiet openrouter z client.alpha.decisions.create kontra openai SDK z własnym POST do https://openrouter.ai/api/alpha/decisions. Modele to openai/gpt-6-luna-decisions i typesafe/jev-1.14. To endpoint typowanych Choice/Noul/Score, nie chat completion ani natywny kontrakt OpenAI Decisions. Obraz jest base64 image_url w state. Raport to Markdown + statyczny HTML, bez serwera i aplikacji UI. Zweryfikuj bieżącą dokumentację przez Context7, a brakujące szczegóły w źródłach oficjalnych. Zapisz wybrane wersje, linki i zweryfikowane identyfikatory dokumentacji, bez wymyślania API.

Ustal kontrakty: surowa i znormalizowana prędkość, przyczyny wyłączeń, lista dopuszczalnych highway i kontrola access, CRS i jednostki, dystans N metrów, remisy i wiele dróg, kierunek i warunkowe ograniczenia, brak współrzędnych, stany unknown/none/abstain/model_unavailable. Oddziel ocenę zdjęcia od dołączenia mapy. Uzgodnij ze mną progi prawdopodobieństwa, obecności i czytelności; zapisz, że są hipotezą do sprawdzenia, a nie gwarancją jakości. Model nie otrzymuje maxspeed, etykiety ani podpowiedzi z nazwy pliku.

Uwzględnij brak automatycznych retry płatnego API, timeout, cache zależny od hasha obrazu/modelu/pytań, limit wywołań i kosztów, bezpieczne błędy bez nagłówków uwierzytelniających, oraz zachowanie licencji w raporcie. Zapisz plan testów jednostkowych, integracyjnych i rzeczywistego uruchomienia CLI. Mock płatnego API wolno utworzyć dopiero z bezpiecznego rzeczywistego przechwycenia odpowiedzi bez sekretów. Diagram pokaże, gdzie kończy się model, a zaczyna deterministyczny kod i człowiek. Zakończ na ADR i poproś o jego przegląd.
~~~

Po obejrzeniu ADR włącz plan mode: w Codexie `/plan`, w Claude Code `Shift+Tab` do trybu planowania. Następny prompt jest do planowania, nie do wdrożenia:

~~~text
Przeczytaj docs/PRD.md, uzgodnione docs/ADR/ i AGENTS.md. Przygotuj etapowy plan implementacji do docs/plan.md: najpierw profil i testy normalizacji/CRS/łączenia na syntetycznych wejściach, potem snapshot, wrapper modelu, mała ewaluacja i raport. Dla etapu podaj pliki, zależności, test, warunek zakończenia i rzeczywiste sprawdzenie CLI. Rozdziel Red, Green i Refactor. Nie uruchamiaj API ani implementacji. Jeśli tryb planowania blokuje zapis, pokaż treść planu, poczekaj na moją akceptację i dopiero po wyjściu z tego trybu zapisz uzgodniony docs/plan.md. Zatrzymaj się przed kodowaniem.
~~~

**Wynik i Twoja kontrola:** sprawdź, czy ADR wybiera jedną spójną ścieżkę SDK, a plan ma obserwowalne warunki zakończenia. Zatwierdź dokumenty przed M5.

**Jeśli utkniesz:** nie akceptuj metody wymyślonej przez agenta. Otwórz podlinkowaną dokumentację i sprawdź sygnaturę. W razie braku dostępu zapisz nierozstrzygnięty kontrakt i zatrzymaj zależny etap.

**Rozszerzenie:** opisz koszt utrzymania dwóch adapterów SDK i warunek, pod którym drugi adapter rzeczywiście będzie potrzebny.

## M5. Etap 1 z testami, TDD

**Cel:** otrzymać sprawdzalny pipeline bez zależności od płatnego modelu. **Agent: Codex.**

**Prompt do skopiowania:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, uzgodnione docs/ADR/, docs/plan.md i reports/map-qa/profile.md. Wykonaj tylko pierwszy etap deterministycznego pipeline'u w app/. Użyj syntetycznych wejść course-materials/exercise-data/map-qa/synthetic/labels.csv i synthetic_roads.geojson; potem sprawdź course-materials/exercise-data/map-qa/osm/osm_roads.geojson. Nie wywołuj modelu, nie zmieniaj danych wejściowych. Korzystaj z uzgodnionej konfiguracji uv i poleceń projektu.

Najpierw zapisz testy pytest wynikające z wymagań i ADR. Pokaż ich odkrycie i niepowodzenie z oczekiwanej przyczyny, dopiero potem dodaj minimalny kod. Testuj: normalizację wyłącznie obsługiwanych formatów maxspeed z zachowaniem oryginału; puste, PL:urban, warunkowe i kierunkowe wartości bez zgadywania; filtrowanie drivable ways zgodnie z ustaloną listą highway/access; poprawną transformację obu warstw EPSG:4326 -> EPSG:2180 przed nearest join w N metrach; znany kontrolny dystans, brak dopasowania i remisy; brak współrzędnych; unknown pozostaje unknown zamiast stawać się zerem lub none. Każdy rekord ma końcowy status, a liczniki rozłącznych przyczyn wyłączeń i przyjęć sumują się do wejścia. Nie redukuj każdego braku do konfliktu.

Po Green uruchom cały zestaw testów zmienionego zakresu i wykonaj Refactor tylko przy zielonych testach. Uruchom rzeczywisty CLI na syntetycznych danych, zapisując kandydatów i liczniki do reports/map-qa/, a następnie na snapshocie. Dane Commons bez pasujących współrzędnych nie mają być na siłę przypisane do Łodzi. Jeśli brakuje rzeczywistego odczytu znaku, raportuj brak obserwacji zamiast fabrykować konflikt. W raporcie rozróżnij obliczenia na etykietach od odczytów modelu. Pokaż osobno testy, uruchomienie i ręczne sprawdzenie CLI, komendy, liczniki i hash wejść przed/po. Nie podawaj oczekiwanej liczby konfliktów bez jej obliczenia. Nie wdrażaj jeszcze kolejnego etapu.
~~~

**Twoja kontrola:** otwórz kilka PNG, odszukaj ich wiersze w `labels.csv` i odpowiadające odcinki syntetyczne. Sam porównaj liczbę ze znaku i `maxspeed`, potem z listą kandydatów. Sprawdź także przykład zgodny i brak znaku. Obejrzyj test dystansu: musi wykrywać użycie stopni zamiast metrów.

**Wynik:** uruchamialny CLI i testy z widocznym Red -> Green; żaden płatny request. Polecenie uruchomienia CLI pochodzi z implementacji, nie jest z góry udawaną komendą startera.

**Jeśli utkniesz:** poproś o pojedynczy nieprzechodzący test i minimalny przypadek wejściowy. Nie pozwalaj zmieniać asercji, dopóki agent nie porówna ich z PRD i danymi.

**Rozszerzenie:** dodaj test pokazujący dwie bliskie jezdnie i wyjaśnij, dlaczego odległość sama nie wystarcza do przypisania znaku.

## M6. Model decyzyjny na zdjęciach

**Cel:** zmierzyć odczyt obrazu i abstencję bez mieszania tego z jakością joinu. **Agent: Claude Code.**

Dokumentacja: [typowane żądanie](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request), [obrazy w state](https://openrouter.ai/docs/guides/community/multimodal-decisions), [oficjalny SDK Python](https://openrouter.ai/docs/client-sdks/python/sdks/decisions/README). Dwie ścieżki poniżej wysyłają ten sam kontrakt OpenRouter. Natywne `client.decisions.create()` z OpenAI SDK ma inny kontrakt i nie jest zamiennikiem.

**Prompt do skopiowania:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md, dotychczasowy kod i course-materials/exercise-data/map-qa/README.md. Wykonaj tylko etap odczytu zdjęć i ewaluacji. Klucz OPENROUTER_API_KEY jest już w środowisku; sprawdź jedynie jego obecność, nigdy wartość. Nie czytaj .env ani plików sekretów. Bez klucza lub budżetu przygotuj lokalną walidację kontraktu i oznacz brak pomiaru, nie udawaj odpowiedzi API.

Dodaj wrapper zgodny z ADR: openai/gpt-6-luna-decisions przez https://openrouter.ai/api/alpha/decisions, typed Choice prędkości 30/50/70/90/none, Noul obecności znaku ograniczenia prędkości i Score czytelności na poziomach 0/1/2. Obraz wyślij jako base64 data URL w image_url w state obok zwykłego tekstu. Nie przekazuj labels, kategorii, nazwy pliku ani atrybutów mapy. none oznacza brak czytelnej wartości z dozwolonego zestawu, nie błąd API; dla trudnych przykładów zachowaj prawdopodobieństwa i abstencję. Obsłuż orientację i rozmiar obrazu zgodnie z wymaganiami obu modeli. Nie loguj base64, klucza ani nagłówka Authorization.

Referencja kontraktu OpenRouter: body ma model, state i questions jako obiekt pytań. Przykładowy kształt, który uzupełnisz zgodnie z wybraną biblioteką i aktualną dokumentacją:
{
  "model": "openai/gpt-6-luna-decisions",
  "state": ["Oceń wyłącznie widoczny znak ograniczenia prędkości.", {"type": "image_url", "image_url": {"url": "data:image/png;base64,BASE64_OBRAZU"}}],
  "questions": {
    "speed": {"type": "choice", "instructions": "Odczytaj najbardziej widoczny znak ograniczenia. Wybierz none, gdy nie da się odczytać wartości 30, 50, 70 lub 90; pomiń tablice informacyjne.", "criteria": {"30": "Czytelne 30 km/h", "50": "Czytelne 50 km/h", "70": "Czytelne 70 km/h", "90": "Czytelne 90 km/h", "none": "Brak czytelnego ograniczenia z podanego zestawu"}},
    "sign_visible": {"type": "noul", "instructions": "Czy widoczny jest znak ograniczenia prędkości, także gdy cyfry są nieczytelne?"},
    "legibility": {"type": "score", "instructions": "Oceń czytelność cyfr najbardziej widocznego znaku ograniczenia prędkości.", "criteria": ["Brak znaku", "Znak widoczny, cyfry nieczytelne", "Cyfry czytelne"]}
  }
}

Ścieżka A, oficjalny openrouter SDK: from openrouter import OpenRouter; client.alpha.decisions.create(model=body["model"], state=body["state"], questions=body["questions"]). Ustaw jawnie timeout_ms=40000 i brak retry, np. RetryConfig("none", BackoffStrategy(100, 100, 1, 100), False) z openrouter.utils jako retry_config konstruktora. Zweryfikuj sygnatury dla przypiętej wersji; punktem odniesienia jest openrouter==1.3.107.
Ścieżka B, openai SDK jako transport HTTP: from openai import OpenAI; klient z api_key=os.environ["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1", max_retries=0 i timeout=40; wywołanie client.post("https://openrouter.ai/api/alpha/decisions", body=body, cast_to=dict). Punktem odniesienia jest openai==3.42.1. Nie przekazuj tego body do client.decisions.create(). To dwie alternatywy, wdrażaj wybraną w ADR.
Odpowiedź OpenRouter ma answers jako obiekt: answers.speed.probabilities jest mapą klasa -> prawdopodobieństwo, Noul zwraca noul, Score zwraca score. Zweryfikuj pełne pola rzeczywistej odpowiedzi, nie zgaduj nazw usage. Rozkład Choice nie jest generowanym uzasadnieniem. Score 0-2 nie jest prawdopodobieństwem.

Zacznij od testów lokalnej walidacji, limitu, cache i reguł abstencji bez fikcyjnego mocka odpowiedzi API. Zanim zrobisz mock endpointu, wykonaj jeden rzeczywisty request na publicznym lub syntetycznym obrazie w przyznanym limicie. Zachowaj status, bezpieczne nagłówki bez sekretów, treść odpowiedzi, datę, endpoint i wersję SDK. Dopiero z tego capture utwórz fixture testową. Pierwsza próba jest częścią limitu, nie dodatkiem. Limit obejmuje wszystkie próby HTTP, także nieudane: najwyżej 25 Luna i 5 Jev, łącznie najwyżej 30, albo mniej według przydziału grupy. Wyłącz retry również wewnątrz SDK; błąd lub timeout to model_unavailable i jawny wpis, bez automatycznej ponownej opłaty. Kod stosuje ustalone progi Choice/Noul/Score, nie model. Nieznana prędkość drogi pozostaje osobnym stanem.

Najpierw pokaż manifest próby i maksymalną liczbę żądań. Uruchom najwyżej 25 unikalnych obrazów na Luna i te same 5 na typesafe/jev-1.14, sekwencyjnie i tylko w przyznanej części wspólnego limitu. Wybierz po jednym czytelnym przykładzie każdej dostępnej klasy, a brak klasy zgłoś. Jeśli próg kosztu nie został uzgodniony, zapytaj przed płatnym uruchomieniem. Nie zmieniaj zdjęć ani pytań między porównywanymi modelami. Zapisuj model zwrócony przez API, wersję pytań, hash obrazu, latencję, input/output tokens i koszt raportowany przez API; rozróżnij koszt OpenRouter i ewentualny koszt upstream BYOK oraz brak wartości. Nie publikuj całych obrazów Commons w Git; cache i capture trzymaj w ignorowanym katalogu wyników bez sekretów.

Zbuduj tabelę accuracy przed abstencją, accuracy na przyjętych odpowiedziach, coverage, liczby abstencji i błędów API, tokenów, kosztu i latencji dla każdego modelu. Pokaż mianowniki i wyłączenia ambiguous_excluded, nie traktuj pustej etykiety jako none. Etykiety Commons są wstępne: pokaż mi obrazy niezgodne z etykietą do ręcznego przeglądu. Progi ustalamy przed końcowym pomiarem, nie dopasowujemy ich do wyniku testu. Pięć obrazów nie uzasadnia wniosku o kalibracji ani przewadze modelu. Uruchom testy i rzeczywisty CLI, zapisz komendy i wyniki. Nie edytuj OSM i nie generuj jeszcze UI.
~~~

**Wynik i Twoja kontrola:** obejrzyj jedno zdjęcie, jego pełny rozkład i decyzję kodu. Sprawdź, że suma prób obejmuje także pierwsze wywołanie, a ponowne uruchomienie używa cache. Porównaj tę samą piątkę modeli, bez dopisywania metryk w razie braku dostępu. Rysunki testują mechanikę; Commons daje osobny pomiar na fotografiach. Nie mieszaj ich w jedną accuracy.

**Jeśli utkniesz:** przy HTTP 401/402/429 lub timeoutcie zatrzymaj płatną pętlę, zachowaj bezpieczny kod błędu i kontynuuj raport na zapisanych odpowiedziach lub etykietach z wyraźnym opisem źródła. Nie zmieniaj modelu na wariant czatowy i nie powtarzaj żądań automatycznie.

**Rozszerzenie:** narysuj tabelę progów na zapisanych rozkładach, bez nowych wywołań. Wyjaśnij różnicę między confidence modelu, selective accuracy i coverage.

## M7. Raport i podział pracy

**Cel:** przedstawić dowody analitykowi i porównać dwa niezależne review. **Agent prowadzący: Codex; recenzenci: subagent Claude Code i Codex.**

**Prompt do skopiowania, Codex:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md oraz dotychczasowe wyniki reports/map-qa/. Po testach przygotuj generator raportu Markdown i statycznego HTML z zapisanych wyników, bez nowych wywołań API. Raport ma zawierać tabelę kandydatów na konflikt, źródłowy i znormalizowany maxspeed, odczyt, rozkład prawdopodobieństw, decyzję kodu, dystans i CRS, miniatury ze źródłem/autorem/licencją oraz liczniki wyłączeń. Oddziel dane syntetyczne od rzeczywistych, etykiety od predykcji, abstencję od niedostępnego modelu. Zero kandydatów jest dopuszczalnym wynikiem. Podaj ograniczenia: pozycja kamery, service road, kierunek, czas i warunkowe ograniczenia oraz wstępne etykiety.

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

Przed każdym review zapisz `git diff` i identyfikator bazowego commita; jeśli w międzyczasie zrobiłeś commit, użyj tego samego zakresu commitów w obu review. Wspólny katalog nie służy do równoległego edytowania tych samych plików. Sprawdź `/context` w Claude Code i `/status` w Codexie; zestaw tokeny tylko przy porównywalnej metodzie pomiaru, a brakujące oznacz jako brak pomiaru. [Codex: review i komendy](https://developers.openai.com/codex/cli/slash-commands).

**Wynik:** raport i tabela porównania uwag: błąd, agent, dowód, Twoja decyzja, poprawka, ponowne sprawdzenie. Wybierz jedną potwierdzoną uwagę, dodaj test wykrywający problem i dopiero potem popraw kod. Przeczytaj diff i wykonaj sprawdzenie CLI ponownie.

**Jeśli utkniesz:** jeśli agent recenzuje tylko opisy, wskaż konkretny zakres Git i pliki. Nie uznawaj ogólnej pochwały ani kodu wyjścia za dowód jakości. Jeśli nie ma subagentów w danym koncie, zrób niezależny przegląd w nowej sesji Claude Code i oznacz różnicę wykonania.

**Rozszerzenie:** opisz powtarzalne generowanie raportu jako projektowy skill, z wejściami, komendą, limitami, kontrolą licencji i sprawdzeniem w świeżej sesji. Nie dopisuj całej logiki generatora do instrukcji skilla.

## Co dalej (blok 2)

- Utwórz tickety Jira dla potwierdzonych ustaleń przez jawnie skonfigurowany MCP, z dowodem i kryterium akceptacji.
- Dodaj UI kolejki przeglądu po uzgodnieniu nowego zakresu w PRD i ADR.
- Otwórz PR, porównaj review agentów z uwagami człowieka i popraw wykryte błędy.
- Uruchom bounded task przez `codex exec` z zapisanym logiem, zakresem uprawnień i weryfikacją wyniku.
