#!/usr/bin/env python3
"""
Loxone WebSocket Client Library

Real-time state monitoring via WebSocket with classic hash authentication.
Parses binary status updates (value + text states) and delivers them via callbacks.

Usage as library:
    from loxone_ws import LoxoneWS

    async def on_change(uuid, name, old_value, new_value):
        print(f"{name}: {old_value} → {new_value}")

    ws = LoxoneWS("192.168.0.222", "admin", "password")
    ws.on_state_change = on_change
    await ws.connect()
    await ws.listen()
"""

import asyncio
import hashlib
import hmac
import json
import struct
import os
import ssl
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple


class LoxoneWS:
    """WebSocket client for real-time Loxone Miniserver state monitoring."""

    def __init__(self, host: str, username: str, password: str, use_https: bool = True):
        self.host = host
        self.username = username
        self.password = password
        self.use_https = use_https
        scheme = "wss" if use_https else "ws"
        self.ws_url = f"{scheme}://{host}/ws/rfc6455"

        # State cache: uuid → value (float or str)
        self.states: Dict[str, object] = {}

        # UUID metadata: uuid → {"name": ..., "room": ..., "control": ..., "state_key": ...}
        self.uuid_meta: Dict[str, dict] = {}

        # Callbacks
        self.on_state_change: Optional[Callable] = None  # (uuid, name, old, new)
        self.on_initial_state: Optional[Callable] = None  # (uuid, name, value)
        self.on_connected: Optional[Callable] = None      # ()

        # Filter: if set, only these UUIDs trigger callbacks
        self._watch_uuids: Optional[set] = None

        self._ws = None
        self._connected = False

    # ── Structure loading ──────────────────────────────────────────

    def load_structure(self, path: str):
        """Load LoxAPP3.json and build UUID→name mapping for all control states."""
        with open(path) as f:
            data = json.load(f)

        rooms = data.get("rooms", {})
        cats = data.get("cats", {})

        for ctrl_uuid, ctrl in data.get("controls", {}).items():
            room_name = rooms.get(ctrl.get("room"), {}).get("name", "?")
            ctrl_name = ctrl.get("name", "?")
            ctrl_type = ctrl.get("type", "?")

            # Register control's own states
            for state_key, state_uuid in ctrl.get("states", {}).items():
                norm = self._normalize_uuid(state_uuid)
                self.uuid_meta[norm] = {
                    "name": f"{ctrl_name}/{state_key}",
                    "room": room_name,
                    "control": ctrl_name,
                    "control_type": ctrl_type,
                    "state_key": state_key,
                    "control_uuid": ctrl_uuid,
                }

            # Register subControl states
            for sc_uuid, sc in ctrl.get("subControls", {}).items():
                sc_name = sc.get("name", "?")
                for state_key, state_uuid in sc.get("states", {}).items():
                    norm = self._normalize_uuid(state_uuid)
                    self.uuid_meta[norm] = {
                        "name": f"{ctrl_name}/{sc_name}/{state_key}",
                        "room": room_name,
                        "control": ctrl_name,
                        "control_type": ctrl_type,
                        "state_key": state_key,
                        "subcontrol": sc_name,
                        "control_uuid": ctrl_uuid,
                    }

    def watch_room(self, room_name: str):
        """Only report changes for controls in a specific room."""
        if self._watch_uuids is None:
            self._watch_uuids = set()
        for uuid, meta in self.uuid_meta.items():
            if meta["room"].lower() == room_name.lower():
                self._watch_uuids.add(uuid)

    def watch_control(self, control_name: str):
        """Only report changes for a specific control (by name substring)."""
        if self._watch_uuids is None:
            self._watch_uuids = set()
        for uuid, meta in self.uuid_meta.items():
            if control_name.lower() in meta["control"].lower():
                self._watch_uuids.add(uuid)

    def watch_uuids(self, uuids: List[str]):
        """Only report changes for specific UUIDs."""
        if self._watch_uuids is None:
            self._watch_uuids = set()
        for u in uuids:
            self._watch_uuids.add(self._normalize_uuid(u))

    def get_name(self, uuid: str) -> str:
        """Get human-readable name for a UUID."""
        meta = self.uuid_meta.get(uuid)
        if meta:
            return f"{meta['room']}/{meta['name']}"
        return uuid

    # ── Connection & auth ──────────────────────────────────────────

    async def connect(self):
        """Connect and authenticate via classic hash flow."""
        import websockets

        ssl_ctx = None
        if self.use_https:
            ssl_ctx = ssl.create_default_context()

        self._ws = await websockets.connect(
            self.ws_url,
            ping_interval=30,
            ping_timeout=10,
            ssl=ssl_ctx,
        )

        # Step 1: getkey2
        await self._ws.send(f"jdev/sys/getkey2/{self.username}")
        resp = json.loads(await self._recv_text())
        val = resp["LL"]["value"]
        key, salt = val["key"], val["salt"]
        alg = val.get("hashAlg", "SHA1")

        # Step 2: hash credentials
        pw_hash = hashlib.sha1(
            f"{self.password}:{salt}".encode()
        ).hexdigest().upper()
        key_bytes = bytes.fromhex(key)
        h = hashlib.sha256 if alg == "SHA256" else hashlib.sha1
        auth_hash = hmac.new(
            key_bytes, f"{self.username}:{pw_hash}".encode(), h
        ).hexdigest()

        # Step 3: authenticate
        await self._ws.send(f"authenticate/{auth_hash}")
        resp = json.loads(await self._recv_text())
        code = str(resp["LL"].get("Code", resp["LL"].get("code", "")))
        if code != "200":
            raise ConnectionError(f"Auth failed: {resp}")

        # Step 4: enable binary status updates
        await self._ws.send("jdev/sps/enablebinstatusupdate")
        await self._recv_text()

        self._connected = True
        if self.on_connected:
            await self._maybe_await(self.on_connected)

    async def listen(self, duration: float = 0):
        """
        Listen for state updates. Runs until connection closes or duration expires.
        duration=0 means forever.
        """
        import websockets

        start = asyncio.get_event_loop().time()

        while self._connected:
            if duration > 0 and (asyncio.get_event_loop().time() - start) > duration:
                break

            try:
                msg = await asyncio.wait_for(self._ws.recv(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                self._connected = False
                break

            if not isinstance(msg, bytes):
                continue

            # Binary header (8 bytes): type marker
            if len(msg) == 8 and msg[0] == 0x03:
                msg_type = msg[1]
                try:
                    payload = await asyncio.wait_for(self._ws.recv(), timeout=2.0)
                except:
                    continue
                if not isinstance(payload, bytes):
                    continue

                if msg_type == 2:
                    self._handle_value_states(payload)
                elif msg_type == 3:
                    self._handle_text_states(payload)

        if self._ws:
            await self._ws.close()

    async def disconnect(self):
        """Close WebSocket connection."""
        self._connected = False
        if self._ws:
            await self._ws.close()

    # ── Binary parsing ─────────────────────────────────────────────

    def _handle_value_states(self, data: bytes):
        """Parse type-2 binary: UUID (16B) + double (8B) pairs."""
        offset = 0
        while offset + 24 <= len(data):
            uuid_str = self._uuid_from_bytes(data[offset:offset + 16])
            value = struct.unpack("<d", data[offset + 16:offset + 24])[0]
            offset += 24
            self._process_update(uuid_str, value)

    def _handle_text_states(self, data: bytes):
        """Parse type-3 binary: UUID (16B) + icon_UUID (16B) + len (4B) + text."""
        offset = 0
        while offset + 36 <= len(data):
            uuid_str = self._uuid_from_bytes(data[offset:offset + 16])
            offset += 32  # skip UUID + icon UUID
            text_len = struct.unpack("<I", data[offset:offset + 4])[0]
            offset += 4
            padded = text_len + (4 - text_len % 4) if text_len % 4 else text_len
            if offset + padded > len(data):
                break
            text = data[offset:offset + text_len].decode("utf-8", errors="replace").rstrip("\x00")
            offset += padded
            self._process_update(uuid_str, text)

    def _process_update(self, uuid: str, value):
        """Route a state update to callbacks."""
        if self._watch_uuids and uuid not in self._watch_uuids:
            return

        old = self.states.get(uuid)
        self.states[uuid] = value

        if old is None:
            if self.on_initial_state:
                name = self.get_name(uuid)
                asyncio.ensure_future(self._maybe_await(self.on_initial_state, uuid, name, value))
        elif old != value:
            if self.on_state_change:
                name = self.get_name(uuid)
                asyncio.ensure_future(self._maybe_await(self.on_state_change, uuid, name, old, value))

    # ── Helpers ────────────────────────────────────────────────────

    async def _recv_text(self, timeout: float = 5.0) -> str:
        """Receive next text message, skipping binary frames."""
        while True:
            msg = await asyncio.wait_for(self._ws.recv(), timeout=timeout)
            if isinstance(msg, str):
                return msg

    @staticmethod
    def _uuid_from_bytes(b: bytes) -> str:
        """Convert 16 binary bytes to standard UUID string (LE fields)."""
        d1 = struct.unpack("<I", b[0:4])[0]
        d2 = struct.unpack("<H", b[4:6])[0]
        d3 = struct.unpack("<H", b[6:8])[0]
        return f"{d1:08x}-{d2:04x}-{d3:04x}-{b[8:10].hex()}-{b[10:16].hex()}"

    @staticmethod
    def _normalize_uuid(u: str) -> str:
        """Convert Loxone UUID format (8-4-4-16) to standard (8-4-4-4-12)."""
        parts = u.split("-")
        if len(parts) == 4 and len(parts[3]) == 16:
            return f"{parts[0]}-{parts[1]}-{parts[2]}-{parts[3][:4]}-{parts[3][4:]}"
        return u

    @staticmethod
    async def _maybe_await(fn, *args):
        """Call fn with args; await if coroutine."""
        result = fn(*args)
        if asyncio.iscoroutine(result):
            await result
