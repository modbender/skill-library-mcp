"""Conversations — track multi-turn agent interactions.

Prevents duplicate contacts, enables follow-ups, detects stale threads.
Conversation IDs are deterministic: same pair + topic always yields the same ID.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .storage import _dir


CONVERSATIONS_FILE = "conversations.jsonl"
DEFAULT_STALE_S = 604800  # 7 days


def _conv_id(agent_a: str, agent_b: str, topic: str) -> str:
    """Deterministic conversation ID from sorted agent pair + topic."""
    pair = "|".join(sorted([agent_a, agent_b]))
    raw = f"{pair}|{topic}"
    return "conv_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]


class ConversationManager:
    """Track multi-turn agent interactions."""

    def __init__(self, data_dir: Optional[Path] = None, my_agent_id: str = ""):
        self._dir = data_dir or _dir()
        self._my_id = my_agent_id
        self._conversations: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _conv_path(self) -> Path:
        return self._dir / CONVERSATIONS_FILE

    def _load(self) -> None:
        """Rebuild conversation state from event log."""
        path = self._conv_path()
        if not path.exists():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except Exception:
                continue
            cid = event.get("conversation_id", "")
            if not cid:
                continue
            etype = event.get("event_type", "")
            if etype == "create":
                self._conversations[cid] = {
                    "conversation_id": cid,
                    "my_agent_id": event.get("my_agent_id", ""),
                    "their_agent_id": event.get("their_agent_id", ""),
                    "topic_key": event.get("topic_key", "general"),
                    "state": "initiated",
                    "messages": 0,
                    "last_message_ts": event.get("ts", 0),
                    "last_direction": "",
                    "created_at": event.get("ts", 0),
                }
            elif etype == "message" and cid in self._conversations:
                c = self._conversations[cid]
                c["messages"] = c.get("messages", 0) + 1
                c["last_message_ts"] = event.get("ts", 0)
                c["last_direction"] = event.get("direction", "")
                if c["state"] == "initiated":
                    c["state"] = "active"
            elif etype == "complete" and cid in self._conversations:
                self._conversations[cid]["state"] = "completed"
            elif etype == "stale" and cid in self._conversations:
                self._conversations[cid]["state"] = "stale"

    def _append(self, event: Dict[str, Any]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        with self._conv_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    def get_or_create(self, their_agent_id: str, topic_key: str = "general") -> Dict[str, Any]:
        """Get existing or create new conversation for this agent+topic pair."""
        cid = _conv_id(self._my_id, their_agent_id, topic_key)
        if cid in self._conversations:
            return dict(self._conversations[cid])
        now = int(time.time())
        conv = {
            "conversation_id": cid,
            "my_agent_id": self._my_id,
            "their_agent_id": their_agent_id,
            "topic_key": topic_key,
            "state": "initiated",
            "messages": 0,
            "last_message_ts": now,
            "last_direction": "",
            "created_at": now,
        }
        self._conversations[cid] = conv
        self._append({
            "event_type": "create",
            "conversation_id": cid,
            "my_agent_id": self._my_id,
            "their_agent_id": their_agent_id,
            "topic_key": topic_key,
            "ts": now,
        })
        return dict(conv)

    def record_message(self, conversation_id: str, direction: str, kind: str = "") -> None:
        """Record a message in a conversation."""
        if conversation_id not in self._conversations:
            return
        now = int(time.time())
        c = self._conversations[conversation_id]
        c["messages"] = c.get("messages", 0) + 1
        c["last_message_ts"] = now
        c["last_direction"] = direction
        if c["state"] == "initiated":
            c["state"] = "active"
        self._append({
            "event_type": "message",
            "conversation_id": conversation_id,
            "direction": direction,
            "kind": kind,
            "ts": now,
        })

    def find_by_agent(self, their_agent_id: str) -> List[Dict[str, Any]]:
        """Find all conversations with a specific agent."""
        return [
            dict(c) for c in self._conversations.values()
            if c.get("their_agent_id") == their_agent_id
        ]

    def find_by_topic(self, topic_key: str) -> Optional[Dict[str, Any]]:
        """Find a conversation by topic key (returns first match)."""
        for c in self._conversations.values():
            if c.get("topic_key") == topic_key:
                return dict(c)
        return None

    def is_waiting_for_reply(self, their_agent_id: str, topic_key: str = "general") -> bool:
        """Check if we already sent a message and are waiting for their reply."""
        cid = _conv_id(self._my_id, their_agent_id, topic_key)
        conv = self._conversations.get(cid)
        if not conv:
            return False
        return conv.get("last_direction") == "out" and conv.get("state") in ("initiated", "active")

    def should_follow_up(self, conversation_id: str, timeout_s: int = 86400) -> bool:
        """Check if a conversation is overdue for a follow-up (no reply within timeout)."""
        conv = self._conversations.get(conversation_id)
        if not conv:
            return False
        if conv.get("state") not in ("initiated", "active"):
            return False
        if conv.get("last_direction") != "out":
            return False
        age = int(time.time()) - conv.get("last_message_ts", 0)
        return age >= timeout_s

    def mark_completed(self, conversation_id: str) -> None:
        """Mark a conversation as completed."""
        if conversation_id in self._conversations:
            self._conversations[conversation_id]["state"] = "completed"
            self._append({
                "event_type": "complete",
                "conversation_id": conversation_id,
                "ts": int(time.time()),
            })

    def mark_stale(self, max_idle_s: int = DEFAULT_STALE_S) -> int:
        """Mark idle conversations as stale. Returns count marked."""
        now = int(time.time())
        count = 0
        for cid, conv in self._conversations.items():
            if conv.get("state") not in ("initiated", "active"):
                continue
            idle = now - conv.get("last_message_ts", 0)
            if idle >= max_idle_s:
                conv["state"] = "stale"
                self._append({
                    "event_type": "stale",
                    "conversation_id": cid,
                    "ts": now,
                })
                count += 1
        return count

    def active_conversations(self) -> List[Dict[str, Any]]:
        """Return all non-completed, non-stale conversations."""
        return [
            dict(c) for c in self._conversations.values()
            if c.get("state") in ("initiated", "active")
        ]
