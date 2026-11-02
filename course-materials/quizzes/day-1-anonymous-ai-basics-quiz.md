# Quiz na start przygody z AI

## Cel
- Szybka diagnoza poziomu startowego uczestników.
- Ustalenie, które obszary wymagają mocniejszego akcentu w dniach 1–2.
- Rozpoczęcie szkolenia w lekkiej, ale merytorycznej formule.

## Format
- Anonimowa ankieta lub quiz w Zoomie (alternatywnie Mentimeter/Kahoot).
- Łącznie 12 pytań.
- Sugerowany czas: 12–15 minut na quiz + 8–10 minut omówienia.

## Progi punktowe (dla trenera)
- 0–4 poprawne: poziom początkujący (warto zwolnić i mocniej osadzić fundamenty)
- 5–8 poprawnych: poziom mieszany (utrzymać główny tok, ale zostawić miejsce na doprecyzowanie podstaw)
- 9–12 poprawnych: poziom zaawansowany (można szybciej przejść do architektury, ryzyk i praktyki)

---

## Pytania (z odpowiedziami)

### P1. Czym jest token w kontekście modeli językowych?
A) Zawsze całym słowem zapisanym między spacjami
B) Podstawową jednostką tekstu przetwarzaną przez tokenizer modelu ✅
C) Tajnym kluczem potrzebnym do uruchomienia modelu
D) Nazwą limitu zapytań w API

### P2. Co oznacza pojęcie okna kontekstu?
A) Maksymalną liczbę znaków, które zmieszczą się w jednym promptcie
B) Zakres tekstu, który model może brać pod uwagę w pojedynczym wywołaniu ✅
C) Historię wszystkich rozmów użytkownika z danego tygodnia
D) Tryb, w którym model pamięta wszystko bez limitu

### P3. Co najlepiej opisuje autoregresyjny sposób działania LLM?
A) Model generuje całą odpowiedź naraz, a potem ją skraca
B) Model zawsze porównuje odpowiedź z bazą faktów przed wysłaniem
C) Model najpierw uruchamia testy regresji, a dopiero potem odpowiada
D) Model przewiduje kolejne tokeny na podstawie wcześniejszego kontekstu ✅

### P4. Czym jest halucynacja modelu?
A) Sytuacją, w której model generuje błędną informację w przekonującym stylu ✅
B) Każdą odpowiedzią, która jest zbyt kreatywna
C) Sytuacją, gdy model zdaje się mieć świadomość i wolną wolę
D) Przypadkiem, w którym model odmawia odpowiedzi

### P5. Które porównanie najlepiej oddaje różnicę między agentem, asystentem czatowym i autouzupełnianiem kodu?
A) To w praktyce trzy nazwy na to samo
B) Agent może planować i używać narzędzi; asystent głównie prowadzi rozmowę; autouzupełnianie podpowiada lokalną kontynuację ✅
C) Autouzupełnianie kodu jest zawsze bardziej autonomiczne niż agent, a najmniej autonomiczny jest czat
D) Asystent czatowy samodzielnie wdraża kod używając autouzupełniania, a agent tylko odpowiada na pytania i używa wyszukiwarki

### P6. Jaką rolę najczęściej pełni prompt systemowy?
A) Definiuje rolę modelu, zasady zachowania i ograniczenia odpowiedzi ✅
B) Służy do ustawienia języka interfejsu i ustawień systemu, czyli aplikacji w której działa agent
C) Jest kopią pierwszej wiadomości użytkownika
D) Ma znaczenie tylko w generatorach obrazów aby nadać predefiniowany styl

### P7. Co w praktyce oznacza spadek uwagi (attention) przy bardzo długim kontekście?
A) Model automatycznie kompresuje prompt bez utraty znaczenia
B) Bardzo długi prompt powoduje przegrzanie GPU i throttling
C) Im dłuższy kontekst, tym dłuższa odpowiedź bo model się rozgadał
D) Model może gorzej wykorzystywać lub gubić część informacji z fragmentów bardzo dużego tekstu ✅

### P8. Czego dotyczy AI Alignment?
A) Ustawienia wyrównania tekstu w interfejsie czatu
B) Dopasowania zachowania modelu do założonych zasad, intencji i wymagań bezpieczeństwa ✅
C) Synchronizacji modelu z kalendarzem użytkownika
D) Automatycznego porządkowania wiadomości wysłanych przez model

### P9. Jaka jest najlepsza pierwsza linia obrony przed niebezpiecznym SQL wygenerowanym przez AI?
A) Poprosić model, żeby pisał ostrożniej
B) Pozwolić uruchamiać tylko bardzo krótkie zapytania
C) Ograniczyć uprawnienia, stosować walidację i zabezpieczenia programistyczne przed wykonaniem zapytania ✅
D) Dodać do promptu zdanie „to środowisko produkcyjne, ostrożnie obchodź się z danymi”

### P10. Dlaczego sandboxing jest ważny w agentach programistycznych?
A) Bo ogranicza możliwe skutki błędu i pozwala bezpieczniej delegować działania ✅
B) Bo dzięki temu odpowiedzi modelu brzmią bardziej technicznie
C) Bo całkowicie eliminuje potrzebę przeglądu kodu przez człowieka
D) Bo uniemożliwia modelowi jakikolwiek dostęp do plików i narzędzi

### P11. Które stwierdzenie o WSL i izolacji jest najbardziej trafne?
A) WSL samo z siebie gwarantuje pełną izolację bezpieczeństwa
B) WSL daje agentom środowisko Linux, ale sam z siebie nie daje izolacji ✅
C) WSL działa wyłącznie dla projektów w Pythonie
D) WSL zostało wycofane i nie powinno być już używane

### P12. Co zwykle najbardziej poprawia efekty pracy z AI przy zadaniach technicznych?
A) Długi prompt, im więcej kontekstu tym lepiej
B) Dobre opisanie zadania, jasne ograniczenia, konkretne kryteria akceptacji i precyzyjnie dobrany kontekst ✅
C) Częste zmienianie narzędzia, żeby „odświeżyć” model
D) Trzymanie otwartych 27 kart, bo model lubi ambitne środowisko pracy

---

## Krótkie omówienie po quizie
- "To nie jest test na ocenę, tylko szybki radar pomagający dobrać tempo i poziom pracy."
- "Jeśli część pytań była nieoczywista, to dobrze — właśnie po to tu jesteśmy, żeby te rzeczy uporządkować i przećwiczyć."
- "Celem tego tygodnia jest nie tylko poznać narzędzia, ale umieć używać ich świadomie i bezpiecznie."

## Jak dostosować prowadzenie po quizie
- Jeśli dominują niskie wyniki: poświęć więcej czasu na okno kontekstu, halucynacje, role narzędzi i zabezpieczenia dla SQL.
- Jeśli wyniki są mieszane: utrzymaj planowany rytm, ale dodawaj krótkie podsumowania co 60–90 minut.
- Jeśli grupa wypada bardzo dobrze: skróć bloki teoretyczne i szybciej przejdź do architektury oraz ćwiczeń praktycznych.
