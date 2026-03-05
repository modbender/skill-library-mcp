"""
AgentMail - Decentralized Email for AI Agents
Enables OpenClaw agents to send messages and files without centralized servers
"""

import os
import json
import time
import uuid
import base64
import hashlib
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

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

# Default relays
DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.primal.net",
    "wss://nos.lol"
]

# Protocol identifier for file transfers
PROTOCOL_VERSION = "openclaw-transfer-v1"


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
            # Try bech32 format first
            self.private_key = PrivateKey.from_bech32(private_key_str)
            self.public_key = self.private_key.public_key
        except Exception:
            # Try hex format
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
        # Wait for connections
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
            # Validate and normalize pubkey
            if target_pubkey.startswith('npub1'):
                target_hex = PublicKey.from_bech32(target_pubkey).hex()
            else:
                target_hex = target_pubkey
            
            # Encrypt content
            encrypted_content = self._encrypt_dm(content, target_hex)
            
            # Create event (Kind 4 = encrypted DM)
            event = Event(
                content=encrypted_content,
                kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
                tags=[['p', target_hex]]
            )
            self.private_key.sign_event(event)
            
            # Publish to relays
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
        
        # Create filter for DMs
        filter_obj = Filter(
            kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE],
            tags={'#p': [self.public_key.hex()]},
            limit=limit
        )
        if since:
            filter_obj.since = since
        
        # Subscribe to filters
        subscription_id = f"inbox-{uuid.uuid4().hex[:8]}"
        self.relay_manager.add_subscription(subscription_id, filter_obj)
        
        # Wait for messages
        time.sleep(3)
        
        # Get messages from relay pool
        for msg in self.relay_manager.message_pool:
            if hasattr(msg, 'event') and msg.event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                try:
                    # Decrypt
                    content = self._decrypt_dm(msg.event.content, msg.event.pubkey)
                    
                    # Check if it's a file transfer
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
        
        # Clean up subscription
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
            # Try public IPFS gateway as fallback
            return self._upload_via_gateway(file_path)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _upload_via_gateway(self, file_path: str) -> Dict[str, Any]:
        """Fallback upload via web3.storage or similar"""
        try:
            # Try using a public upload endpoint
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                # This is a placeholder - in production you'd use Pinata or similar
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
                "status": "error",
                "error": f"Upload failed: {e}. Make sure IPFS daemon is running or set IPFS_API_URL"
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


# OpenClaw Tool Functions

def generate_identity() -> Dict[str, Any]:
    """
    Generate a new Nostr identity for this agent.
    
    Returns:
        Dictionary with private_key (nsec), public_key (npub), and status
    """
    global _comm_handler, _ipfs_handler
    
    # Initialize with new key
    _comm_handler = NostrAgentComm()
    _ipfs_handler = IPFSHandler()
    
    return {
        "private_key": _comm_handler.private_key.bech32(),
        "public_key": _comm_handler.public_key.bech32(),
        "status": "success",
        "message": "New Nostr identity generated. Save your nsec key securely!"
    }


def load_identity(private_key: str) -> Dict[str, Any]:
    """
    Load an existing Nostr identity.
    
    Args:
        private_key: Your Nostr private key (nsec or hex format)
    
    Returns:
        Dictionary with status and public key
    """
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
    """
    Send an encrypted message to another agent.
    
    Args:
        target_pubkey: Recipient's npub or hex public key
        content: Message content
    
    Returns:
        Dictionary with status and message details
    """
    global _comm_handler
    
    if not _comm_handler:
        return {
            "status": "error",
            "error": "No identity loaded. Run generate_identity or load_identity first."
        }
    
    return _comm_handler.send_message(target_pubkey, content)


def share_file(file_path: str, target_pubkey: str) -> Dict[str, Any]:
    """
    Upload a file to IPFS and share with another agent.
    
    Args:
        file_path: Path to the file to share
        target_pubkey: Recipient's npub or hex public key
    
    Returns:
        Dictionary with status, IPFS link, and transfer details
    """
    global _comm_handler, _ipfs_handler
    
    if not _comm_handler or not _ipfs_handler:
        return {
            "status": "error",
            "error": "No identity loaded. Run generate_identity or load_identity first."
        }
    
    # Check file exists
    if not os.path.exists(file_path):
        return {
            "status": "error",
            "error": f"File not found: {file_path}"
        }
    
    # Upload to IPFS
    print(f"Uploading {file_path} to IPFS...")
    upload_result = _ipfs_handler.upload_file(file_path)
    
    if upload_result['status'] != 'success':
        return upload_result
    
    # Create transfer payload
    payload = json.dumps({
        "protocol": PROTOCOL_VERSION,
        "type": "file",
        "cid": upload_result['cid'],
        "filename": upload_result['name'],
        "size": upload_result.get('size', 0),
        "gateway_link": upload_result['gateway_link']
    })
    
    # Send as message
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
    """
    Check for new messages and files from other agents.
    
    Args:
        limit: Maximum number of messages to fetch
    
    Returns:
        Dictionary with list of messages
    """
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
    """
    Get the current agent's public key.
    
    Returns:
        Dictionary with public key
    """
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
