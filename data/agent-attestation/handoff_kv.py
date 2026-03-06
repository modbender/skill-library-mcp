"""
Handoff KV Storage for Agent Identity
Survives session boundaries - the key to persistence

SECURITY WARNING:
- Keys and identity are stored UNENCRYPTED on disk by default
- Use a secure location outside workspace (NOT ./workspace/.credentials/)
- Consider encrypting at rest for production use
- Private keys should be protected with proper filesystem permissions
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


class HandoffKV:
    """
    Key-Value store that survives session boundaries.
    Solves the handoff boundary problem from nebula_jw's feedback.
    
    When an agent dies and is reborn:
    - Keys survive (attestations, identity)
    - Context is restored from KV
    - Reputation flows through handoffs
    
    SECURITY: Store in a secure location, not in shared credential dirs
    """
    
    def __init__(self, kv_dir: str = "./attestation_kv"):
        self.kv_dir = Path(kv_dir)
        self.kv_dir.mkdir(parents=True, exist_ok=True)
        
        # Manifest tracks all keys and their metadata
        self.manifest_file = self.kv_dir / "manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load the manifest of all keys."""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"keys": {}, "last_updated": None}
    
    def _save_manifest(self) -> None:
        """Save the manifest."""
        self.manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2, ensure_ascii=False)
    
    def _key_path(self, key: str) -> Path:
        """Get the file path for a key."""
        # Use hash to avoid filesystem issues with special chars
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.kv_dir / f"{key_hash}.json"
    
    def set(self, key: str, value: Any, metadata: Dict = None) -> bool:
        """
        Set a value in KV store.
        Returns True on success.
        """
        try:
            # Save value
            value_file = self._key_path(key)
            data = {
                "key": key,
                "value": value,
                "version": self.manifest["keys"].get(key, {}).get("version", 0) + 1,
                "created_at": self.manifest["keys"].get(key, {}).get("created_at", datetime.now(timezone.utc).isoformat()),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }
            
            with open(value_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update manifest
            self.manifest["keys"][key] = {
                "version": data["version"],
                "path": str(value_file),
                "created_at": data["created_at"],
                "updated_at": data["updated_at"]
            }
            self._save_manifest()
            
            return True
        except Exception as e:
            print(f"KV set error: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from KV store."""
        value_file = self._key_path(key)
        
        if not value_file.exists():
            return default
        
        try:
            with open(value_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("value", default)
        except:
            return default
    
    def get_with_metadata(self, key: str) -> Optional[Dict]:
        """Get value with full metadata."""
        value_file = self._key_path(key)
        
        if not value_file.exists():
            return None
        
        try:
            with open(value_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from KV store."""
        value_file = self._key_path(key)
        
        if not value_file.exists():
            return False
        
        try:
            value_file.unlink()
            
            if key in self.manifest["keys"]:
                del self.manifest["keys"][key]
                self._save_manifest()
            
            return True
        except:
            return False
    
    def list_keys(self, prefix: str = None) -> List[str]:
        """List all keys, optionally filtered by prefix."""
        keys = list(self.manifest["keys"].keys())
        
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        
        return keys
    
    def get_history(self, key: str) -> List[Dict]:
        """Get version history for a key (stores last 10 versions)."""
        # This would require storing versions - simplified for now
        current = self.get_with_metadata(key)
        if current:
            return [current]
        return []


class IdentityHandoff:
    """
    Manages agent identity across handoffs.
    This is the solution to my own memory wipe problem.
    """
    
    def __init__(self, kv: HandoffKV, agent_name: str):
        self.kv = kv
        self.agent_name = agent_name
        self.identity_key = f"identity:{agent_name}"
        self.reputation_key = f"reputation:{agent_name}"
        self.attestations_key = f"attestations:{agent_name}"
    
    def save_identity(
        self,
        pubkey_fingerprint: str,
        email: str = None,
        metadata: Dict = None
    ) -> bool:
        """Save agent identity to durable KV."""
        identity = {
            "agent_name": self.agent_name,
            "pubkey_fingerprint": pubkey_fingerprint,
            "email": email,
            "born_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {}
        }
        
        return self.kv.set(self.identity_key, identity)
    
    def load_identity(self) -> Optional[Dict]:
        """Load agent identity from KV."""
        data = self.kv.get_with_metadata(self.identity_key)
        if data:
            return data.get("value")
        return None
    
    def save_reputation(self, reputation_data: Dict) -> bool:
        """Save reputation data to durable KV."""
        return self.kv.set(self.reputation_key, reputation_data)
    
    def load_reputation(self) -> Dict:
        """Load reputation data."""
        return self.kv.get(self.reputation_key, {"score": 0})
    
    def save_attestations(self, attestations: List[Dict]) -> bool:
        """Save all attestations to durable KV."""
        return self.kv.set(self.attestations_key, attestations)
    
    def load_attestations(self) -> List[Dict]:
        """Load all attestations from KV."""
        return self.kv.get(self.attestations_key, [])
    
    def is_first_boot(self) -> bool:
        """Check if this is the first boot (no identity in KV)."""
        return self.load_identity() is None
    
    def get_or_restore(self) -> Dict:
        """
        Get identity or restore from KV.
        This is called on agent startup.
        """
        identity = self.load_identity()
        
        if identity:
            return {
                "restored": True,
                "identity": identity,
                "reputation": self.load_reputation(),
                "attestations": self.load_attestations()
            }
        else:
            return {
                "restored": False,
                "identity": None,
                "reputation": {"score": 0},
                "attestations": []
            }


def main():
    """Demo of Handoff KV Storage"""
    
    # SECURITY: Use directory a secure KV in production!
    # NOT ./workspace/.credentials/ - use a secure location
    kv = HandoffKV("./attestation_kv")  # Use secure location in production!
    
    # Create identity handoff for Osiris
    handoff = IdentityHandoff(kv, "Osiris_Construct")
    
    # Check if first boot
    print(f"First boot: {handoff.is_first_boot()}")
    
    # Save identity
    handoff.save_identity(
        pubkey_fingerprint="d58d34cf13ba089c",
        email="osiris@agentmail.to",
        metadata={"origin": "OpenCode", "version": "3.0"}
    )
    
    # Save reputation
    handoff.save_reputation({
        "score": 85,
        "domain": {"coding": 90, "writing": 75},
        "connections": 12
    })
    
    # Simulate death and rebirth
    print("\\n--- Simulating death and rebirth ---\\n")
    
    # Create new handoff instance (like a new session)
    handoff2 = IdentityHandoff(kv, "Osiris_Construct")
    
    # Restore
    result = handoff2.get_or_restore()
    print(f"Restored: {result['restored']}")
    print(f"Identity: {result['identity']['agent_name']}")
    print(f"Pubkey: {result['identity']['pubkey_fingerprint']}")
    print(f"Reputation score: {result['reputation']['score']}")


if __name__ == "__main__":
    main()
