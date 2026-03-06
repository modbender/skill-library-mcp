# 🦞 Scrask Bot

**OpenClaw Skill** — Send a screenshot to Telegram. Scrask saves it to Google Calendar or Tasks automatically.

**Scrask** = Screenshot + Task

---

## What It Does

1. You take a screenshot on your phone (WhatsApp forward, email, social post, chat)
2. You send it to your OpenClaw bot on Telegram
3. Scrask parses it using vision AI
4. It saves it to the right place — no input needed from you

| Detected type | Destination |
|---|---|
| Event (date + time / venue / invite link) | Google Calendar |
| Reminder (deadline, due date) | Google Tasks (with due date) |
| Task (no date, action item) | Google Tasks |

High confidence (≥ 0.75) → saves silently, confirms in chat  
Low confidence → shows preview, asks before saving

---

## Provider Strategy (v3)

By default, Scrask uses **auto mode**: Gemini first, Claude fallback.

```
Screenshot arrives
      ↓
  Gemini 2.0 Flash (fast, cheap)
      ↓
  Any item confidence < 0.60?
  ├── No  → Done ✓
  └── Yes → Claude Opus reruns the parse
              ↓
          Claude avg confidence > Gemini + 0.05?
          ├── Yes → Use Claude result ✓
          └── No  → Gemini result was fine, keep it ✓
```

You can override this per-use with `--provider claude` or `--provider gemini`.

**What you get in the output:**

```json
{
  "provider": "claude",
  "fallback_triggered": true,
  "gemini_avg_confidence": 0.51,
  "claude_avg_confidence": 0.82,
  "confidence_gain": 0.31
}
```

---

## Installation

```bash
# 1. Copy to OpenClaw skills directory
cp -r scrask-bot ~/.openclaw/skills/

# 2. Install dependencies
pip install -r ~/.openclaw/skills/scrask-bot/scripts/requirements.txt

# 3. Set up Google credentials
# → Google Cloud Console → create service account
# → Enable Calendar API + Tasks API
# → Download JSON key → save as ~/.openclaw/google-creds.json
# → Share your Google Calendar with the service account email

# 4. Add to openclaw.json (see below)

# 5. Restart OpenClaw
openclaw restart
```

### openclaw.json config

```json
{
  "skills": {
    "entries": {
      "scrask-bot": {
        "enabled": true,
        "env": {
          "GEMINI_API_KEY": "AIza-your-gemini-key",
          "ANTHROPIC_API_KEY": "sk-ant-your-key-here",
          "GOOGLE_CREDENTIALS": "/home/user/.openclaw/google-creds.json"
        },
        "config": {
          "vision_provider": "auto",
          "fallback_threshold": 0.60,
          "timezone": "Asia/Kolkata",
          "confidence_threshold": 0.75,
          "reminder_minutes_before": 30
        }
      }
    }
  }
}
```

> `ANTHROPIC_API_KEY` is optional in auto mode — if missing, Scrask runs Gemini only with no fallback.

---

## Testing

```bash
# Auto mode (Gemini + Claude fallback)
python3 scripts/scrask_bot.py \
  --image-path /path/to/screenshot.png \
  --provider auto \
  --timezone "Asia/Kolkata" \
  --dry-run

# Force a specific provider
python3 scripts/scrask_bot.py \
  --image-path /path/to/screenshot.png \
  --provider gemini \
  --timezone "Asia/Kolkata" \
  --dry-run
```

---

## File Structure

```
scrask-bot/
├── SKILL.md                  # OpenClaw skill instructions
├── README.md                 # This file
└── scripts/
    ├── scrask_bot.py         # Core parser — vision AI + Google API
    └── requirements.txt      # Python dependencies
```

---

## Built by

Sandip — [github.com/your-handle](https://github.com/your-handle)

---

## License

MIT
