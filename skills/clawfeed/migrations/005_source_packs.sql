CREATE TABLE IF NOT EXISTS source_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  slug TEXT UNIQUE,
  sources_json TEXT NOT NULL,
  created_by INTEGER REFERENCES users(id),
  is_public INTEGER DEFAULT 1,
  install_count INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);
