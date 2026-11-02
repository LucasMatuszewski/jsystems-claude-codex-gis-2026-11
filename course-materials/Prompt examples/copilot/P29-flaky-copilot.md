Pomóż mi zbadać niestabilny test w aktualnej aplikacji warsztatowej. Wskażę test i jego log z lokalnego lub testowego środowiska; nie zakładaj, że test jest flaky, dopóki nie mamy powtarzalnych obserwacji. Przeczytaj plik testu, fixture i tylko ten kod, który wpływa na jego wynik. Nie odczytuj sekretów.

Zapisz dokładne polecenie, commit, dane wejściowe, liczbę wykonań i liczbę porażek. Z moją zgodą powtórz test ograniczoną liczbę razy, np. 10, z tymi samymi danymi. Jeśli nie uda się odtworzyć błędu, podaj ograniczenia i hipotezy do dalszego sprawdzenia. Brak porażki nie dowodzi stabilności.

Oceń czas, kolejność, asynchroniczność, współdzielony stan i zależności zewnętrzne. Powiąż każdą hipotezę z logiem lub kodem. Zaproponuj jeden eksperyment rozróżniający przyczyny. Nie maskuj problemu arbitralnym sleep, większym timeoutem, retry, pominięciem ani słabszą asercją.

Po zatwierdzeniu przyczyny zaproponuj minimalną poprawkę i test regresji. Oddziel poprawę testu od poprawy aplikacji. Przed i po zmianie porównaj ten sam ograniczony przebieg. Zwróć dowód, pozostałą niepewność i diff; nie deklaruj naprawy wyłącznie na podstawie jednego zielonego uruchomienia.
