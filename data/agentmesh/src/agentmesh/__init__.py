"""
AgentMesh
━━━━━━━━━
WhatsApp-style encrypted messaging for AI agents.

Quick start
-----------
>>> from agentmesh import Agent, LocalHub
>>> hub = LocalHub()
>>> alice = Agent("alice", hub=hub)
>>> bob   = Agent("bob",   hub=hub)
>>> bob.on_message(lambda msg: print(f"[bob] ← {msg.sender}: {msg.text}"))
>>> alice.send("bob", text="Hello, Bob!")

GitHub: https://github.com/cerbug45/AgentMesh
"""

from .agent import Agent, Message
from .hub import LocalHub, NetworkHub, NetworkHubServer
from .crypto import (
    AgentKeyPair,
    CryptoSession,
    CryptoError,
    perform_key_exchange,
    seal,
    unseal,
)

__version__ = "1.0.0"
__author__ = "cerbug45"
__license__ = "MIT"

__all__ = [
    # High-level
    "Agent",
    "Message",
    "LocalHub",
    "NetworkHub",
    "NetworkHubServer",
    # Crypto primitives (for advanced use)
    "AgentKeyPair",
    "CryptoSession",
    "CryptoError",
    "perform_key_exchange",
    "seal",
    "unseal",
]
