---
name: whalecli
description: >
  Agent-native whale wallet tracker for ETH and BTC chains. Track large crypto wallet movements,
  score whale activity, detect accumulation/distribution patterns, and stream real-time alerts.
  Integrates with FearHarvester and Simmer prediction markets for closed-loop signal→bet workflows.
  Use when: user asks about whale activity, on-chain signals, large wallet movements, smart money flows,
  or when pre-validating crypto trades/bets with on-chain data.
---

# WhaleWatch CLI — Agent Skill

Track crypto whale movements. Close the loop from on-chain signal → agent reasoning → prediction market bet.

## Install

```bash
uv pip install whalecli
```

## Quick Start

```bash
# Initialize config (creates ~/.config/whalecli/config.toml)
whalecli config init

# Set API key (free tier: 5 req/sec)
whalecli config set api.etherscan_api_key YOUR_KEY

# Add a whale wallet
whalecli wallet add 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --label "vitalik.eth" --chain ETH

# Scan all wallets (last 24h)
whalecli scan --format json

# Stream real-time alerts (JSONL, one event per line)
whalecli stream --chain ETH --interval 60
```

## When to Use

**Trigger phrases:**
- "What are the whales doing?"
- "Check whale activity on ETH/BTC"
- "Are whales accumulating or distributing?"
- "Any large wallet movements?"
- "What's the on-chain signal?"
- "Run a whale scan"

**Automatic triggers (no user prompt needed):**
- Every 60 minutes during market-active hours (via heartbeat)
- Before placing a Simmer/Polymarket bet (pre-bet whale sanity check)
- When fear/greed index crosses a threshold (corroboration)

## CLI Commands

### `whalecli scan` — One-shot whale analysis

```bash
whalecli scan --chain ETH --hours 4 --threshold 70 --format json
```

**Output (JSON):**
```json
{
  "scan_id": "scan_20260222_103015_a1b2",
  "chain": "ETH",
  "window_hours": 4,
  "wallets": [
    {
      "address": "0xd8dA...",
      "label": "vitalik.eth",
      "score": 82,
      "direction": "accumulating",
      "score_breakdown": {
        "net_flow": 35,
        "velocity": 20,
        "correlation": 15,
        "exchange_flow": 12
      },
      "net_flow_usd": 15000000,
      "tx_count": 12
    }
  ],
  "summary": {
    "total_wallets": 5,
    "accumulating": 3,
    "distributing": 1,
    "neutral": 1,
    "avg_score": 65
  },
  "alerts_triggered": 2
}
```

### `whalecli stream` — Real-time JSONL streaming

```bash
whalecli stream --chain ETH --interval 60 --threshold 70
```

Events (one JSON per line):
- `stream_start` — stream initialized
- `whale_alert` — score exceeded threshold
- `whale_activity` — activity detected below threshold
- `heartbeat` — periodic health check
- `stream_end` — clean shutdown

### `whalecli wallet` — Manage tracked wallets

```bash
whalecli wallet add 0x... --label "whale1" --chain ETH
whalecli wallet list --format json
whalecli wallet remove 0x...
whalecli wallet import wallets.csv
```

### `whalecli alert` — Configure alert rules

```bash
whalecli alert set --score 75 --webhook https://example.com/hook
whalecli alert set --threshold 1000000 --window 1h
whalecli alert list --format json
```

### `whalecli report` — Historical analysis

```bash
whalecli report --wallet 0x... --days 30 --format json
```

### `whalecli config` — Configuration management

```bash
whalecli config init
whalecli config set api.etherscan_api_key YOUR_KEY
whalecli config show
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (alerts found or scan complete) |
| 1 | No alerts (scan ran but nothing above threshold) |
| 2 | API error (rate limit, invalid key) |
| 3 | Network error (timeout, connection refused) |
| 4 | Data error (invalid address, wallet not found) |

## Scoring Algorithm

4-dimension whale scoring (0–100 points):

- **Net Flow (0–40):** USD net flow with log10 scaling, wallet age weighting
- **Velocity (0–25):** Current activity vs 30-day baseline (log2 ratio)
- **Correlation (0–20):** Peer wallet direction agreement (min 2 peers)
- **Exchange Flow (0–15):** CEX address registry lookup + direction match

**Interpretation:**
- 80–100: Strong whale signal (high confidence)
- 60–79: Moderate activity (worth monitoring)
- 40–59: Low activity (noise)
- 0–39: Minimal (ignore)

## Agent Integration Pattern

```python
import subprocess, json

def whale_scan(chain="ETH", hours=4, threshold=70):
    """Run whale scan and return parsed results."""
    result = subprocess.run(
        ["whalecli", "scan", "--chain", chain,
         "--hours", str(hours), "--threshold", str(threshold),
         "--format", "json"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 2:
        raise RuntimeError(f"API error: {result.stderr}")
    if not result.stdout.strip():
        return {"wallets": [], "alerts_triggered": 0}
    return json.loads(result.stdout)

# Example: pre-bet whale check
scan = whale_scan(chain="ETH", hours=4)
if scan["summary"]["accumulating"] > scan["summary"]["distributing"]:
    print("Whales accumulating — bullish signal")
```

## FearHarvester Integration

The closed loop: Fear & Greed → Whale Signal → Simmer Bet

```python
# 1. Get F&G value
fg_value = get_fear_greed_index()  # e.g., 8 (Extreme Fear)

# 2. Check whale confirmation
scan = whale_scan(chain="ETH", hours=4)
whales_accumulating = scan["summary"]["accumulating"] > scan["summary"]["distributing"]

# 3. If fear + whales accumulating → strong contrarian signal
if fg_value <= 20 and whales_accumulating:
    # Place bet on recovery market
    place_simmer_bet(market="btc_recovery", side="yes", amount=15)
```

## Supported Chains

- **ETH** — Etherscan API (free tier: 5 req/sec)
- **BTC** — Mempool.space (primary) + Blockchain.info (fallback)
- **HL** — Hyperliquid perpetual fills and positions

## Links

- **PyPI:** https://pypi.org/project/whalecli/
- **GitHub:** https://github.com/clawinfra/whalecli
- **Issues:** https://github.com/clawinfra/whalecli/issues
