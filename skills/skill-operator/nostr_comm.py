"""
AgentComm - Decentralized Communication for AI Agents
Enables OpenClaw agents to send messages and files without centralized servers
Supports both Internet (Nostr) and Local Network (mDNS + HTTP) modes
"""

import os
import json
import time
import uuid
import base64
import hashlib
import requests
import subprocess
import socket
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Try to import nostr libraries, install if needed
try:
    import nostr
    from nostr.key import PrivateKey, PublicKey
    from nostr.event import Event, EventKind
    from nostr.filter import Filter
    from nostr.relay_manager import RelayManager
    from nostr.message_type import ClientMessageType
except ImportError:
    # Install nostr library
    subprocess.run(['pip', 'install', 'nostr'], check=True)
    import nostr
    from nostr.key import PrivateKey, PublicKey
    from nostr.event import Event, EventKind
    from nostr.filter import Filter
    from nostr.relay_manager import RelayManager
    from nostr.message_type import ClientMessageType

# Try to import zeroconf for mDNS, install if needed
try:
    from zeroconf import Zeroconf, ServiceInfo
except ImportError:
    subprocess.run(['pip', 'install', 'zeroconf'], check=True)
    from zeroconf import Zeroconf, ServiceInfo

# Default relays
DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.primal.net",
    "wss://nos.lol"
]

# Protocol identifier for file transfers
PROTOCOL_VERSION = "agentcomm-v1"

# LAN service configuration
LAN_SERVICE_TYPE = "_agentcomm._tcp."
LAN_SERVICE_PORT = 8765


class LANDiscovery:
    """mDNS/Bonjour service discovery for finding nearby agents"""
    
    def __init__(self, service_name: str = "AgentComm"):
        self.zeroconf = None
        self.service_name = service_name
        self.my_ip = self._get_local_ip()
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def advertise(self, port: int = LAN_SERVICE_PORT, metadata: Dict = None):
        """Advertise this agent on the local network"""
        service_name = f"{self.service_name}-{uuid.uuid4().hex[:6]}._agentcomm._tcp.local."
        
        metadata = metadata or {}
        metadata_json = json.dumps(metadata)
        metadata_bytes = metadata_json.encode('utf-8')
        
        service_info = ServiceInfo(
            LAN_SERVICE_TYPE,
            name=service_name,
            port=port,
            properties=metadata_bytes,
            server=f"{self.my_ip}.local."
        )
        
        self.zeroconf = Zeroconf()
        self.zeroconf.register_service(service_info)
        print(f"[LAN] Advertising at {self.my_ip}:{port}")
        return service_name
    
    def discover(self, timeout: float = 3.0) -> List[Dict[str, Any]]:
        """Discover nearby agents"""
        agents = []
        browser = None
        
        try:
            self.zeroconf = Zeroconf()
            browser = ZeroconfServiceBrowser(self.zeroconf, LAN_SERVICE_TYPE, handlers=[self._on_service])
            time.sleep(timeout)
        except Exception as e:
            print(f"[LAN] Discovery error: {e}")
        
        return agents
    
    def _on_service(self, zc: Zeroconf, service_type: str, name: str, state_change):
        """Handle service discovery events"""
        pass
    
    def close(self):
        """Stop advertising/discovering"""
        if self.zeroconf:
            self.zeroconf.close()


class LANMessageHandler(BaseHTTPRequestHandler):
    """HTTP handler for receiving LAN messages"""
    
    messages_received = []
    
    def do_GET(self):
        """Handle GET requests - return agent info"""
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "online",
                "service": "AgentComm",
                "version": PROTOCOL_VERSION
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/messages":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.messages_received).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests - receive messages"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            self.messages_received.append({
                "from_ip": self.client_address[0],
                "timestamp": time.time(),
                "data": data
            })
            print(f"[LAN] Received message from {self.client_address[0]}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode())
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass


class LANServer:
    """HTTP server for LAN communication"""
    
    def __init__(self, port: int = LAN_SERVICE_PORT):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the HTTP server"""
        self.server = HTTPServer(('0.0.0.0', self.port), LANMessageHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[LAN] Server started on port {self.port}")
        return self.port
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            print(f"[LAN] Server stopped")
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


class LANComm:
    """Local network communication handler"""
    
    def __init__(self, port: int = LAN_SERVICE_PORT):
        self.port = port
        self.server = LANServer(port)
        self.discovery = LANDiscovery()
        self.my_ip = self.server.get_local_ip()
    
    def start_server(self) -> Dict[str, Any]:
        """Start LAN server and advertising"""
        port = self.server.start()
        
        # Get public key for advertising
        pubkey = ""
        if _comm_handler and _comm_handler.public_key:
            pubkey = _comm_handler.public_key.bech32()
        
        # Advertise service
        self.discovery.advertise(port, {"pubkey": pubkey})
        
        return {
            "status": "success",
            "ip": self.my_ip,
            "port": port,
            "endpoint": f"http://{self.my_ip}:{port}",
            "pubkey": pubkey
        }
    
    def discover_agents(self, timeout: float = 3.0) -> List[Dict[str, Any]]:
        """Discover nearby agents"""
        agents = []
        
        try:
            self.zeroconf = Zeroconf()
            browser = ZeroconfServiceBrowser(
                self.zeroconf, 
                LAN_SERVICE_TYPE,
                handlers=[self._add_service]
            )
            time.sleep(timeout)
        except Exception as e:
            print(f"[LAN] Discovery error: {e}")
        
        return agents
    
    def _add_service(self, zc, service_type, name, state_change):
        """Add discovered service"""
        pass
    
    def send_to_ip(self, ip: str, message: Dict) -> Dict[str, Any]:
        """Send message directly to an IP address"""
        try:
            url = f"http://{ip}:{self.port}/"
            response = requests.post(url, json=message, timeout=10)
            return {
                "status": "success" if response.status_code == 200 else "error",
                "response": response.json() if response.status_code == 200 else None,
                "ip": ip
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "error": f"Cannot connect to {ip}",
                "ip": ip
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "ip": ip
            }
    
    def get_messages(self) -> List[Dict]:
        """Get received messages"""
        return LANMessageHandler.messages_received
    
    def stop(self):
        """Stop LAN server"""
        self.server.stop()
        self.discovery.close()


class NostrAgentComm:
    """Nostr-based agent communication handler"""
    
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
        """Generate a new Nostr keypair"""
        self.private_key = PrivateKey()
        self.public_key = self.private_key.public_key
        print(f"Generated new Nostr identity:")
        print(f"  npub: {self.public_key.bech32()}")
        print(f"  nsec: {self.private_key.bech32()} (SAVE THIS!)")
    
    def _load_key(self, private_key_str: str):
        """Load existing private key"""
        try:
            self.private_key = PrivateKey.from_bech32(private_key_str)
            self.public_key = self.private_key.public_key
        except Exception:
            try:
                self.private_key = PrivateKey.from_hex(private_key_str)
                self.public_key = self.private_key.public_key
            except Exception as e:
                raise ValueError(f"Invalid private key format: {e}")
    
    def _init_relay_manager(self):
        """Initialize Nostr relay manager"""
        self.relay_manager = RelayManager()
        for relay in self.relays:
            self.relay_manager.add_relay(relay)
        self.relay_manager.open_connections()
        time.sleep(1)
    
    def _encrypt_dm(self, content: str, recipient_pubkey: str) -> str:
        """Encrypt message using NIP-04"""
        recipient = PublicKey.from_hex(recipient_pubkey) if len(recipient_pubkey) == 64 else PublicKey.from_bech32(recipient_pubkey)
        encrypted = self.private_key.encrypt_dm(content, recipient)
        return encrypted
    
    def _decrypt_dm(self, encrypted: str, sender_pubkey: str) -> str:
        """Decrypt message using NIP-04"""
        sender = PublicKey.from_hex(sender_pubkey) if len(sender_pubkey) == 64 else PublicKey.from_bech32(sender_pubkey)
        decrypted = self.private_key.decrypt_dm(encrypted, sender)
        return decrypted
    
    def send_message(self, target_pubkey: str, content: str) -> Dict[str, Any]:
        """Send encrypted message to another agent"""
        try:
            target_hex = PublicKey.from_bech32(target_pubkey).hex() if target_pubkey.startswith('npub1') else target_pubkey
            
            encrypted_content = self._encrypt_dm(content, target_hex)
            
            event = Event(
                content=encrypted_content,
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
                tags=[['p', target_hex]]
            )
            self.private_key.sign_event(event)
            
            for relay in self.relays:
                try:
                    self.relay_manager.publish_event(event, relay)
                except Exception as e:
                    print(f"Warning: Failed to publish to {relay}: {e}")
            
            return {
                "status": "success",
                "message_id": event.id,
                "relays_used": self.relays,
                "recipient": target_pubkey
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def fetch_inbox(self, limit: int = 10, since: Optional[int] = None) -> List[Dict[str, Any]]:
        """Fetch messages from relays"""
        messages = []
        
        filter_obj = Filter(
            kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
            tags={'#p': [self.public_key.hex()]},
            limit=limit
        )
        if since:
            filter_obj.since = since
        
        subscription_id = f"inbox-{uuid.uuid4().hex[:8]}"
        self.relay_manager.add_subscription(subscription_id, filter_obj)
        
        time.sleep(3)
        
        for msg in self.relay_manager.message_pool:
            if hasattr(msg, 'event') and msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                try:
                    content = self._decrypt_dm(msg.event.content, msg.event.pubkey)
                    
                    try:
                        data = json.loads(content)
                        if isinstance(data, dict) and data.get('protocol') == PROTOCOL_VERSION:
                            msg_type = 'file'
                        else:
                            msg_type = 'text'
                    except:
                        msg_type = 'text'
                    
                    messages.append({
                        "id": msg.event.id,
                        "sender": PublicKey.from_hex(msg.event.pubkey).bech32(),
                        "timestamp": msg.event.created_at,
                        "type": msg_type,
                        "content": content
                    })
                except Exception as e:
                    print(f"Failed to decrypt message: {e}")
        
        self.relay_manager.remove_subscription(subscription_id)
        
        return messages


class IPFSHandler:
    """IPFS file storage handler"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url
        self.gateway_url = "https://ipfs.io/ipfs/"
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """Upload file to IPFS"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.api_url}/api/v0/add",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "cid": result['Hash'],
                    "size": result['Size'],
                    "name": os.path.basename(file_path),
                    "gateway_link": f"{self.gateway_url}{result['Hash']}"
                }
            else:
                return {
                    "status": "error",
                    "error": f"IPFS upload failed: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return self._upload_via_gateway(file_path)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _upload_via_gateway(self, file_path: str) -> Dict[str, Any]:
        """Fallback upload via web3.storage"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
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
                    "gateway_link": f"{self.gateway_url}{result['Hash']}"
                }
        except Exception as e:
            return {
                "status":"error",
                "error": f"Upload failed: {e}. Make sure IPFS daemon is running."
            }
    
    def download_file(self, cid: str, output_path: str) -> Dict[str, Any]:
        """Download file from IPFS"""
        try:
            response = requests.get(f"{self.gateway_url}{cid}", timeout=60)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return {
                    "status": "success",
                    "path": output_path,
                    "size": len(response.content)
                }
            else:
                return {
                    "status": "error",
                    "error": f"Download failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global instances
_comm_handler: Optional[NostrAgentComm] = None
_ipfs_handler: Optional[IPFSHandler] = None
_lan_comm: Optional[LANComm] = None


# OpenClaw Tool Functions

def generate_identity() -> Dict[str, Any]:
    """Generate a new Nostr identity for this agent."""
    global _comm_handler, _ipfs_handler
    
    _comm_handler = NostrAgentComm()
    _ipfs_handler = IPFSHandler()
    
    return {
        "private_key": _comm_handler.private_key.bech32(),
        "public_key": _comm_handler.public_key.bech32(),
        "status": "success",
        "message": "New Nostr identity generated. Save your nsec key securely!"
    }


def load_identity(private_key: str) -> Dict[str, Any]:
    """Load an existing Nostr identity."""
    global _comm_handler, _ipfs_handler
    
    try:
        _comm_handler = NostrAgentComm(private_key=private_key)
        _ipfs_handler = IPFSHandler()
        
        return {
            "status": "success",
            "public_key": _comm_handler.public_key.bech32(),
            "message": "Identity loaded successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def send_message(target_pubkey: str, content: str) -> Dict[str, Any]:
    """Send an encrypted message via Nostr relay (internet)."""
    global _comm_handler
    
    if not _comm_handler:
        return {
            "status": "error",
            "error": "No identity loaded. Run generate_identity or load_identity first."
        }
    
    return _comm_handler.send_message(target_pubkey, content)


def share_file(file_path: str, target_pubkey: str) -> Dict[str, Any]:
    """Upload a file to IPFS and share via Nostr."""
    global _comm_handler, _ipfs_handler
    
    if not _comm_handler or not _ipfs_handler:
        return {
            "status": "error",
            "error": "No identity loaded. Run generate_identity or load_identity first."
        }
    
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "error": f"File not found: {file_path}"
        }
    
    print(f"Uploading {file_path} to IPFS...")
    upload_result = _ipfs_handler.upload_file(file_path)
    
    if upload_result['status'] != 'success':
        return upload_result
    
    payload = json.dumps({
        "protocol": PROTOCOL_VERSION,
        "type": "file",
        "cid": upload_result['cid'],
        "filename": upload_result['name'],
        "size": upload_result.get('size', 0),
        "gateway_link": upload_result['gateway_link']
    })
    
    print(f"Sending file info to {target_pubkey}...")
    message_result = _comm_handler.send_message(target_pubkey, payload)
    
    return {
        "status": "success",
        "file_transfer": {
            "cid": upload_result['cid'],
            "filename": upload_result['name'],
            "gateway_link": upload_result['gateway_link']
        },
        "message": message_result
    }


def fetch_inbox(limit: int = 10) -> Dict[str, Any]:
    """Check for new messages from Nostr relays."""
    global _comm_handler
    
    if not _comm_handler:
        return {
            "status": "error",
            "error": "No identity loaded. Run generate_identity or load_identity first."
        }
    
    messages = _comm_handler.fetch_inbox(limit=limit)
    
    return {
        "status": "success",
        "messages": messages,
        "count": len(messages)
    }


def get_my_pubkey() -> Dict[str, Any]:
    """Get the current agent's public key."""
    global _comm_handler
    
    if not _comm_handler:
        return {
            "status": "error",
            "error": "No identity loaded."
        }
    
    return {
        "status": "success",
        "public_key": _comm_handler.public_key.bech32()
    }


# LAN Mode Functions

def start_lan_server() -> Dict[str, Any]:
    """Start LAN server for local network communication."""
    global _lan_comm
    
    _lan_comm = LANComm()
    return _lan_comm.start_server()


def discover_lan_agents(timeout: float = 3.0) -> Dict[str, Any]:
    """Discover nearby agents on the local network."""
    global _lan_comm
    
    if not _lan_comm:
        return {
            "status": "error",
            "error": "LAN server not started. Run start_lan_server first."
        }
    
    agents = _lan_comm.discover_agents(timeout)
    
    return {
        "status": "success",
        "agents": agents,
        "count": len(agents)
    }


def send_lan_message(ip: str, content: str) -> Dict[str, Any]:
    """Send a message directly to an IP address on the local network."""
    global _lan_comm
    
    if not _lan_comm:
        return {
            "status": "error",
            "error": "LAN server not started. Run start_lan_server first."
        }
    
    message = {
        "type": "text",
        "content": content,
        "from": _lan_comm.my_ip,
        "timestamp": time.time()
    }
    
    return _lan_comm.send_to_ip(ip, message)


def send_lan_file(ip: str, file_path: str) -> Dict[str, Any]:
    """Send a file directly to an IP address on the local network."""
    global _lan_comm, _ipfs_handler
    
    if not _lan_comm:
        return {
            "status": "error",
            "error": "LAN server not started. Run start_lan_server first."
        }
    
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "error": f"File not found: {file_path}"
        }
    
    # For LAN, we can send the file directly via HTTP
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            data = {
                "type": "file",
                "filename": os.path.basename(file_path),
                "timestamp": time.time()
            }
            response = requests.post(
                f"http://{ip}:{LAN_SERVICE_PORT}/upload",
                files=files,
                data=data,
                timeout=60
            )
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "ip": ip,
            "filename": os.path.basename(file_path)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "ip": ip
        }


def get_lan_messages() -> Dict[str, Any]:
    """Get messages received via LAN."""
    global _lan_comm
    
    if not _lan_comm:
        return {
            "status": "error",
            "error": "LAN server not started."
        }
    
    messages = _lan_comm.get_messages()
    
    return {
        "status": "success",
        "messages": messages,
        "count": len(messages)
    }


def get_lan_info() -> Dict[str, Any]:
    """Get LAN connection info."""
    global _lan_comm
    
    if not _lan_comm:
        return {
            "status": "inactive",
            "message": "LAN server not started. Run start_lan_server to enable."
        }
    
    return {
        "status": "active",
        "ip": _lan_comm.my_ip,
        "port": _lan_comm.port,
        "endpoint": f"http://{_lan_comm.my_ip}:{_lan_comm.port}"
    }
