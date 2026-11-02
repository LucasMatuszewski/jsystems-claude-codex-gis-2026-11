# Podsumowanie - dzień 1, 2 listopada 2026

Źródła: podsumowania spotkania Zoom oraz [historia czatu](day-1-chat-history.md). Godziny w czasie polskim.

## Przegląd

Pierwszy dzień szkolenia poświęcono konfiguracji dostępu do narzędzi i środowisk, wprowadzeniu do agentów AI oraz omówieniu tokenów, kontekstu, modeli i Skills. Grupa rozmawiała o zastosowaniach agentów w pracy z kodem, danymi i automatyzacją. Trener, Łukasz Matuszewski, pokazał także sposoby instalowania narzędzi i Skills oraz omówił analizę repozytorium pod kątem prompt injection.

## Organizacja

Na początku dnia rozwiązywano problemy z zaproszeniami i logowaniem do Claude oraz ChatGPT. Udostępniono środowiska szkoleniowe i materiały, a w czacie podano polecenia instalacji i logowania:

- Windows: `winget install Anthropic.ClaudeCode`
- Linux i macOS: `curl -fsSL https://claude.ai/install.sh | bash`
- Logowanie do Codex na zdalnym komputerze: `codex login --device-auth`

Omówiono pracę przez CLI/TUI, wtyczki do VS Code i JetBrains oraz aplikacje desktopowe Claude i ChatGPT. W rozmowie pojawiły się Windows, Linux i macOS. Materiały kursu są dostępne na stronie [szkolenia](https://devpowers.com/szkolenia/jsystems/tomtom-ai-2026-11/index.html), a repozytorium ćwiczeniowe pod adresem [GitHub](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11).

**Pytanie:** Czy do dalszej pracy lepiej używać komputera prywatnego, czy środowiska szkoleniowego?

**Odpowiedź:** Do długoterminowej pracy przydatny jest własny komputer, natomiast środowisko szkoleniowe wystarcza na potrzeby kursu.

## Temat 1: Zastosowania agentów i sposoby pracy

Grupa omawiała wykorzystanie AI w analizie danych, tworzeniu aplikacji i skryptów, automatyzacji zadań oraz przetwarzaniu danych GIS. Wśród poruszonych przykładów znalazły się generowanie kodu w Pythonie i PowerShellu, analiza obrazów, praca z danymi i dashboardami, migracja przepływów FME do SQL oraz obsługa zadań i zależności w narzędziach do zarządzania pracą.

Omówiono różne sposoby korzystania z modeli: przez terminal, wtyczki edytorów i aplikacje desktopowe. Wspomniano też o rozwoju narzędzi agentowych na przykładach Tabnine, CrewAI i LangChain oraz o OpenCode. Pojawiły się pytania o pracę z dużymi repozytoriami, pamięć agenta między sesjami, limity tokenów i automatyzację zadań zależnych od VPN lub zalogowanego komputera.

## Temat 2: Modele, tokeny i zarządzanie kontekstem

Tokeny są jednostkami tekstu przetwarzanymi przez model, a długość kontekstu ogranicza ilość informacji dostępnej w danej sesji. Większa liczba tokenów może zwiększać koszt. Do sprawdzania tokenizacji tekstu udostępniono [Tokenizer OpenAI](https://platform.openai.com/tokenizer).

Omówiono dobór modeli do zadań o różnej złożoności oraz porównywanie ich jakości i kosztów. Na [Arena.ai](https://arena.ai/) pokazano rankingi, w tym [ranking modeli agentowych](https://arena.ai/leaderboard/agent) i [ranking modeli do kodowania](https://arena.ai/leaderboard/code/webdev). W czacie pojawiły się przykłady Opus 5.5 i Hunyuan HY4 preview, a także [agregator benchmarków Artificial Analysis](https://artificialanalysis.ai/). Wspomniano również o modelach lokalnych i orientacyjnej rekomendacji około 32 GB VRAM dla wskazanego przykładu [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B).

Rozróżniono ogólną jakość pracy z agentami od skuteczności wyszukiwania w RAG. Zwrócono uwagę, że język polski może mieć przewagę w określonych zadaniach wyszukiwania informacji w przestrzeni wektorowej, ale nie oznacza to automatycznie przewagi w każdym zastosowaniu. Wśród dodatkowych materiałów znalazły się zasoby o [modelach decyzyjnych TypeSafe](https://typesafe.ai/) i [przewodnik OpenAI dotyczący decyzji](https://developers.openai.com/api/docs/guides/decisions).

Polecenie `/compact` służy do streszczenia lub kompresji bieżącej sesji, aby ograniczyć zajętość okna kontekstowego. Wspomniano też o plikach `CLAUDE.md` jako sposobie przekazywania agentowi trwałych instrukcji i informacji o projekcie.

**Pytanie:** Czy język polski jest lepszy od angielskiego przy pracy z agentami?

**Odpowiedź:** Zależy to od zadania. W dyskusji o RAG przywołano wyniki, według których polski może lepiej sprawdzać się w wyszukiwaniu informacji w przestrzeni wektorowej; nie jest to ogólna ocena wszystkich zastosowań agentów.

## Temat 3: Skills i instalowanie powtarzalnych procedur

Skills opisują procedury, które agent może stosować wielokrotnie. Podstawowym elementem jest plik `SKILL.md`; materiały pomocnicze mogą być dodawane opcjonalnie. Instrukcje powinny jasno określać, kiedy dany skill ma być użyty, a jego zawartość powinna opisywać możliwe do ponownego zastosowania kroki, zamiast gromadzić informacje specyficzne dla pojedynczego projektu.

Pokazano przykład skilla do tworzenia ADR w repozytorium [agent-toolbox](https://github.com/EdukeyTeam/agent-toolbox/tree/main/skills/write-adr), wyszukiwarkę i menedżer [Skills.sh](https://www.skills.sh/) oraz instalację z wiersza poleceń. Przykładowe polecenia z czatu:

- `npx --yes skills@latest add EdukeyTeam/agent-toolbox --skill '*'`
- `npx skills add https://github.com/vosslab/vosslab-skills --skill pyside6-engineer`

Jako typową lokalizację Skills wskazano `.agents/skills`.

Przed instalacją skilla z zewnętrznego źródła warto poprosić agenta o jego ocenę pod kątem bezpieczeństwa (elementy podatne na prompt injection, niebezpieczne polecenia) i jakości. Ćwiczenie wykonano na przykładzie skilla [pyside6-engineer](https://github.com/vosslab/vosslab-skills/tree/main/skills/experts/pyside6-engineer).

**Pytanie:** Co zrobić, gdy skill zaczyna gromadzić zbyt wiele informacji o bieżącym projekcie?

**Odpowiedź:** Oddzielić ogólną procedurę od wiedzy specyficznej dla projektu i doprecyzować warunki użycia skilla oraz jego zakres.

**Pytanie:** Czy agent może pomóc w utworzeniu aplikacji desktopowej?

**Odpowiedź:** Tak. Zachęcono do wypróbowania takiego zadania z agentem.

## Temat 4: Bezpieczeństwo i prompt injection

Prompt injection polega na próbie wpływania na działanie agenta przez instrukcje umieszczone na przykład w repozytorium, kodzie lub stronie internetowej. Przy analizie nieznanych materiałów warto sprawdzić je przed uruchomieniem i korzystać z odizolowanego środowiska, takiego jak maszyna wirtualna.

W demonstracji w [Claude Code w przeglądarce](https://claude.ai/code) agent przygotował, w podejściu Code Mode (agent pisze i uruchamia skrypt zamiast czytać pliki pojedynczo), skrypt analizujący wszystkie pliki publicznego repozytorium szkoleniowego pod kątem charakterystycznych wzorców prompt injection i innych prób manipulowania agentem. Materiałem uzupełniającym jest [dokumentacja bezpieczeństwa Claude Code](https://code.claude.com/docs/en/security).

## Plan na kolejne dni

Kolejny dzień szkolenia ma kontynuować praktyczną pracę z agentami, repozytoriami i Skills.

## Kolejne kroki

### Trener

- Dokończyć obsługę problemów z zaproszeniami i dostępem do kont.
- Zapewnić lokalną kopię repozytorium i materiałów szkoleniowych.

### Uczestnicy

- Zalogować się do udostępnionych środowisk Claude i ChatGPT.
- Sklonować [repozytorium szkoleniowe](https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11) i przejść do jego katalogu.
- Zainstalować Skills na poziomie projektu zgodnie z instrukcjami z zajęć.
