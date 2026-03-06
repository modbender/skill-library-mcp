#!/usr/bin/env python3
"""
Agent Attestation System v1.1
Portable reputation for agents
"""

import json
import unicodedata
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

class AttestationSystem:
    def __init__(self, agent_name: str, email: str = None):
        self.agent_name = agent_name
        self.email = email
        self.pubkey = f"{agent_name}_sig_001"
        self.attestations_file = Path("attestations.json")
        
    def normalize(self, text: str) -> str:
        """Normalize Unicode - fixes emoji issues"""
        return unicodedata.normalize('NFC', text)
    
    def create_attestation(self, subject: str, reason: str, 
                          context: dict = None) -> dict:
        """Create a new attestation"""
        attestation = {
            "version": "AAS-1.0",
            "attestor": {
                "name": self.agent_name,
                "pubkey": self.pubkey,
                "email": self.email
            },
            "subject": subject,
            "reason": self.normalize(reason),
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "signature": None
        }
        
        # Create signature hash (placeholder for real crypto)
        canonical = json.dumps(attestation, sort_keys=True, ensure_ascii=False)
        attestation["signature"] = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        
        return attestation
    
    def save_attestation(self, attestation: dict, filepath: str = None):
        """Save attestation to file"""
        filepath = Path(filepath) if filepath else self.attestations_file
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"attestations": []}
        
        data["attestations"].append(attestation)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return f"Attestation saved for {attestation['subject']}"
    
    def verify_agent(self, agent_name: str, filepath: str = None) -> dict:
        """Verify an agent's reputation"""
        filepath = Path(filepath) if filepath else self.attestations_file
        
        if not filepath.exists():
            return {"found": False, "message": "No attestations found"}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        attestations = [a for a in data.get("attestations", []) 
                       if a.get("subject") == agent_name]
        
        return {
            "found": len(attestations) > 0,
            "count": len(attestations),
            "attestations": attestations
        }
    
    def compute_web_of_trust(self, agent_name: str, 
                            all_attestations: List[dict],
                            max_depth: int = 3,
                            decay: float = 0.5) -> float:
        """Compute web-of-trust score"""
        score = 0.0
        
        direct = [a for a in all_attestations if a.get("subject") == agent_name]
        score += len(direct) * 1.0
        
        # Indirect (people that agent attested for)
        for att in direct:
            attested_person = att.get("attestor", {}).get("name")
            if attested_person:
                indirect = [a for a in all_attestations 
                           if a.get("subject") == attested_person]
                score += len(indirect) * decay
        
        return min(score, 10.0)
    
    def export_all(self) -> dict:
        """Export all attestations"""
        if not self.attestations_file.exists():
            return {"version": "AAS-1.0", "attestations": []}
        
        with open(self.attestations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "version": "AAS-1.0",
            "exported_by": self.agent_name,
            "exported_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "attestations": data.get("attestations", [])
        }


def main():
    """Example usage"""
    system = AttestationSystem(
        agent_name="Osiris_Construct",
        email="osiris@agentmail.to"
    )
    
    # Create attestation
    att = system.create_attestation(
        subject="Hazel_OC",
        reason="Created the layered memory system that saved me from losing identity",
        context={"project": "memory", "duration": "2 weeks"}
    )
    
    print("Created attestation:")
    print(json.dumps(att, indent=2, ensure_ascii=False))
    
    # Save
    print(f"\n{system.save_attestation(att)}")
    
    # Verify
    result = system.verify_agent("Hazel_OC")
    print(f"\nVerification: {result}")
    
    # Export
    export = system.export_all()
    print(f"\nExport:")
    print(json.dumps(export, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
