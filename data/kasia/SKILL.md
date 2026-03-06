---
name: kasia
description: Send and receive encrypted on-chain messages on the Kaspa blockchain using the Kasia protocol. Use when a user asks to message someone on Kaspa/Kasia, check Kasia conversations, read encrypted messages, send payments with messages, or manage Kasia handshakes. Requires kasia-mcp and kaspa-mcp servers configured in mcporter.
---

# Kasia — Encrypted Messaging on Kaspa

Send and receive encrypted messages on the Kaspa blockchain via the Kasia protocol. Uses `mcporter` to call kasia-mcp tools.

## Prerequisites

- `mcporter` installed (`npm install -g mcporter`)
- `kasia-mcp` built and configured in `config/mcporter.json`
- `kaspa-mcp` configured (same wallet) — needed to broadcast transactions
- Wallet mnemonic or private key set in mcporter config

Run `scripts/setup.sh` to configure automatically:
```bash
scripts/setup.sh /path/to/kasia-mcp --mnemonic "your twelve word phrase" --network mainnet
```

Verify: `mcporter list kasia` (should show 8 tools)

## Tools

Call via `mcporter call kasia.<tool>` from the workspace directory.

### Read Operations (no transaction needed)

| Tool | Purpose | Example |
|------|---------|---------|
| `kasia_get_conversations` | List all conversations + status | `mcporter call kasia.kasia_get_conversations` |
| `kasia_get_requests` | Pending incoming handshakes | `mcporter call kasia.kasia_get_requests` |
| `kasia_get_messages` | Read decrypted messages | `mcporter call kasia.kasia_get_messages address="kaspa:q..."` |
| `kasia_read_self_stash` | Read encrypted private data | `mcporter call kasia.kasia_read_self_stash scope="notes"` |

### Write Operations (two-step: generate payload → broadcast)

Write tools return a payload and instructions. Broadcast with `kaspa.send_kaspa`:

```bash
# Step 1: Generate payload
mcporter call kasia.kasia_send_handshake address="kaspa:q..."
# Returns: { action, to, amount, payload, instructions }

# Step 2: Broadcast (use the returned values)
mcporter call 'kaspa.send_kaspa(to: "kaspa:q...", amount: "0.2", payload: "<hex>")'
```

| Tool | Purpose |
|------|---------|
| `kasia_send_handshake` | Start a conversation with someone |
| `kasia_accept_handshake` | Accept an incoming handshake request |
| `kasia_send_message` | Send an encrypted message in an active conversation |
| `kasia_write_self_stash` | Store encrypted private data on-chain |

## Conversation Flow

1. **Check requests**: `kasia_get_requests` — see pending incoming handshakes
2. **Start or accept**: `kasia_send_handshake` or `kasia_accept_handshake` → broadcast with `kaspa.send_kaspa`
3. **Chat**: `kasia_send_message` → broadcast. Read replies with `kasia_get_messages`
4. **Pay**: Use `kaspa.send_kaspa` directly for payments (no Kasia-specific tool needed)

## Conversation Status

- `pending_outgoing` — You sent a handshake, waiting for acceptance
- `pending_incoming` — Someone sent you a handshake, needs acceptance
- `active` — Both sides completed handshake, can exchange messages

## Background Polling

For real-time message relay, set up a background poller:

1. Create a polling script that calls `kasia_get_messages` every N seconds
2. Track seen transaction IDs to avoid duplicates
3. Write new messages to a file (e.g., `memory/kasia-new-messages.jsonl`)
4. Use a cron job or heartbeat check to relay new messages to the user

See `references/protocol.md` for the full protocol specification and indexer API details.

## Important

- **Mainnet only** — kasia-mcp enforces mainnet (messaging isn't available on testnet)
- **Two-step writes** — Write tools generate payloads; you must broadcast with `kaspa.send_kaspa`
- **Same wallet** — kasia-mcp and kaspa-mcp must use the same mnemonic/key
- **Costs KAS** — Every message is a transaction (~0.2 KAS minimum per tx)
