# Przykłady instrukcji dla agentów

To są **materiały do skopiowania i dostosowania podczas zajęć**, nie instrukcje aktywne w tym repozytorium. Copilot nie potraktuje pliku `claude-course-2026-07-AGENTS.md` jako głównego `AGENTS.md` tylko dlatego, że znajduje się w tym folderze.

| Plik | Zastosowanie |
| --- | --- |
| `claude-course-2026-07-AGENTS.md` | Zachowany przykład z wcześniejszego, trzydniowego kursu. Pokazuje strukturę projektu, proces od PRD i ADR do testów, zasady commitów i kryteria ukończenia. |
| `claude-course-2026-07-CLAUDE.md` | Towarzyszący przykład konfiguracji Claude Code, odsyłający do głównego `AGENTS.md`. Przy pracy wyłącznie z Copilotem nie trzeba go dodawać. |
| `nextjs-example-AGENTS.md` | Bardziej szczegółowy przykład dla projektu Next.js i PayloadCMS. |
| `microsoft-mcp-AGENTS.md` | Przykład dla istniejącego repozytorium edukacyjnego o MCP. |

## Ćwiczenie z własnym projektem

1. Otwórz przykład z wcześniejszego kursu i **porównaj go** ze swoim PRD, ADR (jeśli powstał), kodem i rzeczywistymi poleceniami testowymi.
2. Skopiuj go do głównego katalogu **własnego projektu** jako `AGENTS.md`. Usuń lub zmień informacje o dawnym kursie, maszynach, narzędziach, stosie technologicznym i ścieżkach, które nie pasują do Twojej aplikacji.
3. Zachowaj tylko reguły, które grupa akceptuje i może sprawdzić: gdzie są wymagania, jak uruchomić aplikację, jak testować, jak przeglądać zmiany i kiedy wolno commitować lub wysyłać kod.
4. Poproś agenta o wskazanie, **które instrukcje faktycznie odczytał**. Po zmianie architektury lub poleceń aktualizuj `AGENTS.md` razem z kodem.

Przykład z lipca zachowano jako materiał historyczny; 16.10.2026 uzupełniono go o regułę mocków opartych na rzeczywistej odpowiedzi i sekcję Manual QA. Jego opis środowiska Windows Server, narzędzi Claude, biblioteki Context7 i skryptu publikacji slajdów **nie dotyczy automatycznie** obecnego kursu.
