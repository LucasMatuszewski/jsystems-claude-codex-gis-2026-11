# Analiza legacy: dobór kontekstu i narzędzi

## Zacznij od zadania

| Potrzeba | Wybór | Dlaczego |
| --- | --- | --- |
| Znany plik, metoda lub błąd | `rg`, oryginalny kod, caller i test | Dokładne symbole i zachowanie bez pakowania całego repo. |
| Przegląd podsystemu, eksport do czatu | Repomix z `--include` / `--ignore` | Powtarzalny zakres, ścieżki i pomiar tokenów. |
| Orientacja w klasach i zależnościach | [Aider repo-map](https://aider.chat/docs/repomap.html), bez lokalnego testu jFTP | Mapa wskazuje ważne symbole i potrzebne pliki w budżecie kontekstu. |
| Wielokrotne pytania o framework / wiele repo | Trwały indeks kodu oraz sprawdzonych dokumentów | Pobieranie fragmentów do konkretnego zadania i odświeżanie zmian. |

Repomix to paczka, a nie automatycznie wiedza o działaniu aplikacji. Kompresja pomaga w orientacji; do zachowania, warunków, błędów i edycji czytaj pełną metodę. Nie usuwaj z wybranego zakresu testów, zasobów ani konfiguracji potrzebnych do pytania.

## Pomiar jFTP

Repomix 1.18.1, jFTP `14e62ceba4e371c2a0b955604b10f065f46f4f7d`, zakres `**/*.java,pom.xml`:

- Pełny zakres: 183 pliki, 221 241 tokenów.
- Ten sam zakres z kompresją: 138 187 tokenów, redukcja 37,54%.
- Wybrany `JFTPUtil.java` i POM: 2 pliki, 2 859 tokenów.

Liczby pochodzą z tokenizera Repomix, nie z każdego modelu. W skompresowanym `getTimeString` brakuje obliczeń i warunków. Zawężenie do dwóch plików mierzy wybór zakresu, nie skuteczność kompresji całego repo.

Do powtórzenia w osobnym klonie, po przygotowaniu Node.js 22+ i pnpm:

```bash
pnpm dlx repomix@1.18.1 --include '**/*.java,pom.xml' --style xml --output jftp-full.xml
```

```bash
pnpm dlx repomix@1.18.1 --include '**/*.java,pom.xml' --style xml --compress --output jftp-compressed.xml
```

Dwa pliki z ostatniego pomiaru:

```bash
pnpm dlx repomix@1.18.1 --include 'src/main/java/com/myjavaworld/jftp/JFTPUtil.java,pom.xml' --style xml --output jftp-utility-scope.xml
```

## Opinie i ograniczenia

W [dyskusji użytkowników](https://www.reddit.com/r/ChatGPTCoding/comments/1lzmicv/is_repomix_useful/) część osób nie widzi korzyści przy agencie, który już czyta pliki. Inni używają paczek wybranych obszarów do planowania w osobnym czacie. To doświadczenia użytkowników, bez wspólnego benchmarku.

[Wątek Claude Pro](https://www.reddit.com/r/ClaudeAI/comments/1l7s291/) opisuje eksport repo do czatu i przeniesienie planu do agenta. Przydaje się tam, gdzie czat nie ma dostępu do plików; nie dowodzi przewagi nad selektywnym czytaniem.

[Autor Yek](https://news.ycombinator.com/item?id=42755517) podał w styczniu 2025 bardzo duży mnożnik szybkości względem linkowanego forka Repomix. Nie używamy go jako aktualnego porównania oficjalnych wersji. [Yek](https://github.com/mohsen1/yek) jest alternatywnym eksporterem; limit tokenów może odrzucać pliki, więc trzeba sprawdzić zawartość paczki. [files-to-prompt](https://github.com/simonw/files-to-prompt) jest prostszym wyborem do eksportu wskazanych plików.

[Zgłoszenie #1815](https://github.com/yamadashy/repomix/issues/1815) opisuje błędne drzewa katalogów w split-output wersji 1.18.0. W małym lokalnym przykładzie split-output, osobnym od jFTP, w wersji 1.18.1 dwie paczki miały drzewa zgodne ze swoimi plikami; błędu nie odtworzyliśmy. Zgłoszenie starszej wersji nie wystarcza do odrzucenia obecnego narzędzia.

Opisy konkurencyjnych produktów i rankingi narzędzi służą jako tropy. Funkcje sprawdzamy w oficjalnej dokumentacji, przydatność na tym samym repo i pytaniach.

## Kod i dokumentacja w Context7

[Context7](https://context7.com/docs/adding-libraries) przyjmuje repozytoria jako źródła. Zwykle parsuje dokumentację; przy małej ilości dokumentacji może generować przykłady ze źródeł. Dla prywatnych repo generowanie dokumentacji z kodu jest opcjonalne. Nie zakładaj, że zwykłe dodanie repo zawsze indeksuje każdy plik Java.

Własny backend może indeksować bezpośrednio kod oraz sprawdzone karty API. [CLI](https://github.com/upstash/context7/blob/master/packages/cli/src/index.ts) pozwala wskazać go przez `--base-url`. Test lokalny z niezmienionym ctx7 0.5.13 obejmował 182 pliki Java, 701 fragmentów, pięć wybranych wcześniej zapytań o symbole i dwa o nieistniejące API. Indeksowaliśmy surowy kod, bez kart API. SQLite FTS5 znalazł oczekiwany plik w top 3 dla 4/5 zapytań; priorytet definicji, dobrany na tym samym zestawie, poprawił wynik do 5/5. Oba pytania o nieistniejące symbole nie zwróciły fragmentów; klient wyświetlił komunikat o braku wyników. Fragmenty zgadzały się z zapisanymi liniami oryginału. To test zgodności i symboli, nie semantycznego RAG ani dużego frameworka.

## Rozszerzenie: trwały indeks

[ken](https://github.com/townsendmerino/ken) ma lokalną hybrydę BM25 + embeddings i obsługę Javy. [Qdrant](https://github.com/qdrant/qdrant-client) daje tryb lokalny do eksperymentów i serwer do współdzielenia; [hybryda](https://qdrant.tech/documentation/concepts/hybrid-queries/) łączy rankingi gęste i rzadkie. [claude-context](https://github.com/zilliztech/claude-context) oferuje indeks kodu i MCP, z Milvus oraz wybranym modelem embeddings. Te warianty wymagają osobnego testu na naszych pytaniach.

SQLite FTS5 wystarcza na początek. `sqlite-vec` może dodać wektory, ale nadal trzeba zapewnić embeddings, łączenie rankingów i odświeżanie. Oficjalna dokumentacja [Chroma Search API](https://docs.trychroma.com/cloud/search-api/overview) obecnie opisuje zaawansowaną hybrydę jako funkcję cloud; nie zakładamy tego samego API lokalnie.

Porównaj co najmniej 20 zapisanych wcześniej pytań: symbole, zachowania, caller, granica framework/aplikacja, nieistniejące API i starsza wersja. Mierz znalezione źródła, poprawność cytowania, tokeny, czas indeksowania i odpowiedzi. Sprawdź zmianę oraz usunięcie pliku. Reranker dodaj dopiero, gdy poprawi wynik przy akceptowalnym czasie; licencję modelu sprawdzaj osobno od licencji silnika.

Stan źródeł i testów: 05.10.2026.
