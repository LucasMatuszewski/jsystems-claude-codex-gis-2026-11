# PRD prompt: Dostępność transportu publicznego

**Jak użyć:** uruchom zainstalowany skill `write-prd` (`claude` -> `/write-prd`) i wklej cały poniższy prompt jako opis produktu. Możesz też wkleić go bezpośrednio i pozwolić skillowi się aktywować. Odpowiedz na pytania skilla. Wynik zapisz jako `docs/PRD.md`.

---

Przygotuj PRD produktu "Mapa dostępu do komunikacji". Planista chce zobaczyć, które części Łodzi mają przystanek w odległości 400 m oraz ile odjazdów jest dostępnych w poszczególnych godzinach. Większość logiki to deterministyczny SQL i obliczenia przestrzenne, a nie zadanie dla AI.

## Użytkownicy i źródła

- Analityk GIS sprawdza poprawność importu GTFS i porównuje pokrycie obszarów.
- Planista transportu wybiera datę i godzinę, ogląda odjazdy i obszary słabego dostępu.
- Odbiorca raportu chce rozumieć miarę dostępności i ograniczenia danych o ludności.
- Oficjalny [GTFS Łodzi](https://otwarte.miasto.lodz.pl/transport_komunikacja/), archiwum `https://otwarte.miasto.lodz.pl/wp-content/uploads/2025/06/GTFS.zip`. Skrypt `course-materials/exercise-data/real/download_gtfs.py` pobiera i rozpakowuje cały feed oraz ładuje `stops.txt` do DuckDB. Do częstości potrzebne są także `trips`, `routes`, `stop_times`, `calendar` i/lub `calendar_dates`; importer aplikacji ma je obsłużyć.
- Granice osiedli: warstwa `jednostki_pomocnicze` (14) w [oficjalnym InterSIT Łodzi](https://mapa.lodz.pl/3/rest/services/OGC/Lodz/MapServer/14), do pobrania przez operację query z geometrią w WGS84. Ludność: [zestawienie UM dla osiedli na 2026 r.](https://bip.uml.lodz.pl/files/bip/public/BIP_TW_26/BAM_12_BO_podzial_20260108.pdf), z nazwami i liczbami mieszkańców; [GUS BDL](https://bdl.stat.gov.pl/) jako alternatywa po sprawdzeniu poziomu jednostki. Zachowaj datę statystyki i nie utożsamiaj meldunków z faktyczną liczbą osób przebywających na obszarze. Przed przyjęciem liczb zweryfikuj dostępność granic i zgodnych jednostek, identyfikatory oraz warunki pobrania. Brak ludności na poziomie osiedla blokuje wskaźnik ludnościowy; nie przypisuj automatycznie liczby mieszkańców całego miasta do każdego osiedla.
- PRD ma opisać połączenie nazw osiedli w warstwie i tabeli, jawne korekty nazw oraz raport niedopasowanych jednostek; potwierdź dostęp do geometrii i aktualność granic przed przyjęciem wskaźników. MVP geometryczne może działać bez ludności. Publiczne statystyki agregatowe nie są danymi o pojedynczych osobach.

## Funkcje i przepływ

1. Pipeline Python + DuckDB importuje feed, datę obowiązywania, jednostki administracyjne i dane ludności. Panel pokazuje ich daty, obszar i wyniki walidacji.
2. Kod tworzy bufory 400 m wokół aktywnych przystanków w metrycznym CRS i oblicza sumę geometryczną, bez podwójnego liczenia przecięć. To odległość w linii prostej; rzeki, tory i dostęp pieszy mogą zmieniać faktyczny zasięg.
3. SQL liczy odjazdy na przystanek i godzinę dla wybranej daty: kalendarz kursowania, wyjątki, kierunek i wartości czasu po `24:00:00` muszą być obsłużone. Dla przystanków nadrzędnych i peronów uzgodnij regułę agregacji, żeby nie dublować odjazdów.
4. Dashboard WWW pokazuje przystanki, bufory i granice osiedli/dzielnic, warstwę częstości, filtry daty/godziny/linii oraz tabelę pokrytej powierzchni. Kliknięcie przystanku pokazuje liczbę odjazdów i rozkład godzinowy.
5. Jeśli dostępna jest zgodna przestrzennie siatka ludności, kod liczy liczbę mieszkańców w zasięgu. Sama liczba ludności dzielnicy pozwala najwyżej na przybliżenie z założeniem równomiernego rozmieszczenia. Oznacz je jako estymację i pokaż osobno od dokładnie zmierzonej powierzchni. Nie przedstawiaj udziału powierzchni jako udziału ludności.
6. Eksport CSV/GeoParquet zawiera definicję wskaźników, wersję danych i wyniki testów jakości. Niedostępne dane ludności lub data poza kalendarzem mają czytelny komunikat zamiast zera.

## Opcjonalny Jev

Jev by TypeSafe przez OpenRouter jest opcjonalnym ćwiczeniem semantycznym, wyłączonym w podstawowym MVP. Klasyfikuje wyłącznie nazwę przystanku i publiczny opis przystanku (jeśli istnieje), bez współrzędnych, godzin i ludności.

Pytanie Choice: "Jaką funkcję lokalizacji wskazuje nazwa/opis przystanku?" Stałe odpowiedzi: `rail_interchange`, `education`, `healthcare`, `airport`, `other`, `unknown`. Opisz granice klas i sposób obsługi nazwy zawierającej kilka funkcji. Kod stosuje próg abstencji i kieruje niepewne przypadki do `human_review`. Ta etykieta służy do filtrowania mapy, nigdy do obliczeń dostępności.

Jeśli rozszerzenie wejdzie do zakresu, przygotuj ręcznie oznaczone nazwy z każdej klasy, przypadki wieloznaczne i `unknown`, osobny zbiór do progów i testowy. Raportuj accuracy per klasę, macierz pomyłek, liczebności i coverage po abstencji. Bez etykiet nie deklaruj jakości. Awaria OpenRouter nie blokuje mapy ani SQL; żadna część podstawowego pipeline'u nie wymaga AI.

## Jakość i akceptacja

- Kontrole: wymagane pliki GTFS, klucze obce i unikalność ID, współrzędne, poprawność geometrii jednostek i CRS, zakres kalendarza, wyjątki świąteczne, czasy powyżej 24 godzin, brakujące odjazdy, zgodność roku i poziomu danych ludności.
- Uwzględnij testy punktu wewnątrz, na granicy 400 m i poza nią, nakładających się buforów, kursu nocnego, dnia bez kursów, wyjątku kalendarza, przystanku bez współrzędnych i braku danych ludności.
- Kryteria mają porównywać agregaty SQL z ręcznie policzonymi przypadkami z małego wycinka realnego feedu. Uzgodnij czas odpowiedzi mapy dla faktycznie policzonego wycinka, nie dla całej Polski.

## Poza zakresem

GTFS-Realtime, prognozy opóźnień, planowanie tras i izochron pieszych, ocena dostępności dla osób z niepełnosprawnościami na podstawie samego bufora, analiza pojedynczych mieszkańców, zmiany rozkładu i obowiązkowe AI.

## Wspólne ograniczenia

- To lokalne MVP dla jednego obszaru, uruchamiane na Windows 11 i Linux przez Python 3.12 + uv, bez Dockera, WSL i Hyper-V. Pipeline Python + DuckDB przygotowuje dane i agregaty; dashboard korzysta z jego wyników.
- Dashboard WWW ma mapę MapLibre GL JS z kaflami OpenFreeMap, bez klucza API (np. styl `https://tiles.openfreemap.org/styles/liberty`). Atrybucje "© OpenStreetMap contributors", OpenFreeMap i OpenMapTiles pozostają widoczne. Dodaj atrybucje warstw tematycznych.
- Styl wizualny aplikacji weź z tokenów i zasobów utworzonych podczas kursu w `assets/`, a jeśli istnieje, także z `docs/design-guidelines.md`. Nie wymyślaj nowego brandingu; brak tokenów zgłoś jako pytanie.
- Wejścia pozostają tylko do odczytu. Zapisuj oddzielnie wyniki, raport jakości i decyzje użytkownika. Błąd pobrania, pusty zbiór i brak wartości to różne stany, nigdy poprawne zera.
- Korzystamy tylko z publicznych danych wskazanych poniżej. Do zewnętrznych modeli wysyłamy wyłącznie jawnie wymienione pola; bez kluczy, prywatnych danych i całej bazy. Klucz OpenRouter pozostaje po stronie backendu.
- Jev by TypeSafe przez OpenRouter jest modelem decyzji semantycznych. PRD opisuje typy pytań i zamknięte wyniki, a aktualny identyfikator modelu, zgodność transportu z Noul/Choice i format API trzeba sprawdzić przed integracją. Brak obsługi lub awaria daje jawny stan niedostępności, nigdy wymyślony wynik. Nie wywołuj płatnego API podczas tworzenia PRD.
- Utrwalaj wersję danych, obszar, datę pobrania, konfigurację reguł, wersję modelu i pytania oraz wynik i prawdopodobieństwa. Ponowne przetworzenie tych samych wejść nie tworzy nowych duplikatów; decyzje człowieka mają trwały ślad.

Przygotuj funkcjonalne PRD: problem, użytkownicy, główny przepływ, historie użytkownika, mierzalne kryteria akceptacji, błędy i puste stany, jakość danych, ewaluacja, zakres MVP i poza zakresem oraz założenia i pytania. Użyj zainstalowanego `write-prd`, nie przepisuj jego metodyki. Szczegóły architektury pozostaw do osobnego ADR. Zapisz wynik po polsku w `docs/PRD.md`; nie implementuj jeszcze aplikacji. Jeśli ten plik istnieje, najpierw ustal z użytkownikiem, czy opis dotyczy aktualnego produktu.
