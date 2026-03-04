---
name: polymarket-monitor
description: Monitor Polymarket prediction markets and alert when odds cross a threshold. Use when a user wants to track any Polymarket market probability, set up recurring price checks, or get notified when a market's Yes/No probability exceeds a specific percentage. Covers searching for markets by topic, fetching current odds, and setting up cron-based alerts via Slack or other channels.
---

# Polymarket Monitor

Set up ongoing monitoring for any Polymarket prediction market with threshold-based alerts.

## Workflow

### 1. Find the market(s)

Search the Gamma API for active markets matching the user's topic:

```bash
curl "https://gamma-api.polymarket.com/events?search=<topic>&limit=10&active=true"
```

Parse the response to find relevant markets. For each, note:
- `conditionId` — needed to fetch prices
- `question` — market title
- `outcomePrices` — current Yes/No probabilities (JSON string)

See `references/api.md` for full API details.

### 2. Check current odds

Use the bundled script to fetch current prices for one or more markets:

```bash
python3 scripts/check_markets.py <conditionId1> [conditionId2 ...]
```

Output: JSON with `question`, `yes_prob` (0–1 float), and `url` per market.

### 3. Report current state

Show the user the markets found and their current probabilities before setting up monitoring.

### 4. Set up the cron alert

Create a cron job that runs every N minutes (default: 30) with `sessionTarget: "isolated"` and `payload.kind: "agentTurn"`. The agent task should:

1. Fetch each market via `web_fetch` using the Gamma API (conditionId endpoint)
2. Parse `outcomePrices[0]` as the Yes probability
3. If any market exceeds the threshold: send a Slack DM alert via the `message` tool (channel=slack, target=<user_id>)
4. If none exceed threshold: do nothing (no output)

Use `delivery.mode: "none"` to suppress default cron delivery — the agent handles its own alerting.

**Template cron task message:**

```
Check these Polymarket markets. For each, fetch:
  https://clob.polymarket.com/markets/<conditionId>
Parse tokens array: find outcome=="Yes" and use its price as probability (0–1).
If any exceeds <threshold> (e.g. 0.70):
  Send Slack DM to <user_slack_id> with: market question, current %, and Polymarket URL.
If none exceed threshold, do nothing.

Markets:
- <question>: https://clob.polymarket.com/markets/<conditionId> | https://polymarket.com/event/<slug>
```

### 5. Confirm setup

Tell the user:
- Which markets are being monitored
- Current odds for each
- Alert threshold and check frequency
- How to cancel (cron job ID + `cron remove <id>`)

## Notes

- Polymarket has no "today" daily markets — use the nearest deadline market for short-term signals
- `outcomePrices` is always `["yes", "no"]` — first value is Yes
- Closed markets return prices of 0 or 1; skip them
- No API key needed
