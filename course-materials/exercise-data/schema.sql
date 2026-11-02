-- Schema for the course exercise dataset (SQLite / ANSI-friendly).
-- No indexes on purpose (beyond PKs) - creating them is part of the optimization exercise.

CREATE TABLE products (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  category    TEXT NOT NULL,
  price       REAL NOT NULL,
  supplier    TEXT NOT NULL
);

CREATE TABLE customers (
  id          INTEGER PRIMARY KEY,
  name        TEXT NOT NULL,
  country     TEXT NOT NULL,
  created_at  TEXT NOT NULL          -- ISO date
);

CREATE TABLE orders (
  id          INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  order_date  TEXT NOT NULL,         -- ISO date
  status      TEXT NOT NULL          -- completed | cancelled | pending
);

CREATE TABLE order_items (
  id          INTEGER PRIMARY KEY,
  order_id    INTEGER NOT NULL REFERENCES orders(id),
  product_id  INTEGER NOT NULL REFERENCES products(id),
  quantity    INTEGER NOT NULL,
  unit_price  REAL NOT NULL
);

CREATE TABLE complaints (
  id              INTEGER PRIMARY KEY,
  order_id        INTEGER NOT NULL REFERENCES orders(id),
  product_id      INTEGER NOT NULL REFERENCES products(id),
  type            TEXT NOT NULL,     -- complaint | return
  reason_category TEXT NOT NULL,
  created_at      TEXT NOT NULL,     -- ISO date
  resolved_at     TEXT,              -- ISO date, NULL = unresolved
  decision        TEXT NOT NULL,     -- accepted | rejected | partial refund
  decision_source TEXT NOT NULL      -- ai | human
);
