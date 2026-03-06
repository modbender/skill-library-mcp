# Design: Hive Mind

**Role:** The "Shared Memory"
**Goal:** Persist small state (KV pairs) across agent sessions.

## 🏗 Architecture

1.  **DSN Management:** Stores the connection string in `~/.openclaw_hive_mind_dsn`.
    *   If file exists -> Reuse DB (Persistent).
    *   If missing -> Create new DB (30-day life).
2.  **Schema:** `user_prefs` table (Key, Value, UpdatedAt).
3.  **Operations:** `REPLACE INTO` for set, `SELECT` for get.

## ⚠️ Limitations
*   **30-Day TTL:** The DB expires after 30 days. For truly permanent storage, user must upgrade to TiDB Cloud Serverless (Free Tier).
