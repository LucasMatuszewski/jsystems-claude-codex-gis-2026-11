# Brownfield Checklist - agenci w istniejącym projekcie (legacy)

Kolejność kroków przy wdrażaniu agentów (Claude Code, OpenCode - z modelami
chmurowymi lub self-hosted) do istniejącego kodu. Skrócona wersja
i wyjaśnienie "co gdzie": [harness-checklist.md](harness-checklist.md).

Różnica vs greenfield: tu agent NIE zna decyzji, które ukształtowały kod,
a kod pełen jest niespodzianek. Dlatego kolejność jest odwrócona:
**najpierw granice i eksploracja, dopiero potem zmiany**.

---

## Krok 0 - granice bezpieczeństwa PRZED pierwszą sesją

- [ ] Denylist od dnia 1: produkcyjne CLI, komendy destrukcyjne, migracje
      baz, katalogi z sekretami (stary kod = więcej niespodzianek niż nowy)
- [ ] Claude Code: `permissions` w `.claude/settings.json`;
      OpenCode: `"permission"` w `opencode.json` (`"allow"`/`"ask"`/`"deny"`
      dla `edit`, `bash`, `webfetch`)
- [ ] Sprawdź, czy w repo nie leżą sekrety (`.env` w git? tokeny w konfiguracji?);
      jeśli tak - usuń/zrotuj ZANIM agent zacznie czytać pliki
- [ ] `.env.example` zamiast prawdziwych wartości; sekrety do zmiennych
      środowiskowych
- [ ] Upewnij się, że jest kopia/branch startowy - agentowi potrzebny punkt
      powrotu (`git switch -c agents-onboarding`)

## Krok 1 - sesja eksploracji: agent pisze szkic AGENTS.md

- [ ] Poproś agenta o zwiedzenie repo i NAPISANIE szkicu AGENTS.md:
      komendy build/test/lint (niech je URUCHOMI i potwierdzi, że działają),
      struktura katalogów, konwencje, które widzi w kodzie
- [ ] TY weryfikujesz każdą linię - agent zgaduje z kodu, a kod bywa
      niereprezentatywny (stare wzorce, martwe katalogi)
- [ ] Zapisz też to, czego agent NIE wywnioskuje z kodu: dziwne środowisko,
      "tego katalogu nie ruszamy, bo...", zależności od innych systemów
- [ ] Claude Code: `CLAUDE.md` = jedna linia `@AGENTS.md`;
      OpenCode: czyta `AGENTS.md` natywnie
- [ ] Cel: 30-60 linii; nie przepisuj całej wiedzy plemiennej naraz -
      dopisuj, gdy agent się potknie

## Krok 2 - ADR-y wstecz dla 3-5 kluczowych decyzji

- [ ] Z `git log`, komentarzy i wywiadu z zespołem odtwórz decyzje, które
      ukształtowały architekturę ("czemu monolit", "czemu ta baza",
      "czemu własny framework do X")
- [ ] Format: kontekst -> decyzja -> konsekwencje -> odrzucone alternatywy;
      jeden ADR = jedna decyzja, do `docs/ADR/`
- [ ] Bez tego agent w dobrej wierze "naprawi" świadome decyzje - i zrobi
      to przekonująco
- [ ] Dopisuj kolejne ADR-y, gdy podczas pracy odkryjecie następne
      niepisane decyzje

## Krok 3 - stan testów: ustal, na czym stoisz

- [ ] Uruchom istniejące testy; zapisz w AGENTS.md, jak się je odpala
      i czego się spodziewać (które są flaky, które wolne)
- [ ] Brak testów w obszarze, który będziesz zmieniać? Najpierw testy
      charakteryzujące (opisujące OBECNE zachowanie, nawet jeśli dziwne) -
      dopiero potem zmiany
- [ ] Definicja "done" w AGENTS.md: co musi być zielone przed commitem
- [ ] Testy przechodzą != aplikacja działa: zapisz też, jak uruchomić
      aplikację i po czym poznać, że żyje

## Krok 4 - sub-agent researcher do mapowania

- [ ] Zanim zmienisz moduł, wyślij sub-agenta researchera (rola tylko-czytanie),
      żeby zmapował zależności i zwrócił raport - jego "brudny" kontekst
      (dziesiątki przeczytanych plików) nie zaśmieca Twojej sesji
- [ ] Claude Code: `.claude/agents/researcher.md` (bez prawa edycji);
      OpenCode: `.opencode/agents/researcher.md` (`mode: subagent`,
      wywołanie `@researcher`)
- [ ] Wnioski z raportów: trwałe -> AGENTS.md lub docs, jednorazowe -> plan

## Krok 5 - MCP tam, gdzie firma już ma dane

- [ ] Integracje firmowe: Jira/Confluence (Atlassian MCP), GitLab/Bitbucket -
      agent czyta tickety i historię zamiast zgadywać
- [ ] Serwer dokumentacji (np. Context7) dla bibliotek, na których stoi projekt
- [ ] Ciężkie/rzadkie serwery `"enabled": false`, włączane na żądanie
- [ ] Claude Code: `.mcp.json`; OpenCode: `"mcp"` w `opencode.json`
      (różnice składni: harness-checklist sekcja 9)

## Krok 6 - pierwsze zmiany: wyłącznie plan mode + małe PR-y

- [ ] Każda zmiana zaczyna się od planu: kroki, pliki, testy, checkpointy;
      edycje dopiero po Twojej akceptacji planu
- [ ] Małe PR-y (jeden temat), częste commity, łatwy rollback
- [ ] Zasada dla legacy: refactoring i zmiana zachowania NIGDY w jednym
      commicie
- [ ] Po zadaniu: decyzje -> ADR, nowe zasady -> AGENTS.md, procedura
      do powtórki -> skill, plan skasuj

## Krok 7 - zagnieżdżone AGENTS.md dla obszarów o różnych regułach

- [ ] Moduły z własnymi konwencjami (stary frontend vs nowy, inny język,
      inne standardy) dostają własny `AGENTS.md` w podkatalogu -
      agent czyta go dopiero, gdy tam pracuje (naturalne lazy loading)
- [ ] Główny AGENTS.md zostaje krótki i uniwersalny (~150 linii max)

## Krok 8 - automatyzacja bramek jakości

- [ ] Lint/format po każdej edycji; szybkie testy przed commitem
- [ ] Blokady na pliki wrażliwe i katalogi generowane
- [ ] Claude Code: `hooks` w `settings.json`; OpenCode: pluginy
- [ ] W legacy hooki są ważniejsze niż w greenfield: automatyczna bramka
      wyłapie regresję, o której instrukcja w markdown "zapomni"

## Krok 9 - skills z powtarzalnych procedur zespołu

- [ ] Procedury, które zespół powtarza od lat ("jak dodajemy endpoint",
      "jak robimy release", "jak debugujemy X") - spisz jako skills;
      to jednocześnie onboarding dla ludzi i dla agentów
- [ ] Skills: `.claude/skills/` lub `.agents/skills/` - OpenCode czyta oba
      oraz własny `.opencode/skills/` (jeden skill działa w obu narzędziach)
- [ ] OpenCode dodatkowo: proste szablony promptów jako custom commands
      (`.opencode/commands/*.md`, zmienne `$ARGUMENTS`, `$1..$n`)
- [ ] Sygnał: trzeci raz tłumaczysz agentowi to samo -> skill

## Krok 10 - rytm i higiena

- [ ] Nowe zadanie = świeża sesja; nie ciągnij jednego kontekstu przez
      wiele tematów
- [ ] Raz w tygodniu: przejrzyj AGENTS.md (rośnie? wydziel), skasuj
      martwe plany, dopisz brakujące ADR-y
- [ ] Mierz efekt: czy agent przestał zadawać te same pytania? Czy PR-y
      przechodzą review bez uwag o konwencje? To test jakości harnessu

---

## Minimalny dzień pierwszy (wersja "nie mam czasu")

1. Krok 0 (denylist + sprawdź sekrety + branch startowy)
2. Krok 1 (sesja eksploracji -> szkic AGENTS.md, Ty weryfikujesz)
3. Krok 6 (pierwsza zmiana przez plan mode, mały PR)

ADR-y wstecz (Krok 2) zrób w pierwszym tygodniu - to najtańsze
ubezpieczenie od "agent naprawił nam architekturę".
