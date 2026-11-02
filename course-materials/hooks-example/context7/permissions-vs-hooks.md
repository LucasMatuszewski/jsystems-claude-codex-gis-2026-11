# Permissions czy hooki? Dobór mechanizmu na przykładzie Context7

Stan dokumentacji: 26.10.2026 (ponownie sprawdzono kontrakt hooków Copilot
i rozróżnienie harnessów VS Code). Przykład dotyczy Copilot CLI, VS Code Copilot
oraz Claude Code. Zawsze sprawdź wersję klienta i aktywny harness.

## Najważniejsze rozróżnienie

**Brak automatycznej zgody nie oznacza zakazu.**

| Decyzja | Znaczenie |
|---|---|
| `allow` | Automatycznie zatwierdź pasujące wywołanie |
| `ask` | Poproś użytkownika o zgodę; może zatwierdzić lub odmówić |
| `deny` | Odrzuć wywołanie |
| Brak decyzji hooka, np. `{}` | Pozostaw standardowy mechanizm uprawnień |

`{}` nie jest synonimem `ask`: zwykłe ustawienia mogą już dopuszczać polecenie.
Z kolei `ask` nie jest synonimem `deny`, choć bez interaktywnego użytkownika
żądanie zgody może zakończyć się odmową.

W [przykładzie Context7](README.md) wymaganie brzmi:

> Automatycznie zatwierdzaj samodzielne zapytania `ctx7 library` i `ctx7 docs`
> o dowolną bibliotekę, z opcjonalnym `--yes` lub `-y`. Dla innych wykrytych
> wywołań `npx` pytaj o zgodę.
> Nie zabraniaj korzystania z `npx`.

To inna polityka niż "Context7 wolno uruchomić, wszystkie inne pakiety są zakazane".
Przed konfiguracją ustal, o którą z nich chodzi.

## Najpierw zwykłe permissions

Jeśli potrzebujesz tylko przestać zatwierdzać powtarzalne polecenie, zacznij od
wąskiego `allow`. Jest krótsze, czytelniejsze i nie wymaga własnego programu.
Polecenia poza regułą nadal przechodzą przez standardowy mechanizm uprawnień.

Narzędzia mają różne mechanizmy:

- **Claude Code:** `permissions.allow`, `permissions.ask` i `permissions.deny`
  w ustawieniach; projektowa konfiguracja współdzielona to `.claude/settings.json`.
- **Copilot CLI:** m.in. `--allow-tool` i `--deny-tool` z wzorcami `shell(...)`.
  Obsługiwane ustawienia repozytorium sprawdzisz przez `copilot help config`,
  a semantykę wzorców przez `copilot help permissions`. Nie zakładaj, że klucz
  `permissions.allow` z Claude Code działa tak samo w Copilot CLI.
- **VS Code Local:** m.in. reguły `chat.tools.terminal.autoApprove`
  w `.vscode/settings.json`. Wartość `false` wymaga zgody, nie oznacza zakazu.
  Nie przenoś ich bez sprawdzenia do sesji korzystającej z innego harnessu.

Wąska zgoda jest lepsza od zatwierdzenia całego `npx`: ten program potrafi
pobierać i uruchamiać dowolne pakiety, nie tylko narzędzie do dokumentacji.
Nie zapisuj zgody globalnej, jeśli potrzeba dotyczy jednego projektu.

## Pułapka: szeroki zakaz i wąski wyjątek

Nie zakładaj, że bardziej szczegółowa reguła zawsze wygrywa.

W Claude Code kolejność kategorii to `deny`, potem `ask`, potem `allow`.
Szeroki zakaz `Bash(npx *)` obejmuje także Context7; węższe `allow` nie tworzy
w nim wyjątku. Szerokie `ask` również ma pierwszeństwo przed pasującym `allow`.
Copilot CLI dokumentuje pierwszeństwo `deny` nad `allow`.
VS Code Local nadaje pierwszeństwo pasującym regułom `false` przed `true`.

Są to różne silniki reguł, nie jeden wspólny format. Zanim podasz gotową regułę,
sprawdź dopasowanie argumentów, cytowanie, polecenia złożone i pierwszeństwo
w docelowym kliencie. Sam poprawny JSON nie dowodzi poprawnej polityki.

## Kiedy hook ma uzasadnienie?

Hook warto rozważyć, gdy wbudowane reguły nie wyrażają wygodnie potrzebnego
warunku albo potrzebujesz dodatkowej, mierzalnej logiki:

- sprawdzania całego wywołania i jego argumentów zamiast samego prefiksu;
- różnych decyzji zależnych od treści, pliku, gałęzi lub stanu repozytorium;
- uzasadnienia decyzji widocznego dla użytkownika lub agenta;
- testów wejście-wyjście dla jednej logiki używanej przez kilka klientów;
- dodatkowej walidacji lub kontrolowanej modyfikacji argumentów.

W tym przykładzie hook rozróżnia trzy przypadki:

```text
Pasujące, samodzielne zapytanie Context7 -> allow
Inny wykryty tekst wywołania npx         -> ask
Pozostałe wywołania                     -> brak decyzji
```

Pytanie o inną bibliotekę nie wymaga dopisywania jej do listy.
`library` przyjmuje niepustą cytowaną nazwę i pytanie; `docs` przyjmuje
identyfikator `/owner/library` (opcjonalnie z wersją) i niepuste cytowane
pytanie. Reguła obejmuje `npx` i `npx.cmd`, bez dodatkowych opcji poza
opcjonalnym pojedynczym `--yes` lub `-y`. Najpierw rozwiąż nazwę przez
`library`, potem użyj zwróconego identyfikatora w `docs`; hook bez stanu
nie weryfikuje, czy poprzedni krok się odbył.
Automatyczna zgoda dotyczy prostych cytowanych argumentów: bez `&`, `|`,
`<`, `>`, `^`, `%`, `!` i osadzonych podwójnych cudzysłowów także wewnątrz
apostrofów. Wyklucza też `‘ ’ “ ”` (PowerShell traktuje je jako delimitery)
i znaki sterujące ASCII `U+0000–U+001F`, `U+007F`; zwykłe polskie znaki
pozostają dozwolone. Podwójne cudzysłowy dodatkowo wykluczają `$`, backtick
i backslash.
To celowe zawężenie dla przenośności: Windows może przekazać `npx`/`npx.cmd`
do pliku wsadowego i `cmd.exe`, również przy wywołaniu z PowerShell.
Cytowanie w pierwszej powłoce nie gwarantuje bezpiecznego przekazania dalej.
Złożone pytania, dodatkowe opcje, interpolacja lub doklejone drugie polecenie
prowadzą do `ask`, nie `deny`. Nadal można je świadomie zatwierdzić.

## Koszt i korzyści

| Kryterium | Zwykłe permissions | Własny hook |
|---|---|---|
| Prosta, powtarzalna zgoda | Zwykle najlepszy wybór | Często zbędna komplikacja |
| Warunki i dodatkowa walidacja | Ograniczone językiem reguł | Możliwe w kodzie |
| Utrzymanie | Niewielka konfiguracja | Skrypt, runtime, testy, diagnostyka |
| Wiele klientów | Osobne formaty ustawień | Wspólna logika, nadal osobne adaptery |
| Obsługa błędów | Zapewniana przez klienta | Trzeba ją zaprojektować i sprawdzić |
| Ochrona systemu operacyjnego | Nie zastępuje sandboxa | Również nie zastępuje sandboxa |

Nie wybieraj hooka tylko dlatego, że jest bardziej elastyczny.
Elastyczność zwiększa również liczbę rzeczy, które mogą działać niepoprawnie.
Do samego wygodnego zatwierdzania Context7 zwykłe, wąskie `allow` może wystarczyć.

## Ograniczenia i obsługa błędów

Przykład używa konserwatywnego dopasowania tekstowego dla Bash i PowerShell,
z ograniczeniami uwzględniającymi przekazanie do pliku wsadowego Windows.
Nie rozpoznaje pełnej semantyki powłok. Może pytać o niewinny tekst
zawierający `npx`, a przeoczyć wywołanie ukryte w innym skrypcie.
Nie stanowi granicy bezpieczeństwa ani ochrony przed każdym obejściem.
Testy procesu sprawdzają decyzję dla tekstu wejściowego; nie uruchamiają tych
poleceń. Wykonanie end-to-end w Windows pozostaje niezweryfikowane.

Hooki nie mają identycznej obsługi błędów we wszystkich klientach:

- Copilot: niezerowy kod wyjścia procesu `preToolUse` (poza timeoutem)
  blokuje wywołanie; timeout pozostawia zwykłą ścieżkę uprawnień.
  Nazwa zdarzenia `PreToolUse` i alias narzędzia `Bash` są obsługiwane
  w formacie zgodności.
- Claude Code: kod wyjścia `2` blokuje obsługiwane zdarzenie; inne awarie
  co do zasady nie blokują, o ile nie skonfigurowano odpowiedniego mechanizmu
  blokowania przy błędzie. Nie traktuj dowolnego wyjątku Node.js jako zakazu.
- Dla VS Code sprawdź dokumentację wybranego harnessu. Współdzielony Copilot
  runtime i starszy Local nie są tym samym mechanizmem wykonawczym.

Skrypt zwraca strukturalne `allow` albo `ask` przy poprawnym wejściu.
Błędne wejście zgłasza wyjątkiem, bez udawania sukcesu. Nie dodaje własnej
konfiguracji blokowania przy awarii. Świadomie nie przedstawiamy go jako
administracyjnej polityki bezpieczeństwa.

Tryb bez użytkownika także zmienia wynik: Copilot CLI autopilot i cloud
agent odrzucają `ask`, bo nie mogą wyświetlić pytania.
Nie rozwiązuj tego przez masowe `allow`.
Zaplanuj zatwierdzony zakres pracy automatycznej albo użyj sesji interaktywnej.

## Jak zweryfikować decyzję?

1. Spisz oczekiwane zachowanie: automatyczna zgoda, pytanie czy zakaz.
2. Sprawdź, czy wystarczą natywne reguły. Nie kopiuj składni innego produktu.
3. Jeśli potrzebny jest hook, przetestuj poprawne i niepasujące polecenia.
4. Sprawdź dodatkowe opcje, cytowanie, interpolację i łączenie poleceń.
5. Sprawdź brak wpływu na inne narzędzia oraz obsługę błędnego wejścia.
6. Uruchom nową sesję docelowego klienta i sprawdź faktyczne pytanie o zgodę.
   Test samego procesu hooka nie dowodzi, że klient go załadował.

**Reguła do zapamiętania: najpierw permissions; hook dopiero wtedy, gdy jego
dodatkowa logika rozwiązuje konkretną potrzebę. `ask` i `deny` to różne decyzje.**

## Źródła

Kontrakt hooków Copilot i rozróżnienie harnessów VS Code sprawdzono ponownie
26.10.2026; tego dnia zweryfikowano też reguły cytowania PowerShell.
Pozostałe źródła i lokalna pomoc Copilot CLI 1.0.103: 25.10.2026.

- [Copilot CLI: opcje i uprawnienia narzędzi](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
  oraz polecenia `copilot help permissions` i `copilot help config`.
- [Copilot: konfiguracja, wejście, decyzje i błędy hooków](https://docs.github.com/en/copilot/reference/hooks-reference).
- [VS Code: zgody i automatyczne zatwierdzanie terminala](https://code.visualstudio.com/docs/agents/run/approvals).
- [VS Code: hooki i rozróżnienie harnessów](https://code.visualstudio.com/docs/agent-customization/hooks).
- [VS Code Local: kontrakt hooków](https://code.visualstudio.com/docs/agents/reference/hooks-reference).
- [Claude Code: uprawnienia i pierwszeństwo reguł](https://code.claude.com/docs/en/permissions).
- [Claude Code: hooki, format JSON i obsługa błędów](https://code.claude.com/docs/en/hooks).

- [Microsoft PowerShell: reguły cytowania i typograficzne cudzysłowy](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_quoting_rules?view=powershell-7.5).
