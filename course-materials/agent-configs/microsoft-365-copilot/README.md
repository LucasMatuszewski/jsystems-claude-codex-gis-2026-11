# Microsoft 365 Copilot: agent z dwoma skillami

Przykład agenta z Agent Buildera w Microsoft 365 Copilot. Pokazuje te same elementy co agent w GitHub Copilot: instrukcje (odpowiednik `AGENTS.md`), agenta z własną rolą i skille, także ze skryptem.

**Repository Checker** ocenia repozytorium z GitHub albo GitLab (bibliotekę, skill agenta, serwer MCP), zanim je sklonujesz, pobierzesz lub uruchomisz, i doradza, do czego może się przydać w Twojej pracy.

[Paczka agenta (ZIP)](repository-checker/repository-checker.zip) | [Rozpakowana zawartość](repository-checker/agent/)

| Plik | Do czego służy |
|---|---|
| [`declarativeAgent_0.json`](repository-checker/agent/declarativeAgent_0.json) | Instrukcje agenta, pięć startowych promptów, wyszukiwanie w sieci ograniczone do github.com i gitlab.com, Code Interpreter |
| [`manifest.json`](repository-checker/agent/manifest.json) | Manifest aplikacji Microsoft 365 (nazwa, opis, ikony) |
| [`repository-security-audit`](repository-checker/agent/skills/repository-security-audit/SKILL.md) | Skill: audyt bezpieczeństwa bez uruchamiania kodu repozytorium. Prompt injection, wykonywanie poleceń, wyciek danych, telemetria, zależności, CI, ryzyka typowe dla Javy i reputacja projektu. Kończy się jedną z pięciu rekomendacji. |
| [`scripts/main.py`](repository-checker/agent/skills/repository-security-audit/scripts/main.py) | Statyczny skaner wzorców (Python, bez zależności) uruchamiany w Code Interpreterze. Zapisuje `repository-audit.json` z plikiem, linią i ważnością każdego trafienia. Trafienie to trop do sprawdzenia, nie dowód. |
| [`repository-use-case-advisor`](repository-checker/agent/skills/repository-use-case-advisor/SKILL.md) | Skill: co repozytorium robi, jak działa i gdzie pasuje w Twojej pracy. Uwzględnia wynik audytu i nie poleca uruchamiania czegoś, co audyt odradził. |

## Jak użyć

- **Microsoft 365 Copilot:** utwórz agenta w Agent Builderze, wklej `instructions` i startowe prompty z `declarativeAgent_0.json`, włącz Code Interpreter i dodaj oba foldery skilli, jeśli Twój tenant obsługuje skille w agentach. Czy możesz zaimportować całą paczkę ZIP, zależy od ustawień Twojej organizacji; zapytaj administratora Microsoft 365.
- **GitHub Copilot:** foldery z `repository-checker/agent/skills/` to zwykłe skille agenta (`SKILL.md` z opisem i instrukcjami). Skopiuj je do `.github/skills/` w swoim projekcie.

Czysty wynik skanera nie dowodzi, że repozytorium jest bezpieczne. O pobraniu kodu do sieci firmowej decydujesz zgodnie z zasadami swojej organizacji.
