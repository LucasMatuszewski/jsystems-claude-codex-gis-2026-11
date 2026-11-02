# JetBrains AI Assistant: przykład reguły projektu

Przykład dla osób, które pracują w IntelliJ IDEA lub innym IDE JetBrains z AI Assistant. To punkt startowy, nie gotowa konfiguracja.

Folder `.aiassistant/` ma kształt konfiguracji projektu AI Assistant. Aby reguła działała, skopiuj go do katalogu głównego swojego repozytorium:

```bash
cp -r course-materials/agent-configs/jetbrains-ai-assistant/.aiassistant .
```

[`pom-security.md`](.aiassistant/rules/pom-security.md) działa przy plikach `pom.xml` (`apply: by file patterns`). Każe sprawdzić zależność przed dodaniem i rozważyć własny kod zamiast małej biblioteki, bo każda zależność to potencjalne ryzyko.

Regułę możesz też utworzyć i edytować w ustawieniach AI Assistant w IDE. Dostosuj jej treść i wzorce plików do swojego projektu.
