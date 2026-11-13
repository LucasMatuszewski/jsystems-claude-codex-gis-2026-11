# Podsumowanie - dzień 4, 13 listopada 2026

## Zakres dnia

Czwarty dzień szkolenia JSystems dotyczył praktycznej pracy z Claude Code i Codex: analizy danych z użyciem modeli decyzyjnych i LLM, planowania implementacji, Skills, uprawnień i sandboxa, a także integracji przez MCP. OpenCode pojawił się jako dodatkowy worker CLI, a nie jako główne narzędzie kursu.

## 1. Analiza zdjęć i ocena modeli

Prowadzący pokazał pipeline do analizy danych mapowych i porównania Jev, Luna Decisions oraz Luna LLM. Raport obejmował 558 par zdjęcie-droga ze zbioru 561 zdjęć. Odczyt obrazów przez modele wykonywano na wybranej próbce. Wyniki trafiały do raportów, a osobne narzędzie służyło do ręcznej kontroli jakości i porównania decyzji z etykietami referencyjnymi.

Przykłady implementacji:

- [PR #10 - narzędzie do analizy danych mapowych: Jev, Luna Decisions i Luna LLM](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/pull/10)
- [PR #11 - osobne narzędzie do manualnej ewaluacji](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/pull/11)
- [Raport map QA](https://devpowers.com/szkolenia/jsystems/tomtom-ai-2026-11/reports/map-qa/report.html)
- [Podsumowanie raportu](https://devpowers.com/szkolenia/jsystems/tomtom-ai-2026-11/reports/map-qa/summary.html)
- [Manualny przegląd decyzji](https://devpowers.com/szkolenia/jsystems/tomtom-ai-2026-11/reports/map-qa/review/review.html)

Modele decyzyjne mogą być przydatne do szybkiej klasyfikacji, ale ich jakość trzeba mierzyć, a wyniki sprawdzać. Do wiarygodnej oceny potrzebny jest poprawny zbiór referencyjny. W pokazanym raporcie etykiety referencyjne przygotowały modele AI, dlatego wymagały ręcznej weryfikacji. Warto zestawiać wyniki z pełnym modelem, badać przypadki błędne i dobierać próg pewności na podstawie walidacji, zamiast zakładać, że pojedynczy wynik confidence sam potwierdza poprawność. Wyniki ręcznej oceny można wykorzystać jako dane do dalszej analizy.

Przy zlecaniu analizy należy podać wymagania techniczne, takie jak oczekiwana rozdzielczość i format danych. Jeżeli agent ma delegować pracę, instrukcja lub plan powinny określać tę delegację wprost, łącznie z tym, co ma wykonać worker i jak sprawdzić jego wynik.

## 2. Planowanie pracy agentów

Planowanie omówiono w kontekście Spec-Driven Development. Specyfikacja, PRD i ADR dostarczają kontekstu oraz decyzji; plan rozpisuje kolejność realizacji. Przed rozpoczęciem implementacji warto:

1. Zebrać wymagania i materiały wejściowe.
2. Przygotować plan z logicznymi etapami i priorytetami, nawet jeśli aplikacja ma powstać w jednym ciągu pracy.
3. Poprosić agenta o przegląd planu i rekomendacje zmian.
4. Sprawdzić spójność `AGENTS.md`, PRD, ADR i planu. Plan powinien odwoływać się do źródeł prawdy, a nie powielać większości ich treści.
5. Określić sposób delegowania zadań, jeśli jest wymagany, i uwzględnić testy oraz końcową walidację człowieka.
6. Dopiero po przeglądzie uruchomić realizację planu jako cel.

Jako praktyczny punkt odniesienia podano plan rzędu 200-300 linii i sprawdzenie, czy nie przekracza 500 linii. Długość nie zastępuje jakości: plan ma być czytelny, spójny z PRD i ADR oraz na tyle szczegółowy, by agent mógł pracować etapami. Przykładowa instrukcja uruchomienia celu:

```text
/goal implement the plan from @docs/plans/implementation-plan.md Before completing the plan, make sure that all conditions from the ADR and PRD files are met.
```

Przykładowy prompt planowania z macierzą subagentów, zależnościami i mapą zadań znajduje się w [repozytorium szkoleniowym](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Prompt%20examples/Plan-SubAgents-matrix-dependency-map.md).

Przy ograniczonych, dobrze określonych zadaniach warto rozważyć tańsze, mniejsze workery. W przykładzie szkoleniowym wymieniono Claude Code subagents z Haiku 5.5 do większości takich zadań, Codex Sol 6.1 do trudniejszych zadań i code review oraz Luna 6 do prostszych zadań i researchu. OpenCode z MiMo-V2.6-FlashXiaomi Token Plan pokazano jako dodatkowego workera CLI w headless mode. Jeśli plan zakłada delegowanie do agentów CLI, należy zbadać ich uruchamianie w headless mode i zawrzeć konkretne instrukcje w planie.

Materiały o podejściu spec-driven:

- [Spec-Driven Development](https://specs.md/)
- [Fire Flow](https://specs.md/fire-flow/overview)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [Przykładowe Skills dla SDD, PRD, ADR i planowania](https://www.skills.sh/search?q=spec), [PRD](https://www.skills.sh/search?q=prd), [ADR](https://www.skills.sh/search?q=adr), [planów](https://www.skills.sh/search?q=plan)

## 3. Sesje i tworzenie Skills

Skill to wielokrotnie używana instrukcja, która opisuje, kiedy i jak agent ma wykonać określony rodzaj pracy. Można tworzyć go na podstawie historii sesji: wskazać sesję, poprosić o wydobycie skutecznych kroków i popełnionych błędów, a następnie wygenerować i sprawdzić plik Skill. Głównym elementem jest instrukcja Markdown w odpowiednim folderze Skills.

Przykładowy Skill do planowania powinien określać:

- sygnały, kiedy należy go użyć;
- wymagane dane wejściowe i sposób pracy z ID sesji;
- tryb pytań, gdy brakuje informacji;
- wymagane elementy planu i zasady delegowania;
- przegląd `AGENTS.md`, PRD, ADR i planu przed implementacją;
- kontrolę wyników i sposób obsługi błędów z wcześniejszej sesji.

Szablony mogą opisywać różne warianty pracy, na przykład "subagents only" albo delegowanie do workerów CLI w headless mode. Skill warto sprawdzić w praktyce i poprawić, jeśli pierwsze użycie ujawni niejasne instrukcje. Do inspiracji przy tworzeniu Skills: [skill-creator](https://www.skills.sh/search?q=skill-creator). W szkoleniu wskazano zapis w `.agents/skills`.

Do podglądu szczegółów wywołań narzędzi używano `Ctrl+T` w Codex i `Ctrl+O` w Claude. Materiały o pracy CLI bez interfejsu: [tryby headless, JSON streaming i CI/CD](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/Headless%20agents%20-%20CLI%20automation%2C%20JSON%20streaming%2C%20subscriptions%20and%20CI-CD.md).

Przydatne skróty sesji pokazane w Claude:

```text
/btw
/fork
/status
```

`/btw` pozwala zadać poboczne pytanie bez przerywania bieżącej pracy agenta. `/fork` tworzy kopię sesji wraz z jej historią, którą można wykorzystać do pracy od wybranego punktu. `/status` służy do sprawdzenia stanu sesji; podczas ćwiczenia użyto go także do odnalezienia ID sesji.

## 4. Personalizacja, statusline i konfiguracje

Instrukcje dla agentów można umieszczać na poziomie projektu, użytkownika oraz ustawień konta webowego. Przykład personalizacji ChatGPT omawiany podczas sesji obejmował swobodny, ale profesjonalny ton, zwięzłe odpowiedzi, instrukcje krok po kroku i jasne oznaczanie opinii. Ustawienia personalizacji Claude są dostępne w [Claude Code](https://claude.ai/code#settings/personalization); ustawienia ChatGPT wskazano w [personalizacji ChatGPT](https://chatgpt.com/settings/personalization?instructions=chatgpt).

Dla Codex pokazano konfigurację statusline przez `/statusline`; elementy wybiera się klawiszami strzałek, zatwierdza spacją i ustawia kolejność. W Claude `/statusline` tworzy plik skryptu statusline. Przykładowe ustawienia Claude wskazane w materiałach:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/statusline.sh",
    "refreshInterval": 30
  }
}
```

Przykładowy skrypt znajduje się w `course-materials/agent-configs/claude/statusline.sh`, a ustawienia w `course-materials/agent-configs/claude/settings.json`. Do pracy skryptu wspomniano instalację `jq`. Dla Codex pokazano ustawienia `approvals_reviewer` i `approval_policy` w `config.toml`; dokładne ustawienia powinny być dobrane do aktywnego sandboxa i potrzeb danego środowiska, a nie kopiowane bez sprawdzenia. Przykładowe pliki są w repozytorium kursu.

Omówiono też rozdzielenie ustawień na osobne katalogi. Dla Claude służy do tego `CLAUDE_CONFIG_DIR`, a dla Codex `CODEX_HOME`. Przykładowa zmienna środowiskowa Claude:

```text
CLAUDE_CONFIG_DIR=/home/you/.claude-work
```

Dokumentacja Claude: [zmienne środowiskowe](https://code.claude.com/docs/en/env-vars). Dla Codex wskazano [lokalizację konfiguracji i danych](https://learn.chatgpt.com/docs/config-file/config-advanced#config-and-state-locations). Przykłady konfiguracji Bash i PowerShell są w [plikach konfiguracyjnych kursu](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/tree/main/course-materials/agent-configs).

## 5. Permissions i sandbox

Uprawnienia mogą być ustawiane na poziomie użytkownika i projektu, a część polityk może być narzucona przez organizację. Rozmowa dotyczyła konfiguracji Claude Code i Codex; oba narzędzia mają własne mechanizmy i składnię, więc nie należy zakładać, że reguły jednego można bezpośrednio przenieść do drugiego.

W przykładach Codex omówiono tryby sandboxa, w tym `elevated` i `unelevated`, oraz wariant Windows MXC. Podczas sesji podano, że `elevated` może wymagać uprawnień administracyjnych do konfiguracji, `unelevated` jest wariantem niewymagającym takiej konfiguracji, a na Linuksie Codex korzysta z Bubblewrap. MXC wskazano jako nowy sandbox Windows, wymagający osobnego sprawdzenia zgodności. Podkreślono, że dobór zależy od środowiska i nie należy zmieniać ustawień bez sprawdzenia skutków.

Przykładowy fragment TOML podany na czacie:

```toml
[windows]
sandbox = "elevated"

[features]
# Tested course baseline; MXC requires a separate acceptance run.
prefer_mxc = false
network_proxy = false
```

Na głównym poziomie `config.toml`, przed nagłówkami sekcji, pokazano także:

```toml
approvals_reviewer = "auto_review"
approval_policy = "on-request"
personality = "pragmatic"
```

To ustawienia przykładowe, nie uniwersalna polityka dla każdego projektu. Konfiguracje i reguły ułatwiają ograniczanie działań, ale nie są pełną gwarancją bezpieczeństwa. Reguły powinny być wąskie i dopasowane do pracy: przykładowo mogą wymagać zatwierdzenia operacji sieciowych lub blokować określone destrukcyjne polecenia. Ochrona ważnych gałęzi powinna być dodatkowo ustawiona po stronie hostingu repozytorium.

Materiały do dalszego sprawdzenia:

- [Przykładowe profile permissions Codex](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/.codex/config.toml#L304)
- [Instrukcja permissions Codex](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/agent-configs/codex/PERMISSIONS.md)
- [Przykładowy plik permissions Codex](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/agent-configs/codex/permissions.toml)
- [Przykładowe ustawienia Claude](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/agent-configs/claude/settings.json)
- [Przykładowe reguły Codex](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/agent-configs/codex/rules/course.rules)
- [Materiały o konfiguracji i uprawnieniach Claude, Codex i Copilot](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/config-files-and-permissions.md)
- [Porównanie sandboxa Claude i Codex](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/Sandboxing-and-harness-in-Codex-vs-ClaudeCode.md)
- [Sandbox Windows Codex](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/codex-sandbox-facts-and-limitations-2026-11-06.md)
- [Rozwiązywanie problemów z sandboxem Windows](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/codex-windows-sandbox-troubleshooting-2026-10-15.md)

## 6. Code Mode i hooks

Code Mode oznacza pisanie skryptów, które wykonują wiele operacji na raz, na wielu plikach lub przez wiele poleceń. To sposób organizacji pracy kodem, a nie osobny model. Materiał: [Code Mode i migracje algorytmiczne](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/code-mode-and-algorithmic-code-migration-2026-10-13.md).

Hooks w Claude i Codex to zaawansowany temat dotyczący uruchamiania działań w określonych punktach przepływu pracy. Udostępnione materiały:

- [Przykłady hooks w repozytorium kursu](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/tree/main/course-materials/hooks-example)
- [Dokumentacja hooks Claude](https://code.claude.com/docs/en/hooks)
- [Agent hook configuration](https://code.claude.com/docs/en/hooks#agent-hook-configuration)

## 7. MCP i integracje

MCP standaryzuje sposób, w jaki agent uzyskuje dostęp do narzędzi udostępnianych przez serwer. W sesji rozróżniono kilka ścieżek integracji:

1. Gotowy konektor chmurowy w aplikacji, dostępny zależnie od usługi i konfiguracji konta.
2. Custom connector, w którym podaje się HTTPS URL serwera MCP.
3. Lokalną konfigurację serwera dla projektu, np. przez `.mcp.example.json`.
4. Własny serwer MCP, na przykład dla wdrożenia on-premises.
5. Skill uruchamiający lokalny skrypt i korzystający z API, jako odrębny wariant integracji.

Rovo Cloud MCP, custom connector i własny wrapper lub Skill do API dla środowiska on-premises to różne drogi. Podczas próby połączenia z Atlassian pojawił się komunikat o braku dostępu do serwera. W diagnostyce sprawdzano adres serwera i jego dostępność.

Materiały wskazane podczas sesji:

- [Wprowadzenie do MCP](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro)
- [Budowanie serwera MCP](https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server)
- [Atlassian Rovo MCP](https://support.atlassian.com/atlassian-ai-gateway/docs/get-started-with-the-atlassian-remote-mcp-server/)
- [Dokumentacja deweloperska Rovo MCP](https://developer.atlassian.com/cloud/rovo-mcp/)
- [Dodawanie custom connector w Claude](https://claude.ai/customize/connectors)
- [Skill do pracy z Atlassian on-premises](https://github.com/EdukeyTeam/agent-toolbox/tree/main/skills/atlassian-onprem-safe)
- [Informacje o Atlassian Personal Access Token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)

Dane dostępowe należy przechowywać poza promptami, historią poleceń i repozytorium. Skill lub skrypt powinien ujawniać agentowi tylko potrzebne operacje i dane. W przypadku systemu on-premises wybór rozwiązania i uwierzytelniania zależy od zatwierdzonej konfiguracji organizacji.

### Pluginy i marketplace

Omówiono także udostępnianie rozszerzeń przez marketplace. Jako wzorzec repozytorium pokazano [EdukeyTeam/agent-toolbox](https://github.com/EdukeyTeam/agent-toolbox), w tym plik [`.claude-plugin/marketplace.json`](https://github.com/EdukeyTeam/agent-toolbox/blob/main/.claude-plugin/marketplace.json). Administrator może dodać marketplace w [ustawieniach organizacji Claude](https://claude.ai/admin-settings/skills?tab=marketplaces). To odrębny element konfiguracji od adresu serwera MCP i jego poświadczeń.

## 8. Sesje zdalne, monitory i wielu agentów

Wspomniano o monitorach Claude oraz Shell. Monitory mogą uruchamiać działania w tle według czasu lub zdarzenia, na przykład ponownie sprawdzić stan zadania. Ich zastosowanie wymaga dokładnej instrukcji, co i kiedy ma być sprawdzane.

Funkcje zdalne zostały przypisane do Claude Code i mają różne cele:

- `/rc` lub `/remote-control` służy do kontroli lokalnej sesji z chmury. Dokumentacja: [Remote Control](https://code.claude.com/docs/en/remote-control).
- `/teleport` pobiera sesję Claude Code z chmury do lokalnego terminala, aby można ją było tam kontynuować. Z poziomu powłoki służy do tego także `claude --teleport`. Dokumentacja: [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web).

W Remote Control wykonanie pozostaje na lokalnym urządzeniu. Teleport pozwala wznowić w lokalnym terminalu pracę rozpoczętą w sesji chmurowej.

Do zarządzania wieloma agentami pokazano [Herdr](https://herdr.dev/) oraz materiały o [menedżerach agentów i agentach zdalnych](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/blob/main/course-materials/Research/agent-managers-and-remote-agents.md). Wspomniano też Termux jako shell na Androidzie. Dodatkowo omówiono zatrzymywanie serwera sesji Claude działającego w tle:

```text
claude daemon stop --any
```

## 9. Obserwowalność i materiały kursu

Do obserwowalności agentów wskazano [Langfuse](https://langfuse.com/) - narzędzie do analizy przebiegu, kosztów i jakości; można je podłączyć do [OpenRouter](https://openrouter.ai/) albo bezpośrednio w kodzie aplikacji. Jako przykład rozwoju modeli świata podano [Genie 3](https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/).

Pozostałe przydatne materiały:

- [Repozytorium kursu](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11/tree/main)
- [Materiały szkoleniowe JSystems TomTom AI](https://devpowers.com/szkolenia/jsystems/tomtom-ai-2026-11/)
- [Checklista po szkoleniu - harness](https://devpowers.com/szkolenia/jsystems/tomtom-ai-2026-11/checklisty.html#harness)
- [Ankieta szkoleniowa](https://ankiety.jsystems.pl/)

## Limity i dostępność usług

Stan wykorzystania Codex sprawdzano przez `/usage`, a dostępne resety przez `Redeem reset`. Do podglądu wykorzystania pokazano [ustawienia ChatGPT](https://chatgpt.com/settings/usage?tab=overview) i [ustawienia Claude](https://claude.ai/new#settings/usage). Przed wykorzystaniem resetu sprawdź jego zakres i termin ważności.

Przy problemach z dostępnością aplikacji warto sprawdzić [status Claude](https://status.claude.com/) oraz [status OpenAI](https://status.openai.com/).

## Praca własna

1. Przygotuj Skill do tworzenia aplikacji z pipeline'em modelu decyzyjnego dla dowolnych danych, korzystając z doświadczeń z sesji narzędzia szkoleniowego.
2. Przygotuj Skill do tworzenia narzędzia Manual QA, które pozwala ręcznie walidować decyzje modelu.
3. W Skillu planistycznym uwzględnij pracę na historii wybranej sesji, pytania przy brakujących danych, warianty delegowania oraz przegląd `AGENTS.md`, ADR, PRD i planu przed uruchomieniem implementacji.
4. Przećwicz tryb pytań z agentem, a konfigurację statusline i uprawnień wykonuj na podstawie dokumentacji i profilu dopasowanego do własnego środowiska.
5. Zachowaj pracę z wirtualnego środowiska szkoleniowego w GitHub lub pobierz potrzebne pliki lokalnie przed zamknięciem środowiska.
6. Wypełnij ankietę szkoleniową pod linkiem powyżej.

Repozytorium kursu zawiera aktualizowane przykłady konfiguracji i dodatkowe materiały.
