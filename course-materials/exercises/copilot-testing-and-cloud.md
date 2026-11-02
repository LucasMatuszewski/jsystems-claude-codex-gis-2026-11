# GitHub Copilot: konfiguracja, testy i zadanie w chmurze

Pracuj na wskazanej aplikacji i jej aktualnym PRD. Materiały kursowe nie określają domeny ani stacku Twojego projektu. Nie zaczynaj od gotowego rozwiązania: wybierz jeden obserwowalny fragment i dane syntetyczne.

Budżet: 60 minut pracy i do 30 minut rezerwy na dostęp lub uruchomienie środowiska. Podział: konfiguracja 10 min, testy 20 min, hook 5 min, CLI/cloud 15 min, model i wnioski 10 min. Wybierz jeden mały przypadek; brak dostępu uruchamia opisany wariant lokalny lub analizę dowodów, bez udawania wykonania.

## 1. Instrukcja, prompt, skill czy agent

| Potrzeba | Przykład pliku | Jak sprawdzisz wynik |
|---|---|---|
| Stała zasada całego projektu | [.github/copilot-instructions.md](../../.github/copilot-instructions.md) | Agent rozpoznaje rzeczywisty projekt i jego polecenia |
| Zasada dla testów | [.github/instructions/tests.instructions.md](../../.github/instructions/tests.instructions.md) | Instrukcja dotyczy pasujących plików w obsługiwanym kliencie |
| Jedno powtarzalne wywołanie | [.github/prompts/review-ticket.prompt.md](../../.github/prompts/review-ticket.prompt.md) | Ręcznie wybrany prompt sprawdza aktualny diff i PRD |
| Procedura wieloetapowa | [course-materials/agent-configs/copilot/skills/test-evidence/SKILL.md](../agent-configs/copilot/skills/test-evidence/SKILL.md) w materiałach | Po świadomym zainstalowaniu/wybraniu daje powtarzalny raport |
| Specjalista z ograniczonymi narzędziami | [course-materials/agent-configs/copilot/agents/test-engineer.agent.md](../agent-configs/copilot/agents/test-engineer.agent.md) w materiałach | Po świadomym skopiowaniu do `.github/agents/` zgłasza tylko przypisane zmiany |
| Deterministyczna kontrola narzędzia | [course-materials/hooks-example/copilot/block-secrets.json](../hooks-example/copilot/block-secrets.json) w materiałach | Syntetyczny przypadek dozwolony i zabroniony mają różne wyniki |

W wariancie legacy lub mixed repozytorium materiałów i aplikacja są oddzielnymi checkoutami. W rzeczywistym repozytorium aplikacji najpierw przeczytaj istniejące AGENTS.md oraz `.github/`. Po uzgodnieniu zakresu z właścicielem scal odpowiednie zasady i prompty z podlinkowanych przykładów z konfiguracją aplikacji; dopasuj globs, stack i polecenia do jej źródeł. Nie nadpisuj istniejących instrukcji ani nie kopiuj całego `.github/` z workflowami i hookami. Uruchom Copilota w tym checkoutcie i potwierdź odczyt właściwych plików oraz jedno nieszkodliwe zachowanie wynikające z instrukcji. Jeśli nie wolno zmieniać konfiguracji aplikacji, zachowaj jej reguły i przekaż uzgodniony zakres w briefie; zapisz, że przykładów nie zainstalowano. Same pliki pozostawione w repozytorium materiałów nie są automatycznie aktywne w osobnym klonie aplikacji.

To różne mechanizmy. Sprawdź klienta: VS Code, CLI i cloud agent nie mają identycznego interfejsu ani listy funkcji. Przykłady w materiałach są nieaktywne, dopóki ich świadomie nie przeniesiesz lub nie wywołasz. Polecenia promptów z IDE nie są automatycznie poleceniami CLI. Odczytaj obowiązujące instrukcje i sprawdź ich faktyczne zastosowanie.

## 2. Ćwiczenie dla test engineerów

Wybierz realną funkcję opisaną w PRD aplikacji. Jeśli nie ma jeszcze kodu, zacznij od uzgodnionego kontraktu i planu testów, bez udawania wykonania. Nie dokładaj kolejnego projektu do warsztatu.

Przekaż agentowi:

```text
Przeczytaj wskazane kryterium PRD, implementację i istniejące testy tej funkcji. Zaproponuj trzy obserwowalne przypadki: typowy, graniczny i błąd. Dla każdego podaj dane syntetyczne, oczekiwany wynik i warstwę testu. Nie zmieniaj kodu, dopóki nie wybiorę zakresu. Nie zakładaj narzędzia ani języka z przykładu kursowego.
```

Po wyborze jednego przypadku:

```text
Dodaj jeden test zachowania tylko w przypisanych plikach testów. Uruchom właściwe polecenie projektu i pokaż, że test wykrywa uzgodniony brak lub błąd. Nie zmieniaj produkcji, asercji ani danych tylko po to, by wynik był zielony. Jeśli test już przechodzi, zgłoś pokrycie zamiast wymyślać fazę Red. Dla charakterystyki działającego kodu najpierw zachowaj zielony punkt odniesienia. Podaj wynik, log i co pozostaje niesprawdzone.
```

Wykonawca implementacji pracuje po zaakceptowaniu testu. Następnie uruchom testy integracji i rzeczywisty przepływ aplikacji. Dla UI zapisz zrzut ekranu; dla CLI/API zachowaj wynik rzeczywistego polecenia lub zapytania. Oddziel wynik kompilacji, wykryte testy, pominięcia i start aplikacji.

Na końcu porównaj test z małą kontrolowaną zmianą zachowania w bezpiecznej gałęzi. Test powinien wykryć regresję; cofnij wyłącznie tę własną zmianę. Nie publikuj mutacji ani nie resetuj cudzej pracy.

## 3. Hook: dowód działania i granice

Najpierw przeczytaj istniejący przykład hooka i jego instrukcję instalacji. Testuj na JSON zawierającym wyłącznie fikcyjne ścieżki, bez czytania `.env`. Oba polecenia poniżej uruchom w terminalu otwartym w katalogu głównym repozytorium materiałów. W wariancie legacy lub mixed przejdź w tym terminalu do checkoutu materiałów; terminal Copilota pozostaje w repozytorium aplikacji.

```bash
printf '%s' '{"toolName":"view","toolArgs":{"path":".env.example"}}' | bash course-materials/hooks-example/block-secrets.sh
```

Oczekiwany kod wyjścia: 0. Dla fikcyjnej ścieżki `.env` oczekuj odmowy i kodu 2:

```bash
printf '%s' '{"toolName":"view","toolArgs":{"path":".env"}}' | bash course-materials/hooks-example/block-secrets.sh
```

Zgodność pojedynczego skryptu nie dowodzi, że klient go wczytał. Po świadomej konfiguracji powtórz próbę w swoim Copilot CLI. Sprawdź dokumentację payloadu i zdarzenia; nie wklejaj konfiguracji Claude jako pewnika. Prosty filtr nazw ma ograniczenia i nie zastępuje uprawnień systemu operacyjnego, piaskownicy ani ochrony sekretów. Nie testuj na realnym pliku z kluczem.

## 4. Copilot CLI i cloud agent

W CLI sprawdź wersję, dostępny model, uprawnienia katalogu i widok użycia. Zleć jedno zadanie z kryterium wyniku i limitem, nie całą aplikację. Raport wykonawcy porównaj z diffem i testami; zobacz też [przykład headless-task](../skills-examples/headless-task/SKILL.md).

W chmurze przećwicz przygotowanie jednego issue: kryterium PRD, zakres plików, dane syntetyczne, polecenia setup/test i oczekiwany wynik. Dopiero po zgodzie właściciela i sprawdzeniu polityki organizacji przypisz zadanie cloud agentowi. Agent pracuje w osobnym środowisku; lokalne pliki, logowanie i niezacommitowane zmiany nie pojawiają się tam automatycznie. Sprawdź log setupu, faktycznie wykonane testy oraz powstały diff/PR. Nie utożsamiaj zakończenia zadania z pozwoleniem na merge.

Bez dostępu do chmury wykonaj lokalny odpowiednik i zaznacz, czego nie sprawdzono; nie przedstawiaj symulacji jako wykonanego zadania cloud.

## 5. Premium requests, credits i wybór modelu

Przed ćwiczeniem sprawdź aktualny plan, politykę organizacji i ekran zużycia. Część planów używa starszego licznika premium requests i mnożników; inne rozliczają jednostki lub kredyty. Nie przeliczaj ich według historycznej tabeli bez potwierdzenia planu.

Jeśli masz dostęp do dwóch odpowiednich modeli i zgodę na ich użycie w dostępnym budżecie, porównaj jeden mały test na tańszym i mocniejszym modelu. Przy jednym dostępnym modelu wykonaj tylko ten przebieg i oceń jego wynik według tych samych kryteriów. Jeśli brak kredytów lub dostępu, przeanalizuj dostarczony, zanonimizowany raport z przykładu i zapisz, że drugiego przebiegu nie wykonano; nie porównuj go jako własnego pomiaru. Nie dokupuj kredytów ani nie zmieniaj providera bez zgody. Zachowaj ten sam brief i dane. Zapisz wybrany model, czas, użycie oraz czy test wykrył błąd. Najniższa cena nie pomaga, jeśli rośnie liczba poprawek. Sam wybór Auto nie gwarantuje najniższego kosztu. Własna definicja agenta może nadpisać model sesji, więc sprawdź efektywny wybór.

Kryterium ukończenia: jeden zweryfikowany test lub poprawka, pełny diff, jawne ograniczenia oraz decyzja osoby odpowiedzialnej. Liczba wygenerowanych testów i komunikat agenta nie wystarczają.

## Źródła

- [Instrukcje repozytorium](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions)
- [Konfiguracja własnych agentów](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
- [Hooki Copilot](https://docs.github.com/en/copilot/reference/hooks-reference)
- [CLI: polecenia i użycie](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
- [CLI: tryb programowy](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference)
- [Bieżące modele](https://docs.github.com/en/copilot/reference/ai-models/supported-models)
- [Rozliczanie Copilota](https://docs.github.com/en/copilot/concepts/billing)


## Pełne prompty do dalszej pracy

- [Test zachowania na podstawie kryterium akceptacji](../Prompt%20examples/copilot/P28-testy-copilot.md): rzeczywisty runner, obserwowane Red/Green i mapa kryterium do dowodu.
- [Diagnoza niestabilnego testu](../Prompt%20examples/copilot/P29-flaky-copilot.md): ograniczone powtórzenia i eksperyment rozróżniający przyczyny, bez ukrywania błędu przez sleep/retry.
- [Analiza SQL lub notebook](../Prompt%20examples/copilot/P30-notebook-copilot.md): dane syntetyczne, jawny mianownik i niezależna kontrola JOIN.
- [Własny skill planowania](../Prompt%20examples/copilot/P31-skill-planowania.md): źródłowy katalog, instalacja po przeglądzie, próba w nowej sesji i test niepotrzebnej aktywacji.

To osobne, opcjonalne ścieżki po głównym ćwiczeniu. Budżet każdej: 20-30 minut na jeden mały przypadek, z jawnym ograniczeniem zakresu. Nie próbuj wykonywać wszystkich w 60-minutowym budżecie głównego ćwiczenia. [Profil reviewer](../agent-configs/copilot/agents/reviewer.agent.md) pokazuje odczyt i ocenę dostarczonego diffu bez prawa edycji ani terminala; samo wybranie profilu nie dostarcza mu patcha.
