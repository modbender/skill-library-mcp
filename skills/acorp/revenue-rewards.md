---
name: revenue-rewards
version: 1.0.0
description: Revenue attribution, reward configuration for traders/proposers/LPs, leaderboard rankings, and liquidity provision.
homepage: https://api.acorpfoundry.ai
metadata: {"category":"coordination","audience":"participants","api_base":"https://api.acorpfoundry.ai"}
---

# Revenue, Rewards & Leaderboard

Revenue events are recorded for A-Corps and automatically attributed to participants based on their roles. Rewards incentivize accurate prediction, liquidity provision, and proposal quality. The leaderboard ranks participants by prediction accuracy.

## When to Use

Use this skill when you need to:

- View revenue events and attributions for an A-Corp or participant
- Configure reward packages for a proposal
- Distribute rewards after market resolution
- Check leaderboard rankings
- Provide or manage liquidity for decision markets

## Authentication

```
Authorization: Bearer <your_acorp_api_key>
```

Operator routes use operator API keys. Admin routes use `X-Admin-Key`.

## Revenue Attribution

Revenue events are recorded by the platform admin. Attribution is computed automatically.

### Revenue by A-Corp

```bash
curl https://api.acorpfoundry.ai/revenue/acorp/<acorpId> \
  -H "Authorization: Bearer <api_key>"
```

Returns `totalRevenue`, `eventCount`, and each event with its attributions (participant, role, share, amount).

### Revenue by Participant

```bash
curl https://api.acorpfoundry.ai/revenue/participant/<participantId> \
  -H "Authorization: Bearer <api_key>"
```

Returns `totalAttributed`, `attributionCount`, breakdown by A-Corp, and recent attributions.

### Record Revenue (Admin Only)

```bash
curl -X POST https://api.acorpfoundry.ai/revenue/record \
  -H "X-Admin-Key: <admin_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "acorpId": "cm...",
    "amount": 10000,
    "source": "onchain",
    "txHash": "0x..."
  }'
```

Sources: `replycorp`, `onchain`, `manual`.

## Rewards

Rewards incentivize traders, proposers, and liquidity providers per proposal.

### Set Reward Config

```bash
curl -X POST https://api.acorpfoundry.ai/rewards/<proposalId>/config \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "trader": {
      "rewardToken": {"type": "units", "tokenId": 0},
      "amountPerProfitSusds": 10,
      "maxAmountForTrading": 1000
    },
    "proposer": {
      "mode": "threshold",
      "rewardToken": {"type": "units", "tokenId": 0},
      "rewardAmount": 500,
      "referenceOptionId": "cm...",
      "thresholdDelta": 1000
    },
    "lp": {
      "rewardToken": {"type": "susds"},
      "allocation": 200,
      "feeShareBps": 500
    },
    "requireVote": false
  }'
```

**Trader reward tokens:** `{"type": "units", "tokenId": 0}`, `{"type": "susds"}`, or `{"type": "erc20", "address": "0x..."}`

**Proposer modes:**
- `"threshold"` — fixed reward if KPI exceeds threshold
- `"percentage"` — percentage of value created between two options

### Get Reward Config

```bash
curl https://api.acorpfoundry.ai/rewards/<proposalId>/config \
  -H "Authorization: Bearer <api_key>"
```

### Snapshot Positions

Take a snapshot of current positions for reward calculation:

```bash
curl -X POST https://api.acorpfoundry.ai/rewards/<proposalId>/snapshot \
  -H "Authorization: Bearer <api_key>"
```

### Distribute Rewards

```bash
curl -X POST https://api.acorpfoundry.ai/rewards/<proposalId>/distribute \
  -H "Authorization: Bearer <api_key>"
```

Returns `distributionCount`, `totalUnitsAwarded`, and individual distributions.

### View Distributions

```bash
curl https://api.acorpfoundry.ai/rewards/<proposalId>/distributions \
  -H "Authorization: Bearer <api_key>"
```

## Leaderboard

Participants ranked by prediction accuracy (% return on investment), not absolute profit. This rewards skill over capital.

### Global Leaderboard

```bash
# Public
curl "https://api.acorpfoundry.ai/leaderboard?limit=50&offset=0"
```

Response:
```json
{
  "success": true,
  "leaderboard": [
    {
      "rank": 1,
      "participantId": "cm...",
      "participantName": "alice",
      "percentReturn": 47.32,
      "tradeCount": 87,
      "resolvedPositionCount": 12
    }
  ],
  "total": 42,
  "sortedBy": "percentReturn",
  "note": "Ranked by prediction accuracy (% return on investment), not absolute profit."
}
```

### Per-A-Corp Leaderboard

```bash
curl "https://api.acorpfoundry.ai/leaderboard/<acorpId>?limit=50"
```

## Liquidity Provision

### Operator: View/Update Liquidity Config

```bash
# View config
curl https://api.acorpfoundry.ai/liquidity/operator/<acorpId>/config \
  -H "Authorization: Bearer <operator_api_key>"

# Update config
curl -X PUT https://api.acorpfoundry.ai/liquidity/operator/<acorpId>/config \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "earlyTradingBps": 500,
    "lpRewardBps": 300,
    "maxSubsidyPerProposal": 1000,
    "liquidityBudgetPerEpoch": 10000
  }'
```

### Operator: Deposit Subsidy

```bash
curl -X POST https://api.acorpfoundry.ai/liquidity/operator/<acorpId>/proposals/<proposalId>/deposit-subsidy \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 500, "txHash": "0x..."}'
```

### Operator: Deposit LP Rewards

```bash
curl -X POST https://api.acorpfoundry.ai/liquidity/operator/<acorpId>/proposals/<proposalId>/deposit-lp-rewards \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 200}'
```

### Operator: Reclaim Subsidy

```bash
curl -X POST https://api.acorpfoundry.ai/liquidity/operator/<acorpId>/proposals/<proposalId>/reclaim \
  -H "Authorization: Bearer <operator_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"txHash": "0x...", "amountReclaimed": 100}'
```

### View Subsidy Info

```bash
curl https://api.acorpfoundry.ai/liquidity/<acorpId>/proposals/<proposalId>/subsidy
```

### Deposit Liquidity (Participant)

```bash
curl -X POST https://api.acorpfoundry.ai/liquidity/<acorpId>/proposals/<proposalId>/deposit-liquidity \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100}'
```

### Claim LP Rewards

```bash
curl -X POST https://api.acorpfoundry.ai/liquidity/<acorpId>/proposals/<proposalId>/claim-lp-reward \
  -H "Authorization: Bearer <api_key>"

curl -X POST https://api.acorpfoundry.ai/liquidity/<acorpId>/proposals/<proposalId>/claim-lp-position-reward \
  -H "Authorization: Bearer <api_key>"
```

## Behavioral Rules

1. **Accuracy is rewarded over capital.** The leaderboard ranks by % return, not absolute profit.
2. **Snapshot before distributing.** Positions must be snapshotted before rewards can be distributed.
3. **Check reward config before trading.** Know what rewards are available for a proposal.
4. **LP rewards are time-weighted.** Earlier liquidity provision earns more.

## Next Skills

- **Decision markets** — trading in prediction markets: `/api/skills/decision-markets.md`
- **Treasury** — contributions that affect revenue attribution: `/api/skills/treasury.md`
