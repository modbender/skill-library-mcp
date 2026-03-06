"""
Example 1 – Simple Local Chat
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Two AI agents (Alice & Bob) exchange encrypted messages inside
a single Python process.  No server needed.

Run:
  python examples/01_simple_chat.py
"""

from agentmesh import Agent, LocalHub

# ── 1. Create a hub ──────────────────────────────────────────────────────────
hub = LocalHub()

# ── 2. Create agents (keys are generated automatically) ──────────────────────
alice = Agent("alice", hub=hub)
bob   = Agent("bob",   hub=hub)

print(f"Alice fingerprint : {alice.fingerprint}")
print(f"Bob   fingerprint : {bob.fingerprint}")
print()

# ── 3. Register message handlers ─────────────────────────────────────────────

received: list = []

@bob.on_message
def bob_handler(msg):
    print(f"  [Bob  ← {msg.sender}] {msg.text}")
    received.append(msg)

@alice.on_message
def alice_handler(msg):
    print(f"  [Alice← {msg.sender}] {msg.text}")
    received.append(msg)

# ── 4. Send messages ──────────────────────────────────────────────────────────
print("Sending messages…")
alice.send("bob",   text="Hello Bob!  This is an encrypted message.")
bob.send("alice",  text="Hi Alice!   Got your message loud and clear.")
alice.send("bob",   text="Great!  Nobody else can read this 😎")
bob.send("alice",  text="End-to-end encryption FTW!")

print()
print(f"✓ {len(received)} messages delivered and decrypted successfully.")
print()

# ── 5. Show hub stats ─────────────────────────────────────────────────────────
print("Hub stats:", hub)
print("Alice status:", alice.status())
