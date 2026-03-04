import json
import sqlite3
import time
from typing import Optional, Any, Dict
from config import CACHE_DB_PATH

def _conn():
    c = sqlite3.connect(CACHE_DB_PATH)
    c.execute("""
    CREATE TABLE IF NOT EXISTS cache (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL,
      expires_at INTEGER NOT NULL
    )
    """)
    return c

def get(key: str) -> Optional[Dict[str, Any]]:
    now = int(time.time())
    with _conn() as c:
        row = c.execute("SELECT value, expires_at FROM cache WHERE key=?", (key,)).fetchone()
        if not row:
            return None
        value, expires_at = row
        if expires_at < now:
            c.execute("DELETE FROM cache WHERE key=?", (key,))
            return None
        return json.loads(value)

def set(key: str, value: Dict[str, Any], ttl_sec: int):
    expires_at = int(time.time()) + ttl_sec
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO cache(key,value,expires_at) VALUES(?,?,?)",
            (key, json.dumps(value, ensure_ascii=False), expires_at)
        )
