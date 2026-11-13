# Jira: od zgłoszeń do konfiguracji jobów

W 45 minut przygotujesz po jednym YAML na zamówienie mapowe i raport problemów do decyzji człowieka. Odczytasz snapshot 40 zgłoszeń Jira, 5 stron Confluence, 10 PR-ów GitHub i 10 PR-ów Bitbucket (9 z repozytorium pipeline, 1 z obcego repozytorium). W Jira masz 7 epiców, 29 tasków, 2 błędy i 2 podzadania. Treść jest syntetyczna, a eksport zanonimizowany. Pracujesz tylko do odczytu, bez uruchamiania przetwarzania ani zapisu do usług.

Ćwiczenie wykonasz samodzielnie na swoim komputerze, bez prowadzącego, konta Jira i wspólnego tokenu. Otwórz PowerShell 5 lub 7. Potrzebujesz Git, uv, Pythona 3.12, klonu tego repozytorium i własnego dostępu do Claude Code albo Codex CLI. Pozostań w katalogu głównym repozytorium; dostosuj literę dysku do swojego klonu.

```powershell
Set-Location D:\jsystems-claude-codex-gis-2026-11
```

| Etap | Czas | Wynik |
|---|---|---|
| J0 | 5 min | Odczyt A-offline lub C, opcjonalnie A/B |
| J1 | 15 min | `jobs/<klucz-zamówienia>.yaml` i `issues.md` z jednego promptu |
| J2 | 10 min | Analiza ze skillem i kontrola pięciu zamówień |
| J3 | 15 min | Powiązania PR i Confluence z Jira, `links.csv` i `links.md` |
| J4, opcjonalnie | poza limitem | Porównanie modeli na tym samym zakresie |

## J0. Wybierz ścieżkę odczytu

Porównaj [cztery sposoby połączenia agenta z Atlassian](../../Research/atlassian-agents-mcp-plugins-skill-2026-11.md): connector, plugin, MCP i skill z API.

Zacznij od A-offline, aby pracować skryptem CLI bez konta i tokenu, albo C, aby przećwiczyć MCP na tych samych danych. A i B są opcjonalne: wymagają twojego konta Jira Cloud i projektu, do którego masz prawo dostępu. Nie używaj dawnych tokenów szkoleniowych. Dla firmowego Server/DC zobacz osobne konfiguracje MCP; czytnik live w tym ćwiczeniu obsługuje Cloud, a skill Server/DC nie zastępuje go bez dostosowania.

Przeczytaj [kontrakt danych](../../exercise-data/jira-jobs/README.md) i [schemat v2](../../exercise-data/jira-jobs/job-params.schema.json). Nie edytuj wejść. Zakończ poprzednią sesję przed zmianą agenta, aby dwa procesy nie pisały tego samego raportu. Internet jest potrzebny do instalacji bibliotek i działania agenta; lokalne narzędzia odczytują zgłoszenia bez sieci.

### A-offline. Ten sam CLI, bez tokenu

Włącz tryb offline w bieżącym PowerShell. Agent uruchomiony z tego okna odziedziczy ustawienie.

```powershell
$env:JIRA_OFFLINE = "1"
```

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py search "project = TEST ORDER BY key"
```

Oczekujesz 40 kluczy, TEST-1..TEST-40. Pobierz epic, jego komentarze i bezpośrednie dzieci.

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py get TEST-1
```

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py comments TEST-1
```

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py search "parent = TEST-1 ORDER BY key"
```

Podzadanie z bbox znajdziesz przez dalszy odczyt taska i `parent = TEST-8`. Lista `Dzieci` obejmuje bezpośrednie dzieci, nie całe drzewo. Aby szukać dowodów poza hierarchią, użyj pełnej kolejki i wyszukiwania tekstowego, także w komentarzach.

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py search 'project = TEST AND text ~ "SL-461"'
```

Zamiast zmiennej środowiskowej możesz podać `--offline` przed podkomendą.

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py --offline search "project = TEST AND issuetype = Epic ORDER BY key"
```

Lokalny podzbiór JQL obsługuje `project`, `labels`, `status`, `issuetype`, `parent`, `key` z `=`, `text` z `~`, łączenie przez `AND` i `ORDER BY key` z opcjonalnym `ASC` lub `DESC`. Nie obsługuje OR, funkcji JQL ani pełnej składni serwera Jira; nieobsługiwane zapytanie zgłasza błąd. Odczyt `get` pokazuje rodzica, dzieci i linki, a `comments` pełną treść komentarzy. Używaj tych poleceń, zamiast otwierać pliki JSON.

### A. Własna Jira Cloud przez API, opcjonalnie

Wybierz A tylko dla własnego konta i dozwolonego projektu. Utwórz osobisty token z minimalnymi zakresami odczytu w panelu konta Atlassian. Zastąp `TEST` i przykładowe klucze wartościami swojego projektu. Nie zakładaj, że twoja Jira zawiera 40 zgłoszeń z tego ćwiczenia: oczekiwane odpowiedzi i samokontrola dotyczą wyłącznie snapshotu. Do porównania z nimi wróć do A-offline lub C. Tryb live jest domyślny; wyłącz ustawienie offline.

```powershell
Remove-Item Env:JIRA_OFFLINE -ErrorAction SilentlyContinue
```

```powershell
$env:JIRA_BASE_URL = "https://twoja-strona.atlassian.net"
```

```powershell
$env:JIRA_EMAIL = Read-Host "E-mail właściciela tokenu Jira Cloud"
```

```powershell
$env:JIRA_CLOUD_ID = (Invoke-RestMethod -Uri "$env:JIRA_BASE_URL/_edge/tenant_info").cloudId
```

Wpisz token w ukryte pole. Nie zapisuj go w promptach, plikach i historii poleceń. Zmienna zawiera token tylko w pamięci bieżącej sesji; nie proś agenta o jej wypisanie.

```powershell
$jiraSecureToken = Read-Host "Token" -AsSecureString
```

```powershell
$env:JIRA_API_TOKEN = [System.Net.NetworkCredential]::new("", $jiraSecureToken).Password
```

Używaj tych samych poleceń `search`, `get`, `comments` co w A-offline. CLI pobiera wszystkie strony wyszukiwania i komentarzy. W live zapytania wykonuje Jira i dostępna jest jej pełna składnia JQL. `get` pokazuje pola rodzica i podzadań; taski epika wyszukaj dodatkowo przez `parent = <klucz>`. Nie zakładaj, że `subtasks` zawiera wszystkie dzieci epika.

Po ustawieniu `JIRA_CLOUD_ID` klient korzysta z bramy `https://api.atlassian.com/ex/jira/{cloudId}`. Bez tej zmiennej używa `JIRA_BASE_URL`. Potrzebujesz uprawnień właściciela tokenu do projektu i odpowiednich zakresów odczytu. Odczyt odmawia POST, DELETE i endpointów poza wyszukiwaniem, zgłoszeniami i komentarzami. Błędy 401/403 wymagają sprawdzenia dostępu i zakresów tokenu; 429 oznacza limit. Jeśli nie możesz rozwiązać problemu z administratorem, wróć do A-offline lub C. Nie potrzebujesz dostępu live do ukończenia ćwiczenia.

### B. Rovo MCP na własnym koncie, opcjonalnie

Jeśli masz własne konto z dostępem do dozwolonego projektu Cloud, możesz połączyć oficjalny endpoint Rovo MCP przez OAuth. Wykonaj polecenie dla swojego klienta przed nową sesją. [Przykładowe konfiguracje](../../agent-configs/mcp-atlassian/README.md) wyjaśniają osobne konta, zakresy konfiguracji i alternatywę Server/DC.

```powershell
claude mcp add --transport http --scope local atlassian-oauth https://mcp.atlassian.com/v2/mcp
```

W Claude Code uwierzytelnij połączenie przez `/mcp`. Dla Codex:

```powershell
codex mcp add atlassian-oauth --url https://mcp.atlassian.com/v2/mcp
```

```powershell
codex mcp login atlassian-oauth
```

Sprawdź katalog narzędzi i rzeczywisty odczyt, nie tylko status połączenia. Szukaj `searchJiraIssuesUsingJql`, `getJiraIssue`, `listJiraIssueComments` albo aktualnych odpowiedników odczytu. Pobierz wszystkie strony. OAuth może udostępniać zapis, ale w ćwiczeniu wybierasz wyłącznie odczyt. Nie potrzebujesz tego połączenia do A-offline ani C.

### C. Lokalny serwer MCP

Serwer korzysta z tego samego snapshotu co A-offline. Nie używa konta ani tokenu i nie łączy się z Jira. Dodaj go w swoim kliencie, dopasowując ścieżkę Windows.

```powershell
claude mcp add --transport stdio --scope local jira-jobs -- uv run --with mcp "D:\jsystems-claude-codex-gis-2026-11\course-materials\exercises\jira-mcp\server.py"
```

Dla Codex:

```powershell
codex mcp add jira-jobs -- uv run --with mcp "D:\jsystems-claude-codex-gis-2026-11\course-materials\exercises\jira-mcp\server.py"
```

Uruchom nową sesję. Wpisz `/mcp` i sprawdź osiem narzędzi: `search_tickets`, `get_ticket`, `list_comments`, `search_pages`, `get_page`, `list_prs`, `get_pr`, `get_remote_links`. Wywołaj `search_tickets` z pustym `query`, następnie pozostałe narzędzia dla TEST-1. Oczekujesz 40 kluczy. Wyszukiwanie MCP dopasowuje wszystkie słowa bez rozróżniania liter, także w komentarzach i kluczach hierarchii. `status` dopasowuje dokładną nazwę. To nie jest JQL.

`get_ticket` pokaże dzieci TEST-1. Otwórz każde dziecko, potem podzadania. Sprawdź też linki i wyszukaj numer źródłowy w całej kolejce. Parametry mogą być w zadaniu bez parenta i bez linku.

W razie problemu sprawdź ścieżkę oraz `uv --version` w tym samym PowerShell. Testy narzędzi:

```powershell
uv run --with mcp --with httpx --with pytest pytest course-materials/exercises/jira-mcp -q
```

## J1. Szybki prompt bez skilla

Zastąp `[ścieżka]` przez A-offline, A, B lub C. Masz zgodę na wskazane materiały kursowe i zapis wyników. Jednorazowy odczyt i raport nie wymagają PRD aplikacji; powtarzalny system lub uruchamianie jobów to osobne zadanie.

~~~text
Pracuj ścieżką [ścieżka], tylko do odczytu. Możesz przeczytać README.md i job-params.schema.json z course-materials/exercise-data/jira-jobs/ oraz instrukcję wybranego narzędzia w course-materials/exercises/jira-mcp/README.md. Nie czytaj bezpośrednio tickets.json, issue-example.json, confluence-pages.json, github-prs.json, bitbucket-prs.json, remote-links.json, seed-spec.json, testów, klucza odpowiedzi ani wcześniejszych wyników. Dane pobieraj przez jira_read.py lub narzędzia MCP tej ścieżki. Nie instaluj jeszcze skilla.
Odkryj wszystkie zgłoszenia bez filtra statusu. Zrekonstruuj każde zamówienie przez epic, jego taski, podzadania, linki i wszystkie komentarze. Wyszukaj także dowody bez parenta lub linku po numerze źródłowym i tytule. Nie traktuj każdego ticketu jako osobnego joba.
Zapisz jeden YAML na zamówienie w reports/jira-jobs/jobs/<klucz-zamówienia>.yaml oraz reports/jira-jobs/issues.md. YAML: job_id, region, area_name, bbox, layers, data_release, start_step, steps, output_format, output_path, deadline, requester_team, notes i unknown_reasons, zgodnie ze schematem v2. job_id to klucz epika, a dla nowego samodzielnego zamówienia klucz jego zgłoszenia. Zachowaj kandydata będącego możliwym duplikatem, ale oznacz HOLD w notes i raporcie; nie zatwierdzaj dwóch runów. Braki i nierozstrzygnięte konflikty to null z powodem. Jawny brak bbox dla całego regionu też wyjaśnij. Cytuj dowody dla korekt i nie przenoś ich automatycznie między zamówieniami. Release i daty zapisz jako napisy w cudzysłowach.
W issues.md rozróżnij duplikaty, podobne odrębne zamówienia, konflikty, jawne nadpisania, braki, historyczne wartości i szum ignore_non_job. Przy każdym problemie podaj klucz zamówienia i źródła, pole, cytat, opis lub ID i datę komentarza, proponowaną wartość, pewność z uzasadnieniem oraz pytanie do człowieka. Wyjaśnij rolę każdego odkrytego klucza: zamówienie, dowód albo szum.
Zwaliduj każdy YAML względem schematu, daty kalendarzowe, bbox i kolejność steps od start_step. Uruchom walidator validate_jobs.py zgodnie z README. W snapshocie oczekujesz 40 zgłoszeń: 7 zamówień pod epicami oraz 2 samodzielne nowe zamówienia wymagające potwierdzenia. Zachowaj 9 szkiców, także HOLD/BLOCKED; błędy uruchomień i kontrola dzienna nie tworzą jobów. Ręcznie sprawdź pięć zamówień wraz z dowodami. Zgłoś braki dostępu i niepełne strony bez domysłów. Nie zmieniaj Jira ani aplikacji i nie uruchamiaj Databricks ani pipeline.
~~~

Walidator sprawdza format, daty i reguły między polami. Nie weryfikuje prawdziwości dowodów ani intencji zamawiającego i nie stanowi zgody na wykonanie.

```powershell
uv run --with pyyaml --with jsonschema course-materials/exercises/jira-mcp/validate_jobs.py reports/jira-jobs/jobs
```

## J2. Ta sama praca ze skillem

Zachowaj wynik J1 w nowym katalogu przed kolejną próbą. Jeśli katalog docelowy już istnieje, wybierz nową nazwę.

```powershell
Copy-Item -Recurse reports/jira-jobs reports/jira-jobs-j1
```

Zainstaluj wyłącznie kursowy skill ze źródła w tym repozytorium. Zachowaj inne skille i sprawdź istniejący katalog przed kopiowaniem. Dla Claude Code:

```powershell
New-Item -ItemType Directory -Force .claude/skills | Out-Null
```

```powershell
Copy-Item -Recurse course-materials/exercises/jira-mcp/skill/jira-jobs-triage .claude/skills/
```

Dla Codex:

```powershell
New-Item -ItemType Directory -Force .agents/skills | Out-Null
```

```powershell
Copy-Item -Recurse course-materials/exercises/jira-mcp/skill/jira-jobs-triage .agents/skills/
```

Uruchom świeżą sesję z tego samego PowerShell i użyj promptu:

~~~text
Użyj skilla jira-jobs-triage. Pracuj wybraną wcześniej ścieżką A-offline, A, B lub C. Masz zgodę na wskazane materiały kursowe oraz zapis reports/jira-jobs/jobs/<klucz-zamówienia>.yaml, reports/jira-jobs/issues.md i reports/jira-jobs/links.csv. Nie czytaj wyników J1 ani istniejących konfiguracji: wygeneruj je ponownie na podstawie narzędzi. Zastosuj pełne wyszukiwanie epic + dzieci + podzadania + linki + komentarze oraz dowody spoza hierarchii. Odczytaj stronę Konwencje parametrów zleceń przez pages/page lub search_pages/get_page, zastosuj ją do normalizacji i sprawdź PR-y. Powiązania zapisz według kontraktu J3. Nie zmieniaj Jira ani aplikacji. Zwaliduj YAML i na końcu podaj zastosowane instrukcje oraz decyzje potrzebne od człowieka.
~~~

Porównaj J1 i J2: kompletność dowodów, korekty parametrów, rozpoznanie duplikatu i odróżnienie identycznych nazw różnych obszarów. Sprawdź ręcznie pięć zamówień wraz z ich komentarzami i dziećmi. Zapisz różnice w `reports/jira-jobs/comparison-j1-j2.md`. Użycie skilla samo nie dowodzi lepszego wyniku.

## J3. Powiązania: PR i strony Confluence - Jira

Jira, Confluence, GitHub i Bitbucket odczytujesz jako osobne źródła. Snapshot zawiera już cztery linki zewnętrzne Jira do Bitbucket, w tym jeden błędny; nie zakładaj kompletnej integracji ani poprawności linku. Zbierz dowody przez narzędzia i przygotuj propozycje odnośników. W A/B możesz zachować odczyt Jira live; strony i PR-y tego ćwiczenia odczytaj lokalnie z `--offline`, z kluczami TEST. Nie mieszaj ich z innym projektem bez uzgodnionego mapowania.

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline pages
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline page 220135425
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline prs
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline pr 10
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline prs --source bitbucket
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline pr 9 --source bitbucket
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline remotelinks TEST-13
```

```powershell
uv run course-materials/exercises/jira-mcp/jira_read.py --offline pr 1 --source bitbucket --repo ai-php-course-08-2026
```

`pages` i `prs` przyjmują tekst wyszukiwania po wszystkich słowach, bez rozróżniania liter. `--source github` jest domyślne; `--source bitbucket` zwraca też PR z obcego repozytorium. Numer PR jest lokalny dla repozytorium: `pr N --source bitbucket` wybiera `map-data-jobs-pipelines`, a `--repo` wskazuje inne. Lista pokazuje URL rozróżniający repozytoria. W MCP użyj `search_pages`, `get_page`, `list_prs(query, source, repo)`, `get_pr(number, source, repo)` i `get_remote_links(key)`. GitHub ma diffy plików; Bitbucket w tym zestawie ma opisy, gałęzie, commity i komentarze, bez osobnego zasobu diff. Brakującej treści YAML nie odtwarzaj z domysłów.

Limit J3 pozostaje 15 minut. Odkryj pełne listy, potem skup analizę na poprawnym istniejącym linku, linku na niewłaściwym tickecie, kluczu tylko w gałęzi/commicie, literówce i PR z obcego repozytorium. Uwzględnij także dowód GitHub i stronę Confluence. Pięć najtrudniejszych wzmianek sprawdź ręcznie; pozostałe nieprzeczytane źródła wymień jako luki pokrycia.

~~~text
Pracuj tylko do odczytu przez narzędzia wybranej ścieżki. Masz zgodę na README ćwiczenia, kontrakt danych i zapis raportów. Nie czytaj bezpośrednio snapshotów JSON, testów, seed-spec ani klucza odpowiedzi. Odkryj wszystkie 40 zgłoszeń, 5 stron, 10 PR-ów GitHub i 10 PR-ów Bitbucket, bez filtra statusu. W limicie J3 wybierz przypadki opisane powyżej i odczytaj ich szczegóły oraz wszystkie komentarze. Pobierz istniejące linki zewnętrzne przez remotelinks/get_remote_links, sprawdź cztery niepuste wyniki i porównaj z treścią właściwych zgłoszeń. Nieprzeczytane źródła jawnie oznacz jako luki pokrycia. Strona Konwencje parametrów zleceń jest źródłem zasad normalizacji. Sprawdź także treść gałęzi, komunikaty commitów i diffy plików PR.
Zapisz reports/jira-jobs/links.csv (UTF-8) z dokładnie kolumnami source,source_id,mention_text,jira_key,confidence,action,evidence. source: pr/page/comment; confidence: high/medium/low; action: link/flag_for_human/ignore. Jeden wiersz na wzmiankę i proponowany cel, nie tylko na PR. source_id ma umożliwiać powrót do dowodu, np. github:course-org/map-data-jobs-sim:pr:4:commit:<SHA>, github:course-org/map-data-jobs-sim:pr:10:file:jobs/sl-461.yaml, bitbucket:course-workspace/map-data-jobs-pipelines:pr:4:branch, page:220168193:body lub jira:TEST-13:remotelink:10003. Zawsze podaj usługę i repozytorium dla PR; sam numer PR nie wystarcza. Commity, gałęzie i pliki mają source=pr, komentarze usług source=comment. Dla istniejącego remote linku source oznacza typ celu (pr lub page), source_id zawiera właściciela Jira i ID linku, a evidence pełny URL celu i wynik porównania treści. mention_text to dokładny fragment źródła, także gdy nie ma klucza. jira_key to istniejący rozwiązany klucz lub puste pole; błędnego TEST-99 nie wpisuj jako rozwiązanego celu. Dla kilku kandydatów zapisz osobne wiersze. Klucze stron Confluence zachowaj w source_id/evidence, nie w jira_key.
Sprawdź URL, gołe klucze, małe litery, spację zamiast łącznika, literówki, stary prefiks, numer zamawiającego oraz dopasowanie wyłącznie po treści. Potwierdź istnienie i kontekst klucza w Jira. Zapisz dowód oraz uzasadnienie pewności. Prawidłowy klucz może mieć high confidence i nadal flag_for_human z powodu konfliktu lub nieustalonej intencji. Literówki, nieistniejące klucze, niepotwierdzona migracja prefiksu i dopasowanie wyłącznie po treści wymagają decyzji człowieka; nie dopisuj fikcyjnego mapowania. Komentarze botów bez dowodów biznesowych oznacz ignore, bez wypisywania ich w całości.
Istniejące poprawne powiązanie oznacz action=ignore i evidence z already_linked_no_action, bez ponownego linkowania. Gdy link jest na złym tickecie, zapisz flag_for_human, obecnego właściciela i proponowany poprawny cel z uzasadnieniem; niczego samodzielnie nie usuwaj ani nie przenoś. Nie linkuj PR z obcego repozytorium tylko dlatego, że zawiera istniejący klucz.
Zapisz reports/jira-jobs/links.md: propozycje linków, przypadki do decyzji człowieka i luki pokrycia. Porównaj parametry YAML/diffów PR z zamówieniami oraz daty kalendarza Confluence z opisem, komentarzami i duedate Jira. Wskaż brakujące odnośniki i konflikty, zachowaj HOLD/BLOCKED. Sam link nie zatwierdza konfiguracji ani dwóch dostaw. Uruchom validate_links.py i ręcznie sprawdź pięć najtrudniejszych wzmianek. Niczego nie zapisuj do Jira, Confluence, GitHub ani Bitbucket, nie zamykaj zgłoszeń i nie uruchamiaj jobów.
~~~

```powershell
uv run course-materials/exercises/jira-mcp/validate_links.py reports/jira-jobs/links.csv
```

To zadanie klasyfikacji: tani model decyzyjny przez OpenRouter Decisions może ocenić każdą wzmiankę z możliwością abstencji, a agent zbiera kontekst i przygotowuje kandydatów. Kod sprawdza istnienie kluczy i kontrakt wyniku, a człowiek rozstrzyga niepewne dopasowania oraz konflikty.

### J3 Decisions. Opcjonalna próba na własnym koncie

Podstawowe J3 nie wykonuje płatnych wywołań. Ten dodatek wykonaj poza limitem 45 minut, tylko jeśli świadomie wybierasz własne konto OpenRouter z dostępnym modelem Decisions i kluczem w odziedziczonej zmiennej `OPENROUTER_API_KEY`. Nie korzystaj ze wspólnego tokenu ani budżetu szkoleniowego. [Dokumentacja Decisions](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request) opisuje surowy `POST https://openrouter.ai/api/alpha/decisions`, pytania Choice i odpowiedź `answers.<id>.probabilities`; to osobny endpoint, nie Chat Completions. Dokumentacja pokazuje `typesafe/jev-1.13`; dostępność i koszt na twoim koncie trzeba sprawdzić przed wyborem próby.

Sprawdź jedynie obecność klucza w bieżącym PowerShell, bez odczytu plików sekretów:

```powershell
[bool]$env:OPENROUTER_API_KEY
```

Jeśli wynik to `False`, pomiń wariant płatny i porównaj raport z samokontrolą. Jeśli to `True` i chcesz wykonać próbę na własny koszt, wklej poniższy prompt do agenta. Obejmuje przygotowanie i wykonanie maksymalnie pięciu żądań, bez dodatkowej próby technicznej. Przed uruchomieniem przeczytaj przygotowany manifest i kod klienta.

~~~text
Wykonaj opcjonalną próbę J3 Decisions na moim własnym koncie OpenRouter. Budżet: maksymalnie 5 żądań POST łącznie w tej próbie, wliczając pierwszy capture, timeouty i błędy; jedno żądanie na wzmiankę i jednego kandydata. Nie wykonuj dodatkowego testowego wywołania, retry ani zamiany modelu. Wznowienie nie zeruje licznika. Po błędzie HTTP, sieciowym, walidacji odpowiedzi lub braku wymaganych prawdopodobieństw przerwij całą płatną pętlę.
Najpierw przeczytaj bieżący oficjalny kontrakt OpenRouter Decisions. Użyj modelu typesafe/jev-1.13, surowego POST https://openrouter.ai/api/alpha/decisions i klienta Python httpx bez SDK i bez automatycznych retry; timeout 40 s, follow_redirects=False. Nie wykonuj płatnych wywołań, jeśli kontrakt lub dostępność modelu nie są potwierdzone. Nie czytaj pliku samokontroli przed zapisaniem wyników. Wejścia czytaj wyłącznie przez lokalne narzędzia ćwiczenia, nie bezpośrednio z JSON ani testów.
Przygotuj w reports/jira-jobs/decisions/ manifest pięciu par: GitHub course-org/map-data-jobs-sim PR 5 i kandydat z literówki; GitHub PR 9 i kandydat po treści; GitHub PR 10 i jeden z dwóch kluczy; Bitbucket course-workspace/map-data-jobs-pipelines PR 9 i kandydat wynikający z treści; Bitbucket course-workspace/ai-php-course-08-2026 PR 1 i wspomniany klucz. Zapisz source_id, dokładną wzmiankę, kandydata, dowody i wcześniejszą ocenę agenta przed API. Odczytaj również właściwe tickety, komentarze, istniejące remote linki i dostępne diffy. Nie dopowiadaj brakujących plików.
W każdym request użyj questions.relation.type="choice" oraz identycznych instructions: "Czy praca opisana w source dotyczy tego samego zamówienia i zakresu co candidate?". criteria: same_work="Źródło i kandydat dotyczą tego samego zamówienia i zakresu pracy."; different_work="Źródło opisuje inne zamówienie lub inny zakres pracy niż kandydat."; insufficient_evidence="Dostępna treść nie rozstrzyga, którego zamówienia i zakresu dotyczy źródło.". State to obiekt source i candidate z treścią potrzebną do tej oceny oraz kontekstem repozytorium i parametrów. Wysyłaj tylko dane syntetyczne, bez klucza odpowiedzi, wcześniejszych etykiet agenta, prawdziwej poczty i danych osób.
Klucz odczytaj wyłącznie z os.environ["OPENROUTER_API_KEY"]. Nie czytaj żadnego pliku sekretów, nie loguj nagłówka Authorization i nie wypisuj wartości klucza. Zapisz manifest i klienta decyzji, potem pokaż ich ścieżki oraz pięć par do mojego przeglądu przed płatnym wykonaniem.
Licznik prób zapisz na dysku przed każdym POST; przerwij, jeśli wynosi już 5, także po ponownym uruchomieniu. Pierwsze żądanie jest zarazem capture: zapisz datę, endpoint, wersję httpx, bezpieczny request bez nagłówka Authorization, status, nagłówki odpowiedzi po usunięciu wartości sekretów i pełny syntetyczny body. Nie twórz mocka przed capture. Nie drukuj surowych błędów, które mogłyby ujawnić nagłówki żądania. Każdy wynik zapisz z model/provider/id, questions, answers, confidence, probabilities, czasem i usage.cost; brak kosztu oznacz null, nie zero. Podaj koszt zmierzony oraz liczbę prób bez pomiaru kosztu.
Polityka próby ustalona przed pomiarem: abstain i flag_for_human, jeśli wygrywa insufficient_evidence, max(probabilities)<0.85 lub różnica dwóch największych prawdopodobieństw<0.20. Brak rozkładu lub błędna odpowiedź oznacza model_unavailable i przerwanie, nigdy zgodę na link. Model ocenia związek semantyczny, a nie pozwolenie na zmianę. Niezależnie od prawdopodobieństw literówki, migracja prefiksu, dopasowanie tylko po treści, błędny istniejący link, konflikt parametrów i nieustalona intencja dostawy pozostają flag_for_human. Poprawny istniejący link to ignore/already_linked_no_action; obce repozytorium nie dostaje linku przez sam zgodny klucz.
Po mojej decyzji o wykonaniu uruchom przygotowanego klienta dokładnie raz. Zapisz comparison.md z oceną agenta, odpowiedzią modelu i decyzją po zastosowaniu reguł dla każdej pary. Dopiero po zapisaniu wyników otwórz plik samokontroli i porównaj z sekcjami GitHub, Bitbucket oraz Confluence. Policz błędne propozycje linków, poprawne decyzje i abstencje; nie traktuj abstencji jako fałszywej pewności ani pięciu przykładów jako kalibracji produkcyjnej. Nie zmieniaj progów po obejrzeniu odpowiedzi. Niczego nie zapisuj do usług i nie uruchamiaj jobów.
~~~

Próg `0.85` i margines `0.20` to polityka tej demonstracji, a nie gwarancja jakości modelu. Różnica między oceną związku a propozycją linku jest zamierzona: model może rozpoznać wspólną pracę, a kod nadal musi zachować `flag_for_human` przy konflikcie lub brakującej decyzji.

## J4. Opcjonalne porównanie modeli

Wybierz tańszy i mocniejszy model dostępny na koncie przez `/model`. W dwóch świeżych sesjach użyj identycznego promptu J1 i tej samej ścieżki. Nie pokazuj drugiemu modelowi pierwszego wyniku. Zapisz wyniki w nowych katalogach `reports/jira-jobs-comparison/cheap` i `reports/jira-jobs-comparison/strong`.

Ręcznie oceń pięć tych samych zamówień: TEST-1..TEST-5 wraz z pełnym drzewem i dowodami spoza hierarchii, potem porównaj je ze [Sprawdź się](./SPRAWDZ-SIE.md). W live samodzielnie wybierz i zapisz równoważny zakres własnego projektu; nie porównuj go z odpowiedziami snapshotu. Oceniaj 12 pól poza job_id, maksymalnie 60 punktów; notes jako jedno pole. Sprawdź osobno job_id, liczbę plików i unknown_reasons. `null` jest poprawny tylko z właściwym powodem. Nie porównuj samych tytułów ani statusów.

Zapisz dokładne nazwy modeli, czas i dostępny pomiar zużycia. `/context` w Claude Code lub `/status` w Codex może pokazywać wielkość kontekstu albo limit konta, nie zużyte tokeny; zachowaj nazwę i jednostkę pomiaru z ekranu. Jeśli zużycie nie jest dostępne, napisz to. Nie potrzebujesz dodatkowego płatnego API.

## Samokontrola i zakończenie

Zachowaj swój pierwszy raport, zanim otworzysz [Sprawdź się](./SPRAWDZ-SIE.md). Plik zawiera spoilery: oczekiwane ustalenia dla dziewięciu zamówień, zasiane problemy oraz decyzje o linkach. Porównaj parametry i dowody, nie tylko wynik walidatora. Poprawki zapisz jako osobny wynik z krótkim uzasadnieniem różnic. Ćwiczenie jest ukończone, gdy masz YAML-e i oba raporty, jawne HOLD/BLOCKED oraz rozumiesz pięć ręcznie sprawdzonych przypadków.

Nie zapisuj tokenów, surowych eksportów ani mapowania kont w repozytorium. W A używaj wyłącznie dozwolonego projektu, ponieważ token sam nie ogranicza dostępu do tego projektu. Po ćwiczeniu wyczyść zmienne w bieżącej sesji.

```powershell
Remove-Item Env:JIRA_API_TOKEN,Env:JIRA_EMAIL,Env:JIRA_CLOUD_ID,Env:JIRA_BASE_URL,Env:JIRA_OFFLINE -ErrorAction SilentlyContinue
```

```powershell
Remove-Variable jiraSecureToken -ErrorAction SilentlyContinue
```

`sanitize_export.py` i `seed_jira.py` nie są potrzebne do samodzielnego ćwiczenia. Ten drugi obsługuje dawny płaski format, nie hierarchię v2; nie odtwarzaj nim tej kolejki. Dane wejściowe pozostają bez zmian.

Źródła: [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/), [ADF](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/), [Rovo MCP](https://developer.atlassian.com/cloud/rovo-mcp/), [Claude Code MCP](https://code.claude.com/docs/en/mcp), [Codex MCP](https://developers.openai.com/codex/mcp/).
