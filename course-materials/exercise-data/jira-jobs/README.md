# Jira jobs: snapshot rzeczywistego API

Pracujesz z 34 zgłoszeniami utworzonymi w rzeczywistej Jira Cloud: 7 epiców zamówień, 25 tasków i 2 podzadania. Treść zamówień, role, obszary i ścieżki są syntetyczne. Statusy to 19 To Do, 11 In Progress i 4 Done. Zbiór zawiera 12 komentarzy i 8 relacji strukturalnych. Nie potrzebujesz dostępu do strony prowadzącego ani tokenu.

`tickets.json` zachowuje kopertę wyszukiwania `{"issues": [...]}` i komplet pól eksportu, w tym puste wartości, niestandardowe `customfield_*`, ID, statusy, relacje, rodziców, podzadania i znaczniki czasu. Nie dodano sztucznego `total`: źródłowy eksport nie zawierał paginacji. `issue-example.json` jest zbudowany ze zgłoszenia TEST-1 w tym samym eksporcie i pokazuje kształt GET issue: `expand`, `id`, `self`, `key`, `fields`. Dodatkowe `webUrl` pozostaje w wynikach wyszukiwania z konektora.

## Jak powstały pliki

Prowadzący utworzył zgłoszenia na podstawie `seed-spec.json`, wyeksportował pełne pola i komentarze przez konektor, a następnie uruchomił `sanitize_export.py`. Surowy eksport i mapowanie tożsamości pozostają poza repozytorium. To snapshot rzeczywistych odpowiedzi po anonimizacji i odtworzeniu reprezentacji REST v3, nie bajtowa kopia odpowiedzi HTTP.

Zastosowano: fikcyjny host `course-site.atlassian.net`, zerowy cloud ID, stabilne `accountId` w formacie `712020:course-user-1`, nazwę użytkownika `Analityk (kurs)`, nazwę projektu `Projekt kursowy` i ogólne awatary. Usunięto `emailAddress`, zastąpiono wystąpienia tożsamości także w adresach i tekście. `timeZone` zachowano. Ścieżki `self` pozostały bez zmian, zmieniły się host i identyfikatory użytkowników lub cloud ID.

`description` przekonwertowany do ADF tak jak zwraca REST v3. W dostarczonym eksporcie także wszystkie komentarze były Markdown, mimo oczekiwania ADF; ich `body` przekonwertowano tą samą metodą. Zachowano akapity, nagłówki, listy, bloki kodu z językiem, tabele, pogrubienia, kursywę i kod inline. Dosłowne sekwencje `\n` w opisach odtworzono jako podziały wierszy. Dodane przez konektor `\[` i `\]` w komentarzach odtworzono jako nawiasy. Gotowe węzły ADF nie są ponownie interpretowane. Alias autora w tekście komentarza oznacza rolę, a `author.displayName` jest kontem technicznym.

To celowo zagęszczona kolejka szkoleniowa. Prawdziwy kształt API nie potwierdza istnienia notebooków, storage ani wyników przetwarzania. `seed-spec.json` to lista definicji dla prowadzącego, nie odpowiedź REST. Nie używaj jej zamiast narzędzi w ćwiczeniu.

## Gdzie szukać parametrów

| Źródło | Pola API | Co z niego odczytasz |
|---|---|---|
| Zamówienie | `fields.issuetype`, `fields.summary`, `fields.description` | Epic, numer źródłowy, tabela lub opis parametrów |
| Taski pod epikiem | `fields.parent.key` w wynikach wyszukiwania | Kroki, SQL, historyczne komórki YAML, warunki odbioru |
| Podzadania | `fields.subtasks` oraz `fields.parent.key` | Zakres bbox i wyjaśnienie kolejności osi |
| Komentarze | `fields.comment.comments[].body`, `id`, `created` | Korekty parametrów, potwierdzenia i blokady |
| Linki | `fields.issuelinks[].type`, `inwardIssue`, `outwardIssue` | Zależności i podejrzenie duplikatu, z zachowaniem kierunku |
| Wyszukiwanie tekstowe | Tytuł, opis i komentarze całej kolejki | Zadania bez parenta lub linku, wskazane numerem zamówienia albo tytułem |

`subtasks` nie jest listą wszystkich tasków epika. Wyszukaj także `parent = TEST-1`, a następnie dzieci tasków. Powiązania tekstowe mogą prowadzić do zgłoszenia poza hierarchią. Dane biznesowe region/deadline/format są w treści, nie w specjalnie utworzonych polach Jira. Nie utożsamiaj autora technicznego ani statusu Jira z zamawiającym lub zgodą na wykonanie.

## Kontrakt wyniku v2

Zapisz jeden plik `reports/jira-jobs/jobs/<klucz-epika>.yaml` na każde zamówienie. Zachowaj także kandydata będącego możliwym duplikatem; nie usuwaj go i nie planuj drugiego runu bez rozstrzygnięcia. Taski i podzadania są dowodami, nie osobnymi jobami. Zgłoszenia dostępu i błędów UI bez zamówienia danych opisz jako `ignore_non_job` w `issues.md`, bez generowania konfiguracji.

Każdy YAML zawiera 13 pól: `job_id`, `region`, `area_name`, `bbox`, `layers`, `data_release`, `start_step`, `steps`, `output_format`, `output_path`, `deadline`, `requester_team`, `notes`, oraz obowiązkowe `unknown_reasons`. `job_id` to rzeczywisty klucz epika, np. `TEST-1`. `notes` to lista napisów. Release i deadline zapisuj w cudzysłowach, np. `'2026.11'` i `'2026-11-19'`. Schemat waliduje jeden obiekt YAML, nie listę wszystkich zgłoszeń.

Normalizuj wydanie do `YYYY.MM`, datę do `YYYY-MM-DD`, region do potwierdzonego ISO 3166-2, format i kroki do małych liter. Warstwy to lista: `roads`, `junctions`, `poi`, `speed_limits`, `addresses`. `steps` to kroki pozostałe od `start_step`, w kolejności wykonania. Nie dodawaj zakończonych etapów na podstawie liczby tasków. Bbox to `[west, south, east, north]` w EPSG:4326. Zamiana osi wymaga dowodu w źródle, nie tylko legalnych zakresów liczb.

Każde nieznane lub nierozstrzygnięte pole ma `null` i konkretny powód w `unknown_reasons`. Jawnie zamówiony cały region może mieć `bbox: null`; wtedy powód wyjaśnia brak dodatkowego wycinka, a nie brak informacji. Brak docelowej ścieżki blokuje wykonanie, chociaż szkic z `null` i powodem przechodzi schemat. HOLD, BLOCKED i warunki odbioru zachowaj w `notes` oraz `issues.md`. Poprawna walidacja nie jest zgodą na uruchomienie.

W `issues.md` podaj dla problemu klucz zamówienia i zgłoszenia dowodowego, pole, cytat, źródło (opis lub ID i data komentarza), wartość, pewność z uzasadnieniem i pytanie do człowieka. Rozróżnij: duplikaty, podobne odrębne zamówienia, konflikty, zatwierdzone nadpisania, braki, wartości historyczne i szum. Późniejszy komentarz zmienia parametry tylko tam, gdzie jawnie zatwierdzono zmianę. Nie przenoś korekty do innego epika automatycznie.

Sprawdź YAML względem `job-params.schema.json`, daty kalendarzowe, kolejność kroków i relacje bbox. Walidator kursowy uruchomisz z katalogu głównego repozytorium:

```powershell
uv run --with pyyaml --with jsonschema course-materials/exercises/jira-mcp/validate_jobs.py reports/jira-jobs/jobs
```

Oczekujesz 7 kandydatów zamówień. Każdy z 34 kluczy musi mieć wyjaśnioną rolę: zamówienie, dowód albo szum. Nie zmieniaj Jira i nie uruchamiaj Databricks ani pipeline GIS.

## Odtworzenie snapshotu przez prowadzącego

Surowy eksport trzymaj poza repozytorium, np. w `D:\trainer-private\jira-export.json`. Polecenie nadpisuje tylko dwa jawne pliki docelowe; nie zapisuje danych surowych ani mapowania użytkowników.

```powershell
python course-materials/exercises/jira-mcp/sanitize_export.py D:\trainer-private\jira-export.json course-materials/exercise-data/jira-jobs/tickets.json --example course-materials/exercise-data/jira-jobs/issue-example.json
```

`seed_jira.py` jest narzędziem legacy dla płaskiego formatu zgłoszeń. Nie obsługuje `seed-spec.json`, nie odtwarza epiców, parentów ani workflow v2. Nie używaj go do odtworzenia bieżącego zbioru. Użyj procedury seedowania v2 prowadzącego, potem wyeksportuj i zanonimizuj dane. Dokumentacja ADF: [format dokumentu Atlassiana](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/).
