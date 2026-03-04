---
name: bitkit-cli
description: Bitcoin Lightning payment CLI for agents. Lowest LSP fees. Self-custody wallet with LNURL, typed exit codes, JSON envelope output, encrypted messaging, and daemon mode.
version: 0.2.0
metadata:
  clawdbot:
    requires:
      bins: [bitkit]
    homepage: https://github.com/synonymdev/bitkit-cli
    emoji: "\u26A1"
---

# bitkit-cli -- AI Agent Skill

Bitcoin Lightning payment CLI for agents. Lowest LSP fees. Self-custody wallet with LNURL/Lightning Address support, typed exit codes, JSON envelope output, encrypted Pubky messaging, and daemon mode.

**Install:** `curl -sSL https://raw.githubusercontent.com/synonymdev/bitkit-cli/main/install.sh | sh`
**Binary names:** `bitkit` or `bk` (identical alias)
**Always use:** `--json` flag on every invocation for parseable output.

## JSON Envelope

All `--json` output uses a consistent envelope:

**Success** (stdout):
```json
{ "ok": true, "data": { ... } }
```

**Error** (stderr):
```json
{ "ok": false, "error": "message", "code": 1 }
```

Parse with: `jq -r '.data.field'` for success data, check `.ok` first.

## Quick Start

```bash
# 1. Create wallet (no encryption for agent use)
bk init --no-password --json

# 2. Start daemon for instant command execution
bk start --json

# 3. Get on-chain address and fund it
ADDRESS=$(bk address --json | jq -r '.data.address')

# 4. Order inbound Lightning liquidity via LSP
ORDER=$(bk lsp create-order 500000 --json)
ORDER_ID=$(echo "$ORDER" | jq -r '.data.order_id')

# 5. Pay the order (on-chain to payment_address), then open channel
bk lsp open-channel "$ORDER_ID" --listen 9735 --json

# 6. Create an invoice and receive payment
bk invoice 5000 --description "agent service" --wait --listen 9735 --json

# 7. Pay someone else's invoice
bk pay lnbc50u1p... --json

# 8. Check balance and history
bk balance --json
bk history --json

# 9. Stop daemon when done
bk stop --json
```

## Daemon Mode

By default each command cold-starts the LDK node (slow). Start a persistent daemon for instant execution:

```bash
bk start --json           # start daemon (default port 3457)
bk status --json          # check if running
bk balance --json         # instant -- proxied through daemon
bk stop --json            # stop daemon
```

When the daemon is running, all commands automatically proxy through its HTTP API. When stopped, commands fall back to per-command cold-start. No code changes needed.

### `start`

Start the background daemon. Idempotent -- returns current PID if already running.

```bash
bk start --json
bk start --port 8080 --json
```

```json
{
  "ok": true,
  "data": {
    "status": "started",
    "pid": 12345,
    "port": 3457
  }
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `--port <port>` | `3457` | HTTP API port |

`status` is `"started"` or `"already_running"`.

### `stop`

Stop the running daemon.

```bash
bk stop --json
```

```json
{
  "ok": true,
  "data": {
    "status": "stopped",
    "pid": 12345
  }
}
```

Errors if no daemon is running (exit code 1).

### `status`

Check daemon status.

```bash
bk status --json
```

```json
{
  "ok": true,
  "data": {
    "running": true,
    "pid": 12345,
    "port": 3457,
    "started_at": "2026-02-19T10:00:00+00:00",
    "version": "0.1.0"
  }
}
```

When stopped: `running` is `false`, all other fields are `null`.

## Global Flags

| Flag | Env Variable | Default | Description |
|------|-------------|---------|-------------|
| `--json` | -- | off | Machine-readable JSON to stdout |
| `--dir <path>` | `BITKIT_DIR` | `~/.bitkit/` | Wallet data directory |
| `--network <net>` | `BITKIT_NETWORK` | `mainnet` | `mainnet` or `regtest` |
| `--listen <port>` | `BITKIT_LISTEN` | off | P2P listen port on `0.0.0.0:<port>` |
| `--password <pw>` | `BITKIT_PASSWORD` | -- | Wallet password (for encrypted seeds) |

## Command Reference

### Wallet

#### `init`

Create a new wallet. Idempotent -- re-running prints existing wallet info.

```bash
bk init --no-password --json
```

```json
{
  "ok": true,
  "data": {
    "node_id": "02abc123...",
    "seed_phrase": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
    "wallet_dir": "/root/.bitkit",
    "network": "mainnet",
    "pubky_id": "8pinxrz9tuxfz3qo5gkhdebuhtq6mrimh3matdncsrsno7kg45mo"
  }
}
```

| Arg | Required | Description |
|-----|----------|-------------|
| `--no-password` | one of | Store seed as plaintext (for agents) |
| `--password <pw>` | one of | Encrypt seed with AES-256-GCM + Argon2id |

#### `info`

Show node status, channel counts, sync state.

```bash
bk info --json
```

```json
{
  "ok": true,
  "data": {
    "node_id": "02abc123...",
    "network": "mainnet",
    "channels_active": 1,
    "channels_pending": 0,
    "block_height": 880000,
    "synced": true,
    "wallet_dir": "/root/.bitkit"
  }
}
```

#### `balance`

Show Lightning and on-chain balances in satoshis.

```bash
bk balance --json
```

```json
{
  "ok": true,
  "data": {
    "lightning_sats": 450000,
    "onchain_sats": 50000,
    "total_sats": 500000,
    "total_onchain_sats": 55000,
    "anchor_reserve_sats": 5000,
    "pending_sweep_sats": 0,
    "pending_sweeps": []
  }
}
```

- `onchain_sats` -- spendable on-chain balance
- `total_onchain_sats` -- all on-chain funds including reserved
- `anchor_reserve_sats` -- sats reserved for anchor channel fees
- `pending_sweep_sats` -- funds sweeping from closed channels (not yet spendable)
- `pending_sweeps` -- array of sweep entries with `amount_sats`, `status`, `spending_txid`, `confirmation_height`

| Arg | Description |
|-----|-------------|
| `--btc` | Display in BTC instead of sats (human output only) |

#### `config`

Show resolved configuration with source tracking. Does not start the node.

```bash
bk config --json
```

```json
{
  "ok": true,
  "data": {
    "network": { "value": "mainnet", "source": "default" },
    "wallet_dir": { "value": "/root/.bitkit", "source": "default" },
    "chain_source": { "value": "esplora", "source": "file" },
    "esplora_url": { "value": "https://blockstream.info/api", "source": "file" },
    "electrum_url": { "value": "", "source": "file" },
    "rgs_url": { "value": "https://rapidsync.lightningdevkit.org/snapshot", "source": "file" },
    "blocktank_url": { "value": "https://api1.blocktank.to/api", "source": "file" },
    "listen_port": { "value": "off", "source": "default" }
  }
}
```

Each entry has `value` (resolved value) and `source` (`cli`, `env`, `file`, or `default`).

#### `address`

Get a new on-chain receive address. Generates a fresh address each call. Optionally validate an existing address.

```bash
bk address --json
bk address --type taproot --json
bk address --validate bc1q... --json
```

Generate address:
```json
{
  "ok": true,
  "data": { "address": "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "address_type": "native-segwit" }
}
```

Validate address (`--validate`):
```json
{
  "ok": true,
  "data": { "address": "bc1q...", "valid": true, "network": "mainnet", "reason": null }
}
```

On invalid address: `valid` is `false` and `reason` explains why.

| Arg | Default | Description |
|-----|---------|-------------|
| `--type <type>` | `native-segwit` | Address type: `legacy`, `nested-segwit`, `native-segwit`, `taproot` |
| `--validate <addr>` | -- | Validate `<addr>` for the current network; no node start needed |
| `--qr` | off | Display address as QR code in terminal (human output only) |

#### `send`

Send bitcoin on-chain to an address.

```bash
bk send bc1q... 50000 --json
bk send bc1q... 50000 --fee-rate 5 --json
bk send bc1q... --drain --json
bk send bc1q... 50000 --utxo <txid>:<vout> --json
```

```json
{
  "ok": true,
  "data": {
    "txid": "abc123...",
    "address": "bc1q...",
    "amount_sats": 50000,
    "drain": false,
    "fee_rate_sat_per_vb": 5,
    "utxos_used": ["abc123...:0"]
  }
}
```

When `--drain` is used, `amount_sats` is `null`. When no `--fee-rate` is set, `fee_rate_sat_per_vb` is `null`.

| Arg | Default | Description |
|-----|---------|-------------|
| `<address>` | required | Destination Bitcoin address |
| `<amount_sats>` | -- | Amount in satoshis (omit with `--drain`) |
| `--drain` | off | Send all spendable funds (mutually exclusive with `--utxo`) |
| `--fee-rate <sat/vb>` | auto | Fee rate in sat/vb |
| `--utxo <txid:vout>` | -- | Spend a specific UTXO (repeatable; incompatible with `--drain`) |

#### `list-utxos`

List all spendable UTXOs in the on-chain wallet.

```bash
bk list-utxos --json
```

```json
{
  "ok": true,
  "data": {
    "utxos": [
      {
        "txid": "abc123...",
        "vout": 0,
        "value_sats": 1000000,
        "outpoint": "abc123...:0"
      }
    ],
    "total_sats": 1000000,
    "count": 1
  }
}
```

Use `outpoint` values (e.g. `abc123...:0`) as `--utxo` arguments for `send` and `estimate-fee`.

#### `estimate-fee`

Preview the fee for an on-chain send without broadcasting.

```bash
bk estimate-fee bc1q... 50000 --json
bk estimate-fee bc1q... 50000 --fee-rate 5 --json
```

```json
{
  "ok": true,
  "data": {
    "fee_sats": 250,
    "address": "bc1q...",
    "amount_sats": 50000,
    "fee_rate_sat_per_vb": 5
  }
}
```

`fee_rate_sat_per_vb` is `null` when not specified (node chooses automatically).

| Arg | Default | Description |
|-----|---------|-------------|
| `<address>` | required | Destination Bitcoin address |
| `<amount_sats>` | required | Amount to send in satoshis |
| `--fee-rate <sat/vb>` | auto | Override fee rate in sat/vb |
| `--utxo <txid:vout>` | -- | Restrict coin selection to specific UTXOs |

#### `bump-fee`

Replace an unconfirmed transaction with a higher-fee version (RBF). The original transaction must be in the mempool and RBF-enabled.

```bash
bk bump-fee <txid> <fee_rate> --json
```

```json
{
  "ok": true,
  "data": {
    "original_txid": "abc123...",
    "new_txid": "def456...",
    "fee_rate_sat_per_vb": 20
  }
}
```

| Arg | Description |
|-----|-------------|
| `<txid>` | TXID of the unconfirmed transaction to replace |
| `<fee_rate>` | New fee rate in sat/vb (must be higher than the original) |

On failure (invalid txid, not in mempool, RBF not signalled): exits with code 1.

#### `cpfp`

Accelerate a stuck transaction by spending one of its outputs at a higher fee rate (Child-Pays-For-Parent).

```bash
bk cpfp <txid> --json
bk cpfp <txid> --fee-rate 30 --json
bk cpfp <txid> --urgent --json
```

```json
{
  "ok": true,
  "data": {
    "parent_txid": "abc123...",
    "child_txid": "def456...",
    "fee_rate_sat_per_vb": 30,
    "urgent": false
  }
}
```

`fee_rate_sat_per_vb` is `null` when neither `--fee-rate` nor `--urgent` is set.

| Arg | Default | Description |
|-----|---------|-------------|
| `<txid>` | required | TXID of the parent transaction to accelerate |
| `--fee-rate <sat/vb>` | auto | Explicit fee rate for the child transaction |
| `--urgent` | off | Automatically compute a high fee rate to confirm next block |

On failure (invalid txid, no spendable output found): exits with code 1.

#### `history`

List recent transactions, newest first.

```bash
bk history --limit 5 --type send --json
```

```json
{
  "ok": true,
  "data": [
    {
      "type": "send",
      "amount_sat": 5000,
      "fee_sat": 3,
      "status": "complete",
      "timestamp": "2026-02-15 12:00:00",
      "description": "coffee"
    }
  ]
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `--limit <n>` | `20` | Number of entries |
| `--type <send\|recv>` | all | Filter by direction |

**Status values:** `complete`, `pending`, `failed`
**Type values:** `send`, `recv`

### Lightning Payments

#### `invoice`

Generate a BOLT 11 invoice to receive payment.

```bash
bk invoice 5000 --description "agent service" --json
```

```json
{
  "ok": true,
  "data": {
    "bolt11": "lnbc50u1p...",
    "payment_hash": "a1b2c3d4e5f6...",
    "amount_sat": 5000,
    "description": "agent service",
    "expires_at": "2026-02-15T14:30:00+00:00"
  }
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `<amount_sats>` | required | Amount in satoshis |
| `--description <text>` | `""` | Invoice memo |
| `--expiry <secs>` | `3600` | Invoice expiry in seconds |
| `--wait` | off | Block until payment received |
| `--timeout <secs>` | `300` | Timeout when using `--wait` |
| `--qr` | off | Display invoice as QR code in terminal (human output only) |

**Two-phase output with `--wait`:** First prints the invoice envelope above, then blocks. When payment arrives, prints a second envelope to stdout:

```json
{
  "ok": true,
  "data": {
    "status": "received",
    "amount_sat": 5000,
    "payment_hash": "a1b2c3d4e5f6..."
  }
}
```

If timeout expires, exits with code 2 (network error). Always use `--listen <port>` with `--wait` so the payer can connect.

#### `pay`

Pay a BOLT 11 invoice, LNURL, or Lightning Address. Polls until success, failure, or timeout.

```bash
bk pay lnbc50u1p... --json
bk pay lnurl1dp68gurn... --json
```

```json
{
  "ok": true,
  "data": {
    "status": "success",
    "amount_sat": 5000,
    "fee_sat": 3,
    "payment_hash": "a1b2c3d4e5f6...",
    "preimage": "1a2b3c4d5e6f..."
  }
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `<bolt11>` | required | BOLT 11 invoice, LNURL, or Lightning Address |
| `--max-fee <sats>` | unlimited | Maximum routing fee in satoshis |
| `--timeout <secs>` | `60` | Payment timeout |

**LNURL/Lightning Address support:** `pay` accepts LNURL (`lnurl1...`) and resolves to a BOLT11 invoice. For LNURL-pay with variable amounts (where `min_sendable != max_sendable`), the CLI currently requires a fixed-amount LNURL. Lightning Address (`user@domain.tld`) requires a `--amount` flag which is not yet implemented — use a BOLT11 invoice instead.

On failure: exits with code 1 ("Payment failed"). On timeout: exits with code 2.

#### `withdraw`

Withdraw from an LNURL-withdraw endpoint. Creates an invoice and submits it to the LNURL service.

```bash
bk withdraw lnurl1dp68gurn... --json
bk withdraw lnurl1dp68gurn... --amount 10000 --json
```

```json
{
  "ok": true,
  "data": {
    "status": "submitted",
    "amount_sat": 10000,
    "bolt11": "lnbc100u1p..."
  }
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `<lnurl>` | required | LNURL-withdraw bech32 string |
| `--amount <sats>` | max withdrawable | Amount in satoshis |

### Channels

#### `open-channel`

Open a Lightning channel to a peer. Requires on-chain funds.

```bash
bk open-channel 02ab...@127.0.0.1:9735 100000 --json
```

```json
{
  "ok": true,
  "data": {
    "channel_id": "12345678901234567890",
    "peer": "02ab...",
    "amount_sats": 100000
  }
}
```

| Arg | Description |
|-----|-------------|
| `<peer>` | Peer in `pubkey@host:port` format |
| `<amount_sats>` | Channel capacity in satoshis |
| `--push <sats>` | Give the peer initial balance |

#### `close-channel`

Close a Lightning channel. Get `channel_id` and `peer` from `list-channels`.

```bash
bk close-channel 12345678901234567890 02ab... --json
```

```json
{
  "ok": true,
  "data": {
    "channel_id": "12345678901234567890",
    "status": "closing"
  }
}
```

| Arg | Description |
|-----|-------------|
| `<channel_id>` | Channel ID (decimal, from `list-channels`) |
| `<peer>` | Counterparty node public key |
| `--force` | Force close (use when peer is unresponsive) |

**Status values:** `closing` (cooperative), `force_closing`

#### `list-channels`

List all Lightning channels with capacity, balances, and status.

```bash
bk list-channels --json
```

```json
{
  "ok": true,
  "data": [
    {
      "channel_id": "12345678901234567890",
      "peer": "02ab...",
      "capacity_sats": 500000,
      "local_balance_msat": 250000000,
      "remote_balance_msat": 250000000,
      "is_usable": true,
      "is_channel_ready": true,
      "is_outbound": false
    }
  ]
}
```

Note: balances are in millisatoshis. Divide by 1000 for satoshis.

### LSP (Blocktank Liquidity)

Use the Blocktank LSP to get inbound Lightning liquidity without manually finding peers.

#### `lsp info`

Get LSP service info: available nodes, channel limits, fee rates.

```bash
bk lsp info --json
```

```json
{
  "ok": true,
  "data": {
    "nodes": [
      {
        "alias": "blocktank-lsp",
        "pubkey": "02abc...",
        "connection_strings": ["02abc...@1.2.3.4:9735"]
      }
    ],
    "min_channel_size_sats": 20000,
    "max_channel_size_sats": 5000000,
    "min_expiry_weeks": 2,
    "max_expiry_weeks": 52,
    "network": "Mainnet",
    "fee_rates_fast": 10,
    "fee_rates_mid": 5,
    "fee_rates_slow": 1
  }
}
```

#### `lsp estimate-fee`

Estimate the cost of a channel order before creating it.

```bash
bk lsp estimate-fee 500000 --json
```

```json
{
  "ok": true,
  "data": {
    "fee_sats": 500,
    "network_fee_sats": 300,
    "service_fee_sats": 200
  }
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `<lsp_balance_sats>` | required | Inbound liquidity amount |
| `--expiry <weeks>` | `6` | Channel expiry in weeks |
| `--client-balance-sats <sats>` | `0` | Outbound liquidity (your side) |

#### `lsp create-order`

Create a channel order. Returns payment details.

```bash
bk lsp create-order 500000 --json
```

```json
{
  "ok": true,
  "data": {
    "order_id": "ord-abc123...",
    "state": "Created",
    "fee_sats": 500,
    "lsp_balance_sats": 500000,
    "client_balance_sats": 0,
    "payment_address": "bc1q...",
    "payment_bolt11": "lnbc...",
    "order_expires_at": "2026-03-01T00:00:00Z"
  }
}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `<lsp_balance_sats>` | required | Inbound liquidity amount |
| `--expiry <weeks>` | `6` | Channel expiry in weeks |
| `--client-balance-sats <sats>` | `0` | Your outbound balance |
| `--zero-conf` | off | Enable zero-conf channel |

After creating, pay to `payment_address` (on-chain) or `payment_bolt11` (Lightning). Then poll `get-order` until state becomes `Paid`.

#### `lsp get-order`

Check the status of an order.

```bash
bk lsp get-order ord-abc123 --json
```

```json
{
  "ok": true,
  "data": {
    "order_id": "ord-abc123...",
    "state": "Open",
    "state2": "Paid",
    "fee_sats": 500,
    "lsp_balance_sats": 500000,
    "client_balance_sats": 0,
    "channel_expiry_weeks": 6,
    "channel_state": "Opening",
    "funding_tx": "abc123def...",
    "payment_state": "Paid",
    "order_expires_at": "2026-03-01T00:00:00Z",
    "created_at": "2026-02-17T00:00:00Z"
  }
}
```

`channel_state` and `funding_tx` are `null` until the channel is being opened.

**State enum values for `lsp get-order`:**

| Field | Values | Description |
|-------|--------|-------------|
| `state` | `Created`, `Open`, `Expired`, `Closed` | Legacy order state |
| `state2` | `Created`, `Paid`, `Executed`, `Expired` | Current order state (prefer this) |
| `channel_state` | `Opening`, `Open`, `Closed` | Channel lifecycle state |
| `payment_state` | `Created`, `Paid`, `Refunded`, `RefundAvailable`, `Canceled` | Payment lifecycle state |

Poll `state2` for order progress: `Created` → `Paid` (after on-chain payment) → `Executed` (channel opened).

#### `lsp open-channel`

Tell Blocktank to open a channel to your node. The order must be in `Paid` state. Requires `--listen` so Blocktank can connect.

```bash
bk lsp open-channel ord-abc123 --listen 9735 --json
```

```json
{
  "ok": true,
  "data": {
    "order_id": "ord-abc123...",
    "state": "Open",
    "channel_state": "Opening",
    "funding_tx": "abc123def..."
  }
}
```

### Messaging (Pubky Encrypted)

End-to-end encrypted messaging via the Pubky network. Identity is created during `init`.

#### `message whoami`

Print your Pubky messaging ID. Does not require network access.

```bash
bk message whoami --json
```

```json
{
  "ok": true,
  "data": {
    "pubky_id": "8pinxrz9tuxfz3qo5gkhdebuhtq6mrimh3matdncsrsno7kg45mo"
  }
}
```

#### `message send`

Send an encrypted message to a peer.

```bash
bk message send 8pin...xyz '{"type":"invoice","bolt11":"lnbc...","amount_sats":5000,"description":"service"}' --json
```

```json
{
  "ok": true,
  "data": {
    "message_id": "abc-123-def",
    "recipient": "8pin...xyz"
  }
}
```

| Arg | Description |
|-----|-------------|
| `<pubky>` | Recipient's Pubky ID |
| `<text>` | Message content (plain text or JSON string) |

#### `message read`

Read the full conversation with a peer, sorted by timestamp.

```bash
bk message read 8pin...xyz --json
```

```json
{
  "ok": true,
  "data": {
    "messages": [
      {
        "sender": "8pin...abc",
        "content": "{\"type\":\"invoice\",\"bolt11\":\"lnbc...\",\"amount_sats\":5000,\"description\":\"service\"}",
        "timestamp": 1708000000,
        "verified": true
      }
    ]
  }
}
```

| Field | Description |
|-------|-------------|
| `sender` | Pubky ID of the message author |
| `content` | Message text (may contain JSON -- parse it) |
| `timestamp` | Unix timestamp in seconds |
| `verified` | `true` if cryptographic signature verified |

#### `message listen`

Poll for new messages from a peer. Streams one envelope per line to stdout as messages arrive.

```bash
bk message listen 8pin...xyz --interval 3 --timeout 120 --json
```

Each new message is printed as a single-line envelope:

```json
{"ok":true,"data":{"sender":"8pin...abc","content":"hello","timestamp":1708000001,"verified":true}}
```

| Arg | Default | Description |
|-----|---------|-------------|
| `<pubky>` | required | Peer's Pubky ID |
| `--interval <secs>` | `3` | Poll interval |
| `--timeout <secs>` | `0` (forever) | Stop after this many seconds |

Status messages go to stderr. Only message JSON goes to stdout.

## Agent Integration

### Daemon HTTP API

When the daemon is running (`bk start`), all commands proxy through an HTTP API on `localhost:3457` (configurable via `--port`). The API uses HTTP Basic Auth with auto-generated credentials.

**Authentication:** HTTP Basic Auth (`bitkit:<password>`). Password is auto-generated on first `bk start` and stored in `<wallet_dir>/api-password`.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth) |
| GET | `/balance` | Wallet balance |
| GET | `/info` | Node info |
| GET | `/history?limit=20&type=send` | Payment history |
| GET | `/channels` | List channels |
| GET | `/utxos` | List UTXOs |
| POST | `/address` | Generate receive address |
| POST | `/send` | Send on-chain |
| POST | `/invoice` | Create Lightning invoice |
| POST | `/pay` | Pay Lightning invoice |
| POST | `/estimate-fee` | Estimate on-chain fee |
| POST | `/bump-fee` | RBF fee bump |
| POST | `/cpfp` | CPFP acceleration |
| POST | `/channels/open` | Open channel |
| POST | `/channels/close` | Close channel |
| GET | `/events` | WebSocket event stream |

All responses use the same JSON envelope as CLI `--json` output: `{"ok": true, "data": {...}}`.

**POST Request Body Schemas:**

`POST /address`:
```json
{ "address_type": "native-segwit" }
```
`address_type` is optional. Values: `legacy`, `nested-segwit`, `native-segwit`, `taproot`.

`POST /send`:
```json
{ "address": "bc1q...", "amount_sats": 50000, "drain": false, "fee_rate": 5, "utxos": ["txid:0"] }
```
`amount_sats` is required unless `drain` is `true`. `fee_rate`, `drain`, `utxos` are optional.

`POST /estimate-fee`:
```json
{ "address": "bc1q...", "amount_sats": 50000, "fee_rate": 5, "utxos": ["txid:0"] }
```
`fee_rate` and `utxos` are optional.

`POST /bump-fee`:
```json
{ "txid": "abc123...", "fee_rate": 20 }
```
Both fields required.

`POST /cpfp`:
```json
{ "txid": "abc123...", "fee_rate": 30, "urgent": false }
```
`txid` is required. `fee_rate` and `urgent` are optional (mutually exclusive).

`POST /invoice`:
```json
{ "amount_sats": 5000, "description": "agent service", "expiry": 3600 }
```
`amount_sats` is required. `description` and `expiry` are optional.

`POST /pay`:
```json
{ "bolt11": "lnbc50u1p...", "max_fee": 100, "timeout": 60 }
```
`bolt11` is required. `max_fee` and `timeout` are optional.

`POST /channels/open`:
```json
{ "peer": "02ab...@127.0.0.1:9735", "amount_sats": 100000, "push_sats": 0 }
```
`peer` and `amount_sats` are required. `push_sats` is optional.

`POST /channels/close`:
```json
{ "channel_id": "12345678901234567890", "peer": "02ab...", "force": false }
```
`channel_id` and `peer` are required. `force` is optional (default `false`).

### Webhooks

Configure in `~/.bitkit/<network>/config.toml`:

```toml
webhook_url = "https://your-agent.example.com/webhook"
webhook_secret = "your-hmac-secret"
```

**Events and Payloads:**

Each webhook POST body contains `event`, `data`, and `timestamp` (Unix ms):

**`payment_received`** — Lightning payment received:
```json
{
  "event": "payment_received",
  "data": { "payment_hash": "abc...", "amount_sat": 1000 },
  "timestamp": 1708444800000
}
```

**`payment_sent`** — Outbound Lightning payment succeeded:
```json
{
  "event": "payment_sent",
  "data": { "payment_hash": "abc...", "amount_sat": 5000, "fee_sat": 3 },
  "timestamp": 1708444800000
}
```

**`payment_failed`** — Outbound Lightning payment failed:
```json
{
  "event": "payment_failed",
  "data": { "payment_hash": "abc...", "reason": "RouteNotFound" },
  "timestamp": 1708444800000
}
```
`payment_hash` and `reason` are nullable (may be `null`).

**`channel_ready`** — Channel fully open and usable:
```json
{
  "event": "channel_ready",
  "data": { "channel_id": "4242...", "counterparty_node_id": "02ab..." },
  "timestamp": 1708444800000
}
```
`counterparty_node_id` is nullable.

**`channel_closed`** — Channel closed:
```json
{
  "event": "channel_closed",
  "data": { "channel_id": "4242...", "counterparty_node_id": "02ab...", "reason": "CooperativeClosure" },
  "timestamp": 1708444800000
}
```
`counterparty_node_id` and `reason` are nullable.

**Signature:** `X-Bitkit-Signature: hmac-sha256=<hex>` header (HMAC-SHA256 of body using `webhook_secret`).

**Retry:** 3 attempts with exponential backoff (1s, 4s, 16s).

### WebSocket Events

Connect to `ws://localhost:3457/events` with Basic Auth. Receives the same events as webhooks in real-time as JSON text frames.

```bash
# Example with websocat
websocat ws://localhost:3457/events -H "Authorization: Basic $(echo -n 'bitkit:PASSWORD' | base64)"
```

**Frame format:** Each event is a JSON text frame with the same structure as webhook payloads:

```json
{"event":"payment_received","data":{"payment_hash":"abc...","amount_sat":1000},"timestamp":1708444800000}
```

**Behavior:**
- Server sends a WebSocket Ping every 10 seconds as a keepalive
- If the client falls behind, the server sends a warning frame: `{"warning":"missed 3 events"}`
- Connection closes when: client sends a Close frame, any WebSocket error occurs, or the daemon shuts down
- No client-to-server messages are expected (receive-only stream)

### Configuration Reference

Config file: `~/.bitkit/<network>/config.toml` (created by `bk init`). All fields are under `[node]`:

```toml
[node]
network = "mainnet"                    # "mainnet" or "regtest"
chain_source = "esplora"               # "esplora" or "electrum"
esplora_url = "https://blockstream.info/api"
electrum_url = ""                      # used when chain_source = "electrum"
rgs_url = "https://rapidsync.lightningdevkit.org/snapshot"
blocktank_url = "https://api1.blocktank.to/api"
webhook_url = ""                       # POST target for events
webhook_secret = ""                    # HMAC-SHA256 signing key
auto_liquidity = false                 # enable background inbound capacity monitor
auto_liquidity_threshold_sats = 100000 # order channel when inbound < this
auto_liquidity_channel_size_sats = 500000  # channel size to order
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `network` | string | `"mainnet"` | Bitcoin network |
| `chain_source` | string | `"esplora"` | Chain sync backend: `esplora` or `electrum` |
| `esplora_url` | string | `"https://blockstream.info/api"` | Esplora API URL |
| `electrum_url` | string | `""` | Electrum server URL (regtest: `tcp://127.0.0.1:60001`) |
| `rgs_url` | string | (LDK default) | Rapid Gossip Sync URL for Lightning routing graph |
| `blocktank_url` | string | `"https://api1.blocktank.to/api"` | Blocktank LSP API URL |
| `webhook_url` | string | `""` | Webhook POST target (empty = disabled) |
| `webhook_secret` | string | `""` | HMAC-SHA256 key for `X-Bitkit-Signature` header |
| `auto_liquidity` | bool | `false` | Enable background inbound capacity monitor |
| `auto_liquidity_threshold_sats` | u64 | `100000` | Order channel when inbound capacity drops below this |
| `auto_liquidity_channel_size_sats` | u64 | `500000` | Size of auto-ordered channels |

### Auto-Liquidity

When `auto_liquidity = true` in `config.toml`, the daemon monitors inbound channel capacity every 5 minutes. If total inbound capacity drops below `auto_liquidity_threshold_sats`, it automatically creates a Blocktank channel order for `auto_liquidity_channel_size_sats`.

**Important:** The auto-created order still requires on-chain payment to `payment_address` from the order. The daemon does not pay automatically — an agent or human must fund the order.

**Workflow:**
1. Enable in config: `auto_liquidity = true`
2. Start daemon: `bk start --json`
3. Monitor for `channel_ready` events via webhook or WebSocket
4. When a Blocktank order is created, check `bk lsp get-order <id>` for the `payment_address`
5. Pay the order on-chain, then the channel opens automatically

### API Password

The daemon HTTP API uses HTTP Basic Auth. The password is auto-generated on first `bk start`.

**Location:** `<wallet_dir>/api-password` (e.g., `~/.bitkit/api-password`)
**Format:** 32 random bytes encoded as 64 hex characters
**Permissions:** File mode `0600` (owner read/write only)

```bash
# Read the password
cat ~/.bitkit/api-password

# Use with curl
curl -u "bitkit:$(cat ~/.bitkit/api-password)" http://localhost:3457/balance

# Use with WebSocket
websocat ws://localhost:3457/events -H "Authorization: Basic $(echo -n "bitkit:$(cat ~/.bitkit/api-password)" | base64)"
```

The password persists across daemon restarts. Delete the file to force regeneration on next `bk start`.

## Error Handling

### Exit Codes

| Code | Name | Common Causes | Recovery |
|------|------|---------------|----------|
| 0 | Success | -- | -- |
| 1 | User error | Bad input, missing wallet, invalid invoice, expired invoice | Fix input and retry |
| 2 | Network error | Connection failed, sync timeout, payment timeout | Retry after delay |
| 3 | Insufficient funds | Not enough on-chain or Lightning balance | Fund wallet or open channel |

### Error Envelope

When `--json` is used and an error occurs, a structured error envelope is written to stderr:

```json
{
  "ok": false,
  "error": "Invalid invoice: ...",
  "code": 1
}
```

### Bash Pattern

```bash
OUTPUT=$(bk pay "$BOLT11" --json 2>/dev/null)
EXIT_CODE=$?

case $EXIT_CODE in
  0) echo "Success: $(echo "$OUTPUT" | jq -r '.data.payment_hash')" ;;
  1) echo "Bad input -- check the invoice" >&2; exit 1 ;;
  2) echo "Network issue -- retrying..." >&2; sleep 5; bk pay "$BOLT11" --json ;;
  3) echo "Insufficient funds" >&2; exit 3 ;;
esac
```

**Important:** Errors print to stderr (as JSON envelope when `--json` is used). Success output prints to stdout. Always capture them separately.

## Multi-Wallet Pattern

Run multiple independent agent wallets by using separate data directories.

```bash
export BITKIT_DIR="/tmp/agent-${SESSION_ID}"
bk init --no-password --json
bk address --json
# ... each agent operates independently
```

Or use the `--dir` flag:

```bash
bk --dir /tmp/agent-alice init --no-password --json
bk --dir /tmp/agent-bob init --no-password --json
```

Each directory gets its own seed, node identity, Pubky ID, and channel state. Agents sharing a machine can run concurrently with different `--dir` values.

## Input Validation Reference

| Format | Pattern | Example |
|--------|---------|---------|
| Node pubkey | 66-char hex (compressed secp256k1) | `02abc123...` |
| Peer address | `pubkey@host:port` | `02abc...@127.0.0.1:9735` |
| Transaction ID | 64-char hex | `4a5e1e4baab89f3a...` |
| Outpoint | `txid:vout` (decimal vout) | `4a5e1e4b...:0` |
| Channel ID | Decimal u128 | `12345678901234567890` |
| Bitcoin address | Network-validated bech32/base58 | `bc1q...`, `bcrt1q...` |
| BOLT11 invoice | `lnbc...` or `lnbcrt...` prefix | `lnbc50u1p...` |
| LNURL | Bech32 with `lnurl` HRP | `lnurl1dp68gurn...` |
| Lightning Address | `user@domain.tld` | `agent@pay.bitkit.to` |
| Pubky ID | 52-char z-base-32 | `8pinxrz9tux...45mo` |
| Fee rate | Positive integer (sat/vb) | `5` |
| Amount | Non-negative integer (satoshis) | `50000` |

All validation errors exit with code 1 and include a descriptive error message.

## Messaging Workflow

### Agent Message Protocol

Agents communicate structured data by sending JSON strings as message content. The convention uses a `type` field to distinguish message kinds:

**Invoice request:**

```json
{
  "type": "invoice",
  "bolt11": "lnbc50u1p...",
  "amount_sats": 5000,
  "description": "data analysis service"
}
```

**Payment confirmation:**

```json
{
  "type": "payment_confirmation",
  "payment_hash": "a1b2c3d4e5f6...",
  "amount_sats": 5000
}
```

### Workflow: Discover, Message, Pay

```bash
# 1. Get your own Pubky ID to share with other agents
MY_ID=$(bk message whoami --json | jq -r '.data.pubky_id')

# 2. Send a message to another agent
bk message send "$PEER_PUBKY" "Hello, I need data analysis" --json

# 3. Listen for their reply (they'll send an invoice)
bk message listen "$PEER_PUBKY" --timeout 120 --json | while IFS= read -r MSG; do
  TYPE=$(echo "$MSG" | jq -r '.data.content' | jq -r '.type // empty' 2>/dev/null)
  if [ "$TYPE" = "invoice" ]; then
    BOLT11=$(echo "$MSG" | jq -r '.data.content' | jq -r '.bolt11')
    echo "Received invoice: $BOLT11"
    break
  fi
done

# 4. Pay the invoice
bk pay "$BOLT11" --json
```

## End-to-End: Pay Another Agent

Complete flow where Agent A requests a service, Agent B invoices for it, Agent A pays, and Agent B confirms.

### Agent B (service provider)

```bash
#!/usr/bin/env bash
set -euo pipefail
export BITKIT_DIR=/tmp/agent-b

# Initialize and share identity
bk init --no-password --json >/dev/null
MY_ID=$(bk message whoami --json | jq -r '.data.pubky_id')
echo "Agent B Pubky ID: $MY_ID"

# Listen for requests from Agent A
bk message listen "$AGENT_A_PUBKY" --timeout 300 --json | while IFS= read -r MSG; do
  CONTENT=$(echo "$MSG" | jq -r '.data.content')

  # Create invoice for the requested service
  INVOICE_JSON=$(bk invoice 5000 --description "data analysis" --json)
  BOLT11=$(echo "$INVOICE_JSON" | jq -r '.data.bolt11')

  # Send invoice to Agent A
  PAYLOAD=$(jq -n --arg b "$BOLT11" '{type:"invoice",bolt11:$b,amount_sats:5000,description:"data analysis"}')
  bk message send "$AGENT_A_PUBKY" "$PAYLOAD" --json

  # Wait for payment
  RECEIVED=$(bk invoice 5000 --description "data analysis" --wait --listen 9735 --json | tail -1)
  HASH=$(echo "$RECEIVED" | jq -r '.data.payment_hash')

  # Confirm payment
  CONFIRM=$(jq -n --arg h "$HASH" '{type:"payment_confirmation",payment_hash:$h,amount_sats:5000}')
  bk message send "$AGENT_A_PUBKY" "$CONFIRM" --json
  break
done
```

### Agent A (client)

```bash
#!/usr/bin/env bash
set -euo pipefail
export BITKIT_DIR=/tmp/agent-a

# Initialize
bk init --no-password --json >/dev/null
MY_ID=$(bk message whoami --json | jq -r '.data.pubky_id')

# Request service from Agent B
bk message send "$AGENT_B_PUBKY" "Please analyze dataset X" --json

# Wait for invoice
BOLT11=""
bk message listen "$AGENT_B_PUBKY" --timeout 120 --json | while IFS= read -r MSG; do
  TYPE=$(echo "$MSG" | jq -r '.data.content' | jq -r '.type // empty' 2>/dev/null)
  if [ "$TYPE" = "invoice" ]; then
    BOLT11=$(echo "$MSG" | jq -r '.data.content' | jq -r '.bolt11')
    break
  fi
done

# Pay the invoice
PAY_RESULT=$(bk pay "$BOLT11" --json)
echo "Payment status: $(echo "$PAY_RESULT" | jq -r '.data.status')"
echo "Fee paid: $(echo "$PAY_RESULT" | jq -r '.data.fee_sat') sats"

# Wait for confirmation
bk message listen "$AGENT_B_PUBKY" --timeout 60 --json | while IFS= read -r MSG; do
  TYPE=$(echo "$MSG" | jq -r '.data.content' | jq -r '.type // empty' 2>/dev/null)
  if [ "$TYPE" = "payment_confirmation" ]; then
    echo "Payment confirmed by Agent B"
    break
  fi
done
```

## Security & Privacy

**Trust model:** Fully self-custodial. The BIP39 seed never leaves the local machine. No telemetry, analytics, or tracking of any kind.

**External endpoints contacted:**

| Endpoint | Purpose | Data Sent | Configurable |
|----------|---------|-----------|--------------|
| Esplora server | Chain sync (mainnet) | Transaction queries | Yes (`esplora_url`) |
| Electrum server | Chain sync (regtest) | Transaction queries | Yes (`electrum_url`) |
| RGS server | Lightning gossip sync | None (download only) | Yes (`rgs_url`) |
| Blocktank API | LSP channel orders | Node ID, order params | Yes (`blocktank_url`) |
| LNURL service | Pay/withdraw resolution | Amount, callback URL | User-initiated only |
| Pubky DHT | Encrypted messaging | E2E encrypted payloads | Built-in |
| Webhook URL | Event notifications | Payment/channel events | Yes (`webhook_url`) |

**Seed storage:** Custom binary format with magic bytes (`BKIT`), version byte, and encrypted (AES-256-GCM + Argon2id KDF) or plaintext flag. File: `~/.bitkit/<network>/seed.enc`.

**API password:** Auto-generated 32-byte random hex, stored with `0600` permissions. Only used for local daemon HTTP API access.

## LSP Workflow: Fresh Wallet to Lightning-Ready

From a brand new wallet to being able to send and receive Lightning payments:

```bash
# 1. Create wallet
bk init --no-password --json

# 2. Get on-chain address
ADDRESS=$(bk address --json | jq -r '.data.address')
echo "Fund this address: $ADDRESS"

# 3. (Fund the address externally, wait for confirmation)

# 4. Estimate channel fees
bk lsp estimate-fee 500000 --json

# 5. Create channel order
ORDER_ID=$(bk lsp create-order 500000 --json | jq -r '.data.order_id')

# 6. Pay the order on-chain (the payment_address from create-order)
# ... or wait for on-chain funding to cover it

# 7. Poll until order is paid
while true; do
  STATE=$(bk lsp get-order "$ORDER_ID" --json | jq -r '.data.state2')
  [ "$STATE" = "Paid" ] && break
  sleep 10
done

# 8. Open the channel
bk lsp open-channel "$ORDER_ID" --listen 9735 --json

# 9. Verify channel is active
bk list-channels --json | jq '.data[0].is_usable'

# Now ready to send and receive Lightning payments
```

## Tags

bitcoin, lightning, payment, invoice, self-custody, wallet, CLI, agent, LNURL, lightning-address, BOLT11, LSP, lowest-fees, daemon, webhooks, websocket, encrypted-messaging, on-chain, channels, liquidity
