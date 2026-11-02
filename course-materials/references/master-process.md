# Mapa procesu - od pomysłu do sprawdzonej zmiany

> Każdy temat łączy się z kolejnym krokiem pracy nad projektem.
> Zakres i prezentacje znajdziesz na stronie materiałów kursu.

## Zasady nadrzędne

- Prowadzący demonstruje proces **na żywo** (TypeScript + Vercel AI SDK);
  uczestnicy podążają **we własnym stacku** (Java/Spring, Python, C#, Go…).
- Repo: `main` = TYLKO materiały kursu. Aplikacja powstaje na **osobnym
  branchu** per uczestnik/grupa.
- **E2E i testy manualne agenta: NIC nie mockujemy** — część LLM testowana na żywo przez OpenRouter (unit/integration mockują wg tabeli w AGENTS.md)
  (`OPENROUTER_API_KEY` na VM). E2E i testy manualne idą po prawdziwym stacku.
- Commity **granularne** po każdej zielonej fazie TDD.

---

## Krok 1 — Ideacja + PRD

- **Co robimy:** grupowa dyskusja pomysłów → specyfikacja produktu:
  funkcjonalności, flow, persony, kryteria akceptacji, out-of-scope.
  W naszej aplikacji demo: multimodalny chat (zwrot/reklamacja sprzetu ze
  zdjeciem), dwa rozne prompty zaleznie od sciezki.
- **Czym:** skill `.agents/skills/write-prd/SKILL.md` (wymaga min. 5 pytań
  wyjaśniających); prompt `course-materials/Prompt examples/PRD-generation-prompt-promtcowboy.md`
  jako referencja stylu PRD. Wynik: `docs/PRD.md` (EN).
- **Etap:** Po ustaleniu pomysłu i zakresu aplikacji.
- **Ukończenie:** PRD z mierzalnymi kryteriami akceptacji (AC-XX), sekcja
  „Out of Scope", diagram Mermaid flow; min. 5 pytań zadanych i rozstrzygniętych.

## Krok 2 — Wireframes (OPCJONALNE)

- **Co robimy:** generujemy proste mockupy ekranów modelem obrazowym.
  Przy dzisiejszych modelach krok **NIE jest wymagany** — PRD + Design
  Guidelines wystarczą agentowi do zbudowania dobrego UI.
- **Czym:** dowolny model image-gen dostępny na VM. (wybor narzedzia: decyzja trenera przed kursem)
- **Etap:** Opcjonalnie po PRD; pomiń bez straty dla dalszej pracy.
- **Ukończenie:** 1–3 obrazki-mockup; opcjonalne — pomiń bez straty dla reszty
  procesu.

## Krok 3 — Design Guidelines

- **Co robimy:** reverse-engineering designu ze strony referencyjnej (marka
  uczestnika lub dowolna). Zbieramy tokeny, kolory, typografię, logo, favicon,
  screenshot → gotowy design system dla agenta FE.
- **Czym:** skill `.agents/skills/create-design-system/SKILL.md` (Playwright
  MCP, gotowy skrypt `evaluate`); prompt `course-materials/Prompt examples/Design System reverse-engineering with Playwright.md`.
  Trend: **CLI > MCP**. Wynik: `assets/design-tokens.json`, `assets/logo.svg`,
  `assets/homepage.png`, `docs/design-guidelines.md`.
- **Etap:** Przed implementacją interfejsu: MCP + Playwright, praktyka z Design Guidelines wygenerowanymi z dowolnej strony.
- **Ukończenie:** pliki `design-tokens.json` + `design-guidelines.md` istnieją;
  tokeny mają konkretne wartości hex/px; logo SVG zapisane.

## Krok 4 — ADR (Architecture Decision Record)

- **Co robimy:** decyzje techniczne — stack, struktury danych, kontrakty API,
  diagramy, strategia testów. Wszystko, czego agent implementujący potrzebuje,
  by nie zgadywać architektonicznie.
- **Czym:** skill `.agents/skills/write-adr/SKILL.md` (min. 5 pytań,
  rozstrzygnięcie Context7 handle dla każdej biblioteki). Wynik: `docs/ADR/`
  (np. `000-main-architecture.md`, `001-backend.md`, `002-frontend.md`).
- **Etap:** Przed planowaniem implementacji; dokument można pogłębić samodzielnie.
- **Ukończenie:** ADR z tabelą Context7 handles, diagramy Mermaid
  (architektura + sekwencje per flow), sekcja „Testing Strategy" z TAC-XX.

## Krok 5 — Plan (macierz zależności + agenci równolegli)

- **Co robimy:** główny agent jest tylko orkiestratorem — tworzy fazy, małe
  kroki, macierz zależności między zadaniami i agentami, by mogli pracować
  częściowo równolegle bez wzajemnego przerywania. Commity po każdej fazie.
  Opcjonalnie: workflow script orkiestrujący subagentów.
- **Czym:** prompt `course-materials/Prompt examples/Plan-SubAgents-matrix-dependency-map.md` (punkt odniesienia dla planu) oraz role `be-developer`, `fe-developer`, `qa-engineer` z Modułu 2.3. Domyślnie rozdziel pliki lub foldery w jednym checkout i zapisz zależności. Worktree to wyjątek dla koniecznych równoległych zmian tych samych plików w osobnych checkoutach: uzgodnij kontrakty, scalaj wyniki kolejno, rozwiąż konflikty i uruchom testy. Zapis Git (gałąź, indeks, staging i commit) wykonuje wyłącznie koordynator. W AGENTS.md zapisz zakaz domyślnego tworzenia worktree: instalacje zależności zużywają dysk i CPU, a sprzątanie bywa pomijane. Przed pokazem sprawdź na VM, czy skrypt orkiestrujący działa.
- **Etap:** Po PRD i ADR: Task Plan Matrix, podział plików, zależności i ewentualny worktree.
- **Ukończenie:** dokument planu z fazami, macierzą zależności i briefami per
  agent (tylko wymagany kontekst, bez balastu); każdy agent wie, co robi, bez
  pytań.

## Krok 6 — Pętla TDD (z obowiązkowymi testami manualnymi agenta)

- **Co robimy:** Red-Green-Refactor. Testy jednostkowe/integracyjne pisane
  **przed** kodem. **OBOWIĄZKOWE**: testy manualne przez agenta — Playwright
  (MCP lub CLI) / Chrome DevTools; weryfikacja screenshotów vs mockupy i Design
  Guidelines. **LLM testowany na żywo** — żadnych mocków części AI. Tabela:
  Unit = wszystkie zależności mockowane (be/fe-dev); Integration = tylko
  zewn. LLM API mockowany; E2E = **NIC** nie mockowane (qa-engineer).
- **Czym:** agent `qa-engineer` (Moduł 2.3); Playwright MCP z kroku 3; skille
  `java-junit`/`java-springboot` dla Java devs; Context7 dla aktualnych API.
- **Etap:** Po zatwierdzeniu planu: TDD z sub-agentami, testowanie i jakość, Playwright MCP w testach, code review.
- **Ukończenie:** `npm test` / odpowiednik zielone; test E2E po prawdziwym
  stacku przechodzi; screenshot aplikacji porównany z design guidelines; LLM
  odpowiada realnie na realne zdjęcie.

## Krok 7 — Debugowanie

- **Co robimy:** diagnoza usterek wykrytych w testach i w testach manualnych
  agenta. Analiza logów, iteracyjne poprawki, code review z agentem (security,
  jakość). Human review jako ostateczna instancja.
- **Czym:** `qa-engineer` (code review); Chrome DevTools MCP dla inspekcji;
  Context7 dla bieżących API; `AGENTS.md` reguły weryfikacji przed commitem.
- **Etap:** Po wykryciu błędu: ograniczenia AI i human review.
- **Ukończenie:** wszystkie błędy z pętli TDD zamknięte; lint + build + test
  zielone; aplikacja startuje poprawnie.

## Krok 8 — Demo + nowe funkcje

- **Co robimy:** prezentacja działającej aplikacji na żywo (realne zdjęcie →
  realna decyzja LLM → chat support). Rozszerzenia: historia czatów, rendering
  markdown. Retrospektywa, dalsza nauka.
- **Czym:** aplikacja na branchu uczestnika.
- **Etap:** Po sprawdzeniu działania aplikacji.
- **Ukończenie:** end-to-end demo przechodzi bez błędu; gotowy scenariusz z
  danymi testowymi (zdjęcie sprzetu + opis).
