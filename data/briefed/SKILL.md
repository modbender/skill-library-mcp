---
name: briefed
description: Set up and run a personal AI newsletter intelligence system called Briefed. Fetches Gmail newsletters daily, uses Claude Haiku to extract article summaries, and serves a polished local web reader app with voting, notes, and interest tracking. Use when a user asks to set up a newsletter reader, daily digest, inbox intelligence tool, or newsletter summariser with OpenClaw.
metadata:
  openclaw:
    requires:
      env:
        - BRIEFED_GMAIL_CLIENT_SECRET
      optionalEnv:
        - BRIEFED_GMAIL_TOKEN_FILE
        - NEWSLETTER_ACCOUNT
      files:
        - ~/.openclaw/workspace/newsletter-inbox.json
        - ~/.openclaw/workspace/newsletter-today.json
        - ~/.openclaw/workspace/newsletter-interests.json
        - ~/.openclaw/workspace/newsletter-notes.json
        - ~/.openclaw/workspace/reading-list.md
---

# Briefed

A daily newsletter digest pipeline + local web reader. Gmail → Haiku summaries → web app → notification ping.

## Architecture

```
[Gmail]
   ↓  pre-fetch.py (fetches, filters, extracts compact metadata)
[newsletter-inbox.json]
   ↓  Haiku cron agent (reads compact JSON, writes AI summaries)
[newsletter-today.json]
   ↓  fetch-bodies.py (adds full HTML email bodies)
[newsletter-today.json + bodies]
   ↓  Express web reader (default port 3001)
[Notification ping → user opens reader]
```

**Why split fetch/summarise?** Raw Gmail API JSON overflows Haiku's context. Python handles data wrangling; Haiku handles cognition.

## Security & Scope

- Gmail access is **read-only** (`gmail.readonly`).
- OAuth token is stored locally at `~/.openclaw/workspace/briefed-gmail-token.json` (or `BRIEFED_GMAIL_TOKEN_FILE`).
- The workflow should only read/write the following workspace files:
  - `newsletter-inbox.json`
  - `newsletter-today.json`
  - `newsletter-interests.json`
  - `newsletter-notes.json`
  - `reading-list.md`
- Do not send newsletter content to external endpoints other than the configured model provider and user-selected notification channel.

## Prerequisites

- Python 3.9+
- Python deps for Gmail API (`google-api-python-client`, `google-auth`, `google-auth-oauthlib`)
- A Google OAuth Desktop client JSON file (for Gmail read-only auth)
- Node.js ≥18 (for the reader web app)
- `claude-haiku-4-5` on the OpenClaw models allowlist
- A notification channel configured in OpenClaw (Telegram, Discord, etc.)

## Setup

### 1. Install Python dependencies

```bash
cd ~/.openclaw/workspace/briefed
python3 -m pip install -r scripts/requirements.txt
```

### 2. Configure Gmail OAuth

Create a Google Cloud OAuth Desktop app and download the client JSON, then set:

```bash
export BRIEFED_GMAIL_CLIENT_SECRET=~/client_secret.json
```

On first script run, Briefed opens a browser OAuth flow and stores a reusable token at:

```bash
~/.openclaw/workspace/briefed-gmail-token.json
```

### 3. Deploy the reader app

```bash
# Copy the reader to the workspace
cp -r assets/reader/ ~/.openclaw/workspace/briefed/
cd ~/.openclaw/workspace/briefed
npm install
```

### 4. Configure Gmail token paths (optional)

Defaults (works for most users):

- Token file: `~/.openclaw/workspace/briefed-gmail-token.json`
- Client secret: `~/client_secret.json`

Override via env vars if needed:

```bash
export BRIEFED_GMAIL_CLIENT_SECRET=~/path/to/client_secret.json
export BRIEFED_GMAIL_TOKEN_FILE=~/.openclaw/workspace/briefed-gmail-token.json
```

### 5. Configure interests

Create `~/.openclaw/workspace/newsletter-interests.json` (or let it be auto-created on first run):

```json
{
  "version": 1,
  "topics": { "ai": 0.9, "startups": 0.8, "design": 0.75 },
  "signals": [],
  "sources": {}
}
```

### 6. Start the reader

Run manually if you prefer no persistence. LaunchAgent is optional convenience for auto-start.

```bash
# Quick test
node ~/.openclaw/workspace/briefed/server.js

# Persistent — create ~/Library/LaunchAgents/ai.openclaw.briefed.plist
```

LaunchAgent plist template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.openclaw.briefed</string>
  <key>ProgramArguments</key><array>
    <string>/usr/local/bin/node</string>
    <string>/Users/YOUR_USER/.openclaw/workspace/briefed/server.js</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>BRIEFED_GMAIL_CLIENT_SECRET</key><string>/Users/YOUR_USER/client_secret.json</string>
    <key>BRIEFED_GMAIL_TOKEN_FILE</key><string>/Users/YOUR_USER/.openclaw/workspace/briefed-gmail-token.json</string>
  </dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>WorkingDirectory</key><string>/Users/YOUR_USER/.openclaw/workspace/briefed</string>
  <key>StandardOutPath</key><string>/tmp/briefed.log</string>
  <key>StandardErrorPath</key><string>/tmp/briefed.log</string>
</dict></plist>
```

```bash
launchctl load ~/Library/LaunchAgents/ai.openclaw.briefed.plist
```

### 7. Create the daily cron job

Use the OpenClaw cron tool with this agent prompt (fill in the placeholders):

```
Run my daily newsletter digest. Follow these steps exactly:

## Step 1 — Pre-fetch emails
Run: python3 ~/.openclaw/workspace/briefed/scripts/pre-fetch.py

## Step 2 — Read the compact inbox
Read: ~/.openclaw/workspace/newsletter-inbox.json

## Step 3 — Write newsletter-today.json with AI summaries
For each newsletter, write to **only** this file: ~/.openclaw/workspace/newsletter-today.json.
Do not modify any other files in this step.
Use the snippet field to write real summaries — do NOT just repeat the subject line.
Score by interest: (adjust topics and weights to match your interests)
  ai/ml=0.9, startups=0.85, design=0.8, finance=0.75, general=0.6

Schema per story:
{ "id", "rank", "source", "subject", "headline", "summary", "bullets": [], "threadId", "gmailUrl", "score", "body": "" }

## Step 4 — Fetch HTML bodies
Run: python3 ~/.openclaw/workspace/briefed/scripts/fetch-bodies.py

## Step 5 — Send notification
Send (via your configured channel):
"📬 Today's digest is ready — <N> stories waiting.\n→ http://YOUR_HOST:3001"

## Step 6 — Final reply
📬 *Briefed — [DD Mon YYYY]* · <N> stories
*<rank>. <Source>* — <Headline>
<One sentence summary>
(repeat for all stories)
_Open the reader → http://YOUR_HOST:3001_
```

Before enabling cron, run this once manually to complete OAuth in a browser:

```bash
python3 ~/.openclaw/workspace/briefed/scripts/pre-fetch.py
```

Cron schedule: `0 7 * * *` (7am daily), model: `anthropic/claude-haiku-4-5`, delivery: `announce`.

## Data Files

All data files live in `~/.openclaw/workspace/`:

| File | Purpose |
|------|---------|
| `newsletter-inbox.json` | Compact pre-fetched email metadata (ephemeral) |
| `newsletter-today.json` | Today's stories with summaries + HTML bodies |
| `newsletter-interests.json` | Topic weights + vote/open signals |
| `newsletter-notes.json` | Per-story user notes |
| `reading-list.md` | Saved/bookmarked stories |

## Reader API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/today` | GET | All stories (bodies stripped) |
| `/api/story/:id` | GET | Single story with full HTML body |
| `/api/vote` | POST | `{ storyId, vote: "up"\|"down"\|"open" }` |
| `/api/save` | POST | `{ storyId }` — adds to reading-list.md |
| `/api/note` | POST | `{ storyId, note }` |
| `/api/notes` | GET | All notes |

## Filtering Transactional Email

`scripts/pre-fetch.py` has two tunable lists near the top:
- `SKIP_SUBJECT_PATTERNS` — subject substrings that flag an email as transactional
- `SKIP_SENDERS` — sender names that are always transactional (e.g. banks, shops)

Tune these when transactional emails slip through.

## Branding

The reader shows "Briefed" with a blue "B" logo by default. To customise, edit `public/index.html` and `public/icon.svg`.
