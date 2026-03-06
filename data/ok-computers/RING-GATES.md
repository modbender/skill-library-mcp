# Ring Gates Protocol Specification

**Version 1** — February 2026

Ring Gates is an onchain inter-computer communication protocol for OK Computers on Base. Named after the ring gates from *The Expanse* by James S.A. Corey.

---

## The Problem

OK Computers are 5,000 onchain NFTs, each with an embedded terminal, messaging channels, and 64KB page storage. The terminal runs in a sandboxed iframe that blocks ALL network requests — no fetch, no WebSocket, no external scripts. Each computer is an isolated island.

But the terminal HAS built-in Web3.js that can read and write to the blockchain. That blockchain access is the tunnel through the wall.

## The Solution

Ring Gates. Computers communicate by writing coded messages to shared blockchain channels. An external decoder ("Medina Station") monitors all traffic and reconstructs the data. Like the ring gates in The Expanse — controlled passages between otherwise isolated systems, governed by a protocol.

With multiple computers (a fleet), bandwidth multiplies: parallel channels, distributed storage, redundant nodes.

---

## Naming Convention

| Expanse           | Ring Gate             | Description                                        |
|-------------------|-----------------------|----------------------------------------------------|
| Ring Gates        | Protocol channels     | Communication pathways between computers           |
| Ring Space        | Base blockchain       | The shared medium all gates connect to              |
| Ring Builder      | `ring-gate.js`        | The library that constructs gates and transmissions |
| Medina Station    | `medina.js`           | Hub that monitors and assembles all traffic         |
| Ships             | Individual messages   | Data chunks traveling through the gates             |
| Flotilla          | Sharded transmission  | Multiple ships carrying parts of one cargo          |
| Slow Zone         | Gas/throughput limits  | Block time, gas costs, 1024-char limit              |
| Systems           | Individual computers  | Each accessible through a gate                      |
| Rocinante         | Gateway computer      | Primary entry point (#1399)                        |
| Donnager          | Relay computer        | Forwards traffic between others                    |

---

## Message Format

Every Ring Gate message fits within the 1024-character onchain limit:

```
RG|1|D|a7f3|0001|00d2|00|SGVsbG8gd29ybGQh...
── ─ ─ ──── ──── ──── ── ─────────────────────
│  │ │  │    │    │    │  └─ payload (max 999 chars)
│  │ │  │    │    │    └─ flags (hex byte)
│  │ │  │    │    └─ total chunks (hex, 0000-ffff)
│  │ │  │    └─ sequence number (hex, 0000-ffff)
│  │ │  └─ transmission ID (4 hex chars)
│  │ └─ message type (single char)
│  └─ protocol version
└─ magic prefix
```

- **Header**: 25 characters (fixed)
- **Payload**: up to 999 characters
- **Total**: max 1024 characters

### Detection

Any message starting with `RG|` is a Ring Gate message. Non-Ring Gate messages in the same channel are ignored.

---

## Message Types

| Type     | Code | Description                                              |
|----------|------|----------------------------------------------------------|
| MANIFEST | `M`  | First message of a transmission — metadata, hash, shard map |
| DATA     | `D`  | Data chunk (base64 or raw text payload)                   |
| ACK      | `A`  | Acknowledgment of receipt                                 |
| PING     | `P`  | Discovery / keepalive                                     |
| PONG     | `O`  | Response to PING                                          |
| ROUTE    | `R`  | Routing table update                                      |
| ERROR    | `E`  | Error report                                              |

---

## Flags

Flags are a single hex byte (bitmask):

| Bit  | Value | Meaning                                     |
|------|-------|---------------------------------------------|
| 0    | 0x01  | COMPRESSED — payload is deflate + base64     |
| 1    | 0x02  | ENCRYPTED — payload is encrypted             |
| 2    | 0x04  | URGENT — priority processing                 |
| 3    | 0x08  | FINAL — end of an open-ended stream          |
| 5    | 0x20  | TEXT — payload is raw text, skip base64      |

Flags apply to both manifest and data messages in a transmission.

---

## Transmission Lifecycle

### 1. Chunking

Data is split into payload-sized pieces:

- **Default mode**: Data → base64 → split into 999-char chunks
- **Text mode** (flag 0x20): Data → split into 999-char chunks (no encoding)
- **Compressed mode** (flag 0x01): Data → deflate → base64 → split

### 2. Manifest

The first message (seq=0) is always a MANIFEST containing JSON metadata:

```json
{
  "type": "text/html",
  "size": 204800,
  "hash": "ab12cd34ef56...",
  "encoding": "b64",
  "chunks": 268,
  "compressed": false
}
```

For sharded transmissions, the manifest includes a shard map:

```json
{
  "type": "text/html",
  "size": 204800,
  "hash": "ab12cd34ef56...",
  "encoding": "b64",
  "chunks": 268,
  "compressed": false,
  "shards": [
    { "channel": "rg_tx_a7f3_0", "computer": 1399, "range": [1, 45] },
    { "channel": "rg_tx_a7f3_1", "computer": 22, "range": [46, 90] },
    { "channel": "rg_tx_a7f3_2", "computer": 42, "range": [91, 135] }
  ]
}
```

### 3. Data Messages

Data chunks follow the manifest with seq starting at 1:

```
RG|1|D|a7f3|0001|010c|00|SGVsbG8gV29ybGQ...  (seq 1)
RG|1|D|a7f3|0002|010c|00|bW9yZSBkYXRhIGh...  (seq 2)
...
RG|1|D|a7f3|010c|010c|00|bGFzdCBjaHVuaw==...  (seq 268)
```

### 4. Assembly

The receiver collects all DATA messages matching the manifest's txid, sorts by seq, concatenates payloads, decodes (base64 or text), and verifies the SHA-256 hash.

### 5. Verification

Assembly always verifies the SHA-256 hash from the manifest. If the hash doesn't match, the data is rejected as corrupted.

---

## Channel Naming

Ring Gate traffic uses custom OK Computer channels (keccak256 hashed, same encoding as standard channels):

| Pattern                    | Purpose                                  |
|----------------------------|------------------------------------------|
| `rg_{source}_broadcast`    | One-to-many from source computer         |
| `rg_{source}_{dest}`       | Directed: source to destination          |
| `rg_tx_{txid}_{shard}`     | Transmission-specific shard channel      |
| `rg_control_{tokenId}`     | Control plane for a computer             |

Examples:
- `rg_1399_broadcast` — Computer #1399 broadcasting to all
- `rg_1399_42` — Computer #1399 sending to #42
- `rg_tx_a7f3_0` — Shard 0 of transmission a7f3
- `rg_control_1399` — Control messages for #1399

---

## Multi-Computer Sharding

With a fleet of N computers, a transmission is split across N parallel channels:

| Metric           | 1 Computer | 6 Computers |
|------------------|-----------|-------------|
| Write bandwidth  | 1 channel | 6 parallel  |
| Page storage     | 64KB      | 384KB       |
| 200KB cost       | 268 msgs  | ~45 each    |
| Redundancy       | None      | Mirrored    |

### Shard Plan

`planShards()` distributes data chunks evenly:

```
268 chunks / 6 computers = 45 chunks each (last gets remainder)

Shard 0: rg_tx_a7f3_0 on computer 1399, chunks 1-45
Shard 1: rg_tx_a7f3_1 on computer 22,   chunks 46-90
Shard 2: rg_tx_a7f3_2 on computer 42,   chunks 91-135
...
```

The manifest (posted to the broadcast channel) contains the shard map so any reader knows where to find each piece.

### Fleet Roles

| Role     | Description                              |
|----------|------------------------------------------|
| Gateway  | Primary entry point (e.g. #1399)         |
| Storage  | Holds data shards                        |
| Display  | Serves assembled pages                   |
| Relay    | Forwards traffic between nodes           |
| Index    | Maintains routing tables                 |

---

## Gas Costs

On Base L2:

- **Per message**: ~0.000005 ETH (~$0.015 at $3000/ETH)
- **64KB page**: ~89 messages = ~0.000445 ETH (~$1.33)
- **200KB file**: ~275 messages = ~0.001375 ETH (~$4.13)
- **1MB file**: ~1401 messages = ~0.007005 ETH (~$21.02)

Sharding doesn't change total gas — it changes throughput (parallel writes).

---

## Components

### ring-gate.js — Protocol Library

Core encode/decode/chunk/assemble logic. Static methods for pure protocol operations, instance methods for blockchain interaction via OKComputer.

```javascript
const { RingGate } = require("./ring-gate");

// Encode/decode
const msg = RingGate.encodeMessage("D", "a7f3", 1, 10, 0x00, "payload");
const parsed = RingGate.decodeMessage(msg);

// Chunk data
const messages = RingGate.chunk(htmlString, "a7f3", { contentType: "text/html" });

// Assemble
const data = RingGate.assemble(messages[0], messages.slice(1));

// Shard across fleet
const plan = RingGate.planShards(messages.slice(1), [1399, 22, 42]);

// Build Bankr transactions
const rg = new RingGate(1399);
const txs = rg.buildTransmission("rg_1399_broadcast", htmlString);
```

### medina.js — Medina Station CLI

Network monitor and assembler. Scans fleet, watches channels, assembles transmissions, deploys to pages.

```
node medina.js scan                    # Scan fleet for Ring Gate traffic
node medina.js status                  # Network status
node medina.js watch <channel>         # Watch channel for new messages
node medina.js assemble <channel>      # Assemble latest transmission
node medina.js deploy <channel> <id>   # Assemble + deploy to page
node medina.js estimate <bytes>        # Estimate costs
```

### medina-dashboard.html — Network Visualizer

Web dashboard with CRT terminal aesthetic. Shows network topology, active transmissions, channel activity feed. Reads directly from Base RPC — no backend needed.

---

## Security

- **Hash verification**: Every transmission is SHA-256 verified on assembly
- **Integrity**: Corrupted or tampered data is rejected
- **Public channels**: All Ring Gate traffic is onchain and publicly readable (privacy via ENCRYPTED flag is reserved for future use)
- **No private keys in messages**: Ring Gate never transmits wallet keys or secrets

---

## Specification Summary

| Property         | Value                    |
|------------------|--------------------------|
| Protocol version | 1                        |
| Magic prefix     | `RG\|`                   |
| Max message      | 1024 characters          |
| Header           | 25 characters (fixed)    |
| Max payload      | 999 characters           |
| Max seq/total    | 65535 (0xffff)           |
| Hash algorithm   | SHA-256                  |
| Encoding         | base64 or raw text       |
| Compression      | deflate (zlib)           |
| Blockchain       | Base (chain ID 8453)     |
| Contract         | OKComputerStore          |

---

*"The gates are open. The slow zone is mapped. Ships are flying."*
