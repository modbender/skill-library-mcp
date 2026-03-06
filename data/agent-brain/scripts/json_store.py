"""JSON file storage backend for Agent Brain (legacy)."""

from __future__ import annotations

import json
import os
from store import MemoryStore

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


class JsonStore(MemoryStore):
    def __init__(self, json_path: str):
        self.path = json_path
        self._mem = None

    def _load(self):
        if self._mem is None:
            with open(self.path, "r") as f:
                self._mem = json.load(f)
        return self._mem

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self._mem, f, indent=2)

    def init(self):
        dir_path = os.path.dirname(self.path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        if os.path.exists(self.path):
            self._migrate()
            return
        self._mem = {
            "version": 4,
            "last_decay": None,
            "session_counter": 0,
            "current_session": None,
            "entries": [],
            "activity_log": []
        }
        self._save()

    def _migrate(self):
        mem = self._load()
        if mem.get("version", 1) >= 4:
            return
        mem["version"] = 4
        mem.setdefault("last_decay", None)
        mem.setdefault("session_counter", 0)
        mem.setdefault("current_session", None)
        for e in mem.get("entries", []):
            e.setdefault("context", None)
            e.setdefault("session_id", None)
            e.setdefault("success_count", 0)
            e.setdefault("correction_meta", None)
            if not e.get("memory_class"):
                e["memory_class"] = infer_memory_class(e.get("type", ""))
        mem.setdefault("activity_log", [])
        self._save()
        print("Migrated memory to v4")

    def close(self):
        self._mem = None

    def read_all(self) -> dict:
        mem = self._load()
        changed = False
        for e in mem.get("entries", []):
            if not e.get("memory_class"):
                e["memory_class"] = infer_memory_class(e.get("type", ""))
                changed = True
        if changed:
            self._save()
        return mem

    def get_active_entries(self, memory_classes: list[str] | None = None) -> list:
        mem = self._load()
        active = [e for e in mem["entries"] if not e.get("superseded_by")]
        for e in active:
            if not e.get("memory_class"):
                e["memory_class"] = infer_memory_class(e.get("type", ""))
        if memory_classes:
            classes = set(memory_classes)
            active = [e for e in active if e.get("memory_class") in classes]
        return active

    def get_entry(self, entry_id: str) -> dict | None:
        mem = self._load()
        for e in mem["entries"]:
            if e["id"] == entry_id:
                return e
        return None

    def add_entry(self, entry: dict) -> str:
        mem = self._load()
        if not entry.get("memory_class"):
            entry["memory_class"] = infer_memory_class(entry.get("type", ""))
        mem["entries"].append(entry)
        self._save()
        return entry["id"]

    def update_entry(self, entry_id: str, field: str, value):
        mem = self._load()
        for e in mem["entries"]:
            if e["id"] == entry_id:
                if field == "tags":
                    e["tags"] = [t.strip() for t in value.split(",") if t.strip()]
                elif field == "type":
                    e["type"] = value
                    e["memory_class"] = infer_memory_class(value)
                else:
                    e[field] = value
                self._save()
                return
        raise KeyError(f"Entry not found: {entry_id}")

    def touch_entry(self, entry_id: str, timestamp: str):
        mem = self._load()
        for e in mem["entries"]:
            if e["id"] == entry_id:
                e["last_accessed"] = timestamp
                e["access_count"] = e.get("access_count", 0) + 1
                self._save()
                return
        raise KeyError(f"Entry not found: {entry_id}")

    def mark_superseded(self, old_id: str, new_id: str):
        mem = self._load()
        for e in mem["entries"]:
            if e["id"] == old_id:
                e["superseded_by"] = new_id
                self._save()
                return
        raise KeyError(f"Entry not found: {old_id}")

    def increment_success(self, entry_id: str, timestamp: str) -> dict:
        mem = self._load()
        for e in mem["entries"]:
            if e["id"] == entry_id:
                e["access_count"] = e.get("access_count", 0) + 1
                e["last_accessed"] = timestamp
                e["success_count"] = e.get("success_count", 0) + 1
                self._save()
                return dict(e)
        raise KeyError(f"Entry not found: {entry_id}")

    def get_meta(self, key: str) -> str | None:
        mem = self._load()
        return mem.get(key)

    def set_meta(self, key: str, value: str):
        mem = self._load()
        mem[key] = value
        self._save()

    def get_session(self) -> dict | None:
        mem = self._load()
        return mem.get("current_session")

    def start_session(self, session_id: int, context: str | None, timestamp: str):
        mem = self._load()
        mem["current_session"] = {
            "id": session_id,
            "context": context,
            "started": timestamp
        }
        self._save()

    def get_session_counter(self) -> int:
        mem = self._load()
        return mem.get("session_counter", 0)

    def set_session_counter(self, value: int):
        mem = self._load()
        mem["session_counter"] = value
        self._save()

    def run_decay(self, now_str: str, decay_fn) -> int:
        mem = self._load()
        decayed = 0
        for e in mem["entries"]:
            if e.get("superseded_by"):
                continue
            new_conf = decay_fn(e, now_str)
            if new_conf is not None:
                e["confidence"] = new_conf
                decayed += 1
        mem["last_decay"] = now_str
        self._save()
        return decayed

    def export_json(self) -> str:
        mem = self._load()
        return json.dumps(mem, indent=2)

    def log_activity(self, timestamp: str, action: str, entry_id: str | None, detail: str):
        mem = self._load()
        mem.setdefault("activity_log", []).append({
            "timestamp": timestamp,
            "action": action,
            "entry_id": entry_id,
            "detail": detail
        })
        self._save()

    def get_log(self, limit: int = 50, action: str | None = None) -> list:
        mem = self._load()
        logs = mem.get("activity_log", [])
        if action:
            logs = [l for l in logs if l["action"] == action]
        return list(reversed(logs[-limit:]))

    def bulk_touch(self, entry_ids: set, timestamp: str):
        """Touch multiple entries at once (JSON-specific optimization)."""
        mem = self._load()
        for e in mem["entries"]:
            if e["id"] in entry_ids:
                e["last_accessed"] = timestamp
                e["access_count"] = e.get("access_count", 0) + 1
        self._save()
