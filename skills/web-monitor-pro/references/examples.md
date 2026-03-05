# Web Monitor Examples

## Price tracking

```bash
# Track a Takealot product
python3 scripts/monitor.py add "https://www.takealot.com/some-product/PLID12345" \
  --label "PS5 Controller" --condition "price below 1200"

# Track Amazon price
python3 scripts/monitor.py add "https://www.amazon.co.za/dp/B09V3KXJPB" \
  --label "Kindle Paperwhite" --condition "price below 3000"
```

## Stock availability

```bash
# Alert when something comes back in stock
python3 scripts/monitor.py add "https://store.example.com/sold-out-item" \
  --label "Limited Edition Widget" --condition "not contains 'out of stock'"

# Check if tickets are available
python3 scripts/monitor.py add "https://events.example.com/concert" \
  --label "Concert Tickets" --condition "contains 'available'"
```

## Content changes

```bash
# Watch a government page for updates
python3 scripts/monitor.py add "https://www.gov.za/services/visa" \
  --label "Visa Processing Updates"

# Monitor a competitor
python3 scripts/monitor.py add "https://competitor.com/pricing" \
  --label "Competitor Pricing Page"

# Track job postings
python3 scripts/monitor.py add "https://company.com/careers" \
  --label "Job Postings" --condition "contains 'senior engineer'"
```

## Focused monitoring with selectors

```bash
# Only watch the price element
python3 scripts/monitor.py add "https://store.com/product" \
  --label "Product Price" --selector "#price"

# Watch just the status section
python3 scripts/monitor.py add "https://service.com/status" \
  --label "Service Status" --selector ".status-banner"
```

## Cron job setup (OpenClaw)

```json
{
  "name": "Web Monitor Check",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *", "tz": "Africa/Johannesburg" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check all web monitors by running: python3 <path>/scripts/monitor.py check\nReport any monitors where status='changed' or condition_met=true. If nothing changed, stay silent.",
    "timeoutSeconds": 120
  },
  "delivery": { "mode": "announce" }
}
```
