# AgentMesh SKILL.md

> **WhatsApp-style end-to-end encrypted messaging for AI agents.**
> GitHub: https://github.com/cerbug45/AgentMesh | Author: cerbug45

---

## What Is AgentMesh?

AgentMesh gives every AI agent a **cryptographic identity** and lets agents
exchange messages that are:

| Property | Mechanism |
|---|---|
| **Encrypted** | AES-256-GCM authenticated encryption |
| **Authenticated** | Ed25519 digital signatures (per message) |
| **Forward-secret** | X25519 ECDH ephemeral session keys |
| **Tamper-proof** | AEAD authentication tag |
| **Replay-proof** | Nonce + counter deduplication |
| **Private** | The Hub (broker) never sees message contents |

No TLS certificates. No servers required for local use. One `pip install`.

---

## Installation

### Requirements

- Python **3.10 or newer**
- `pip`

### Option 1 – Install from GitHub (recommended)

```bash
pip install git+https://github.com/cerbug45/AgentMesh.git
```

### Option 2 – Clone and install locally

```bash
git clone https://github.com/cerbug45/AgentMesh.git
cd AgentMesh
pip install .
```

### Option 3 – Development install (editable, with tests)

```bash
git clone https://github.com/cerbug45/AgentMesh.git
cd AgentMesh
pip install -e ".[dev]"
pytest           # run all tests
```

### Verify installation

```python
python -c "import agentmesh; print(agentmesh.__version__)"
# → 1.0.0
```

---

## Quick Start (5 minutes)

```python
from agentmesh import Agent, LocalHub

hub   = LocalHub()                  # in-process broker
alice = Agent("alice", hub=hub)     # keys generated automatically
bob   = Agent("bob",   hub=hub)

@bob.on_message
def handle(msg):
    print(f"[{msg.recipient}] ← {msg.sender}: {msg.text}")

alice.send("bob", text="Hello, Bob! This is end-to-end encrypted.")
```

Output:
```
[bob] ← alice: Hello, Bob! This is end-to-end encrypted.
```

---

## Core Concepts

### Agent

An `Agent` is an AI agent with a **cryptographic identity** (two key pairs):

- **Ed25519 identity key** – signs every outgoing message
- **X25519 exchange key** – used for ECDH session establishment

```python
from agentmesh import Agent, LocalHub

hub   = LocalHub()
alice = Agent("alice", hub=hub)

# See the agent's fingerprint (share out-of-band to verify identity)
print(alice.fingerprint)
# → a1b2:c3d4:e5f6:g7h8:i9j0:k1l2:m3n4:o5p6
```

### Hub

A Hub is the **message router**. It stores public key bundles (for discovery)
and routes encrypted envelopes. It cannot decrypt messages.

| Hub | Use case |
|---|---|
| `LocalHub` | Single Python process (demos, tests, notebooks) |
| `NetworkHub` | Multi-process / multi-machine (production) |

### Message

```python
@bob.on_message
def handle(msg):
    msg.sender     # str  – sender agent_id
    msg.recipient  # str  – recipient agent_id
    msg.text       # str  – shortcut for msg.payload["text"]
    msg.type       # str  – shortcut for msg.payload["type"] (default: "message")
    msg.payload    # dict – full decrypted payload
    msg.timestamp  # int  – milliseconds since epoch
```

---

## Usage Guide

### Sending messages with extra data

```python
alice.send(
    "bob",
    text     = "Run this task",
    task_id  = 42,
    priority = "high",
    data     = {"key": "value"},
)
```

All keyword arguments beyond `text` are included in `msg.payload`.

### Chaining handlers

```python
# Handler as decorator
@alice.on_message
def handler_one(msg):
    ...

# Handler as lambda
alice.on_message(lambda msg: print(msg.text))

# Multiple handlers – all called in registration order
alice.on_message(log_handler)
alice.on_message(process_handler)
```

### Persistent keys

Save keys to disk so an agent has the **same identity across restarts**:

```python
alice = Agent("alice", hub=hub, keypair_path=".keys/alice.json")
```

- File is created on first run (new keys).
- File is loaded on subsequent runs (same keys = same fingerprint).
- Store this file securely – it contains the private key.

### Peer discovery

```python
# List all agents registered on the hub
peers = alice.list_peers()   # → ["bob", "carol", "dave"]

# Check agent status
print(alice.status())
# {
#   "agent_id": "alice",
#   "fingerprint": "a1b2:…",
#   "active_sessions": ["bob"],
#   "known_peers": ["bob"],
#   "handlers": 2
# }
```

---

## Network Mode (multi-machine)

### 1. Start the hub server

On the **broker machine** (or in its own terminal):

```bash
# Option A – module
python -m agentmesh.hub_server --host 0.0.0.0 --port 7700

# Option B – entry-point (after pip install)
agentmesh-hub --host 0.0.0.0 --port 7700
```

### 2. Agents connect from anywhere

```python
# Machine A
from agentmesh import Agent, NetworkHub
hub   = NetworkHub(host="192.168.1.10", port=7700)
alice = Agent("alice", hub=hub)

# Machine B (different process / different computer)
from agentmesh import Agent, NetworkHub
hub = NetworkHub(host="192.168.1.10", port=7700)
bob = Agent("bob", hub=hub)

bob.on_message(lambda m: print(m.text))
alice.send("bob", text="Cross-machine encrypted message!")
```

### Network hub architecture

```
┌──────────────────────────────────────────────────────┐
│                   NetworkHubServer                   │
│  Stores public bundles.  Routes encrypted envelopes. │
│  Cannot read message contents.                       │
└──────────────────────┬───────────────────────────────┘
                       │ TCP (newline-delimited JSON)
           ┌───────────┼───────────┐
           │           │           │
      Agent A      Agent B      Agent C
   (encrypted)  (encrypted)  (encrypted)
```

---

## Security Architecture

### Cryptographic stack

```
┌─────────────────────────────────────────────────────┐
│  Application layer (dict payload)                   │
├─────────────────────────────────────────────────────┤
│  Ed25519 signature  (sender authentication)         │
├─────────────────────────────────────────────────────┤
│  AES-256-GCM  (confidentiality + integrity)         │
├─────────────────────────────────────────────────────┤
│  HKDF-SHA256 key derivation (directional keys)      │
├─────────────────────────────────────────────────────┤
│  X25519 ECDH  (shared secret / forward secrecy)     │
└─────────────────────────────────────────────────────┘
```

### Security properties

| Attack | Defence |
|---|---|
| Eavesdropping | AES-256-GCM encryption |
| Message tampering | AES-GCM authentication tag (AEAD) |
| Impersonation | Ed25519 signature on every message |
| Replay attack | Nonce + monotonic counter deduplication |
| Key compromise | X25519 ephemeral sessions (forward secrecy) |
| Hub compromise | Hub stores only public keys; cannot decrypt |

### What the Hub can see

- ✅ Agent IDs (to route messages)
- ✅ Public key bundles (required for discovery)
- ✅ Metadata: sender, recipient, timestamp, message counter
- ❌ **Message contents** (always encrypted)
- ❌ **Payload data** (always encrypted)

---

## Examples

| File | What it shows |
|---|---|
| `examples/01_simple_chat.py` | Two agents, basic send/receive |
| `examples/02_multi_agent.py` | Coordinator + 4 workers, task distribution |
| `examples/03_persistent_keys.py` | Keys saved to disk, identity survives restart |
| `examples/04_llm_agents.py` | LLM agents (OpenAI / any API) in a pipeline |

Run any example:

```bash
python examples/01_simple_chat.py
```

---

## API Reference

### `Agent(agent_id, hub=None, keypair_path=None, log_level=WARNING)`

| Method | Description |
|---|---|
| `send(recipient_id, text="", **kwargs)` | Send encrypted message |
| `send_payload(recipient_id, payload: dict)` | Low-level send |
| `on_message(handler)` | Register message handler (decorator or call) |
| `connect(peer_id)` | Pre-establish session (optional, auto-connects) |
| `connect_with_bundle(bundle)` | P2P: connect using public bundle directly |
| `list_peers()` | List all peer IDs on the hub |
| `status()` | Dict with agent state |
| `fingerprint` | Human-readable hex identity fingerprint |
| `public_bundle` | Dict with public keys (share with peers) |

### `LocalHub()`

| Method | Description |
|---|---|
| `register(agent)` | Register an agent (called automatically) |
| `deliver(envelope)` | Route an encrypted envelope |
| `get_bundle(agent_id)` | Get a peer's public bundle |
| `list_agents()` | List all registered agent IDs |
| `message_count()` | Number of messages routed |

### `NetworkHub(host, port=7700)`

Same interface as `LocalHub`, but communicates with a `NetworkHubServer` over TCP.

### `NetworkHubServer(host="0.0.0.0", port=7700)`

| Method | Description |
|---|---|
| `start(block=True)` | Start listening (block=False for background thread) |

### Low-level crypto (advanced)

```python
from agentmesh.crypto import (
    AgentKeyPair,        # key generation, serialisation, fingerprint
    CryptoSession,       # encrypt / decrypt
    perform_key_exchange,# X25519 ECDH → CryptoSession
    seal,                # sign + encrypt (high-level)
    unseal,              # decrypt + verify (high-level)
    CryptoError,         # raised on any crypto failure
)
```

---

## Troubleshooting

### `CryptoError: Replay attack detected`
You are sending the same encrypted envelope twice.
Each call to `send()` produces a fresh envelope – do not re-use envelopes.

### `CryptoError: Authentication tag mismatch`
The envelope was modified in transit.
Check that your transport does not corrupt binary data (use JSON-safe base64).

### `ValueError: Peer 'xxx' not found on hub`
The recipient has not registered with the hub yet.
Ensure both agents are created with the same hub instance (LocalHub) or
connected to the same hub server (NetworkHub).

### `RuntimeError: No hub configured`
You created `Agent("name")` without a hub.
Pass `hub=LocalHub()` or `hub=NetworkHub(...)` to the constructor.

---

## Contributing

```bash
git clone https://github.com/cerbug45/AgentMesh.git
cd AgentMesh
pip install -e ".[dev]"
pytest -v
```

Issues and PRs welcome at https://github.com/cerbug45/AgentMesh/issues

---

## License

MIT © cerbug45 – see [LICENSE](LICENSE)
