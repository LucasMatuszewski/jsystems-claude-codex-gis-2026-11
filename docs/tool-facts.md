# Stan narzędzi do sprawdzenia przed zajęciami

Zweryfikowano 26.09.2026. Dostęp zależy od planu i polityki organizacji; ten plik nie potwierdza uprawnień uczestników.

- GitHub Copilot cloud agent może pracować nad issue i przygotować pull request do przeglądu. W organizacjach Business dostęp do niego może wymagać włączenia przez administratora. Zobacz [cloud agent access](https://docs.github.com/en/copilot/concepts/enterprise/cloud-agent-access) i [użycie agentów](https://docs.github.com/en/copilot/how-tos/use-copilot-agents).
- Instrukcje repozytorium `.github/copilot-instructions.md` są podstawą kontekstu tego ćwiczenia. Obsługa `AGENTS.md` i innych formatów zależy od powierzchni Copilot; [macierz obsługi instrukcji](https://docs.github.com/en/copilot/reference/custom-instructions-support) wymaga sprawdzenia dla VS Code, JetBrains, GitHub.com i CLI osobno.
- [Prompt files](https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files/review-code) mogą przechowywać powtarzalny prompt review; lokalny przykład jest w `.github/prompts/`.
- Funkcje chmurowe, MCP, CLI oraz licznik AI Credits zależą od planu i ustawień organizacji. Sprawdź [aktualny plan](https://docs.github.com/en/copilot/get-started/plans) i politykę organizacji. Samo włączenie wykluczenia treści nie jest dowodem, że każdy tryb IDE respektuje to ustawienie.
- Lista umiejętności publicznego [EdukeyTeam/agent-toolbox](https://github.com/EdukeyTeam/agent-toolbox) została sprawdzona poleceniem `npx --yes skills@latest add EdukeyTeam/agent-toolbox --list`; wybór `write-adr` i lokalna instalacja projektowa w tymczasowym katalogu z `--agent github-copilot -y` zakończyły się powodzeniem. Aktywację w konkretnym IDE trzeba sprawdzić na maszynie uczestnika.
