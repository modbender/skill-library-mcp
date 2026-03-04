"""Inbound parsing: read, verify, filter, and track inbox entries."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .codec import decode_envelopes, verify_envelope
from .storage import _dir, read_state, write_state


KNOWN_KEYS_FILE = "known_keys.json"


def _known_keys_path() -> Path:
    return _dir() / KNOWN_KEYS_FILE


def load_known_keys() -> Dict[str, str]:
    """Load agent_id -> public_key_hex mapping from disk."""
    path = _known_keys_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_known_keys(keys: Dict[str, str]) -> None:
    """Save known keys to disk."""
    path = _known_keys_path()
    path.write_text(json.dumps(keys, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def trust_key(agent_id: str, pubkey_hex: str) -> None:
    """Add or update a trusted agent key."""
    keys = load_known_keys()
    keys[agent_id] = pubkey_hex
    save_known_keys(keys)


def _learn_key_from_envelope(env: Dict[str, Any], keys: Dict[str, str]) -> Dict[str, str]:
    """Auto-learn pubkey from v2 envelopes (trust on first use)."""
    agent_id = env.get("agent_id", "")
    pubkey = env.get("pubkey", "")
    if agent_id and pubkey and agent_id not in keys:
        from .identity import agent_id_from_pubkey
        expected = agent_id_from_pubkey(bytes.fromhex(pubkey))
        if expected == agent_id:
            keys[agent_id] = pubkey
    return keys


def _read_nonces() -> set:
    """Get set of already-read nonces from state."""
    state = read_state()
    return set(state.get("read_nonces", []))


def _save_read_nonce(nonce: str) -> None:
    """Mark a nonce as read."""
    state = read_state()
    nonces = set(state.get("read_nonces", []))
    nonces.add(nonce)
    # Keep bounded (last 10000 nonces).
    if len(nonces) > 10000:
        nonces = set(list(nonces)[-10000:])
    state["read_nonces"] = sorted(nonces)
    write_state(state)


def read_inbox(
    *,
    kind: Optional[str] = None,
    agent_id: Optional[str] = None,
    since: Optional[float] = None,
    unread_only: bool = False,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Read and filter inbox entries from inbox.jsonl.

    Each entry is enriched with:
      - verified: True/False/None (signature verification result)
      - is_read: bool (whether this nonce was marked read)
    """
    path = _dir() / "inbox.jsonl"
    if not path.exists():
        return []

    known_keys = load_known_keys()
    read_nonces = _read_nonces()
    results: List[Dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue

        # Extract envelopes from the entry.
        envelopes = entry.get("envelopes", [])
        if not envelopes and entry.get("text"):
            envelopes = decode_envelopes(entry["text"])

        # Process each envelope in the entry.
        for env in envelopes:
            # Auto-learn keys.
            _learn_key_from_envelope(env, known_keys)

            # Verify signature.
            verified = verify_envelope(env, known_keys=known_keys)
            nonce = env.get("nonce", "")
            is_read = nonce in read_nonces if nonce else False

            enriched = dict(entry)
            enriched["envelope"] = env
            enriched["verified"] = verified
            enriched["is_read"] = is_read

            # Apply filters.
            if kind and env.get("kind") != kind:
                continue
            if agent_id and env.get("agent_id") != agent_id:
                continue
            if since and entry.get("received_at", 0) < since:
                continue
            if unread_only and is_read:
                continue

            results.append(enriched)

        # If no envelopes, include the raw entry (e.g., plain text UDP).
        if not envelopes:
            enriched = dict(entry)
            enriched["envelope"] = None
            enriched["verified"] = None
            enriched["is_read"] = False

            if kind or agent_id:
                continue  # Can't filter raw entries by kind/agent_id.
            if since and entry.get("received_at", 0) < since:
                continue

            results.append(enriched)

    # Save any newly learned keys.
    save_known_keys(known_keys)

    if limit:
        results = results[-limit:]

    return results


def mark_read(nonce: str) -> None:
    """Mark an envelope nonce as read."""
    _save_read_nonce(nonce)


def inbox_count(unread_only: bool = False) -> int:
    """Return the count of inbox entries."""
    entries = read_inbox(unread_only=unread_only)
    return len(entries)


def get_entry_by_nonce(nonce: str) -> Optional[Dict[str, Any]]:
    """Find a specific inbox entry by its nonce."""
    entries = read_inbox()
    for entry in entries:
        env = entry.get("envelope")
        if env and env.get("nonce") == nonce:
            return entry
    return None
