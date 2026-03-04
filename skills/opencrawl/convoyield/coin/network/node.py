"""
ConvoCoin Node — A full peer-to-peer network node.

This is the equivalent of Bitcoin Core's networking layer.
Each node:
1. Listens for connections from other nodes
2. Connects to known peers
3. Exchanges blocks and transactions
4. Maintains the longest valid chain
5. Relays new blocks and transactions to peers

Built on asyncio for concurrent peer handling, using only stdlib.

Usage:
    node = ConvoCoinNode(host="0.0.0.0", port=9333)
    node.add_seed_peer("192.168.1.100", 9333)
    await node.start()
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import secrets
import struct
import time
from dataclasses import dataclass, field
from typing import Optional

from convoyield.coin.network.protocol import (
    Message,
    MessageType,
    msg_version,
    msg_verack,
    msg_ping,
    msg_pong,
    msg_inv,
    msg_getdata,
    msg_block,
    msg_tx,
    msg_getblocks,
    msg_headers,
    msg_addr,
    msg_getaddr,
    msg_reject,
    InvType,
)

logger = logging.getLogger("convocoin.node")


@dataclass
class PeerInfo:
    """Information about a connected peer."""

    host: str
    port: int
    node_id: str = ""
    version: str = ""
    chain_height: int = 0
    best_hash: str = ""
    connected_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    latency_ms: float = 0.0
    messages_sent: int = 0
    messages_received: int = 0
    writer: Optional[asyncio.StreamWriter] = field(default=None, repr=False)
    reader: Optional[asyncio.StreamReader] = field(default=None, repr=False)
    handshake_complete: bool = False
    _ping_nonce: int = 0
    _ping_time: float = 0.0

    @property
    def address(self) -> str:
        return f"{self.host}:{self.port}"

    def to_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "node_id": self.node_id,
            "version": self.version,
            "chain_height": self.chain_height,
            "connected_at": self.connected_at,
            "last_seen": self.last_seen,
            "latency_ms": self.latency_ms,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "handshake_complete": self.handshake_complete,
        }


class ConvoCoinNode:
    """
    A full ConvoCoin network node.

    Handles peer discovery, block propagation, transaction relay,
    and chain synchronization.
    """

    PROTOCOL_VERSION = "1.0.0"
    MAX_PEERS = 125  # Bitcoin default
    PING_INTERVAL = 120  # Seconds between pings
    HANDSHAKE_TIMEOUT = 10  # Seconds to complete handshake

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9333,
        node_id: str = "",
        blockchain=None,
    ):
        self.host = host
        self.port = port
        self.node_id = node_id or f"node_{secrets.token_hex(8)}"
        self.blockchain = blockchain

        self.peers: dict[str, PeerInfo] = {}
        self.seed_peers: list[tuple[str, int]] = []
        self.known_addresses: set[str] = set()
        self._server: Optional[asyncio.AbstractServer] = None
        self._running = False
        self._block_handlers: list = []
        self._tx_handlers: list = []
        self._known_blocks: set[str] = set()
        self._known_txs: set[str] = set()

    def add_seed_peer(self, host: str, port: int):
        """Add a seed peer to connect to on startup."""
        self.seed_peers.append((host, port))
        self.known_addresses.add(f"{host}:{port}")

    def on_block(self, handler):
        """Register a callback for when a new block is received."""
        self._block_handlers.append(handler)

    def on_transaction(self, handler):
        """Register a callback for when a new transaction is received."""
        self._tx_handlers.append(handler)

    async def start(self):
        """Start the node: listen for connections and connect to seeds."""
        self._running = True

        # Start the listener
        self._server = await asyncio.start_server(
            self._handle_incoming,
            self.host,
            self.port,
        )

        addr = self._server.sockets[0].getsockname()
        logger.info(f"Node {self.node_id} listening on {addr[0]}:{addr[1]}")

        # Connect to seed peers
        for host, port in self.seed_peers:
            asyncio.create_task(self._connect_to_peer(host, port))

        # Start maintenance tasks
        asyncio.create_task(self._ping_loop())
        asyncio.create_task(self._discovery_loop())

    async def stop(self):
        """Stop the node and disconnect all peers."""
        self._running = False

        # Close all peer connections
        for peer in list(self.peers.values()):
            await self._disconnect_peer(peer)

        # Stop the server
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        logger.info(f"Node {self.node_id} stopped")

    # ── Connection Handling ───────────────────────────────────────

    async def _handle_incoming(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        """Handle an incoming peer connection."""
        addr = writer.get_extra_info("peername")
        if not addr:
            writer.close()
            return

        host, port = addr[0], addr[1]
        logger.info(f"Incoming connection from {host}:{port}")

        if len(self.peers) >= self.MAX_PEERS:
            writer.close()
            return

        peer = PeerInfo(
            host=host,
            port=port,
            reader=reader,
            writer=writer,
        )

        await self._handshake(peer, initiator=False)

        if peer.handshake_complete:
            self.peers[peer.address] = peer
            await self._message_loop(peer)

    async def _connect_to_peer(self, host: str, port: int):
        """Actively connect to a peer."""
        address = f"{host}:{port}"
        if address in self.peers:
            return

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=10,
            )

            peer = PeerInfo(
                host=host,
                port=port,
                reader=reader,
                writer=writer,
            )

            await self._handshake(peer, initiator=True)

            if peer.handshake_complete:
                self.peers[peer.address] = peer
                logger.info(f"Connected to peer {address}")
                await self._message_loop(peer)
            else:
                writer.close()

        except (ConnectionRefusedError, asyncio.TimeoutError, OSError) as e:
            logger.debug(f"Could not connect to {address}: {e}")

    async def _disconnect_peer(self, peer: PeerInfo):
        """Disconnect a peer."""
        address = peer.address
        if peer.writer:
            peer.writer.close()
        self.peers.pop(address, None)
        logger.info(f"Disconnected peer {address}")

    # ── Handshake ─────────────────────────────────────────────────

    async def _handshake(self, peer: PeerInfo, initiator: bool):
        """
        Perform the version handshake (like Bitcoin's).

        Initiator:  version -> verack <- version <- verack
        Responder:  version <- verack -> version -> verack
        """
        chain_height = 0
        best_hash = ""
        if self.blockchain:
            chain_height = self.blockchain.height
            best_hash = self.blockchain.last_block.hash

        try:
            if initiator:
                # Send our version
                await self._send_message(peer, msg_version(
                    self.node_id, self.PROTOCOL_VERSION,
                    chain_height, best_hash,
                ))

                # Wait for their version
                msg = await self._recv_message(peer, timeout=self.HANDSHAKE_TIMEOUT)
                if msg and msg.msg_type == MessageType.VERSION:
                    peer.node_id = msg.node_id
                    peer.version = msg.payload.get("version", "")
                    peer.chain_height = msg.payload.get("chain_height", 0)
                    peer.best_hash = msg.payload.get("best_hash", "")

                    # Exchange veracks
                    await self._send_message(peer, msg_verack(self.node_id))

                    verack = await self._recv_message(peer, timeout=self.HANDSHAKE_TIMEOUT)
                    if verack and verack.msg_type == MessageType.VERACK:
                        peer.handshake_complete = True

            else:
                # Wait for their version
                msg = await self._recv_message(peer, timeout=self.HANDSHAKE_TIMEOUT)
                if msg and msg.msg_type == MessageType.VERSION:
                    peer.node_id = msg.node_id
                    peer.version = msg.payload.get("version", "")
                    peer.chain_height = msg.payload.get("chain_height", 0)
                    peer.best_hash = msg.payload.get("best_hash", "")

                    # Send our version + verack
                    await self._send_message(peer, msg_version(
                        self.node_id, self.PROTOCOL_VERSION,
                        chain_height, best_hash,
                    ))
                    await self._send_message(peer, msg_verack(self.node_id))

                    # Wait for their verack
                    verack = await self._recv_message(peer, timeout=self.HANDSHAKE_TIMEOUT)
                    if verack and verack.msg_type == MessageType.VERACK:
                        peer.handshake_complete = True

        except (asyncio.TimeoutError, ConnectionError):
            peer.handshake_complete = False

    # ── Message Loop ──────────────────────────────────────────────

    async def _message_loop(self, peer: PeerInfo):
        """Main message processing loop for a connected peer."""
        while self._running and peer.address in self.peers:
            try:
                msg = await self._recv_message(peer, timeout=300)
                if not msg:
                    break

                peer.last_seen = time.time()
                peer.messages_received += 1

                await self._handle_message(peer, msg)

            except (ConnectionError, asyncio.TimeoutError):
                break
            except Exception as e:
                logger.error(f"Error in message loop for {peer.address}: {e}")
                break

        await self._disconnect_peer(peer)

    async def _handle_message(self, peer: PeerInfo, msg: Message):
        """Route a message to the appropriate handler."""
        handlers = {
            MessageType.PING: self._handle_ping,
            MessageType.PONG: self._handle_pong,
            MessageType.INV: self._handle_inv,
            MessageType.GETDATA: self._handle_getdata,
            MessageType.BLOCK: self._handle_block,
            MessageType.TX: self._handle_tx,
            MessageType.GETBLOCKS: self._handle_getblocks,
            MessageType.ADDR: self._handle_addr,
            MessageType.GETADDR: self._handle_getaddr,
        }

        handler = handlers.get(msg.msg_type)
        if handler:
            await handler(peer, msg)

    # ── Message Handlers ──────────────────────────────────────────

    async def _handle_ping(self, peer: PeerInfo, msg: Message):
        nonce = msg.payload.get("nonce", 0)
        await self._send_message(peer, msg_pong(self.node_id, nonce))

    async def _handle_pong(self, peer: PeerInfo, msg: Message):
        nonce = msg.payload.get("nonce", 0)
        if nonce == peer._ping_nonce:
            peer.latency_ms = (time.time() - peer._ping_time) * 1000

    async def _handle_inv(self, peer: PeerInfo, msg: Message):
        """Handle inventory announcement — request unknown items."""
        inv_type = msg.payload.get("type", "")
        hashes = msg.payload.get("hashes", [])

        known = self._known_blocks if inv_type == InvType.BLOCK else self._known_txs
        unknown = [h for h in hashes if h not in known]

        if unknown:
            await self._send_message(
                peer, msg_getdata(self.node_id, inv_type, unknown)
            )

    async def _handle_getdata(self, peer: PeerInfo, msg: Message):
        """Handle data request — send requested blocks/transactions."""
        inv_type = msg.payload.get("type", "")
        hashes = msg.payload.get("hashes", [])

        if inv_type == InvType.BLOCK and self.blockchain:
            for block in self.blockchain.chain:
                if block.hash in hashes:
                    await self._send_message(
                        peer, msg_block(self.node_id, block.to_dict())
                    )

    async def _handle_block(self, peer: PeerInfo, msg: Message):
        """Handle a received block."""
        block_data = msg.payload.get("block", {})
        block_hash = block_data.get("hash", "")

        if block_hash in self._known_blocks:
            return  # Already have it

        self._known_blocks.add(block_hash)

        # Notify handlers
        for handler in self._block_handlers:
            try:
                handler(block_data, peer)
            except Exception as e:
                logger.error(f"Block handler error: {e}")

        # Relay to other peers (flooding)
        await self.broadcast_except(
            msg_inv(self.node_id, InvType.BLOCK, [block_hash]),
            exclude=peer.address,
        )

    async def _handle_tx(self, peer: PeerInfo, msg: Message):
        """Handle a received transaction."""
        tx_data = msg.payload.get("transaction", {})
        tx_hash = tx_data.get("tx_hash", "")

        if tx_hash in self._known_txs:
            return

        self._known_txs.add(tx_hash)

        for handler in self._tx_handlers:
            try:
                handler(tx_data, peer)
            except Exception as e:
                logger.error(f"TX handler error: {e}")

        # Relay
        await self.broadcast_except(
            msg_inv(self.node_id, InvType.TX, [tx_hash]),
            exclude=peer.address,
        )

    async def _handle_getblocks(self, peer: PeerInfo, msg: Message):
        """Handle block request — send headers from requested height."""
        from_height = msg.payload.get("from_height", 0)

        if self.blockchain:
            headers = []
            for block in self.blockchain.chain[from_height:from_height + 500]:
                headers.append({
                    "index": block.index,
                    "hash": block.hash,
                    "previous_hash": block.previous_hash,
                    "timestamp": block.timestamp,
                    "proof_of_yield": block.proof_of_yield,
                })

            await self._send_message(
                peer, msg_headers(self.node_id, headers)
            )

    async def _handle_addr(self, peer: PeerInfo, msg: Message):
        """Handle peer address sharing."""
        addresses = msg.payload.get("addresses", [])
        for addr_info in addresses:
            addr = f"{addr_info.get('host')}:{addr_info.get('port')}"
            if addr not in self.known_addresses and len(self.peers) < self.MAX_PEERS:
                self.known_addresses.add(addr)
                # Optionally connect to new peers
                asyncio.create_task(
                    self._connect_to_peer(
                        addr_info["host"], addr_info["port"]
                    )
                )

    async def _handle_getaddr(self, peer: PeerInfo, msg: Message):
        """Share known peer addresses."""
        addresses = []
        for p in self.peers.values():
            if p.address != peer.address:
                addresses.append({
                    "host": p.host,
                    "port": p.port,
                    "node_id": p.node_id,
                })

        await self._send_message(
            peer, msg_addr(self.node_id, addresses)
        )

    # ── Broadcasting ──────────────────────────────────────────────

    async def broadcast(self, msg: Message):
        """Broadcast a message to all connected peers."""
        for peer in list(self.peers.values()):
            try:
                await self._send_message(peer, msg)
            except ConnectionError:
                await self._disconnect_peer(peer)

    async def broadcast_except(self, msg: Message, exclude: str):
        """Broadcast to all peers except one (flood fill)."""
        for peer in list(self.peers.values()):
            if peer.address != exclude:
                try:
                    await self._send_message(peer, msg)
                except ConnectionError:
                    await self._disconnect_peer(peer)

    async def announce_block(self, block_hash: str):
        """Announce a newly mined block to the network."""
        self._known_blocks.add(block_hash)
        await self.broadcast(
            msg_inv(self.node_id, InvType.BLOCK, [block_hash])
        )

    async def announce_transaction(self, tx_hash: str):
        """Announce a new transaction to the network."""
        self._known_txs.add(tx_hash)
        await self.broadcast(
            msg_inv(self.node_id, InvType.TX, [tx_hash])
        )

    # ── Wire I/O ──────────────────────────────────────────────────

    async def _send_message(self, peer: PeerInfo, msg: Message):
        """Send a message to a peer."""
        if not peer.writer:
            return

        data = msg.serialize()
        peer.writer.write(data)
        await peer.writer.drain()
        peer.messages_sent += 1

    async def _recv_message(
        self,
        peer: PeerInfo,
        timeout: float = 30,
    ) -> Optional[Message]:
        """Receive a message from a peer."""
        if not peer.reader:
            return None

        try:
            # Read length prefix
            length_data = await asyncio.wait_for(
                peer.reader.readexactly(4),
                timeout=timeout,
            )
            length = struct.unpack(">I", length_data)[0]

            if length > 10_000_000:  # 10MB max message
                return None

            # Read body
            body = await asyncio.wait_for(
                peer.reader.readexactly(length),
                timeout=timeout,
            )

            return Message.deserialize(body)

        except (asyncio.IncompleteReadError, asyncio.TimeoutError):
            return None

    # ── Maintenance Tasks ─────────────────────────────────────────

    async def _ping_loop(self):
        """Periodically ping peers to check liveness."""
        while self._running:
            await asyncio.sleep(self.PING_INTERVAL)

            for peer in list(self.peers.values()):
                try:
                    nonce = int(time.time() * 1000)
                    peer._ping_nonce = nonce
                    peer._ping_time = time.time()
                    await self._send_message(
                        peer, msg_ping(self.node_id)
                    )
                except ConnectionError:
                    await self._disconnect_peer(peer)

    async def _discovery_loop(self):
        """Periodically discover new peers."""
        while self._running:
            await asyncio.sleep(300)  # Every 5 minutes

            if len(self.peers) < 8:
                # Ask existing peers for more addresses
                for peer in list(self.peers.values()):
                    try:
                        await self._send_message(
                            peer, msg_getaddr(self.node_id)
                        )
                    except ConnectionError:
                        pass

    # ── Status ────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """Get node status."""
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "protocol_version": self.PROTOCOL_VERSION,
            "running": self._running,
            "peer_count": len(self.peers),
            "max_peers": self.MAX_PEERS,
            "known_addresses": len(self.known_addresses),
            "known_blocks": len(self._known_blocks),
            "known_transactions": len(self._known_txs),
            "peers": [p.to_dict() for p in self.peers.values()],
        }
