# Własny workflow GitLab z `codex exec`

Cel: każdy buduje jeden własny job CI, w którym agent Codex wykonuje powtarzalną pracę zespołu: opis MR, kontrola zgodności z AGENTS.md, luki w testach, diagnoza nieudanego builda, notatki wydania albo raport nocny. Job uruchamia się na runnerze GitLab szkoleniowego, więc VM wykonuje tylko lekkie polecenia: edycję plików, `glab ci lint` i `git push`.

Warunek wstępny: własny projekt w GitLabie z zielonym pipeline według [przykładu z review Codex](../cicd-headless/gitlab-codex-review/.gitlab-ci.yml), czyli katalog `ci/agent-review/` i zmienna `GITLAB_TOKEN` w projekcie.

## Klocki

- Obraz `agent-ci:1` z Codex CLI, `git`, `curl`, `jq` i `ripgrep`.
- [`ci/agent-review/codex_run.sh`](../cicd-headless/agent-review/codex_run.sh) uruchamia `codex exec` z plikiem promptu i zapisuje końcową odpowiedź do pliku. Model: Luna przez OpenRouter, klucz `OPENROUTER_API_KEY` ustawia trener dla całej instancji.
- [`ci/agent-review/post_review_comment.sh`](../cicd-headless/agent-review/post_review_comment.sh) publikuje plik Markdown jako komentarz w MR. Nagłówek komentarza bierze ze zmiennej `AGENT`.
- Prompt trzymasz w pliku `ci/prompts/<nazwa>.md`, nie w YAML: łatwiej go poprawiać i recenzować.

Jeśli Twój katalog `ci/agent-review/` nie ma jeszcze `codex_run.sh`, skopiuj go z repozytorium kursu (sklonowanego obok jako `..\kurs`), będąc w katalogu swojego projektu:

```powershell
Copy-Item ..\kurs\course-materials\cicd-headless\agent-review\codex_run.sh ci\agent-review\
```

Wzorcowy job (W1, opis MR):

```yaml
mr-summary:
  stage: review
  image: agent-ci:1
  needs: []
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  variables:
    GIT_DEPTH: "0"
    AGENT: "codex: opis MR"
    CODEX_SANDBOX: danger-full-access
  script:
    - git fetch origin "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"
    - bash ci/agent-review/codex_run.sh ci/prompts/mr-summary.md .agent/mr-summary.md
    - bash ci/agent-review/post_review_comment.sh .agent/mr-summary.md
  artifacts:
    when: always
    paths: [.agent/]
    expire_in: 3 days
```

`CODEX_SANDBOX: danger-full-access` jest tu potrzebny, bo sandbox Codex na Linuksie nie tworzy przestrzeni nazw w zwykłym kontenerze Docker; granicą jest kontener joba. Prompt nadal zabrania zmian w plikach, a job niczego nie pushuje.

## Wybierz jeden workflow

| Nr | Workflow | Kiedy uruchamia się job | Wynik |
|---|---|---|---|
| W1 | Opis MR dla recenzenta | każdy MR | komentarz: zakres, pliki, ryzyka, jak sprawdzić |
| W2 | Zgodność z AGENTS.md | każdy MR | komentarz: naruszenia reguł z cytatem reguły i plik:linia |
| W3 | Luki w testach | każdy MR | komentarz: zmienione klasy bez testów i propozycje przypadków |
| W4 | Diagnoza nieudanego builda | MR, tylko gdy build nie przejdzie | komentarz: przyczyna z cytatem z logu i minimalna poprawka |
| W5 | Notatki wydania | MR do `master` | komentarz lub artefakt: zmiany dla użytkownika i dla zespołu |
| W6 | Raport nocny | harmonogram (`glab schedule`) | zgłoszenie w GitLabie z listą TODO, ostrzeżeń i ryzyk |

Przykładowe prompty do plików `ci/prompts/`:

- **W1:** `Przeczytaj zmiany: git diff origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD. Napisz po polsku opis dla recenzenta: cel zmiany, lista plików z jednym zdaniem każdy, ryzyka, jak sprawdzić ręcznie. Nie zmieniaj żadnych plików. Maksymalnie 25 linii.`
- **W2:** `Przeczytaj AGENTS.md i zmiany względem gałęzi docelowej. Wypisz tylko naruszenia reguł: cytat reguły, plik:linia, dlaczego. Jeśli brak naruszeń, napisz "Brak naruszeń" i jakie reguły sprawdziłeś. Nie zmieniaj plików.`
- **W3:** `Znajdź klasy produkcyjne zmienione w tym MR. Dla każdej sprawdź, czy istnieje test w src/test/java i czy pokrywa zmienione metody. Wypisz luki i 2-3 konkretne przypadki testowe na lukę. Nie pisz kodu i nie zmieniaj plików.`
- **W4:** `Build nie przeszedł. Przeczytaj build.log. Wskaż pierwszą rzeczywistą przyczynę z cytatem z logu, plik i test, oraz minimalną poprawkę. Nie proponuj wyłączenia ani osłabienia testów. Nie zmieniaj plików.`
- **W5:** `Na podstawie commitów i diffu względem gałęzi docelowej napisz notatki wydania: zmiany widoczne dla użytkownika, zmiany techniczne, ryzyka migracji. Bez marketingu, tylko fakty z kodu.`
- **W6:** `Przejrzyj repozytorium: TODO i FIXME, zależności Maven z wersjami, ostrzeżenia w konfiguracji. Napisz raport do 30 linii z priorytetami. Nie zmieniaj plików.`

Różnice w YAML względem wzoru:

- **W4:** w jobie `build` zapisz log i dodaj go do artefaktów; job diagnozy pobiera artefakt i uruchamia się tylko po porażce:

  ```yaml
  build:
    script:
      - chmod +x mvnw
      - ./mvnw -B -ntp clean package 2>&1 | tee build.log
    artifacts:
      when: always
      paths: [build.log]
      reports:
        junit: target/surefire-reports/TEST-*.xml
  ```

  ```yaml
  build-triage:
    stage: review
    image: agent-ci:1
    needs: [{job: build, artifacts: true}]
    rules:
      - if: $CI_PIPELINE_SOURCE == "merge_request_event"
        when: on_failure
  ```

  Sprawdź go celowo nieprzechodzącym testem na osobnej gałęzi, a potem usuń ten test.
- **W5:** reguła `- if: $CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_TARGET_BRANCH_NAME == "master"`.
- **W6:** reguła `- if: $CI_PIPELINE_SOURCE == "schedule"`. W harmonogramie nie ma merge requestu, więc usuń `git fetch origin "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"` i krok z komentarzem w MR, a w prompcie analizuj bieżącą gałąź. Wynik zapisz jako zgłoszenie (blok `|`, bo zwykły tekst YAML z `: ` w środku GitLab odrzuca):

  ```yaml
  script:
    - bash ci/agent-review/codex_run.sh ci/prompts/nightly.md .agent/nightly.md
    - |
      jq -n --arg t "Raport nocny $(date +%F)" --rawfile d .agent/nightly.md '{title:$t, description:$d}' \
        | curl -fsS -X POST -H "PRIVATE-TOKEN: $GITLAB_TOKEN" -H "Content-Type: application/json" \
          --data @- "$CI_API_V4_URL/projects/$CI_PROJECT_ID/issues" > /dev/null
  ```

  Harmonogram tworzysz i uruchamiasz od razu, bez czekania na noc:

  ```powershell
  glab schedule create --cron "0 6 * * 1-5" --cronTimeZone "Europe/Warsaw" --ref master --description "Raport nocny"
  ```

  ```powershell
  glab schedule list
  ```

  ```powershell
  glab schedule run <ID>
  ```

## Niech Codex zbuduje job

Na gałęzi od `master` (np. `git switch -c ci/w2-agents-check`) poproś lokalnego Codex:

```text
Do pracy z GitLabem używaj glab; składnię sprawdzaj w `glab <polecenie> --help`. Dodaj do .gitlab-ci.yml nowy job <nazwa> według wzoru z course-materials/exercises/gitlab-codex-exec-workflows.md w repozytorium kursu (..\kurs). Prompt zapisz w ci/prompts/<nazwa>.md. Job ma używać obrazu agent-ci:1, uruchamiać bash ci/agent-review/codex_run.sh i publikować wynik przez post_review_comment.sh. Nie zmieniaj istniejących jobów poza tym, czego wymaga wybrany workflow. Na koniec uruchom glab ci lint, pokaż diff i nie pushuj bez mojej zgody.
```

Po akceptacji diffu:

```powershell
git add .gitlab-ci.yml ci
git commit -m "CI: własny job agenta"
git push -u origin HEAD
```

```powershell
glab mr create --fill --target-branch master --yes
```

```powershell
glab ci status --live
```

```powershell
glab mr view --comments
```

## Kiedy job jest gotowy

- `glab ci lint` przechodzi, a job rzeczywiście uruchomił się w pipeline (lint nie dowodzi uruchomienia).
- Wynik agenta jest w MR, w zgłoszeniu albo w artefakcie `.agent/`, a nie tylko w logu.
- Sprawdziłeś co najmniej jedno stwierdzenie agenta w kodzie lub logu i wiesz, czy było trafne.
- Job nie wypisuje sekretów do logu, nie zmienia plików i nie pushuje.
- Wiesz, ile kosztowało uruchomienie: model, czas joba, rozmiar wyniku. Raport w MR nie jest zgodą na merge.

Rozszerzenia: drugi workflow z tabeli; wynik w formacie JSON przez `codex exec --output-schema`; ten sam prompt na innym modelu (`MODEL` w zmiennych joba) i porównanie jakości.
