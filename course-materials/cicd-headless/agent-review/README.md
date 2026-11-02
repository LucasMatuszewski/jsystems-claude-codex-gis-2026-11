# Code review i security review od agenta w CI/CD

Zestaw do uruchamiania agenta bez interfejsu (headless) w Azure Pipelines, GitLab CI i Bitbucket Pipelines. Agent przegląda zmiany z pull requestu, komentuje PR, dopisuje wynik do zadania w Jira i opcjonalnie zmienia jego status. Do wyboru cztery CLI: **Copilot, Claude Code, Codex, OpenCode**.

## Jak to działa

1. Pipeline startuje z własnego obrazu z czterema CLI ([Dockerfile](Dockerfile)).
2. [agent_review.sh](agent_review.sh) zapisuje diff względem gałęzi docelowej i uruchamia wybranego agenta z [promptem do code review](prompts/code-review.md) albo [security review](prompts/security-review.md). Agent może czytać pliki i uruchamiać `git diff/log/show`; nie może edytować plików ani pushować.
3. Jeśli nazwa gałęzi zawiera klucz Jira (np. `feature/SHOP-123-zwroty`), skrypt pobiera treść zadania, a agent sprawdza, czy zmiana realizuje to, o co w nim chodzi.
4. [post_review_comment.sh](post_review_comment.sh) dodaje wynik jako komentarz do PR, [jira_update.sh](jira_update.sh) jako komentarz w Jira i opcjonalnie przenosi zadanie do statusu np. "In Review".

## Pipeline'y

| Platforma | Plik | Przykładowy agent |
|---|---|---|
| Azure Pipelines | [pipelines/azure-pipelines.yml](pipelines/azure-pipelines.yml) | Copilot |
| GitLab CI | [pipelines/.gitlab-ci.yml](pipelines/.gitlab-ci.yml) | Claude Code |
| Bitbucket Pipelines | [pipelines/bitbucket-pipelines.yml](pipelines/bitbucket-pipelines.yml) | Codex (review), OpenCode (security) |
| GitHub Actions | [../github-actions/](../github-actions/) | Claude Code |
| GitLab CI (przetestowane) | [../gitlab-codex-review/.gitlab-ci.yml](../gitlab-codex-review/.gitlab-ci.yml) | Codex przez OpenRouter |

Agenta zmieniasz jedną zmienną: `AGENT=copilot|claude|codex|opencode`. Każdy plik zaczyna się od listy kroków konfiguracji.

## Przetestowany przykład: GitLab CI i Codex

Sprawdzone 30.10.2026 na self-managed GitLab 19.5.3 z runnerem Docker: [pipeline](../gitlab-codex-review/.gitlab-ci.yml) buduje projekt Maven z testami, a job `codex-review` w każdym merge requeście uruchamia `codex exec` (Codex CLI 0.165.0 z [Dockerfile](Dockerfile), model `openai/gpt-6-luna` przez OpenRouter) i publikuje review jako komentarz. `CODEX_SANDBOX=danger-full-access` jest potrzebny, bo sandbox Codex nie startuje w zwykłym kontenerze Docker; granicą jest kontener joba. Własne joby (opis MR, zgodność z AGENTS.md, luki w testach, diagnoza builda) buduje się z [codex_run.sh](codex_run.sh), zobacz [ćwiczenie](../../exercises/gitlab-codex-exec-workflows.md).

![Komentarz "Agent review (codex)" w merge requeście GitLab: problemy blokujące, nieblokujące, brakujące testy i podsumowanie](examples/codex-review-gitlab-mr-2026-10-30.png)

[Pełna treść tego review](examples/codex-review-gitlab-mr-2026-10-30.md). Codex sam wskazał ryzyko tej konfiguracji: agent z pełnym dostępem do powłoki widzi klucz API i token GitLab, więc w projektach firmowych używaj kluczy z limitem kosztów i tokenów o minimalnych uprawnieniach.

## Dostęp do modeli

Najprościej: **jeden klucz OpenRouter** (`OPENROUTER_API_KEY`) dla wszystkich czterech agentów, ustawiony jako tajna zmienna CI. Skrypt przełącza każde CLI na OpenRouter (`LLM_PROVIDER=openrouter`, domyślnie). Model wybierasz zmienną `REVIEW_MODEL`, np. `openai/gpt-6-luna`.

Własne konto każdego narzędzia (`LLM_PROVIDER=native`):

| Agent | Zmienna | Uwagi |
|---|---|---|
| Copilot CLI | `COPILOT_GITHUB_TOKEN` | fine-grained PAT z uprawnieniem **Copilot Requests**, utworzony na koncie użytkownika (nie organizacji); zużywa jego kredyty. Tokeny klasyczne `ghp_` nie działają |
| Claude Code | `ANTHROPIC_API_KEY` | klucz z Claude Console |
| Codex | `CODEX_API_KEY` | klucz OpenAI API; ta zmienna działa tylko w `codex exec` |
| OpenCode | np. `OPENROUTER_API_KEY` | dowolny dostawca obsługiwany przez OpenCode |

Klucz ustawiaj tylko w kroku, który uruchamia agenta, a nie dla całego joba: skrypty budowania i zależności z tego samego joba mogłyby go odczytać.

## Obraz Dockera

Obraz bazuje na `node:24-bookworm-slim`, a nie na Alpine. CLI agentów i ich dodatki (ripgrep, natywne moduły, opcjonalnie Playwright) zakładają glibc i bash; na Alpine (musl) część z nich nie działa bez dodatkowych pakietów. Wersje CLI są przypięte w `ARG`, żeby review nie zmieniało się między uruchomieniami. Zbuduj obraz raz i wypchnij do rejestru, z którego korzysta Twoje CI:

```bash
docker build -t registry.example.com/agent-ci:1 ci/agent-review
docker push registry.example.com/agent-ci:1
```

Bez własnego rejestru możesz zainstalować CLI w samym jobie (`npm install -g ...`), kosztem około minuty na każde uruchomienie.

## Przed pierwszym użyciem

Na żywo przetestowano tylko ścieżkę GitLab + Codex ([przykład wyżej](#przetestowany-przykład-gitlab-ci-i-codex), 30.10.2026). Pozostałe warianty (Azure, Bitbucket, inne agenty w GitLab) nie były jeszcze uruchomione na żywo. Przed wdrożeniem w zespole:

1. `docker build` i `docker run --rm agent-ci:1 sh -c 'copilot --version; claude --version; codex --version; opencode --version'`
2. Lokalnie, na gałęzi z małą zmianą: `AGENT=opencode bash ci/agent-review/agent_review.sh main` i sprawdź `.agent-review/review.md`; powtórz dla pozostałych agentów.
3. Pierwszy PR w każdej platformie: sprawdź komentarz i log joba.

## Dokumentacja

- [Copilot CLI: uruchamianie programowe](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically), [uwierzytelnianie](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli)
- [Claude Code: tryb headless](https://code.claude.com/docs/en/headless), [OpenRouter dla Claude Code](https://openrouter.ai/docs/guides/guides/claude-code-integration)
- [Codex: tryb nieinteraktywny](https://developers.openai.com/codex/noninteractive)
- [OpenCode: konfiguracja uprawnień](https://opencode.ai/docs/permissions/)
- [Azure DevOps: wątki komentarzy w PR](https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-threads/create), [GitLab: notatki w MR](https://docs.gitlab.com/api/notes/), [Bitbucket: komentarze w PR](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/), [Bitbucket: koniec app passwords](https://www.atlassian.com/blog/bitbucket/bitbucket-cloud-transitions-to-api-tokens-enhancing-security-with-app-password-deprecation)
- [Jira: komentarze i przejścia statusów](https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-comments/)
