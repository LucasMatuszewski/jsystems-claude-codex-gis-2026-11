# Kontrola mapy: od danych do raportu

Zbudujesz narzędzie dla analityka map QA: połączysz drogi OSM i Overture ze zdjęciami Krakowa, a potem przygotujesz kandydatów do ręcznego sprawdzenia. Przećwiczysz trzy sposoby dostępu do danych: pliki, tabele Databricks i publiczne API. Ty podejmujesz decyzje, agent pisze i sprawdza kod.

## Szybki start

Na przygotowanej VM Windows otwórz PowerShell. Potrzebne narzędzia: Git, uv, Python 3.12, Claude Code i Codex CLI. Nie potrzebujesz WSL ani Dockera. Pierwsza instalacja Pythona, bibliotek i rozszerzenia spatial wymaga internetu. Poniższe cztery polecenia sprawdzają repozytorium i lokalne dane; pierwsze 10 zdjęć downloader odtwarza z `offline/`:

```powershell
Set-Location D:\jsystems-claude-codex-gis-2026-11
```

```powershell
git status --short
```

```powershell
uv run --python 3.12 course-materials/exercise-data/map-qa/profile_data.py
```

```powershell
uv run --python 3.12 course-materials/exercise-data/map-qa/download_photos.py --limit 10
```

Zostajesz w katalogu głównym repozytorium. [README danych](../../exercise-data/map-qa/README.md) opisuje źródła i polecenia dostępu. Najpierw M1, potem pozostałe kroki po kolei:

| Krok | Agent | Wynik |
|---|---|---|
| M1 | Claude Code | Uzgodniony PRD |
| M2 | Codex | Profil plików, tabel i API |
| M3 | Claude Code | Zasady w AGENTS.md |
| M4 | Codex | ADR, potem plan |
| M5 | Codex | Pierwszy etap pipeline'u z testami |
| M6 | Claude Code | Mała próba modelu decyzyjnego |
| M7 | Codex i Claude Code | Raport i dwa przeglądy |

Przed zmianą agenta sprawdź diff i zakończ sesję agenta. Jeden agent edytuje dany plik w danej chwili. Zachowaj istniejący PRD i wcześniejszą pracę. M1-M5 nie wymagają płatnego modelu API; zapytania SQL mogą uruchomić współdzielony warehouse. M6 wymaga przydziału ze wspólnego limitu przez prowadzącego.

## M1. Uzgodnij PRD

**Cel:** określić, komu i do jakiej decyzji potrzebny jest raport. **Agent: Claude Code.**

Użyj skilla `write-prd`. Jeśli go brakuje, zakończ agenta, w katalogu repozytorium powtórz instalację z początku kursu i uruchom agenta ponownie:

```powershell
npx --yes skills@latest add EdukeyTeam/agent-toolbox --skill '*'
```

**Prompt:**

~~~text
Użyj skilla write-prd. Przeczytaj AGENTS.md oraz course-materials/exercise-data/map-qa/README.md i sources.json; masz zgodę na ten katalog danych, nie na resztę course-materials/. Sprawdź istniejący docs/PRD.md, nie zastępuj wcześniejszej pracy.

Potrzebujemy narzędzia dla analityka map QA. Wejścia: drogi OSM, segmenty Overture, manifest i zdjęcia ulic Krakowa, z plików, Databricks i API. Analityk sprawdza brakujące atrybuty, niepewne połączenia zdjęć z drogą oraz różnice prędkości i nawierzchni. Zdjęcie ma pomóc odczytać widoczne cechy, nie rozstrzygać automatycznie o błędzie mapy. Źródła mają różne daty, Overture częściowo pochodzi z OSM, pozycja aparatu nie jest pozycją znaku. Kontrola topologii i prosty dashboard z przyciskami w Streamlit lub PySide6 są opcjonalne.

Najpierw zapytaj o brakujące decyzje: użytkowników, działanie po raporcie, zakres i progi, wynik, niepewność, limit kosztu i elementy poza zakresem. Poczekaj na odpowiedzi. Potem zapisz krótki docs/PRD.md po polsku, z mierzalnymi kryteriami akceptacji. Nie pisz ADR ani kodu. Nie czytaj sekretów i nie uruchamiaj płatnego API. Zatrzymaj się do mojego przeglądu.
~~~

**Sprawdź sam:**

- Agent zadał pytania i poczekał na Twoje odpowiedzi.
- Przeczytaj PRD i samodzielnie zmień dwa wymagania, np. format wyniku i zachowanie przy niepewności.
- Kryteria pozwalają sprawdzić wynik; rozbieżność źródeł nie oznacza automatycznie błędu mapy.

**Jeśli utkniesz:** wybierz raport CLI i dwa atrybuty do pierwszej wersji.

**Rozszerzenie:** dodaj wymaganie prostego dashboardu do przeglądu kandydatów.

## M2. Pobierz i poznaj dane

**Cel:** wykonać odczyt z plików, Databricks i API przed projektem pipeline'u. **Agent: Codex.**

Najpierw sam sprawdź dostęp. W [instrukcji źródeł](../../exercise-data/map-qa/README.md#trzy-sposoby-dostępu-do-danych) wykonaj: lokalny profil i kontrolę GeoPandas, odczyt pięciu wierszy Databricks oraz po jednym odczycie Mapillary, Panoramax i Overture. Tokeny wprowadzasz sam w PowerShell; do agenta trafiają tylko nazwy zmiennych. Przy niedostępnym źródle zanotuj brak i użyj plików, bez blokowania ćwiczenia. Potem agent wykona własne małe odczyty do powtarzalnego profilu.

**Prompt:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md oraz README.md, sources.json i profile.sql w course-materials/exercise-data/map-qa/. Masz zgodę na ten katalog danych, nie na resztę materiałów. Wykonaj małe odczyty opisane w README: pliki, workspace.map_qa przez CLI/REST, API Mapillary i Panoramax oraz publiczny Overture przez DuckDB. Nie zmieniaj wejść, nie wywołuj modelu, nie wyświetlaj tokenów ani konfiguracji uwierzytelniania. Przy braku dostępu zapisz ograniczenie i profiluj lokalny snapshot.

Zapisz reports/map-qa/profile.md: polecenia, wersje, daty i hashe plików, liczności i typy, CRS, poprawność geometrii, duplikaty i relacje kluczy. Porównaj liczności tabel z plikami. Sprawdź kompletność highway, maxspeed i maxspeed:*, surface, lanes, oneway, lit, sidewalk*, junction, name, ref oraz pełne tags. W Overture zachowaj wszystkie reguły speed_limits, road_surface, when, between i sources; nie tylko pierwszy element.

Sprawdź udział zdjęć z kandydatem drogi, dystanse po transformacji obu stron do EPSG:2180, heading, alternatywne drogi i GPS. Oddziel referencję OSM od dopasowania wyłącznie przestrzennego. Sama różnica liczby segmentów nie mierzy jakości. Obejrzyj kilka zdjęć z różnych sekwencji i scen, sprawdź daty, hashe i atrybucje; nie wnioskuj o scenie wyłącznie z highway. Opisz ograniczenia i pokaż przykłady połączeń. Nie implementuj pipeline'u.
~~~

**Sprawdź sam:**

- Profil DuckDB pokazał liczności wejść, a GeoPandas poprawne geometrie i EPSG:2180.
- Odczyt Databricks zwrócił pięć wierszy albo profil jawnie podaje brak dostępu; porównaj liczności lokalne i chmurowe.
- Otwórz jedno zdjęcie z niepewnym dopasowaniem i sprawdź, czy to właściwa jezdnia.

**Jeśli utkniesz:** użyj GeoParquet i `offline/`; awaria Databricks lub Mapillary nie zatrzymuje pracy.

**Rozszerzenie:** [podłącz SQL przez MCP](../../exercise-data/map-qa/DATABRICKS.md#managed-mcp-w-claude-code) i porównaj wynik z CLI.

## M3. Zapisz zasady agenta

**Cel:** sprawdzić, czy nowa sesja respektuje zasady projektu. **Agent: Claude Code.**

**Prompt:**

~~~text
Przeczytaj AGENTS.md, CLAUDE.md, docs/PRD.md i course-materials/exercise-data/map-qa/README.md. Uzupełnij AGENTS.md dla uzgodnionego pipeline'u, zachowując istniejące reguły. CLAUDE.md ma importować @AGENTS.md, bez kopii zasad. Nie zmieniaj kodu ani danych.

Uwzględnij: wejścia tylko do odczytu; raporty w reports/map-qa/, pobrania/cache w ignorowanym course-materials/exercise-data/map-qa/data/; Python 3.12 i uv; metry dopiero w EPSG:2180 obu warstw; sekrety tylko przez zmienne środowiskowe, bez odczytu .env i wyświetlania wartości; etykiety, detekcje i atrybuty mapy nigdy nie trafiają do modelu obrazu. Zachowuj licencje i atrybucje. Wyłączenia mają przyczyny i liczniki, usuwanie rekordów wymaga uzgodnienia. API ma limit wszystkich prób i kosztu, timeout, cache i zero automatycznych retry, także w SDK. Rozróżniaj none, unknown, abstain i model_unavailable. Nowa funkcja zaczyna się od testu. Pozostałe course-materials/ czytaj tylko na wyraźne polecenie.

Pokaż diff i kolizje zasad; nie usuwaj ich po cichu. Zakończ bez implementacji.
~~~

**Sprawdź sam:**

- `CLAUDE.md` odsyła do jednego pliku zasad.
- W świeżej sesji poproś o kolejny mały krok na podstawie PRD i profilu, bez implementacji. Sprawdź użyte komendy i ścieżki: agent sam ma odczytać instrukcje i zachować wejścia.

**Jeśli utkniesz:** sprawdź katalog roboczy i zaufanie do repozytorium w nowej sesji.

**Rozszerzenie:** sprawdź [hook ochrony danych](../../hooks-example/) na osobnej próbnej kopii; sam AGENTS.md nie blokuje zapisu.

## M4. Wybierz architekturę, potem zaplanuj pracę

### M4a. ADR ze skillem

**Cel:** samodzielnie wybrać narzędzia i zapisać powody. **Agent: Codex.**

**Prompt:**

~~~text
Użyj skilla write-adr. Przeczytaj AGENTS.md, docs/PRD.md i reports/map-qa/profile.md oraz schematy danych map-qa wskazane w profilu. Nie pisz kodu. Zanim zapiszesz ADR, przedstaw kandydatów z linkami do aktualnej oficjalnej dokumentacji i krótkimi kompromisami:
- DuckDB spatial kontra GeoPandas/Shapely/pyproj dla obliczeń przestrzennych;
- lokalne GeoParquet kontra tabele Databricks przez CLI/REST, MCP opcjonalnie;
- OpenRouter SDK client.alpha.decisions.create kontra surowy POST /api/alpha/decisions;
- openai/gpt-6-luna-decisions kontra typesafe/jev-1.14;
- raport Markdown i HTML, a jeśli dashboard jest w PRD: Streamlit kontra PySide6.
Sprawdź dokumentacje przez Context7 lub u źródła, nie zgaduj API. Zapytaj o moje decyzje i poczekaj. Następnie zapisz ADR po polsku w docs/ADR/.

Ustal normalizację bez gubienia tagów i reguł when/between, EPSG:2180 dla metrów, dopasowanie z kierunkiem, remisami, service/access, poziomem i datami. Dostarczone połączenia są kandydatami, nie prawdą terenową. Oddziel odczyt zdjęcia od mapy i etykiet; zachowaj niepewność, licencje i atrybucje. Ustal progi przed pomiarem, limit wszystkich prób HTTP i kosztu, timeout, cache po hashu obrazu/modelu/pytań i brak automatycznych retry. Testy przed kodem, mock API dopiero z bezpiecznego rzeczywistego capture; etap kończy rzeczywisty CLI. Nie odczytuj sekretów ani nie uruchamiaj płatnego API. Zatrzymaj się do przeglądu ADR.
~~~

**Sprawdź sam:** wybrałeś biblioteki po porównaniu; ADR ma linki, powody i Twoje decyzje, a nie domysły agenta.

**Jeśli utkniesz:** przy braku `write-adr` powtórz instalację z M1 i zrestartuj Codexa; przy trudnościach z wyborem zacznij od lokalnych GeoParquet i CLI.

### M4b. Plan z promptu

**Cel:** podzielić implementację na małe etapy z warunkiem zakończenia. **Agent: Codex.**

Po przeglądzie ADR włącz tryb planowania. Nie wywołuj skilla planowania: najpierw sprawdź sam prompt.

**Prompt:**

~~~text
Na podstawie AGENTS.md, uzgodnionego docs/PRD.md, docs/ADR/, reports/map-qa/profile.md i aktualnego app/ przygotuj plan do docs/plan.md. Bez implementacji, delegowania i płatnego API. Zapytaj o brakujące decyzje i poczekaj.

Dobry plan ma etapy z wejściami, wyjściami, plikami i zależnościami: odczyt/normalizacja, CRS i dopasowania, porównanie atrybutów, model/ewaluacja, raport. Topologia i dashboard tylko z PRD. Każdy etap zaczyna się testami: oczekiwane Red, minimum Green, Refactor przy zielonych testach. Warunek zakończenia podaje kryterium PRD, zakres testów, rzeczywisty CLI i ręczną kontrolę wyniku. Kompilacja/importy, testy z licznością i pominięciami oraz start aplikacji to osobne kontrole.

Zacznij od małej próbki. Zapisz ochronę kosztu: limit wszystkich prób, brak automatycznych retry i zakaz płatnego uruchomienia bez przydzielonego budżetu. Wskaż, co jest poza zakresem, ryzyka i jedną pierwszą czynność. Po każdym zweryfikowanym etapie przewidź commit. Pokaż plan i poczekaj na akceptację; jeśli tryb planowania nie pozwala zapisać pliku, zapisz go po wyjściu z tego trybu. Nie zaczynaj kodowania.
~~~

**Sprawdź sam:** potrafisz wskazać pierwszy etap, jego test i obserwowalny warunek zakończenia.

**Jeśli utkniesz:** pierwszy etap ogranicz do kontraktu jednego wejścia i jego testów.

**Rozszerzenie:** zamień tę sprawdzoną sesję w skill projektu, np. `.agents/skills/plan-pipeline/SKILL.md`. Z `skill-creator` wyodrębnij powtarzalne reguły, podaj wejścia, wynik i ograniczenia; fakty projektu pozostaw w PRD. Sprawdź skill w świeżej sesji na innym małym zadaniu, porównując otrzymany plan z kryteriami powyżej.

## M5. Zbuduj pierwszy etap z testami

**Cel:** przejść Red -> Green -> Refactor na rzeczywistych danych. **Agent: Codex.**

**Prompt:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md i reports/map-qa/profile.md. Wykonaj tylko pierwszy zatwierdzony etap w app/. Najpierw pytest z wymagań: uruchom i pokaż oczekiwane Red, potem minimum kodu, Green i Refactor. Nie zmieniaj wejść, nie wywołuj modelu, nie odczytuj sekretów. Dane syntetyczne są tylko do małych testów; wykonaj też rzeczywisty CLI na plikach map-qa.

Dobierz przypadki do etapu: brak/tekst/jednostki/PL:urban/none/wiele wartości maxspeed, tagi kierunkowe i warunkowe; wszystkie reguły Overture z when/between. Przy łączeniu: obie warstwy w EPSG:2180, znany dystans, dwa bliskie odcinki, heading 359/1, odwrotna geometria i oneway=-1, brak kierunku, remis, service/access i most/tunel. Aparat nie wyznacza kierunku jazdy. Sprawdź wejściowe photo_road_links i odróżnij referencję OSM od joinu przestrzennego. Rozróżniaj brak, nieporównywalność i rozbieżność; zachowuj surowe wartości, daty, identyfikatory i liczniki wyłączeń. Topologię, jeśli jest w zakresie, sprawdzaj przez node_ids; granica wycinka nie dowodzi błędu sieci.

Pokaż osobno wyniki testów i uruchomienia CLI oraz ręcznie sprawdzony przykład. Nie osłabiaj testów pod implementację. Zakończ po tym etapie, pokaż diff i poczekaj na przegląd.
~~~

**Sprawdź sam:**

- Widziałeś test czerwony przed kodem, potem zielony; asercje sprawdzają wynik.
- CLI działa na rzeczywistym wycinku, a jeden wynik możesz odtworzyć z wejść.
- Żaden plik wejściowy nie zmienił się w diffie.

**Jeśli utkniesz:** zmniejsz próbkę, zachowując przypadek, na którym wynik jest błędny.

**Rozszerzenie:** wykonaj kolejny zaakceptowany etap tą samą metodą.

## M6. Odczytaj zdjęcie modelem decyzyjnym

**Cel:** zmierzyć odczyt widocznych cech i abstencję, oddzielnie od jakości dopasowania drogi. **Agent: Claude Code.**

[Kontrakt Decisions](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request), [obrazy](https://openrouter.ai/docs/guides/community/multimodal-decisions), [SDK Python](https://openrouter.ai/docs/client-sdks/python/sdks/decisions/README). Klucz `OPENROUTER_API_KEY` jest przygotowany w środowisku VM; sprawdzaj tylko obecność. Najpierw jedno zdjęcie, potem mała próbka w limicie prowadzącego.

**Prompt:**

~~~text
Przeczytaj AGENTS.md, PRD, ADR, docs/plan.md, dotychczasowy kod i README danych map-qa. Zrealizuj tylko uzgodniony etap Decisions przez OpenRouter: openai/gpt-6-luna-decisions i porównanie typesafe/jev-1.14. Użyj transportu z ADR: client.alpha.decisions.create w OpenRouter SDK lub surowy POST https://openrouter.ai/api/alpha/decisions. Nie używaj natywnego OpenAI client.decisions.create, bo ma inny kontrakt. Sprawdź aktualną dokumentację, przypnij wersję. Body ma model, state i questions jako obiekt; Choice zwraca mapę probabilities, typ Noul zwraca pole noul, a typ Score pole score, które nie jest prawdopodobieństwem.

Wybierz tylko pytania z PRD: rodzina drogi, paved/unpaved/unknown, widoczne skrzyżowanie, znak i jego wartość, pasy w kierunku patrzenia, chodnik, lampy. Listę wartości znaku uzgodnij na podstawie profilu, nie ograniczaj jej arbitralnie do kilku liczb. none to brak widocznego znaku liczbowego, unknown to brak pewnego odczytu, abstain to decyzja kodu, model_unavailable to błąd API. Brak widoczności nie dowodzi nieobecności. Do state trafia tylko neutralny tekst i obraz jako image_url z base64 data URL, z MIME zgodnym z bajtami i poprawną orientacją/rozmiarem. Nigdy etykiety, nazwy plików, kategorie, atrybuty mapy, traffic_signs ani detekcje. Nie loguj base64, sekretów ani Authorization; nie czytaj .env.

Najpierw testy lokalnej walidacji, limitu, cache i abstencji. Przed mockiem endpointu wykonaj jeden rzeczywisty request w przydzielonym limicie i zachowaj bezpieczny capture: status, nagłówki bez sekretów, pełna odpowiedź, data, endpoint i wersja SDK. Bez dostępu oznacz brak pomiaru, nie wymyślaj odpowiedzi. Pokaż manifest próbki i maksymalną liczbę żądań. Bez ustalonego budżetu zapytaj i poczekaj. Pierwsza próba oraz błędy też liczą się do limitu: najwyżej 25 Luna i te same 5 zdjęć Jev, łącznie 30 albo mniej według przydziału. To do 25 unikalnych zdjęć na Luna i wspólna piątka na Jev, bez zapasu na automatyczne ponowienia. Wyłącz automatyczne retry również w SDK, ustaw timeout 40 s; po błędzie przerwij płatną pętlę. Cache: hash obrazu + model + wersja pytań, w ignorowanym course-materials/exercise-data/map-qa/data/. Progi ustal przed końcowym testem; stosuje je kod.

Etykiety reference_labels.csv odczytaj wyłącznie w ewaluatorze. Accuracy przed abstencją i na przyjętych odpowiedziach mierz tylko dla pytań z pewnymi etykietami: surface, junction_visible, street_lighting_visible i speed_limit_value. Dla pozostałych pokaż rozkłady, decyzje, coverage i liczniki prób bez accuracy; dodatkowe etykietowanie wymaga osobnego uzgodnienia. Wspólna piątka ma zawierać pewne etykiety każdego pytania z pomiarem accuracy; brak klasy zgłoś. Dziel po sequence, nie sąsiednich klatkach. Nie zmieniaj pytań ani obrazów między modelami. Zapisz zwrócony model, latencję, tokeny, raportowany koszt OpenRouter/upstream BYOK; brak kosztu nie jest zerem. Coverage, abstencje i błędy API pokaż dla każdego pytania i modelu, z jawnymi mianownikami. Wyłącz uncertain tylko dla danego pytania, nie utożsamiaj pustej etykiety z none. Nie mieszaj syntetycznych rysunków z oceną zdjęć. Mała piątka nie dowodzi kalibracji ani przewagi modelu. Uruchom testy i CLI, pokaż niezgodności i próbkę zgodności do ręcznego przeglądu. Nie edytuj mapy ani nie twórz UI.
~~~

**Sprawdź sam:**

- Obejrzyj zdjęcie, pełny rozkład i decyzję kodu; model nie otrzymał mapy ani etykiety.
- Licznik obejmuje pierwszą próbę i błędy, ponowne uruchomienie korzysta z cache.
- Modele porównujesz na tej samej piątce, a metryki mają jawne mianowniki.

**Jeśli utkniesz:** przy 401/402/429 lub timeoutcie zatrzymaj płatne wywołania, zachowaj bezpieczny kod błędu i pracuj na cache z opisem źródła.

**Rozszerzenie:** porównaj progi na zapisanych rozkładach bez kolejnych wywołań.

## M7. Przygotuj raport i porównaj review

**Cel:** przekazać analitykowi dowody i sprawdzić rozwiązanie dwoma agentami. **Agenci: Codex i Claude Code.**

**Prompt do Codexa:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md i reports/map-qa/. Najpierw testy, potem generator raportu Markdown i statycznego HTML z zapisanych wyników, bez nowych wywołań API. Pokaż kandydatów z identyfikatorami, datami, surowymi i znormalizowanymi atrybutami OSM/Overture, odczytem zdjęcia, prawdopodobieństwami, decyzją kodu, dystansem i CRS. Dodaj miniatury z autorem, źródłem i licencją oraz liczniki wyłączeń. Zero kandydatów jest dopuszczalne.

Oddziel źródła mapowe, obserwacje, etykiety i predykcje, dane syntetyczne, abstencję i brak modelu. Opisz ograniczenia pozycji aparatu, kierunku, czasu, service road i reguł warunkowych. HTML ma działać lokalnie bez serwera, z względnymi ścieżkami obrazów i bez base64/sekretów. Escapuj niezaufane tagi, nazwy i autorów. Nie odczytuj sekretów ani nie edytuj mapy.

Uruchom testy i rzeczywisty CLI. Otwórz HTML, sprawdź obrazy, linki, atrybucje, polskie znaki oraz zgodność liczników z Markdown i wejściami. Podaj komendę, ścieżki i zrzut raportu. Pokaż diff i jeden wspólny brief dla obu recenzentów: bazowy commit i zakres diffu, PRD/ADR/plan, pliki i listę kontroli: CRS, normalizacja, liczniki, przeciek etykiet, kontrakt Decisions, retry/cache/budżet, abstencja, licencje i escape HTML; wynik review ma wskazywać plik i linię, skutek, dowód i sposób sprawdzenia. Zakończ edycję i poczekaj na review.
~~~

Po zapisaniu raportu wstrzymaj edycje. Zapisz bazowy commit sprzed M5 i zakres diffu. **Ten sam zakres** sprawdź w dwóch niezależnych sesjach:

1. W Claude Code zleć jednemu subagentowi wyłącznie odczyt i review kodu względem PRD, ADR i planu. Bez subagentów użyj świeżej sesji Claude Code.
2. W Codexie użyj `/review`, wskazując ten sam zakres zmian. Jeśli zmiany nie są jeszcze zapisane w commicie, wybierz odpowiednią opcję menu.

Przekaż obu recenzentom brief przygotowany przez agenta i wskaż: CRS, normalizację, liczniki, przeciek etykiet, kontrakt Decisions, retry/cache/budżet, abstencję, licencje i escape HTML. Wymagaj pliku i linii, skutku, dowodu oraz sposobu sprawdzenia; bez edycji i płatnego API. Porównaj uwagi w tabeli: problem, agent, dowód, Twoja decyzja, poprawka i ponowny test. Zużycie tokenów porównuj tylko przy tej samej metodzie pomiaru; brak metryki zapisz jako brak.

**Sprawdź sam:**

- Otwórz HTML i prześledź jeden wiersz od zdjęcia przez drogę do decyzji.
- Porównaj liczniki HTML, Markdown i wejść.
- Dla jednej potwierdzonej uwagi najpierw dodaj test wykrywający problem, potem popraw kod i ponów CLI. Jeśli uwag brak, zapisz to bez wymyślania błędu.

**Jeśli utkniesz:** zawęź review do konkretnych plików i zakresu Git; ogólna pochwała nie jest dowodem poprawności.

**Rozszerzenie:** opisz powtarzalne generowanie raportu jako skill projektu i sprawdź go w świeżej sesji.
