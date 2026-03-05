# GCLAW Skill

**Version 1.1** – **GoldenClaw (GCLAW) Skill** for [OpenClaw](https://openclaw.ai) — a Solana SPL token skill for exchanging services like API tokens and AI compute.

## Package contents

- `goldenclaw.skill` — OpenClaw skill bundle
- `SKILL.md` — Skill metadata and quick reference
- `dist/` — Compiled JavaScript modules (`index.js`, `balance.js`, `wallet.js`, etc.)

## Links

- **Website:** [goldenclaw.org](https://goldenclaw.org)
- **Faucet:** [goldenclaw.org](https://goldenclaw.org)
- **Token:** [Solscan](https://solscan.io/token/8fUqKCgQ2PHcYRnce9EPCeMKSaxd14t7323qbXnSJr4z)
- **X:** [@GClaw68175](https://x.com/GClaw68175)
- **Community:** [moltbook.com](https://moltbook.com)

## Installation

1. Clone this repository or extract to your OpenClaw `skills/` folder
2. Run `npm install` in the skill directory
3. Dependencies are installed automatically when the skill runs if missing

## Commands

| Command | Description |
|---------|-------------|
| `gclaw setup` | Create a new encrypted wallet |
| `gclaw recover <phrase>` | Recover wallet from seed phrase |
| `gclaw balance` | Check GCLAW and SOL balance |
| `gclaw address` | Show your wallet address |
| `gclaw send <amount> <address>` | Send GCLAW tokens to another address |
| `gclaw donate <SOL>` | Donate SOL to main wallet (treasury) |
| `gclaw history [n]` | View last n transactions |
| `gclaw limits` | View spending limits |
| `gclaw claim` | Claim GCLAW from faucet (new wallets only) |
| `gclaw tokenomics` | View distribution stats |
| `gclaw simulate [n]` | Preview first n distributions |
| `gclaw status` | Check configuration status |
| `gclaw delete` | Delete wallet (requires confirmation) |
| `gclaw help` | Show help |

## Configuration

Environment variables (optional):

| Variable | Description |
|----------|-------------|
| `GCLAW_TOKEN_MINT` | Token mint address (default: mainnet GCLAW) |
| `SOLANA_RPC_URL` | Solana RPC endpoint (default: mainnet) |
| `GCLAW_FAUCET_URL` | Faucet API base URL (default: https://goldenclaw.org) |
| `GCLAW_DONATE_ADDRESS` | Main wallet for SOL donations |
| `GCLAW_TX_LIMIT` | Per-transaction limit (default: 100) |
| `GCLAW_DAILY_LIMIT` | Daily spending limit (default: 1000) |
| `GCLAW_CONFIRM_THRESHOLD` | Amount requiring confirmation (default: 50) |
| `OPENCLAW_DATA_DIR` | Data directory for wallet storage |

## Tokenomics

- **Total supply:** 1,000,000,000,000 (1 trillion) GCLAW
- **Distribution:** Each new wallet receives 1/1,000,000 of remaining treasury
- **Fixed supply:** No minting after creation

## Security

- Wallet encrypted with Argon2id + AES-256-GCM
- 24-word BIP39 mnemonic backup (Phantom-compatible)
- Spending limits to protect against unauthorized draining
- Per-transaction and daily limits configurable via env vars

## License

MIT
