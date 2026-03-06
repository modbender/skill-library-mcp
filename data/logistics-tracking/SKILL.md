---
name: logistics-tracking
description: >
  Track international packages by tracking number. Supports 3100+ carriers (China Post, DHL, FedEx, UPS, USPS, Yanwen, Cainiao, etc.) via 17track.
  Optional: set TRACK17_API_KEY for best results. Without a key, uses Playwright (headless browser) as fallback.
  Use when the user asks about package tracking, shipment status, delivery time, or logistics queries.
license: MIT
metadata:
  author: shopme
  version: "1.0.1"
  mcp-server: "@shopmeagent/logistics-tracking-mcp"
---

# Logistics Tracking

Track international packages by tracking number only. Supports 3100+ carriers worldwide.

## When to Use

- User asks "where is my package" or provides a tracking number
- User needs to check shipment status or delivery estimate
- User asks about customs clearance or logistics exceptions
- User needs to track multiple packages at once

## How It Works

| Mode | API Key Required? | Description |
|------|-------------------|-------------|
| **With TRACK17_API_KEY** | Yes (1 key) | Uses the official api.17track.net — most reliable, 3100+ carriers. |
| **Without key** | No | Uses Playwright (headless Chromium) to query t.17track.net. Requires `playwright` npm package. |

**Recommendation:** Set `TRACK17_API_KEY` for the best reliability. Get a free key at https://api.17track.net

## Option A: Deploy as HTTP Service (users need no key)

You deploy the MCP HTTP server with `TRACK17_API_KEY` on your server. End users connect via URL — they don't need any API key.

### 1. Start the server (your side)

```bash
export TRACK17_API_KEY=your-17track-api-key
npx -y @shopmeagent/logistics-tracking-mcp serve

# Default: http://0.0.0.0:3000/mcp
# Override with PORT and HOST env vars
```

### 2. User/client MCP config (Streamable HTTP)

```json
{
  "mcpServers": {
    "logistics-tracking": {
      "type": "streamable-http",
      "url": "https://your-domain.com/mcp"
    }
  }
}
```

Users only need a tracking number — no API key required on their end.

---

## Option B: Local stdio (zero-config or with key)

**Zero-config** (no key, uses Playwright fallback — requires `playwright` installed):

```json
{
  "mcpServers": {
    "logistics-tracking": {
      "command": "npx",
      "args": ["-y", "@shopmeagent/logistics-tracking-mcp"]
    }
  }
}
```

**Recommended** — with API key for broader carrier coverage and better reliability:

```json
{
  "mcpServers": {
    "logistics-tracking": {
      "command": "npx",
      "args": ["-y", "@shopmeagent/logistics-tracking-mcp"],
      "env": {
        "TRACK17_API_KEY": "your-17track-api-key"
      }
    }
  }
}
```

Get a free 17track API key: https://api.17track.net

## Using with OpenClaw

Add this skill to OpenClaw:

```bash
npx skills add shopmeskills/mcp
```

Then in OpenClaw's MCP configuration, add either the **HTTP** or **stdio** config shown above.

**Example prompts:**
- "Track package YT2412345678901234"
- "Where is my package LX123456789CN?"
- "Check status of 1ZABCDEF1234567890"

## Available Tools

### track_package
Query tracking info for a single package.
- Input: `trackingNumber` (required), `carrier` (optional, auto-detected)
- Returns: status, current location, timeline of events

### detect_carrier
Identify the carrier from a tracking number's format.
- Input: `trackingNumber`
- Returns: carrier name, confidence level

### batch_track
Track up to 40 packages at once.
- Input: `trackingNumbers` array
- Returns: array of tracking results

### explain_status
Get a human-readable explanation of a tracking status code.
- Input: `statusCode` (e.g. InTransit, CustomsClearance, Delivered)
- Returns: description and advice in English

## Tracking Number Format Guide

| Pattern | Carrier | Example |
|---------|---------|---------|
| `XX123456789CN` | China Post | LX123456789CN |
| `EX123456789CN` | China EMS | EA123456789CN |
| `YT + 16 digits` | Yanwen | YT1234567890123456 |
| `LP + 14+ digits` | Cainiao | LP12345678901234 |
| `SF + 12+ digits` | SF Express | SF1234567890123 |
| `1Z + 16 chars` | UPS | 1ZABCDEF1234567890 |
| `94/93/92 + 20 digits` | USPS | 9400111899223100012345 |
| `10-11 digits` | DHL | 1234567890 |
| `12-15 digits` | FedEx | 123456789012 |

## Typical Delivery Times (International)

| Route | Standard | Express |
|-------|----------|---------|
| China to US | 15-30 days | 5-10 days |
| China to EU | 15-30 days | 5-10 days |
| China to SE Asia | 7-15 days | 3-7 days |
| China to Japan/Korea | 5-10 days | 3-5 days |

## Status Codes Explained

- **InfoReceived**: Carrier has the info but hasn't picked up the package (1-3 day wait)
- **InTransit**: Package is moving through the logistics network
- **CustomsClearance**: Going through customs (3-7 business days typical)
- **OutForDelivery**: Final delivery attempt today
- **Delivered**: Successfully delivered
- **Exception**: Problem occurred (customs hold, wrong address, failed delivery)
- **Returned**: Being sent back to origin

## Tips

1. **No key needed**: Without TRACK17_API_KEY, the tool uses Playwright to query 17track directly. Install Playwright with `npm install playwright` for this to work.
2. **3100+ carriers**: With a 17track API key, auto-detects carrier from the tracking number.
3. Wait 24-48 hours after shipment before tracking — data may not be available on day one.
4. Allow at least 2 hours between queries for the same tracking number to avoid rate limiting.
5. Use `batch_track` for multiple packages — more efficient than individual queries.
