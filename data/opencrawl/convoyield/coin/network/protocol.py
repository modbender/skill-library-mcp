"""
ConvoCoin Wire Protocol — Message format for node communication.

Every message between nodes follows this format:
    4 bytes:  message length (big-endian uint32)
    N bytes:  JSON-encoded message body

Message types (modeled after Bitcoin's P2P protocol):
    version    — Handshake: announce node capabilities
    verack     — Handshake acknowledgment
    ping/pong  — Keep-alive
    inv        — Announce new blocks/transactions
    getdata    — Request blocks/transactions
    block      — Send a complete block
    tx         — Send a transaction
    getblocks  — Request block headers from a height
    headers    — Send block headers
    addr       — Share known peer addresses
    getaddr    — Request peer addresses
    reject     — Reject a message with reason
"""

from __future__ import annotations

import json
import struct
import time
from dataclasses import dataclass, field, asdict
from enum import Enum


class MessageType(str, Enum):
    VERSION = "version"
    VERACK = "verack"
    PING = "ping"
    PONG = "pong"
    INV = "inv"
    GETDATA = "getdata"
    BLOCK = "block"
    TX = "tx"
    GETBLOCKS = "getblocks"
    HEADERS = "headers"
    ADDR = "addr"
    GETADDR = "getaddr"
    REJECT = "reject"
    YIELD_PROOF = "yield_proof"


class InvType(str, Enum):
    BLOCK = "block"
    TX = "tx"


@dataclass
class Message:
    """A wire protocol message."""

    msg_type: str
    payload: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    node_id: str = ""

    def serialize(self) -> bytes:
        """Serialize to wire format: length prefix + JSON body."""
        body = json.dumps({
            "type": self.msg_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
        }).encode("utf-8")

        length = struct.pack(">I", len(body))
        return length + body

    @staticmethod
    def deserialize(data: bytes) -> "Message":
        """Deserialize from wire format."""
        body = json.loads(data.decode("utf-8"))
        return Message(
            msg_type=body["type"],
            payload=body.get("payload", {}),
            timestamp=body.get("timestamp", time.time()),
            node_id=body.get("node_id", ""),
        )

    @staticmethod
    def read_length(data: bytes) -> int:
        """Read the message length prefix (first 4 bytes)."""
        if len(data) < 4:
            return 0
        return struct.unpack(">I", data[:4])[0]


# ── Message Factories ─────────────────────────────────────────────────────────

def msg_version(
    node_id: str,
    version: str,
    chain_height: int,
    best_hash: str,
) -> Message:
    """Create a version handshake message."""
    return Message(
        msg_type=MessageType.VERSION,
        node_id=node_id,
        payload={
            "version": version,
            "chain_height": chain_height,
            "best_hash": best_hash,
            "services": ["full_node", "miner"],
            "user_agent": "ConvoCoin/1.0.0",
        },
    )


def msg_verack(node_id: str) -> Message:
    return Message(msg_type=MessageType.VERACK, node_id=node_id)


def msg_ping(node_id: str) -> Message:
    return Message(
        msg_type=MessageType.PING,
        node_id=node_id,
        payload={"nonce": int(time.time() * 1000)},
    )


def msg_pong(node_id: str, nonce: int) -> Message:
    return Message(
        msg_type=MessageType.PONG,
        node_id=node_id,
        payload={"nonce": nonce},
    )


def msg_inv(node_id: str, inv_type: str, hashes: list[str]) -> Message:
    """Announce new blocks or transactions."""
    return Message(
        msg_type=MessageType.INV,
        node_id=node_id,
        payload={
            "type": inv_type,
            "hashes": hashes,
        },
    )


def msg_getdata(node_id: str, inv_type: str, hashes: list[str]) -> Message:
    """Request specific blocks or transactions."""
    return Message(
        msg_type=MessageType.GETDATA,
        node_id=node_id,
        payload={
            "type": inv_type,
            "hashes": hashes,
        },
    )


def msg_block(node_id: str, block_data: dict) -> Message:
    """Send a complete block."""
    return Message(
        msg_type=MessageType.BLOCK,
        node_id=node_id,
        payload={"block": block_data},
    )


def msg_tx(node_id: str, tx_data: dict) -> Message:
    """Send a transaction."""
    return Message(
        msg_type=MessageType.TX,
        node_id=node_id,
        payload={"transaction": tx_data},
    )


def msg_getblocks(node_id: str, from_height: int) -> Message:
    """Request blocks starting from a height."""
    return Message(
        msg_type=MessageType.GETBLOCKS,
        node_id=node_id,
        payload={"from_height": from_height},
    )


def msg_headers(node_id: str, headers: list[dict]) -> Message:
    """Send block headers."""
    return Message(
        msg_type=MessageType.HEADERS,
        node_id=node_id,
        payload={"headers": headers},
    )


def msg_addr(node_id: str, addresses: list[dict]) -> Message:
    """Share known peer addresses."""
    return Message(
        msg_type=MessageType.ADDR,
        node_id=node_id,
        payload={"addresses": addresses},
    )


def msg_getaddr(node_id: str) -> Message:
    return Message(msg_type=MessageType.GETADDR, node_id=node_id)


def msg_reject(node_id: str, rejected_type: str, reason: str) -> Message:
    return Message(
        msg_type=MessageType.REJECT,
        node_id=node_id,
        payload={"rejected": rejected_type, "reason": reason},
    )
