-- Load the exercise dataset into H2 (for Java participants).
-- Run from THIS directory, e.g.:
--   java -cp h2-*.jar org.h2.tools.RunScript -url "jdbc:h2:./lab" -script load-h2.sql
-- or paste into H2 Console (set the working dir or use absolute paths in CSVREAD).
-- In Spring Boot: put this as schema.sql/data.sql or run via ScriptUtils.

CREATE TABLE products (
  id INT PRIMARY KEY, name VARCHAR(100) NOT NULL, category VARCHAR(30) NOT NULL,
  price DECIMAL(10,2) NOT NULL, supplier VARCHAR(60) NOT NULL
);
CREATE TABLE customers (
  id INT PRIMARY KEY, name VARCHAR(100) NOT NULL, country CHAR(2) NOT NULL, created_at DATE NOT NULL
);
CREATE TABLE orders (
  id INT PRIMARY KEY, customer_id INT NOT NULL REFERENCES customers(id),
  order_date DATE NOT NULL, status VARCHAR(20) NOT NULL
);
CREATE TABLE order_items (
  id INT PRIMARY KEY, order_id INT NOT NULL REFERENCES orders(id),
  product_id INT NOT NULL REFERENCES products(id),
  quantity INT NOT NULL, unit_price DECIMAL(10,2) NOT NULL
);
CREATE TABLE complaints (
  id INT PRIMARY KEY, order_id INT NOT NULL REFERENCES orders(id),
  product_id INT NOT NULL REFERENCES products(id),
  type VARCHAR(20) NOT NULL, reason_category VARCHAR(40) NOT NULL,
  created_at DATE NOT NULL, resolved_at DATE, decision VARCHAR(20) NOT NULL,
  decision_source VARCHAR(10) NOT NULL
);

INSERT INTO products    SELECT * FROM CSVREAD('csv/products.csv',    NULL, 'charset=UTF-8');
INSERT INTO customers   SELECT * FROM CSVREAD('csv/customers.csv',   NULL, 'charset=UTF-8');
INSERT INTO orders      SELECT * FROM CSVREAD('csv/orders.csv',      NULL, 'charset=UTF-8');
INSERT INTO order_items SELECT * FROM CSVREAD('csv/order_items.csv', NULL, 'charset=UTF-8');
INSERT INTO complaints  SELECT * FROM CSVREAD('csv/complaints.csv',  NULL, 'charset=UTF-8');

SELECT 'products' AS tbl, COUNT(*) AS rows FROM products
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'complaints', COUNT(*) FROM complaints;
