"""In-process memory and session management for the voice-agent bridge.

Stores caller sessions, long-term memory (facts), and daily notes as JSON
files under ``DATA_DIR``.  All functions are synchronous and file-backed so
the bridge can run without an external database.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATA_DIR: Path = Path(os.getenv("DATA_DIR", "./data"))


# ── Type definitions ────────────────────────────────────────────────────────


class Session(TypedDict, total=False):
    """Represents a single caller session."""

    session_id: str
    phone_hash: str
    caller_name: str
    call_count: int
    first_seen: float
    last_seen: float
    last_call_sid: str
    active: bool


class MemoryStore(TypedDict, total=False):
    """Long-term facts stored per caller."""

    phone_hash: str
    facts: list[str]


class Note(TypedDict):
    """A daily / global context note."""

    timestamp: float
    note: str
    phone_hash: str | None


# ── Helpers ─────────────────────────────────────────────────────────────────


def _sessions_path() -> Path:
    """Return the path to the sessions JSON file."""
    return DATA_DIR / "sessions.json"


def _memories_path() -> Path:
    """Return the path to the memories JSON file."""
    return DATA_DIR / "memories.json"


def _notes_path() -> Path:
    """Return the path to the notes JSON file."""
    return DATA_DIR / "notes.json"


def _read_json(path: Path) -> dict | list:
    """Read and return parsed JSON from *path*, or an empty dict on failure."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read %s: %s", path, exc)
        return {}


def _write_json(path: Path, data: dict | list) -> None:
    """Atomically write *data* as JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
    except OSError as exc:
        logger.error("Failed to write %s: %s", path, exc)


# ── Public API ──────────────────────────────────────────────────────────────


def ensure_data_dir() -> None:
    """Create the data directory tree if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Data directory ready: %s", DATA_DIR.resolve())


def load_session(phone_hash: str) -> Session:
    """Load an existing session or create a new one for *phone_hash*.

    Returns a ``Session`` dict.  The ``call_count`` is incremented each time
    this function is called (i.e., per inbound call).
    """
    sessions: dict[str, Session] = _read_json(_sessions_path())  # type: ignore[assignment]
    now = time.time()

    if phone_hash in sessions:
        session = sessions[phone_hash]
        session["call_count"] = session.get("call_count", 0) + 1
        session["last_seen"] = now
        session["active"] = True
        logger.info(
            "Returning caller %s — call #%d",
            phone_hash[:8],
            session["call_count"],
        )
    else:
        session = Session(
            session_id=f"{phone_hash[:12]}_{int(now)}",
            phone_hash=phone_hash,
            caller_name="",
            call_count=1,
            first_seen=now,
            last_seen=now,
            last_call_sid="",
            active=True,
        )
        logger.info("New caller %s", phone_hash[:8])

    sessions[phone_hash] = session
    _write_json(_sessions_path(), sessions)
    return session


def end_session(phone_hash: str, call_sid: str) -> None:
    """Mark the session for *phone_hash* as inactive after a call ends."""
    sessions: dict[str, Session] = _read_json(_sessions_path())  # type: ignore[assignment]
    if phone_hash in sessions:
        sessions[phone_hash]["active"] = False
        sessions[phone_hash]["last_call_sid"] = call_sid
        _write_json(_sessions_path(), sessions)


def get_memories(phone_hash: str) -> list[str]:
    """Return the list of stored facts for *phone_hash*."""
    memories: dict[str, MemoryStore] = _read_json(_memories_path())  # type: ignore[assignment]
    store = memories.get(phone_hash, {})
    return store.get("facts", [])


def add_memory(phone_hash: str, fact: str) -> list[str]:
    """Append *fact* to long-term memory for *phone_hash*.

    Returns the updated list of facts.
    """
    memories: dict[str, MemoryStore] = _read_json(_memories_path())  # type: ignore[assignment]
    if phone_hash not in memories:
        memories[phone_hash] = MemoryStore(phone_hash=phone_hash, facts=[])
    memories[phone_hash].setdefault("facts", []).append(fact)
    _write_json(_memories_path(), memories)
    logger.info("Stored fact for %s (total: %d)", phone_hash[:8], len(memories[phone_hash]["facts"]))
    return memories[phone_hash]["facts"]


def get_notes(phone_hash: str | None = None) -> list[Note]:
    """Return notes, optionally filtered by *phone_hash*.

    Global notes (``phone_hash is None``) are always included.
    """
    all_notes: list[Note] = _read_json(_notes_path()) or []  # type: ignore[assignment]
    return [
        n
        for n in all_notes
        if n.get("phone_hash") is None or n.get("phone_hash") == phone_hash
    ]


def add_note(note: str, phone_hash: str | None = None) -> Note:
    """Create a new note and persist it.

    If *phone_hash* is provided the note is scoped to that caller; otherwise
    it is a global/daily note visible to all callers.
    """
    all_notes: list[Note] = _read_json(_notes_path()) or []  # type: ignore[assignment]
    entry = Note(timestamp=time.time(), note=note, phone_hash=phone_hash)
    all_notes.append(entry)
    _write_json(_notes_path(), all_notes)
    logger.info("Added note (global=%s)", phone_hash is None)
    return entry
