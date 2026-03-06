---
name: review-reply
description: "Automatically monitors your App Store reviews and drafts warm, on-brand replies for 1–3 star reviews — so unhappy users hear back fast. Connects to App Store Connect API, detects repeat complaint patterns as bug signals, and delivers a daily approval queue to Telegram at 8am. You approve, it sends. Supports multiple apps simultaneously."
version: "1.0.2"
category: app-management
tags: [app-store, ios, reviews, replies, monitoring, app-store-connect, ratings, customer-support, automation, indie-dev, solo-founder]
---

# ReviewReply Skill

Automated App Store review monitor, reply drafter, and pattern detector. Monitors App Store Connect for new reviews, drafts warm on-brand replies for 1–3★ reviews using Claude, surfaces repeat-complaint patterns as bug alerts, and delivers a daily Telegram approval queue at 8am.

## Skill Directory

```
skills/review-reply/
├── SKILL.md                          # This file — AI instructions & skill spec
├── README.md                         # Full usage docs and setup guide
├── scripts/
│   ├── monitor.py                    # Polls App Store Connect API for new reviews
│   ├── draft_reply.py                # Drafts warm on-brand replies via Claude
│   ├── pattern_detector.py           # Surfaces repeat-complaint patterns as bug alerts
│   └── queue_manager.py              # Manages approval queue, Telegram 8am digest
├── references/
│   ├── app-store-connect-api.md      # API auth setup (JWT, keys, endpoints)
│   └── reply-guidelines.md           # Brand voice, tone, dos/don'ts
├── templates/
│   └── reply-prompts.md              # Claude prompt templates per star rating
└── data/
    ├── reviews.json                  # Raw review store (auto-created)
    ├── queue.json                    # Pending approval queue (auto-created)
    └── metrics.json                  # Response rate, timing, rating trends (auto-created)
```

---

## 1. Monitor Workflow

**Script:** `scripts/monitor.py`

### What It Does
1. Reads app list from config
2. For each app, calls App Store Connect API → `/v1/apps/{id}/customerReviews`
3. Stores new reviews in `data/reviews.json` (skips already-seen IDs)
4. For reviews rated 1–3★: triggers `draft_reply.py` automatically
5. Passes all new reviews to `pattern_detector.py`
6. Logs run timestamp to `data/metrics.json`

### Run Schedule
- Designed to run via cron/launchd every 4 hours
- Manual run: `python3 scripts/monitor.py`

### Review Data Schema
```json
{
  "id": "string",
  "app_id": "string",
  "app_name": "string",
  "rating": 1,
  "title": "string",
  "body": "string",
  "reviewer": "string",
  "territory": "string",
  "created_date": "ISO8601",
  "fetched_at": "ISO8601",
  "reply_status": "pending|drafting|approved|posted|rejected|skipped",
  "draft_reply": "string|null",
  "approved_reply": "string|null",
  "replied_at": "ISO8601|null"
}
```

---

## 3. Draft Reply Workflow

**Script:** `scripts/draft_reply.py`

### What It Does
1. Receives a review object (rating, title, body, app name)
2. Selects the appropriate prompt template from `templates/reply-prompts.md` based on star rating
3. Calls Claude API with brand guidelines injected
4. Stores draft in `data/queue.json` with status `pending`
5. Does NOT auto-post — all replies require human approval

### Only Drafts For
- 1★, 2★, 3★ reviews (negative/neutral)
- 4★ and 5★ reviews: logged but no draft created (status = `skipped`)

### Output
```json
{
  "review_id": "string",
  "app_name": "string",
  "rating": 2,
  "review_title": "string",
  "review_body": "string",
  "draft_reply": "string",
  "drafted_at": "ISO8601",
  "status": "pending",
  "approved_reply": null,
  "posted_at": null
}
```

---

## 4. Pattern Detection Workflow

**Script:** `scripts/pattern_detector.py`

### What It Does
1. Reads all reviews from the last 7 days in `data/reviews.json`
2. Groups by app
3. Extracts complaint keywords/themes using Claude (semantic clustering)
4. **Threshold:** If the same theme/complaint appears 3+ times in 7 days → bug alert
5. Sends immediate Telegram alert (does not wait for 8am queue)

### Alert Format (Telegram)
```
🚨 *Pattern Alert — FeedFare*

Complaint: "Feed not refreshing / stuck on loading"
Count: 5 reviews in the last 7 days
Rating avg: 1.8★

Recent examples:
• "App is broken, feed never loads" — 1★ (2026-02-18)
• "Stuck on spinning wheel for days" — 2★ (2026-02-17)
• "Used to work great, now broken" — 2★ (2026-02-16)

👉 Likely bug. Recommend investigating feed refresh logic.
```

### Pattern Deduplication
- Patterns already alerted in the last 24h are not re-sent
- Each unique theme per app gets one alert per 24h window
- State stored in `data/metrics.json` under `pattern_alerts`

---

## 5. Approval Queue Workflow

**Script:** `scripts/queue_manager.py`

### Daily Digest (8am Telegram)
Every morning at 8:00 AM local time, `queue_manager.py` sends a Telegram message summarizing all pending replies:

```
📱 *ReviewReply Morning Queue — 3 Pending*

━━━━━━━━━━━━━━━━━━━
1️⃣ *FeedFare* — 2★ by @user123 (Feb 18)
   "App crashes every time I open it"

   📝 *Draft Reply:*
   "Hi there! We're so sorry to hear about the crashes — that's definitely not the experience we want for you. Our team just pushed a fix in v2.1.1 that addresses the crash on launch. Please update and let us know if it helps! 🙏"

   ✅ /approve_1  ✏️ /edit_1  ❌ /reject_1
━━━━━━━━━━━━━━━━━━━
2️⃣ *FeedFare* — 1★ by @disappointed_dev (Feb 18)
   ...
━━━━━━━━━━━━━━━━━━━

📊 Stats: 12 reviewed · 8 replied · 67% response rate
```

### Reply Approval Commands
- `/approve_N` — marks reply as approved, posts to App Store Connect
- `/edit_N <new text>` — replaces draft with edited text, marks approved
- `/reject_N` — marks as rejected (no reply sent), removes from queue
- `/skip_N` — marks as skipped (no reply ever), removes from queue

### Queue State Machine
```
new review
    │
    ▼
[drafting] → draft failed → [error]
    │
    ▼
[pending] ←→ [edited]
    │
    ├─ approve → [approved] → post API → [posted]
    ├─ reject  → [rejected]
    └─ skip    → [skipped]
```

### Auto-Posting
When a reply is approved:
1. `queue_manager.py` calls App Store Connect API → `POST /v1/customerReviewResponses`
2. Marks status as `posted` in `data/queue.json`
3. Records `replied_at` timestamp for metrics

---

## 6. Metrics Tracking

**Data file:** `data/metrics.json`

### Tracked Metrics

| Metric | Description |
|--------|-------------|
| `total_reviews` | All-time review count per app |
| `reviews_this_week` | Rolling 7-day count |
| `avg_rating` | Current average star rating per app |
| `rating_trend` | Direction vs previous 7-day period |
| `response_rate` | % of 1-3★ reviews with approved/posted replies |
| `avg_response_time_hrs` | Average hours between review and reply posted |
| `pending_count` | Currently in queue |
| `posted_count` | Successfully replied |
| `rejected_count` | Intentionally skipped |
| `pattern_alerts` | History of pattern alerts sent |

### On-Demand Metrics Report
Say "review metrics" or "how are my apps doing?" and the AI will read `data/metrics.json` and format a summary.

---

## 7. AI Instructions — Conversational Commands

The AI handles these conversational patterns:

| User Says | AI Action |
|-----------|-----------|
| "check for new reviews" | Run `python3 scripts/monitor.py` |
| "show pending replies" | Read `data/queue.json`, list pending items |
| "approve reply 3" | Run `python3 scripts/queue_manager.py --approve 3` |
| "edit reply 2: <new text>" | Run `python3 scripts/queue_manager.py --edit 2` then pass text via stdin or temp file — never interpolate user text directly into shell strings |
| "reject reply 1" | Run `python3 scripts/queue_manager.py --reject 1` |
| "draft a reply for review X" | Run `python3 scripts/draft_reply.py --review-id X` |
| "how are my apps doing?" | Read `data/metrics.json`, format summary |
| "show me recent reviews" | Read `data/reviews.json`, show last 10 |
| "any patterns this week?" | Run `python3 scripts/pattern_detector.py --report` |
| "response rate?" | Read metrics, show response_rate per app |
| "add app MyApp 1234567890" | Add to APPS config in monitor.py |

---

## 8. Environment Variables Required

| Variable | Description |
|----------|-------------|
| `APP_STORE_KEY_ID` | App Store Connect API Key ID |
| `APP_STORE_ISSUER_ID` | App Store Connect Issuer ID |
| `APP_STORE_PRIVATE_KEY_PATH` | Path to `.p8` private key file |
| `ANTHROPIC_API_KEY` | Claude API key for reply drafting |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |

Store these in `~/.openclaw/.env` or export in shell profile.

---

## 9. Cron / LaunchAgent Schedule

```
# App Store review monitor — every 4 hours
0 */4 * * * cd /Users/nick/.openclaw/workspace && python3 skills/review-reply/scripts/monitor.py >> /tmp/review-reply.log 2>&1

# Daily approval queue — 8am every day
0 8 * * * cd /Users/nick/.openclaw/workspace && python3 skills/review-reply/scripts/queue_manager.py --send-digest >> /tmp/review-reply.log 2>&1
```

See README.md for LaunchAgent plist setup.

---

## 10. Data Files Reference

All data lives in `data/` and is plain JSON — easy to inspect, backup, and migrate.

| File | Purpose |
|------|---------|
| `data/reviews.json` | All fetched reviews, one object per review |
| `data/queue.json` | Active reply queue (pending/approved/rejected items) |
| `data/metrics.json` | Aggregated metrics, pattern alert history |

### Backup
```bash
cp -r skills/review-reply/data/ ~/review-reply-backup/
```
