# Kontrola mapy: od danych do raportu

Zbudujesz narzędzie dla analityka map QA: połączysz drogi OSM i Overture ze zdjęciami Krakowa, a potem przygotujesz kandydatów do ręcznego sprawdzenia. Przećwiczysz dostęp przez pliki i tabele Databricks, a jeśli masz czas, także przez publiczne API. Ty podejmujesz decyzje, agent pisze i sprawdza kod.

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
| M2 | Codex | Profil plików i tabel, API opcjonalnie |
| M3 | Claude Code | Zasady w AGENTS.md |
| M4 | Codex | ADR, potem plan |
| M5 | Codex | Pierwszy etap pipeline'u z testami |
| M6 | Claude Code | Mała próba modelu decyzyjnego |
| M7 | Codex | Raport Markdown i HTML |

Przed zmianą agenta sprawdź diff i zakończ sesję agenta. Jeden agent edytuje dany plik w danej chwili. Zachowaj istniejący PRD i wcześniejszą pracę. M1-M5 nie wymagają płatnego modelu API; zapytania SQL mogą uruchomić współdzielony warehouse. M6 wymaga przydziału ze wspólnego limitu przez prowadzącego.

## M1. Uzgodnij PRD

**Cel:** określić, komu i do jakiej decyzji potrzebny jest raport. **Agent: Claude Code.**

Użyj skilla `write-prd`. Jeśli go brakuje, zakończ agenta, w katalogu repozytorium powtórz instalację z początku kursu i uruchom agenta ponownie:

```powershell
npx --yes skills@latest add EdukeyTeam/agent-toolbox --skill '*' --agent claude-code codex --yes
```

**Prompt:**

~~~text
Użyj skilla write-prd. Przeczytaj AGENTS.md oraz course-materials/exercise-data/map-qa/README.md i sources.json; masz zgodę na ten katalog danych, nie na resztę course-materials/. Sprawdź istniejący docs/PRD.md, nie zastępuj wcześniejszej pracy.

Potrzebujemy narzędzia dla analityka map QA. Wejścia: drogi OSM, segmenty Overture, manifest i zdjęcia ulic Krakowa, z plików, Databricks i API. Analityk sprawdza brakujące atrybuty, niepewne połączenia zdjęć z drogą oraz różnice prędkości i nawierzchni. Zdjęcie ma pomóc odczytać widoczne cechy, nie rozstrzygać automatycznie o błędzie mapy. Źródła mają różne daty, Overture częściowo pochodzi z OSM, pozycja aparatu nie jest pozycją znaku. Kontrola topologii i prosty dashboard z przyciskami w Streamlit lub PySide6 są opcjonalne.

Najpierw zapytaj o brakujące decyzje: użytkowników, działanie po raporcie, zakres i progi, wynik, niepewność, limit kosztu i elementy poza zakresem. Poczekaj na odpowiedzi. Potem zapisz krótki docs/PRD.md po polsku, z mierzalnymi kryteriami akceptacji. Nie pisz ADR ani kodu. Nie czytaj sekretów i nie uruchamiaj płatnego API. Zatrzymaj się do mojego przeglądu.
~~~

**Własny pomysł:** pełniejszy przykład opisu produktu jest w [PRD-map-qa-street-photos.md](../../Prompt%20examples/PRD-map-qa-street-photos.md). Możesz go wkleić zamiast promptu powyżej albo potraktować jako wzór i opisać narzędzie z własnej pracy: inny atrybut, inne źródło, inny odbiorca raportu.

**Sprawdź sam:**

- Agent zadał pytania i poczekał na Twoje odpowiedzi.
- Przeczytaj PRD i samodzielnie zmień dwa wymagania, np. format wyniku i zachowanie przy niepewności.
- Kryteria pozwalają sprawdzić wynik; rozbieżność źródeł nie oznacza automatycznie błędu mapy.

**Jeśli utkniesz:** wybierz raport CLI i dwa atrybuty do pierwszej wersji.

**Rozszerzenie:** dodaj wymaganie prostego dashboardu do przeglądu kandydatów.

## M2. Pobierz i poznaj dane

**Cel:** odczytać pliki i Databricks przed projektem pipeline'u; odczyt API opcjonalnie. **Agent: Codex.**

Najpierw sam sprawdź dostęp. W [instrukcji źródeł](../../exercise-data/map-qa/README.md#trzy-sposoby-dostępu-do-danych) wykonaj obowiązkowo lokalny profil, kontrolę GeoPandas i odczyt pięciu wierszy Databricks ze wspólnym tokenem od prowadzącego z czatu. Odczyty Mapillary, Panoramax i Overture są opcjonalne: wykonaj je, jeśli masz czas. Tokeny wprowadzasz sam w PowerShell; do agenta trafiają tylko nazwy zmiennych. Przy niedostępnym źródle zanotuj brak i użyj plików. Potem agent wykona własne małe odczyty do profilu.

Uruchom Codexa z tego samego okna PowerShell, w którym ustawiłeś zmienne, i zatwierdzaj polecenia sieciowe, gdy poprosi o zgodę.

**Prompt:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md oraz README.md, sources.json i profile.sql w course-materials/exercise-data/map-qa/. Masz zgodę na ten katalog danych, nie na resztę materiałów. Wykonaj małe odczyty opisane w README: pliki i workspace.map_qa przez CLI/REST; jeśli masz czas, także API Mapillary i Panoramax oraz publiczny Overture przez DuckDB. Nie zmieniaj wejść, nie wywołuj modelu, nie wyświetlaj tokenów ani konfiguracji uwierzytelniania. Przy braku dostępu zapisz ograniczenie i profiluj lokalny snapshot.

Zapisz reports/map-qa/profile.md: polecenia, wersje, daty i hashe plików, liczności i typy, CRS, poprawność geometrii, duplikaty i relacje kluczy. Porównaj liczności tabel z plikami. Sprawdź kompletność highway, maxspeed*, surface, lanes, lit, sidewalk* oraz pełne tags. W Overture zachowaj wszystkie reguły speed_limits, road_surface, when, between i sources; nie tylko pierwszy element.

Sprawdź udział zdjęć z kandydatem drogi, dystanse po transformacji obu stron do EPSG:2180, heading, alternatywne drogi i GPS. Oddziel referencję OSM od dopasowania wyłącznie przestrzennego. Sama różnica liczby segmentów nie mierzy jakości. Opisz ograniczenia i pokaż przykłady połączeń. Nie implementuj pipeline'u.
~~~

**Sprawdź sam:**

- Profil DuckDB pokazał liczności wejść, a GeoPandas poprawne geometrie i EPSG:2180.
- Odczyt Databricks zwrócił pięć wierszy albo profil jawnie podaje brak dostępu; porównaj liczności lokalne i chmurowe.
- Otwórz jedno zdjęcie z niepewnym dopasowaniem i sprawdź, czy to właściwa jezdnia.

**Jeśli utkniesz:** użyj GeoParquet i `offline/`; awaria Databricks lub Mapillary nie zatrzymuje pracy.

**Rozszerzenie:** w Claude Code [podłącz SQL przez MCP](../../exercise-data/map-qa/DATABRICKS.md#managed-mcp-w-claude-code) i porównaj wynik z CLI.

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
Sprawdź dokumentacje przez Context7 lub u źródła, nie zgaduj API. Zadaj najwyżej 5 pytań. Zapytaj o moje decyzje i poczekaj. Następnie zapisz ADR po polsku w docs/ADR/.

Ustal normalizację bez gubienia tagów i reguł when/between, EPSG:2180 dla metrów, dopasowanie z kierunkiem, remisami, service/access, poziomem i datami. Dostarczone połączenia są kandydatami, nie prawdą terenową. Oddziel odczyt zdjęcia od mapy i etykiet; zachowaj niepewność, licencje i atrybucje. Ustal progi przed pomiarem, limit wszystkich prób HTTP i kosztu, timeout, cache po hashu obrazu/modelu/pytań i brak automatycznych retry. Testy przed kodem, mock API dopiero z bezpiecznego rzeczywistego capture; etap kończy rzeczywisty CLI. Nie odczytuj sekretów ani nie uruchamiaj płatnego API. Zatrzymaj się do przeglądu ADR.
~~~

**Własny pomysł:** przykład promptu ADR z linkami do dokumentacji jest w [ADR-generation-python-gis-map-qa.md](../../Prompt%20examples/ADR-generation-python-gis-map-qa.md); dopisz do niego biblioteki, których używasz w pracy.

**Sprawdź sam:** wybrałeś biblioteki po porównaniu; ADR ma linki, powody i Twoje decyzje, a nie domysły agenta.

**Jeśli utkniesz:** przy braku `write-adr` powtórz instalację z M1 i zrestartuj Codexa; przy trudnościach z wyborem zacznij od lokalnych GeoParquet i CLI.

### M4b. Plan z promptu

**Cel:** podzielić implementację na małe etapy z warunkiem zakończenia. **Agent: Codex.**

Po przeglądzie ADR w Codex CLI wpisz `/plan` i naciśnij Enter ([dokumentacja OpenAI](https://learn.chatgpt.com/docs/developer-commands?surface=cli#switch-to-plan-mode-with-plan)). Opcjonalnie w Claude Code przełączaj tryby klawiszami Shift+Tab, aż zobaczysz tryb planowania. Jeśli Twoja wersja nie udostępnia tego trybu, poproś o plan bez zmian w plikach. Nie wywołuj skilla planowania: najpierw sprawdź sam prompt.

**Prompt:**

~~~text
Na podstawie AGENTS.md, uzgodnionego docs/PRD.md, docs/ADR/, reports/map-qa/profile.md i aktualnego app/ przygotuj plan do docs/plan.md. Bez implementacji, delegowania i płatnego API. Zadaj najwyżej 5 pytań. Zapytaj o brakujące decyzje i poczekaj.

Dobry plan ma etapy z wejściami, wyjściami, plikami i zależnościami: odczyt/normalizacja, CRS i dopasowania, porównanie atrybutów, model/ewaluacja, raport. Topologia i dashboard tylko z PRD. Każdy etap zaczyna się testami: oczekiwane Red, minimum Green, Refactor przy zielonych testach. Warunek zakończenia podaje kryterium PRD, zakres testów, rzeczywisty CLI i ręczną kontrolę wyniku. Kompilacja/importy, testy z licznością i pominięciami oraz start aplikacji to osobne kontrole.

Zacznij od małej próbki. Zapisz ochronę kosztu: limit wszystkich prób, brak automatycznych retry i zakaz płatnego uruchomienia bez przydzielonego budżetu. Wskaż, co jest poza zakresem, ryzyka i jedną pierwszą czynność. Po każdym zweryfikowanym etapie przewidź commit. Pokaż plan i poczekaj na akceptację; jeśli tryb planowania nie pozwala zapisać pliku, zapisz go po wyjściu z tego trybu. Nie zaczynaj kodowania.
~~~

**Sprawdź sam:** potrafisz wskazać pierwszy etap, jego test i obserwowalny warunek zakończenia.

**Jeśli utkniesz:** pierwszy etap ogranicz do kontraktu jednego wejścia i jego testów.

**Rozszerzenie:** zamień tę sprawdzoną sesję w skill projektu, np. `.agents/skills/plan-pipeline/SKILL.md`. Poproś agenta (albo skill `skill-creator`, jeśli masz go zainstalowanego), aby wyodrębnił powtarzalne reguły, wejścia, wynik i ograniczenia; fakty projektu pozostaw w PRD. Sprawdź skill w świeżej sesji na innym małym zadaniu, porównując otrzymany plan z kryteriami powyżej.

Po zaakceptowaniu i zapisaniu planu sprawdź diff, a następnie zatwierdź PRD, ADR, AGENTS.md, CLAUDE.md i plan. Zapisz hash bazowego commitu sprzed M5 do późniejszego review:

```powershell
git add docs AGENTS.md CLAUDE.md
```

```powershell
git commit -m "Docs: PRD, ADR, plan"
```

```powershell
git rev-parse HEAD
```

## M5. Zbuduj pierwszy etap z testami

**Cel:** przejść Red -> Green -> Refactor na rzeczywistych danych. **Agent: Codex.**

**Prompt:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md i reports/map-qa/profile.md. Wykonaj tylko pierwszy zatwierdzony etap w app/. Najpierw pytest z wymagań: uruchom i pokaż oczekiwane Red, potem minimum kodu, Green i Refactor. Nie zmieniaj wejść, nie wywołuj modelu, nie odczytuj sekretów. Do testów wybierz kilka prawdziwych rekordów z plików map-qa; wykonaj też rzeczywisty CLI na pełnych plikach map-qa.

Wybierz najwyżej 6 przypadków testowych dla tego etapu. Dobierz je do zakresu: brak/tekst/jednostki/PL:urban/none/wiele wartości maxspeed, tagi kierunkowe i warunkowe; wszystkie reguły Overture z when/between. Przy łączeniu: obie warstwy w EPSG:2180, znany dystans, dwa bliskie odcinki, heading 359/1, odwrotna geometria i oneway=-1, brak kierunku, remis, service/access i most/tunel. Aparat nie wyznacza kierunku jazdy. Sprawdź wejściowe photo_road_links i odróżnij referencję OSM od joinu przestrzennego. Rozróżniaj brak, nieporównywalność i rozbieżność; zachowuj surowe wartości, daty, identyfikatory i liczniki wyłączeń. Topologię, jeśli jest w zakresie, sprawdzaj przez node_ids; granica wycinka nie dowodzi błędu sieci.

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

[Kontrakt Decisions](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request), [obrazy](https://openrouter.ai/docs/guides/community/multimodal-decisions), [SDK Python](https://openrouter.ai/docs/client-sdks/python/sdks/decisions/README). Klucz `OPENROUTER_API_KEY` jest przygotowany w środowisku VM; sprawdzaj tylko obecność. Pierwsze zdjęcie i request do capture wlicz do przydziału; potem kontynuuj małą próbkę.

**Prompt:**

~~~text
Przeczytaj AGENTS.md, docs/PRD.md, docs/ADR/, docs/plan.md, app/ i README danych map-qa. Zrealizuj tylko etap Decisions: openai/gpt-6-luna-decisions i typesafe/jev-1.14 przez transport OpenRouter z ADR, nie natywny klient OpenAI. Sprawdź aktualną dokumentację i przypnij wersję SDK. Pytania wyłącznie z PRD. Do state trafia tylko neutralny tekst i obraz jako data URL; nigdy etykiety, nazwy plików, atrybuty mapy ani detekcje. Nie loguj base64 ani sekretów.

Najpierw testy walidacji, limitu, cache i abstencji. Pokaż manifest próbki i maksymalną liczbę żądań, poczekaj na moją zgodę i przydział budżetu przed pierwszym wywołaniem. Limit obejmuje pierwszą próbę i błędy: najwyżej 25 Luna + te same 5 zdjęć Jev, mniej według przydziału. Zero automatycznych retry, także w SDK; timeout 40 s. Po błędzie przerwij płatną pętlę. Pierwszy rzeczywisty request w limicie wykonaj przed mockiem i zachowaj bezpieczny capture: status, nagłówki bez sekretów, pełna odpowiedź, data, endpoint, wersja SDK. Bez dostępu zgłoś brak pomiaru. Cache: hash obrazu + model + wersja pytań, w ignorowanym course-materials/exercise-data/map-qa/data/.

Etykiety reference_labels.csv czyta wyłącznie ewaluator. Accuracy przed abstencją i po niej licz tylko dla etykiet certain danego pytania, z jawnymi mianownikami; pustych nie zamieniaj na none. Pokaż coverage, abstencje, błędy i licznik żądań dla każdego modelu i pytania. Podziel próbkę po sequence; progi ustal przed pomiarem. Porównuj te same obrazy i pytania. Uruchom testy i CLI, pokaż niezgodności do ręcznego przeglądu. Nie edytuj mapy ani nie twórz UI.
~~~

**Sprawdź sam:**

- Obejrzyj zdjęcie, pełny rozkład i decyzję kodu; model nie otrzymał mapy ani etykiety.
- Licznik obejmuje pierwszą próbę i błędy, ponowne uruchomienie korzysta z cache.
- Modele porównujesz na tej samej piątce, a metryki mają jawne mianowniki.

**Jeśli utkniesz:** przy 401/402/429 lub przekroczeniu czasu 40 s zatrzymaj płatne wywołania, zachowaj bezpieczny kod błędu i pracuj na cache z opisem źródła.

**Rozszerzenie:** porównaj progi na zapisanych rozkładach bez kolejnych wywołań.

## M7. Przygotuj raport Markdown i HTML

**Cel:** przekazać analitykowi dowody do ręcznej kontroli. **Agent: Codex.**

**Prompt:**

~~~text
Przeczytaj AGENTS.md, PRD, ADR, plan i reports/map-qa/. Najpierw testy, potem raport Markdown i statyczny HTML z zapisanych wyników, bez nowych wywołań API. Pokaż kandydatów, identyfikatory, daty, atrybuty mapy, odczyt zdjęcia, decyzję kodu, dystans z CRS i liczniki wyłączeń. Oddziel obserwacje, etykiety, predykcje, abstencję i brak modelu. Dodaj miniatury z autorem, źródłem i licencją. Zero kandydatów jest dopuszczalne.

HTML ma działać lokalnie bez serwera, ze względnymi ścieżkami obrazów. Escapuj niezaufany tekst; nie osadzaj sekretów ani base64. Uruchom testy i CLI, otwórz HTML i prześledź jeden wiersz od wejść do decyzji. Sprawdź obrazy, atrybucje, polskie znaki i zgodność liczników z Markdown. Pokaż polecenie, ścieżki, zrzut raportu i diff.
~~~

**Sprawdź sam:**

- Otwórz HTML i prześledź jeden wiersz od zdjęcia przez drogę do decyzji.
- Porównaj liczniki HTML, Markdown i wejść.

**Jeśli utkniesz:** ogranicz raport do jednego sprawdzalnego kandydata; zachowaj atrybucję i wyjaśnienie niepewności.

**Rozszerzenie: dwa niezależne review.** Wstrzymaj edycje i przekaż obu agentom ten sam zakres diffu od commitu zapisanego po M4b oraz PRD, ADR i plan.
W Claude Code zleć jednemu subagentowi review tylko do odczytu (albo użyj świeżej sesji), a w Codex CLI uruchom `/review` dla tego samego zakresu.
Poproś o plik i linię, skutek, dowód i sposób sprawdzenia; bez edycji i płatnego API. Porównaj uwagi w tabeli: problem, agent, dowód, Twoja decyzja.
Dla potwierdzonej uwagi najpierw dodaj test, potem popraw kod i ponów CLI; jeśli uwag brak, zapisz to bez wymyślania błędu.
