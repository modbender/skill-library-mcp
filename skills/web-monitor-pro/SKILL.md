---
name: web-monitor
version: 3.5.0
description: "Monitor web pages for changes, price drops, stock availability, and custom conditions. Use when a user asks to watch/track/monitor a URL, get notified about price changes, check if something is back in stock, or track any website for updates. Also handles listing, removing, checking, and reporting on existing monitors. v3 adds change summaries, visual diffs, price comparison, templates, JS rendering, and webhooks."
metadata:
  {
    "openclaw":
      {
        "emoji": "👁️",
        "requires": { "bins": ["python3", "curl"] },
      },
  }
---

# Web Monitor Pro

Watch any web page. Know when it changes.

## Quick Start

```bash
python3 scripts/monitor.py quickstart                        # shows suggestions + engine status
python3 scripts/monitor.py watch "https://example.com/product"
python3 scripts/monitor.py check
```

### First Run

Use `quickstart` on first run. It:
1. Creates the data directory
2. Checks which fetch engines are available (curl, cloudscraper, playwright)
3. Returns suggestions for popular monitoring scenarios (price drops, restocks, page changes, sales)
4. Lists available templates
5. Shows tips for missing engines

The agent can use this info to ask the user what they want to monitor and set it up for them.

## What It Does

- Monitors web pages for content changes, price drops, and restocks
- Smart change summaries ("Price dropped from $389 to $331, 15% off")
- Visual side-by-side diffs showing exactly what changed
- Price history tracking with trends and sparklines
- Price comparison across multiple stores
- Templates for common setups (price drop, restock, sale)
- JS rendering via Playwright for dynamic sites
- Webhooks to Slack, Discord, or any endpoint
- Groups, notes, snapshots, exports
- No API keys. Data in `~/.web-monitor/`. Uses `curl` by default.

## Smart Watch

The easiest way to start. Point it at a URL and it figures out the rest.

```bash
python3 scripts/monitor.py watch "https://example.com/product"
```

It detects whether it's a product page (sets up price monitoring), a stock page (watches availability), or a regular page (tracks content). No flags needed.

Add options if you want more control:

```bash
python3 scripts/monitor.py watch "https://example.com" --group wishlist
python3 scripts/monitor.py watch "https://example.com" --browser --webhook "https://hooks.slack.com/..."
```

## Adding Monitors

When you want full control, use `add`:

```bash
python3 scripts/monitor.py add "https://example.com/product" \
  --label "Cool Gadget" \
  --condition "price below 500" \
  --interval 360 \
  --group "wishlist" \
  --priority high \
  --target 3000 \
  --browser \
  --webhook "https://hooks.slack.com/..."
```

**All options** (work with both `add` and `watch`):

- `--label/-l` name for the monitor
- `--selector/-s` CSS selector to focus on (`#price`, `.stock-status`)
- `--condition/-c` when to alert (see Condition Syntax below)
- `--interval/-i` check interval in minutes (default: 360)
- `--group/-g` category name ("wishlist", "work")
- `--priority/-p` high, medium, or low (default: medium)
- `--target/-t` price target number
- `--browser/-b` use Playwright for JS-rendered pages
- `--webhook/-w` webhook URL, repeatable for multiple endpoints

## Checking Monitors

```bash
python3 scripts/monitor.py check                # check all
python3 scripts/monitor.py check --id 3          # check one
python3 scripts/monitor.py check --verbose       # include content preview
```

Returns status (changed/unchanged), condition info, price data, and a human-readable change summary. Examples of what summaries look like:

- "Price dropped from $389 to $331 (15% off). Lowest price in 30 days."
- "Back in stock! Was out of stock for 3 days."
- "New content: 'Breaking news: AI model achieves...'"

When changes are detected, an HTML diff is auto-generated. The path appears in the `diff_path` field.

## Dashboard

Everything at a glance.

```bash
python3 scripts/monitor.py dashboard
python3 scripts/monitor.py dashboard --whatsapp
```

Shows status icons, last check time, days monitored, current prices, target progress, and browser/webhook config. Groups monitors by category.

## Price Trends

```bash
python3 scripts/monitor.py trend 3
python3 scripts/monitor.py trend 3 --days 30
```

Shows direction (rising/dropping/stable), min/max/avg with dates, target progress, and a sparkline.

## Price Comparison

Compare prices across stores in a group:

```bash
python3 scripts/monitor.py compare mygroup
python3 scripts/monitor.py compare --all
```

Shows cheapest to most expensive, price history, and the best deal as a percentage below average.

Add a competitor to an existing monitor:

```bash
python3 scripts/monitor.py add-competitor 3 "https://competitor.com/same-product"
```

Creates a new monitor in the same group with the same condition.

## Templates

Pre-built setups for common patterns. Skip the manual config.

```bash
python3 scripts/monitor.py template list
python3 scripts/monitor.py template use price-drop "https://example.com/product"
python3 scripts/monitor.py template use restock "https://example.com/product"
python3 scripts/monitor.py template use sale "https://example.com/deals"
```

Available templates:

- `price-drop` watches for price decreases, snapshots current price as baseline
- `restock` looks for "in stock", "available", "add to cart"
- `content-update` tracks page changes with smart diff
- `sale` watches for "sale", "discount", "% off"
- `new-release` watches for new items or versions

Each one pre-configures the condition, interval, and priority.

## Managing Monitors

```bash
python3 scripts/monitor.py list                    # all monitors
python3 scripts/monitor.py list --group wishlist   # filter by group
python3 scripts/monitor.py pause 3                 # skip during checks
python3 scripts/monitor.py resume 3                # re-enable
python3 scripts/monitor.py remove 3                # delete
```

## Notes and Snapshots

Attach notes to any monitor:

```bash
python3 scripts/monitor.py note 3 "waiting for Black Friday"
python3 scripts/monitor.py notes 3
```

Take a manual snapshot:

```bash
python3 scripts/monitor.py snapshot 3
python3 scripts/monitor.py snapshot 3 --note "price before sale"
```

View history:

```bash
python3 scripts/monitor.py history 3
python3 scripts/monitor.py history 3 --limit 10
```

## Visual Diffs

Side-by-side HTML comparison. Old on the left, new on the right. Green for additions, red for removals, yellow for changes.

```bash
python3 scripts/monitor.py diff 3
python3 scripts/monitor.py screenshot 3
```

`diff` generates the comparison and opens it in your browser. `screenshot` saves the current content for future diffing.

## Reports

Weekly summary, formatted for WhatsApp:

```bash
python3 scripts/monitor.py report
```

## Groups

```bash
python3 scripts/monitor.py groups
```

Lists all groups with monitor counts.

## Engines and Cloudflare Support

The monitor uses a fetch engine to grab page content. By default (`--engine auto`), it tries engines in order until one works:

1. **curl** -- fast, no dependencies, works on most sites
2. **cloudscraper** -- handles Cloudflare JS challenges without a full browser
3. **playwright** -- full headless browser for JS-heavy SPAs

Check what's available on your system:

```bash
python3 scripts/monitor.py engines
```

Force a specific engine:

```bash
python3 scripts/monitor.py watch "https://example.com" --engine cloudscraper
python3 scripts/monitor.py add "https://example.com" --engine browser
```

Install cloudscraper (recommended for Cloudflare-protected e-commerce sites):

```bash
pip3 install cloudscraper
```

The engine preference is saved per monitor. You can mix engines across monitors.

## JS Rendering

Sites like Amazon, Best Buy, and most SPAs load content with JavaScript. Default `curl` fetching won't see it. Add `--browser` to use Playwright's headless Chromium:

```bash
python3 scripts/monitor.py watch "https://amazon.com/dp/B0EXAMPLE" --browser
```

If Playwright isn't installed, it falls back to `curl` and warns you. Install with:

```bash
pip3 install playwright && python3 -m playwright install chromium
```

## Webhooks

Fire a JSON POST when conditions are met or content changes:

```bash
python3 scripts/monitor.py add "https://example.com" --webhook "https://hooks.slack.com/services/..."
```

Use `--webhook` multiple times for multiple endpoints. The payload includes monitor_id, label, url, event details (status, condition_met, change_summary, current_price), and timestamp.

Webhooks fire during `check` whenever something triggers.

## Export and Import

```bash
python3 scripts/monitor.py export > monitors.json
python3 scripts/monitor.py import monitors.json
```

Import skips duplicates by URL.

## GUI Console

```bash
python3 scripts/monitor.py gui
```

Opens `~/.web-monitor/console.html` in your browser. Single self-contained HTML file. Shows all monitors, price trends, alert history, groups, and templates. Dark/light mode, filtering, sorting, sparklines. No external dependencies.

Add `--no-open` to generate without launching.

## Condition Syntax

- `price below 500` or `price < 500` alerts when price drops below threshold
- `price above 1000` or `price > 1000` alerts when price exceeds threshold
- `contains 'in stock'` alerts when text appears on page
- `not contains 'out of stock'` alerts when text disappears

## Priority Levels

- **high** fires an immediate alert
- **medium** is the default
- **low** gets batched into digests

## Automation with Cron

Set up a cron job to check monitors regularly:

```
Task: Check all web monitors. Run: python3 <skill_dir>/scripts/monitor.py check
Report any monitors where status is "changed" or "condition_met" is true.
If nothing changed, stay silent.
```

Recommended schedule: every 6 hours (`0 */6 * * *`). For weekly reports, run `report` on Mondays.

## Feedback

```bash
python3 scripts/monitor.py feedback "your message"
python3 scripts/monitor.py feedback --bug "something broke"
python3 scripts/monitor.py feedback --idea "wouldn't it be cool if..."
python3 scripts/monitor.py debug
```

## Tips

- `watch` is almost always the right starting point. Use `add` only when you need specific conditions.
- `--selector` reduces noise. If you only care about the price, point it at `#price` instead of the whole page.
- Group related monitors, then use `compare` to find the best deal across stores.
- Up to 50 snapshots per monitor are kept. Content is capped at 10KB per snapshot.
- Price targets show progress in both `dashboard` and `check` output.
- `snapshot --note` before a sale event gives you a clean baseline to diff against.
- For JS-heavy sites, `--browser` is not optional. It's required.
- Combine webhooks with Slack or Discord for real-time alerts without polling.
