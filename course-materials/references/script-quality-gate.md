# Script Quality Gate (for cron agent)

Use this checklist before marking the private trainer timetable as DONE. Keep `COURSE AGENDA - <course> <group>.md` beside the course notes in the trainer's Obsidian vault, never in participant materials, repositories, slides or chats. Public materials contain scope and ordered presentations only.

## 1) Spójność i ciągłość (day-by-day)
- Czy dzień N logicznie wynika z dnia N-1?
- Czy uniknięto powtarzania tych samych treści bez nowej wartości?
- Czy na końcu dnia jest jasne przejście do kolejnego dnia?

## 2) Pokrycie wymagań
- Czy blok ma: co mówię (szczegółowy scenariusz, nie tylko listę punktów) / co pokazuję / co wklejam na chat (konkretne linki, prompty, ćwiczenia, nie tylko brief concept) / ćwiczenie (link do konkretnego pliku md z ćwiczeniem - 1 plik na exercise) / feedback / czas?
- Czy są sekcje: "Czego się nauczymy" i "Dlaczego warto"?
- Czy narracja jest po polsku, z wyjaśnieniem angielskich terminów?
- WAŻNE: to ma być skrypt jak scenariusz, co ja mam powiedzieć realnie, a nie lista punktów i pomysłów! W skrypcie potrzebuję od razu mieć co mam wkleić na chat, jakie ćwiczenie, jaki prompt, ja nie będę miał czasu chodzić po plikach i szperać, wszystko ma być w prywatnym pliku COURSE AGENDA, w osobnych sekcjach dla poszczególnych dni!

## 3) Czas i wykonalność
- Czy harmonogram mieści się w uzgodnionych godzinach kursu z przerwami?
- Czy estymacje bloków sumują się realistycznie i są wykonalne?
- Czy przy każdej przerwie zapisano checkpoint tempa: planowany i faktyczny stan oraz następny krok lub wariant skrócony?
- Czy każdy blok ma dzień, godziny, deck i dokładny slajd, a godziny przerw w materiałach uczestnika występują tylko w Start kursu?
- Czy ćwiczenia są wykonalne na VM i limicie czasowym?

## 4) Zoom/chat usability
- Czy każdy prompt/ćwiczenie ma osobny plik do szybkiego wysłania na czacie?
- Czy dzienny skrypt ma ścieżki do tych plików?
- Czy teksty chat-paste są krótkie (zoom-friendly)?

## 5) Narzędzia i zgodność z założeniami
- Czy zachowany jest Claude Code-first, z Codex tylko jako krótką notą pozycjonującą?
- Czy porównania Claude/IntelliJ są krótkie i rzeczowe?
- Czy uniknięto tool sprawl (OpenCode/Goose/Cursor/Zed jako core)?
- WAŻNE: czy jest zgodne z uzgodnionym zakresem szkolenia i listą prezentacji na stronie materiałów?

## 6) Cloud vs on-prem realizm
- Czy pokazano "max możliwości" (cloud) + "jak to adaptować on-prem"?
- Czy przykłady CI/CD i integracji są oparte o research i źródła?
- Czy pokazujemy jak używać modeli alternatywnych (np. Ollama, OpenRouter) głównie w Claude Code (CLI i Desktop), a Codex/IntelliJ tylko jako krótkie porównanie? (aby potrafili potem się przenieść na modele on-prem)

## 7) Styl i ton
- Czy to co mówię i ćwiczenia są angażujące, ciekawe, zachęcające i motywujące? (to ma być przygoda, nie nudne suche szkolenie)
- Czy styl jest profesjonalny i klient-facing?
- Czy humor jest subtelny, nerdowy, bez przesady?
- Czy jest pozytywna, motywująca narracja (bez języka oceniającego braki)?

## Decision rule
- Jeśli 2 lub więcej punktów jest "NIE" -> nie oznaczaj TODO jako DONE.
- Najpierw popraw, potem dopiero commit.
