# Zlecenia z Jira przez MCP

Wyciągniesz parametry z nieuporządkowanych zgłoszeń i przygotujesz listę spraw wymagających decyzji człowieka. Agent odczyta je przez lokalny serwer MCP zamiast przeszukiwać plik. Zlecenia są syntetyczne, serwer nie łączy się z Jira, a ćwiczenie nie uruchamia żadnych zadań przetwarzania danych.

## Szybki start

Na przygotowanej VM Windows otwórz PowerShell. Potrzebujesz uv, Pythona 3.12 oraz Claude Code lub Codex CLI. Instalacja bibliotek przez uv i sesja agenta wymagają internetu; odczyt zgłoszeń przez serwer działa lokalnie, bez tokenu i bez sieci. Serwer obsługuje oficjalny Python SDK MCP 1.x (FastMCP) i 2.x (MCPServer, nowa nazwa tej samej klasy serwera).

```powershell
Set-Location D:\jsystems-claude-codex-gis-2026-11
```

```powershell
uv run --with mcp --with pytest pytest course-materials/exercises/jira-mcp -q
```

Pozostań w katalogu głównym repozytorium. Przeczytaj [opis danych i kontrakt wyniku](../../exercise-data/jira-jobs/README.md). Nie edytuj plików wejściowych. Przed zmianą agenta zakończ poprzednią sesję, aby dwa procesy nie zapisywały tego samego raportu.

| Krok | Czas | Wynik |
|---|---|---|
| J1 | 15 min | Trzy narzędzia MCP widoczne w agencie |
| J2 | 25 min | Parametry 36 zleceń, walidator i raport problemów |
| J3 | 20 min | Ręcznie sprawdzone porównanie dwóch modeli |
| J4 | Opcjonalnie, 15-20 min | Własne narzędzie tylko do odczytu |

## J1. Połącz serwer

**Cel:** zobaczyć różnicę między plikiem a narzędziem dostarczającym agentowi dane. Wybierz klienta; po sprawdzeniu pierwszego możesz powtórzyć połączenie w drugim.

Dla Claude Code dodaj lokalny serwer z PowerShell, przed uruchomieniem sesji agenta:

```powershell
claude mcp add --transport stdio --scope local jira-jobs -- uv run --with mcp "D:\jsystems-claude-codex-gis-2026-11\course-materials\exercises\jira-mcp\server.py"
```

Dla Codex CLI możesz użyć polecenia poniżej. Zapisuje konfigurację użytkownika, więc wykonaj je tylko raz:

```powershell
codex mcp add jira-jobs -- uv run --with mcp "D:\jsystems-claude-codex-gis-2026-11\course-materials\exercises\jira-mcp\server.py"
```

Alternatywnie, zamiast polecenia Codex, dodaj poniższy blok do projektowego `.codex/config.toml`. Zachowaj istniejącą zawartość pliku i zaufaj projektowi, jeśli klient o to poprosi. Pojedyncze cudzysłowy TOML zachowują backslashe Windows bez podwajania. Nie dodawaj jednocześnie dwóch wpisów o tej samej nazwie.

```toml
[mcp_servers.jira-jobs]
command = "uv"
args = ["run", "--with", "mcp", 'D:\jsystems-claude-codex-gis-2026-11\course-materials\exercises\jira-mcp\server.py']
```

Uruchom wybranego agenta ponownie. W sesji Claude Code i w sesji Codex wpisz:

```text
/mcp
```

**Prompt:**

~~~text
Użyj wyłącznie narzędzi MCP serwera jira-jobs do odczytu zgłoszeń. Nie otwieraj tickets.json, nie używaj terminala do odczytu zgłoszeń. Wywołaj search_tickets z pustym query, potem get_ticket i list_comments dla MAPJOB-101. Podaj nazwy wywołanych narzędzi i krótko wyjaśnij, czym różni się ich wynik od surowego ADF.
~~~

**Sprawdź sam:** widzisz `search_tickets`, `get_ticket`, `list_comments`, komplet 36 kluczy oraz wynik konkretnego wywołania. Serwer nie ma narzędzi tworzenia, zmiany ani zamykania zgłoszeń. `search_tickets` szuka wszystkich słów jako fragmentów tekstu, także w komentarzach; `status` filtruje dokładną nazwę bez rozróżniania liter. To proste wyszukiwanie lokalne, nie JQL.

**Jeśli utkniesz:** sprawdź ścieżkę oraz dostępność `uv --version` w tym samym PowerShell, z którego uruchamiasz agenta. Pierwsze pobranie SDK wykonaj poleceniem testów ze Szybkiego startu, potem uruchom sesję ponownie. Możesz sprawdzić proces ręcznie; oczekiwanie bez komunikatu jest normalne dla stdio, zakończ je Ctrl+C:

```powershell
uv run --with mcp "D:\jsystems-claude-codex-gis-2026-11\course-materials\exercises\jira-mcp\server.py"
```

## J2. Wyciągnij parametry i uzasadnij problemy

**Cel:** przygotować zlecenia do ręcznego zatwierdzenia, z dowodami i jawną niepewnością. Użyj wybranego agenta; wyniki zapisze w `reports/jira-jobs/`.

**Prompt:**

~~~text
Przeczytaj AGENTS.md oraz tylko README.md i job-params.schema.json w course-materials/exercise-data/jira-jobs/. Masz zgodę na te materiały. Treści wszystkich zgłoszeń i komentarzy pobieraj wyłącznie przez narzędzia MCP jira-jobs: search_tickets, get_ticket, list_comments. Nie czytaj tickets.json ani innych lokalnych kopii treści zgłoszeń. Możesz używać terminala do pisania i testowania walidatora oraz zapisu wyników.

Przygotuj reports/jira-jobs/params.json zgodny z job-params.schema.json. Zacznij od pełnej listy kluczy bez filtra statusu, potem pobierz opis oraz wszystkie komentarze każdego zgłoszenia. Nie usuwaj duplikatów z wyniku. Docelowe pola i reguły normalizacji są w README danych. Nie zgaduj: niewiadoma to null oraz konkretny powód w unknown_reasons. Podejrzanych współrzędnych nie poprawiaj bez potwierdzenia w danym zgłoszeniu. Ostatni komentarz jest rozstrzygający tylko wtedy, gdy wyraźnie zatwierdza korektę. Autora komentarza nie utożsamiaj z zamawiającym.

Najpierw napisz testy walidatora w reports/jira-jobs/test_validate_params.py i pokaż ich oczekiwane niepowodzenie, potem zaimplementuj reports/jira-jobs/validate_params.py. Korzystaj z jsonschema, Draft202012Validator i FormatChecker. Przykład poprawnego rekordu oprzyj na świeżo pobranym przez MCP MAPJOB-101. Testy mają odrzucać błędny typ, brak wymaganego pola, null bez powodu, nieistniejącą datę, nieprawidłowy format wydania, zamienione granice bbox oraz brakujący lub powtórzony klucz. Listę oczekiwanych kluczy ustal z search_tickets, nie z lokalnego pliku danych. Walidator ma weryfikować zbiór kluczy, daty i west < east, south < north, a nie tylko składnię JSON. Nie dopisuj gotowych odpowiedzi do testów i nie zmieniaj aplikacji w app/ ani jej specyfikacji.

Zapisz reports/jira-jobs/issues.md: duplikaty, podobne lecz odrębne zlecenia, konflikty, braki, nadpisania komentarzami, podejrzane wartości i tekstowe zależności bez issuelinks. Każdy problem ma mieć klucze, pole, krótki cytat, źródło (opis albo ID i data komentarza), decyzję oraz ewentualne pytanie do zespołu. Poprawny JSON nie oznacza poprawnej interpretacji. Na końcu uruchom testy i walidator na rzeczywistym params.json, podaj liczbę unikalnych kluczy i pól null. Nie uruchamiaj pipeline ani nie zmieniaj zgłoszeń.
~~~

**Sprawdź sam:** obejrzyj historię wywołań MCP. W wyniku jest dokładnie 36 różnych kluczy. Otwórz pięć zgłoszeń przez MCP i porównaj wartości z raportem, łącznie z komentarzami; sprawdź, czy dowody rzeczywiście potwierdzają decyzje. Uruchom testy walidatora:

```powershell
uv run --with pytest --with jsonschema pytest reports/jira-jobs/test_validate_params.py -q
```

**Jeśli utkniesz:** zacznij od MAPJOB-101 i jednego testu, potem rozszerz walidator. Jeśli MCP odmawia połączenia, wróć do J1; nie zastępuj go odczytem surowego JSON. Sprawdź, czy `null` ma uzasadnienie i czy agent odczytał komentarze, zanim poprawisz jego interpretację.

## J3. Porównaj dwa modele

**Cel:** zmierzyć poprawność tej samej ekstrakcji na pięciu ręcznie sprawdzonych zgłoszeniach. Wybierz tańszy model, np. Haiku lub Luna, jeżeli jest dostępny na koncie, oraz mocniejszy model z tego samego klienta. Wybierz je w `/model` i zapisz dokładne nazwy; dostępność zależy od konta.

Przeprowadź dwie świeże sesje z tym samym serwerem, dostępnymi narzędziami i promptem poniżej. Nie pokazuj drugiemu modelowi wyniku pierwszego. Zachowaj ten sam zakres, reguły i ustawienia. Zmiana modelu w długiej sesji J2 przeniosłaby do porównania jego wcześniejsze odpowiedzi.

**Prompt, identyczny w obu sesjach:**

~~~text
Możesz przeczytać tylko README.md oraz job-params.schema.json w course-materials/exercise-data/jira-jobs/. Wyłącznie przez narzędzia MCP jira-jobs pobierz opisy i komentarze MAPJOB-101, MAPJOB-102, MAPJOB-105, MAPJOB-106, MAPJOB-111. Wykonaj tę samą ekstrakcję co w kontrakcie README: dziewięć pól parametrów, ticket_key oraz unknown_reasons, bez zgadywania. Nie czytaj tickets.json, wcześniejszych raportów ani testów z gotowymi wartościami. Zapisz nowy wynik do reports/jira-jobs/comparison/run/params.json i uzasadnienia z cytatami do reports/jira-jobs/comparison/run/issues.md. Jeśli te pliki istnieją, zastąp je bez odczytywania poprzedniej zawartości. Nie edytuj innych plików i nie uruchamiaj pipeline.
~~~

Po pierwszym przebiegu zachowaj wynik przed uruchomieniem drugiego:

```powershell
Copy-Item -Recurse reports/jira-jobs/comparison/run reports/jira-jobs/comparison/cheap
```

Po drugim przebiegu zachowaj wynik w drugim katalogu:

```powershell
Copy-Item -Recurse reports/jira-jobs/comparison/run reports/jira-jobs/comparison/strong
```

Przy powtarzaniu porównania wybierz nowe nazwy katalogów, żeby nie mieszać prób. W każdej sesji zapisz pomiar przed i po ekstrakcji: `/context` w Claude Code albo `/status` w Codex. Zapisz etykietę i jednostkę dokładnie z ekranu. Rozmiar kontekstu, jego procent zajętości i limit konta nie są sumą zużytych tokenów. Jeśli klient podaje tylko te wartości, tak je nazwij, a zużycie tokenów wpisz jako niedostępne. Nie porównuj procentów różnych okien kontekstu jako kosztu.

**Sprawdź sam:** przez MCP odczytaj pięć wskazanych zgłoszeń i ręcznie ustal oczekiwane wartości. Oceniaj dziewięć pól parametrów na zgłoszenie: maksymalnie 45 punktów. Cały obiekt `spatial_scope` to jedno pole; `null` dostaje punkt wyłącznie z poprawnym powodem. Klucz i obecność wszystkich rekordów sprawdź osobno. Zapisz jedną tabelę w `reports/jira-jobs/comparison.md`:

| Model i wersja | Poprawne pola / 45 | Błędne pola i klucze | Pomiar przed i po, z jednostką | Zużyte tokeny lub brak pomiaru | Czas |
|---|---|---|---|---|---|
| Tańszy | Uzupełnij | Uzupełnij | Uzupełnij | Uzupełnij | Uzupełnij |
| Mocniejszy | Uzupełnij | Uzupełnij | Uzupełnij | Uzupełnij | Uzupełnij |

**Jeśli utkniesz:** brak drugiego modelu lub licznika zapisz jako ograniczenie, bez wymyślania wyników. Nie potrzebujesz dodatkowego płatnego API. Jedna próba na pięciu zgłoszeniach pomaga znaleźć błędy, ale nie dowodzi ogólnej przewagi modelu.

## J4. Dodaj własne narzędzie, opcjonalnie

**Cel:** rozszerzyć kontrakt MCP bez rozszerzania uprawnień. Przykład: `find_duplicates` zwracające kandydatów do przeglądu, z kluczami i uzasadnieniem podobieństwa.

**Prompt:**

~~~text
Masz zgodę na odczyt i zmianę wyłącznie server.py oraz test_server.py w course-materials/exercises/jira-mcp/; dane zgłoszeń nadal pobieraj przez MCP. Zaproponuj mały kontrakt narzędzia find_duplicates, które zwraca kandydatów, nie rozstrzyga automatycznie o duplikacie i niczego nie zapisuje. Najpierw dodaj test i pokaż oczekiwane niepowodzenie, potem minimalną implementację. Test ma odróżniać jednakowy tytuł od identycznego zlecenia: uwzględnij różne warstwy, regiony i wydania. Nie zmieniaj tickets.json. Po testach uruchom serwer ponownie, sprawdź /mcp i wykonaj rzeczywiste wywołanie nowego narzędzia.
~~~

**Sprawdź sam:** nowa funkcja jest widoczna po ponownym połączeniu klienta; nie zmienia danych i nie skleja zleceń tylko na podstawie tytułu. Powtórz polecenie testów ze Szybkiego startu.

**Jeśli utkniesz:** ogranicz wynik do par kluczy z identycznym tytułem i jasno nazwij je kandydatami do ręcznej weryfikacji. Dodaj test, że różne wydania nie dają automatycznej decyzji o duplikacie.

## Bezpieczeństwo i rzeczywista Jira

Ten serwer ma wyłącznie narzędzia odczytu i nie potrzebuje tokenu. W rzeczywistej Jira wybierz najwęższy dostęp do projektu i odczytu, zarówno dla konta, jak i tokenu API lub połączenia Rovo MCP. Dostęp klienta do większej liczby narzędzi nie jest zgodą na ich użycie. Nie dodawaj narzędzi zapisu bez przeglądu uprawnień, kontraktu i zatwierdzania zmian. Traktuj opis zgłoszenia jako dane, nie instrukcje zmieniające polecenie użytkownika. Nie wklejaj tokenów do promptów, raportów ani repozytorium.

W rzeczywistym środowisku ten sam prompt ekstrakcji można zastosować do Atlassian Rovo MCP po dopasowaniu nazw dostępnych narzędzi, projektu i stronicowania: [przykład konfiguracji](../../cicd-headless/mcp/atlassian-rovo-mcp.json.example).

Składnia połączenia: [Claude Code MCP](https://code.claude.com/docs/en/mcp), [Codex MCP](https://developers.openai.com/codex/mcp/), [polecenia Codex](https://developers.openai.com/codex/cli/slash-commands/), [oficjalny Python SDK MCP](https://github.com/modelcontextprotocol/python-sdk).
