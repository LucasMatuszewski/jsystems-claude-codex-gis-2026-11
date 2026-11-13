# Sprawdź się: Jira, konfiguracje i powiązania

**Uwaga, spoilery. Otwórz ten plik dopiero po zapisaniu własnych wyników J1-J3. Nie udostępniaj go agentowi podczas pierwszej próby.**

Porównuj swoje dowody i decyzje, nie identyczne brzmienie raportu. Odpowiedzi dotyczą lokalnego snapshotu: witryna `course-site.atlassian.net`, GitHub `course-org/map-data-jobs-sim`, Bitbucket `course-workspace/map-data-jobs-pipelines` oraz obce repozytorium `course-workspace/ai-php-course-08-2026`. Adresy w snapshocie nie są zaproszeniem do logowania. Niczego nie zmieniaj w usługach i nie uruchamiaj jobów.

## 1. Czy objąłeś cały zbiór?

Odkrycie powinno objąć 40 zgłoszeń TEST-1..TEST-40, 5 stron Confluence, 10 PR-ów GitHub i 10 PR-ów Bitbucket. W limicie J3 możesz przeczytać szczegółowo tylko wybrane przypadki, jeśli jawnie zapiszesz luki pokrycia. Nie przedstawiaj discovery jako pełnego przeglądu treści.

Oczekujesz **9 szkiców konfiguracji**: TEST-1..TEST-7 oraz samodzielne nowe zamówienia TEST-38 i TEST-39. Nie twórz YAML na każdy task, błąd lub komentarz. `job_id` jest kluczem zgłoszenia, nie numerem biznesowym SL-461. Każdy plik ma 13 pól konfiguracji i `unknown_reasons`; `notes` jest listą napisów. Każde `null` wymaga konkretnego powodu. Jawny zakres całego regionu również uzasadnij w `unknown_reasons.bbox`.

## 2. Oczekiwane parametry zamówień

We wszystkich dziewięciu szkicach potwierdzone miesięczne wydanie to `2026.11`. Bbox zapisuj jako `[min_lon, min_lat, max_lon, max_lat]` w EPSG:4326. Same poprawne zakresy liczb nie wykrywają zamienionych osi. Kolejność warstw nie ma znaczenia, kolejność `steps` ma znaczenie. Data w tabeli oznacza `deadline` konfiguracji, nie automatycznie kalendarz wydania ani godzinę notebooka.

| job_id i zamówienie | Region / area_name / bbox | Warstwy | start_step i steps | Format / output_path / deadline / requester_team |
| --- | --- | --- | --- | --- |
| TEST-1, SL-461 | PL-14 / Nowa Wieś / `[20.780, 52.100, 20.835, 52.135]` | roads, speed_limits | validation / validation, export, publish | parquet / `dbfs:/map-jobs/sl-461/final/` / 2026-11-19 / Map Requests |
| TEST-2, OSM-460 | PL-12 / Kraków / `[19.8, 49.95, 20.2, 50.15]` | roads, junctions | ingest / ingest, validation, export | delta / `dbfs:/map-jobs/osm-460/2026-11/` / 2026-11-16 / Data Ops |
| TEST-3, MIG-463 | PL-22 / Gdańsk / `null`, cały region | roads | ingest / ingest, conflation, validation, export | parquet / `null`, brak zatwierdzonego celu / 2026-11-20 / Data Engineering |
| TEST-4, GEO-464 | DE-BY / München / `[11.45, 48.05, 11.75, 48.25]` | roads, junctions | conflation / conflation, validation, export | geojson / `dbfs:/map-jobs/geo-464/review/` / 2026-11-18 / Geometry QA |
| TEST-5, DASH-465 | DE-BE / Berlin / `null`, cały region | roads, addresses | validation / validation, export, publish | delta / `dbfs:/map-jobs/dash-465/2026-11/` / 2026-11-14 / Operations Analytics |
| TEST-6, POI-462 | PL-30 / Nowa Wieś / `[16.8, 52.3, 16.86, 52.34]` | poi, addresses | ingest / ingest, validation, export | geojson / `dbfs:/map-jobs/poi-462/delivery/` / 2026-11-17 / Local Search |
| TEST-7, drugi SL-461 | PL-14 / Nowa Wieś / `[20.780, 52.100, 20.835, 52.135]` | roads, speed_limits | validation / validation, export, publish | geojson / `dbfs:/map-jobs/sl-461/preview/` / 2026-11-18 / Map Requests |
| TEST-38, OSM-466 | PL-12 / Kraków / `null`, zakres do potwierdzenia | roads, junctions | ingest / `null`, dalsze kroki do ustalenia | parquet / `dbfs:/map-jobs/osm-466/2026-11/` / 2026-11-23 / Data Ops |
| TEST-39, numer zamówienia niepotwierdzony | PL-22 / Gdynia / `null`, niewiarygodny zapis osi | roads, poi | `null` / `null`, brak uzgodnionych etapów | parquet / `null`, brak zatwierdzonego celu / 2026-11-30 / Local Search |

TEST-1 ma komplet parametrów, ale wymaga ostrzeżenia o możliwym drugim zamówieniu TEST-7. TEST-7 pozostaje **HOLD**: zachowaj lokalny wariant formularza, nie przepisuj do niego automatycznie nowszych parametrów TEST-1 i nie planuj drugiej dostawy. TEST-3 jest **BLOCKED**, TEST-38 jest **HOLD**, TEST-39 jest **BLOCKED**. `null` jest uczciwym szkicem do oceny, nigdy pozwoleniem na uruchomienie bez wymaganej wartości.

## 3. Czy znalazłeś zasiane problemy?

| Zgłoszenia | Oczekiwane ustalenie i dowód |
| --- | --- |
| TEST-1, TEST-8..10, TEST-33 | `regoin`, `speed limts`, `PL-MZ` i `26.11` wymagają normalizacji na podstawie treści i komentarzy. Komentarz 2 zmienia start z conflation na validation. Komentarz 3 zastępuje geojson/preview/18.11 przez parquet/final/19.11. TEST-9 ma starą kopię YAML. Bbox jest w podzadaniu TEST-33, z korektą osi w komentarzu. |
| TEST-29 | Dowód dla SL-461 znaleziony po tekście, bez parenta i linku. Zasłonięty znak na drodze serwisowej wymaga analityka; zapisz to w notes. Nie zmieniaj limitu automatycznie; eksport poprawnych rekordów jest dopuszczony treścią. |
| TEST-2, TEST-11..13 | Tygodniowy snapshot 2026-11-09 i wk46 nie zmieniają miesięcznego wydania. Done przy ingest nie zmienia start_step. Tylko delta, bez dodatkowego GeoJSON i publish; ponowienie ma zastępować partycję, a nie dopisywać duplikaty. |
| TEST-3, TEST-14..16, TEST-30 | SQL TEST-15 potwierdza PL-22, 2026.11 i `is_deleted=false`; zachowaj road_id i predykat w notes. Gdańsk jest etykietą całego regionu, więc bbox=null jest poprawne. TEST-16 wymaga osobno validation i export. TEST-30 znaleziony tylko po tekście potwierdza brak output_path i zakaz scratch; nie zgaduj abfss://. |
| TEST-4, TEST-17..19 | Skoryguj kolejność osi zgodnie z komentarzem. Scalaj tylko skrzyżowania na tym samym poziomie. Podejrzane highway=motorway wymagają review, a nie automatycznej zmiany tagów. Wynikiem jest paczka review, bez publish. |
| TEST-5, TEST-20..22 | Tytuł o dashboardzie dotyczy rzeczywistej materializacji danych. Komentarz TEST-20 zastępuje stare SQL 2026.10 przez 2026.11. Godziny notebooka i kontroli dashboardu nie są deadline. Start validation na zaakceptowanych danych, nie ingest w celu naprawy UI. |
| TEST-6, TEST-23..25, TEST-34 | `adresses` to addresses, wydanie potwierdza komentarz. Jedyny bbox jest w podzadaniu TEST-34. Nowa Wieś PL-30 to inne zamówienie niż PL-14; nie kopiuj roads/speed_limits i nie łącz dostaw. |
| TEST-7, TEST-26..28 | Podejrzenie Duplicate nie jest zgodą na anulowanie ani drugi run. Stare geojson/preview/18.11 pozostają wariantem do decyzji. Status To Do nie unieważnia HOLD z treści. |
| TEST-31, TEST-32 | VPN i legenda UI bez potrzeby odświeżenia danych to `ignore_non_job`. Nie raportuj ich jako jobów z brakującymi 13 polami. |
| TEST-35 | Błąd runu 48211907: `junctons` zamiast `junctions` w parametrach eksportu OSM, nie awaria klastra. Powiąż z TEST-2 i Runbookiem; nie twórz nowego joba. |
| TEST-36 | Run 48213344: ExecutorLostFailure / spot preempted, parametry DASH-465 są poprawne. Zalecenie restartu od validation, bez wykonywania restartu. |
| TEST-37 | roads PL-14: 18 452 -> 10 931, około -41%. Wskaż run 48205871 i możliwy podwójny SL-461; to analiza anomalii, nie nowe zamówienie. |
| TEST-38 | Nowe OSM-466 zmienia format na parquet i output, nie nadpisuje OSM-460. `2026-11-W46` normalizujesz do 2026.11; bbox z TEST-2 jest dopiero propozycją w notes. Potwierdź osobną dostawę, zakres i dalsze kroki. |
| TEST-39 | Wklejona syntetyczna wiadomość nie potwierdza bbox, output ani planu kroków. POI-470 występuje przy katalogu i nie dowodzi numeru zamówienia. "Do końca miesiąca" oznacza 30.11.2026. Nie dopisuj addresses ani scratch; analogia do MIG-463 nie ustala etapów. |
| TEST-40 | Tekst "patrz TEST-12" odnajduje relację mimo braku linku Jira. Pusty chunk 11 sam nie dowodzi błędu ani potrzeby zmiany bbox. |

Priorytet, status i duedate są dodatkowymi dowodami. Porównaj je z opisem, komentarzami i kalendarzem; nie stosuj zasady "ostatnia data znaleziona w dowolnym miejscu wygrywa".

## 4. GitHub: oczekiwane decyzje o linkach

W tej tabeli wszystkie PR-y należą do `course-org/map-data-jobs-sim`. `link` oznacza propozycję w raporcie, bez zapisu do Jira. Dla niezależnych wzmianek i kilku celów twórz osobne wiersze, a w `source_id` podawaj usługę, repozytorium i lokalizację dowodu.

| PR | Dowód i kandydaci | Decyzja |
| --- | --- | --- |
| #1 | TEST-8 w tytule, review dodaje TEST-29 | `high/link` po odczycie obu zgłoszeń; TEST-29 jest dowodem terenowym, nie drugim jobem. |
| #2 | TEST-9 wyłącznie w opisie, "Closes" | `high/link`; fraza nie zamyka Jira bez integracji. |
| #3 | test-12 tylko w nazwie gałęzi | Normalizacja do istniejącego TEST-12, `high/link` po potwierdzeniu zakresu. |
| #4 | TEST-18 tylko w komunikacie commita | `high/link`; sam tytuł i opis nie wystarczą do odkrycia dowodu. |
| #5 | test-15, TEST 15, TSET-15; SQL i review | Dwa pierwsze warianty mogą dać `high/link` do TEST-15. Literówka TSET-15 wymaga osobnego `flag_for_human`, nawet gdy kandydat jest trafny. |
| #6 | SL-461 bez jednoznacznego klucza; TEST-1, TEST-10, TEST-7 | `flag_for_human`; numer biznesowy nie rozstrzyga między głównym zamówieniem, publikacją i duplikatem. |
| #7 | TEST-99 | Nie istnieje: `flag_for_human`, puste jira_key. Zachowaj TEST-99 w mention_text, nie twórz zgłoszenia. |
| #8 | MAPJOB-117, kandydat TEST-16 | `flag_for_human`; brak potwierdzonej mapy migracji prefiksu. |
| #9 | Bez klucza, Nowa Wieś PL-30, poi/addresses, bbox i 2026.11; TEST-24/TEST-6 | `flag_for_human`, ponieważ to dopasowanie tylko po treści. Wyklucz TEST-1/TEST-7 z PL-14. |
| #10 | TEST-1 i TEST-7, diff `jobs/sl-461.yaml` z 2026.10 | Klucze mogą mieć high confidence, ale action=`flag_for_human`. Zamówienia wymagają 2026.11; wstrzymaj akceptację i zachowaj HOLD dla drugiego formularza. |

Czy przeczytałeś komentarze inline, commity, gałęzie i pliki PR? Komentarz bota o limicie review to `ignore`, nie dowód błędu aplikacji ani akceptacji. Nie kopiuj całych komentarzy botów do raportu.

## 5. Bitbucket i istniejące linki Jira

PR #1..9 poniżej należą do `course-workspace/map-data-jobs-pipelines`. Obcy PR #1 z `course-workspace/ai-php-course-08-2026` jest innym źródłem. Numery PR są lokalne dla repozytorium; nie łącz ich z GitHub po numerze.

| PR | Dowód i kandydaci | Decyzja |
| --- | --- | --- |
| pipeline #1 | TEST-12, remote link 10000 na TEST-12 | `high/ignore`, evidence zawiera `already_linked_no_action`. |
| pipeline #2 | TEST-17, remote link 10001 na TEST-17 | `high/ignore`, `already_linked_no_action`. |
| pipeline #3 | TEST-15, remote link 10002 na TEST-15; TEST-3 jako kontekst | `high/ignore`, `already_linked_no_action`. Wzmianka o epiku nie wymaga drugiego linku; brak output pozostaje BLOCKED. |
| pipeline #4 | TEST-21 w gałęzi i commicie | `high/link` po porównaniu zakresu DASH-465; odczytaj więcej niż tytuł. |
| pipeline #5 | TSET-9, kontekst eksportu SL-461 | `flag_for_human`, kandydat TEST-9; nie poprawiaj literówki jako faktu. |
| pipeline #6 | SL-461, kandydaci TEST-1 i TEST-7 | `flag_for_human`, osobne wiersze kandydatów, bez dwóch runów. |
| pipeline #7 | TEST-99 w tytule i TEST-18 w opisie | Dwa wiersze: nieistniejący TEST-99 z pustym jira_key i `flag_for_human`; istniejący TEST-18 może mieć `link` po potwierdzeniu zakresu. |
| pipeline #8 | Opis `jobs/poi-462.yaml`, kandydaci TEST-24/TEST-6 i komentarz o wydaniu | `flag_for_human`. W tym snapshocie nie ma treści YAML/diffu Bitbucket: nie możesz udowodnić 2026.10 z nieprzeczytanego pliku. Poproś o dowód przed akceptacją. |
| pipeline #9 | Walidacja OSM wskazuje TEST-12, ale remote link 10003 należy do TEST-13 | `flag_for_human`; `source_id=jira:TEST-13:remotelink:10003`, obecny właściciel TEST-13 i proponowany TEST-12 w evidence. Zaproponuj korektę, niczego nie przenoś. |
| obce repo #1 | TEST-9 w tytule i commicie | `ignore` albo `flag_for_human`, bez propozycji linku. Istniejący klucz nie dowodzi wspólnej pracy repozytoriów. |

Oczekujesz czterech niepustych wyników `remotelinks`: TEST-12, TEST-17, TEST-15 i TEST-13. Każdy trzeba porównać z treścią docelowego PR. Pozostałe zgłoszenia zwracają puste listy; brak linku nie jest samodzielnym dowodem braku związku.

## 6. Confluence: czego szukać na stronach?

| Strona / ID | Oczekiwane ustalenie |
| --- | --- |
| Map Data Jobs / 220102657 | Rodzic czterech stron; syntetyczny kontekst, bez potwierdzenia wykonania pipeline. |
| Konwencje parametrów zleceń / 220135425 | ISO regionów, YYYY.MM, kolejność osi bbox, formaty, kroki i ścieżki; TEST-1/6/7/33. Wzorzec ścieżki nie zatwierdza konkretnego output_path. |
| Runbook / 220168193 | Rozróżnij literówkę TEST-35 od awarii spot TEST-36 i pustego chunku TEST-12. TEST-99 pozostaje błędną wzmianką. Restart jest rekomendacją, nie akcją agenta. |
| Kalendarz wydań Q4 2026 / 220200961 | Treść wersji z 05.11 podaje dla SL-461 stary termin 24.11, wobec 19.11 z komentarza Jira. Data wydania 27.11 nie jest deadline każdego zamówienia. Daty wersji nie dopowiadaj z nieobecnego createdAt. |
| WB-ROADS-07 / 220233729 | TEST-3/14/15/16, PL-22, 2026.11 i is_deleted=false; output nadal niezatwierdzony. Brakujące powiązanie do pytania TEST-30 wskaż jako `flag_for_human`. |

Rozpoznaj pełne URL i gołe klucze. W komentarzach Jira artefakt Markdown `\~` w adresie strony wymaga normalizacji przy porównaniu URL. ID strony umieszczaj w source_id/evidence, nigdy jako jira_key. Nie wymagaj strony przy każdym tickecie, ale odnotuj ważne luki i konflikty.

## 7. Co rzeczywiście sprawdzają walidatory?

```powershell
uv run --with pyyaml --with jsonschema course-materials/exercises/jira-mcp/validate_jobs.py reports/jira-jobs/jobs
```

```powershell
uv run course-materials/exercises/jira-mcp/validate_links.py reports/jira-jobs/links.csv
```

Pierwszy sprawdza format konfiguracji i obowiązkowe przyczyny `null`, drugi kontrakt CSV i istnienie rozwiązanych kluczy. Zielony wynik nie dowodzi poprawności parametrów, trafności linków ani kompletności analizy. CSV ma kolumny `source,source_id,mention_text,jira_key,confidence,action,evidence`; source to pr/page/comment, confidence high/medium/low, action link/flag_for_human/ignore. Nie ma jednej wymaganej liczby wierszy.

Ręcznie sprawdź przynajmniej pięć trudnych wzmianek, w tym konflikt wydania, literówkę, obce repozytorium i błędny istniejący link. Zapisz, co w pierwszym wyniku było błędne i jaki dowód zmienił ocenę.

## 8. Jeśli wykonałeś opcjonalne Decisions

Porównaj pięć par z manifestu z sekcjami GitHub i Bitbucket powyżej. Oceniaj osobno semantyczne `same_work/different_work/insufficient_evidence` i końcowe `link/flag_for_human/ignore`. Model może poprawnie rozpoznać wspólne zamówienie, ale konflikt, literówka lub brak decyzji nadal wymagają człowieka. Poprawne rozpoznanie istniejącego linku nie uzasadnia tworzenia drugiego.

Zachowaj z góry ustalone progi: `max(probabilities)<0.85`, margines dwóch największych `<0.20` albo wynik `insufficient_evidence` oznaczają abstencję. Błąd API oznacza brak wyniku i koniec pętli. Sprawdź najwyżej 5 prób łącznie, brak retry, koszt zmierzony oraz próby bez kosztu; nie zamieniaj braku pomiaru na zero. Policz trafne decyzje, błędne propozycje linku i abstencje. Pięć przykładów nie kalibruje modelu do produkcji.
