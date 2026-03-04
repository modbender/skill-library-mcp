# 📱 ReviewReply Skill

Automated App Store review monitor, reply drafter, and pattern detector. Polls App Store Connect for new reviews, uses Claude to draft warm on-brand replies for 1–3★ reviews, surfaces repeat complaints as instant bug alerts, and delivers a daily 8am Telegram approval queue.

---

## What It Does

- **🔍 Monitors reviews** — polls App Store Connect every 4h across all your apps
- **✏️ Drafts replies** — Claude writes warm, on-brand responses for 1–3★ reviews
- **🚨 Pattern alerts** — same complaint 3+ times in 7 days → instant Telegram bug alert
- **📲 Daily queue** — 8am Telegram digest with pending replies; approve/edit/reject inline
- **📤 Auto-posts** — approved replies posted directly to App Store Connect
- **📊 Metrics** — response rate, avg response time, rating trend per app

---

## Quick Start

### 1. Prerequisites

```bash
# Python 3.9+
python3 --version

# JWT library for App Store Connect auth
pip3 install PyJWT cryptography
```

### 2. App Store Connect API Key

You need an API key to fetch reviews and post replies. Full setup in `references/app-store-connect-api.md`.

**Quick version:**
1. Sign in to [App Store Connect](https://appstoreconnect.apple.com) → Users & Access → Integrations → App Store Connect API
2. Create key with **Customer Support** role
3. Download the `.p8` file (only shown once!)
4. Note your **Key ID** and **Issuer ID**

### 3. Telegram Bot

Get your bot token and chat ID:

```bash
# Create a bot: message @BotFather on Telegram → /newbot
# Get your chat ID: message @userinfobot → copy your ID
```

### 4. Set Environment Variables

Add to `~/.zshrc` (or `~/.openclaw/.env`):

```bash
# App Store Connect
export APP_STORE_KEY_ID="ABC123DEF4"
export APP_STORE_ISSUER_ID="69a6de70-xxxx-xxxx-xxxx-xxxxxxxxxx"
export APP_STORE_PRIVATE_KEY_PATH="$HOME/.appstoreconnect/keys/AuthKey_ABC123DEF4.p8"

# Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Telegram
export TELEGRAM_BOT_TOKEN="1234567890:AAxxxxxxxxxxxxxxxx"
export TELEGRAM_CHAT_ID="123456789"
```

```bash
source ~/.zshrc
```

### 5. First Run

```bash
cd /Users/nick/.openclaw/workspace
python3 skills/review-reply/scripts/monitor.py --dry-run   # Test auth + fetch
python3 skills/review-reply/scripts/monitor.py             # Live run
```

### 6. Schedule with Cron

```bash
crontab -e
```

Add:
```cron
# ReviewReply: fetch reviews every 4 hours
0 */4 * * * cd /Users/nick/.openclaw/workspace && python3 skills/review-reply/scripts/monitor.py >> /tmp/review-reply.log 2>&1

# ReviewReply: send daily approval digest at 8am
0 8 * * * cd /Users/nick/.openclaw/workspace && python3 skills/review-reply/scripts/queue_manager.py --send-digest >> /tmp/review-reply.log 2>&1
```

---

## Directory Structure

```
skills/review-reply/
├── SKILL.md                           # AI instructions & skill spec
├── README.md                          # This file
├── scripts/
│   ├── monitor.py                     # Polls App Store Connect for new reviews
│   ├── draft_reply.py                 # Drafts replies with Claude
│   ├── pattern_detector.py            # Detects complaint patterns → bug alerts
│   └── queue_manager.py               # Approval queue + Telegram digest
├── references/
│   ├── app-store-connect-api.md       # API auth setup guide
│   └── reply-guidelines.md            # Brand voice, tone, dos/don'ts
├── templates/
│   └── reply-prompts.md               # Claude prompts per star rating
└── data/                              # Auto-created on first run
    ├── reviews.json                   # All fetched reviews
    ├── queue.json                     # Approval queue
    └── metrics.json                   # Response rate, rating trends
```

---

## Monitored Apps

| App | App ID | Status |
|-----|--------|--------|
| FeedFare | `6758923557` | ✅ Live |
| Inflection Point | TBD | ⏳ Pending |
| PetFace | TBD | ⏳ When live |

To add an app, edit `scripts/monitor.py` → `APPS` list:
```python
APPS = [
    {"name": "FeedFare",         "id": "6758923557"},
    {"name": "Inflection Point", "id": "YOUR_APP_ID"},
    {"name": "PetFace",          "id": "YOUR_APP_ID"},
]
```

---

## Daily Workflow

### 1. Monitor (every 4 hours, automated)

```
python3 scripts/monitor.py
```

- Fetches new reviews from App Store Connect
- Auto-drafts replies for 1–3★ reviews using Claude
- Runs pattern detection across all recent reviews
- Sends immediate Telegram alert if a complaint pattern is detected

### 2. Morning Queue (8am, automated)

Telegram message shows all pending replies:

```
📱 ReviewReply Morning Queue — 3 Pending (Thu Feb 19)

────────────────────
1️⃣ FeedFare — ★★☆☆☆ by @user123 (Feb 18)
   "App crashes every time I open it"

   📝 Draft:
   "We're so sorry — crashing immediately is the worst experience
   and you deserve better. We pushed a fix in v2.1.1 specifically
   for this; updating should resolve it. If it persists, please
   reach out at support@feedfare.app and we'll fix it directly. 🙏"

   ✅ /approve_1  ✏️ /edit_1  ❌ /reject_1
────────────────────
2️⃣ FeedFare — ★★★☆☆ by @AviatorMike (Feb 18)
   ...
────────────────────

📊 FeedFare: 4.2★ ➡️ · 78% replied
```

### 3. Approve/Edit/Reject

```bash
# Approve and post to App Store
python3 scripts/queue_manager.py --approve 1

# Edit then approve
python3 scripts/queue_manager.py --edit 1 "Your custom reply text here"

# Reject (no reply sent)
python3 scripts/queue_manager.py --reject 2

# Skip (never reply)
python3 scripts/queue_manager.py --skip 3
```

Or respond via conversational AI — see [AI Commands](#ai-commands) below.

---

## Pattern Detection

The pattern detector runs after every monitor fetch. If the same complaint appears **3+ times in 7 days**, an immediate Telegram alert fires:

```
🚨 Pattern Alert — FeedFare

📌 Complaint: Feed not refreshing / stuck on loading
Count: 5 reviews in the last 7 days
Rating avg: 1.8★

Recent examples:
• "App is broken, feed never loads" — 1★ (2026-02-18)
• "Stuck on spinning wheel for days" — 2★ (2026-02-17)
• "Used to work great, now broken" — 2★ (2026-02-16)

👉 Severity: HIGH
```

**Deduplication:** Same pattern won't re-alert within 24 hours.

Run manually:
```bash
python3 scripts/pattern_detector.py --report   # Print only, no Telegram
python3 scripts/pattern_detector.py            # Run + send alerts
python3 scripts/pattern_detector.py --days 14  # 14-day lookback
```

---

## Metrics

```bash
python3 scripts/queue_manager.py --metrics
```

```
ReviewReply Metrics — 2026-02-19

📱 FeedFare
   Total reviews:     142
   Average rating:    4.2★  (➡️ stable)
   Response rate:     78.5%
   Avg response time: 14.3h
   Replies posted:    34
   Rejected:          3

🚨 Pattern Alerts (last 7 days): 1
   • FeedFare: "Feed not refreshing" (5x)

⏱  Last monitor run: 2026-02-19 08:00 UTC
```

---

## Script Reference

### monitor.py

```bash
python3 scripts/monitor.py                    # Normal run
python3 scripts/monitor.py --dry-run          # Fetch without saving
python3 scripts/monitor.py --app 6758923557   # Single app only
python3 scripts/monitor.py --since 2026-02-01 # Custom lookback date
python3 scripts/monitor.py --no-draft         # Skip reply drafting
python3 scripts/monitor.py --no-patterns      # Skip pattern detection
```

### draft_reply.py

```bash
python3 scripts/draft_reply.py --review-id <id>         # Draft for specific review
python3 scripts/draft_reply.py --all-pending             # Draft all unqueued reviews
python3 scripts/draft_reply.py --dry-run --all-pending   # Preview without saving
```

### pattern_detector.py

```bash
python3 scripts/pattern_detector.py            # Run + send Telegram alerts
python3 scripts/pattern_detector.py --report   # Print report only
python3 scripts/pattern_detector.py --dry-run  # Detect but don't send Telegram
python3 scripts/pattern_detector.py --days 14  # Custom lookback window
```

### queue_manager.py

```bash
python3 scripts/queue_manager.py --send-digest         # Send 8am Telegram digest
python3 scripts/queue_manager.py --approve 1           # Approve reply #1
python3 scripts/queue_manager.py --edit 1 "New text"   # Edit and approve reply #1
python3 scripts/queue_manager.py --reject 2            # Reject reply #2
python3 scripts/queue_manager.py --skip 3              # Skip reply #3 forever
python3 scripts/queue_manager.py --post 1              # Retry posting reply #1
python3 scripts/queue_manager.py --status              # Show full queue status
python3 scripts/queue_manager.py --metrics             # Show metrics report
python3 scripts/queue_manager.py --dry-run --send-digest  # Preview digest
```

---

## AI Commands

When the skill is active, the AI handles these naturally:

| You say | What happens |
|---------|-------------|
| "check for new reviews" | Runs monitor.py |
| "show pending replies" | Reads queue, lists pending items |
| "approve reply 1" | Runs queue_manager.py --approve 1 |
| "edit reply 2: Great news, we fixed this in v2.1!" | Runs queue_manager.py --edit 2 "..." |
| "reject reply 3" | Runs queue_manager.py --reject 3 |
| "how are my apps doing?" | Reads metrics.json, formats summary |
| "any patterns this week?" | Runs pattern_detector.py --report |
| "response rate?" | Shows response_rate per app |
| "show recent reviews" | Reads reviews.json, shows last 10 |
| "draft all pending" | Runs draft_reply.py --all-pending |
| "add app MyApp 1234567890" | Guides you to update APPS list |
| "send the digest" | Runs queue_manager.py --send-digest |

---

## Reply Status Reference

| Status | Meaning |
|--------|---------|
| `new` | Review fetched, not yet processed |
| `drafting` | Claude is generating a draft |
| `pending` | Draft ready, awaiting approval |
| `approved` | Approved but not yet posted |
| `posted` | Reply posted to App Store ✅ |
| `rejected` | Decided not to reply |
| `skipped` | 4–5★ reviews (no reply needed) |
| `error` | Draft or post failed |

---

## Data Format

### reviews.json (sample entry)
```json
{
  "id": "1234567890abcdef",
  "app_id": "6758923557",
  "app_name": "FeedFare",
  "rating": 2,
  "title": "Used to be great",
  "body": "Feed stopped refreshing after the last update. Was my go-to aviation app.",
  "reviewer": "Pilot_Mike",
  "territory": "USA",
  "created_date": "2026-02-18T14:23:00+00:00",
  "fetched_at": "2026-02-18T16:00:00+00:00",
  "reply_status": "posted",
  "draft_reply": "We're sorry the update caused this — that's on us...",
  "approved_reply": "We're sorry the update caused this — that's on us...",
  "replied_at": "2026-02-19T09:15:00+00:00"
}
```

### queue.json (sample entry)
```json
{
  "review_id": "1234567890abcdef",
  "app_id": "6758923557",
  "app_name": "FeedFare",
  "rating": 2,
  "review_title": "Used to be great",
  "review_body": "Feed stopped refreshing after the last update.",
  "reviewer": "Pilot_Mike",
  "territory": "USA",
  "created_date": "2026-02-18T14:23:00+00:00",
  "draft_reply": "We're sorry the update caused this...",
  "drafted_at": "2026-02-18T16:02:00+00:00",
  "status": "pending",
  "approved_reply": null,
  "posted_at": null,
  "edited_at": null
}
```

---

## macOS LaunchAgent Setup (Alternative to Cron)

Create `/Library/LaunchAgents/com.talos.reviewreply.monitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.talos.reviewreply.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/nick/.openclaw/workspace/skills/review-reply/scripts/monitor.py</string>
    </array>
    <key>StartInterval</key>
    <integer>14400</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/review-reply-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/review-reply-monitor.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>APP_STORE_KEY_ID</key>
        <string>YOUR_KEY_ID</string>
        <key>APP_STORE_ISSUER_ID</key>
        <string>YOUR_ISSUER_ID</string>
        <key>APP_STORE_PRIVATE_KEY_PATH</key>
        <string>/Users/nick/.appstoreconnect/keys/AuthKey_KEYID.p8</string>
        <key>ANTHROPIC_API_KEY</key>
        <string>sk-ant-...</string>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>YOUR_BOT_TOKEN</string>
        <key>TELEGRAM_CHAT_ID</key>
        <string>YOUR_CHAT_ID</string>
    </dict>
</dict>
</plist>
```

Load it:
```bash
launchctl load /Library/LaunchAgents/com.talos.reviewreply.monitor.plist
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `JWT error: Missing credentials` | Set all 3 `APP_STORE_*` env vars |
| `Private key not found` | Check `APP_STORE_PRIVATE_KEY_PATH` path |
| `API error 401` | Key ID or Issuer ID mismatch — verify in App Store Connect |
| `API error 403` | Key needs **Customer Support** or higher role |
| `Claude error: API key not set` | Set `ANTHROPIC_API_KEY` |
| `Telegram not sending` | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| `PyJWT not found` | `pip3 install PyJWT cryptography` |
| Draft seems generic | Review content in `templates/reply-prompts.md` and `references/reply-guidelines.md` |
| Pattern alerts not firing | Check threshold (default: 3 reviews in 7 days) in `pattern_detector.py` |

---

## Example Full Session

```
[4:00am] Monitor runs → fetches 4 new reviews for FeedFare
         → 2 are 1★, 1 is 2★ → Claude drafts 3 replies
         → Pattern detector: "feed not refreshing" appears 4x in 7 days
         → Telegram: 🚨 Pattern Alert sent immediately

[8:00am] Daily digest sent to Telegram
         → Shows 3 pending replies

Nick: /approve_1   → Reply posted to App Store for review #1
Nick: /edit_2 "Hey! We actually fixed this in our latest update — would love for you to try it again!"
                   → Edited reply posted to App Store for review #2
Nick: /reject_3    → Review #3 flagged as rejected (legal threat)

[Metrics]
FeedFare: 4.2★ ➡️ | 78% replied | avg 14.3h response time
```

---

<!-- STANDARD FOOTER — Include at the bottom of every skill README.md -->

---

## Want Your Entire AI Stack Set Up Like This?

This skill is one piece of a fully automated personal AI system — morning briefs, smart dashboards, fleet monitoring, trading bots, notification digests, and more.

**I'll build and customize the whole thing for you.**

👉 [nickrae.net](https://nickrae.net) — See the full stack and book a setup call.

---

**Built by [Nick Rae](https://nickrae.net)** · Pilot · Builder · Maker  
**License:** MIT  
**Compatibility:** macOS, Linux | Requires Python 3.9+, PyJWT, cryptography
