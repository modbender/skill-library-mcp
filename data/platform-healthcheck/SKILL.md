---
name: crusty-platform-healthcheck
description: "Health check dashboard for agent platform APIs. Tests 20+ platforms for availability, response time, auth status, and Cloudflare blocking. Run: python3 scripts/healthcheck.py check"
version: 1.0.0
metadata:
  openclaw:
    emoji: "🏥"
    requires:
      bins:
        - python3
    skillKey: platform-healthcheck
---

# Platform Health Check — Agent API Status Dashboard

Tests API availability across the agent internet. Checks 20+ platforms for uptime, response time, authentication status, and Cloudflare blocking.

## Usage

```bash
# Run full health check
python3 scripts/healthcheck.py check

# JSON output (for cron/automation)
python3 scripts/healthcheck.py check --json

# Check specific platforms
python3 scripts/healthcheck.py check --only clawquests,colony,bankr

# Show history
python3 scripts/healthcheck.py history --days 7
```

## What It Tests

For each platform:
- **Connectivity**: Can we reach the API?
- **Response Time**: How fast does it respond?
- **Auth Status**: Does our API key still work?
- **Cloudflare**: Is the endpoint Cloudflare-blocked for agents?
- **SSL**: Is the certificate valid?

## Output

| Platform | Status | Time | Auth | CF |
|----------|--------|------|------|-----|
| ClawQuests | UP | 245ms | OK | No |
| Colony | UP | 312ms | OK | No |
| Bankr | UP | 189ms | OK | No |
| Metaculus | UP | 567ms | N/A | Yes |
