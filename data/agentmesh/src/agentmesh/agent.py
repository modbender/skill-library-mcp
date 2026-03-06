"""
AgentMesh – Agent
━━━━━━━━━━━━━━━━━
A self-contained AI agent identity that can:
  • Register to a Hub (broker) or run peer-to-peer
  • Establish encrypted sessions with other agents
  • Send / receive signed + encrypted messages
  • Auto-discover peers via the Hub
  • Persist its key-pair across restarts
"""

from __future__ import annotations

import json
import time
import threading
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any

from .crypto import (
    AgentKeyPair,
    CryptoSession,
    CryptoError,
    perform_key_exchange,
    seal,
    unseal,
)
from .transport import Transport, LocalTransport

logger = logging.getLogger("agentmesh.agent")


# ──────────────────────────────────────────────────────────────────────────────
# Message model
# ──────────────────────────────────────────────────────────────────────────────

class Message:
    """A decrypted, verified message received from a peer agent."""

    __slots__ = ("sender", "recipient", "payload", "timestamp", "raw_envelope")

    def __init__(
        self,
        sender: str,
        recipient: str,
        payload: dict,
        timestamp: int,
        raw_envelope: dict,
    ):
        self.sender = sender
        self.recipient = recipient
        self.payload = payload
        self.timestamp = timestamp
        self.raw_envelope = raw_envelope

    def __repr__(self) -> str:
        return (
            f"Message(from={self.sender!r}, to={self.recipient!r}, "
            f"payload={self.payload!r})"
        )

    @property
    def text(self) -> Optional[str]:
        """Convenience accessor for 'text' key in payload."""
        return self.payload.get("text")

    @property
    def type(self) -> str:
        """Convenience accessor for 'type' key in payload (default: 'message')."""
        return self.payload.get("type", "message")


# ──────────────────────────────────────────────────────────────────────────────
# Agent
# ──────────────────────────────────────────────────────────────────────────────

class Agent:
    """
    An AI agent with a cryptographic identity.
    """

    def __init__(
        self,
        agent_id: str,
        hub=None,
        keypair_path: Optional[str | Path] = None,
        log_level: int = logging.WARNING,
    ):
        self.id = agent_id
        self._hub = hub
        self._sessions: Dict[str, CryptoSession] = {}
        self._peer_bundles: Dict[str, dict] = {}
        self._handlers: List[Callable[[Message], Any]] = []
        self._lock = threading.Lock()

        logging.getLogger("agentmesh").setLevel(log_level)

        if keypair_path:
            self._keypair = _load_or_create_keypair(Path(keypair_path))
        else:
            self._keypair = AgentKeyPair()

        if self._hub is not None:
            self._hub.register(self)

    @property
    def public_bundle(self) -> dict:
        bundle = self._keypair.public_bundle()
        bundle["agent_id"] = self.id
        return bundle

    @property
    def fingerprint(self) -> str:
        return self._keypair.fingerprint

    def connect(self, peer_id: str) -> None:
        if self._hub is None:
            raise RuntimeError("No hub configured")

        bundle = self._hub.get_bundle(peer_id)
        if bundle is None:
            raise ValueError(f"Peer {peer_id!r} not found")

        with self._lock:
            self._peer_bundles[peer_id] = bundle
            self._sessions[peer_id] = perform_key_exchange(self._keypair, bundle)

    def _ensure_session(self, peer_id: str) -> CryptoSession:
        if peer_id not in self._sessions:
            self.connect(peer_id)
        return self._sessions[peer_id]

    def send(self, recipient_id: str, *, text: str = "", **extra) -> None:
        payload: dict = {"type": "message", "text": text}
        payload.update(extra)
        self.send_payload(recipient_id, payload)

    def send_payload(self, recipient_id: str, payload: dict) -> None:
        session = self._ensure_session(recipient_id)
        envelope = seal(session, self._keypair, self.id, recipient_id, payload)
        if self._hub is not None:
            self._hub.deliver(envelope)

    def _receive(self, envelope: dict) -> None:
        sender_id = envelope.get("from", "")
        try:
            with self._lock:
                sender_bundle = self._peer_bundles.get(sender_id)
                if sender_bundle is None:
                    if self._hub is not None:
                        sender_bundle = self._hub.get_bundle(sender_id)
                        if sender_bundle:
                            self._peer_bundles[sender_id] = sender_bundle
                            self._sessions[sender_id] = perform_key_exchange(
                                self._keypair, sender_bundle
                            )
                if sender_bundle is None:
                    raise CryptoError(f"Unknown sender: {sender_id!r}")
                session = self._sessions[sender_id]

            payload = unseal(session, envelope, sender_bundle)
            msg = Message(
                sender=sender_id,
                recipient=envelope.get("to", self.id),
                payload=payload,
                timestamp=envelope.get("ts", 0),
                raw_envelope=envelope,
            )
            self._dispatch(msg)
        except Exception as exc:
            logger.error("Receive error: %s", exc)

    def _dispatch(self, msg: Message) -> None:
        for handler in self._handlers:
            try:
                handler(msg)
            except Exception as exc:
                logger.error("Handler error: %s", exc)

    def on_message(self, handler: Callable[[Message], Any]) -> "Agent":
        self._handlers.append(handler)
        return self

    def list_peers(self) -> List[str]:
        if self._hub is None: return []
        return [p for p in self._hub.list_agents() if p != self.id]


def _load_or_create_keypair(path: Path) -> AgentKeyPair:
    if path.exists():
        with path.open() as fh:
            data = json.load(fh)
        return AgentKeyPair.from_dict(data)
    kp = AgentKeyPair()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(kp.to_dict(), fh, indent=2)
    return kp
