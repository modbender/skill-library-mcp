---
name: spend-pulse
description: Proactive spending alerts via Plaid. Track credit card spending against a monthly budget with pace-based alerts.
---

# Spend Pulse

> Proactive spending alerts via Plaid. Track credit card spending against a monthly budget with pace-based alerts.

## Installation

```bash
# Install globally
npm install -g spend-pulse

# Or from source
git clone https://github.com/jbornhorst1524/spend-pulse.git
cd spend-pulse
npm install && npm run build && npm link
```

Verify installation:
```bash
spend-pulse --version
```

## First-Time Setup

Run the interactive setup wizard:

```bash
spend-pulse setup
```

This will:
1. Prompt for Plaid API credentials (get them at https://dashboard.plaid.com/developers/keys)
2. Ask to choose Sandbox (test data) or Development (real bank) mode
3. Set monthly spending budget
4. Open browser for Plaid Link bank authentication
5. Store credentials securely in macOS Keychain

**For Sandbox testing**, use these Plaid test credentials when the bank login appears:
- Username: `user_good`
- Password: `pass_good`

After setup, run initial sync:
```bash
spend-pulse sync
```

## Commands

### `spend-pulse check` — Primary Command

Returns alert decision with full context. **This is the main command to use.**

```yaml
should_alert: true
reasons:
  - 3 new transactions
  - end of month approaching
month: "2026-01"
budget: 8000
spent: 6801.29
remaining: 1198.71
day_of_month: 30
days_in_month: 31
days_remaining: 1
expected_spend: 7200.00
pace: under
pace_delta: -398.71
pace_percent: -6
pace_source: last_month
oneline: "Jan: $6.8k of $8k (85%) | $1.2k left | 1 days | > On track"
new_transactions: 3
new_items:
  - merchant: Whole Foods
    amount: 47.50
    category: Groceries
  - merchant: Amazon
    amount: 125.00
    category: Shopping
```

**Alert triggers** (`should_alert: true` when any apply):
- New transactions since last check
- Over pace (spending faster than expected)
- Remaining budget < $500
- End of month (last 3 days)
- First of month (new month started)

### `spend-pulse sync`

Pull latest transactions from Plaid. Run before `check` for fresh data.

```yaml
synced: 16
new: 3
account: "Amex Gold (...1234)"
total_this_month: 6801.29
```

### `spend-pulse status [--oneline]`

Full spending summary, or quick one-liner:

```bash
spend-pulse status --oneline
# Jan: $6.8k of $8k (85%) | $1.2k left | 1 days | > On track
```

### `spend-pulse recent [--days N] [--count N]`

Recent transactions (default: last 5 days).

### `spend-pulse config [key] [value]`

View or modify settings:
```bash
spend-pulse config                  # show all
spend-pulse config target 8000      # set monthly budget
spend-pulse config timezone America/Chicago
```

### `spend-pulse link [--status] [--remove <id>]`

Manage linked bank accounts:
```bash
spend-pulse link --status    # show linked accounts
spend-pulse link             # add another account
spend-pulse link --remove <item_id>
```

### `spend-pulse chart [-o <path>]`

Generate a cumulative spending chart as a PNG image showing:
- Current month spending (solid blue line with gradient fill, ends with a dot at today)
- Last month spending (dashed gray line, full month)
- Budget target (dashed amber horizontal line)

```bash
spend-pulse chart                    # Writes to ~/.spend-pulse/chart.png
spend-pulse chart -o /tmp/chart.png  # Custom output path
```

Outputs the file path to stdout so you can capture it and attach to messages.

### `spend-pulse check --chart`

Generate a chart alongside the alert check. Adds `chart_path` to the YAML output:

```yaml
should_alert: true
chart_path: /Users/you/.spend-pulse/chart.png
# ... rest of check output
```

## Recommended Workflow

```bash
# 1. Sync latest transactions
spend-pulse sync

# 2. Check if alert needed, generate chart
spend-pulse check --chart
```

**If `should_alert: true`**: Compose a brief, friendly spending update using the data. **Attach the chart image** from `chart_path` — it shows current vs. last month spending at a glance.

**If `should_alert: false`**: Stay quiet unless the user asks about spending.

## Composing Messages

Use the `oneline` field as the core message, then add context. Always attach the chart image when available — it communicates pace visually better than any text can.

**Under pace (positive):**
> "Quick spending pulse: Jan at $6.8k of $8k, $1.2k left with 1 day to go. Under pace by 12% — nice work!"
> [attach chart.png]

**On track:**
> "January update: $5.5k of $8k (69%) with 10 days left. Right on pace. Recent: $125 Amazon, $47 Whole Foods."
> [attach chart.png]

**Over pace (heads up):**
> "Heads up — January's at $7.2k of $8k with 5 days to go. About 10% over pace. The travel charges added up."
> [attach chart.png]

**Over budget:**
> "January budget: $8.5k spent, about $500 over the $8k target. Something to keep in mind for February."
> [attach chart.png]

**Guidelines:**
- Tone: helpful friend, not nagging accountant
- Keep text under 280 characters when possible
- Mention 1-2 notable items from `new_items` if interesting
- Use `reasons` array for context
- Always include the chart image — it's designed to be readable on a phone screen

## Pace Explained

Spend Pulse paces against **last month's actual cumulative spend curve** when available, falling back to a linear budget ramp when no prior month data exists.

- `expected_spend`: Where you were at this point last month (or linear ramp fallback)
- `spent`: Actual spending
- `pace_delta`: Difference (negative = under, positive = over)
- `pace`: `under` | `on_track` | `over`
- `pace_source`: `last_month` (curve-based) or `linear` (ramp fallback)

This means early-month bills (rent, subscriptions) won't trigger false "over pace" alerts if you had similar bills last month.

Example: Day 15, last month you'd spent $4.2k by this point → expected ~$4.2k.

## Upgrading to Real Bank Data

After testing with Sandbox, upgrade to Development mode for real transactions:

```bash
spend-pulse setup --upgrade
```

This clears sandbox data and connects your real bank account.

## Troubleshooting

**"Plaid credentials not found"**: Run `spend-pulse setup` to configure.

**"Access token not found"**: Run `spend-pulse setup` to re-authenticate.

**"No accounts found"**: Check `spend-pulse link --status` and add account if needed.

**Stale data**: Run `spend-pulse sync` to refresh from Plaid.
