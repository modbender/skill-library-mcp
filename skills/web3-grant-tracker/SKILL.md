# Web3 Grant Tracker — Gitcoin, Giveth & DAO Funding Monitor

Track active Web3 grant rounds, deadlines, and funding opportunities across Gitcoin, Giveth, Optimism RPGF, Arbitrum, and other DAO treasuries. Get alerts before rounds close.

## What It Does

- **Live grant round scanning** — checks Gitcoin GG rounds, Giveth, Octant, and more
- **Deadline alerts** — WhatsApp/Telegram warning 48h and 24h before round ends
- **Matching fund calculator** — estimates your potential QF match based on donor count
- **Project eligibility checker** — analyzes your GitHub/project against round requirements
- **Application tracker** — tracks which rounds you've applied to and their status
- **Portfolio dashboard** — shows all active + upcoming rounds with deadlines
- **Round history** — historical data on past rounds and typical funding amounts

## Quick Start

```bash
# Scan all active grant rounds right now
web3-grant-tracker scan

# Check what's closing soon (next 7 days)
web3-grant-tracker urgent

# Add your project for tracking
web3-grant-tracker add-project \
  --name "OpenClaw Infrastructure" \
  --github "https://github.com/yourusername/project" \
  --tags "infrastructure,ai,open-source"

# Check project eligibility for active rounds
web3-grant-tracker check-eligibility --project "OpenClaw Infrastructure"

# Set up deadline alerts
web3-grant-tracker alerts-setup \
  --channel whatsapp \
  --advance-hours 48

# Get matching fund estimate (Quadratic Funding)
web3-grant-tracker estimate-match \
  --project "OpenClaw Infrastructure" \
  --donor-count 50 \
  --round gitcoin-gg24
```

## Commands

| Command | Description |
|---------|-------------|
| `web3-grant-tracker scan` | Scan all active rounds + deadlines |
| `web3-grant-tracker urgent` | Rounds closing in next 7 days |
| `web3-grant-tracker add-project <name>` | Register a project to track |
| `web3-grant-tracker list-projects` | List your tracked projects |
| `web3-grant-tracker check-eligibility` | Check which rounds your project qualifies for |
| `web3-grant-tracker estimate-match` | QF matching fund calculator |
| `web3-grant-tracker apply-guide <round>` | Step-by-step application guide |
| `web3-grant-tracker alerts-setup` | Configure deadline alerts |
| `web3-grant-tracker history` | Past rounds + average payouts |
| `web3-grant-tracker portfolio` | Full dashboard of all applications |

## Supported Platforms

| Platform | Data Available | Application Link |
|----------|---------------|-----------------|
| **Gitcoin Grants** | Rounds, deadlines, QF match | grants.gitcoin.co |
| **Giveth** | Project listings, GIVbacks | giveth.io |
| **Octant** | Epoch funding, allocations | octant.app |
| **Optimism RPGF** | Retroactive grants | app.optimism.io |
| **Arbitrum DAO** | Grant programs | forum.arbitrum.foundation |
| **ENS Ecosystem** | Small grants | discuss.ens.domains |
| **Uniswap Grants** | UGP rounds | uniswapgrants.eth.limo |
| **Nouns Builder** | DAO-specific rounds | nouns.build |

## Example Output

```
╔═══════════════════════════════════════════════════╗
║   WEB3 GRANT TRACKER — 2026-02-25 02:30 UTC       ║
╠═══════════════════════════════════════════════════╣
║ ACTIVE ROUNDS (4 found)                           ║
╠═══════════════════════════════════════════════════╣
║ Gitcoin GG24 — Infrastructure                     ║
║   💰 Pool: ~$250,000 matching                     ║
║   ⏰ Closes: 2026-03-15 (18 days)                 ║
║   ✅ Your project: ELIGIBLE                        ║
╠═══════════════════════════════════════════════════╣
║ Octant Epoch 5                                    ║
║   💰 Pool: ~$800,000 ETH                          ║
║   ⏰ Closes: 2026-03-01 (4 days) ⚠️ URGENT       ║
║   ⚠️ Eligibility: check-eligibility to verify     ║
╠═══════════════════════════════════════════════════╣
║ Giveth GIVbacks Round 42                          ║
║   💰 Rewards: GIV tokens per donation             ║
║   ⏰ Rolling — no deadline                        ║
║   ✅ Your project: ELIGIBLE                        ║
╠═══════════════════════════════════════════════════╣

📊 QF MATCH ESTIMATE (Gitcoin GG24, 50 donors):
   Conservative: $180–450
   Optimistic:   $600–1,200
   (Based on 50 unique donors × avg $5 contribution)

💡 Recommendation: Apply to GG24 Infrastructure round
   → run: web3-grant-tracker apply-guide gitcoin-gg24
```

## QF Matching Calculator

Quadratic Funding rewards projects with many small donors over few large ones:

```bash
# See how adding more donors affects your match
web3-grant-tracker estimate-match \
  --project "my-project" \
  --round gitcoin-gg24 \
  --donor-count 100 \
  --avg-donation 10

# Output:
# sqrt(10) * 100 donors = 316 QF units
# Estimated match: $1,200–2,800 (depends on pool)
# Getting to 200 donors would 2x your match!
```

## Application Guide Example

```bash
web3-grant-tracker apply-guide gitcoin-gg24

# Output:
# GITCOIN GG24 — INFRASTRUCTURE ROUND APPLICATION GUIDE
# ═══════════════════════════════════════════════════════
# Step 1: Create project on Builder (builder.gitcoin.co)
#   → Connect GitHub + wallet
#   → Fill: name, description, links, banner image
# Step 2: Apply to round on Explorer (explorer.gitcoin.co)
#   → Select: Infrastructure/Tooling round
#   → Write impact statement (see templates below)
# Step 3: Community amplification
#   → Tweet with #GG24 #Gitcoin hashtags
#   → Post in Farcaster /gitcoin channel
#   → Share in relevant Discord servers
# Step 4: Donor drive
#   → Need 1 min donation ($1+) from unique wallets
#   → Each unique donor increases QF match
# ...
```

## Deadline Alert Example

```
⏰ GRANT DEADLINE ALERT — 24h remaining

Round: Gitcoin GG24 — Infrastructure
Closes: 2026-03-15 20:00 UTC (in 23h 42m)
Your project: OpenClaw Infrastructure
Status: Applied ✅

Action items:
• Share project link for last-day donors
• Post reminder on social media
• Check you haven't hit any submission limits

Project link: explorer.gitcoin.co/projects/openclaw-infra
```

## Data Storage

All data stored locally at `~/.openclaw/workspace/web3-grant-tracker/`. No telemetry. Grant round data refreshed every 6 hours via public APIs and web fetches.

## Configuration

```json
{
  "alert_channel": "whatsapp",
  "alert_advance_hours": [48, 24, 6],
  "wallet_address": "0xYourAddress",
  "default_tags": ["infrastructure", "open-source", "ai"],
  "auto_scan_interval_hours": 6
}
```

## Requirements

- OpenClaw 1.0+
- Python 3.8+
- Optional: Ethereum wallet address (for on-chain verification)

## Use Cases

- **Builders** — Never miss a grant round again
- **DAOs** — Track ecosystem funding opportunities
- **Researchers** — Monitor Web3 public goods funding landscape
- **Investors** — Identify well-funded projects early (donor velocity signal)

## Source & Issues

- **Source:** https://github.com/mariusfit/web3-grant-tracker
- **Issues:** https://github.com/mariusfit/web3-grant-tracker/issues
- **Author:** [@mariusfit](https://github.com/mariusfit)
