---
name: shipment-tracker
description: "Track packages across carriers (USPS, UPS, FedEx, DHL, Amazon, OnTrac, LaserShip). Use when: user asks about package status, adds a tracking number, wants delivery updates, or mentions shipments. Reads a markdown shipments file, auto-detects carrier from tracking number patterns, and checks status. Hybrid approach: tries direct HTTP first, recommends browser-use for JS-heavy carrier pages. ⚠️ Privacy: browser-use fallback sends tracking data to cloud services."
---

# Shipment Tracker

Track packages across multiple carriers from a markdown shipments file. Auto-detects carrier from tracking number patterns. Hybrid status checking: tries direct HTTP first, falls back to recommending browser-use for full tracking details.

## Shipments File Format

The skill reads a markdown file with a table of active shipments:

```markdown
# Active Shipments

| Order | Item | Carrier | Tracking | Link | Added |
|-------|------|---------|----------|------|-------|
| Acme #1234 | Widget | USPS | 9449050899562006763949 | [Track](https://...) | 2026-02-19 |
```

- **Carrier** and **Link** are optional — auto-detected from tracking number pattern
- Remove entries once delivered to keep the file clean
- Default location: `memory/shipments.md` in the workspace

## Usage

```bash
# Check all active shipments
python3 scripts/shipment_tracker.py memory/shipments.md

# JSON output for integrations
python3 scripts/shipment_tracker.py memory/shipments.md --format json

# Detect carrier from a tracking number
python3 scripts/shipment_tracker.py --detect 9449050899562006763949
```

## Carrier Detection

Automatically identifies carrier from tracking number patterns:

| Carrier | Pattern Examples |
|---------|-----------------|
| USPS | 92, 93, 94, 95 + 20-26 digits |
| UPS | 1Z + 16 alphanumeric |
| FedEx | 12, 15, or 20 digits; 7489 prefix |
| DHL | 10-11 digits or 3 letters + 7 digits |
| Amazon | TBA + 12+ digits |
| OnTrac | C or D + 14 digits |
| LaserShip | L + letter + 8+ digits |

## Status Checking (Hybrid)

1. **Direct HTTP** — Attempts to extract status from carrier tracking pages via urllib. Works for basic status on USPS and some other carriers.
2. **Browser-use fallback** — When HTTP fails or carriers use JS-heavy pages, the script provides the exact browser-use command to run.

When the script output includes `needs_browser_use: true`, it will provide a complete browser-use command:

```python
python3 -c "
import asyncio
from browser_use import Agent, Browser, ChatBrowserUse
async def main():
    browser = Browser(use_cloud=True)
    llm = ChatBrowserUse()
    agent = Agent(
        task='Go to <tracking_url> and extract the current tracking status, delivery date, and location',
        llm=llm, browser=browser
    )
    result = await agent.run(max_steps=10)
    print('TRACKING:', result)
asyncio.run(main())
"
```

This ensures reliable tracking across all carriers, even those with aggressive bot detection.

**When browser-use is needed:**
- UPS, FedEx, Amazon (heavily JS-based tracking pages)
- USPS when basic parsing fails (complex status updates)
- Any carrier with CAPTCHA or bot detection
- Sites that require user interaction or form submission

## Workflow

1. User provides a tracking number → run `--detect` to identify carrier
2. Add to `memory/shipments.md` with order details
3. Morning briefing or on-demand: run the script to check all shipments
4. For shipments needing browser-use:
   - **Non-sensitive packages:** Use the provided browser-use command
   - **Privacy-sensitive packages:** Manual browser check instead (data stays local)
5. When delivered: remove from the shipments file

**Privacy guidance:** For medical supplies, personal items, or confidential orders, consider manual tracking to avoid sending shipment details to cloud services.

## System Access

**Direct skill execution:**
- **File reads:** One markdown file (path provided as argument)
- **Network:** HTTPS GET to carrier tracking pages (e.g., `tools.usps.com`) — read-only, no authentication
- **No file writes, no subprocess calls, no shell execution**

**Browser-use fallback (privacy implications):**
When the skill recommends browser-use commands, **external data transmission occurs**:
- **Tracking numbers** and **order information** sent to cloud browser service
- **Package details** processed by external LLM (ChatBrowserUse)
- **Carrier tracking URLs** accessed via cloud infrastructure

**Privacy consideration:** Browser-use fallback involves third-party services that may log or process shipment data. For sensitive packages, consider manual browser tracking instead of the provided browser-use commands.

## Requirements

- Python 3.10+
- Outbound HTTPS access to carrier tracking sites
- browser-use (optional, for full tracking on JS-heavy sites)
