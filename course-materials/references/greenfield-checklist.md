# Greenfield Checklist - nowy projekt z agentami od dnia pierwszego

Kolejność kroków przy starcie nowego projektu, w którym od początku pracują
agenci (Claude Code, OpenCode - z modelami chmurowymi lub self-hosted).
Skrócona wersja i wyjaśnienie "co gdzie": [harness-checklist.md](harness-checklist.md).

Zasada: **najpierw dokumenty i granice, potem kod**. Każda godzina włożona
w PRD, ADR i AGENTS.md zwraca się w każdej kolejnej sesji agenta.

---

## Krok 0 - repo i szkielet

- [ ] `git init` + pierwszy commit (agent musi mieć punkt powrotu od początku)
- [ ] README: jedno zdanie "co budujemy i dla kogo" (agent też je czyta)
- [ ] `.gitignore` + `.env.example` (sekrety NIGDY w repo - agent może
      wkleić zawartość plików do odpowiedzi i logów)

## Krok 1 - PRD zanim powstanie kod

- [ ] Problem: czyj problem rozwiązujemy i skąd wiemy, że istnieje
- [ ] Persona / użytkownik docelowy
- [ ] Zakres MVP + jawna lista "POZA zakresem" (to zatrzymuje scope creep,
      także ten proponowany przez agenta)
- [ ] Kryteria akceptacji - mierzalne, testowalne
- [ ] Zapisz do `docs/PRD-....md`; wygeneruj z agentem w trybie wywiadu
      (przykładowe prompty: `course-materials/Prompt examples/`)

## Krok 2 - pierwsze ADR-y

- [ ] ADR-001: wybór stacku (kontekst -> decyzja -> konsekwencje ->
      odrzucone alternatywy)
- [ ] Jeden ADR = jedna decyzja, max 1 strona, do `docs/ADR/`
- [ ] Każda kolejna ważna decyzja w trakcie budowy = nowy ADR (inaczej
      następna sesja agenta "naprawi" Wam świadomy wybór)

## Krok 3 - AGENTS.md (konstytucja repo, 30-60 linii)

- [ ] Komendy: build, test, lint, typecheck - dokładne, z package managerem
- [ ] Konwencje: język, styl, struktura katalogów, nazewnictwo
- [ ] Definicja "done": co musi przejść, zanim agent uzna pracę za skończoną
- [ ] Granice: czego nie czytać (sekrety), czego nie uruchamiać (deploy)
- [ ] Wskaźniki do PRD/ADR ("wymagania: docs/PRD-....md")
- [ ] Claude Code: `CLAUDE.md` z jedną linią `@AGENTS.md`
- [ ] OpenCode: czyta `AGENTS.md` natywnie (nic więcej nie trzeba);
      dodatkowe pliki można wskazać w `opencode.json` -> `"instructions"`
- [ ] Trzymaj krótko; szczegóły modułów trafią później do zagnieżdżonych
      `AGENTS.md` w podkatalogach

## Krok 4 - permissions od startu

- [ ] Allowlist bezpiecznych komend projektu (test, lint, build) - mniej
      pytań o zgodę, szybsza praca
- [ ] Denylist: destrukcyjne komendy, produkcyjne CLI, katalogi z sekretami
- [ ] Claude Code: `permissions` w `.claude/settings.json` (commitowane
      dla zespołu)
- [ ] OpenCode: `"permission"` w `opencode.json`, wartości `"allow"` /
      `"ask"` / `"deny"` dla `edit`, `bash`, `webfetch` (też per agent)
- [ ] Reguła: kosztowna zasada = permissions, nie zdanie w markdown
      (markdown to prośba, settings to prawo)

## Krok 5 - MCP tylko tam, gdzie potrzebne

- [ ] Serwer dokumentacji (np. Context7) - aktualne docs wybranego stacku
- [ ] Playwright MCP, jeśli budujecie UI (agent sam zweryfikuje efekt
      w przeglądarce)
- [ ] Ciężkie/rzadkie serwery z `"enabled": false` - włączane na żądanie
- [ ] Claude Code: `.mcp.json` w repo; OpenCode: `"mcp"` w `opencode.json`
      (schematy różnią się składnią - tabela w harness-checklist, sekcja 9;
      przykład: `course-materials/agent-configs/opencode/opencode.jsonc`)

## Krok 6 - pierwszy feature przez plan mode

- [ ] Agent najpierw bada i proponuje plan; edycje dopiero po akceptacji
- [ ] Plan: kroki z plikami i testami, checkpointy weryfikacji, kryterium
      końca
- [ ] Po wykonaniu: decyzje -> ADR, nowe zasady -> AGENTS.md, sam plan
      można skasować (plan, który został "dokumentacją", to dług)

## Krok 7 - testy jako fundament

- [ ] Infrastruktura testowa w pierwszym tygodniu, nie "kiedyś"
- [ ] TDD z agentem: test przed implementacją; agent ma potwierdzić,
      że nowy test najpierw failuje z oczekiwanego powodu
- [ ] Definicja "done" w AGENTS.md odwołuje się do testów ("testy pakietu
      zielone, lint bez błędów")

## Krok 8 - automatyzacja bramek jakości

- [ ] Lint/format automatycznie po każdej edycji pliku
- [ ] Szybkie testy przed commitem
- [ ] Claude Code: `hooks` w `settings.json`; OpenCode: pluginy
- [ ] Hook ma być szybki - pełny build w hooku po edycji to ból

## Krok 9 - skills i sub-agenci dopiero przy powtórce

- [ ] Trzeci raz tłumaczysz agentowi to samo w prompcie -> czas na skill
- [ ] Dobra sesja, którą chcesz umieć powtórzyć -> "zrób z tej sesji skill"
- [ ] Skills: `.claude/skills/` lub `.agents/skills/` - OpenCode czyta
      oba te katalogi oraz własny `.opencode/skills/` (jeden skill działa
      w obu narzędziach)
- [ ] OpenCode dodatkowo: proste szablony promptów jako custom commands
      (`.opencode/commands/*.md`, zmienne `$ARGUMENTS`, `$1..$n`)
- [ ] Sub-agenci, gdy klarują się role: reviewer (bez prawa edycji),
      researcher, QA - Claude Code: `.claude/agents/*.md`;
      OpenCode: `.opencode/agents/*.md` (`mode: subagent`, wywołanie `@nazwa`)

## Krok 10 - rytm pracy

- [ ] Małe zadania, małe PR-y; jeden logiczny temat = jeden commit
- [ ] Commit dopiero po weryfikacji (testy + lint + aplikacja startuje;
      testy przechodzą != aplikacja działa)
- [ ] Nowe zadanie = świeży kontekst/sesja; nie ciągnij jednej rozmowy
      przez trzy różne tematy
- [ ] Raz w tygodniu przejrzyj AGENTS.md: czy urósł ponad ~150 linii?
      Wydziel skills / zagnieżdżone pliki / docs

---

## Minimalny dzień pierwszy (wersja "nie mam czasu")

1. Krok 0 + Krok 3 (AGENTS.md, choćby 20 linii: komendy + definicja done)
2. Krok 4 (permissions: denylist destrukcyjnych)
3. Krok 1 (PRD - może być 1 strona)
4. Pierwszy feature przez plan mode (Krok 6)

Reszta dojdzie naturalnie - byle nie pomijać ADR-ów przy ważnych decyzjach.
