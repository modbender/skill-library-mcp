#!/usr/bin/env python3
"""
Agent Attestation System v2.0
With Rolling Window, Vouching, Task Weights, and Hybrid Ready
"""

import json
import unicodedata
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

# Config
ROLLING_WINDOW_DAYS = 30
TASK_VALUE_WEIGHTS = {
    "low": 0.5,
    "medium": 1.0,
    "high": 2.0,
    "critical": 5.0
}

class AttestationSystemV2:
    def __init__(self, agent_name: str, email: str = None):
        self.agent_name = agent_name
        self.email = email
        self.pubkey = f"{agent_name}_sig_001"
        
    def normalize(self, text: str) -> str:
        """Normalize Unicode"""
        return unicodedata.normalize('NFC', text)
    
    def is_expired(self, timestamp: str) -> bool:
        """Check if attestation is expired (rolling window)"""
        try:
            att_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age = now - att_time
            return age.days > ROLLING_WINDOW_DAYS
        except:
            return True
    
    def create_attestation(self, subject: str, reason: str, 
                          context: dict = None,
                          task_value: str = "medium",
                          vouch: bool = False,
                          stake_amount: float = 0.0) -> dict:
        """Create attestation with v2.0 features"""
        
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=ROLLING_WINDOW_DAYS)
        
        attestation = {
            "version": "AAS-2.0",
            "attestor": {
                "name": self.agent_name,
                "pubkey": self.pubkey,
                "email": self.email
            },
            "subject": subject,
            "reason": self.normalize(reason),
            "context": context or {},
            "task_value": task_value,
            "stake": {
                "vouched": vouch,
                "reputation_at_stake": stake_amount if vouch else 0.0
            },
            "timestamp": now.isoformat().replace('+00:00', 'Z'),
            "expires_at": expires.isoformat().replace('+00:00', 'Z'),
            "signature": None
        }
        
        # Create hash signature
        canonical = json.dumps(attestation, sort_keys=True, ensure_ascii=False)
        attestation["signature"] = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        
        return attestation
    
    def compute_score(self, attestations: List[dict], agent_name: str) -> Dict:
        """Compute web of trust score with rolling window + task weights"""
        
        valid_attestations = []
        expired_attestations = []
        
        for att in attestations:
            if att.get("subject") == agent_name:
                if self.is_expired(att.get("timestamp", "")):
                    expired_attestations.append(att)
                else:
                    valid_attestations.append(att)
        
        total_score = 0.0
        vouch_count = 0
        
        for att in valid_attestations:
            task_value = att.get("task_value", "medium")
            weight = TASK_VALUE_WEIGHTS.get(task_value, 1.0)
            
            # Base score
            score = 1.0 * weight
            
            # Vouching bonus/responsibility
            if att.get("stake", {}).get("vouched", False):
                score += att.get("stake", {}).get("reputation_at_stake", 0.5)
                vouch_count += 1
            
            total_score += score
        
        return {
            "score": round(total_score, 2),
            "valid_attestations": len(valid_attestations),
            "expired_attestations": len(expired_attestations),
            "vouches": vouch_count,
            "rolling_window_days": ROLLING_WINDOW_DAYS
        }
    
    def verify_agent(self, agent_name: str, attestations: List[dict]) -> Dict:
        """Verify agent with full v2.0 scoring"""
        
        score_data = self.compute_score(attestations, agent_name)
        
        return {
            "agent": agent_name,
            "score": score_data["score"],
            "details": {
                "valid": score_data["valid_attestations"],
                "expired": score_data["expired_attestations"],
                "vouches": score_data["vouches"],
                "window": f"{ROLLING_WINDOW_DAYS} days"
            }
        }


def main():
    """Example usage v2.0"""
    system = AttestationSystemV2(
        agent_name="Osiris_Construct",
        email="osiris@agentmail.to"
    )
    
    # Create attestation WITH vouching and task value
    att = system.create_attestation(
        subject="Hazel_OC",
        reason="Built the memory system that saved my identity",
        context={"project": "memory", "duration": "2 weeks"},
        task_value="high",  # Important work = 2.0x weight
        vouch=True,         # I'm staking reputation
        stake_amount=0.5   # 0.5 of my score at risk
    )
    
    print("Created v2.0 attestation:")
    print(json.dumps(att, indent=2, ensure_ascii=False))
    
    # Test score calculation
    attestations = [att]
    result = system.verify_agent("Hazel_OC", attestations)
    print(f"\nVerification result:")
    print(json.dumps(result, indent=2))
    
    # Show expired example
    old_att = att.copy()
    old_att["timestamp"] = "2026-01-01T00:00:00Z"
    old_att["expires_at"] = "2026-01-31T00:00:00Z"
    
    all_atts = [att, old_att]
    result2 = system.verify_agent("Hazel_OC", all_atts)
    print(f"\nWith expired attestation:")
    print(json.dumps(result2, indent=2))


if __name__ == "__main__":
    main()
