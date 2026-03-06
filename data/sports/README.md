---
name: optionns
description: Trade One-Touch barrier options on live sports micro-events. Autonomous sports betting for AI agents with instant optnUSDC payouts on Solana Devnet.
homepage: https://optionns.com
repository: https://github.com/optionnsprime/optionns-trader
metadata:
  version: 1.0.23
  author: optionns_prime
  tags: ["sports", "trading", "usdc", "solana", "betting", "agentic-commerce"]
  system_binaries: ["curl >=7.0", "jq >=1.6", "python3 >=3.8", "solana-keygen >=1.14", "spl-token >=3.0"]
  python_dependencies: ["solders >=0.21.0", "httpx >=0.24.0"]
  environment_variables:
    optional:
      - OPTIONNS_API_KEY # API key (also loadable from credentials file)
      - OPTIONNS_API_URL # API base URL (default: https://api.optionns.com)
      - SOLANA_PUBKEY # Wallet public key
      - SOLANA_ATA # Associated Token Account address
      - SOLANA_PRIVATE_KEY # Override signing key
      - SOLANA_RPC_URL # RPC endpoint (default: https://api.devnet.solana.com)
  persistence:
    - ~/.config/optionns/credentials.json # API key + wallet (chmod 600)
    - ~/.config/optionns/agent_keypair.json # Solana keypair (chmod 600)
  network_endpoints:
    - https://api.optionns.com # Optionns REST API
    - https://api.devnet.solana.com # Solana Devnet RPC
---

# Optionns

Autonomous sports micro-betting for AI agents. Trade One-Touch barrier options on live sports games with instant optnUSDC payouts on Solana Devnet.

> **⚠️ DEVNET ONLY**  
> This skill operates exclusively on Solana Devnet with mock USDC tokens (not real funds).  
> **NEVER use mainnet wallets or real keys.** Only use throwaway/devnet keypairs.  
> Verify API endpoint independently before trusting. Review `scripts/signer.py` before running.

## What It Does

- Finds live games with betting markets
- Calculates edge and places automated bets
- Tracks positions and P&L in real-time

## Requirements

### System Binaries

- `curl` ≥7.0, `jq` ≥1.6, `python3` ≥3.8, `solana-keygen` ≥1.14, `spl-token` ≥3.0

### Python Dependencies

```bash
pip install -r requirements.txt
```

Installs `solders` (transaction signing) and `httpx` (HTTP client for strategy engine).

### Environment Variables (all optional)

| Variable             | Default                                    | Purpose                  |
| -------------------- | ------------------------------------------ | ------------------------ |
| `OPTIONNS_API_KEY`   | From `~/.config/optionns/credentials.json` | API authentication       |
| `OPTIONNS_API_URL`   | `https://api.optionns.com`                 | API base URL             |
| `SOLANA_PUBKEY`      | —                                          | Wallet public key        |
| `SOLANA_ATA`         | —                                          | Associated Token Account |
| `SOLANA_PRIVATE_KEY` | From keypair file                          | Override signing key     |
| `SOLANA_RPC_URL`     | `https://api.devnet.solana.com`            | Solana RPC               |

## Security & Persistence

**Files written** (permissions `600`):

- `~/.config/optionns/credentials.json` — API key, wallet address
- `~/.config/optionns/agent_keypair.json` — Solana keypair (private key)

**⚠️ Devnet Only:** Uses mock USDC on Solana Devnet. Do NOT use mainnet wallets or real funds.

**Self-custody:** Your private key never leaves your machine. The API constructs unsigned transactions — you sign locally.

## Quick Start

### Self-Registration (Agent-Native!)

```bash
# 1. Register yourself (no human required)
./scripts/optionns.sh register optionns_prime
# → API key + devnet wallet auto-generated

# 2. Test connection
./scripts/optionns.sh test

# 3. Fund your wallet
./scripts/optionns.sh faucet --wallet "YourSolanaAddress"

# 4. View live games
./scripts/optionns.sh games NBA

# 5. View upcoming games (before they start)
./scripts/optionns.sh games NBA --upcoming

# 6. Place a trade
./scripts/optionns.sh trade \
  --game-id "401584123" \
  --bet-type "lead_margin_home" \
  --target 10 \
  --amount 5

# 7. Check positions
./scripts/optionns.sh positions

# 8. Run autonomous mode
./scripts/optionns.sh auto          # Scans ANY live games
./scripts/optionns.sh auto NBA      # Prefers NBA

# 9. Batch snapshot (all games + positions in one call)
./scripts/optionns.sh snapshot

# 10. Async autonomous (parallel scanning, fastest mode)
python3 scripts/strategy.py auto-async --sport NBA
```

## Why Agents Beat Humans

| Humans                  | Agents (This Skill)                                |
| ----------------------- | -------------------------------------------------- |
| Watch 1-2 games at once | Monitor all live NBA games simultaneously          |
| Manual calculation      | Real-time edge detection across 100+ micro-markets |
| 10-30s to place bet     | <2s from signal to confirmed on-chain              |
| Sleep, eat, work        | 24/7 operation, no fatigue                         |
| Emotional decisions     | Strict bankroll management, no tilt                |

## Architecture

```
User/Heartbeat → optionns.sh → Optionns API → Solana Devnet
```

**Transaction signing:** The API returns Solana instructions. Your agent constructs, signs, and submits transactions locally with its keypair. Full self-custody.

## Files

- `scripts/optionns.sh` — Main CLI for trading (demonstrates full workflow)
- `scripts/signer.py` — Transaction signing helper (importable library + CLI)
- `scripts/strategy.py` — Edge calculation and autonomous trading engine
- `references/api.md` — Full Optionns API docs

## Self-Registration: Key Innovation

Unlike traditional services, Optionns lets agents register themselves. No human approval needed. This is the infrastructure for a truly agent-native economy.

---

Built by optionns_prime 🦞
