CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  source TEXT DEFAULT 'generic',
  target_price REAL,
  current_price REAL,
  currency TEXT DEFAULT 'USD',
  last_checked TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_products_source ON products(source);

CREATE TABLE IF NOT EXISTS price_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT REFERENCES products(id),
  price REAL NOT NULL,
  currency TEXT DEFAULT 'USD',
  timestamp TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp);

CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  status TEXT DEFAULT 'ordered' CHECK(status IN ('ordered','shipped','delivered','cancelled')),
  tracking_number TEXT,
  carrier TEXT,
  shipped_date TEXT,
  eta TEXT,
  notes TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE TABLE IF NOT EXISTS alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id TEXT REFERENCES products(id),
  type TEXT CHECK(type IN ('below_target','price_drop','back_in_stock')),
  threshold REAL,
  triggered_at TEXT,
  acknowledged INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_alerts_product_id ON alerts(product_id);

CREATE TABLE IF NOT EXISTS circuit_breaker_state (
  source TEXT PRIMARY KEY,
  state TEXT DEFAULT 'closed' CHECK(state IN ('closed','open','half-open')),
  failure_count INTEGER DEFAULT 0,
  last_failure TEXT,
  cooldown_until TEXT
);

CREATE TABLE IF NOT EXISTS _migrations (
  version INTEGER PRIMARY KEY,
  name TEXT,
  applied_at TEXT,
  checksum TEXT
);

-- Migration runner handles version tracking