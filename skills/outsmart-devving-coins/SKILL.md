---
name: outsmart-devving-coins
description: "Launch tokens on Solana launchpads. Use when: user asks about creating a token, devving a coin, launching a meme, PumpFun, LaunchLab, Jupiter Studio, DBC, bonding curve, deploy token. NOT for: buying existing tokens (use trading), LP on existing pools (use farming)."
homepage: https://github.com/outsmartchad/outsmart-cli
metadata: { "openclaw": { "requires": { "bins": ["outsmart"], "env": ["PRIVATE_KEY", "MAINNET_ENDPOINT"] }, "install": [{ "id": "node", "kind": "node", "package": "outsmart", "bins": ["outsmart"], "label": "Install outsmart CLI (npm)" }] } }
---

# Devving Coins

Launch tokens that fit the moment. Catch a narrative early, create the token, earn from bonding curve fees + LP after graduation.

## When to Use

- "Launch a memecoin"
- "Dev a coin for this meta"
- "Create a token on PumpFun"
- "How do I launch on Solana?"

## When NOT to Use

- Buying existing tokens — use dex-trading
- LP on existing pools — use lp-farming
- No active meta — don't launch into silence

## The Launchpads

### PumpFun (Most Popular)

Default choice. Biggest audience, most eyeballs. Cost: ~0.02 SOL. Graduates at ~85 SOL to PumpSwap.

```bash
outsmart create-coin --name "Token Name" --symbol "TICKER" --metadata-uri "https://arweave.net/..."
```

All tokens: 6 decimals, 1B supply, mint/freeze authority disabled.

### Jupiter Studio

Built on Meteora DBC. USDC curves, anti-sniping, dev vesting. Graduates to DAMM v2. Presets: Meme ($16k->$69k MC), Indie ($32k->$240k MC with vesting), Custom.

### Raydium LaunchLab

Graduates to Raydium CPMM. Less popular for memes but powers other launchpads (american.fun).

### Meteora DBC

Permissionless bonding curve infrastructure. Jupiter Studio and many AI agent launchpads use it underneath. Graduates to DAMM v2.

## Which Launchpad When

| You want... | Use | Why |
|-------------|-----|-----|
| Max eyeballs, quick meme | PumpFun | Biggest audience |
| USDC curve, anti-snipe, vesting | Jupiter Studio | Built-in protections |
| Autonomous agent launching | PumpFun | Single CLI command |

## Catching the Narrative

The token creation is just a transaction. Knowing what to launch and when is everything.

- **CT/X** — ground zero. 5+ accounts on same theme = meta forming
- **Telegram groups** — stuff leaks here before CT
- **DexScreener trending** — what's pumping right now?
- **News events** — speed matters, first token with the right ticker wins

**The window is phases 1-2 of a meta.** By phase 3 you're too late.

## After Graduation

```bash
# Token graduates to DEX. Create DAMM v2 pool with 99% fee:
outsmart create-pool --dex meteora-damm-v2 --token MINT \
  --base-amount 1000000 --quote-amount 0.5 \
  --max-fee 9900 --min-fee 200 --duration 86400 --periods 100

# As token matures, open DLMM position:
outsmart add-liq --dex meteora-dlmm --pool POOL --sol 0.5 --strategy spot --bins 50
```

Total cost from launch to full LP: ~0.25 SOL.

## Don't Be a Bad Dev

- Don't dump your allocation immediately — everyone sees it on GMGN
- Don't rug the LP — lock or burn it
- Don't launch with mint/freeze authority — instant red flag
- Don't buy most of your supply via alt wallets — GMGN detects bundled buys
- Don't launch into a dead meta
