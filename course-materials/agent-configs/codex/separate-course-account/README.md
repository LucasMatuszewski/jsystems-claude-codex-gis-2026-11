# Osobne konto Codex na kurs (szkoleniowe obok firmowego)

Cel: pracować na koncie szkoleniowym (np. ChatGPT Business od trenera) tak, żeby firmowe konto, historia i konfiguracja Codex zostały nietknięte. Osobny katalog `CODEX_HOME` rozdziela logowanie, historię i konfigurację Codex na tym samym komputerze i koncie Windows.

Stan: Codex CLI 0.164.0, sprawdzone 28.10.2026. [Konfiguracja](https://developers.openai.com/codex/config-reference/) · [Logowanie](https://developers.openai.com/codex/auth/) · [Windows](https://developers.openai.com/codex/windows).

## Drugie konto Codex przez `CODEX_HOME`

Katalog `CODEX_HOME` rozdziela konfigurację, historię i lokalne dane autoryzacji. Profil wybiera ustawienia; sam nie przełącza konta. Utwórz katalogi i funkcje dla kont; każda funkcja przywraca poprzednie `CODEX_HOME` po zakończeniu polecenia:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.codex-business", "$HOME\.codex-enterprise" | Out-Null
```

```powershell
function codex-business { $previousCodexHome = $env:CODEX_HOME; try { $env:CODEX_HOME = "$HOME\.codex-business"; codex @args } finally { $env:CODEX_HOME = $previousCodexHome } }
```

```powershell
function codex-enterprise { $previousCodexHome = $env:CODEX_HOME; try { $env:CODEX_HOME = "$HOME\.codex-enterprise"; codex @args } finally { $env:CODEX_HOME = $previousCodexHome } }
```

Na kursie logujesz tylko konto szkoleniowe: `codex-business login`, potem `codex-business login status`. Przeglądarka musi wskazywać konto szkoleniowe. Nie kopiuj `auth.json` i nie wyświetlaj jego zawartości. Konto firmowe konfigurujesz zgodnie z polityką firmy. Funkcje działają w bieżącym terminalu; zdefiniuj je ponownie w nowym. Na Windows wystarcza natywny sandbox Codex, bez WSL.

### Profile: analiza i implementacja

Pliki [course-analysis.config.toml](course-analysis.config.toml) (tylko odczyt) i [course-implementation.config.toml](course-implementation.config.toml) (zapis w projekcie) skopiuj do `$HOME\.codex-business\`. Uruchom `codex-business --profile course-analysis` albo `codex-business --profile course-implementation`.

- Profil z `sandbox_mode` to konfiguracja klasyczna. Projekt może wybierać nazwany profil uprawnień o wyższym priorytecie; wtedy użyj `codex-business -c 'default_permissions="course-review"'` do analizy, a `course-workspace` do implementacji. Nie mieszaj obu mechanizmów bez sprawdzenia wyniku: `/permissions`, `/status`, `codex doctor --all`.
- Nie dodawaj `[profiles.nazwa]`: aktualne profile to osobne pliki `$env:CODEX_HOME\nazwa.config.toml`. Nie ustawiaj modelu w projekcie, jeśli ma go wybierać profil użytkownika.
- Proxy sieciowe włączaj na poziomie użytkownika; reguły domen bez działającego proxy nie ograniczają ruchu poleceń.

## Podagent tylko do odczytu

Przykładowa rola [luna-reader.toml](../agents/luna-reader.toml) (model Luna do ograniczonej analizy z cytowaniem źródeł) jest w katalogu `agents/` razem z innymi rolami. Skopiuj ją do `.codex/agents/` analizowanego projektu i jawnie poproś o delegację; kontrolę tylko do odczytu zapewnia sandbox rodzica, nie sama instrukcja w roli.
