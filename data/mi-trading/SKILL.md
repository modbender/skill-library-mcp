---
name: clawdex
description: Trade tokens on Solana using the ClawDex CLI. Use when the user asks to swap tokens, check balances, get quotes, or manage a Solana trading wallet.
tools: Bash, Read
metadata:
  tags: solana, trading, defi, jupiter, swap, crypto
---

# ClawDex — Solana DEX Trading Skill

Trade any Solana token through Jupiter aggregator with simulation, safety guardrails, and full JSON output.

## Prerequisites

Before using this skill, ensure ClawDex is installed and configured:

```bash
which clawdex || npm install -g clawdex@latest
```

If not configured yet, run onboarding:
```bash
clawdex status --json
```
If status fails, set up with:
```bash
clawdex onboarding \
  --jupiter-api-key "$JUPITER_API_KEY" \
  --rpc "${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}" \
  --wallet ~/.config/solana/id.json \
  --json
```

## Commands

### Check wallet balances

```bash
clawdex balances --json
```

Returns an array of `{ token, symbol, mint, balance, decimals }` objects. Zero-balance accounts are included in JSON output.

### Get a quote (no execution)

```bash
clawdex quote --in SOL --out USDC --amount 0.01 --json
```

Lightweight price check — no simulation, no wallet needed.

### Simulate a swap (dry run)

```bash
clawdex swap --in SOL --out USDC --amount 0.01 --simulate-only --json
```

Runs full simulation on-chain without broadcasting. Does not require `--yes`. Use this to preview the output amount and route before committing.

### Execute a swap

```bash
clawdex swap --in SOL --out USDC --amount 0.01 --yes --json
```

**`--yes` is required** for non-interactive execution. Without it, ClawDex exits with code 1.

### Health check

```bash
clawdex status --json
```

Verify RPC connectivity, wallet validity, and config state.

## Trading Workflow

Always follow this sequence:

1. **Health check** — `clawdex status --json` — abort if `rpc.healthy` is false
2. **Check balances** — `clawdex balances --json` — verify sufficient funds
3. **Simulate** — `clawdex swap --simulate-only --json` — preview the trade
4. **Execute** — `clawdex swap --yes --json` — only if simulation looks good
5. **Verify** — `clawdex balances --json` — confirm balances updated (may need 5s delay on public RPC)

## Token Specification

Tokens can be passed by symbol or mint address:
- **By symbol**: `SOL`, `USDC`, `USDT`
- **By mint**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`

## Exit Codes

| Code | Meaning | Agent action |
|------|---------|-------------|
| 0 | Success | Continue |
| 1 | General error | Check message |
| 2 | Config error | Run onboarding |
| 3 | Safety violation | Reduce amount or adjust limits |
| 4 | Simulation failed | Try different pair/amount |
| 5 | Send failed | Retry with backoff |

## Safety

Set guardrails to prevent runaway trades:
```bash
clawdex safety set max_slippage_bps=300 max_trade_sol=1 max_price_impact_bps=100
```

When a guardrail triggers, the JSON response includes a `violations` array describing what failed.

## Important Rules

- **Always use `--json`** for machine-parseable output
- **Always use `--yes`** for real swaps (not needed for `--simulate-only`)
- **Never skip simulation** unless you have a good reason — use `--simulate-only` first
- **Parse `balance` as a string**, not a number — it preserves full decimal precision
- **Check exit codes** — non-zero means the trade did not succeed
- **Wait before verifying** — RPC balance reads can lag a few seconds after a swap
