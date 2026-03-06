---
name: base-alpha-scanner
description: "Real-time Base chain alpha intelligence for ZHAO (CryptoZhaoX). Use when scanning Base memecoins for second-wave setups or early gem launches; checking GMGN smart money flows; analyzing holder distribution for a Base token; scanning Clanker or Bankr.fun for high-quality narrative token deployments; monitoring VIRTUAL Protocol AI agent launches; running the AI narrative scanner on Base; generating trade alerts on Base memecoins or mainstream assets (BTC/ETH/UNI); any on-chain analysis task on Base chain."
---

# Base Alpha Scanner

ZHAO's on-chain intelligence toolkit for Base chain. Data-first, no hype. Alert only on high-conviction setups.

## Scripts

### scan_base.py — Core on-chain scanner
```
python3 skills/base-alpha-scanner/scripts/scan_base.py --mode <mode> [addr]
```
Modes:
- `trending` — Top Base tokens ranked by conviction score (1h)
- `new` — Early launch scanner: 0–45min + 45min–3h windows
- `token <addr>` — Deep dive on specific token (all timeframes)
- `holders <addr>` — Holder distribution + concentration check
- `gmgn <addr>` — GMGN smart money data (may need browser fallback)

### scan_narrative.py — Narrative & platform scanner
```
python3 skills/base-alpha-scanner/scripts/scan_narrative.py --mode <mode>
```
Modes:
- `clanker` — Latest Clanker token deployments on Base
- `bankr` — Bankr.fun trending tokens (Farcaster-native)
- `virtual` — VIRTUAL Protocol AI agent ecosystem
- `ai` — Broad AI narrative scan across Base

## Workflow

### Standard market scan (run on demand or every 1–2h):
1. `scan_base.py --mode trending` → identify what's moving
2. For anything score ≥ 60: `scan_base.py --mode token <addr>` → deep dive
3. If AI narrative or Farcaster signals: `scan_narrative.py --mode ai` + `clanker`
4. Apply alert rules → ping ZHAO only if threshold met

### Early launch scan (continuous background):
1. `scan_base.py --mode new` → check 0–45min window
2. Score ≥ 60 + clean signals → immediate check with `token` mode
3. Cross-reference with `scan_narrative.py --mode clanker` for Farcaster origin
4. If all checks pass → early gem ping

### Holder distribution check:
1. `scan_base.py --mode holders <addr>`
2. Flag if top-5 > 40% supply or any single wallet > 15%
3. Cross with DexScreener buy/sell maker count to confirm real distribution

## Alert Rules

Read `references/alert-rules.md` for full ruleset. Summary:
- **Immediate ping**: Tier 1 only (vol spike + narrative + clean chart + liq > $100K)
- **Second-wave alert**: 45min–3h old, sustained vol + holder growth, score ≥ 65
- **Early gem**: <45min, score ≥ 60, clean team, real momentum. Max 2–3/day
- **Mainstream (BTC/ETH/UNI)**: Key level breaks, on-chain flows, funding extremes

## API Reference

See `references/api-endpoints.md` for all endpoints, field names, and data source details.

Key addresses:
- VIRTUAL token (Base): `0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b`
- cbBTC (Base): `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf`

## Conviction Score (0–100)

Built into `scan_base.py`. Score ≥ 65 = alert candidate. Score < 50 = ignore.
Factors: 1h volume, liquidity, buy pressure ratio, age (45min–3h = peak), momentum, mcap.

## GMGN Notes

GMGN often blocks direct API access. Fallback options:
1. Use `browser` tool to navigate `https://gmgn.ai/base/token/<addr>`
2. Take screenshot for ZHAO if needed
3. Check wallet history at `https://gmgn.ai/base/address/<wallet>`

## Bankr Notes

No clean public API. Bankr alpha comes from Warpcast:
- Channel: `https://warpcast.com/~/channel/bankr`
- Use `web_search` for recent Bankr mentions + `web_fetch` on Warpcast casts
- High signal: power users (>5K followers) buying via Bankr frame in <30min of launch
