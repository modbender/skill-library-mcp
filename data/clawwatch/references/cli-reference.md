# ClawWatch CLI Reference

## Global Options

| Flag | Description |
|------|-------------|
| `--version`, `-v` | Show version |
| `--help` | Show help |

---

## `clawwatch add <SYMBOLS...>`

Add one or more assets to the watchlist. Auto-detects crypto vs stock.

| Option | Description |
|--------|-------------|
| `--tag`, `-t` | Tags to apply (repeatable) |
| `--note`, `-n` | Note to attach |

**Examples:**
```bash
clawwatch add BTC ETH NVDA SAP.DE
clawwatch add BTC --tag portfolio --note "Bought at $92k"
clawwatch add AAPL MSFT --tag tech --tag us-stocks
```

---

## `clawwatch remove <SYMBOLS...>`

Remove one or more assets from the watchlist. Also removes associated alerts.

**Examples:**
```bash
clawwatch remove TSLA
clawwatch remove BTC ETH
```

---

## `clawwatch list`

Show all watchlist assets (without fetching prices).

| Option | Description |
|--------|-------------|
| `--tag`, `-t` | Filter by tag |
| `--type` | Filter by type: `crypto` or `stock` |
| `--json` | Output as JSON |

**Examples:**
```bash
clawwatch list
clawwatch list --type crypto
clawwatch list --tag portfolio --json
```

---

## `clawwatch check [SYMBOLS...]`

Fetch latest prices for watchlist assets.

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON (for agent parsing) |

**Examples:**
```bash
clawwatch check                    # All assets
clawwatch check BTC NVDA           # Specific assets
clawwatch check --json             # JSON output for agent
```

---

## `clawwatch feargreed`

Show the Crypto Fear & Greed Index.

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

---

## `clawwatch alert add <SYMBOL> <CONDITION> <VALUE>`

Set a price alert.

| Condition | Description | Example |
|-----------|-------------|---------|
| `above` | Trigger when price goes above value | `alert add BTC above 100000` |
| `below` | Trigger when price drops below value | `alert add ETH below 2000` |
| `change` | Trigger on ±X% 24h change | `alert add SOL change 5` |

---

## `clawwatch alert list`

Show all alerts (active and triggered).

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

---

## `clawwatch alert remove <ALERT_ID>`

Remove a specific alert by its ID.

---

## `clawwatch alert check`

Check all active alerts against current prices.

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |

**Exit codes:** 0 = no alerts triggered, 1 = alerts triggered.

---

## `clawwatch export`

Export watchlist data.

| Option | Description |
|--------|-------------|
| `--format`, `-f` | Export format: `json` (default) or `csv` |

---

## `clawwatch config`

Set or show configuration.

| Option | Description |
|--------|-------------|
| `--coincap-key` | Set CoinCap API key (optional) |
| `--finnhub-key` | Set Finnhub API key |
| `--currency` | Set default currency (`usd`/`eur`) |
| `--show` | Display current config |

---

## `clawwatch update-cache`

Force refresh the CoinPaprika coin list cache.
