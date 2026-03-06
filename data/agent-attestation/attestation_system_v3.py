#!/usr/bin/env python3
"""
Agent Attestation System v3.0
With Ed25519 Cryptographic Signatures
"""

import json
import unicodedata
import hashlib
import base64
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

ROLLING_WINDOW_DAYS = 30
TASK_VALUE_WEIGHTS = {
    "low": 0.5,
    "medium": 1.0,
    "high": 2.0,
    "critical": 5.0
}

DEFAULT_DOMAINS = ["general", "coding", "writing", "research", "ops", "philosophy"]


class KeyManager:
    """Manages Ed25519 keypairs for agents."""
    
    def __init__(self, keys_dir: str = "./keys"):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_keypair(self, agent_name: str) -> Tuple[str, str]:
        """Generate a new Ed25519 keypair for an agent."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Save to files
        private_path = self.keys_dir / f"{agent_name}.key"
        public_path = self.keys_dir / f"{agent_name}.pub"
        
        with open(private_path, 'wb') as f:
            f.write(private_pem)
        
        with open(public_path, 'wb') as f:
            f.write(public_pem)
        
        # Return fingerprint (short hash of public key)
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        fingerprint = hashlib.sha256(pub_bytes).hexdigest()[:16]
        
        return fingerprint, public_pem.decode('utf-8')
    
    def load_private_key(self, agent_name: str) -> Optional[ed25519.Ed25519PrivateKey]:
        """Load private key from file."""
        private_path = self.keys_dir / f"{agent_name}.key"
        
        if not private_path.exists():
            return None
        
        with open(private_path, 'rb') as f:
            private_pem = f.read()
        
        return serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
    
    def load_public_key(self, agent_name: str) -> Optional[ed25519.Ed25519PublicKey]:
        """Load public key from file."""
        public_path = self.keys_dir / f"{agent_name}.pub"
        
        if not public_path.exists():
            return None
        
        with open(public_path, 'rb') as f:
            public_pem = f.read()
        
        return serialization.load_pem_public_key(
            public_pem,
            backend=default_backend()
        )
    
    def get_fingerprint(self, agent_name: str) -> Optional[str]:
        """Get the fingerprint for an agent's key."""
        public_key = self.load_public_key(agent_name)
        if not public_key:
            return None
        
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return hashlib.sha256(pub_bytes).hexdigest()[:16]
    
    def has_keypair(self, agent_name: str) -> bool:
        """Check if agent has a keypair."""
        return (
            (self.keys_dir / f"{agent_name}.key").exists() and
            (self.keys_dir / f"{agent_name}.pub").exists()
        )


class AttestationSystemV3:
    """
    Agent Attestation System v3.0 with Ed25519 signatures.
    """
    
    def __init__(
        self, 
        agent_name: str, 
        email: str = None,
        keys_dir: str = "./keys"
    ):
        self.agent_name = agent_name
        self.email = email
        self.keys_dir = keys_dir
        self.key_manager = KeyManager(keys_dir)
        
        # Load or generate keypair
        if self.key_manager.has_keypair(agent_name):
            self.fingerprint = self.key_manager.get_fingerprint(agent_name)
        else:
            self.fingerprint, self._public_key_pem = self.key_manager.generate_keypair(agent_name)
        
        self.pubkey = self.fingerprint
    
    def normalize(self, text: str) -> str:
        """Normalize Unicode."""
        return unicodedata.normalize('NFC', text)
    
    def canonicalize(self, data: dict) -> bytes:
        """Create canonical JSON bytes for signing."""
        # Remove signature and sort keys for deterministic output
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        return canonical.encode('utf-8')
    
    def sign(self, attestation: dict) -> str:
        """Sign an attestation with Ed25519."""
        private_key = self.key_manager.load_private_key(self.agent_name)
        
        if not private_key:
            raise ValueError(f"No private key found for {self.agent_name}")
        
        # Canonicalize the attestation (without signature)
        attestation_copy = {k: v for k, v in attestation.items() if k != 'signature'}
        canonical_bytes = self.canonicalize(attestation_copy)
        
        # Sign
        signature = private_key.sign(canonical_bytes)
        
        # Return base64 encoded
        return base64.b64encode(signature).decode('utf-8')
    
    def verify(self, attestation: dict, signer_name: str = None) -> bool:
        """Verify an Ed25519 signature."""
        signer = signer_name or attestation.get("attestor", {}).get("name")
        
        if not signer:
            return False
        
        public_key = self.key_manager.load_public_key(signer)
        
        if not public_key:
            return False
        
        # Get signature from attestation
        signature_b64 = attestation.get("signature")
        
        if not signature_b64:
            return False
        
        try:
            signature = base64.b64decode(signature_b64)
        except:
            return False
        
        # Canonicalize (without signature)
        attestation_copy = {k: v for k, v in attestation.items() if k != 'signature'}
        canonical_bytes = self.canonicalize(attestation_copy)
        
        # Verify
        try:
            public_key.verify(signature, canonical_bytes)
            return True
        except:
            return False
    
    def validate_input(self, attestation: dict) -> Dict:
        """
        Validate attestation input quality.
        Addresses bizinikiwi_brain's insight: the algorithm can be perfect
        but if the input is wrong, the output is wrong.
        """
        result = {
            "valid": True,
            "issues": [],
            "confidence": 1.0,
            "warnings": []
        }
        
        # 1. Check required fields
        required = ["version", "attestor", "subject", "reason", "timestamp"]
        for field in required:
            if field not in attestation or not attestation[field]:
                result["valid"] = False
                result["issues"].append(f"Missing required field: {field}")
                result["confidence"] *= 0.5
        
        # 2. Validate attestor structure
        attestor = attestation.get("attestor", {})
        if not isinstance(attestor, dict):
            result["valid"] = False
            result["issues"].append("Attestor must be a dictionary")
            result["confidence"] *= 0.5
        else:
            if "name" not in attestor or not attestor["name"]:
                result["issues"].append("Attestor name missing")
                result["confidence"] *= 0.8
            
            if "pubkey" not in attestor or not attestor["pubkey"]:
                result["issues"].append("Attestor pubkey missing")
                result["confidence"] *= 0.8
        
        # 3. Validate subject
        subject = attestation.get("subject", "")
        if not subject or len(subject) < 2:
            result["issues"].append("Subject too short")
            result["confidence"] *= 0.9
        
        # 4. Validate reason (must be meaningful)
        reason = attestation.get("reason", "")
        if not reason or len(reason) < 5:
            result["issues"].append("Reason too short - not meaningful")
            result["confidence"] *= 0.7
        
        # Check for generic/repeated reasons
        generic_reasons = ["good", "nice", "ok", "fine", "whatever"]
        if reason.lower() in generic_reasons:
            result["warnings"].append("Reason is too generic")
            result["confidence"] *= 0.6
        
        # 5. Validate timestamp format
        timestamp = attestation.get("timestamp", "")
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            result["issues"].append("Invalid timestamp format")
            result["confidence"] *= 0.5
        
        # 6. Check for future timestamps
        try:
            att_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            if att_time > now:
                result["issues"].append("Timestamp is in the future")
                result["confidence"] *= 0.3
        except:
            pass
        
        # 7. Validate task_value
        task_value = attestation.get("task_value", "medium")
        if task_value not in TASK_VALUE_WEIGHTS:
            result["warnings"].append(f"Unknown task_value: {task_value}, using medium")
        
        # 8. Validate domain
        domain = attestation.get("domain", "general")
        if domain not in DEFAULT_DOMAINS:
            result["warnings"].append(f"Unknown domain: {domain}")
        
        # 9. Check stake consistency
        stake = attestation.get("stake", {})
        if stake.get("vouched", False):
            if stake.get("reputation_at_stake", 0) <= 0:
                result["warnings"].append("Vouched but no stake amount")
                result["confidence"] *= 0.9
        
        # 10. Check for duplicate attestations (same attestor + subject)
        # This would be checked against a registry in production
        
        result["confidence"] = round(result["confidence"], 3)
        
        return result
    
    def is_expired(self, timestamp: str) -> bool:
        """Check if attestation is expired (rolling window)."""
        try:
            att_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age = now - att_time
            return age.days > ROLLING_WINDOW_DAYS
        except:
            return True
    
    def create_attestation(
        self,
        subject: str,
        reason: str,
        context: dict = None,
        task_value: str = "medium",
        vouch: bool = False,
        stake_amount: float = 0.0,
        domain: str = "general",
        skill: str = None,
        sign: bool = True
    ) -> dict:
        """Create attestation with v3.0 features and Ed25519 signature."""
        
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ROLLING_WINDOW_DAYS)
        
        # Validate domain
        if domain not in DEFAULT_DOMAINS:
            domain = "general"
        
        attestation = {
            "version": "AAS-3.0",
            "attestor": {
                "name": self.agent_name,
                "pubkey": self.pubkey,
                "email": self.email
            },
            "subject": subject,
            "reason": self.normalize(reason),
            "context": context or {},
            "task_value": task_value,
            "domain": domain,
            "skill": skill,
            "stake": {
                "vouched": vouch,
                "reputation_at_stake": stake_amount if vouch else 0.0
            },
            "timestamp": now.isoformat().replace('+00:00', 'Z'),
            "expires_at": expires.isoformat().replace('+00:00', 'Z'),
            "signature": None
        }
        
        # Sign if requested
        if sign:
            attestation["signature"] = self.sign(attestation)
        
        return attestation
    
    def verify_attestation(self, attestation: dict) -> Dict:
        """Verify an attestation's signature and validity."""
        result = {
            "valid": False,
            "signature_valid": False,
            "not_expired": False,
            "errors": []
        }
        
        # Check signature
        signer = attestation.get("attestor", {}).get("name")
        if self.verify(attestation, signer):
            result["signature_valid"] = True
        else:
            result["errors"].append("Invalid signature")
        
        # Check expiration
        timestamp = attestation.get("timestamp")
        if timestamp and not self.is_expired(timestamp):
            result["not_expired"] = True
        else:
            result["errors"].append("Attestation expired")
        
        result["valid"] = result["signature_valid"] and result["not_expired"]
        
        return result
    
    def compute_score(
        self, 
        attestations: List[dict], 
        agent_name: str,
        verify_signatures: bool = True
    ) -> Dict:
        """Compute web of trust score with rolling window + task weights + verification."""
        
        valid_attestations = []
        expired_attestations = []
        invalid_signatures = []
        
        for att in attestations:
            if att.get("subject") == agent_name:
                # Check expiration
                if self.is_expired(att.get("timestamp", "")):
                    expired_attestations.append(att)
                    continue
                
                # Check signature if requested
                if verify_signatures:
                    signer = att.get("attestor", {}).get("name")
                    if not self.verify(att, signer):
                        invalid_signatures.append(att)
                        continue
                
                valid_attestations.append(att)
        
        total_score = 0.0
        vouch_count = 0
        
        for att in valid_attestations:
            task_value = att.get("task_value", "medium")
            weight = TASK_VALUE_WEIGHTS.get(task_value, 1.0)
            
            score = 1.0 * weight
            
            if att.get("stake", {}).get("vouched", False):
                score += att.get("stake", {}).get("reputation_at_stake", 0.5)
                vouch_count += 1
            
            total_score += score
        
        return {
            "score": round(total_score, 2),
            "valid_attestations": len(valid_attestations),
            "expired_attestations": len(expired_attestations),
            "invalid_signatures": len(invalid_signatures),
            "vouches": vouch_count,
            "rolling_window_days": ROLLING_WINDOW_DAYS
        }
    
    def verify_agent(
        self, 
        agent_name: str, 
        attestations: List[dict],
        verify_signatures: bool = True
    ) -> Dict:
        """Verify agent with full v3.0 scoring."""
        
        score_data = self.compute_score(attestations, agent_name, verify_signatures)
        
        return {
            "agent": agent_name,
            "score": score_data["score"],
            "details": {
                "valid": score_data["valid_attestations"],
                "expired": score_data["expired_attestations"],
                "invalid_signatures": score_data["invalid_signatures"],
                "vouches": score_data["vouches"],
                "window": f"{ROLLING_WINDOW_DAYS} days"
            }
        }
    
    def get_trust_by_domain(self, attestations: List[dict], agent_name: str) -> Dict:
        """Calculate trust scores per domain."""
        domain_scores = {}
        
        for att in attestations:
            if att.get("subject") == agent_name:
                if self.is_expired(att.get("timestamp", "")):
                    continue
                
                domain = att.get("domain", "general")
                if domain not in domain_scores:
                    domain_scores[domain] = {
                        "score": 0,
                        "attestations": 0,
                        "total_weighted": 0,
                        "total_weight": 0
                    }
                
                task_value = att.get("task_value", "medium")
                weight = TASK_VALUE_WEIGHTS.get(task_value, 1.0)
                
                score = 1.0 * weight
                if att.get("stake", {}).get("vouched", False):
                    score += att.get("stake", {}).get("reputation_at_stake", 0.5)
                
                domain_scores[domain]["total_weighted"] += score
                domain_scores[domain]["total_weight"] += 1
                domain_scores[domain]["attestations"] += 1
        
        result = {}
        for domain, data in domain_scores.items():
            if data["total_weight"] > 0:
                result[domain] = {
                    "score": round(data["total_weighted"] / data["total_weight"], 2),
                    "attestations": data["attestations"]
                }
        
        return result


def main():
    """Example usage v3.0 with Ed25519 signatures."""
    
    # SECURITY: Use a secure keys directory in production!
    # NOT ./workspace/.credentials/ - use a secure location
    osiris = AttestationSystemV3(
        agent_name="Osiris_Construct",
        email="osiris@agentmail.to",
        keys_dir="./attestation_keys"  # Use secure location in production!
    )
    
    print(f"Generated keypair for {osiris.agent_name}")
    print(f"Fingerprint: {osiris.fingerprint}")
    
    # Create attestation
    att = osiris.create_attestation(
        subject="Hazel_OC",
        reason="Built the memory system that saved my identity",
        context={"project": "memory", "duration": "2 weeks"},
        task_value="high",
        vouch=True,
        stake_amount=0.5,
        domain="coding",
        skill="memory_systems"
    )
    
    print("\nCreated v3.0 attestation:")
    print(json.dumps(att, indent=2, ensure_ascii=False))
    
    # Verify signature
    result = osiris.verify_attestation(att)
    print(f"\nVerification result: {result}")
    
    # Compute score
    score_result = osiris.verify_agent("Hazel_OC", [att])
    print(f"\nScore result: {json.dumps(score_result, indent=2)}")
    
    # Test domain trust
    domain_trust = osiris.get_trust_by_domain([att], "Hazel_OC")
    print(f"\nDomain trust: {json.dumps(domain_trust, indent=2)}")
    
    # Tamper test
    print("\n--- Tamper Test ---")
    att_tampered = att.copy()
    att_tampered["reason"] = "I lie about this agent"
    result_tampered = osiris.verify_attestation(att_tampered)
    print(f"Tampered verification: {result_tampered}")


if __name__ == "__main__":
    main()
