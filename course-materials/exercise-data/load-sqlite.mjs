#!/usr/bin/env node
// Create lab.db (SQLite) from schema.sql + csv/*.csv using the built-in node:sqlite
// (Node 22.5+, no npm install needed). Usage: node load-sqlite.mjs

import { DatabaseSync } from 'node:sqlite';
import { readFileSync, existsSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const base = dirname(fileURLToPath(import.meta.url));
const dbPath = join(process.cwd(), 'lab.db');
if (existsSync(dbPath)) rmSync(dbPath);

// Minimal CSV parser (handles quoted fields; our data has no embedded newlines)
function parseCsv(text) {
  return text.trim().split(/\r?\n/).map((line) => {
    const out = [];
    let cur = '', inQ = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (inQ) {
        if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
        else if (ch === '"') inQ = false;
        else cur += ch;
      } else if (ch === '"') inQ = true;
      else if (ch === ',') { out.push(cur); cur = ''; }
      else cur += ch;
    }
    out.push(cur);
    return out;
  });
}

const db = new DatabaseSync(dbPath);
db.exec(readFileSync(join(base, 'schema.sql'), 'utf-8'));

for (const t of ['products', 'customers', 'orders', 'order_items', 'complaints']) {
  const rows = parseCsv(readFileSync(join(base, 'csv', `${t}.csv`), 'utf-8'));
  const cols = rows[0];
  const stmt = db.prepare(
    `INSERT INTO ${t} (${cols.join(',')}) VALUES (${cols.map(() => '?').join(',')})`
  );
  db.exec('BEGIN');
  for (const r of rows.slice(1)) stmt.run(...r.map((v) => (v === '' ? null : v)));
  db.exec('COMMIT');
  const { n } = db.prepare(`SELECT COUNT(*) AS n FROM ${t}`).get();
  console.log(`${t}: ${n} rows`);
}

db.close();
console.log(`OK -> ${dbPath}`);
