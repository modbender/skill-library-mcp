---
name: linkedin-followup
description: Manage LinkedIn outreach leads from Google Sheets — search by name, read live conversation threads, update status, and send contextual follow-up messages. Use after linkedin-dm to move leads through the pipeline (Sent → Replied → Call Scheduled → Demo Done → Closed).
metadata:
  {
    "openclaw": {
      "emoji": "🔁",
      "requires": { "bins": ["gog"] },
      "skills": ["gog"],
      "tags": ["linkedin", "crm", "outreach", "sales", "follow-up"]
    }
  }
---

# linkedin-followup

Manage ongoing LinkedIn conversations from a central Google Sheet CRM. Read threads, draft context-aware replies, send messages, and keep the sheet updated — all from one skill.

---

## Pre-flight Checklist

Before doing anything:

1. **Sheet ID** — Confirm the CRM sheet ID (from `linkedin-dm` setup). Default: `1eEZDGcr1dIbSC782mNkxvD7pVrF8rOFySWCVZ1RXkhM`, tab: `Sheet1` (or `Outreach` if renamed).
2. **gog auth** — Run `gog auth list`. If no tokens: see [gog auth setup](#gog-auth-setup) below.
3. **Browser** — Open the openclaw browser profile and confirm LinkedIn is logged in. Navigate to `/feed/` first.
4. **Mode** — Identify which mode the user wants (see [Modes](#modes)).

---

## Sheet Schema

The CRM sheet uses these columns (A–P):

| Col | Field | Notes |
|---|---|---|
| A | Date Sent | ISO date |
| B | Person Name | Full name |
| C | Role / Title | |
| D | Company | |
| E | LinkedIn URL | Profile URL |
| F | Relationship Hook | Hook used in opener |
| G | Opener Sent | Message 1 text |
| H | Pitch Sent | Message 2 text |
| I | Campaign | Batch label |
| J | Status | Current pipeline stage |
| K | Notes | Context and history |
| L | Last Updated | ISO timestamp |
| M | Last Reply Date | When they last replied |
| N | Last Reply (preview) | First 200 chars of their last reply |
| O | Conversation Log | Full thread (see format below) |
| P | Next Action | What to do next (agent or human) |

**Status values:**
`Sent` → `Replied` → `Call Scheduled` → `Demo Done` → `Follow Up Sent` → `No Response` → `Closed Won` → `Closed Lost`

**Conversation Log format** (column O):
```
[2026-02-13 17:05 SENT] Hey Rishabh, we both had stints at CRED...
[2026-02-13 17:05 SENT] I'm building an AI calling agent...
[2026-02-15 09:30 RECEIVED] Hey! Sounds interesting, tell me more.
[2026-02-15 09:45 SENT] Happy to show you a live demo — are you free Thursday?
```

If columns M–P don't exist yet, add them first:
```bash
gog sheets update <SHEET_ID> "Sheet1!M1:P1" \
  --values-json '[["Last Reply Date","Last Reply (preview)","Conversation Log","Next Action"]]' \
  --input USER_ENTERED
```

---

## Modes

### Mode 1 — Quick Status Update

User says: *"Mark Rishabh as Replied"* or *"Rishabh got back to me, he's interested"*

1. **Find the row** — Search the sheet for the person:
   ```bash
   gog sheets get <SHEET_ID> "Sheet1!A:P" --json
   ```
   Match by name (col B) or LinkedIn URL (col E). Get the row number.

2. **Update status** (col J) and last updated (col L):
   ```bash
   gog sheets update <SHEET_ID> "Sheet1!J<ROW>:L<ROW>" \
     --values-json '[["Replied","","<ISO_TIMESTAMP>"]]' \
     --input USER_ENTERED
   ```

3. If the user provides reply content, also update:
   - Col M: Last Reply Date
   - Col N: Last Reply preview (first 200 chars)
   - Col O: Append to Conversation Log
   - Col P: Next Action (what should happen next)

4. Confirm update to user.

---

### Mode 2 — Full Follow-up (Read + Draft + Send)

User says: *"Follow up with Rishabh"* or *"Send a follow-up to everyone who replied"*

#### Step 1 — Load the person's data from sheet

```bash
gog sheets get <SHEET_ID> "Sheet1!A:P" --json
```
Find their row. Load: Name, Company, Role, LinkedIn URL, Opener Sent, Pitch Sent, Status, Notes, Conversation Log, Next Action.

#### Step 2 — Navigate to their LinkedIn profile

**Always go to feed first** (anti-detection):
```
https://www.linkedin.com/feed/
```
Wait 2–4 seconds. Then navigate to their profile URL (col E).

#### Step 3 — Open message thread and read conversation

Click the **Message** button on their profile. Wait for the conversation bubble to load.

Scrape the full thread with JavaScript:
```javascript
const events = Array.from(document.querySelectorAll('.msg-s-message-list__event'));
const messages = [];
events.forEach(el => {
  const groups = el.querySelectorAll('.msg-s-event-listitem');
  groups.forEach(g => {
    const nameEl = g.closest('.msg-s-message-group')?.querySelector('.msg-s-message-group__profile-link');
    const bodyEl = g.querySelector('.msg-s-event-listitem__body');
    const timeEl = g.closest('.msg-s-message-group')?.querySelector('.msg-s-message-group__timestamp');
    if (bodyEl?.textContent?.trim()) {
      messages.push({
        sender: nameEl?.textContent?.trim() || 'unknown',
        time: timeEl?.textContent?.trim() || '',
        text: bodyEl.textContent.trim()
      });
    }
  });
});
return JSON.stringify(messages);
```

If the thread is empty or not loading, scroll up in the conversation bubble to load older messages.

#### Step 4 — Analyse the conversation

With the full thread loaded + their profile data, determine:

- **What did they say last?** — Identify the most recent message from them.
- **What's the intent?** — Interested / wants more info / asked a question / cold / objection / not interested.
- **What's the right next message?** — See [Response Playbook](#response-playbook) below.
- **Tone** — Mirror their tone (casual vs formal, brief vs detailed).

#### Step 5 — Draft the follow-up

Write a response that:
- **Directly addresses** what they said last
- **Doesn't re-pitch** unless they asked for it
- **Moves toward a specific action** (demo, call, intro, forward to team)
- Is **brief** — 2–4 sentences max
- Feels human, not templated

Show the draft to the user and ask for approval before sending:

> **Draft reply to [Name]:**
> [message]
>
> Send this? (y / edit / skip)

#### Step 6 — Send the message

Same JS evaluate method as linkedin-dm:
```javascript
const active = document.querySelector('.msg-overlay-conversation-bubble--is-active .msg-form__contenteditable');
if (active) { active.focus(); document.execCommand('insertText', false, '<message>'); }
```
Then find and click Send.

#### Step 7 — Update the sheet

After sending:
```bash
gog sheets update <SHEET_ID> "Sheet1!J<ROW>:P<ROW>" \
  --values-json '[["<new_status>","<last_reply_date>","<last_reply_preview>","<updated_conversation_log>","<next_action>","<ISO_TIMESTAMP>"]]' \
  --input USER_ENTERED
```

---

### Mode 3 — Batch Review

User says: *"Who needs a follow-up?"* or *"Check my outreach"*

1. Load all rows from the sheet.
2. Filter by status and time:
   - **`Sent` older than 3 days** → candidate for "No Response" or gentle follow-up
   - **`Replied`** → needs a response
   - **`Follow Up Sent` older than 5 days** → consider "No Response"
   - **`Call Scheduled`** → check if call happened, update status
3. Present a table of candidates:
   ```
   Name             Status    Last Updated    Suggested Action
   Rishabh Nayan    Replied   2026-02-14      Reply to their message
   Shorya Saini     Sent      2026-02-10      Follow-up nudge (4 days)
   Shantam Mohata   Sent      2026-02-13      Too soon (today)
   ```
4. User picks who to action, then enter Mode 2 for each.

---

## Response Playbook

Use these as a guide — always adapt to the actual conversation:

| They said | Intent | Your move |
|---|---|---|
| "Sounds interesting, tell me more" | Curious | Short explanation + offer a specific demo slot |
| "How does it work?" | Exploring | 2-line description + invite to a 15-min call |
| "We already use [X]" | Objection | Acknowledge, explain differentiation, offer demo |
| "Send me more details" | Soft interest | Share a Loom/deck/link + follow up in 2 days |
| "Not relevant right now" | Soft no | Respect it, leave door open: "No worries, I'll ping you in a few months" |
| "Who else is using it?" | Trust-building | Share a relevant use case, offer intro to a user |
| [No reply in 4 days] | Silence | Light nudge: "Hey [Name], just checking — any thoughts?" |
| [No reply in 8 days] | Cold | One final message, then mark No Response |

---

## Anti-Detection Rules

Same rules as linkedin-dm:
- Always go to `/feed/` before navigating to a profile
- Wait 2–4 seconds after loading feed
- Max **15–20 messages per session** (combined sends across follow-ups)
- Space out follow-ups: don't ping multiple people in rapid succession
- Natural delays between typing and sending (1–2 seconds)

---

## gog Auth Setup

If `gog auth list` returns empty, the user needs to set up Google OAuth credentials:

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project (or select existing)
3. Enable **Google Sheets API** (APIs & Services → Library)
4. Create OAuth credentials: APIs & Services → Credentials → Create → OAuth client ID → Desktop App
5. Download `client_secret_<id>.json`
6. Run:
   ```bash
   gog auth credentials set /path/to/client_secret.json
   gog auth add your@gmail.com --services sheets
   ```
7. A browser window will open — log in and grant access
8. Verify: `gog auth list`

**Fallback (no gog):** All sheet reads/writes can be done manually via browser — open the sheet in the openclaw browser and update cells directly. Less automated but functional.

---

## Session Limits

- Max 15–20 follow-up messages per session
- Log every send immediately to sheet (don't batch)
- If gog is unavailable, log to local `linkedin_followup_log.json` and sync to sheet next session
