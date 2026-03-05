---
name: package-tracker
description: Track packages and shipments via the 17track API. Use when the user asks to track a package, check delivery status, add a tracking number, list tracked shipments, or get updates on deliveries. Supports 2000+ carriers worldwide with auto carrier detection and tracking URLs.
---

# Package Tracker

Track packages via the 17track universal API. Supports FedEx, UPS, DHL, CTT, China Post, Royal Mail, USPS, and 2000+ other carriers with automatic carrier detection.

## Setup

Run once from the skill directory:

```bash
cd /root/.openclaw/workspace/skills/package-tracker
bash scripts/setup.sh
```

Then edit `scripts/.env` to add your API key:

```
SEVENTEEN_TRACK_API_KEY=your_key_here
```

Get a free key at https://admin.17track.net (100 registrations/month, unlimited status checks).

## Usage

All commands run from the skill directory. Activate the venv first:

```bash
cd /root/.openclaw/workspace/skills/package-tracker
source scripts/venv/bin/activate
```

### Add a Package

```bash
python scripts/cli.py add "TRACKING_NUMBER" -d "Description of contents"
```

- Carrier is auto-detected from the tracking number format
- Override with `-c "FedEx"` if needed
- Uses 1 registration from monthly quota (100/month free)
- Returns a tracking URL for the detected carrier

### Check for Updates

```bash
python scripts/cli.py check
```

- Queries 17track for all active packages
- Prints status changes and new tracking events
- Outputs notifications to stdout for OpenClaw to relay via native messaging
- gettrackinfo calls are free and unlimited

### List Packages

```bash
python scripts/cli.py list          # Active only
python scripts/cli.py list --all    # Include delivered/inactive
```

### Package Details

```bash
python scripts/cli.py details "TRACKING_NUMBER"
```

Shows full tracking history with all events, locations, and timestamps.

### Remove a Package

```bash
python scripts/cli.py remove "TRACKING_NUMBER"
```

Deactivates tracking (does not delete history).

### Check API Quota

```bash
python scripts/cli.py quota
```

Shows registrations used this month vs. the 100/month free limit.

## Cron Integration

Set up periodic checks with cron or OpenClaw heartbeats.

### Using cron (every 3 hours)

```bash
# Add to crontab:
0 */3 * * * cd /root/.openclaw/workspace/skills/package-tracker && scripts/venv/bin/python scripts/check_updates.py --quiet
```

### Using OpenClaw heartbeat

In your heartbeat logic, include:

```bash
cd /root/.openclaw/workspace/skills/package-tracker
source scripts/venv/bin/activate
python scripts/check_updates.py
```

The check_updates.py script:
- Checks all active packages for updates
- Prints notifications to stdout for OpenClaw to relay
- Exits 0 on success, 1 on error
- Use `--quiet` to suppress output when there are no updates

## Notifications

When updates are detected, the tracker outputs formatted notifications to stdout. OpenClaw reads this output and relays it via its native message tool — which works on Telegram, Signal, Discord, WhatsApp, or whatever channel the user has configured.

## Tracking URLs

Every package gets a carrier-specific tracking URL:

| Carrier | URL Pattern |
|---------|------------|
| FedEx | `fedex.com/fedextrack/?trknbr={tn}` |
| UPS | `ups.com/track?tracknum={tn}` |
| DHL | `dhl.com/en/express/tracking.html?AWB={tn}` |
| CTT | `ctt.pt/.../objectSearch.jspx?objects={tn}` |
| USPS | `tools.usps.com/go/TrackConfirmAction?tLabels={tn}` |
| Fallback | `t.17track.net/en#nums={tn}` |

The `get_tracking_url(tracking_number, carrier)` function in tracker.py generates these.

## Status Codes

| Status | Emoji | Meaning |
|--------|-------|---------|
| pending | ⏳ | Just added, not yet checked |
| Not Found | ❓ | 17track has no data yet |
| In Transit | 🚚 | Package is moving |
| Pick Up | 📬 | Ready for pickup |
| Delivered | ✅ | Delivered (auto-deactivated) |
| Undelivered | ⚠️ | Delivery attempt failed |
| Expired | ⌛ | Tracking data expired |
| Alert | 🚨 | Exception or issue |

Delivered packages are automatically deactivated.

## Data Storage

- **Database:** `scripts/data/tracker.db` (SQLite)
- **Tables:** `packages`, `tracking_events`, `api_usage`
- All data is local. Nothing is sent externally except 17track API calls.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SEVENTEEN_TRACK_API_KEY` | Yes | 17track API key from admin.17track.net |

## Troubleshooting

- **"API key not set"** — Edit `scripts/.env` and add your 17track key
- **"Monthly limit reached"** — Free tier is 100 registrations/month. Wait or upgrade.
- **No carrier detected** — Pass `-c "CarrierName"` when adding, or let 17track auto-detect (carrier code 0)

## References

- `references/carriers.md` — Full list of supported carriers with patterns and URLs
- `references/17track-api.md` — API endpoint reference, status codes, rate limits