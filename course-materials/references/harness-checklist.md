# Harness Checklist - co gdzie umieszczać w konfiguracji agenta

Praktyczny przewodnik: AGENTS.md vs Skills vs Sub-Agents vs Rules vs Memory
vs MCP vs PRD/ADR vs Plan. Dla zespołów pracujących z Claude Code, OpenCode,
Codex, Gemini CLI i innymi agentami zgodnymi z konwencjami AGENTS.md /
SKILL.md. Odpowiedniki OpenCode (w tym self-hosted modele): sekcje 9 i 10.

---

## Model myślowy: dwie osie

Każda informacja dla agenta ma swoje miejsce wyznaczone przez dwie osie:

1. **Trwałość** - jak długo informacja pozostaje prawdziwa?
   (jedna sesja -> jeden PR -> jeden feature -> całe repo -> cała organizacja)
2. **Zasięg** - kogo i czego dotyczy?
   (jeden plik -> jeden moduł -> jedno repo -> wiele repo -> preferencje osoby)

Zasada nadrzędna: **kontekst agenta jest drogi i ulotny**. Wszystko, co
wkładasz "na stałe" do kontekstu (AGENTS.md, rules), agent czyta w KAŻDEJ
sesji - płacisz za to uwagą modelu. Wszystko, co ładuje się na żądanie
(skills, PRD, ADR, plan), kosztuje tylko wtedy, gdy jest potrzebne.

Szybki test: *"Czy ta informacja będzie prawdziwa za miesiąc i potrzebna
w większości sesji?"*
- TAK -> AGENTS.md / rules.
- Prawdziwa za miesiąc, ale potrzebna rzadko -> skill, PRD/ADR lub docs.
- Nieprawdziwa za miesiąc (dotyczy jednego zadania) -> plan, opis PR, task.

---

## 1) AGENTS.md / CLAUDE.md - stała konstytucja repo

**Co to jest:** plik w katalogu głównym repo (i opcjonalnie w podkatalogach),
ładowany automatycznie do kontekstu na starcie każdej sesji. AGENTS.md to
konwencja między-agentowa (Claude Code, Codex, Gemini, Cursor i inne);
CLAUDE.md może po prostu wskazywać na AGENTS.md jednym importem `@AGENTS.md`.

**Co tu umieszczać (checklist):**
- [ ] Komendy: build, test, lint, typecheck (dokładne, z package managerem)
- [ ] Konwencje kodu: język, styl, struktura katalogów, nazewnictwo
- [ ] Ograniczenia środowiska: OS, wersje, czego nie uruchamiać (np. dev server)
- [ ] Granice bezpieczeństwa: czego nie czytać (sekrety), czego nie dotykać (prod)
- [ ] Definicja "done": co musi przejść zanim agent uzna pracę za skończoną
- [ ] Wskazniki do głębszej dokumentacji ("architektura: docs/ARCHITECTURE.md")

**Czego NIE umieszczać:**
- Sekretów i tokenów (nigdy; agent może je wkleić do odpowiedzi lub logów)
- Planów jednorazowych zadań (to idzie do planu / opisu PR)
- Długich opisów architektury (link do docs/, nie treść)
- Instrukcji specyficznych dla jednego narzędzia w pliku wspólnym
  (delegacja między modelami, preferencje osobiste -> do ~/.claude/CLAUDE.md)

**Zagnieżdżanie:** trzymaj główny AGENTS.md KRÓTKI i uniwersalny; szczegóły
modułów umieszczaj w zagnieżdżonych AGENTS.md w podkatalogach (np.
`frontend/AGENTS.md` z konwencjami komponentów). Agent czyta zagnieżdżony
plik dopiero gdy pracuje w tym katalogu - to naturalne "lazy loading".

**Antywzorzec:** AGENTS.md liczący 500+ linii. Model gubi środek długiego
pliku, a Ty płacisz kontekstem w każdej sesji. Ponad ~150 linii = sygnał,
że część treści powinna być skillem, zagnieżdżonym plikiem albo docs.

---

## 2) Rules / Settings / Permissions - twarde granice

**Co to jest:** deterministyczna konfiguracja narzędzia (w Claude Code:
`settings.json` + permissions; w Cursor: `.cursor/rules`). Różnica vs
AGENTS.md: instrukcje w markdown model może zignorować lub źle zrozumieć;
permissions egzekwuje sam harness - zawsze.

**Co tu umieszczać (checklist):**
- [ ] Allowlist bezpiecznych komend (mniej pytań o zgodę = szybsza praca)
- [ ] Denylist: produkcyjne CLI, destrukcyjne komendy, katalogi z sekretami
- [ ] Hooks (patrz punkt 5) i zmienne środowiskowe sesji
- [ ] Wybór modelu / trybu domyślnego dla zespołu (`settings.json` w repo)

**Reguła:** jeśli złamanie zasady jest kosztowne (usunięcie danych, wyciek
sekretu, deploy na prod), NIE ufaj instrukcji w markdown - wymuś to
permissions/hooks. Markdown to prośba, settings to prawo.

---

## 3) Skills (SKILL.md) - powtarzalne procedury na żądanie

**Co to jest:** katalog z plikiem SKILL.md (+ opcjonalne skrypty i zasoby),
opisujący procedurę. Ładowany do kontekstu TYLKO gdy pasuje do zadania lub
gdy użytkownik wywoła go jawnie (`/nazwa`). Konwencja działa w wielu
narzędziach (Claude Code, OpenCode, Codex, Gemini). Dawne "commands" w Claude
Code zostały scalone ze skills; w OpenCode custom commands to nadal osobny,
prostszy byt (szablony promptów) - patrz sekcja 10.

**Co tu umieszczać (checklist):**
- [ ] Procedury powtarzane w wielu sesjach/repo ("jak robimy security review")
- [ ] Workflow wielokrokowy z narzędziami ("release: wersja, changelog, tag")
- [ ] Wiedzę domenową potrzebną rzadko, ale wtedy w całości (np. format
      dokumentów firmowych, checklisty compliance)
- [ ] Skrypty pomocnicze obok SKILL.md, żeby agent nie pisał ich od zera

**Czego NIE umieszczać:** wiedzy potrzebnej w każdej sesji (to AGENTS.md),
szczegółów jednego feature'a (to plan/PRD).

**Sygnał, że czas na skill:** trzeci raz tłumaczysz agentowi to samo w
prompcie, albo kończysz sesję, którą chciałbyś umieć powtórzyć. "Zrób z tej
sesji skill" to legalne zakończenie dobrej sesji.

---

## 4) Sub-Agents - role z własnym kontekstem

**Co to jest:** definicje agentów-pomocników (np. `.claude/agents/*.md`)
z własnym promptem systemowym, narzędziami i limitem uprawnień. Główny agent
deleguje im zadania; wracają z raportem, a ich "brudny" kontekst (przeczytane
pliki, logi) NIE zaśmieca kontekstu głównego.

**Co tu umieszczać (checklist):**
- [ ] Role z jasnym kontraktem wejście/wyjście: reviewer, QA, researcher
- [ ] Zadania czytające dużo plików, z których potrzebujesz tylko wniosków
- [ ] Prace równoległe i niezależne (każdy agent inny obszar!)
- [ ] Ograniczenia roli: reviewer bez prawa edycji, researcher bez Bash

**Czego NIE robić:**
- Worktree twórz tylko wtedy, gdy agenci muszą równolegle zmieniać te same pliki, np. przy różnych zadaniach w tym samym kodzie. W pozostałych przypadkach rozdziel zadania według plików lub folderów, poinformuj agentów o równoległej pracy i zapisz plan zależności; wspólne zmiany scalaj kolejno.
- W AGENTS.md zapisz regułę: agent nie tworzy worktree domyślnie. Osobne instalacje zależności zużywają dysk i CPU, a agenci często zapominają je posprzątać.
- Stan Git (gałąź, indeks i commity) zmienia tylko jeden koordynator; pozostali agenci edytują przydzielone pliki. Worktree nie usuwa konfliktów zmian tych samych plików - rozwiąż je przy scalaniu.
- Nie deleguj zadań wymagających pełnego kontekstu rozmowy (sub-agent go
  nie ma - dostaje tylko to, co napiszesz w zleceniu)

**Reguła:** sub-agent = "wynajmij konsultanta, przeczytaj raport".
Jeśli potrzebujesz dialogu i wspólnej pamięci - zostań w jednej sesji.

---

## 5) Hooks - deterministyczne bramki jakości

**Co to jest:** komendy uruchamiane automatycznie przez harness na zdarzenia
cyklu życia (przed/po edycji, przed commitem, na stop). W odróżnieniu od
instrukcji "pamiętaj o lintach" - hook wykona się ZAWSZE.

**Co tu umieszczać (checklist):**
- [ ] Format + lint po każdej edycji pliku
- [ ] Szybkie testy pakietu przed commitem
- [ ] Blokady: edycja plików wrażliwych, katalogów generowanych
- [ ] Automatyczne "czy na pewno skończone?" na zdarzenie stop

**Czego NIE umieszczać:** ciężkich analiz spowalniających każdą akcję
(pełny build w hooku po edycji = ból). Hook ma być szybki albo asynchroniczny.

---

## 6) Memory - fakty o osobie i sposobie pracy

**Co to jest:** trwała pamięć agenta między sesjami (w Claude Code: katalog
memory + MEMORY.md), zapisywana przez samego agenta lub skrótem `#`.

**Co tu umieszczać (checklist):**
- [ ] Preferencje osoby: package manager, styl odpowiedzi, godziny pracy
- [ ] Stabilne fakty o środowisku niewidoczne w repo
- [ ] Feedback "rób tak / nie rób tak" z uzasadnieniem

**Czego NIE umieszczać:** decyzji projektowych (te należą do repo - ADR!),
rzeczy, które widać w kodzie lub git history, sekretów. Test: *"czy nowy
członek zespołu też powinien to wiedzieć?"* Jeśli tak - to nie memory,
to AGENTS.md albo docs w repo.

---

## 7) PRD + ADR + Design Guidelines - pamięć produktu i architektury

**Co to jest:** dokumenty w repo (`docs/`), czytane przez agenta na żądanie.
Pisane **dla ludzi I dla agentów** - ten sam dokument służy zespołowi jako
źródło prawdy i agentowi jako kontekst.
PRD: co budujemy i po co (problem, użytkownik, zakres, kryteria akceptacji).
ADR: krótki zapis decyzji architektonicznej z alternatywami, które odrzucono.
Design Guidelines: system projektowy - tokeny (kolory, typografia, spacing),
komponenty, ton komunikacji - żeby agent generował spójne UI, a nie
"wariację na temat" przy każdej sesji.

**Co tu umieszczać (checklist):**
- [ ] PRD: problem, persona, zakres MVP, kryteria akceptacji, co POZA zakresem
- [ ] ADR: kontekst -> decyzja -> konsekwencje -> odrzucone alternatywy
- [ ] Jeden ADR = jedna decyzja (krótki; 1 strona max)
- [ ] Design Guidelines: tokeny + zasady użycia komponentów (np.
      `docs/design-guidelines.md`); wskaż go agentowi przy każdej pracy nad UI

**Dlaczego to element harnessu:** agent w nowej sesji nie pamięta, DLACZEGO
kod wygląda tak, a nie inaczej. Bez ADR "naprawi" Wam świadomą decyzję.
PRD zatrzymuje scope creep: agent sam sprawdza, czy feature jest w zakresie.

**Czego NIE umieszczać:** tasków i TODO (to plan/issues), szczegółów
implementacji zmiennych w czasie (to kod i testy).

---

## 8) Plan - mapa jednego zadania

**Co to jest:** plan konkretnego zadania: kolejność kroków, pliki do zmiany,
testy, checkpointy. W Claude Code: plan mode (agent najpierw bada i proponuje
plan, dopiero po akceptacji edytuje). Może być też plikiem `plan.md` / todo.
W odróżnieniu od PRD/ADR (dla ludzi i agentów, trwałe) plan jest **tylko dla
agentów i jednorazowy** - dokładne rozpisanie zadań na jedno wykonanie.

**Co tu umieszczać (checklist):**
- [ ] Kroki w kolejności, z plikami i testami per krok
- [ ] Checkpointy weryfikacji ("po kroku 2: testy pakietu X zielone")
- [ ] Ryzyka i decyzje do potwierdzenia z człowiekiem
- [ ] Kryterium końca ("done = testy + lint + demo działa")

**Cykl życia:** plan ŻYJE KRÓTKO. Po wykonaniu: wartościowe decyzje -> ADR,
zmiany zasad repo -> AGENTS.md, procedura do powtórzenia -> skill,
a sam plan można skasować. Plan, który został "dokumentacją", to dług.

**Reguła:** im większe zadanie, tym więcej wart plan. Zmiana 1 pliku nie
potrzebuje planu; refactoring 40 plików bez planu to hazard.

---

## 9) MCP - zewnętrzne narzędzia i dane dla agenta

**Co to jest:** Model Context Protocol - standard podłączania zewnętrznych
narzędzi (Jira, baza danych, przeglądarka, dokumentacja bibliotek) jako
narzędzi agenta. Serwer MCP działa lokalnie (stdio) albo zdalnie (HTTP)
i rozszerza możliwości agenta bez pisania własnych integracji.

**Gdzie konfigurować:**
- Claude Code: `.mcp.json` w katalogu głównym repo (zespołowe, commitowane)
  lub konfiguracja osobista (`claude mcp add`)
- OpenCode: klucz `"mcp"` w `opencode.json` (projektowym lub globalnym)

**Co tu umieszczać (checklist):**
- [ ] Serwer dokumentacji (np. Context7) - aktualne docs bibliotek na żądanie
- [ ] Integracje firmowe: Jira/Confluence (Atlassian MCP), GitLab/Bitbucket
- [ ] Narzędzia przeglądarkowe (Playwright MCP) - weryfikacja UI, testy E2E
- [ ] `"enabled": false` dla ciężkich/rzadko używanych serwerów - włączanie
      na żądanie (przykład: JetBrains MCP w `agent-configs/opencode/`)

**Czego NIE robić:**
- Nie włączaj wszystkich serwerów na stałe: każdy serwer MCP wstrzykuje
  opisy swoich narzędzi do kontekstu KAŻDEJ sesji (płacisz jak za długi
  AGENTS.md, a model gorzej wybiera narzędzia)
- Nie wpisuj sekretów wprost do konfiguracji - używaj zmiennych środowiskowych
- Nie podłączaj serwerów MCP z niezaufanych źródeł (opisy narzędzi to wektor
  prompt injection; serwer widzi też dane, które agent mu przekazuje)

**Różnice schematów** (ta sama idea, inna składnia):

| | Claude Code `.mcp.json` | OpenCode `opencode.json` |
|---|---|---|
| serwer stdio | `"type": "stdio"`, `command` (string) + `args` | `"type": "local"`, `command` (tablica) |
| zmienne środowiskowe | `"env"` | `"environment"` |
| serwer HTTP | `"type": "http"` | `"type": "remote"` + `"url"` |
| wyłączenie | `"enabled": false` | `"enabled": false` |

Przykłady z komentarzami w tym repo: `course-materials/agent-configs/opencode/opencode.jsonc`
oraz `.mcp.json` w katalogu głównym.

---

## 10) OpenCode - mapa odpowiedników

Cały ten dokument stosuje się też do OpenCode (również z modelami
self-hosted). Różnią się głównie składnia i lokalizacje plików:

| Element harnessu | Claude Code | OpenCode |
|---|---|---|
| Instrukcje repo | `AGENTS.md` / `CLAUDE.md` (import `@AGENTS.md`) | `AGENTS.md` natywnie (czyta też `CLAUDE.md`); dodatkowe pliki przez `"instructions"` w `opencode.json` |
| Instrukcje osobiste globalne | `~/.claude/CLAUDE.md` | `~/.config/opencode/AGENTS.md` |
| Settings | `.claude/settings.json` | `opencode.json` w repo / `~/.config/opencode/opencode.json` (JSONC, kolejność: globalny -> projektowy) |
| Permissions | `permissions` (listy allow/deny) | `"permission"`: `edit` / `bash` / `webfetch` = `"allow"` / `"ask"` / `"deny"` (także per agent) |
| Skills | `.claude/skills/` lub `.agents/skills/` | `.opencode/skills/`; czyta TEŻ `.claude/skills/` i `.agents/skills/` - te same skille działają w obu narzędziach |
| Custom commands | scalone ze skills (`/nazwa`) | osobny byt: `.opencode/commands/*.md` z frontmatter (`description`, `agent`, `model`) i szablonem (`$ARGUMENTS`, `$1..$n`, `@plik`) |
| Sub-agents | `.claude/agents/*.md` | `.opencode/agents/*.md`, frontmatter `mode: primary/subagent`; wywołanie `@nazwa` lub automatycznie przez Task tool |
| Hooks | `hooks` w `settings.json` | pluginy (custom tools, hooks, integracje) |
| Memory | katalog memory + MEMORY.md, skrót `#` | brak automatycznej pamięci - trwałe fakty zapisuj świadomie w `AGENTS.md` |
| MCP | `.mcp.json` | `"mcp"` w `opencode.json` (sekcja 9) |
| Model domyślny | `settings.json` / `/model` | `"model": "<provider>/<model-id>"` + opcjonalnie `"small_model"` |

**Modele lokalne / self-hosted w OpenCode:** blok `"provider"` z endpointem
OpenAI-compatible (Ollama, vLLM itp.) - kompletny przykład z komentarzami:
`course-materials/agent-configs/opencode/opencode.jsonc`.

---

## Tabela decyzyjna (ściąga)

| Informacja | Trwałość | Miejsce |
| --- | --- | --- |
| "Testy odpalamy `pnpm test`" | stała, całe repo | AGENTS.md |
| "Frontend: komponenty wg wzorca X" | stała, jeden moduł | `frontend/AGENTS.md` |
| "Nigdy nie dotykaj prod CLI" | stała, krytyczna | permissions/rules (+ zdanie w AGENTS.md) |
| "Jak robimy security review" | stała, wiele repo | skill |
| "Review robi osobny agent bez edycji" | stała, rola | sub-agent |
| "Lint po każdej edycji" | stała, automat | hook |
| "Wolę pnpm, odpowiadaj po polsku" | stała, osobista | memory / ~/.claude/CLAUDE.md |
| "Operator pobiera zgłoszenia z wybranego miesiąca do CSV, bez danych kontaktowych" | do zmiany wymagań produktu | PRD |
| "Pieniądze w decimal cents, nie float" | stała decyzja | ADR |
| "Kolory, typografia, zasady komponentów" | stała, całe UI | Design Guidelines |
| "T1: kontrakt CSV i test pustego miesiąca; T2: endpoint (po T1); T3: przycisk (po T1); T4: test przepływu (po T2 i T3)" | jedno zadanie | plan / plan mode |
| "Odrzucam sugestię X w tym diffie" | jeden PR | komentarz PR |
| "Aktualna dokumentacja biblioteki Y" | na żądanie | MCP (np. Context7) |
| "Szablon promptu z parametrami" | stała, powtarzalna | skill lub custom command (Claude Code / OpenCode) |

---

## Top 8 antywzorców

1. **Wszystko do AGENTS.md** - 500 linii, których model nie czyta uważnie.
2. **Sekrety w plikach instrukcji** - trafią do logów i odpowiedzi.
3. **Plan jako dokumentacja** - nieaktualny plan myli kolejne sesje.
4. **Memory zamiast ADR** - decyzje projektowe znikają z repo.
5. **Skill na wszystko** - 40 skilli o zbyt podobnych opisach; agent
   wybiera zły albo żaden. Skill ma mieć ostry trigger.
6. **Instrukcja markdown zamiast permissions** - "nie kasuj bazy" musi być
   regułą harnessu, nie prośbą.
7. **Sub-agenci na wspólnych plikach** - Worktree twórz tylko wtedy, gdy agenci muszą równolegle zmieniać te same pliki, np. przy różnych zadaniach w tym samym kodzie. W pozostałych przypadkach rozdziel zadania według plików lub folderów, poinformuj agentów o równoległej pracy i zapisz plan zależności; wspólne zmiany scalaj kolejno.
8. **Wszystkie serwery MCP włączone na stałe** - opisy narzędzi zjadają
   kontekst każdej sesji; ciężkie serwery trzymaj z `"enabled": false`.

---

## Minimalny zestaw startowy

**Greenfield (nowy projekt):**
1. AGENTS.md (30-60 linii): komendy, konwencje, definicja done
2. PRD (1-2 strony) + pierwszy ADR (stack)
3. Permissions: allowlist komend projektu, denylist destrukcyjnych
4. Plan mode dla pierwszego feature'a; po nim - zapisz ADR-y
5. Hook: lint/format po edycji
6. Skills i sub-agentów dodawaj dopiero, gdy zobaczysz powtórkę

**Brownfield (istniejący kod):**
1. Sesja eksploracji: agent sam pisze szkic AGENTS.md (Ty weryfikujesz!)
2. ADR-y wstecz dla 3-5 kluczowych decyzji (z git log / wywiadu z zespołem)
3. Permissions od dnia 1 (stary kod = więcej niespodzianek)
4. Sub-agent researcher do mapowania modułów przed pierwszą zmianą
5. Pierwsze zmiany wyłącznie przez plan mode + małe PR-y

Pełne wersje krok po kroku (z odpowiednikami OpenCode):
[greenfield-checklist.md](greenfield-checklist.md) i
[brownfield-checklist.md](brownfield-checklist.md) w tym katalogu.
