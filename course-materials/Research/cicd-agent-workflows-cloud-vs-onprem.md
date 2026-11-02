# CI/CD agent workflows: cloud vs on-prem

Status: draft for trainer use (Phase G1)  
Ostatnia aktualizacja: 2026-03-15

## Po co ten materiał
Ten dokument daje trenerowi realistyczne, „bankowo-wiarygodne” przykłady jak wpiąć pracę agentów AI do CI/CD:
- wariant **cloud-first** (GitHub Actions),
- wariant **on-prem / enterprise** (Jenkins + GitHub Enterprise + lokalne modele),
- warianty z bramkami bezpieczeństwa i akceptacjami.

> Uwaga trenerska: celem nie jest uczenie DevOps od zera, tylko pokazanie wzorców integracji i kompromisów (szybkość vs kontrola).

---

## 1) Architektura porównawcza (skrót)

## A. Cloud-first (GitHub.com + GitHub Actions + CLI agent)
**Kiedy pasuje:** zespoły, które mogą używać usług cloud i mają zgodę na dane poza on-prem.  
**Plusy:** szybki start, łatwy autoskalowalny runner model, dobry onboarding.  
**Ryzyka:** polityki danych, sekrety, zależność od usług zewnętrznych.

Przepływ:
1. PR/push uruchamia workflow.
2. Job odpala CLI agenta (np. Codex CLI / Claude Code CLI) do analizy diffa, test-planu, lub auto-fix proposal.
3. Wynik trafia do:
   - komentarza PR,
   - artefaktu (raport JSON/MD),
   - opcjonalnie commitu do gałęzi roboczej.
4. Deployment gate wymaga aprobaty (required reviewer / environment protection).

## B. On-prem (GitHub Enterprise Server + Jenkins + lokalny endpoint modelu)
**Kiedy pasuje:** bank/regulated, twarde wymagania data residency i audytowalności.  
**Plusy:** kontrola nad siecią, sekretami, modelem i retencją logów.  
**Ryzyka:** większy koszt utrzymania, wolniejsza ewolucja toolingu, potrzeba silnych standardów pipeline.

Przepływ:
1. PR/push w GHES triggeruje webhook/build Jenkins.
2. Jenkins uruchamia agenta CLI lub lokalny skrypt, który woła endpoint lokalnego modelu (np. gateway wewnętrzny).
3. Wynik zapisuje się jako artefakt + komentarz do PR (przez API GHES lub plugin).
4. Przed merge/deploy pipeline zatrzymuje się na `input` (manual approval) lub dedykowanej bramce jakości/security.

---

## 2) Przykład 1 — GitHub Actions + Codex/Claude CLI (cloud)

Poniżej minimalny i realistyczny szkic. Nie zakłada „full auto merge”, tylko bezpieczny tryb rekomendacji.

```yaml
name: ai-pr-review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  ai-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write   # jeśli używamy OIDC do cloud auth
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install CLI tools
        run: |
          npm i -g @openai/codex
          # lub instalacja innego CLI agenta wg polityki firmy

      - name: Generate AI review report
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          codex exec "Review current PR diff for: security, tests missing, rollback risk. Return JSON." \
            > ai-review.json

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: ai-review
          path: ai-review.json
```

### Co jest „enterprise-safe” w tym wariancie
- Agent generuje **raport/rekomendację**, a nie bezwarunkowy deploy.
- Sekrety są w `secrets`, a dostęp do chmury można robić przez **OIDC** (krótkotrwałe tokeny zamiast stałych kluczy).
- Można wymusić aprobaty przed deploymentem przez **GitHub Environments required reviewers**.

---

## 3) Przykład 2 — Jenkins + GHES + lokalny model (on-prem)

Wersja uproszczona, realistyczna dla bankowego środowiska.

```groovy
pipeline {
  agent { label 'linux-onprem' }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('AI Analysis (local endpoint)') {
      steps {
        withCredentials([string(credentialsId: 'llm_api_token', variable: 'LLM_TOKEN')]) {
          sh '''
            set +x
            ./scripts/ai-review.sh \
              --model-endpoint https://llm-gateway.internal \
              --token "$LLM_TOKEN" \
              --diff "$(git diff origin/main...HEAD)" \
              --out ai-review.json
          '''
        }
        archiveArtifacts artifacts: 'ai-review.json', fingerprint: true
      }
    }

    stage('Quality & Security Gates') {
      steps {
        sh './mvnw -q -DskipTests=false test'
        sh './mvnw -q spotbugs:check'
      }
    }

    stage('Manual Approval') {
      steps {
        input message: 'Czy zatwierdzasz deploy po raporcie AI i gate\'ach?', ok: 'Tak, deploy'
      }
    }

    stage('Deploy') {
      steps {
        sh './scripts/deploy.sh'
      }
    }
  }
}
```

### Co jest „enterprise-safe” w tym wariancie
- Model endpoint jest **wewnątrz sieci** (on-prem / private).
- Sekrety przechodzą przez `withCredentials` (maskowanie w logach).
- Jest twardy **manual gate** (`input`) przed deploy.
- AI jest doradcą jakości/ryzyka, nie autonomicznym deployerem.

---

## 4) Security i approvals — wzorzec dla enterprise

Minimalny zestaw zasad, który warto pokazać na szkoleniu:

1. **Rozdział ról**
   - Agent może analizować i proponować,
   - człowiek zatwierdza produkcję.

2. **Least privilege**
   - Workflow ma minimalne `permissions`.
   - Tokeny krótkotrwałe (OIDC), nie stałe klucze gdzie się da.

3. **Policy-as-code + gate’y**
   - testy + SAST/SCA + quality gates przed approval.
   - deploy dopiero po pozytywnych checkach.

4. **Ślad audytowy**
   - raport agenta jako artefakt (JSON/MD),
   - metadane: commit SHA, kto zatwierdził, kiedy i dlaczego.

5. **Tryb fail-safe**
   - jeśli agent niepewny / brak danych / timeout → pipeline przechodzi w tryb manualny, bez auto-akcji.

---

## 5) Cloud vs on-prem — gotowy komentarz trenera (krótki)

„W cloud pokazujemy maksimum możliwości i szybkość iteracji.  
W on-prem pokazujemy, jak zachować ten sam proces decyzyjny, ale pod większą kontrolą: lokalny model, lokalne sekrety, mocniejsze bramki i audyt.  
To nie są dwa różne światy — to ten sam workflow, tylko inna granica zaufania.”

---

## 6) Czego **nie** obiecywać uczestnikom

- „AI samo utrzyma jakość” — nie, jakość wymaga gate’ów i odpowiedzialności zespołu.
- „On-prem zawsze tańszy” — nie zawsze; zależy od kosztu utrzymania platformy i kompetencji.
- „Cloud zawsze niezgodny z regulacjami” — nie zawsze; zależy od klasyfikacji danych i polityki organizacji.

---

## 7) Źródła (do dalszego czytania)

### GitHub Actions / GitHub Enterprise
- GitHub Actions — self-hosted runners:  
  https://docs.github.com/actions/hosting-your-own-runners
- GitHub Actions — self-hosted runners reference:  
  https://docs.github.com/en/actions/reference/runners/self-hosted-runners
- GitHub Actions — environments i required reviewers:  
  https://docs.github.com/actions/deployment/targeting-different-environments/using-environments-for-deployment
- GitHub Actions — OIDC w deploymentach:  
  https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers
- GitHub Actions — artifact attestations:  
  https://docs.github.com/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds
- GitHub Enterprise Server — self-hosted runners (enterprise):  
  https://docs.github.com/en/enterprise-server@3.14/admin/managing-github-actions-for-your-enterprise/getting-started-with-github-actions-for-your-enterprise/getting-started-with-self-hosted-runners-for-your-enterprise

### Jenkins
- Jenkins Pipeline: Input Step (`input`):  
  https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/
- Jenkins Credentials Binding (`withCredentials`):  
  https://www.jenkins.io/doc/pipeline/steps/credentials-binding/
- Jenkins Shared Libraries:  
  https://www.jenkins.io/doc/book/pipeline/shared-libraries/

### Integracje agentów (materiał pomocniczy)
- OpenAI Codex — GitHub integration docs:  
  https://developers.openai.com/codex/integrations/github/
- Claude Code — product/docs hub:  
  https://claude.com/product/claude-code

---

## 8) Jak użyć tego w kursie (dla Day 4 / Day 5)

- Day 4: pokazać 1 slajd architektury + 1 mini snippet YAML + 1 mini snippet Jenkinsfile.
- Day 5: w wrap-up zrobić checklistę „co wdrożyć od poniedziałku”:
  1. jeden pipeline AI-review w trybie read-only,
  2. jeden manual approval gate,
  3. jeden artefakt audytowy per build,
  4. dopiero potem eksperyment z auto-fix na branchu roboczym.

## 9) Krótki snippet trenerski (G2) — „cloud max” vs „on-prem adaptacja”

### 9.1 Co mówię (90–120 sekund)
„Najpierw pokażę wersję cloud-max, bo tam najszybciej widać pełny potencjał: szybkie uruchomienie, wygodne integracje i krótkie pętle feedbacku.
Potem dokładnie ten sam workflow mapujemy do on-prem: zamiast usług cloud mamy lokalny endpoint modelu, zamiast domyślnych integracji — świadomie ustawione bramki i audyt.
To nie jest zmiana filozofii, tylko zmiana granicy zaufania.”

### 9.2 Co wklejam na chat (wersja ultra-krótka)
```text
Cloud demo (max możliwości):
- PR -> AI review -> testy -> approval -> merge/deploy

Adaptacja on-prem:
- ten sam flow,
- model i sekrety w sieci wewnętrznej,
- mocniejsze approvale i ślad audytowy.
```

### 9.3 Co pokazuję na slajdzie (bez deep dive infra)
- **Cloud-max (demo):** GitHub Actions + CLI agent + artefakt raportu + required reviewer.
- **On-prem (adaptacja):** Jenkins/GHES + lokalny endpoint modelu + `withCredentials` + manual gate.
- **Wspólny rdzeń:** prompt → diff → test → review → approval.

### 9.4 Czego nie rozwijam na zajęciach (scope guard)
- Nie wchodzimy w szczegóły hardeningu runnerów, segmentacji sieci i pełnej architektury IAM.
- Nie robimy benchmarków modeli „kto szybszy”.
- Nie obiecujemy full autonomy bez człowieka w pętli.
