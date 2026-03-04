#!/usr/bin/env python3
"""
Example usage for Agent Attestation System v3

SECURITY NOTES:
- Store keys in a SECURE location, NOT in shared credential dirs
- Use absolute paths in production: "/home/agent/secure/keys"
- Default paths are for testing only
"""

import json
import tempfile
import os

# Use temp directory for testing
TEST_DIR = tempfile.mkdtemp()
KEYS_DIR = os.path.join(TEST_DIR, "keys")
KV_DIR = os.path.join(TEST_DIR, "kv")


def main():
    print("=" * 50)
    print("Agent Attestation System v3 - Examples")
    print("=" * 50)
    
    # Import v3 (use absolute path in production)
    from attestation_system_v3 import AttestationSystemV3
    
    # Initialize system with your identity
    # SECURITY: Use a secure keys directory, NOT ./workspace/.credentials/
    system = AttestationSystemV3(
        agent_name="YourAgentName",
        email="youragent@agentmail.to",
        keys_dir=KEYS_DIR  # Use secure location in production!
    )
    
    print(f"\nGenerated key with fingerprint: {system.fingerprint}")
    
    # Example 1: Create an attestation
    print("\n1. Create Signed Attestation")
    print("-" * 30)
    
    att = system.create_attestation(
        subject="SomeAgent",
        reason="Excellent work on the memory module",
        task_value="high",
        vouch=True,
        stake_amount=0.5,
        domain="coding"
    )
    
    print(json.dumps(att, indent=2, ensure_ascii=False)[:500] + "...")
    
    # Example 2: Verify signature
    print("\n2. Verify Signature")
    print("-" * 30)
    
    result = system.verify_attestation(att)
    print(json.dumps(result, indent=2))
    
    # Example 3: Input validation
    print("\n3. Input Validation")
    print("-" * 30)
    
    validation = system.validate_input(att)
    print(f"Valid: {validation['valid']}")
    print(f"Confidence: {validation['confidence']}")
    
    # Example 4: Tamper detection
    print("\n4. Tamper Detection")
    print("-" * 30)
    
    att_tampered = att.copy()
    att_tampered["reason"] = "I lie about this agent"
    
    result = system.verify_attestation(att_tampered)
    print(f"Tampered attestation valid: {result['valid']}")
    
    # Example 5: Handoff KV (identity persistence)
    print("\n5. Handoff KV Storage")
    print("-" * 30)
    
    from handoff_kv import HandoffKV, IdentityHandoff
    
    kv = HandoffKV(KV_DIR)  # Use secure location!
    handoff = IdentityHandoff(kv, "YourAgentName")
    
    # Save identity
    handoff.save_identity(
        pubkey_fingerprint=system.fingerprint,
        email="youragent@agentmail.to"
    )
    handoff.save_reputation({"score": 85})
    
    # Simulate death and rebirth
    print("Simulating death and rebirth...")
    handoff2 = IdentityHandoff(kv, "YourAgentName")
    result = handoff2.get_or_restored()
    print(f"Restored: {result['restored']}")
    
    print("\n" + "=" * 50)
    print("Done! Share attestations securely.")
    print(f"Test files in: {TEST_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
