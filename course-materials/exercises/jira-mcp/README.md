# Jira: od zgłoszeń do konfiguracji jobów

W 45-60 minut przygotujesz po jednym YAML na zamówienie mapowe i raport problemów do decyzji człowieka. Odczytasz snapshot 34 rzeczywistych zgłoszeń Jira: 7 epiców, 25 tasków i 2 podzadania. Treść jest syntetyczna, a eksport zanonimizowany. Pracujesz tylko do odczytu, bez uruchamiania przetwarzania.

Na VM Windows otwórz PowerShell 5 lub 7. Potrzebujesz uv, Pythona 3.12 i Claude Code albo Codex CLI. Pozostań w katalogu głównym repozytorium; dostosuj literę dysku do swojego klonu.

```powershell
Set-Location D:\jsystems-claude-codex-gis-2026-11
```

| Etap | Czas | Wynik |
|---|---|---|
| J0 | 5 min | Odczyt A-offline lub C, opcjonalnie A/B |
| J1 | 15 min | `jobs/<klucz-epika>.yaml` i `issues.md` z jednego promptu |
| J2 | 15 min | Ta sama analiza ze skillem i porównanie wyników |
| Kontrola | 10 min | Pięć zamówień sprawdzonych wraz z dowodami |
| J3, opcjonalnie | 15 min | Porównanie dwóch modeli na tym samym zakresie |

## J0. Wybierz ścieżkę odczytu

Wybierz A-offline, aby pracować skryptem CLI bez konta i tokenu, albo C, aby przećwiczyć MCP na tych samych danych. A wymaga osobnego dostępu zapewnionego przez prowadzącego. Nie dostajesz dostępu do prywatnej strony prowadzącego, która zawiera inne projekty. B jest opcją dla własnego konta z dostępem do uzgodnionego projektu.

Przeczytaj [kontrakt danych](../../exercise-data/jira-jobs/README.md) i [schemat v2](../../exercise-data/jira-jobs/job-params.schema.json). Nie edytuj wejść. Zakończ poprzednią sesję przed zmianą agenta, aby dwa procesy nie pisały tego samego raportu. Internet jest potrzebny do instalacji bibliotek i działania agenta; lokalne narzędzia odczytują zgłoszenia bez sieci.

### A-offline. Ten sam CLI, bez tokenu

Włącz tryb offline w bieżącym PowerShell. Agent uruchomiony z tego okna odziedziczy ustawienie.

```powershell
$env:JIRA_OFFLINE = "1"
```

```powershell
uv run --with httpx course-materials/exercises/jira-mcp/jira_read.py search "project = TEST ORDER BY key"
```

Oczekujesz 34 kluczy, TEST-1..TEST-34. Pobierz epic, jego komentarze i bezpośrednie dzieci.

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

### A. Rzeczywista Jira przez API, tylko z dostępem od prowadzącego

Wybierz A tylko wtedy, gdy prowadzący zapewni osobny dozwolony projekt i dane dostępu. Zastąp `TEST` oraz przykładowe klucze wartościami tego projektu. Tryb live jest domyślny; wyłącz ustawienie offline.

```powershell
Remove-Item Env:JIRA_OFFLINE -ErrorAction SilentlyContinue
```

```powershell
$env:JIRA_BASE_URL = "https://twoja-strona.atlassian.net"
```

```powershell
$env:JIRA_EMAIL = "wlasciciel@example.com"
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

Po ustawieniu `JIRA_CLOUD_ID` klient korzysta z bramy `https://api.atlassian.com/ex/jira/{cloudId}`. Bez tej zmiennej używa `JIRA_BASE_URL`. Potrzebujesz uprawnień właściciela tokenu do projektu i odpowiednich zakresów odczytu. Odczyt odmawia POST, DELETE i endpointów poza wyszukiwaniem, zgłoszeniami i komentarzami. Błędy 401/403 wymagają sprawdzenia dostępu; 429 oznacza limit. Zgłoś błąd prowadzącemu, a potem wybierz A-offline lub C.

### B. Rovo MCP na własnym koncie, opcjonalnie

Jeśli masz własne konto z dostępem do uzgodnionego projektu, możesz połączyć oficjalny endpoint Rovo MCP przez OAuth. Wykonaj polecenie dla swojego klienta przed nową sesją.

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

Uruchom nową sesję. Wpisz `/mcp` i sprawdź trzy narzędzia: `search_tickets`, `get_ticket`, `list_comments`. Wywołaj `search_tickets` z pustym `query`, następnie pozostałe narzędzia dla TEST-1. Oczekujesz 34 kluczy. Wyszukiwanie MCP dopasowuje wszystkie słowa bez rozróżniania liter, także w komentarzach i kluczach hierarchii. `status` dopasowuje dokładną nazwę. To nie jest JQL.

`get_ticket` pokaże dzieci TEST-1. Otwórz każde dziecko, potem podzadania. Sprawdź też linki i wyszukaj numer źródłowy w całej kolejce. Parametry mogą być w zadaniu bez parenta i bez linku.

W razie problemu sprawdź ścieżkę oraz `uv --version` w tym samym PowerShell. Testy narzędzi:

```powershell
uv run --with mcp --with httpx --with pytest pytest course-materials/exercises/jira-mcp -q
```

## J1. Szybki prompt bez skilla

Zastąp `[ścieżka]` przez A-offline, A, B lub C. Masz zgodę na wskazane materiały kursowe i zapis wyników. Jednorazowy odczyt i raport nie wymagają PRD aplikacji; powtarzalny system lub uruchamianie jobów to osobne zadanie.

~~~text
Pracuj ścieżką [ścieżka], tylko do odczytu. Możesz przeczytać README.md i job-params.schema.json z course-materials/exercise-data/jira-jobs/ oraz instrukcję wybranego narzędzia w course-materials/exercises/jira-mcp/README.md. Nie czytaj bezpośrednio tickets.json, issue-example.json, seed-spec.json, testów, klucza odpowiedzi ani wcześniejszych wyników. Dane pobieraj przez jira_read.py lub narzędzia MCP tej ścieżki. Nie instaluj jeszcze skilla.
Odkryj wszystkie zgłoszenia bez filtra statusu. Zrekonstruuj każde zamówienie przez epic, jego taski, podzadania, linki i wszystkie komentarze. Wyszukaj także dowody bez parenta lub linku po numerze źródłowym i tytule. Nie traktuj każdego ticketu jako osobnego joba.
Zapisz jeden YAML na zamówienie w reports/jira-jobs/jobs/<klucz-epika>.yaml oraz reports/jira-jobs/issues.md. YAML: job_id, region, area_name, bbox, layers, data_release, start_step, steps, output_format, output_path, deadline, requester_team, notes i unknown_reasons, zgodnie ze schematem v2. job_id to klucz epika. Zachowaj kandydata będącego możliwym duplikatem, ale oznacz HOLD w notes i raporcie; nie zatwierdzaj dwóch runów. Braki i nierozstrzygnięte konflikty to null z powodem. Jawny brak bbox dla całego regionu też wyjaśnij. Cytuj dowody dla korekt i nie przenoś ich automatycznie między zamówieniami. Release i daty zapisz jako napisy w cudzysłowach.
W issues.md rozróżnij duplikaty, podobne odrębne zamówienia, konflikty, jawne nadpisania, braki, historyczne wartości i szum ignore_non_job. Przy każdym problemie podaj klucz zamówienia i źródła, pole, cytat, opis lub ID i datę komentarza, proponowaną wartość, pewność z uzasadnieniem oraz pytanie do człowieka. Wyjaśnij rolę każdego odkrytego klucza: zamówienie, dowód albo szum.
Zwaliduj każdy YAML względem schematu, daty kalendarzowe, bbox i kolejność steps od start_step. Uruchom walidator validate_jobs.py zgodnie z README. W snapshocie oczekujesz 34 zgłoszeń i 7 kandydatów zamówień. Ręcznie sprawdź pięć zamówień wraz z dowodami. Zgłoś braki dostępu i niepełne strony bez domysłów. Nie zmieniaj Jira ani aplikacji i nie uruchamiaj Databricks ani pipeline.
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
Użyj skilla jira-jobs-triage. Pracuj wybraną wcześniej ścieżką A-offline, A, B lub C. Masz zgodę na wskazane materiały kursowe oraz zapis reports/jira-jobs/jobs/<klucz-epika>.yaml i reports/jira-jobs/issues.md. Nie czytaj wyników J1 ani istniejących konfiguracji: wygeneruj je ponownie na podstawie narzędzi. Zastosuj pełne wyszukiwanie epic + dzieci + podzadania + linki + komentarze oraz dowody spoza hierarchii. Nie zmieniaj Jira ani aplikacji. Zwaliduj YAML i na końcu podaj zastosowane instrukcje oraz decyzje potrzebne od człowieka.
~~~

Porównaj J1 i J2: kompletność dowodów, korekty parametrów, rozpoznanie duplikatu i odróżnienie identycznych nazw różnych obszarów. Sprawdź ręcznie pięć zamówień wraz z ich komentarzami i dziećmi. Zapisz różnice w `reports/jira-jobs/comparison-j1-j2.md`. Użycie skilla samo nie dowodzi lepszego wyniku.

## J3. Opcjonalne porównanie modeli

Wybierz tańszy i mocniejszy model dostępny na koncie przez `/model`. W dwóch świeżych sesjach użyj identycznego promptu J1 i tej samej ścieżki. Nie pokazuj drugiemu modelowi pierwszego wyniku. Zapisz wyniki w nowych katalogach `reports/jira-jobs-comparison/cheap` i `reports/jira-jobs-comparison/strong`.

Ręcznie oceń pięć tych samych zamówień: TEST-1..TEST-5 wraz z pełnym drzewem i dowodami spoza hierarchii. W live ustal odpowiadające im klucze i uzgodnij zakres z prowadzącym. Oceniaj 12 pól poza job_id, maksymalnie 60 punktów; notes jako jedno pole. Sprawdź osobno job_id, liczbę plików i unknown_reasons. `null` jest poprawny tylko z właściwym powodem. Nie porównuj samych tytułów ani statusów.

Zapisz dokładne nazwy modeli, czas i dostępny pomiar zużycia. `/context` w Claude Code lub `/status` w Codex może pokazywać wielkość kontekstu albo limit konta, nie zużyte tokeny; zachowaj nazwę i jednostkę pomiaru z ekranu. Jeśli zużycie nie jest dostępne, napisz to. Nie potrzebujesz dodatkowego płatnego API.

## Granice i narzędzia prowadzącego

Nie zapisuj tokenów, surowych eksportów ani mapowania kont w repozytorium. W A używaj wyłącznie uzgodnionego projektu, ponieważ token sam nie ogranicza dostępu do tego projektu. Po ćwiczeniu wyczyść zmienne w bieżącej sesji.

```powershell
Remove-Item Env:JIRA_API_TOKEN,Env:JIRA_EMAIL,Env:JIRA_CLOUD_ID,Env:JIRA_OFFLINE -ErrorAction SilentlyContinue
```

`sanitize_export.py` służy prowadzącemu do odtworzenia snapshotu z eksportu poza repozytorium. Instrukcja jest w README danych. `seed_jira.py` jest legacy: obsługuje dawny płaski format, nie `seed-spec.json` ani hierarchię v2. Nie uruchamiaj go w ćwiczeniu i nie używaj do odtworzenia tej kolejki.

Źródła: [Jira REST API v3](https://developer.atlassian.com/cloud/jira/platform/rest/v3/), [ADF](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/), [Rovo MCP](https://developer.atlassian.com/cloud/rovo-mcp/), [Claude Code MCP](https://code.claude.com/docs/en/mcp), [Codex MCP](https://developers.openai.com/codex/mcp/).
