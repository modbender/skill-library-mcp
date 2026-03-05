# Bot Detection Scoring — Reference

## Score Weights (100 total)

| Signal | Points | Description |
|--------|--------|-------------|
| wAPE Ratio | 30 | % of NFT buys paid with wAPE instead of native APE. Bots use wAPE for programmatic approvals. |
| Fast Flip | 25 | Buy→sell within 24 hours. Bots flip quickly for profit. |
| Fast List | 20 | Buy→list within 30 minutes. Bots auto-list immediately after purchase. |
| Aggressive Pricing | 15 | Listings significantly below floor price (>2% under). Bots undercut to sell fast. |
| Cross-Collection | 10 | Activity spread across many collections (>10 = max score). Bots spray across collections. |

## Verdicts

| Score Range | Verdict |
|-------------|---------|
| 0-19 | `human` — Normal wallet activity |
| 20-39 | `probably_human` — Some automated patterns but likely human |
| 40-59 | `suspicious` — Mixed signals, needs manual review |
| 60-74 | `likely_bot` — Strong bot patterns detected |
| 75-100 | `definite_bot` — Overwhelming bot indicators |

## Minimum Data

Requires at least 3 NFT buys to generate a score. Below that threshold, returns `insufficient_data`.

## wAPE Detection

wAPE contract on ApeChain: `0x48b62137edfa95a428d35c09e44256a739f6b557`

Bots prefer wAPE because:
- ERC-20 approve() allows programmatic spending
- No need for native APE gas estimation per-tx
- Batch operations are easier with token approvals
