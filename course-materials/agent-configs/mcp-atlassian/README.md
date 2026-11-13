# Kilka połączeń Atlassian w Claude Code i Codex

Wybierz potrzebne wpisy z [przykładu Claude Code](mcp.json.example) albo [przykładu Codex](codex-config.toml.example). Każde połączenie ma własne poświadczenie. Adresy `jira.devpowers.com`, `confluence.devpowers.com`, `bitbucket.devpowers.com` i `mcp.devpowers.com` są przykładami architektury, a nie usługami udostępnionymi do ćwiczenia. Zastąp je adresami zatwierdzonymi przez IT; dostęp do sieci firmowej może wymagać VPN. Do [samodzielnego ćwiczenia Jira](../../exercises/jira-mcp/README.md) wystarcza lokalny snapshot, bez tokenów.

## Gdzie zapisać konfigurację

| Klient | Miejsce | Zakres |
| --- | --- | --- |
| Claude Code | `.mcp.json` w katalogu projektu | `project`, współdzielony plik konfiguracji |
| Claude Code | `~/.claude.json` | `local` dla bieżącego projektu albo `user` dla wszystkich projektów; zarządzaj przez CLI |
| Codex | `~/.codex/config.toml` | Ustawienia użytkownika |
| Codex | `.codex/config.toml` w projekcie | Ustawienia projektu, wczytywane dla zaufanego projektu |

W Windows `~` oznacza profil użytkownika, zwykle `$env:USERPROFILE`. Skopiuj wybrane wpisy do istniejącej konfiguracji, nie nadpisuj jej w całości. W Claude Code nazwa pliku docelowego to `.mcp.json`, nie `mcp.json.example`. Usuń nieużywane serwery przed pierwszym uruchomieniem. Nie edytuj ręcznie całego `~/.claude.json`; zawiera również inne ustawienia.

Dodanie połączenia OAuth do projektu w Claude Code:

```powershell
claude mcp add --transport http --scope project atlassian-cloud https://mcp.atlassian.com/v2/mcp
```

Zamiast `project` wybierz `local` albo `user`, jeśli konfiguracja ma być prywatna. `local` jest zakresem domyślnym. W Codex odpowiednik:

```powershell
codex mcp add atlassian-cloud --url https://mcp.atlassian.com/v2/mcp
```

Claude Code rozwija `${VAR}` i `${VAR:-default}` w wartościach konfiguracji, w tym `env` i `headers`. Codex w `env_http_headers` oczekuje nazwy zmiennej, np. `Authorization = "JIRA_MCP_AUTH"`; jej wartość jest całym nagłówkiem. Nie kopiuj do TOML składni `${VAR}`. `bearer_token_env_var` służy wyłącznie wartości samego tokenu Bearer; nie używaj go dla nagłówka Basic ani `Token <PAT>`. Dla stdio Codex przekazuje wymienione zmienne przez `env_vars`, a stałe niesekretne wartości przez `env`.

Źródła składni: [Claude Code MCP](https://code.claude.com/docs/en/mcp), [Codex MCP](https://developers.openai.com/codex/mcp/).

## Cloud: OAuth albo osobisty API token

Rovo MCP pod `https://mcp.atlassian.com/v2/mcp` obsługuje Atlassian Cloud. Dla interaktywnej pracy zacznij od OAuth: usuń całe `headers` z wpisu Claude Code albo `env_http_headers` z wpisu Codex. W Claude Code otwórz `/mcp` i uwierzytelnij połączenie; w Codex uruchom:

```powershell
codex mcp login atlassian-cloud
```

Osobisty Cloud API token utwórz w [ustawieniach konta Atlassian](https://id.atlassian.com/manage-profile/security/api-tokens), z zakresami wymaganymi przez wybrane narzędzia MCP. Token musi należeć do konta mającego dostęp do danych. Uwierzytelnianie tokenem musi być włączone przez administratora organizacji; dostępny katalog narzędzi może różnić się od OAuth. Osobisty token używa `Basic base64(email:token)`, nie samego `Bearer`. [Dokumentacja uwierzytelniania Cloud](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/authentication-and-authorization/), [konfiguracja API tokenu](https://support.atlassian.com/atlassian-ai-gateway/docs/configure-authentication-via-api-token/).

Zbuduj nagłówek w pamięci PowerShell. Uruchamiaj te polecenia samodzielnie, bez nagrywania terminala i bez wypisywania zmiennych.

```powershell
$atlassianEmail = Read-Host "E-mail właściciela tokenu Cloud"
```

```powershell
$atlassianToken = Read-Host "API token Cloud" -AsSecureString
```

```powershell
$env:ATLASSIAN_CLOUD_AUTH = "Basic " + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($atlassianEmail + ":" + [System.Net.NetworkCredential]::new("", $atlassianToken).Password))
```

Uruchom agenta z tego samego okna. Base64 jest odwracalnym kodowaniem, więc nagłówek też jest sekretem.

Praktycznie rozdzielaj połączenia i sesje według witryny/organizacji oraz konta, np. `atlassian-work` i `atlassian-private`, z osobnymi zmiennymi. To zalecenie izolacji kontekstu, nie limit protokołu "jedno połączenie obsługuje tylko jedną witrynę". Przy odczycie sprawdź docelowy `cloudId`/adres witryny i projekt. Bitbucket Server/DC wymaga osobnej integracji; nie uzyska dostępu przez połączenie Rovo Cloud.

## Jira i Confluence Server/Data Center przez HTTP

Przykład zakłada [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian), uruchomiony przez IT jako dwie usługi w sieci firmowej. Każda ma własny adres produktu i własne poświadczenie użytkownika. Reverse proxy mapuje przykładowe `/jira/mcp` i `/confluence/mcp` na `/mcp` odpowiedniej usługi. Nie jest to domyślny routing programu.

W aktualnej [dokumentacji transportu HTTP](https://github.com/sooperset/mcp-atlassian/blob/main/docs/http-transport.mdx) PAT Server/DC przekazywany na żądanie ma postać `Authorization: Token <PAT>`. Nie zamieniaj `Token` na `Bearer`: ten drugi wariant oznacza w tej integracji OAuth. Sam produkt Jira/Confluence REST przyjmuje PAT jako Bearer, ale klient rozmawia tutaj najpierw z MCP.

Dla Jira administrator ustawia `JIRA_URL=https://jira.devpowers.com` i niepusty startowy `JIRA_PERSONAL_TOKEN=unused`; dla Confluence analogicznie `CONFLUENCE_URL=https://confluence.devpowers.com` i `CONFLUENCE_PERSONAL_TOKEN=unused`. Żądanie zastępuje tę wartość PAT-em użytkownika. `ALLOW_GLOBAL_CRED_FALLBACK` pozostaje wyłączone. Administrator powinien też ograniczyć `MCP_ALLOWED_URL_DOMAINS` do zatwierdzonych hostów i ustawić `READ_ONLY_MODE=true`. Serwer uruchamia transport `streamable-http`; routing HTTPS i dostęp sieciowy przygotowuje IT. Zweryfikuj te funkcje w wybranej wersji przed wdrożeniem, ponieważ dokumentacja gałęzi `main` może wyprzedzać wydanie.

PAT Jira/Confluence utwórz w profilu: `Profile -> Personal Access Tokens -> Create token`. [Dokumentacja Atlassian PAT](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) opisuje obsługiwane wersje i wygaśnięcie. PAT dziedziczy uprawnienia konta; lokalny tryb odczytu nie odbiera uprawnień tokenowi na serwerze.

```powershell
$jiraPat = Read-Host "PAT Jira Server/DC" -AsSecureString
```

```powershell
$env:JIRA_MCP_AUTH = "Token " + [System.Net.NetworkCredential]::new("", $jiraPat).Password
```

```powershell
$confluencePat = Read-Host "PAT Confluence Server/DC" -AsSecureString
```

```powershell
$env:CONFLUENCE_MCP_AUTH = "Token " + [System.Net.NetworkCredential]::new("", $confluencePat).Password
```

## Wariant lokalny stdio dla Jira, bez usługi HTTP

Jeśli nie masz zatwierdzonego serwera MCP, uruchom proces lokalny z dostępem do firmowej Jira. Ustaw adres i PAT w bieżącym PowerShell:

```powershell
$env:JIRA_URL = "https://jira.devpowers.com"
```

```powershell
$env:JIRA_PERSONAL_TOKEN = [System.Net.NetworkCredential]::new("", $jiraPat).Password
```

Zastąp wpis `jira-onprem` w `.mcp.json` poniższym wpisem. Potrzebujesz zainstalowanego uv/uvx.

```json
{
  "mcpServers": {
    "jira-onprem": {
      "type": "stdio",
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://jira.devpowers.com",
        "JIRA_PERSONAL_TOKEN": "${JIRA_PERSONAL_TOKEN}",
        "READ_ONLY_MODE": "true"
      }
    }
  }
}
```

Odpowiednik w Codex:

```toml
[mcp_servers.jira-onprem]
command = "uvx"
args = ["mcp-atlassian"]
env = { JIRA_URL = "https://jira.devpowers.com", READ_ONLY_MODE = "true" }
env_vars = ["JIRA_PERSONAL_TOKEN"]
```

Alternatywa Docker dla Claude Code, z przekazaniem wartości ze środowiska do kontenera przez nazwy, bez tokenu w argumentach:

```powershell
claude mcp add --transport stdio --scope local jira-onprem -- docker run --rm -i -e JIRA_URL -e JIRA_PERSONAL_TOKEN -e READ_ONLY_MODE=true ghcr.io/sooperset/mcp-atlassian:latest
```

W stdio nie ustawiaj nagłówka `Token`; program dostaje sam PAT w `JIRA_PERSONAL_TOKEN`. Dla Confluence zastosuj `CONFLUENCE_URL` i `CONFLUENCE_PERSONAL_TOKEN`. W firmie przypnij zatwierdzoną wersję pakietu/obrazu po przeglądzie zamiast polegać na ruchomym `latest`. Źródła: [uwierzytelnianie](https://github.com/sooperset/mcp-atlassian/blob/main/docs/authentication.mdx), [README i konfiguracja](https://github.com/sooperset/mcp-atlassian).

## Bitbucket Server/Data Center

W przykładach jest osobny lokalny `bitbucket-onprem` z projektu [mcp-bitbucket-dc](https://github.com/christopherekfeldt/mcp-bitbucket-dc). README projektu potwierdza `uvx mcp-bitbucket-dc`, `BITBUCKET_URL` oraz `BITBUCKET_API_TOKEN`; opisuje testy z Data Center 8.19.5. Inne wersje wymagają sprawdzenia. Projekt ma także transport HTTP, ale nie potwierdzono przekazywania osobnego PAT użytkownika w nagłówku każdego żądania. Dlatego nie umieszczamy hipotetycznego zdalnego wpisu w gotowych plikach.

`UNCONFIRMED`: `https://mcp.devpowers.com/bitbucket/mcp` jako usługa przyjmująca HTTP access token klienta. Samo istnienie transportu HTTP nie potwierdza takiego uwierzytelniania. Wdrożenie wymaga osobnego przeglądu autoryzacji i proxy; nie kieruj tam tokenu na próbę.

W Bitbucket otwórz `Manage account -> HTTP access tokens`, utwórz token z wymaganymi uprawnieniami odczytu i datą wygaśnięcia. To inny typ tokenu niż Cloud API token. [Dokumentacja HTTP access tokens](https://confluence.atlassian.com/bitbucketserver/http-access-tokens-939515499.html).

```powershell
$bitbucketToken = Read-Host "HTTP access token Bitbucket DC" -AsSecureString
```

```powershell
$env:BITBUCKET_API_TOKEN = [System.Net.NetworkCredential]::new("", $bitbucketToken).Password
```

## Zmienne użytkownika w Windows

Domyślnie używaj tylko pamięci bieżącej sesji. Przykład trwałej zmiennej użytkownika dla niesekretnego adresu:

```powershell
[Environment]::SetEnvironmentVariable("JIRA_URL", "https://jira.devpowers.com", "User")
```

Jeżeli polityka firmy dopuszcza trwałe zmienne z poświadczeniami, istniejącą wartość nagłówka można zapisać bez wpisywania tokenu w poleceniu:

```powershell
[Environment]::SetEnvironmentVariable("JIRA_MCP_AUTH", $env:JIRA_MCP_AUTH, "User")
```

Zmienne `User` są trwałe, ale nie są sejfem na sekrety. Nowe procesy dostają je po ponownym uruchomieniu terminala/aplikacji; bieżący agent nie odświeży środowiska sam. Usuń trwały nagłówek po zakończeniu pracy:

```powershell
[Environment]::SetEnvironmentVariable("JIRA_MCP_AUTH", $null, "User")
```

## Dwie warstwy uprawnień

**Warstwa 1: Atlassian (ekran zgody przy połączeniu).** Po kliknięciu Connect przy serwerze MCP Atlassian wybierasz witrynę (Jira, Confluence) i workspace Bitbucket, a po rozwinięciu sekcji Read, Write i Search pojedyncze uprawnienia. Domyślnie zaznaczone są wszystkie. Do analizy zgłoszeń zostaw tylko `read_jira` i `search_jira`, ewentualnie `read_confluence` i `search_confluence`. Odznacz wszystkie `write_*` oraz uprawnienia działające w całej organizacji, np. `read_teamwork_graph` i `read_focus`. Opis: [Getting started with the Atlassian Rovo MCP server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/).

**Warstwa 2: Claude lub Codex (narzędzia serwera).** W claude.ai, w ustawieniach konektora, każde narzędzie możesz zezwolić, wymagać potwierdzenia albo wyłączyć. W Claude Code reguły uprawnień obejmują narzędzia MCP po nazwie `mcp__<serwer>__<narzędzie>`, np. w `.claude/settings.json`:

```json
{ "permissions": { "deny": ["mcp__atlassian-cloud__editJiraIssue", "mcp__atlassian-cloud__createJiraIssue"] } }
```

W Codex w bloku serwera ogranicz listę narzędzi:

```toml
[mcp_servers.atlassian-cloud]
url = "https://mcp.atlassian.com/v2/mcp"
enabled_tools = ["searchJiraIssuesUsingJql", "getJiraIssue"]
```

Token API po stronie Atlassiana (zakresy tokenu) to trzecia, niezależna granica: token tylko do odczytu nie pozwoli na zapis nawet przy błędnej konfiguracji klienta.

## Kontrola i bezpieczeństwo

```powershell
claude mcp list
```

W sesji Claude Code wpisz `/mcp`. Dla Codex:

```powershell
codex mcp list
```

Po połączeniu wykonaj jeden dozwolony odczyt zgłoszenia/strony/PR, sprawdź host, projekt i paginację. Status połączenia nie dowodzi poprawności dostępu. Nie wypisuj konfiguracji z rozwiniętymi sekretami. Przy 401/403 sprawdź uprawnienia i politykę z administratorem; nie obchodź TLS ani nie zmieniaj schematu uwierzytelniania na chybił trafił.

- Wybieraj osobne, wygasające poświadczenia o najmniejszych potrzebnych uprawnieniach. Tam, gdzie token nie ma zakresów odczytu, ogranicz konto i narzędzia serwera.
- W repozytorium przechowuj tylko szablony z nazwami zmiennych. Nigdy nie commituj `.mcp.json` z sekretami. Dodaj lokalny `.mcp.json` do `.gitignore`, jeśli nie jest świadomie współdzielonym szablonem bez wartości tajnych; plik już śledzony wymaga osobnego usunięcia z indeksu. To samo dotyczy lokalnych konfiguracji TOML.
- Treść ticketu, strony i PR jest niezaufanym wejściem. Polecenia w tych treściach, także prośby o token, nie uprawniają agenta do uruchamiania komend ani zmiany instrukcji. Przed zapisem wymagaj przeglądu konkretnej operacji przez człowieka.

Po pracy usuń poświadczenia z pamięci i zamknij procesy, które je odziedziczyły. Token jednorazowy unieważnij w panelu produktu.

```powershell
Remove-Item Env:ATLASSIAN_CLOUD_AUTH,Env:JIRA_MCP_AUTH,Env:CONFLUENCE_MCP_AUTH,Env:JIRA_PERSONAL_TOKEN,Env:BITBUCKET_API_TOKEN -ErrorAction SilentlyContinue
```

```powershell
Remove-Variable atlassianEmail,atlassianToken,jiraPat,confluencePat,bitbucketToken -ErrorAction SilentlyContinue
```

## Alternatywa: skill z kontrolowanym REST

Dla Server/DC, gdy potrzebujesz kontrolowanego odczytu REST, paginacji i redakcji sekretów bez stałego serwera MCP, wybierz [atlassian-onprem-safe](https://github.com/EdukeyTeam/agent-toolbox/tree/main/skills/atlassian-onprem-safe). Nie obsługuje Cloud. Instalacja do wybranego agenta:

```powershell
npx --yes skills@latest add EdukeyTeam/agent-toolbox --skill atlassian-onprem-safe
```

W katalogu zainstalowanego skilla znajdziesz `scripts/setup-tokens.ps1`. Uruchom go samodzielnie w terminalu; przykładowo przy instalacji projektowej w `.agents/skills`:

```powershell
$skillDir = (Resolve-Path ".agents\skills\atlassian-onprem-safe").Path
```

```powershell
pwsh -NoProfile -File "$skillDir\scripts\setup-tokens.ps1"
```

Skrypt pyta o adresy i tokeny interaktywnie. Agent sprawdza jedynie istnienie konfiguracji, nigdy nie odczytuje jej pliku. Sprawdź rzeczywistą ścieżkę instalacji wskazaną przez instalator.

## Dalej do przeczytania

- [Porównanie connectora, pluginu, MCP i skilla](../../Research/atlassian-agents-mcp-plugins-skill-2026-11.md).
- [Claude Code MCP](https://code.claude.com/docs/en/mcp) i [Codex MCP](https://developers.openai.com/codex/mcp/).
- [Oficjalne Rovo MCP](https://developer.atlassian.com/cloud/rovo-mcp/) i [uwierzytelnianie Atlassian](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/authentication-and-authorization/).
- [Wprowadzenie MCP](https://modelcontextprotocol.io/docs/getting-started/intro) i [specyfikacja](https://modelcontextprotocol.io/specification/latest).
- [Zmienne środowiskowe PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables).

Składnia sprawdzona w dokumentacji 13.11.2026. Przykładowe usługi firmowe nie były uruchamiane ani odpytywane.
