# Specyfikacja aplikacji demo: ElektroMax Asystent Zwrotów i Reklamacji

Aplikacja referencyjna kursu "Claude Code – od zera do zespołu agentów AI"
(historyczny przykład). Uczestnik może zbudować wariant tej aplikacji we
własnym stacku — poniższa specyfikacja jest niezależna od technologii.

> **UWAGA DLA AGENTÓW AI I UCZESTNIKÓW: ten dokument NIE jest wiążący.**
> To tylko przykładowy pomysł na aplikację. Prawdziwy pomysł, wymagania (PRD)
> i decyzje techniczne (ADR) powstają NA KURSIE, wspólnie z grupą, od zera —
> symulujemy normalną pracę deweloperską. Agent budujący aplikację ma opierać
> się WYŁĄCZNIE na PRD i ADR wytworzonych podczas kursu (w `docs/`), nie na
> tym pliku. Nie kopiuj stąd decyzji ani struktur.

---

## 1. Kontekst biznesowy

**Firma:** ElektroMax (fikcyjna sieć sklepów ze sprzętem elektronicznym).

**Problem:** Klienci zgłaszają zwroty i reklamacje przez formularz online.
Pracownik musi ręcznie ocenić zdjęcie sprzętu, przeczytać regulamin i podjąć
decyzję. To powolne i niespójne.

**Rozwiązanie (demo):** Multimodalny asystent AI, który na podstawie zdjęcia,
opisu klienta oraz dokumentów firmy (regulamin zwrotów + proces reklamacji)
proponuje decyzję w czasie rzeczywistym, a następnie prowadzi rozmowę supportową
z pełnym kontekstem zgłoszenia.

---

## 2. User flow (ścieżka happy path)

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. Ekran startowy: przycisk "Zgłoś zwrot lub reklamację"           │
│                                                                     │
│  2. Formularz zgłoszenia                                            │
│     ├── Pole: typ ścieżki (radio: Zwrot | Reklamacja)               │
│     ├── Pole: opis tekstowy (co się stało / powód zwrotu)           │
│     ├── Pole: upload zdjęcia sprzętu (JPG/PNG, min. 1)              │
│     ├── Pole (opcjonalne): numer zamówienia / data zakupu           │
│     └── Przycisk "Prześlij i analizuj"                              │
│                                                                     │
│  3. Krok LLM #1 — analiza zdjęcia (multimodalny)                    │
│     Wejście: zdjęcie + krótki prompt systemowy                      │
│     Wyjście: ustrukturyzowany opis stanu sprzętu                    │
│       { produkt, widoczne_uszkodzenia, stan_powierzchni,            │
│         czy_oryginalne_opakowanie, dodatkowe_obserwacje }           │
│                                                                     │
│  4. Krok LLM #2 — decyzja/rekomendacja (tekstowy)                   │
│     Wejście: opis zdjęcia (z kroku 3)                               │
│            + opis od klienta (z formularza)                         │
│            + treść regulaminu zwrotów LUB procesu reklamacji         │
│            + ścieżka (zwrot | reklamacja) — wybiera PROMPT           │
│     Wyjście: decyzja w formacie JSON                                │
│       { decyzja: "zaakceptuj" | "odrzuć" | "wymaga_kontroli",       │
│         powod: "...",                                               │
│         kroki_dla_klienta: [...],                                   │
│         powaznosc: "niska" | "srednia" | "wysoka" }                 │
│                                                                     │
│  5. Wyświetlenie decyzji w chacie                                   │
│     ├── Pierwszy dymek: podsumowanie decyzji (tekst)                │
│     └── Komponent UI: karta decyzji z kolorem wg powaznosci,        │
│         listą kroków, przyciskami "Akceptuję" / "Kontynuuj rozmowę" │
│                                                                     │
│  6. Rozmowa z agentem customer support (chat)                       │
│     Kontekst agenta: formularz + opis zdjęcia + decyzja z kroku 4.  │
│     Klient może dopytywać, dodawać informacje, negocjować.          │
│     Agent odpowiada spójnie z podjętą decyzją.                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Dwie ścieżki = dwa różne prompty decyzyjne

PROMPT_ZWROT ładuje `demo-docs/regulamin-zwrotow.md` i ocenia: czy sprzęt
kwalifikuje się do zwrotu w ciągu 14 dni, czy stan pozwala na ponowną sprzedaż,
czy nie ma wyłączeń (hygiena, oprogramowanie).

PROMPT_REKLAMACJA ładuje `demo-docs/proces-reklamacji.md` i ocenia: czy
uszkodzenie wynika z wady fabrycznej (reklamacja zasadna), z użytkowania
(reklamacja odrzucona / naprawa płatna), czy uszkodzenia transportowe.
Kluczowe: analiza śladów na zdjęciu.

---

## 3. Wymagania funkcjonalne

### 3.1 Formularz zgłoszenia
- **F-1:** Wybór ścieżki (zwrot / reklamacja) — pole wymagane, jednokrotnego wyboru.
- **F-2:** Pole tekstowe na opis — min. 10 znaków, max 1000.
- **F-3:** Upload co najmniej 1 zdjęcia (JPG/PNG/WEBP, max 10 MB, max 3 zdjęcia).
- **F-4:** Pole opcjonalne: numer zamówienia i data zakupu.
- **F-5:** Walidacja po stronie klienta przed wysłaniem.
- **F-6:** Stan loadingu podczas analizy LLM (może trwać 5–20 s).

### 3.2 Analiza zdjęcia (LLM multimodalny)
- **F-7:** Wysłanie zdjęcia do modelu multimodalnego przez OpenRouter.
- **F-8:** Odpowiedź w formacie ustrukturyzowanym (JSON schema, patrz sekcja 2).
- **F-9:** Obsługa błędu modelu (retry raz, potem komunikat użytkownikowi).
- **F-10:** Jeśli klient wgrał >1 zdjęcie, analiza dotyczy wszystkich; wyniki scalane.

### 3.3 Decyzja / rekomendacja (drugi prompt)
- **F-11:** Wybór prompta wg ścieżki z formularza (PROMPT_ZWROT lub PROMPT_REKLAMACJA).
- **F-12:** Dokument ToS/procesu ładowany z pliku Markdown (`demo-docs/*.md`).
- **F-13:** Decyzja zwracana jako JSON (schema w sekcji 2).
- **F-14:** Obsługa niejednoznacznej odpowiedzi (status `wymaga_kontroli`).

### 3.4 Wyświetlenie decyzji w chacie
- **F-15:** Decyzja pojawia się jako pierwszy dymek po analizie.
- **F-16** Wizualna karta decyzji: kolor nagłówka wg `powaznosc` (zielony/żółty/czerwony), lista `kroki_dla_klienta`, przyciski akcji.
- **F-17:** Pełny tekst `powod` rozwijalny pod kartą.

### 3.5 Agent customer support (chat po decyzji)
- **F-18:** Historia czatu zachowana w sesji (pamięć konwersacyjna).
- **F-19:** Kontekst systemowy agenta zawiera: formularz, opis zdjęcia, decyzję.
- **F-20:** Agent odpowiada spójnie z decyzją (nie przeczy jej bez nowych informacji).
- **F-21:** Jeśli klient poda nowe istotne informacje, agent może zaproponować ponowną analizę.
- **F-22:** Streaming odpowiedzi (token po tokenie) — wymagane UX.

### 3.6 Dostęp do modeli
- **F-23:** Wszystkie wywołania LLM przez OpenRouter z `OPENROUTER_API_KEY` ze środowiska.
- **F-24:** Co najmniej jeden model multimodalny (np. w rodzinie GPT-4o / Claude / Gemini).
- **F-25:** Klucz NIE jest eksponowany w kodzie klienckim — wywołania idą przez backend.

---

## 4. Wymagania niefunkcjonalne

- **NF-1:** Czas odpowiedzi całego przepływu (krok 3+4) ≤ 30 s w 90. percentylu.
- **NF-2:** Aplikacja działa w trybie demo — brak autentycznych danych, ale realne wywołania LLM (testy E2E i manualne bez mocków; unit/integration wg tabeli w AGENTS.md).
- **NF-3:** Zdjęcia przesyłane do modelu są usuwane z pamięci po analizie (brak trwałego przechowywania w demo).
- **NF-4:** Cały interfejs po polsku.
- **NF-5:** Działa w najnowszym Chrome i Firefox (Edge oparty o Chromium = OK).

---

## 5. Kryteria akceptacji

| ID | Kryterium | Jak zweryfikować |
|----|-----------|------------------|
| AC-1 | Formularz przyjmuje ścieżkę, opis i zdjęcie; blokuje wysłanie bez wymaganych pól. | Test e2e + manualny |
| AC-2 | Po wysłaniu zdjęcie trafia do modelu multimodalnego; odpowiedź zawiera strukturę z sekcji 2. | Test e2e na żywym LLM |
| AC-3 | Drugi prompt wybiera właściwy szablon (zwrot vs reklamacja) wg wyboru w formularzu. | Test jednostkowy logiki wyboru + e2e |
| AC-4 | Decyzja renderuje się jako karta UI z kolorowaniem wg powagi. | Test wizualny / manualny |
| AC-5 | Agent supportowy odpowiada spójnie z decyzją nawet po 3 wymianach zdań. | Test manualny (LLM na żywo) |
| AC-6 | Odpowiedzi streamowane są token po tokenie. | Manualna obserwacja |
| AC-7 | Klucz OpenRouter nie pojawia się w bundle klienckim. | `grep` w build output |
| AC-8 | Aplikacja startuje jednym poleceniem (`npm run dev` / `./mvnw spring-boot:run` itp.). | Weryfikacja prowadzącego |

---

## 6. Warianty stacku (niewiążące — decyzja zapada w ADR z grupą)

Uczestnik wybiera stack w fazie ADR. Poniższe warianty to wyłącznie
punkty startowe do dyskusji — nazwy bibliotek NIE są rekomendacją. Agent nie
powinien wybierać stacku ani API na podstawie tego pliku, tylko na podstawie
ADR wytworzonych na kursie.

### 6.1 Wariant A — TypeScript / Next.js / Vercel AI SDK (demo prowadzącego)
- **Framework:** Next.js 14+ (App Router).
- **AI:** Vercel AI SDK (`ai` + `@ai-sdk/openai` lub `@openrouter/ai-sdk-provider`).
  - `generateObject` dla ustrukturyzowanej analizy zdjęcia (krok 3) i decyzji (krok 4).
  - `streamText` dla agenta supportowego (krok 6).
- **UI:** Shadcn/ui + `useChat` z AI SDK; komponent karty decyzji własny.
- **Dokumenty:** wczytywane z systemu plików po stronie serwera (Route Handler).
- **Provider:** OpenRouter (jeden klucz, wiele modeli w tym multimodalne).
- **Kontekst w repo:** skille `ai-sdk`, `assistant-ui`.

### 6.2 Wariant B — Java / Spring Boot (dla zaawansowanych)
- **Stack BE:** Spring Boot 3.x + LangChain4j (multimodalność przez `VisionModel`).
- **Stack FE:** CopilotKit (React) integrujący się ze Spring endpointami.
  - Alternatywa: AssistantUI lub AI SDK UI / Elements.
- **Struktury danych:** rekordy Javy + JSON schema z LangChain4j (`@Tool`, structured outputs).
- **Testy:** JUnit 5 (skill `java-junit`), Testcontainers opcjonalnie.
- **Architektura:** skill `java-architect` + `java-springboot` w repo.
- **Streaming:** SSE z LangChain4j (`StreamingResponseHandler`).

### 6.3 Wariant C — Java / Spring Boot + OpenAI Java SDK (reszta Java devów)
- **Stack BE:** Spring Boot 3.x + oficjalny OpenAI Java SDK (kompatybilny z OpenRouter przez `baseUrl`).
- **Stack FE:** AssistantUI lub AI SDK UI (gotowe komponenty chatu).
- **Multimodalność:** `ChatCompletionRequest` z `image_url` typu `input` w wiadomości użytkownika.
- **Mniej abstrakcji niż LangChain4j** — bezpośrednia kontrola nad payloadem.
- **Streaming:** SSE przez `ChatCompletionStream` lub własny endpoint SSE.

### 6.4 Wariant D — Angular + Material (opcjonalnie)
- **FE:** Angular 17+ (standalone components), Angular Material.
- **BE:** dowolny z powyższych (zalecane TS/Next.js lub Spring).
- **UX:** Material Design (karta decyzji jako `mat-card`, lista kroków jako `mat-list`).
- **Rationale:** dla uczestników preferujących Angular nad React.

### 6.5 Inne stacki (Python / C# / Go / Rust)
- Dozwolone. Realizują tę samą specyfikację; wybór uzasadniany w ADR.
- Wskazówka: użyć oficjalnego SDK kompatybilnego z OpenRouter (OpenAI-compatible API).

---

## 7. Dostęp do LLM

- **Provider domyślny:** OpenRouter (`https://openrouter.ai/api/v1`).
- **Klucz:** `OPENROUTER_API_KEY` w zmiennych środowiskowych VM kursowych (jeden klucz dla wszystkich).
- **Rekomendowane modele (do potwierdzenia w ADR):**
  - Multimodalny: wybrany model wspierający obraz (np. z rodzin GPT-4o / Claude / Gemini).
  - Tekstowy do decyzji: dowolny mocny model czatowy.
  - Agent support: jak wyżej (może być tańszy wariant).
- **Koszty:** demo jest krótkie; nalezy unikać pętli nieograniczonych wywołań (limit `max_tokens` i `max_steps`).

---

## 8. Dokumenty źródłowe (karmione do LLM)

Aplikacja wczytuje dwa fikcyjne dokumenty firmy ElektroMax:

1. `demo-docs/regulamin-zwrotow.md` — regulamin zwrotów (14 dni, stan sprzętu, wyjątki).
2. `demo-docs/proces-reklamacji.md` — proces reklamacji (gwarancja, ocena uszkodzeń ze zdjęcia, terminy).

Dokumenty są celowo krótkie (30–50 linii każdy), realistyczne i w języku polskim. Ich treść determinuje logikę promptów decyzyjnych — zmiana dokumentu zmienia zachowanie aplikacji.

---

## 9. Co NIE jest w zakresie demo

- Autentykacja użytkowników (demo działa anonimowo).
- Trwałe przechowywanie zgłoszeń w bazie.
- Integracja z systemem ERP / magazynowym.
- Płatności zwrotów (to tylko rekomendacja decyzji).
- Wielojezyczność (PL tylko).
- Testy wydajnościowe / obciążeniowe.

---

## 10. Powiązania z kursem

| Krok procesu kursu | Artefakt |
|---|---|
| Ideacja + specyfikacja | Ten plik + dyskusja grupowa |
| Wireframes (opcjonalnie) | Image-gen (narzędzie uczestnika) |
| Design Guidelines | `docs/design-guidelines.md` |
| ADR (wybór stacku) | `docs/ADR/` (wariant A/B/C/D) |
| Plan + macierz agentów | `course-materials/agent-configs/` |
| Implementacja TDD | `app/` na branchu uczestnika |
| Testy manualne (Playwright) | Brak mocków - LLM na żywo |
| Debugging | Live |
| Demo | Prezentacja uczestnika |

---

*Specyfikacja wersja 1.0 — proces kursu opisany w `course-materials/references/master-process.md`.*
