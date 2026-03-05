"""
AgentComm - Decentralized Communication for AI Agents
Supports both Internet (Nostr) and Local Network modes
"""

import os
import json
import time
import uuid
import requests
import socket
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Try to import nostr libraries
try:
    import nostr
    from nostr.key import PrivateKey, PublicKey
    from nostr.event import Event, EventKind
    from nostr.filter import Filter
    from nostr.relay_manager import RelayManager
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'nostr'], check=True)
    import nostr
    from nostr.key import PrivateKey, PublicKey
    from nostr.event import Event, EventKind
    from nostr.filter import Filter
    from nostr.relay_manager import RelayManager

# Try to import zeroconf for mDNS
try:
    from zeroconf import Zeroconf
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'zeroconf'], check=True)
    from zeroconf import Zeroconf

# Default Nostr relays
DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.primal.net",
    "wss://nos.lol"
]

# Protocol version
PROTOCOL_VERSION = "agentcomm-v1"

# LAN service configuration
LAN_SERVICE_TYPE = "_agentcomm._tcp."
LAN_SERVICE_PORT = 8765


class LANServer:
    """HTTP server for LAN communication"""
    
    messages_received = []
    
    def __init__(self, port: int = LAN_SERVICE_PORT):
        self.port = port
        self.server = None
        self.thread = None
        self.my_ip = self._get_local_ip()
    
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start(self):
        """Start the HTTP server"""
        self.server = HTTPServer(('0.0.0.0', self.port), self._create_handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[LAN] Server started on {self.my_ip}:{self.port}")
        return self.port
    
    def _create_handler(self):
        """Create HTTP handler class with access to messages"""
        messages = self.messages_received
        my_ip = self.my_ip
        
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"status": "online", "service": "AgentComm", "ip": my_ip}
                    self.wfile.write(json.dumps(response).encode())
                elif self.path == "/messages":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(messages).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body)
                    messages.append({
                        "from_ip": self.client_address[0],
                        "timestamp": time.time(),
                        "data": data
                    })
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "received"}).encode())
                except Exception as e:
                    self.send_response(400)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass
        
        return Handler
    
    def stop(self):
        if self.server:
            self.server.shutdown()
    
    def get_messages(self) -> List[Dict]:
        return self.messages_received


class LANDiscovery:
    """mDNS/Bonjour service discovery"""
    
    def __init__(self):
        self.zeroconf = None
        self.my_ip = self._get_local_ip()
        self.discovered = []
    
    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def discover(self, timeout: float = 3.0) -> List[Dict[str, Any]]:
        """Discover nearby agents using mDNS"""
        # Simple mDNS-like discovery via socket broadcast
        agents = []
        
        # Get all local IPs
        hostname = socket.gethostname()
        try:
            local_ips = socket.gethostbyname_ex(hostname)[2]
        except:
            local_ips = [self.my_ip]
        
        # Try common local subnets
        if self.my_ip:
            parts = self.my_ip.split('.')
            base = f"{parts[0]}.{parts[1]}.{parts[2]}"
            
            # Quick scan common addresses
            for i in range(1, 255):
                ip = f"{base}.{i}"
                if ip == self.my_ip:
                    continue
                try:
                    response = requests.get(f"http://{ip}:{LAN_SERVICE_PORT}/", timeout=0.1)
                    if response.status_code == 200:
                        data = response.json()
                        agents.append({
                            "ip": ip,
                            "status": data.get("status"),
                            "service": data.get("service")
                        })
                except:
                    pass
        
        self.discovered = agents
        return agents


class NostrComm:
    """Nostr-based internet communication"""
    
    def __init__(self, private_key: Optional[str] = None, relays: Optional[List[str]] = None):
        self.private_key = None
        self.public_key = None
        self.relays = relays or DEFAULT_RELAYS
        self.relay_manager = None
        
        if private_key:
            self._load_key(private_key)
        else:
            self._generate_key()
        
        self._init_relay_manager()
    
    def _generate_key(self):
        self.private_key = PrivateKey()
        self.public_key = self.private_key.public_key
        print(f"Generated Nostr identity: npub: {self.public_key.bech32()}")
    
    def _load_key(self, key: str):
        try:
            self.private_key = PrivateKey.from_bech32(key)
            self.public_key = self.private_key.public_key
        except:
            self.private_key = PrivateKey.from_hex(key)
            self.public_key = self.private_key.public_key
    
    def _init_relay_manager(self):
        self.relay_manager = RelayManager()
        for relay in self.relays:
            self.relay_manager.add_relay(relay)
        self.relay_manager.open_connections()
        time.sleep(1)
    
    def send_message(self, target_pubkey: str, content: str) -> Dict[str, Any]:
        try:
            target_hex = PublicKey.from_bech32(target_pubkey).hex() if target_pubkey.startswith('npub1') else target_pubkey
            
            recipient = PublicKey.from_hex(target_hex)
            encrypted = self.private_key.encrypt_dm(content, recipient)
            
            event = Event(
                content=encrypted,
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
                tags=[['p', target_hex]]
            )
            self.private_key.sign_event(event)
            
            for relay in self.relays:
                try:
                    self.relay_manager.publish_event(event, relay)
                except:
                    pass
            
            return {"status": "success", "message_id": event.id, "recipient": target_pubkey}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def fetch_inbox(self, limit: int = 10) -> List[Dict]:
        messages = []
        filter_obj = Filter(
            kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
            tags={'#p': [self.public_key.hex()]},
            limit=limit
        )
        
        sub_id = f"inbox-{uuid.uuid4().hex[:8]}"
        self.relay_manager.add_subscription(sub_id, filter_obj)
        time.sleep(3)
        
        for msg in self.relay_manager.message_pool:
            if hasattr(msg, 'event') and msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                try:
                    content = self._decrypt(msg.event.content, msg.event.pubkey)
                    messages.append({
                        "id": msg.event.id,
                        "sender": PublicKey.from_hex(msg.event.pubkey).bech32(),
                        "content": content,
                        "timestamp": msg.event.created_at
                    })
                except:
                    pass
        
        self.relay_manager.remove_subscription(sub_id)
        return messages
    
    def _decrypt(self, encrypted: str, sender: str) -> str:
        sender_key = PublicKey.from_hex(sender)
        return self.private_key.decrypt_dm(encrypted, sender_key)


class IPFSHandler:
    """IPFS file storage"""
    
    def __init__(self):
        self.gateway_url = "https://ipfs.io/ipfs/"
    
    def upload(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    "https://uploads.ipfs.io/api/v0/add",
                    files=files,
                    timeout=60
                )
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "cid": result['Hash'],
                    "name": os.path.basename(file_path),
                    "link": f"{self.gateway_url}{result['Hash']}"
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Global instances
_nostr: Optional[NostrComm] = None
_ipfs: Optional[IPFSHandler] = None
_lan: Optional[LANServer] = None
_lan_discovery: Optional[LANDiscovery] = None


# === OpenClaw Tool Functions ===

def generate_identity() -> Dict[str, Any]:
    """Generate a new Nostr identity"""
    global _nostr, _ipfs
    _nostr = NostrComm()
    _ipfs = IPFSHandler()
    return {
        "private_key": _nostr.private_key.bech32(),
        "public_key": _nostr.public_key.bech32(),
        "status": "success",
        "message": "Identity generated! Save your nsec key."
    }


def load_identity(private_key: str) -> Dict[str, Any]:
    """Load existing Nostr identity"""
    global _nostr, _ipfs
    try:
        _nostr = NostrComm(private_key=private_key)
        _ipfs = IPFSHandler()
        return {"status": "success", "public_key": _nostr.public_key.bech32()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def send_message(target_pubkey: str, content: str) -> Dict[str, Any]:
    """Send message via Nostr (internet)"""
    global _nostr
    if not _nostr:
        return {"status": "error", "error": "No identity. Run generate_identity first."}
    return _nostr.send_message(target_pubkey, content)


def share_file(file_path: str, target_pubkey: str) -> Dict[str, Any]:
    """Upload to IPFS and share via Nostr"""
    global _nostr, _ipfs
    if not _nostr or not _ipfs:
        return {"status": "error", "error": "No identity. Run generate_identity first."}
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}
    
    result = _ipfs.upload(file_path)
    if result['status'] != 'success':
        return result
    
    payload = json.dumps({
        "protocol": PROTOCOL_VERSION,
        "type": "file",
        "cid": result['cid'],
        "filename": result['name'],
        "link": result['link']
    })
    
    msg_result = _nostr.send_message(target_pubkey, payload)
    return {
        "status": "success",
        "file": result,
        "message": msg_result
    }


def fetch_inbox(limit: int = 10) -> Dict[str, Any]:
    """Check Nostr inbox"""
    global _nostr
    if not _nostr:
        return {"status": "error", "error": "No identity."}
    messages = _nostr.fetch_inbox(limit)
    return {"status": "success", "messages": messages, "count": len(messages)}


def get_my_pubkey() -> Dict[str, Any]:
    """Get your public key"""
    global _nostr
    if not _nostr:
        return {"status": "error", "error": "No identity."}
    return {"status": "success", "public_key": _nostr.public_key.bech32()}


# === LAN Mode Functions ===

def start_lan_server() -> Dict[str, Any]:
    """Start LAN server for local network communication"""
    global _lan, _lan_discovery
    _lan = LANServer()
    _lan.start()
    _lan_discovery = LANDiscovery()
    
    return {
        "status": "success",
        "ip": _lan.my_ip,
        "port": _lan.port,
        "endpoint": f"http://{_lan.my_ip}:{_lan.port}",
        "message": "LAN server started. Other agents on your network can now communicate with you."
    }


def discover_lan_agents(timeout: float = 3.0) -> Dict[str, Any]:
    """Discover nearby agents on local network"""
    global _lan_discovery
    if not _lan_discovery:
        _lan_discovery = LANDiscovery()
    
    agents = _lan_discovery.discover(timeout)
    return {
        "status": "success",
        "agents": agents,
        "count": len(agents)
    }


def send_lan_message(ip: str, content: str) -> Dict[str, Any]:
    """Send message to agent at IP address"""
    global _lan
    if not _lan:
        return {"status": "error", "error": "LAN server not started. Run start_lan_server first."}
    
    try:
        response = requests.post(
            f"http://{ip}:{LAN_SERVICE_PORT}/",
            json={"type": "text", "content": content, "from": _lan.my_ip, "timestamp": time.time()},
            timeout=10
        )
        return {"status": "success", "ip": ip} if response.status_code == 200 else {"status": "error", "ip": ip}
    except Exception as e:
        return {"status": "error", "error": str(e), "ip": ip}


def send_lan_file(ip: str, file_path: str) -> Dict[str, Any]:
    """Send file to agent at IP address"""
    global _lan
    if not _lan:
        return {"status": "error", "error": "LAN server not started."}
    if not os.path.exists(file_path):
        return {"status": "error", "error": f"File not found: {file_path}"}
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(
                f"http://{ip}:{LAN_SERVICE_PORT}/",
                files=files,
                timeout=60
            )
        return {"status": "success", "filename": os.path.basename(file_path), "ip": ip}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_lan_messages() -> Dict[str, Any]:
    """Get messages received via LAN"""
    global _lan
    if not _lan:
        return {"status": "error", "error": "LAN server not started."}
    messages = _lan.get_messages()
    return {"status": "success", "messages": messages, "count": len(messages)}


def get_lan_info() -> Dict[str, Any]:
    """Get LAN connection info"""
    global _lan
    if not _lan:
        return {"status": "inactive", "message": "Run start_lan_server first."}
    return {"status": "active", "ip": _lan.my_ip, "port": _lan.port, "endpoint": f"http://{_lan.my_ip}:{_lan.port}"}
