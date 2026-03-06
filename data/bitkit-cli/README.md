# bitkit

Lightning/Bitcoin CLI wallet for humans and agents.

**AI agents:** See [SKILL.md](./SKILL.md) for a complete reference on using bitkit-cli as an agent tool.

## Features

- Single static binary -- no daemon, no runtime dependencies
- Optional daemon mode -- keeps node running for instant command execution
- Machine-readable `--json` output on every command
- Mainnet by default, regtest for development
- LNURL-pay, LNURL-withdraw, and Lightning Address support
- Blocktank LSP integration for managed channel opening
- Encrypted seed (AES-256-GCM + Argon2id) or plaintext for automation
- Also available as `bk` (short alias)
- Works both ways: stateless per-command or persistent daemon

## Quick Start

```bash
bitkit init --no-password
bitkit address                              # fund this on-chain
bitkit balance
bitkit lsp info                             # check LSP service info
bitkit lsp create-order 500000              # order inbound liquidity
bitkit lsp get-order <order_id>             # check order status
bitkit lsp open-channel <order_id>          # open channel once paid
bitkit invoice 5000 --description "coffee"
bitkit pay <bolt11>
bitkit history
```

## Installation

```bash
curl -sSL https://raw.githubusercontent.com/synonymdev/bitkit-cli/main/install.sh | sh
```

Or build from source:

```bash
git clone --recurse-submodules https://github.com/synonymdev/bitkit-cli.git
cd bitkit-cli
cargo build --release
# binaries at target/release/bitkit and target/release/bk
```

Requires Rust 1.85+.

## For AI Agents

```bash
bitkit init --no-password --json   # create wallet
bitkit start --json                # start daemon
bitkit invoice 5000 --json         # receive payment
bitkit pay lnbc... --json          # send payment
```

Every command supports `--json`. Daemon mode keeps the node running for instant execution. Real-time events available via `ws://localhost:3457/events` (Basic Auth with `bitkit:<api-password>`). See [SKILL.md](./SKILL.md) for the full agent reference including webhook config, WebSocket events, and daemon API endpoints.

### bitkit-cli vs phoenixd

| | bitkit-cli | phoenixd |
|---|---|---|
| LSP fees | Lowest (Blocktank) | Higher (ACINQ) |
| Runtime | Single Rust binary | JVM (requires JRE 11+) |
| Exit codes | Typed: 0/1/2/3 | 0 or 1 |
| Output | JSON envelope on all commands | JSON on API only |
| Messaging | E2E encrypted (Pubky) | None |
| Fee bumping | RBF + CPFP | CPFP only |
| On-chain addresses | Legacy/SegWit/Taproot | SegWit only |
| Webhooks | HMAC-SHA256, 3x retry | HMAC-SHA256, fire-and-forget |
| WebSocket | `/events` with auth | `/websocket` |

## Commands

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `init` | Create a new wallet | `--password`, `--no-password` |
| `start` | Start background daemon | `--port` (default 3457) |
| `stop` | Stop running daemon | |
| `status` | Check daemon status | |
| `invoice` | Generate a BOLT 11 invoice | `<amount_sats>`, `--description`, `--wait`, `--qr` |
| `pay` | Pay a BOLT 11 invoice or LNURL (fixed-amount) | `<bolt11>`, `--max-fee`, `--timeout` |
| `withdraw` | Withdraw from an LNURL-withdraw endpoint | `<lnurl>`, `--amount` |
| `balance` | Show wallet balance | `--btc` |
| `config` | Show resolved config with sources | |
| `info` | Show wallet and node status | |
| `history` | List recent transactions | `--limit`, `--type` |
| `address` | Get on-chain receive address | `--type`, `--validate`, `--qr` |
| `send` | Send bitcoin on-chain | `<address>`, `<amount_sats>`, `--drain`, `--fee-rate`, `--utxo` |
| `list-utxos` | List spendable UTXOs | |
| `estimate-fee` | Preview fee before sending | `<address>`, `<amount_sats>`, `--fee-rate` |
| `bump-fee` | Bump fee via RBF | `<txid>`, `<fee_rate>` |
| `cpfp` | Accelerate tx via CPFP | `<txid>`, `--fee-rate`, `--urgent` |
| `open-channel` | Open a Lightning channel | `<peer>`, `<amount_sats>`, `--push` |
| `close-channel` | Close a Lightning channel | `<channel_id>`, `<peer>`, `--force` |
| `list-channels` | List Lightning channels | |
| `lsp info` | Show LSP service info (nodes, limits) | |
| `lsp estimate-fee` | Estimate channel order fees | `<lsp_balance_sats>` |
| `lsp create-order` | Create a channel order | `<lsp_balance_sats>`, `--expiry`, `--client-balance`, `--zero-conf` |
| `lsp get-order` | Check order status | `<order_id>` |
| `lsp open-channel` | Open channel for a paid order | `<order_id>` |
| `lsp regtest mine` | Mine regtest blocks | `[count]` (default 6) |
| `lsp regtest deposit` | Deposit sats in regtest | `[amount_sats]`, `--address` |
| `lsp regtest pay` | Pay invoice from LSP node | `<bolt11>`, `--amount` |
| `message send` | Send encrypted message | `<recipient>`, `<message>` |
| `message read` | Read messages | `[--from]`, `[--limit]` |
| `message whoami` | Show messaging identity | |
| `completions` | Generate shell completions (hidden) | `<shell>` (bash, zsh, fish, etc.) |

## Shell Completions

Generate tab-completion scripts for your shell:

```bash
# Bash
bitkit completions bash > ~/.local/share/bash-completion/completions/bitkit

# Zsh
bitkit completions zsh > ~/.zfunc/_bitkit

# Fish
bitkit completions fish > ~/.config/fish/completions/bitkit.fish
```

## Global Options

| Option | Env Variable | Description |
|--------|-------------|-------------|
| `--json` | | Machine-readable JSON output |
| `--dir <path>` | `BITKIT_DIR` | Wallet data directory (default `~/.bitkit/`) |
| `--network <net>` | `BITKIT_NETWORK` | Bitcoin network: mainnet, regtest |
| `--listen <port>` | `BITKIT_LISTEN` | P2P listen port (enables inbound connections) |
| `--password <pw>` | `BITKIT_PASSWORD` | Wallet password (for encrypted seeds) |

## Networks

| Network | Chain Source | Default URL | Blocktank URL |
|---------|-------------|-------------|---------------|
| mainnet | Esplora | `https://blockstream.info/api` | `https://api1.blocktank.to/api` |
| regtest | Electrum | `tcp://127.0.0.1:60001` | `https://api.stag0.blocktank.to/blocktank/api/v2` |

Mainnet also uses [Rapid Gossip Sync](https://docs.rs/lightning-rapid-gossip-sync) for fast graph updates.

## Daemon Mode

By default, bitkit cold-starts the LDK node for each command and stops it on exit. For faster execution, run a persistent daemon:

```bash
bitkit start                  # start daemon (default port 3457)
bitkit start --port 8080      # custom port
bitkit status                 # check if daemon is running
bitkit balance                # instant -- proxied through daemon
bitkit stop                   # stop daemon
```

When the daemon is running, all commands automatically proxy through its HTTP API. When stopped, commands fall back to the per-command cold-start behavior. No configuration changes needed.

## Webhooks

Configure event notifications in `~/.bitkit/<network>/config.toml`:

```toml
[node]
webhook_url = "https://your-agent.example.com/webhook"
webhook_secret = "your-hmac-secret"
```

Events: `payment_received`, `payment_sent`, `payment_failed`, `channel_ready`, `channel_closed`. Each POST includes an `X-Bitkit-Signature` HMAC-SHA256 header. Retries 3 times with exponential backoff.

## Auto-Liquidity

Automatically order inbound Lightning capacity when it drops below a threshold:

```toml
[node]
auto_liquidity = true
auto_liquidity_threshold_sats = 100000
auto_liquidity_channel_size_sats = 500000
```

Checks every 5 minutes while the daemon is running. Creates a Blocktank order when inbound capacity falls below the threshold. The order still requires on-chain payment.

## Wallet Directory

Default: `~/.bitkit/`

```
~/.bitkit/
  seed.enc          # BIP39 mnemonic (encrypted or plaintext)
  config.toml       # Node configuration (network, URLs)
  api-password      # Daemon HTTP API password (auto-generated, 0600)
  daemon.json       # Daemon PID file (created by `bitkit start`)
  recovery.pkarr    # Pubky messaging identity
  ldk_node/         # LDK Node persistent storage
```

Override with `--dir` or `BITKIT_DIR`.

## JSON Output

All commands support `--json` for machine-readable output wrapped in an envelope:

```bash
$ bitkit balance --json
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

Errors (when `--json` is used) are written to stderr:

```json
{ "ok": false, "error": "No wallet found...", "code": 1 }
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error (bad input, missing wallet) |
| 2 | Network error (connection, sync timeout) |
| 3 | Insufficient funds |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BITKIT_DIR` | Wallet data directory |
| `BITKIT_NETWORK` | Bitcoin network |
| `BITKIT_LISTEN` | P2P listen port |
| `BITKIT_PASSWORD` | Wallet password (for encrypted seeds) |

## License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for more details.
