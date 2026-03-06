"""
AgentMesh – Hub (Message Broker)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A Hub is the central router / directory-service for a group of agents.
Two implementations are provided:

  LocalHub   – in-process broker (perfect for single-process apps & testing)
  NetworkHub – TCP broker that spans processes / machines (v1.1)

The Hub never sees message *contents* – it only routes opaque encrypted
envelopes.  Agent discovery (public-key bundles) is the only plaintext
information stored.
"""

from __future__ import annotations

import json
import logging
import socket
import threading
import queue
from typing import Dict, List, Optional

logger = logging.getLogger("agentmesh.hub")


# ──────────────────────────────────────────────────────────────────────────────
# Base class / interface
# ──────────────────────────────────────────────────────────────────────────────

class Hub:
    """Abstract hub interface."""

    def register(self, agent) -> None: raise NotImplementedError
    def get_bundle(self, agent_id: str) -> Optional[dict]: raise NotImplementedError
    def deliver(self, envelope: dict) -> None: raise NotImplementedError
    def list_agents(self) -> List[str]: raise NotImplementedError


# ──────────────────────────────────────────────────────────────────────────────
# LocalHub  (in-process)
# ──────────────────────────────────────────────────────────────────────────────

class LocalHub(Hub):
    """In-process message hub."""

    def __init__(self):
        self._agents: Dict[str, object] = {}
        self._bundles: Dict[str, dict] = {}
        self._lock = threading.Lock()
        self._message_log: List[dict] = []

    def register(self, agent) -> None:
        with self._lock:
            self._agents[agent.id] = agent
            self._bundles[agent.id] = agent.public_bundle

    def get_bundle(self, agent_id: str) -> Optional[dict]:
        return self._bundles.get(agent_id)

    def deliver(self, envelope: dict) -> None:
        recipient_id = envelope.get("to")
        with self._lock:
            recipient = self._agents.get(recipient_id)
        if recipient:
            recipient._receive(envelope)

    def list_agents(self) -> List[str]:
        with self._lock:
            return list(self._agents.keys())


# ──────────────────────────────────────────────────────────────────────────────
# NetworkHub  (TCP, cross-process)
# ──────────────────────────────────────────────────────────────────────────────

class NetworkHub(Hub):
    """TCP Hub Client with background receiver thread."""

    def __init__(self, host: str = "localhost", port: int = 7700):
        self.host = host
        self.port = port
        self._sock = None
        self._agent = None
        self._lock = threading.Lock()
        self._pending_resps = queue.Queue()
        self._running = False

    def _connect(self):
        self._sock = socket.create_connection((self.host, self.port), timeout=5)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._running = True
        t = threading.Thread(target=self._recv_loop, daemon=True)
        t.start()

    def _recv_loop(self):
        buf = b""
        try:
            while self._running:
                data = self._sock.recv(65536)
                if not data: break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    msg = json.loads(line)
                    if msg.get("cmd") == "INCOMING":
                        if self._agent:
                            threading.Thread(
                                target=self._agent._receive,
                                args=(msg.get("envelope"),),
                                daemon=True
                            ).start()
                    else:
                        self._pending_resps.put(msg)
        except:
            self._running = False

    def _request(self, msg: dict) -> dict:
        with self._lock:
            if not self._sock:
                self._connect()
            self._sock.sendall((json.dumps(msg) + "\n").encode())
            return self._pending_resps.get(timeout=10)

    def register(self, agent) -> None:
        self._agent = agent
        resp = self._request({"cmd": "REGISTER", "bundle": agent.public_bundle})
        if resp.get("status") != "OK":
            raise RuntimeError(f"Registration failed: {resp}")

    def get_bundle(self, agent_id: str) -> Optional[dict]:
        resp = self._request({"cmd": "GET_BUNDLE", "agent_id": agent_id})
        return resp.get("bundle")

    def deliver(self, envelope: dict) -> None:
        self._request({"cmd": "DELIVER", "envelope": envelope})

    def list_agents(self) -> List[str]:
        resp = self._request({"cmd": "LIST_AGENTS"})
        return resp.get("agents", [])


# ──────────────────────────────────────────────────────────────────────────────
# NetworkHubServer
# ──────────────────────────────────────────────────────────────────────────────

class NetworkHubServer:
    """TCP Hub Server."""

    def __init__(self, host: str = "0.0.0.0", port: int = 7700):
        self.host = host
        self.port = port
        self._bundles = {}
        self._agent_socks = {}
        self._lock = threading.Lock()
        self._srv_sock = None

    def start(self, block: bool = True):
        self._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv_sock.bind((self.host, self.port))
        self._srv_sock.listen(128)
        if block:
            self._accept_loop()
        else:
            threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while True:
            conn, addr = self._srv_sock.accept()
            threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()

    def _handle_client(self, conn):
        agent_id = None
        buf = b""
        try:
            while True:
                data = conn.recv(65536)
                if not data: break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    msg = json.loads(line)
                    cmd = msg.get("cmd")
                    
                    if cmd == "REGISTER":
                        agent_id = msg["bundle"]["agent_id"]
                        with self._lock:
                            self._bundles[agent_id] = msg["bundle"]
                            self._agent_socks[agent_id] = conn
                        conn.sendall(b'{"status": "OK"}\n')
                    elif cmd == "GET_BUNDLE":
                        b = self._bundles.get(msg["agent_id"])
                        conn.sendall((json.dumps({"bundle": b}) + "\n").encode())
                    elif cmd == "DELIVER":
                        target = msg["envelope"]["to"]
                        with self._lock:
                            s = self._agent_socks.get(target)
                        if s:
                            s.sendall((json.dumps({"cmd": "INCOMING", "envelope": msg["envelope"]}) + "\n").encode())
                        conn.sendall(b'{"status": "OK"}\n')
                    elif cmd == "LIST_AGENTS":
                        with self._lock:
                            agents = list(self._bundles.keys())
                        conn.sendall((json.dumps({"agents": agents}) + "\n").encode())
        finally:
            if agent_id:
                with self._lock:
                    self._agent_socks.pop(agent_id, None)
            conn.close()
