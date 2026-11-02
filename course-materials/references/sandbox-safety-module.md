# Sandbox Safety Mini-Module

## Cel modułu (10-25 min)
Dać uczestnikom prosty, praktyczny model bezpieczeństwa pracy z agentami:
1. sandbox vs brak sandboxa,
2. dlaczego **WSL ≠ izolacja**,
3. różnice zachowania agenta w bash vs PowerShell,
4. bezpieczne ustawienia domyślne do codziennej pracy.

---

## 1) Sandbox vs no-sandbox — szybkie porównanie

### Sandbox (zalecany start)
- Agent działa w ograniczonym środowisku (kontrola dostępu do systemu/plików/sieci).
- Łatwiej ograniczyć „blast radius” błędnej komendy.
- Lepszy tryb do nauki, eksperymentów i pracy na niepewnym kodzie.

### No-sandbox (tylko świadomie)
- Agent może dotknąć więcej zasobów hosta.
- Szybciej „działa”, ale rośnie ryzyko nieodwracalnych zmian.
- Wymaga dojrzałych guardrails (approvals, branch policy, backup, review discipline).

### Co powiedzieć grupie
> "Sandbox nie jest o spowalnianiu. Jest o tym, żeby błąd był mały i odwracalny."

---

## 2) WSL != izolacja

WSL to **środowisko uruchomieniowe** Linux na Windows, a nie pełna granica bezpieczeństwa.

- WSL poprawia zgodność narzędzi CLI i developer UX.
- Sam fakt „pracuję w WSL” nie oznacza automatycznie izolacji od hosta.
- Izolację daje dopiero konkretny sandbox/policy/permission model.

### Co powiedzieć grupie
> "WSL pomaga narzędziom działać, ale nie jest automatycznym sejfem. Sejfem są dopiero ograniczenia i approvale."

---

## 3) bash vs PowerShell — co praktycznie zmienia dla agentów

## Bash
- Często lepiej opisane ścieżki dla narzędzi open-source i skryptów dev.
- Spójniejsze zachowanie wielu przykładów z dokumentacji narzędzi AI/CLI.
- Wymaga uwagi na quoting i operatory powłoki.

## PowerShell
- Bardzo dobry w ekosystemie Windows/.NET i automatyzacji administracyjnej.
- Inna składnia, quoting i pipeline niż w bash (częsty punkt potknięć przy kopiowaniu komend 1:1).
- Agent musi dostać jasny kontekst, że komendy mają być generowane pod PowerShell.

### Wniosek trenerski
- Nie ma „jedynej słusznej” powłoki.
- Na kursie trzymamy jeden dominujący tor demonstracyjny (bash/Claude Code-first), ale jasno pokazujemy jak przenieść to na PowerShell bez kopiuj-wklej w ciemno.

---

## 4) Safe defaults — checklista na start zespołu

1. **Dedykowane repo/branch na ćwiczenie** (bez pracy na produkcyjnym main).
2. **Sandbox ON** jako domyślny tryb startowy.
3. **Approvals ON** dla działań potencjalnie ryzykownych.
4. **Małe taski** (jeden cel, mały diff, krótka pętla feedbacku).
5. **Review każdego diffu** przed kolejnym krokiem.
6. **Celowany test/lint** po zmianie (nie wszystko naraz).
7. **Commit po małym kroku** z jasnym opisem decyzji.
8. **Zero sekretów w promptach** i outputach.

### Minimalny chat-paste
```text
Bezpieczny start z agentem:
- pracujemy na dedykowanym branchu,
- sandbox + approvals są domyślnie włączone,
- zadania dzielimy na małe kroki,
- każdy diff czytamy przed testem/commitem,
- AI daje draft, człowiek podejmuje decyzję.
```

---

## 5) Typowe antywzorce (do szybkiego ostrzeżenia)
- "WSL mam, więc jestem bezpieczny".
- "Agent zrobił szybko, to merge bez czytania diffu".
- "Wrzucam duży prompt i liczę, że jakoś wyjdzie".
- "Najpierw wygoda, potem bezpieczeństwo".

---

## 6) Połączenie z resztą kursu
- Start pracy: ustawienie bezpiecznych nawyków.
- Implementacja i debugowanie: utrzymanie guardrails.
- Weryfikacja: quality/security review jako domknięcie procesu.
