---
description: Monitor website uptime, measure response times, and check HTTP status codes for any URL.
---

# Uptime Monitor

Check website availability and performance.

## Capabilities

- **Uptime Check**: Verify if a website is up or down
- **Response Time**: Measure DNS, connect, TLS, and total response times
- **Status Codes**: Report HTTP status codes and redirects
- **Bulk Check**: Monitor multiple URLs at once
- **History**: Repeated checks over time with summary

## Usage

Ask the agent to:
- "Is example.com up?"
- "Measure response time for mysite.org"
- "Check these 5 URLs and report status"
- "Monitor api.example.com every 30 seconds for 5 minutes"

## How It Works

Uses `curl` with timing output:

```bash
curl -o /dev/null -s -w "HTTP %{http_code} | DNS: %{time_namelookup}s | Connect: %{time_connect}s | TLS: %{time_appconnect}s | Total: %{time_total}s\n" https://example.com
```

## Requirements

- `curl` (pre-installed on most systems)
- No API keys needed
