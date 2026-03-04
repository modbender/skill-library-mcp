CREATE TABLE IF NOT EXISTS vaults (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS vault_keys (
  id TEXT PRIMARY KEY,
  vault_id TEXT NOT NULL REFERENCES vaults(id),
  public_key TEXT NOT NULL,
  fingerprint TEXT NOT NULL,
  hostname TEXT NOT NULL DEFAULT '',
  instance_id TEXT NOT NULL DEFAULT '',
  registered_at TEXT DEFAULT (datetime('now')),
  revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS vault_versions (
  id TEXT PRIMARY KEY,
  vault_id TEXT NOT NULL REFERENCES vaults(id),
  s3_key TEXT NOT NULL,
  size_bytes INTEGER NOT NULL DEFAULT 0,
  hash_sha256 TEXT NOT NULL,
  pushed_by TEXT NOT NULL DEFAULT '',
  profile_name TEXT NOT NULL DEFAULT 'default',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_vault_keys_vault ON vault_keys(vault_id);
CREATE INDEX IF NOT EXISTS idx_vault_versions_vault ON vault_versions(vault_id);
CREATE INDEX IF NOT EXISTS idx_vault_versions_profile ON vault_versions(vault_id, profile_name);

CREATE TABLE IF NOT EXISTS sync_rules (
  id           TEXT PRIMARY KEY,
  vault_id     TEXT NOT NULL REFERENCES vaults(id),
  profile_name TEXT NOT NULL,
  path         TEXT NOT NULL,
  created_at   TEXT DEFAULT (datetime('now')),
  UNIQUE(vault_id, profile_name, path)
);
CREATE INDEX IF NOT EXISTS idx_sync_rules_profile ON sync_rules(vault_id, profile_name);
