# Simple Monitoring (15-30 min setup)

## Who This Is For

- Side projects and MVPs
- Solo developers
- Small teams without dedicated ops
- "I just want to know if it's broken"

## The Minimal Stack

### 1. Uptime Monitoring

**Option A: UptimeRobot (SaaS, easiest)**
- Free tier: 50 monitors, 5-min intervals
- Setup: Create account → Add URL → Done
- Alerts: Email, Slack, Telegram, webhooks

**Option B: Uptime Kuma (self-hosted, more control)**
```bash
docker run -d --restart=unless-stopped -p 3001:3001 \
  -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```
- Features: HTTP, TCP, DNS, Docker, push monitors
- Alerts: 90+ notification services (Telegram, Discord, Slack, email...)
- Status pages built-in

### 2. Cron Job Monitoring

**Healthchecks.io** — free tier generous (20 checks)

```bash
# Add to end of your cron job
curl -fsS -m 10 --retry 5 https://hc-ping.com/YOUR-UUID-HERE

# With failure reporting
curl -fsS -m 10 --retry 5 https://hc-ping.com/YOUR-UUID-HERE/$?
```

If the ping doesn't arrive on schedule → alert fires.

### 3. Error Tracking

**Sentry Free Tier** — 5K events/month

```bash
# Next.js
npx @sentry/wizard@latest -i nextjs

# Node.js
npm install @sentry/node
```

```javascript
// Minimal setup
import * as Sentry from "@sentry/node";
Sentry.init({ dsn: "https://xxx@sentry.io/xxx" });
```

## What to Monitor

| Check | Tool | Why |
|-------|------|-----|
| Homepage loads | UptimeRobot/Uptime Kuma | Basic availability |
| API health endpoint | UptimeRobot/Uptime Kuma | Backend alive |
| SSL certificate expiry | UptimeRobot/Uptime Kuma | Avoid surprise expiration |
| Database backup cron | Healthchecks.io | Know if backups stop |
| Production errors | Sentry | Fix bugs before users report |

## Alert Channels

**Telegram** (recommended for solo devs):
1. Create bot via @BotFather
2. Get chat ID
3. Configure in Uptime Kuma/UptimeRobot

**Why Telegram:**
- Free
- Instant
- Works on all devices
- No email noise

## Setup Checklist

```
□ Uptime check on main URL
□ Uptime check on API/health endpoint
□ SSL expiry monitoring
□ Healthchecks.io for critical cron jobs
□ Sentry for error tracking
□ Alerts going to Telegram/Slack
□ Test that alerts actually work
```

**Total time: 15-30 minutes**
**Total cost: $0-5/month**
