---
name: scrask-bot
version: 3.0.0
description: >
  When the user sends a screenshot via Telegram, parse it using Gemini (fast, default)
  with automatic Claude fallback when confidence is low. Saves results to Google Calendar
  (events) or Google Tasks (reminders and tasks). Saves silently if confidence is high;
  asks for confirmation if uncertain.
author: your-name
metadata:
  openclaw:
    emoji: "🦞"
    primaryEnv: GEMINI_API_KEY
    requires:
      env:
        - GOOGLE_CREDENTIALS
        - GEMINI_API_KEY         # required for auto and gemini modes
        # - ANTHROPIC_API_KEY   # optional — enables Claude fallback in auto mode
      bins:
        - python3
    config:
      vision_provider:
        type: string
        description: >
          Vision model provider.
          'auto' = Gemini first, Claude fallback if any item confidence < fallback_threshold.
          'gemini' = Gemini only. 'claude' = Claude only.
        default: auto
      fallback_threshold:
        type: number
        description: "Confidence floor for auto mode. If any item is below this, Claude reruns the parse."
        default: 0.60
      timezone:
        type: string
        description: "User's IANA timezone. Used when none is detected in the screenshot."
        default: "UTC"
      confidence_threshold:
        type: number
        description: "0.0–1.0. Items below this score ask for confirmation. Items above save silently."
        default: 0.75
      reminder_minutes_before:
        type: integer
        description: "Popup reminder lead time in minutes for Google Calendar events."
        default: 30
---

# Scrask Bot

## Overview

This skill activates when the user sends a screenshot via **Telegram**.
It uses vision AI to extract actionable information from the image, then:

- **High confidence (≥ 0.75):** Saves immediately and replies with a brief confirmation.
- **Low confidence (< 0.75):** Shows a structured preview in Telegram and asks for confirmation before saving.

**Provider behaviour (auto mode, default):**

| Step | What happens |
|---|---|
| 1 | Gemini 2.0 Flash parses the screenshot (fast, cheap) |
| 2 | If any item confidence < 0.60, Claude Opus reruns the parse |
| 3 | Whichever provider scores higher average confidence wins |
| 4 | Output includes `provider`, `fallback_triggered`, and confidence delta |

Set `vision_provider` to `"claude"` or `"gemini"` to lock a specific provider.

**Output destinations (AI-decided by content type):**

| Detected type | Destination |
|---|---|
| Event (has date+time, venue, or invite link) | Google Calendar |
| Reminder (deadline, due date, personal action) | Google Tasks (with due date) |
| Task (no date, pure action item) | Google Tasks (no due date) |

---

## Trigger Conditions

Activate when:
1. The user sends a message in Telegram that contains an **image attachment**
2. The image appears to be a **screenshot** — not a photo of a person, place, or physical object
3. No other skill has already claimed the image

Do not activate for:
- Photos of people, places, food, scenery
- Screenshots of code, errors, or UI bugs (leave for other skills)
- Images the user explicitly asks to edit, describe, or analyze for another purpose

---

## Step-by-Step Instructions

### Step 1: Acknowledge Immediately

Reply in Telegram right away so the user knows the skill is working:

> "📸 Got it — analyzing your screenshot..."

Do not make the user wait silently.

---

### Step 2: Run the Parser

```bash
python3 ~/.openclaw/skills/scrask-bot/scripts/scrask_bot.py \
  --image-path "<path-to-temp-image>" \
  --provider "$CONFIG_VISION_PROVIDER" \
  --timezone "$CONFIG_TIMEZONE" \
  --google-credentials "$GOOGLE_CREDENTIALS"

The script auto-resolves the API key from ANTHROPIC_API_KEY or GEMINI_API_KEY
depending on the provider — no need to pass it explicitly.
```

The script returns a JSON object with:
- `success` — whether parsing worked
- `no_actionable_content` — true if nothing found
- `results[]` — one entry per detected item, each with `confidence`, `type`, `destination`, `needs_confirmation`, `action_taken`
- `telegram_reply` — the pre-formatted message to send back to the user

---

### Step 3: Handle the Output

**If `no_actionable_content` is true:**
Reply: "🤷 I couldn't find any event, reminder, or task info in that screenshot. Could you describe what you'd like to add?"

**If `success` is true:**
Send the `telegram_reply` value directly back to the user in Telegram. The script has already:
- Saved high-confidence items silently
- Formatted confirmation prompts for low-confidence items

Do not rephrase or reformat the `telegram_reply` — send it as-is.

---

### Step 4: Handle Confirmation Responses

If the script returned items with `needs_confirmation: true`, wait for the user's reply.

**"yes" or "save" or "add":**
Re-run the script for that specific item with confirmed=true, or use the `calendar_create` / `tasks_create` tools directly with the extracted fields.

**"edit":**
Ask what to change, update the relevant field, then save.

**"skip" or "no":**
Reply: "Got it, skipped ✓"

---

### Step 5: Confirm Saves

For items saved silently (high confidence), the `telegram_reply` from the script already contains the confirmation message. Examples of what the user will see:

- `📅 Added to Calendar: **Team Standup** — 2026-03-01 at 09:00`
- `🔔 Added to Tasks: **Pay electricity bill** (due 2026-02-28)`
- `✅ Added to Tasks: **Review PR for Arjun**`

---

## Edge Cases

| Scenario | Behavior |
|---|---|
| Screenshot is in Hindi, Tamil, or another language | Extract and translate silently; save title in English |
| Recurring event ("every Monday") | Set RRULE on the calendar event; mention it in the reply |
| Date has already passed | Flag in the reply: "⚠️ This date has already passed (Feb 10). Save anyway?" |
| Multiple items in one screenshot | Process each independently; confirm per item if needed |
| Screenshot of someone's calendar | Detect `already_in_calendar_hint`; reply: "Looks like this event is already in your calendar 🗓️" |
| Google API auth failure | Reply with the specific error and suggest re-checking GOOGLE_CREDENTIALS |
| Zoom/Meet link found | Add to Calendar as both location and description |

---

## Configuration

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

---

## Permissions Required

- `image:read` — to access the screenshot from Telegram
- `network:outbound` — to call Anthropic API and Google APIs
- `telegram:reply` — to send confirmation messages back to the user
