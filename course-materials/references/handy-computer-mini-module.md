# Handy.computer mini‑module (opcjonalny)

## Cel modułu
Pokazać uczestnikom **opcjonalny** workflow głosowy (STT + tłumaczenie) bez zmiany głównej ścieżki kursu (Claude Code-first, terminal-first). Moduł ma dodać ergonomię, nie zwiększyć chaos narzędzi.

## Kiedy pokazać
- **Opcjonalnie w bloku porównań narzędzi; krótkie demo głosowe.**
- Pokazujemy tylko jeśli:
  - grupa sygnalizuje zmęczenie pisaniem długich promptów,
  - pojawiają się pytania o pracę głosową/mobilną,
  - mamy stabilny komputer i działający mikrofon.
- Pomijamy bez szkody dla efektu kursu, jeśli czas jest napięty.

## Okno instalacyjne (jeśli demo na żywo)
- **5–8 min max** (nie dłużej):
  1. Krótkie pobranie/uruchomienie narzędzia.
  2. Test mikrofonu i języka.
  3. Jeden prompt transkrypcyjny + jeden prompt tłumaczeniowy.
- Jeśli instalacja przekracza 8 min → przechodzimy na plan B (zrzuty/przykładowy output), żeby nie rozwalić harmonogramu.

## Dwa prompty głosowe do pokazania

### Prompt 1 — transkrypcja notatki technicznej
`Przepisz to jako krótką notatkę techniczną po polsku: cel zadania, założenia, ryzyka, następny krok. Zachowaj format: 1) Cel 2) Założenia 3) Ryzyka 4) Next step.`

### Prompt 2 — tłumaczenie PL↔EN pod pracę zespołową
`Przetłumacz na angielski biznesowo-techniczny, zachowaj sens i skróty domenowe. Na końcu dodaj 3 krótkie alternatywne wersje bardziej: (a) formalna, (b) neutralna, (c) zwięzła do chatu.`

## Fallback gdy VM/laptop nie wyrabia
- Nie naprawiamy środowiska na forum całej grupy.
- Pokazujemy wcześniej przygotowany przykład wejście→wyjście (screen lub gotowy snippet).
- Uczestnik z problemem robi moduł po zajęciach z checklistą:
  1. mikrofon uprawnienia,
  2. język wejścia/wyjścia,
  3. test 30 sekund audio,
  4. eksport tekstu do promptu w Claude Code.
- Komunikat trenerski: „To dodatek ergonomiczny. Główny workflow kursu działa bez tego modułu.”

## Ryzyka i granice bezpieczeństwa
- Nie dyktujemy danych wrażliwych ani danych klienta.
- W przypadku środowisk regulowanych: tylko neutralne/przykładowe treści.
- Voice input ma wspierać przygotowanie promptu/notatki, a nie zastępować review decyzji technicznych.

## Zoom/chat paste (krótkie)
`Handy.computer to opcjonalny dodatek: szybciej zbiera notatki głosowe i tłumaczenia PL↔EN, ale core kursu zostaje Claude Code-first. Jeśli demo instalacji się przeciąga, pokazujemy gotowy przykład i wracamy do głównej ścieżki.`

## Mikro-checklista dla uczestnika
- Czy tracę czas na ręczne pisanie długich notatek/promptów?
- Czy potrzebuję szybkiego tłumaczenia PL↔EN do pracy zespołowej?
- Czy mój laptop/mikrofon działa stabilnie?
- Jeśli 2+ odpowiedzi to „tak” → warto przetestować moduł po zajęciach.
