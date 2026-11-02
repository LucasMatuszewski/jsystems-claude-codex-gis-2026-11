# Uprawnienia GitHub Copilot CLI  -  przykład

Uruchom z katalogu repozytorium:

```powershell
& .\course-materials\agent-configs\copilot\start-copilot.ps1
```

Na Linux/macOS:

```bash
bash course-materials/agent-configs/copilot/start-copilot.sh
```

Przykład automatycznie zatwierdza cztery polecenia do przeglądania zmian i historii Git (`status`, `diff`, `log`, `show`). Odrzuca bez pytania wskazane prefiksy pushów do `main`, `master` i `prod` oraz force-pushów, a także m.in. `git reset`, `git clean` i zapis plików `.env`. Uczestnicy mogą wypychać własne gałęzie i otwierać PR-y; pozostałe działania nie dostają dodatkowej zgody z tego przykładu, więc Copilot stosuje zwykłe reguły i wcześniej zapisane decyzje. Reguły obowiązują tylko w sesji uruchomionej tym skryptem. Możesz przekazać własne argumenty do `copilot` po nazwie skryptu.

Oba skrypty mają identyczne 69 prefiksów odmowy dla pushów: 30 wariantów chronionych gałęzi na `origin`/`upstream`, z `-u`/`--set-upstream` przed lub po nazwie zdalnego repozytorium, oraz 39 wariantów z `--force`, `-f` lub `--force-with-lease`. Przykładowa reguła to `--deny-tool='shell(git push origin main:*)'`. Dokumentacja potwierdza końcowe `:*`, nie dowolne wildcardy wewnątrz polecenia. Same prefiksy mogą przepuścić `git push` na aktywnej chronionej gałęzi, `HEAD:main`, inne nazwy repozytoriów, kolejności opcji i późniejsze flagi force. Ochrona gałęzi w GitHub/Bitbucket jest właściwym zabezpieczeniem; zobacz [porównanie narzędzi](../README.md#protected-branch-push-policy). Agent do przeglądu bez nadzoru nadal ma zakaz wszystkich pushów.

To **reguły zgód CLI**, a nie izolacja procesu. Nie traktuj ich jako ochrony sekretów przed dowolnym poleceniem powłoki. Dla pracy bez nadzoru użyj także [piaskownicy Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview#use-sandboxing) albo odizolowanego środowiska.

Składnia Copilota to `shell(git status:*)`, a nie składnia Claude Code `Bash(git status:*)`. Copilot CLI obecnie nie obsługuje współdzielonych list `allow`/`deny` w `.github/copilot/settings.json`: nieznane klucze repozytorium są ignorowane. Lokalny `~/.copilot/permissions-config.json` zapisuje tylko zatwierdzenia przypisane do bezwzględnej ścieżki repozytorium; nie obsługuje reguł odmowy ani przenośnej konfiguracji dla zespołu. Dlatego przykład używa flag `--allow-tool` i `--deny-tool` przy starcie.

Sprawdzone z Copilot CLI 1.0.88 przed zmianą polityki: `git status --short` wykonał się bez pytania, a wcześniejszy zakaz wszystkich pushów odrzucił `git push --help`. Obecna polityka nie blokuje tego prefiksu. Skrypty mają zgodne argumenty; rzeczywiste egzekwowanie nowych reguł trzeba sprawdzić na wersji uczestnika, ponieważ samo parsowanie konfiguracji tego nie potwierdza.

Źródła: [reguły narzędzi](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools), [zakres ustawień i zapisanych zgód](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference), [składnia poleceń](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference).


## Instrukcje, testy i zadanie w chmurze

[Ćwiczenie Copilot: konfiguracja, testy i cloud agent](../../exercises/copilot-testing-and-cloud.md) łączy instrukcje repozytorium, reguły dla testów, prompt, skill, profil agenta i istniejący przykład hooka. Pracujesz na rzeczywistej aplikacji i jednym kryterium jej PRD.

[Profil test-engineer](agents/test-engineer.agent.md) jest nieaktywnym przykładem. Po przeczytaniu i świadomej decyzji możesz skopiować go do `.github/agents/` projektu. Lista narzędzi nie jest piaskownicą plików: uprawnienia poleceń i katalogów ustal oddzielnie. Profil nie narzuca modelu; wybierz aktualnie dostępny, odpowiedni kosztowo model przed zadaniem.

[Skill test-evidence](skills/test-evidence/SKILL.md) pokazuje odczyt i ocenę dowodów dla jednej funkcji. Pozostaje przykładem w materiałach; nie jest automatycznie aktywnym skillem projektu. Dopiero po przeglądzie włącz go zgodnie z konwencją Twojego klienta, np. jako `.github/skills/test-evidence/SKILL.md`, i sprawdź wykrycie.

Ceny i dostępność modeli sprawdź w aktualnej tabeli [Models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing): zużycie tokenów przelicza się na AI credits (1 kredyt = 0,01 USD). `/model` służy do wyboru modelu lub trybu Auto, a `/usage` pokazuje statystyki sesji: sumy tokenów per model, a na kontach rozliczanych tokenowo także zużycie AI credits każdego modelu. Na starszych planach z rozliczeniem requestowym obowiązują premium requests i mnożniki modeli oznaczone jako legacy; nie utożsamiaj kredytów z requestami i nie zakładaj, że model z dawnej tabeli 0x nadal jest najtańszy lub dostępny. [Rozliczanie](https://docs.github.com/en/copilot/concepts/billing), [modele](https://docs.github.com/en/copilot/reference/ai-models/supported-models).

Profil zawiera `include-custom-instructions: true`, aby przy delegacji przez Copilot CLI jako subagent dostał również instrukcje repozytorium. Przy wyborze profilu jako głównego agenta sesji te instrukcje i tak obowiązują. Sprawdź obsługę w używanej wersji; koordynator nadal przekazuje dokładny kontrakt zadania. [Instrukcje a własny subagent](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli#applying-your-repositorys-custom-instructions-to-a-custom-agent).

Automatyczne dobieranie profilu jest wyłączone osobno dla CLI (`infer: false`) i cloud agenta (`disable-model-invocation: true`). Nazwy pól są zależne od klienta; samo pole cloud nie zastępuje ustawienia CLI. [Pola profilu CLI](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agent-frontmatter-fields).

[Profil reviewer](agents/reviewer.agent.md) jest osobnym, nieaktywnym przykładem tylko do odczytu i wyszukiwania. Koordynator przekazuje plik diffu i dowody testów; profil nie może sam uruchomić git ani testów. Wybierz model odpowiedni do przeglądu i nie utożsamiaj rekomendacji z uprawnieniem do merge. Pełne prompty testów, flaky, notebooka i budowy skilla są podlinkowane w ćwiczeniu.

Istniejący przykład CodeReview używa konkretnych nazw narzędzi, których dostępność trzeba potwierdzić w docelowym kliencie. Nie zakładaj, że jest gotowym profilem CLI. Przykład reviewer używa udokumentowanych aliasów read/search i wymaga dostarczonych dowodów.
