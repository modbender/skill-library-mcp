---
name: meeting-transcripts
description: Capture meeting transcripts from Fireflies.ai via polling or webhooks. Auto-fetches transcripts, extracts action items/decisions/summaries, and writes structured markdown to memory. Use when user asks to check for meeting transcripts, set up meeting capture, or review past meetings. Supports cron-based polling (every 30 min) and real-time webhooks.
---

# Meeting Transcripts (Fireflies.ai)

Auto-capture meeting transcripts from Fireflies.ai, extract action items and decisions, write structured markdown to memory.

## Setup

### 1. Store API key
```bash
echo "YOUR_FIREFLIES_API_KEY" > ~/.openclaw/secrets/fireflies-api-key.txt
```
Get your key from Fireflies dashboard → Settings → Developer Settings.

### 2. Poll for new transcripts (recommended)
```bash
node scripts/poll-new-meetings.js
```
Schedule via OpenClaw cron every 30 minutes. Tracks processed meetings to avoid duplicates.

### 3. Real-time webhooks (optional)
```bash
node scripts/webhook-server.js
```
Runs on port 3142. Expose via Cloudflare Tunnel or ngrok, then paste the URL into Fireflies Settings → Developer Settings → Webhook URL.

Optional webhook secret:
```bash
echo "YOUR_SECRET" > ~/.openclaw/secrets/fireflies-webhook-secret.txt
```

### 4. Fetch a specific transcript
```bash
node scripts/fetch-transcript.js <meetingId>
```

## Output

Transcripts are saved to `memory/meetings/YYYY-MM-DD-<title>.md` with:
- Title, date, duration, participants
- AI summary from Fireflies
- Action items (as checkboxes)
- Key topics and keywords
- Full transcript with speaker labels and timestamps

## Cron Setup

Schedule polling every 30 minutes:
```
Check Fireflies for new meeting transcripts. Run: node <skill-path>/scripts/poll-new-meetings.js — if new meetings found, briefly notify the user with the meeting title(s). If no new meetings, do nothing (NO_REPLY).
```

## Requirements
- Fireflies.ai Pro account ($10/mo) — includes API access
- Node.js 18+
