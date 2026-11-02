# Agenci, uprawnienia i budżet tokenów

Stan dokumentacji: 24.10.2026. Sprawdź wersję narzędzia i dostępne polecenia w swojej sesji. Używaj istniejącego szablonu aplikacji lub wskazanego repozytorium legacy; nie zlecaj budowy nowej aplikacji w miejsce przygotowanego projektu.

## Krótka konfiguracja Claude Code

W `/config` ustaw `Verbose output: false` oraz `Output style: Concise`. Styl Concise jest wbudowany od 2.1.237; w starszym wydaniu wybierz dostępny styl lub utwórz własny krótki styl. W JSON nazwa to `"outputStyle": "Concise"`, z wielką literą. Krótka odpowiedź zmniejsza objętość tekstu, ale nie usuwa kosztu długiego wejścia ani pracy narzędzi. [Style odpowiedzi](https://code.claude.com/docs/en/output-styles).

Ćwiczenie statusline: sprawdź `jq --version`. Jeśli brakuje jq, na Ubuntu/Debian zainstaluj pakiet `jq` zgodnie z uprawnieniami środowiska:

```bash
sudo apt-get install jq
```

W Claude Code wpisz:

```text
/statusline Skonfiguruj pasek na podstawie course-materials/agent-configs/claude/statusline.sh. Pokaż mi zmianę ustawień i sprawdź skrypt na syntetycznym JSON, zanim go włączysz. Zachowaj istniejące ustawienia.
```

Skrypt otrzymuje JSON na stdin i pokazuje m.in. kontekst, koszt szacunkowy oraz cache. Sprawdź go bez płatnego wywołania modelu:

```bash
printf '%s' '{"model":{"id":"example","display_name":"Demo"},"workspace":{"current_dir":"/tmp/demo"},"context_window":{"used_percentage":25},"prompt_cache":{"hit_ratio":0.88}}' | bash course-materials/agent-configs/claude/statusline.sh
```

Oczekiwany fragment: `Cache: 88%`. Brak pola cache nie jest wynikiem 0%. Udział tokenów odczytanych z cache dotyczy głównej rozmowy, nie liczby zapytań ani automatycznej zniżki całego rachunku. [Statusline](https://code.claude.com/docs/en/statusline).

## Zużycie: sprawdzaj właściwy widok

| Narzędzie | Co sprawdzić | Źródło |
|---|---|---|
| Claude Code | `/usage`: koszt sesji, użycie planu i aktywność; `/cost` jest aliasem tego polecenia | [Polecenia Claude Code](https://code.claude.com/docs/en/commands) |
| Codex CLI | `/usage`: zużycie konta; `/status`: informacje o sesji i kontekście | [Codex: /usage](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-view-account-usage-with-usage) |
| Copilot CLI | `/usage`: statystyki; znaczenie opłat sprawdź dla bieżącego planu i modelu | [Polecenia Copilot CLI](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#slash-commands-in-the-interactive-interface) |

Zapisz porównanie przed i po jednym zadaniu: model, wielkość kontekstu, czas, użycie oraz czy zmiana przeszła testy i review. Liczy się koszt zaakceptowanej zmiany, z poprawkami, nie tylko cena tokena.

Opcjonalnie obejrzyj [caveman](https://github.com/juliusbrussee/caveman) i [ponytail](https://github.com/DietrichGebert/ponytail/blob/main/skills/ponytail/SKILL.md). Przeczytaj instrukcje przed instalacją i porównaj wynik na tym samym zadaniu; deklaracje oszczędności autorów nie gwarantują wyniku w Twoim projekcie. Zachowaj kryteria odbioru, błędy i ważne ryzyka w pełnej postaci.

Propozycja narzędzia do analizy lokalnych sesji: [agent-usage-analytics, SKILL.md na gałęzi propozycji](https://github.com/EdukeyTeam/agent-toolbox/blob/skill/agent-usage-analytics/skills/agent-usage-analytics/SKILL.md), [PR #25](https://github.com/EdukeyTeam/agent-toolbox/pull/25). Oczekuje na przegląd; nie jest wymaganą instalacją. Logi sesji mogą zawierać treść projektu i dane osobowe, więc analizuj je lokalnie zgodnie z polityką danych.

## Który rodzaj agenta wybrać

| Mechanizm | Kiedy pomaga | Co ustalić |
|---|---|---|
| Jeden agent | Mała, spójna zmiana | Zakres, dowód wyniku i punkt odbioru |
| Subagent doraźny | Jednorazowe wydzielone zadanie | Brief, model, pliki, wejście i wynik |
| Własna definicja subagenta | Powracająca rola lub stałe ograniczenia narzędzi | Krótka definicja, uprawnienia, model |
| Zespół agentów | Niezależne zadania z potrzebą koordynacji | Właściciele plików, zależności, integrator, limit równoległości |
| Headless CLI | Powtarzalne zadanie przez skrypt lub pipeline | Wejście, zakończenie, kod wyjścia, raport i minimalne uprawnienia |
| Workflow | Sekwencja etapów z bramkami | Zależności, ponowienia, warunek zatrzymania i odbiór |
| Goal | Dłuższy cel kontynuowany przez dany harness | Budżet, kryterium końca, monitoring i możliwość zatrzymania |

Nazwy i dostępność różnią się między narzędziami. Goal nie daje dodatkowych uprawnień ani prawa do publikacji. Do małego zadania wybierz jednego agenta; do jednorazowej delegacji zwykle wystarczy agent doraźny. Własne definicje twórz dopiero, gdy rola wraca. Domyślny tani wykonawca kodu i testów to Haiku w Claude lub Luna w Codex; w Copilocie wybierz najtańszy odpowiedni model dostępny w aktualnym planie. Orkiestrator rozstrzyga decyzje i sprawdza wyniki. [Przykład skilla do delegowania](../skills-examples/headless-task/SKILL.md).

Worktree twórz tylko wtedy, gdy agenci muszą równolegle zmieniać te same pliki, np. przy różnych zadaniach w tym samym kodzie. W pozostałych przypadkach rozdziel zadania według plików lub folderów, poinformuj agentów o równoległej pracy i zapisz plan zależności; wspólne zmiany scalaj kolejno.

W AGENTS.md zapisz regułę: agent nie tworzy worktree domyślnie. Osobne instalacje zależności zużywają dysk i CPU, a agenci często zapominają je posprzątać.

Stan Git (gałąź, indeks i commity) zmienia tylko jeden koordynator; pozostali agenci edytują przydzielone pliki. Worktree nie usuwa konfliktów zmian tych samych plików - rozwiąż je przy scalaniu.

## Permissions, hooks i rules

Instrukcja opisuje zasadę; uprawnienie ogranicza narzędzie, a hook może deterministycznie sprawdzić zdarzenie i zatrzymać niedozwoloną operację. Zakaz "nie kasuj bazy" zacznij od konta bez prawa usuwania i blokady narzędzia, a następnie dodaj krótką zasadę w AGENTS.md. Sprawdź próbę niedozwolonej operacji na danych syntetycznych. Żaden prosty wzorzec polecenia nie rozpoznaje wszystkich aliasów i obejść.

Porównaj [mapę uprawnień Codex](../agent-configs/codex/PERMISSIONS.md), [przykłady hooków](../hooks-example/README.md) i [uprawnienia Claude Code](https://code.claude.com/docs/en/permissions). Do ćwiczenia wybierz jedną blokadę i sprawdź zarówno dozwolony, jak i zabroniony przypadek. Nie włączaj wszystkich przykładów naraz.

## Logowanie bez automatycznego powrotu na localhost

W sprawdzonym Claude Code 2.1.310 polecenie `claude auth login --help` nie pokazuje flagi wymuszającej logowanie kodem urządzenia. `--sso` wymusza SSO, a nie taki tryb. Oficjalna instrukcja opisuje ręczne wklejenie kodu, gdy przeglądarka nie może automatycznie wrócić do lokalnego portu. Nie przedstawiaj wymyślonej flagi jako rozwiązania. [CLI](https://code.claude.com/docs/en/cli-reference), [opis problemu lokalnego logowania](https://code.claude.com/docs/en/errors#couldnt-start-the-local-listener-that-receives-the-browser-sign-in).

Sprawdzenie dokumentacji i pomocy nie zastępuje testu logowania na koncie uczestnika. Nie wylogowuj aktywnej sesji w celu demonstracji.

## Dalsza lektura

[Badania o rynku pracy i zmianie roli programisty, slajd 3](https://devpowers.com/szkolenia/jsystems/claude-code-2026-10/Prezentacja_02_Podstawy_AI.html#3). Oddziel wyniki badania, wypowiedź autora i prognozę; nie obiecuj uniwersalnego wzrostu produktywności.
