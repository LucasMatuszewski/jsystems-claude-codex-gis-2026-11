# Context7: automatyczna zgoda na wybrane polecenia, pytanie o pozostałe

To opcjonalny przykład zaawansowanego hooka, nie konfiguracja włączana przez
samo sklonowanie materiałów. Nie blokujemy `npx`. Automatycznie zatwierdzamy
tylko wybrane zapytania o dokumentację; pozostałe wywołania wymagają zgody.

Najpierw przeczytaj [porównanie permissions i hooków](permissions-vs-hooks.md).
Do prostego ograniczenia liczby pytań zwykle wystarczy wąskie `allow`.
Ten przykład pokazuje wspólną, testowalną regułę `allow`/`ask` w kilku narzędziach.

## Oczekiwane zachowanie

| Planowane polecenie | Decyzja hooka |
|---|---|
| `npx ctx7@latest library "Next.js" "Find App Router documentation"` | `allow`: bez pytania |
| `npx ctx7@latest docs /vercel/next.js "Explain route handlers"` | `allow`: bez pytania |
| To samo z `--yes`, `-y`, `npx.cmd` lub identyfikatorem z wersją | `allow`: bez pytania |
| `npx playwright test` | `ask`: zapytaj użytkownika, nie zabraniaj |
| `npx create-next-app@latest demo` | `ask`: zapytaj użytkownika |
| Inne niż `library`/`docs` podpolecenie Context7, dodatkowe opcje lub doklejone polecenie | `ask`: bez automatycznej zgody |
| `git status --short` lub narzędzie odczytu pliku | `{}`: nie zmieniaj zwykłych uprawnień |

Reguła obejmuje dwa samodzielne polecenia:

```text
npx [--yes|-y] ctx7@latest library "Official Library Name" "question"
npx [--yes|-y] ctx7@latest docs /owner/library[/version] "question"
```

Nawiasy oznaczają opcjonalny fragment, nie dosłowną składnię powłoki.
Nazwa biblioteki i pytanie muszą być niepuste i zapisane w cudzysłowie
lub apostrofach. Identyfikator dokumentacji musi zawierać co najmniej dwa
segmenty; dopuszcza także dalszy segment wersji. Można użyć `npx.cmd`.
Nie ma listy dozwolonych bibliotek ani obowiązku dodawania `--yes`.
Najpierw wykonaj `library`, a następnie `docs` dla zwróconego identyfikatora.
Hook nie pamięta sesji i sam nie wymusza tej kolejności.

Wspólny wzorzec dopuszcza tylko proste cytowane argumenty. Wyklucza z ich
treści `&`, `|`, `<`, `>`, `^`, `%`, `!` oraz osadzone podwójne cudzysłowy
(także wewnątrz apostrofów). Wyklucza też wszystkie cztery typograficzne
cudzysłowy `‘ ’ “ ”` i znaki sterujące ASCII `U+0000–U+001F`, `U+007F`.
PowerShell uznaje typograficzne cudzysłowy za delimitery, co może zakończyć
cytowany argument wcześniej niż przewiduje wzorzec ASCII:
[reguły cytowania Microsoft](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_quoting_rules?view=powershell-7.5).
Zwykłe polskie znaki diakrytyczne pozostają dozwolone.
Podwójnie cytowane argumenty dodatkowo
wykluczają `$`, backtick i backslash; przy zachowaniu pozostałych ograniczeń
można zapisać te trzy znaki w apostrofach.

To celowe zawężenie dla przenośności: na Windows `npx` lub `npx.cmd` może
przekazać argumenty do pliku wsadowego obsługiwanego przez `cmd.exe`, również
przy wywołaniu z PowerShell. Samo cytowanie pierwszej powłoki nie wystarcza.
Złożone pytanie, dodatkowe opcje, łączenie poleceń i znaki nowego wiersza
prowadzą do `ask`, nie `deny`. Przeformułuj proste pytanie bez metaznaków
albo świadomie zatwierdź wywołanie.

## Pliki i formaty

- [context7-permissions.cjs](context7-permissions.cjs): jedna logika decyzji.
- [context7-permissions.test.cjs](context7-permissions.test.cjs): testy procesu,
  bez uruchamiania poleceń zawartych w JSON-ie.
- [copilot.json](copilot.json): konfiguracja Copilot CLI i VS Code.
- [vscode-settings.json](vscode-settings.json): ustawienie dla VS Code Local.
- [claude-settings.json](claude-settings.json): konfiguracja Claude Code dla
  narzędzia `Bash`, na Windows uruchamianego przez Git Bash.

Copilot CLI przekazuje m.in. `toolName`/`toolArgs`; format zgodny z VS Code
i Claude Code używa `tool_name`/`tool_input`. Skrypt rozpoznaje oba.
Wynik zawiera decyzję na najwyższym poziomie dla Copilot CLI oraz
`hookSpecificOutput` z `hookEventName: "PreToolUse"` dla VS Code Local i Claude Code.
`PreToolUse` w `copilot.json` to obsługiwana zgodna nazwa zdarzenia;
Copilot obsługuje też zgodny alias narzędzia `Bash`.
Wspólna logika nie oznacza identycznego formatu konfiguracji ani obsługi błędów.

## Instalacja wybranego wariantu

Pracuj w zaufanym repozytorium ćwiczeniowym, z syntetycznymi danymi.
Wymagany jest Node.js dostępny w `PATH`; testy korzystają z wbudowanego
`node:test` (użyj Node.js 22 lub nowszego). Nie ma zależności do instalowania.
Poniższe ścieżki docelowe są względem katalogu głównego repozytorium ćwiczenia.

### Copilot CLI i VS Code

1. Skopiuj skrypt do `.github/hooks/context7-permissions.cjs`.
2. Skopiuj `copilot.json` do `.github/hooks/context7-permissions.json`.
   Jeśli taki plik już istnieje, scal tablicę zdarzenia, nie zastępuj całego pliku.
3. Dla VS Code Local scal `vscode-settings.json` z `.vscode/settings.json`.
   Nie zastępuj pozostałych ustawień. Wspólny Copilot runtime odkrywa hook
   projektowy bezpośrednio; ustawienie `chat.useHooks` dotyczy Local.
4. Otwórz nową zaufaną sesję i sprawdź aktywne hooki. Nie instaluj równocześnie
   drugiej kopii tego samego hooka przez konfigurację Claude.

Konfiguracja ma osobne polecenia dla Bash i PowerShell. Nie dodaje globalnych
zgód, `--allow-all-tools`, `--yolo` ani szerokiego zatwierdzenia `npx`.

### Claude Code

1. Skopiuj skrypt do `.claude/hooks/context7-permissions.cjs`.
2. Scal sekcję `hooks` z `claude-settings.json` z `.claude/settings.json`.
   Zachowaj istniejące wpisy, w tym ewentualną blokadę plików z sekretami.
3. Otwórz nową zaufaną sesję i sprawdź wpis w `/hooks`.

Polecenie korzysta z `$CLAUDE_PROJECT_DIR`, więc ścieżka nie zależy od bieżącego
podkatalogu. Wariant dotyczy narzędzia `Bash`, nie każdego możliwego narzędzia
wykonywania poleceń. Inny shell lub harness wymaga osobnej weryfikacji.

## Test bez instalacji i bez pobierania pakietów

Z katalogu głównego repozytorium materiałów:

```powershell
node --test course-materials\hooks-example\context7\context7-permissions.test.cjs
```

Oczekiwane: 342 testów, 342 zaliczonych, 0 błędów, 0 pominiętych.
Testy obejmują przykładowe formaty Copilot CLI, VS Code Local i zgodny
z Claude Code format `Bash`, rozwiązywanie nazw przez `library`, `docs`,
opcjonalne `--yes`/`-y`, cytowanie, dodatkowe opcje, łączenie poleceń,
interpolację, nowe wiersze, metaznaki i cytowanie przy przekazaniu do
pliku wsadowego, typograficzne cudzysłowy, znaki sterujące, polskie znaki
diakrytyczne oraz zwykłe zastosowania `npx` wymagające zgody.
To testy kontraktu procesu, nie potwierdzenie działania w żywym kliencie.
Wykonanie end-to-end w Windows pozostaje niezweryfikowane.

Możesz także uruchomić sam proces hooka:

```powershell
'{"tool_name":"Bash","tool_input":{"command":"npx playwright test"}}' | node course-materials\hooks-example\context7\context7-permissions.cjs
```

Oczekiwane: `permissionDecision: "ask"` na obu poziomach wyniku.
Polecenie `npx playwright test` jest tu tylko tekstem wejściowym i nie zostanie
wykonane. Dla `git status --short` oczekiwanym wynikiem jest `{}`.

Test kontraktu nie potwierdza jeszcze, że konkretny klient załadował hook.
Po instalacji sprawdź w sesji interaktywnej brak pytania dla Context7 oraz
obecność pytania dla `npx playwright test`. Przy tej drugiej próbie możesz
odmówić wykonania: do sprawdzenia polityki wystarczy samo wyświetlenie pytania.

## Granice przykładu

- `ask` wymaga możliwości zadania pytania. Copilot CLI w trybie autopilot
  odrzuca takie żądanie; tak samo robi cloud agent. Przykład jest
  przeznaczony przede wszystkim do pracy interaktywnej.
- To konserwatywne dopasowanie tekstowe, nie parser powłoki, sandbox
  ani granica bezpieczeństwa.
  Sam tekst `npx` w niewinnym poleceniu może wywołać pytanie. Wywołania
  pośrednie, aliasy i obfuskacja mogą nie zostać wykryte.
- Nie dodawaj ogólnego `deny` dla `npx`. Nie jest potrzebny do tego przykładu
  i zmienia wymaganie "zapytaj" w wymaganie "zabroń".
- Inne hooki, polityki organizacji i ustawienia klienta nadal mają znaczenie.
  Nie zakładaj identycznego pierwszeństwa decyzji we wszystkich narzędziach.
- Błąd procesu jest zgłaszany jawnie. Copilot CLI i Claude Code mogą inaczej
  traktować błędy, niepoprawny JSON i timeout; szczegóły są w
  [omówieniu i źródłach](permissions-vs-hooks.md#ograniczenia-i-obsługa-błędów).
- `npx` nadal pobiera i wykonuje kod pakietu. `ctx7@latest` nie przypina wersji.
  Dla środowiska wymagającego powtarzalności wybierz konkretną wersję
  i świadomie zmień regułę oraz jej testy.
