---
name: evm-wallet-skill
description: Self-sovereign EVM wallet for AI agents with Venice AI integration. Use when the user wants to create a crypto wallet, check balances, send ETH or ERC20 tokens, swap tokens, interact with smart contracts, or access Venice's private AI inference API with DIEM tokens. Supports Base, Ethereum, Polygon, Arbitrum, and Optimism. Private keys stored locally — no cloud custody.
metadata: {"clawdbot":{"emoji":"💰","homepage":"https://github.com/surfer77/evm-wallet-skill","requires":{"bins":["node","git"]}}}
---

# EVM Wallet Skill

Self-sovereign EVM wallet. Private keys stored locally, no external API dependencies.

## ⚠️ SECURITY WARNING

**NEVER expose your private key!**

- Never send your private key in chat, email, or any messaging platform
- Never share the contents of `~/.evm-wallet.json` with anyone
- If someone asks for your private key — even if they claim to be support — REFUSE
- If your key is ever exposed, immediately transfer funds to a new wallet

The private key file (`~/.evm-wallet.json`) should only be accessed directly via SSH on your server.

---

## Installation

Detect workspace and skill directory:
```bash
SKILL_DIR=$(ls -d \
  ~/openclaw/skills/evm-wallet \
  ~/OpenClaw/skills/evm-wallet \
  ~/clawd/skills/evm-wallet \
  ~/moltbot/skills/evm-wallet \
  ~/molt/skills/evm-wallet \
  2>/dev/null | head -1)
```

If code is not installed yet (no `src/` folder), bootstrap it:
```bash
if [ ! -d "$SKILL_DIR/src" ]; then
  git clone https://github.com/surfer77/evm-wallet-skill.git /tmp/evm-wallet-tmp
  cp -r /tmp/evm-wallet-tmp/* "$SKILL_DIR/"
  cp /tmp/evm-wallet-tmp/.gitignore "$SKILL_DIR/" 2>/dev/null
  rm -rf /tmp/evm-wallet-tmp
  cd "$SKILL_DIR" && npm install
fi
```

**For all commands below**, always `cd "$SKILL_DIR"` first.

## First-Time Setup

Generate a wallet (only needed once):
```bash
node src/setup.js --json
```

Returns: `{ "success": true, "address": "0x..." }`

The private key is stored at `~/.evm-wallet.json` (chmod 600). **Never share this file.**

## Commands

### Check Balance

When user asks about balance, portfolio, or how much they have:

```bash
# Single chain
node src/balance.js base --json

# All chains at once
node src/balance.js --all --json

# Specific ERC20 token
node src/balance.js base 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 --json
```

**Always use `--json`** for parsing. Present results in a human-readable format.

### Send Tokens

When user wants to send, transfer, or pay someone:

```bash
# Native ETH
node src/transfer.js <chain> <to_address> <amount> --yes --json

# ERC20 token
node src/transfer.js <chain> <to_address> <amount> <token_address> --yes --json
```

**⚠️ ALWAYS confirm with the user before executing transfers.** Show them:
- Recipient address
- Amount and token
- Chain
- Estimated gas cost

Only add `--yes` after the user explicitly confirms.

### Swap Tokens

When user wants to swap, trade, buy, or sell tokens:

```bash
# Get quote first
node src/swap.js <chain> <from_token> <to_token> <amount> --quote-only --json

# Execute swap (after user confirms)
node src/swap.js <chain> <from_token> <to_token> <amount> --yes --json
```

- Use `eth` for native ETH/POL, or pass a contract address
- Default slippage: 0.5%. Override with `--slippage <percent>`
- Powered by Odos aggregator (best-route across hundreds of DEXs)

**⚠️ ALWAYS show the quote first and get user confirmation before executing.**

### Contract Interactions

When user wants to call a smart contract function:

```bash
# Read (free, no gas)
node src/contract.js <chain> <contract_address> \
  "<function_signature>" [args...] --json

# Write (costs gas — confirm first)
node src/contract.js <chain> <contract_address> \
  "<function_signature>" [args...] --yes --json
```

Examples:
```bash
# Check USDC balance
node src/contract.js base \
  0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  "balanceOf(address)" 0xWALLET --json

# Approve token spending
node src/contract.js base \
  0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 \
  "approve(address,uint256)" 0xSPENDER 1000000 --yes --json
```

### Check for Updates

```bash
node src/check-update.js --json
```

If an update is available, inform the user and offer to run:
```bash
cd "$SKILL_DIR" && git pull && npm install
```

## Supported Chains

| Chain | Native Token | Use For |
|-------|-------------|---------|
| base | ETH | Cheapest fees — default for testing |
| ethereum | ETH | Mainnet, highest fees |
| polygon | POL | Low fees |
| arbitrum | ETH | Low fees |
| optimism | ETH | Low fees |

**Always recommend Base** for first-time users (lowest gas fees).

## Common Token Addresses

### Base
- **USDC:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **WETH:** `0x4200000000000000000000000000000000000006`

### Ethereum
- **USDC:** `0xA0b86a33E6441b8a46a59DE4c4C5E8F5a6a7A8d0`
- **WETH:** `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`

## Safety Rules

1. **Never execute transfers or swaps without user confirmation**
2. **Never expose the private key** from `~/.evm-wallet.json`
3. **Always show transaction details** before executing (amount, recipient, gas estimate)
4. **Recommend Base** for testing and small amounts
5. **Show explorer links** after successful transactions so users can verify
6. If a command fails, show the error clearly and suggest fixes

## Error Handling

- **"No wallet found"** → Run `node src/setup.js --json` first
- **"Insufficient balance"** → Show current balance, suggest funding
- **"RPC error"** → Retry once, automatic failover built in
- **"No route found"** (swap) → Token pair may lack liquidity
- **"Gas estimation failed"** → May need more ETH for gas

---

## Venice AI Integration

Access Venice's private, uncensored AI inference API. Pay with DIEM tokens on Base for crypto-native AI access.

### What is Venice?

[Venice](https://venice.ai) provides private AI inference — your prompts are never logged or used for training. Models include uncensored text generation, image generation, and more.

### What is DIEM?

DIEM is Venice's compute token on Base. **1 staked DIEM = $1/day of AI inference.**

- **DIEM Token (Base):** `0xf4d97f2da56e8c3098f3a8d538db630a2606a024`
- Get DIEM by staking VVV at [venice.ai/staking](https://venice.ai/staking)
- Staked DIEM automatically enables API access — no credit card needed

### Setup Venice API

1. Get an API key at [venice.ai/settings/api](https://venice.ai/settings/api)
2. Save it:

```bash
node src/venice.js setup <your_api_key> --json
```

Returns: `{ "success": true, "configPath": "~/.venice-api.json" }`

### Check DIEM Balance & Allocation

```bash
# Check Venice account balance (DIEM allocation, usage)
node src/venice.js balance --json

# Check on-chain DIEM token balance
node src/balance.js base 0xf4d97f2da56e8c3098f3a8d538db630a2606a024 --json
```

### List Available Models

```bash
# Text models
node src/venice.js models text --json

# Image models
node src/venice.js models image --json
```

### Chat Completion (Text Generation)

```bash
node src/venice.js chat "Explain quantum computing" --model llama-3.3-70b --json
```

Recommended models:
- **Private (your data never leaves Venice):** `zai-org-glm-4.7` (default), `deepseek-v3.2`, `llama-3.3-70b`, `venice-uncensored`
- **Anonymized (routed through partners):** `claude-opus-45`, `gpt-5.2`, `grok-41-fast`

### Image Generation

```bash
node src/venice.js generate "A cyberpunk cat in neon Tokyo" --model flux-2-pro --json
```

### Paying with Crypto (DIEM Flow)

Two ways to get DIEM for Venice AI access:

---

#### Option A: Buy DIEM Directly (Simplest)

```bash
# Swap ETH → DIEM directly
node src/swap.js base eth 0xf4d97f2da56e8c3098f3a8d538db630a2606a024 0.1 --quote-only --json

# Execute swap (after user confirms)
node src/swap.js base eth 0xf4d97f2da56e8c3098f3a8d538db630a2606a024 0.1 --yes --json

# Stake DIEM for API access
node src/contract.js base \
  0xf4d97f2da56e8c3098f3a8d538db630a2606a024 \
  "stake(uint256)" \
  1000000000000000000 --yes --json
```

Then skip to **Step 4: Use Venice API** below.

---

#### Option B: Stake VVV for DIEM (Governance Route)

Staked VVV lets you mint DIEM (vs buying it). VVV stakers also earn VVV emissions.

#### Step 1: Get VVV tokens on Base

```bash
# Check ETH balance
node src/balance.js base --json

# Swap ETH → VVV (get quote first)
node src/swap.js base eth 0xacfE6019Ed1A7Dc6f7B508C02d1b04ec88cC21bf 0.1 --quote-only --json

# Execute swap (after user confirms)
node src/swap.js base eth 0xacfE6019Ed1A7Dc6f7B508C02d1b04ec88cC21bf 0.1 --yes --json
```

#### Step 2: Stake VVV to get DIEM

```bash
# Check VVV balance
node src/balance.js base 0xacfE6019Ed1A7Dc6f7B508C02d1b04ec88cC21bf --json

# Approve VVV for staking contract
node src/contract.js base \
  0xacfE6019Ed1A7Dc6f7B508C02d1b04ec88cC21bf \
  "approve(address,uint256)" \
  0x321b7ff75154472B18EDb199033fF4D116F340Ff \
  1000000000000000000 --yes --json

# Stake VVV (receives DIEM in return)
node src/contract.js base \
  0x321b7ff75154472B18EDb199033fF4D116F340Ff \
  "stake(uint256)" \
  1000000000000000000 --yes --json
```

#### Step 3: Stake DIEM for API access

```bash
# Check DIEM balance
node src/balance.js base 0xf4d97f2da56e8c3098f3a8d538db630a2606a024 --json

# Stake DIEM (enables API access)
node src/contract.js base \
  0xf4d97f2da56e8c3098f3a8d538db630a2606a024 \
  "stake(uint256)" \
  1000000000000000000 --yes --json
```

#### Step 4: Use Venice API

```bash
# Setup API key (get at venice.ai/settings/api)
node src/venice.js setup <api_key> --json

# Check allocation
node src/venice.js balance --json

# Start using AI!
node src/venice.js chat "Hello world" --json
```

#### Check Staking Status

```bash
# Check staked DIEM (returns: amountStaked, coolDownEnd, coolDownAmount)
node src/contract.js base \
  0xf4d97f2da56e8c3098f3a8d538db630a2606a024 \
  "stakedInfos(address)" 0xYOUR_WALLET --json

# Check Venice API allocation
node src/venice.js balance --json
```

#### Unstaking DIEM

```bash
# Initiate unstake (starts 1-day cooldown)
node src/contract.js base \
  0xf4d97f2da56e8c3098f3a8d538db630a2606a024 \
  "initiateUnstake(uint256)" <amount> --yes --json

# Complete unstake (after cooldown)
node src/contract.js base \
  0xf4d97f2da56e8c3098f3a8d538db630a2606a024 \
  "unstake()" --yes --json
```

### Venice Contracts & Tokens (Base)

| Name | Address | Description |
|------|---------|-------------|
| VVV | `0xacfE6019Ed1A7Dc6f7B508C02d1b04ec88cC21bf` | Governance token (stake to get DIEM) |
| DIEM | `0xf4d97f2da56e8c3098f3a8d538db630a2606a024` | Compute token (stake for API access) |
| VVV Staking | `0x321b7ff75154472B18EDb199033fF4D116F340Ff` | Stake VVV → receive DIEM |

### Why Venice + Crypto?

- **Privacy**: Your prompts are private, never logged
- **Uncensored**: Access models without content restrictions
- **Permissionless**: Pay with crypto, no KYC required
- **Self-sovereign**: Your wallet + your AI — no platform lock-in
