#!/usr/bin/env python3
"""Create lab.db (SQLite) from schema.sql + csv/*.csv. Usage: python3 load-sqlite.py"""

import csv
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(os.getcwd(), "lab.db")

TABLES = ["products", "customers", "orders", "order_items", "complaints"]

if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
with open(os.path.join(BASE, "schema.sql"), encoding="utf-8") as f:
    con.executescript(f.read())

for t in TABLES:
    with open(os.path.join(BASE, "csv", f"{t}.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    cols = rows[0]
    ph = ",".join("?" * len(cols))
    data = [[None if v == "" else v for v in r] for r in rows[1:]]
    con.executemany(f"INSERT INTO {t} ({','.join(cols)}) VALUES ({ph})", data)
    con.commit()
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t}: {n} rows")

con.close()
print(f"OK -> {DB}")
