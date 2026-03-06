"""SQLite storage backend for Agent Brain (default)."""

from __future__ import annotations

import json
import os
import sqlite3
from store import MemoryStore

SCHEMA_VERSION = 4

TYPE_TO_MEMORY_CLASS = {
    "fact": "semantic",
    "ingested": "semantic",
    "preference": "preference",
    "procedure": "procedural",
    "pattern": "procedural",
    "anti-pattern": "procedural",
    "correction": "episodic",
    "policy": "policy",
}


def infer_memory_class(entry_type: str) -> str:
    return TYPE_TO_MEMORY_CLASS.get(entry_type, "semantic")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    memory_class TEXT NOT NULL DEFAULT 'semantic',
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    source_url TEXT,
    tags TEXT,
    context TEXT,
    session_id INTEGER,
    created TEXT NOT NULL,
    last_accessed TEXT NOT NULL,
    access_count INTEGER DEFAULT 1,
    confidence TEXT DEFAULT 'likely',
    superseded_by TEXT,
    success_count INTEGER DEFAULT 0,
    correction_meta TEXT
);

CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type);
CREATE INDEX IF NOT EXISTS idx_entries_confidence ON entries(confidence);
CREATE INDEX IF NOT EXISTS idx_entries_superseded ON entries(superseded_by);
CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created);
CREATE INDEX IF NOT EXISTS idx_entries_session ON entries(session_id);
CREATE INDEX IF NOT EXISTS idx_entries_memory_class ON entries(memory_class);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action TEXT NOT NULL,
    entry_id TEXT,
    detail TEXT
);

CREATE INDEX IF NOT EXISTS idx_log_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_log_action ON activity_log(action);
"""


class SQLiteStore(MemoryStore):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def _connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys=ON")
        return self.conn

    def _row_to_dict(self, row) -> dict:
        d = dict(row)
        if not d.get("memory_class"):
            d["memory_class"] = infer_memory_class(d.get("type", ""))
        # Parse tags from comma-separated string to list
        d["tags"] = [t.strip() for t in (d["tags"] or "").split(",") if t.strip()]
        # Parse correction_meta from JSON string
        if d["correction_meta"]:
            d["correction_meta"] = json.loads(d["correction_meta"])
        return d

    def init(self):
        dir_path = os.path.dirname(self.db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Check for JSON migration opportunity
        json_path = os.path.join(os.path.dirname(self.db_path), "memory.json")
        needs_json_migration = (
            not os.path.exists(self.db_path)
            and os.path.exists(json_path)
        )

        conn = self._connect()
        conn.executescript(SCHEMA_SQL)

        # Initialize/repair required meta keys.
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
            ("version", str(SCHEMA_VERSION)),
        )
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
            ("last_decay", ""),
        )
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
            ("session_counter", "0"),
        )
        conn.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
            ("current_session", ""),
        )

        self._migrate_schema_if_needed()
        conn.commit()

        if needs_json_migration:
            self._migrate_from_json(json_path)

    def _migrate_schema_if_needed(self):
        conn = self._connect()
        row = conn.execute("SELECT value FROM meta WHERE key = 'version'").fetchone()
        try:
            version = int(row["value"]) if row and row["value"] else 0
        except (TypeError, ValueError):
            version = 0

        cols = {r["name"] for r in conn.execute("PRAGMA table_info(entries)").fetchall()}
        if "memory_class" not in cols:
            conn.execute("ALTER TABLE entries ADD COLUMN memory_class TEXT")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_entries_memory_class ON entries(memory_class)"
            )

        # Backfill memory class on old rows.
        for entry_type, mem_class in TYPE_TO_MEMORY_CLASS.items():
            conn.execute(
                """UPDATE entries
                   SET memory_class = ?
                   WHERE type = ? AND (memory_class IS NULL OR memory_class = '')""",
                (mem_class, entry_type),
            )
        conn.execute(
            "UPDATE entries SET memory_class = 'semantic' WHERE memory_class IS NULL OR memory_class = ''"
        )

        if version < SCHEMA_VERSION:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES ('version', ?)",
                (str(SCHEMA_VERSION),),
            )

    def _migrate_from_json(self, json_path: str):
        """Import data from memory.json into SQLite."""
        with open(json_path, "r") as f:
            mem = json.load(f)

        conn = self._connect()
        count = 0
        for e in mem.get("entries", []):
            tags_str = ",".join(e.get("tags", []))
            correction_meta = json.dumps(e["correction_meta"]) if e.get("correction_meta") else None
            memory_class = e.get("memory_class") or infer_memory_class(e.get("type", ""))
            conn.execute(
                """INSERT OR IGNORE INTO entries
                   (id, type, memory_class, content, source, source_url, tags, context, session_id,
                    created, last_accessed, access_count, confidence, superseded_by,
                    success_count, correction_meta)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (e["id"], e["type"], memory_class, e["content"], e["source"], e.get("source_url"),
                 tags_str, e.get("context"), e.get("session_id"),
                 e["created"], e["last_accessed"], e.get("access_count", 1),
                 e.get("confidence", "likely"), e.get("superseded_by"),
                 e.get("success_count", 0), correction_meta)
            )
            count += 1

        # Import meta
        if mem.get("last_decay"):
            conn.execute("UPDATE meta SET value = ? WHERE key = 'last_decay'",
                         (mem["last_decay"],))
        if mem.get("session_counter"):
            conn.execute("UPDATE meta SET value = ? WHERE key = 'session_counter'",
                         (str(mem["session_counter"]),))
        if mem.get("current_session"):
            conn.execute("UPDATE meta SET value = ? WHERE key = 'current_session'",
                         (json.dumps(mem["current_session"]),))

        conn.commit()

        # Backup the old JSON file
        backup_path = json_path + ".bak"
        os.rename(json_path, backup_path)
        print(f"Migrated {count} entries from JSON to SQLite")
        print(f"  Backed up: {backup_path}")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def read_all(self) -> dict:
        conn = self._connect()
        entries = []
        for row in conn.execute("SELECT * FROM entries ORDER BY created"):
            entries.append(self._row_to_dict(row))

        meta = {}
        for row in conn.execute("SELECT key, value FROM meta"):
            meta[row["key"]] = row["value"]

        session = None
        if meta.get("current_session"):
            try:
                session = json.loads(meta["current_session"])
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "version": int(meta.get("version", SCHEMA_VERSION)),
            "last_decay": meta.get("last_decay") or None,
            "session_counter": int(meta.get("session_counter", 0)),
            "current_session": session,
            "entries": entries
        }

    def get_active_entries(self, memory_classes: list[str] | None = None) -> list:
        conn = self._connect()
        if memory_classes:
            placeholders = ",".join(["?"] * len(memory_classes))
            rows = conn.execute(
                f"""SELECT * FROM entries
                    WHERE superseded_by IS NULL AND memory_class IN ({placeholders})
                    ORDER BY created""",
                tuple(memory_classes),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM entries WHERE superseded_by IS NULL ORDER BY created"
            ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_entry(self, entry_id: str) -> dict | None:
        conn = self._connect()
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return self._row_to_dict(row) if row else None

    def add_entry(self, entry: dict) -> str:
        conn = self._connect()
        tags_str = ",".join(entry.get("tags", []))
        correction_meta = json.dumps(entry["correction_meta"]) if entry.get("correction_meta") else None
        memory_class = entry.get("memory_class") or infer_memory_class(entry.get("type", ""))
        conn.execute(
            """INSERT INTO entries
               (id, type, memory_class, content, source, source_url, tags, context, session_id,
                created, last_accessed, access_count, confidence, superseded_by,
                success_count, correction_meta)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (entry["id"], entry["type"], memory_class, entry["content"], entry["source"],
             entry.get("source_url"), tags_str, entry.get("context"),
             entry.get("session_id"), entry["created"], entry["last_accessed"],
             entry.get("access_count", 1), entry.get("confidence", "likely"),
             entry.get("superseded_by"), entry.get("success_count", 0),
             correction_meta)
        )
        conn.commit()
        return entry["id"]

    _UPDATABLE_FIELDS = {"confidence", "tags", "content", "type", "context", "memory_class"}

    def update_entry(self, entry_id: str, field: str, value):
        if field not in self._UPDATABLE_FIELDS:
            raise ValueError(f"Cannot update field '{field}'. Allowed: {', '.join(sorted(self._UPDATABLE_FIELDS))}")
        conn = self._connect()
        if field == "tags":
            value = ",".join(t.strip() for t in value.split(",") if t.strip())
        if field == "type":
            result = conn.execute(
                "UPDATE entries SET type = ?, memory_class = ? WHERE id = ?",
                (value, infer_memory_class(value), entry_id),
            )
        else:
            result = conn.execute(
                f"UPDATE entries SET {field} = ? WHERE id = ?", (value, entry_id)
            )
        conn.commit()
        if result.rowcount == 0:
            raise KeyError(f"Entry not found: {entry_id}")

    def touch_entry(self, entry_id: str, timestamp: str):
        conn = self._connect()
        result = conn.execute(
            "UPDATE entries SET last_accessed = ?, access_count = access_count + 1 WHERE id = ?",
            (timestamp, entry_id)
        )
        conn.commit()
        if result.rowcount == 0:
            raise KeyError(f"Entry not found: {entry_id}")

    def mark_superseded(self, old_id: str, new_id: str):
        conn = self._connect()
        result = conn.execute(
            "UPDATE entries SET superseded_by = ? WHERE id = ?", (new_id, old_id)
        )
        conn.commit()
        if result.rowcount == 0:
            raise KeyError(f"Entry not found: {old_id}")

    def increment_success(self, entry_id: str, timestamp: str) -> dict:
        conn = self._connect()
        result = conn.execute(
            """UPDATE entries
               SET success_count = success_count + 1,
                   access_count = access_count + 1,
                   last_accessed = ?
               WHERE id = ?""",
            (timestamp, entry_id)
        )
        conn.commit()
        if result.rowcount == 0:
            raise KeyError(f"Entry not found: {entry_id}")
        return self.get_entry(entry_id)

    def get_meta(self, key: str) -> str | None:
        conn = self._connect()
        row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        return row["value"] if row["value"] else None

    def set_meta(self, key: str, value: str):
        conn = self._connect()
        conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, value)
        )
        conn.commit()

    def get_session(self) -> dict | None:
        raw = self.get_meta("current_session")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

    def start_session(self, session_id: int, context: str | None, timestamp: str):
        session = {"id": session_id, "context": context, "started": timestamp}
        self.set_meta("current_session", json.dumps(session))

    def get_session_counter(self) -> int:
        raw = self.get_meta("session_counter")
        return int(raw) if raw else 0

    def set_session_counter(self, value: int):
        self.set_meta("session_counter", str(value))

    def run_decay(self, now_str: str, decay_fn) -> int:
        conn = self._connect()
        rows = conn.execute(
            "SELECT * FROM entries WHERE superseded_by IS NULL"
        ).fetchall()
        decayed = 0
        for row in rows:
            entry = self._row_to_dict(row)
            new_conf = decay_fn(entry, now_str)
            if new_conf is not None:
                conn.execute("UPDATE entries SET confidence = ? WHERE id = ?",
                             (new_conf, entry["id"]))
                decayed += 1
        self.set_meta("last_decay", now_str)
        conn.commit()
        return decayed

    def export_json(self) -> str:
        return json.dumps(self.read_all(), indent=2)

    def log_activity(self, timestamp: str, action: str, entry_id: str | None, detail: str):
        conn = self._connect()
        conn.execute(
            "INSERT INTO activity_log (timestamp, action, entry_id, detail) VALUES (?, ?, ?, ?)",
            (timestamp, action, entry_id, detail)
        )
        conn.commit()

    def get_log(self, limit: int = 50, action: str | None = None) -> list:
        conn = self._connect()
        if action:
            rows = conn.execute(
                "SELECT * FROM activity_log WHERE action = ? ORDER BY id DESC LIMIT ?",
                (action, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM activity_log ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def bulk_touch(self, entry_ids: set, timestamp: str):
        """Touch multiple entries at once."""
        conn = self._connect()
        for eid in entry_ids:
            conn.execute(
                "UPDATE entries SET last_accessed = ?, access_count = access_count + 1 WHERE id = ?",
                (timestamp, eid)
            )
        conn.commit()
