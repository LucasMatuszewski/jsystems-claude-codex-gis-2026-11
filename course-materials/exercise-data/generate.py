#!/usr/bin/env python3
"""Deterministic generator for the course exercise dataset (seed=42).

Outputs (all committed to the repo, regenerate only if you change the logic):
  csv/products.csv, csv/customers.csv, csv/orders.csv, csv/order_items.csv, csv/complaints.csv
  kb/*.md            - device spec sheets (knowledge base for RAG/sqlite-vec exercises)
  hidden-patterns.md - SPOILER: documented patterns hidden in the data + measured stats

Hidden patterns baked into the data:
  P1: supplier "TechSource Shenzhen" has a complaint rate rising month-over-month in 2026
  P2: seasonal sales spike in November and December (Black Friday / Christmas)
  P3: customers from France cancel orders ~3x more often than the baseline
  P4: model "Nexon X15" has a cluster of battery complaints (documented in its KB known issues)
"""

import csv
import os
import random
from datetime import date, datetime, timedelta

rng = random.Random(42)
BASE = os.path.dirname(os.path.abspath(__file__))

MONTHS = []  # (year, month) from 2024-07 to 2026-06
y, m = 2024, 7
for _ in range(24):
    MONTHS.append((y, m))
    m += 1
    if m > 12:
        m, y = 1, y + 1

SUPPLIERS = ["TechSource Shenzhen", "Nordic Components", "Quantix Electronics",
             "BlueWave Manufacturing", "Iberia Digital", "PrimeTech Ltd"]

CATEGORIES = {
    "laptop": (2200, 8900), "smartphone": (900, 6500), "tablet": (700, 4200),
    "monitor": (500, 3800), "headphones": (150, 1800), "smartwatch": (400, 2600),
    "router": (120, 900),
}

# Curated devices that also get a KB spec sheet (ids 1..N in insertion order)
KB_DEVICES = [
    {"name": "Nexon X15", "category": "laptop", "supplier": "TechSource Shenzhen",
     "cpu": "OctaCore V9 3.8 GHz", "ram": "16 GB DDR5", "display": "15.6\" IPS 2560x1440 165 Hz",
     "battery": "62 Wh, deklarowane 9 h pracy", "ports": "2x USB-C (1x TB4), 2x USB-A, HDMI 2.1, jack",
     "known_issues": "Znany problem: w partiach produkcyjnych 2025-Q4 i 2026 przyspieszona degradacja "
                     "ogniwa baterii - objawy: spadek do <60% pojemnosci w 6 miesiecy, nagle wylaczenia "
                     "przy 20-30% wskazania. Reklamacje z tym objawem kwalifikuja sie do wymiany baterii "
                     "lub urzadzenia w ramach gwarancji."},
    {"name": "Nexon X13 Air", "category": "laptop", "supplier": "TechSource Shenzhen",
     "cpu": "OctaCore V9e 3.2 GHz", "ram": "16 GB LPDDR5", "display": "13.4\" IPS 1920x1200 60 Hz",
     "battery": "54 Wh, deklarowane 12 h pracy", "ports": "2x USB-C, jack",
     "known_issues": "Brak znanych wad seryjnych. Zawiasy wrazliwe na otwieranie za rog pokrywy."},
    {"name": "Aurix ProBook 14", "category": "laptop", "supplier": "Nordic Components",
     "cpu": "HexaCore N7 4.1 GHz", "ram": "32 GB DDR5", "display": "14\" OLED 2880x1800 90 Hz",
     "battery": "70 Wh, deklarowane 10 h pracy", "ports": "2x TB4, USB-A, HDMI, czytnik SD",
     "known_issues": "Sporadyczne migotanie ekranu OLED przy 90 Hz po aktualizacji sterownika 31.0.101 - "
                     "usuwane aktualizacja firmware, nie kwalifikuje sie jako wada sprzetowa."},
    {"name": "Velar Slim 17", "category": "laptop", "supplier": "Quantix Electronics",
     "cpu": "OctaCore Q5 3.6 GHz", "ram": "16 GB DDR5", "display": "17.3\" IPS 1920x1080 144 Hz",
     "battery": "48 Wh, deklarowane 6 h pracy", "ports": "USB-C, 3x USB-A, HDMI, RJ-45, jack",
     "known_issues": "Brak znanych wad seryjnych."},
    {"name": "Pixelon P9 Pro", "category": "smartphone", "supplier": "BlueWave Manufacturing",
     "cpu": "Krait X2", "ram": "12 GB", "display": "6.7\" AMOLED 3200x1440 120 Hz",
     "battery": "5100 mAh, ladowanie 65 W", "ports": "USB-C, eSIM + nanoSIM",
     "known_issues": "Szklo tylne podatne na pekniecia przy upadku z <1 m - uszkodzenie mechaniczne, "
                     "nie podlega gwarancji, mozliwa platna naprawa."},
    {"name": "Pixelon P9 Lite", "category": "smartphone", "supplier": "BlueWave Manufacturing",
     "cpu": "Krait X1e", "ram": "8 GB", "display": "6.4\" AMOLED 2400x1080 90 Hz",
     "battery": "4800 mAh, ladowanie 33 W", "ports": "USB-C, dual nanoSIM",
     "known_issues": "Brak znanych wad seryjnych."},
    {"name": "Nexon Tab S8", "category": "tablet", "supplier": "TechSource Shenzhen",
     "cpu": "OctaCore V8t", "ram": "8 GB", "display": "11\" IPS 2560x1600 120 Hz",
     "battery": "8000 mAh", "ports": "USB-C, magnetyczne zlacze klawiatury",
     "known_issues": "Brak znanych wad seryjnych. Rysik sprzedawany osobno - brak rysika nie jest brakiem kompletu."},
    {"name": "Aurix View 27Q", "category": "monitor", "supplier": "Nordic Components",
     "cpu": "-", "ram": "-", "display": "27\" IPS 2560x1440 165 Hz, HDR400",
     "battery": "-", "ports": "2x HDMI 2.1, DP 1.4, USB-C 65 W, hub USB",
     "known_issues": "Do 3 martwych subpikseli miesci sie w normie ISO - nie kwalifikuje sie do reklamacji."},
    {"name": "SonicWave ANC 700", "category": "headphones", "supplier": "Iberia Digital",
     "cpu": "-", "ram": "-", "display": "-",
     "battery": "40 h z ANC, ladowanie USB-C", "ports": "USB-C, jack 3.5 mm (kabel w zestawie)",
     "known_issues": "Pierwsze partie (do 2024-10): trzeszczenie prawej sluchawki przy ANC - wada uznawana, "
                     "wymiana na nowy egzemplarz."},
    {"name": "Velar Watch 2", "category": "smartwatch", "supplier": "Quantix Electronics",
     "cpu": "-", "ram": "-", "display": "1.43\" AMOLED 466x466",
     "battery": "14 dni typowe uzycie", "ports": "ladowarka magnetyczna",
     "known_issues": "Uszczelnienie 5 ATM - uszkodzenia po nurkowaniu z aparatura nie podlegaja gwarancji."},
    {"name": "PrimeLink AX6 Router", "category": "router", "supplier": "PrimeTech Ltd",
     "cpu": "-", "ram": "-", "display": "-",
     "battery": "-", "ports": "WAN 2.5 GbE, 4x LAN 1 GbE, USB 3.0",
     "known_issues": "Brak znanych wad seryjnych."},
    {"name": "Nexon X15 Creator", "category": "laptop", "supplier": "TechSource Shenzhen",
     "cpu": "OctaCore V9 3.8 GHz + GPU RTZ 4600", "ram": "32 GB DDR5", "display": "15.6\" OLED 3840x2160 60 Hz",
     "battery": "80 Wh, deklarowane 7 h pracy", "ports": "2x TB4, 2x USB-A, HDMI 2.1, czytnik SD, jack",
     "known_issues": "Wariant Creator NIE jest objety problemem baterii modelu X15 (inne ogniwo, 80 Wh)."},
]

BRANDS = {"laptop": ["Nexon", "Aurix", "Velar"], "smartphone": ["Pixelon", "Nexon"],
          "tablet": ["Nexon", "Pixelon"], "monitor": ["Aurix", "Velar"],
          "headphones": ["SonicWave", "Iberia"], "smartwatch": ["Velar", "Pixelon"],
          "router": ["PrimeLink", "Quantix"]}

FIRST = ["Anna", "Piotr", "Katarzyna", "Marek", "Ewa", "Tomasz", "Agnieszka", "Jan", "Marta", "Pawel",
         "Hans", "Sofie", "Luc", "Marie", "Carlos", "Lucia", "Petr", "Eva", "Joao", "Ines", "Sven", "Nina"]
LAST = ["Kowalski", "Nowak", "Wisniewska", "Wojcik", "Kaminski", "Lewandowska", "Zielinski", "Mazur",
        "Muller", "Schmidt", "Dubois", "Moreau", "Garcia", "Fernandez", "Novak", "Svoboda", "Silva",
        "Santos", "Jansen", "Bakker", "Larsen", "Berg"]
COUNTRIES = ["PL", "PL", "PL", "PL", "DE", "DE", "CZ", "FR", "FR", "ES", "PT", "NL", "SK"]  # weighted

RETURN_REASONS = ["changed mind", "wrong item delivered", "does not meet expectations"]
COMPLAINT_REASONS = ["damaged in transport", "manufacturing defect", "battery issue",
                     "screen defect", "performance issues", "connectivity issues"]


def d(iso_year, iso_month, day):
    return date(iso_year, iso_month, day).isoformat()


def rand_day(year, month):
    last = 28 if month == 2 else 30
    return date(year, month, rng.randint(1, last))


def build_products():
    products = []
    for kb in KB_DEVICES:
        lo, hi = CATEGORIES[kb["category"]]
        products.append({"id": len(products) + 1, "name": kb["name"], "category": kb["category"],
                         "price": round(rng.uniform(lo * 1.2, hi), 2), "supplier": kb["supplier"]})
    suffixes = ["Neo", "Max", "SE", "Mini", "Plus", "Edge", "Core", "One", "Go", "Ultra"]
    seen = {p["name"] for p in products}
    while len(products) < 60:
        cat = rng.choice(list(CATEGORIES))
        name = f"{rng.choice(BRANDS[cat])} {rng.choice(suffixes)} {rng.randint(3, 29)}"
        if name in seen:
            continue
        seen.add(name)
        lo, hi = CATEGORIES[cat]
        products.append({"id": len(products) + 1, "name": name, "category": cat,
                         "price": round(rng.uniform(lo, hi), 2), "supplier": rng.choice(SUPPLIERS)})
    return products


def build_customers(n=800):
    customers = []
    for i in range(1, n + 1):
        created = date(2022, 1, 1) + timedelta(days=rng.randint(0, 900))
        customers.append({"id": i, "name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                          "country": rng.choice(COUNTRIES), "created_at": created.isoformat()})
    return customers


def build_orders(products, customers):
    orders, items = [], []
    oid, iid = 0, 0
    today = date(2026, 6, 30)
    for (yy, mm) in MONTHS:
        n = 180
        if mm == 11:
            n = int(n * 1.9)   # P2: Black Friday
        elif mm == 12:
            n = int(n * 2.2)   # P2: Christmas
        n = int(n * rng.uniform(0.9, 1.1))
        for _ in range(n):
            oid += 1
            cust = rng.choice(customers)
            odate = rand_day(yy, mm)
            cancel_p = 0.18 if cust["country"] == "FR" else 0.055  # P3
            if (today - odate).days < 7:
                status = rng.choice(["pending", "completed", "completed"])
            else:
                status = "cancelled" if rng.random() < cancel_p else "completed"
            orders.append({"id": oid, "customer_id": cust["id"],
                           "order_date": odate.isoformat(), "status": status})
            for _ in range(rng.choices([1, 2, 3], weights=[70, 22, 8])[0]):
                iid += 1
                p = rng.choice(products)
                price = round(p["price"] * rng.uniform(0.9, 1.05), 2)
                items.append({"id": iid, "order_id": oid, "product_id": p["id"],
                              "quantity": rng.choices([1, 2], weights=[92, 8])[0], "unit_price": price})
    return orders, items


def build_complaints(products, orders, items):
    pmap = {p["id"]: p for p in products}
    omap = {o["id"]: o for o in orders}
    base_p = {"laptop": 0.075, "smartphone": 0.08, "tablet": 0.06, "monitor": 0.055,
              "headphones": 0.045, "smartwatch": 0.05, "router": 0.035}
    complaints = []
    cid = 0
    for it in items:
        o = omap[it["order_id"]]
        if o["status"] != "completed":
            continue
        p = pmap[it["product_id"]]
        odate = date.fromisoformat(o["order_date"])
        prob = base_p[p["category"]]
        if p["supplier"] == "TechSource Shenzhen" and odate.year == 2026:  # P1: ramp ~1.5x -> 4x
            prob *= 1.0 + (odate.month / 6.0) * 3.0
        if p["name"] == "Nexon X15":  # P4
            prob = max(prob, 0.30)
        if rng.random() > prob:
            continue
        cid += 1
        is_return = rng.random() < 0.4
        if is_return:
            ctype, reason = "return", rng.choice(RETURN_REASONS)
            created = odate + timedelta(days=rng.randint(1, 14))
        else:
            ctype = "complaint"
            if p["name"] == "Nexon X15" and rng.random() < 0.7:
                reason = "battery issue"  # P4
            else:
                reason = rng.choice(COMPLAINT_REASONS)
            created = odate + timedelta(days=rng.randint(3, 240))
        if created > date(2026, 6, 30):
            created = date(2026, 6, 30)
        decision = rng.choices(["accepted", "rejected", "partial refund"], weights=[55, 30, 15])[0]
        source = rng.choices(["ai", "human"], weights=[60, 40])[0]
        if rng.random() < 0.08:
            resolved = ""
        else:
            resolved = (created + timedelta(days=rng.randint(1, 21))).isoformat()
        complaints.append({"id": cid, "order_id": o["id"], "product_id": p["id"], "type": ctype,
                           "reason_category": reason, "created_at": created.isoformat(),
                           "resolved_at": resolved, "decision": decision, "decision_source": source})
    return complaints


def write_csv(name, rows):
    path = os.path.join(BASE, "csv", name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def write_kb(products):
    pmap = {p["name"]: p for p in products}
    for kb in KB_DEVICES:
        p = pmap[kb["name"]]
        slug = kb["name"].lower().replace(" ", "-")
        lines = [
            f"# {kb['name']} - karta produktu",
            "",
            f"- **Kategoria:** {kb['category']}",
            f"- **Dostawca:** {kb['supplier']}",
            f"- **Cena katalogowa:** {p['price']} PLN",
            f"- **ID w bazie:** {p['id']}",
            "",
            "## Specyfikacja",
            "",
            f"- Procesor: {kb['cpu']}",
            f"- Pamiec: {kb['ram']}",
            f"- Ekran: {kb['display']}",
            f"- Bateria: {kb['battery']}",
            f"- Zlacza: {kb['ports']}",
            "",
            "## Gwarancja i zwroty",
            "",
            "- Gwarancja: 24 miesiace (konsument), 12 miesiecy (B2B).",
            "- Zwrot konsumencki: 14 dni bez podania przyczyny, sprzet bez sladow uzytkowania, komplet w oryginalnym pudelku.",
            "- Uszkodzenia mechaniczne z winy uzytkownika nie podlegaja gwarancji.",
            "",
            "## Znane problemy (dla agenta obslugi reklamacji)",
            "",
            kb["known_issues"],
            "",
        ]
        with open(os.path.join(BASE, "kb", f"{slug}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def write_hidden_patterns(products, orders, items, complaints):
    pmap = {p["id"]: p for p in products}
    omap = {o["id"]: o for o in orders}

    # P1 stats: TechSource complaint rate per H1-2026 month vs others
    ts_sold, ts_compl, ot_sold, ot_compl = {}, {}, {}, {}
    for it in items:
        o = omap[it["order_id"]]
        if o["status"] != "completed" or not o["order_date"].startswith("2026"):
            continue
        mo = o["order_date"][:7]
        if pmap[it["product_id"]]["supplier"] == "TechSource Shenzhen":
            ts_sold[mo] = ts_sold.get(mo, 0) + 1
        else:
            ot_sold[mo] = ot_sold.get(mo, 0) + 1
    for c in complaints:
        o = omap[c["order_id"]]
        if not o["order_date"].startswith("2026"):
            continue
        mo = o["order_date"][:7]
        if pmap[c["product_id"]]["supplier"] == "TechSource Shenzhen":
            ts_compl[mo] = ts_compl.get(mo, 0) + 1
        else:
            ot_compl[mo] = ot_compl.get(mo, 0) + 1
    p1 = ["| miesiac (data zamowienia) | TechSource | pozostali |", "|---|---|---|"]
    for mo in sorted(ts_sold):
        a = 100 * ts_compl.get(mo, 0) / max(ts_sold.get(mo, 1), 1)
        b = 100 * ot_compl.get(mo, 0) / max(ot_sold.get(mo, 1), 1)
        p1.append(f"| {mo} | {a:.1f}% | {b:.1f}% |")

    novdec = sum(1 for o in orders if o["order_date"][5:7] in ("11", "12"))
    x15 = [c for c in complaints if pmap[c["product_id"]]["name"] == "Nexon X15"]
    x15_batt = sum(1 for c in x15 if c["reason_category"] == "battery issue")

    lines = [
        "# SPOILER - ukryte wzorce w danych (nie pokazuj przed cwiczeniem!)",
        "",
        "Wygenerowane deterministycznie przez generate.py (seed=42). Uzyj do weryfikacji,",
        "czy analiza (agenta i Twoja) znalazla te wzorce.",
        "",
        "## P1: Rosnaca awaryjnosc dostawcy TechSource Shenzhen w 2026",
        "",
        "Odsetek pozycji zamowien (completed) z reklamacja/zwrotem wg miesiaca zamowienia:",
        "",
        *p1,
        "",
        "## P2: Sezonowy szczyt sprzedazy listopad-grudzien",
        "",
        f"Zamowienia w XI-XII: {novdec} z {len(orders)} ({100*novdec/len(orders):.1f}%; "
        f"udzial rownomierny wynosilby ~16.7%).",
        "",
        "## P3: Wysoki odsetek anulowanych zamowien we Francji (FR)",
        "",
        "FR ~18% anulowanych vs ~5.5% w pozostalych krajach (sprawdz JOIN orders x customers).",
        "",
        "## P4: Klaster reklamacji baterii modelu Nexon X15",
        "",
        f"Nexon X15: {len(x15)} zgloszen, z czego {x15_batt} to 'battery issue'. "
        "Wariant 'Nexon X15 Creator' NIE jest dotkniety (por. kb/nexon-x15.md).",
        "",
    ]
    with open(os.path.join(BASE, "hidden-patterns.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(os.path.join(BASE, "csv"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "kb"), exist_ok=True)
    products = build_products()
    customers = build_customers()
    orders, items = build_orders(products, customers)
    complaints = build_complaints(products, orders, items)
    counts = {
        "products": write_csv("products.csv", products),
        "customers": write_csv("customers.csv", customers),
        "orders": write_csv("orders.csv", orders),
        "order_items": write_csv("order_items.csv", items),
        "complaints": write_csv("complaints.csv", complaints),
    }
    write_kb(products)
    write_hidden_patterns(products, orders, items, complaints)
    for k, v in counts.items():
        print(f"{k}: {v} rows")
    print(f"kb: {len(KB_DEVICES)} spec sheets")


if __name__ == "__main__":
    main()
