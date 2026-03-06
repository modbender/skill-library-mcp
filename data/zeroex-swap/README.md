# 0x Swap Skill

Secure ERC‑20 swaps via 0x Swap API.

## Files
- `SKILL.md` — agent skill instructions
- `quote.js` — fetch quotes
- `swap.js` — execute swaps
- `package.json` — dependencies

## Setup
```bash
npm install
export ZEROEX_API_KEY="your-0x-api-key"
export PRIVATE_KEY="your-private-key-hex"
export RPC_URL="https://mainnet.base.org"  # optional
```

## Usage
```bash
node quote.js --sell USDC --buy WETH --amount 1 --chain base
node swap.js  --sell USDC --buy WETH --amount 1 --chain base
```

## Security
- Use a dedicated hot wallet
- Set slippage protection
- Approve exact amounts only
