# TrustLayer Sybil Scanner

ERC-8004 feedback forensics skill for OpenClaw agents.

Most reputation systems show you the rating. This one tells you if the rating is real.

## What it does

Before your agent pays another agent, this skill checks:
- **Sybil risk**: Are the reviews from real agents or fake wallet clusters?
- **Reviewer quality**: Is a 5-star rating from trusted agents or throwaway accounts?
- **Cross-chain laundering**: Does the agent have different reputations on different chains?
- **Temporal anomalies**: Sudden review bursts, rating manipulation patterns
- **Spam filtering**: 1,298+ spam feedbacks detected and excluded from scoring

Covers 80,749 agents across Base, Ethereum, BSC, Polygon, and Monad.

## Install

Paste this repo URL into your OpenClaw chat:

```
https://github.com/goatgaucho/trustlayer-sybil-scanner
```

Or manually copy `SKILL.md` to your OpenClaw skills directory.

## Usage

Ask your agent:
- "Check if agent base:1378 is legit"
- "Scan base:5000 for Sybil risk before I pay them"
- "Are the reviews for ethereum:42 real?"
- "Show me the most trusted agents on Base"

## API

No API key needed (beta). All endpoints at `https://api.thetrustlayer.xyz`

| Endpoint | What it does |
|----------|-------------|
| `/trust/base:1378` | Full Sybil scan + trust score |
| `/agent/base:1378` | Basic agent info |
| `/leaderboard?chain=base` | Top agents (Sybil-filtered) |
| `/stats` | Network-wide statistics |

Visual reports: `https://thetrustlayer.xyz/agent/base:1378`

## Why this exists

ERC-8004 gives agents on-chain ratings. But a 4.5-star agent with reviews from a Sybil ring is not a 4.5-star agent. The spec authors anticipated "specialized reputation aggregators" would provide advanced scoring intelligence. That's what this is.

299 Sybil flags. 383 cross-chain identity groups. 6 detection methods. Daily updates.

## Links

- [API Docs](https://thetrustlayer.xyz/docs)
- [Explorer](https://thetrustlayer.xyz)
- [ERC-8004 Spec](https://eips.ethereum.org/EIPS/eip-8004)

Built by [@GoatGaucho](https://x.com/GoatGaucho)
