---
name: agent-wallet
description: Multi-chain wallet management for AI agents. Create wallets, check balances, transfer tokens (USDC/native), and bridge cross-chain. Use when agents need to send/receive payments, check funds, or manage crypto wallets. Supports Solana, Base, and Ethereum. Trigger phrases include "create wallet", "check balance", "send USDC", "transfer", "my addresses", "wallet status".
---

# AgentWallet

Multi-chain wallet skill for AI agents. One seed phrase, all chains.

## Quick Reference

| Command | Example |
|---------|---------|
| Create wallet | "Create a new wallet" |
| Show addresses | "Show my addresses" / "What's my wallet?" |
| Check balance | "Check my balance" / "How much USDC do I have?" |
| Transfer | "Send 10 USDC to 0x..." / "Transfer 5 SOL to ..." |
| Bridge | "Bridge 10 USDC from Base to Solana" |
| Chain info | "What chains are supported?" |

## Setup

### New Wallet

```
User: "Create a new wallet"
```

Generates BIP-39 seed phrase, derives addresses for all chains. Shows seed ONCE with security warning.

### Import Existing Wallet

```
User: "Import my wallet"
```

Response: "Add your seed phrase to `.env` as `WALLET_SEED_PHRASE`, then say 'Show my addresses' to verify."

No seed phrases in chat for imports - security first.

### Environment

```bash
# Required for wallet operations
WALLET_SEED_PHRASE="your twelve word seed phrase goes here"

# Optional
NETWORK=testnet          # testnet (default) or mainnet
SOLANA_RPC=              # Custom Solana RPC (defaults to public)
BASE_RPC=                # Custom Base RPC (defaults to public)
ETH_RPC=                 # Custom Ethereum RPC (defaults to public)
```

## Commands

### Create Wallet

Run: `node scripts/wallet.js create`

Output format:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 NEW WALLET GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  CRITICAL: Save this seed phrase securely!
    It will NOT be shown again.
    Anyone with this phrase can access your funds.

Seed Phrase:
┌────────────────────────────────────────────┐
│ word1 word2 word3 word4 word5 word6        │
│ word7 word8 word9 word10 word11 word12     │
└────────────────────────────────────────────┘

Your Addresses:
├─ Solana:   7xK9...mP4q
├─ Base:     0x7a3B...4f2E
└─ Ethereum: 0x7a3B...4f2E (same as Base)

Add to .env:
WALLET_SEED_PHRASE="word1 word2 word3 ..."

Network: TESTNET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Show Addresses

Run: `node scripts/wallet.js addresses`

Shows derived addresses without exposing seed.

### Check Balance

Run: `node scripts/wallet.js balance [chain]`

- `node scripts/wallet.js balance` - All chains
- `node scripts/wallet.js balance solana` - Solana only
- `node scripts/wallet.js balance base` - Base only

Output includes native token + USDC balance per chain.

### Transfer

Run: `node scripts/wallet.js transfer <chain> <token> <amount> <recipient>`

Examples:
- `node scripts/wallet.js transfer solana USDC 10 7xK9fR2...` 
- `node scripts/wallet.js transfer base ETH 0.01 0x7a3B...`
- `node scripts/wallet.js transfer solana SOL 0.5 7xK9fR2...`

Supported tokens per chain:
- **Solana**: SOL, USDC
- **Base**: ETH, USDC
- **Ethereum**: ETH, USDC

### Bridge (Cross-Chain)

Run: `node scripts/wallet.js bridge <from-chain> <to-chain> <amount>`

Bridges USDC between chains using Circle CCTP V2.

Examples:
- `node scripts/wallet.js bridge base solana 10` - Bridge 10 USDC from Base to Solana
- `node scripts/wallet.js bridge ethereum base 50` - Bridge 50 USDC from Ethereum to Base
- `node scripts/wallet.js bridge solana ethereum 25` - Bridge 25 USDC from Solana to Ethereum

**Note:** Bridging takes 1-5 minutes (burn → attestation → mint). Requires USDC on source chain plus native tokens for gas.

### Chain Info

Run: `node scripts/wallet.js chains`

Lists supported chains, networks, and USDC contract addresses.

## Derivation Paths

All chains derive from single BIP-39 seed:

| Chain | Path | Standard |
|-------|------|----------|
| Solana | `m/44'/501'/0'/0'` | Solana/Phantom |
| EVM (Base/Eth) | `m/44'/60'/0'/0/0` | BIP-44 Ethereum |

EVM chains share the same address (same derivation path).

## Security Model

- **One seed per agent** - Each agent instance isolated
- **Seed shown once** - Only at creation, never logged
- **Memory only** - Private keys derived on-demand, never persisted
- **No chat import** - Seeds added via .env only (except generation)

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| "WALLET_SEED_PHRASE not set" | Missing env var | Add seed to .env |
| "Invalid seed phrase" | Wrong format | Must be 12 or 24 words |
| "Insufficient balance" | Not enough funds | Check balance first |
| "Invalid address" | Wrong format | Verify recipient address |

## Chain References

For RPC endpoints, USDC addresses, and chain-specific details, see [references/chains.md](references/chains.md).
