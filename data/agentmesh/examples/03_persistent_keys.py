"""
Example 3 – Persistent Key Pairs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agents save their key-pairs to disk so they keep the same
cryptographic identity across restarts.

Run twice – the second run will load the saved keys:
  python examples/03_persistent_keys.py
  python examples/03_persistent_keys.py
"""

import os
from pathlib import Path
from agentmesh import Agent, LocalHub

KEYS_DIR = Path(".agentmesh_keys")
KEYS_DIR.mkdir(exist_ok=True)

hub = LocalHub()

# Keys are saved/loaded from .agentmesh_keys/<agent_id>.json
alice = Agent("alice", hub=hub, keypair_path=KEYS_DIR / "alice.json")
bob   = Agent("bob",   hub=hub, keypair_path=KEYS_DIR / "bob.json")

print("Alice fingerprint:", alice.fingerprint)
print("Bob   fingerprint:", bob.fingerprint)
print()
print("(Run this script again – fingerprints will be identical!)")
print()

# Quick round-trip test
got = []
bob.on_message(lambda m: got.append(m.text))
alice.send("bob", text="Persistent identity test!")

assert got[0] == "Persistent identity test!"
print(f"✓ Message delivered: {got[0]!r}")
print()
print("Key files saved in:", KEYS_DIR.resolve())
for f in KEYS_DIR.iterdir():
    print(f"  {f.name}  ({f.stat().st_size} bytes)")
