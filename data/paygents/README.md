# PayGents

> Let your AI agent request payments without ever touching private keys.

PayGents is an [OpenClaw](https://openclaw.ai) skill that lets AI agents generate wallet deeplinks for EVM payments. The user taps the link, approves in their own wallet (MetaMask, Trust Wallet), and the agent verifies the transaction on-chain.

**No backend. No custody. No private keys.** The agent proposes, the human approves.

## How It Works

```
Agent receives payment request
    ↓
Agent generates wallet deeplink (MetaMask / Trust Wallet)
    ↓
Agent sends link to user via chat (Telegram, Discord, etc.)
    ↓
User taps → wallet opens with pre-filled transfer → user approves
    ↓
Agent verifies transaction on-chain
    ↓
Agent generates receipt ✅
```

## Install

```bash
clawhub install paygents
```

Or clone directly:

```bash
git clone https://github.com/AmitayBohadana/paygents.git
```

## Quick Start

### 1. Generate a Payment Link

```bash
# USDC on Base (MetaMask)
scripts/evm-payment-link.sh \
  --to 0x1234...5678 \
  --amount 10 \
  --chain-id 8453

# Native ETH on Sepolia (Trust Wallet)
scripts/evm-payment-link.sh \
  --to 0x1234...5678 \
  --amount 0.01 \
  --asset ETH \
  --chain-id 11155111 \
  --wallet trust
```

### 2. Verify Transaction

After the user confirms they've sent:

```bash
# Scan recent blocks
scripts/evm-verify-tx.sh \
  --chain-id 8453 \
  --from 0xSENDER \
  --to 0xRECIPIENT \
  --asset ERC20 \
  --amount 10

# Or verify a specific tx hash
scripts/evm-verify-tx.sh \
  --chain-id 8453 \
  --from 0xSENDER \
  --to 0xRECIPIENT \
  --asset ERC20 \
  --amount 10 \
  --tx-hash 0xabc123...
```

### 3. Generate Receipt

```bash
scripts/evm-receipt.sh \
  --tx-hash 0xabc123... \
  --chain-id 8453 \
  --memo "order-42" \
  --merchant "Cool Store" \
  --format markdown
```

### 4. Check Wallet Balance

```bash
# All chains
scripts/evm-balance.sh --address 0x1234...5678

# Single chain
scripts/evm-balance.sh --address 0x1234...5678 --chain-id 8453
```

Returns native + major ERC20 balances (USDC, USDT, WETH, WBTC, DAI) across all supported chains. No API key needed.

## Supported Wallets

| Wallet | Deeplink Support | Flag |
|--------|-----------------|------|
| MetaMask | ✅ Native deeplinks | `--wallet metamask` (default) |
| Trust Wallet | ✅ Native deeplinks | `--wallet trust` |
| Rabby | ❌ No send deeplinks | — |
| Coinbase Wallet | ❌ No send deeplinks | — |

## Supported Chains

| Chain | ID | Default USDC |
|-------|----|-------------|
| Ethereum | `1` | `0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48` |
| Base | `8453` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bDa02913` |
| Sepolia (testnet) | `11155111` | `0x1c7d4b196cb0c7b01d743fbc6116a902379c7238` |
| Base Sepolia (testnet) | `84532` | `0x036CbD53842c5426634e7929541eC2318f3dCf7e` |

## Why PayGents?

Every other AI wallet skill gives the agent custody of private keys. That's a security nightmare.

PayGents takes a different approach:
- **Agent never holds keys** — it only generates payment links
- **Human-in-the-loop** — every payment requires wallet approval (Face ID / biometrics)
- **On-chain verification** — agent confirms the tx actually happened, doesn't trust claims
- **No backend** — pure deeplinks + RPC verification, nothing to host

## Requirements

- `node` (for amount conversion and chain verification)
- `bash`

## License

MIT

## Credits

Built by [Amitay Bohadana](https://github.com/AmitayBohadana). Originally created at the Canteen × Tempo Hackathon.
