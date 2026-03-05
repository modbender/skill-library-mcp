---
name: jd-price-protect
description: Auto-apply JD.com (京东) price protection on all eligible orders. Connects to Chrome via OpenClaw Browser Relay CDP, navigates to JD price protection page, clicks all "申请价保" buttons, and reports refund results. Supports pagination and scheduled cron usage.
tags: [shopping, automation, browser, jd, price-protection, china, 京东, 价保]
author: Danielwangyy
version: 1.0.0
---

# JD Price Protection

Auto-apply price protection (价格保护) on all eligible JD.com orders via Chrome Browser Relay.

## Prerequisites

- Chrome with OpenClaw Browser Relay extension installed and connected (badge ON)
- User must be logged into JD.com in Chrome
- OpenClaw gateway running

## Usage

Run the script:

```bash
node <skill-dir>/scripts/price-protect.js
```

The script will:
1. Connect to Chrome via OpenClaw's CDP relay (auto-derives relay token from gateway config)
2. Navigate to `https://pcsitepp-fm.jd.com/` if needed
3. Click every "申请价保" button on the page
4. Reload and collect results (successes with refund amounts, failures with reasons)
5. Output JSON results

## Interpreting Results

```json
{
  "total": 11,
  "clicked": 11,
  "success": [{"name": "ANKER 140W充电线...", "amount": "6.00"}],
  "failed": [{"name": "KAMAN收纳盒...", "reason": "无差价"}]
}
```

- Only notify user if `success` array is non-empty (refunds obtained)
- If all items show "无差价", update state silently

## Scheduled Usage

Set up a cron job to run every ~8 hours. Example agent prompt:

> Run `node <skill-dir>/scripts/price-protect.js`. If Chrome relay is disconnected (error), skip silently. If refunds found, notify user. Otherwise update checkedAt silently.

## Troubleshooting

- **"No browser page available"**: Chrome relay disconnected. User must click Browser Relay toolbar icon.
- **"No gateway token found"**: Set `GATEWAY_TOKEN` env var or ensure `~/.openclaw/openclaw.json` has `gateway.auth.token`.
- **Timeout on clicks**: A popup may be blocking. Script presses Escape after each click to dismiss.

## How It Works

Derives the relay auth token via `HMAC-SHA256(gatewayToken, "openclaw-extension-relay-v1:<port>")`, connects Playwright to Chrome's CDP websocket, then uses `getByText('申请价保', {exact: true}).click()` to trigger each button.
