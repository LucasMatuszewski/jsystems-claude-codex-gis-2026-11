# Przykładowe zdjęcia urządzeń

Zdjęcia do testowania aplikacji, którą budujemy na kursie: pracownik wgrywa zdjęcie sprzętu, a model ocenia jego stan i pomaga zdecydować o zwrocie albo reklamacji.

| Plik | Format | Wymiary | Rozmiar |
| --- | --- | --- | --- |
| `laptop-1.png` | JPEG mimo rozszerzenia `.png` | 3024 x 3135 | 1,2 MB |
| `laptop-2.webp` | WebP | 863 x 843 | 166 KB |
| `phone-1.jpg` | JPEG | 900 x 1200 | 107 KB |
| `phone-2.jpeg` | JPEG | 387 x 516 | 15 KB |
| `phone-3.jpeg` | JPEG | 449 x 445 | 32 KB |

Zestaw jest różnorodny, tak jak pliki, które klienci naprawdę wysyłają: różne formaty, bardzo duże i bardzo małe zdjęcia, rozszerzenie niezgodne z zawartością.

## Jak ich używać

- W testach E2E wgrywaj te pliki przez prawdziwy formularz aplikacji (Playwright `setInputFiles`).
- W ręcznym sprawdzeniu aplikacji wgraj każde zdjęcie i przeczytaj ocenę modelu.
- Wskaż ten katalog w głównym `AGENTS.md`, żeby agent korzystał z tych plików.

## Zasady

- Nie zmieniaj nazw plików i nie dodawaj do nich opisu stanu urządzenia. Nazwa mówi tylko, czy to laptop, czy telefon.
- Nie przycinaj zdjęć, nie zmieniaj formatu, nie dopisuj na nich etykiet ani podpisów.
- Nie podawaj modelowi, co jest na zdjęciu, ani w prompcie, ani w danych testowych. Model ma to ocenić sam, tak jak przy zdjęciu od klienta.
- Opis sprawy wpisany przez pracownika w formularzu to osobne dane. Nie mieszaj go z tym, co widać na zdjęciu.
- Test sprawdza faktyczną ocenę modelu. Nie zakładaj z góry, co model powinien zobaczyć.
- Do testów wgrywania zdjęć nie generuj własnych obrazów, ilustracji ani pustych plików. Używaj tylko prawdziwych zdjęć.
