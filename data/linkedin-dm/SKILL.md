---
name: linkedin-dm
description: Send personalized LinkedIn direct messages to a list of existing 1st-degree connections via browser automation. Use when the user wants to message LinkedIn connections with AI-personalized outreach — e.g. nurturing leads, following up after events, reconnecting with contacts, or announcing something. Takes a data file (CSV/TSV) or plain list with connection names and companies, asks for outreach context/goal, generates a tailored message per person, and sends each one via browser automation. Handles message compose flow, character limits, and incremental status tracking.
---

# LinkedIn DM

Sends personalized LinkedIn messages to existing 1st-degree connections. Each message has:
- A **personalized opening** unique to each person (based on their profile + relationship to the sender)
- A **consistent product/pitch section** confirmed once by the user and reused for all messages

---

## ⚠️ Pre-flight Checklist — Confirm Before Starting

### 1. Connection List
Ask the user for their data file or list. Must include (or be added):
- **Person Name** — full name
- **Company/Role** — their current company or role
- **LinkedIn URL** — optional but helpful
- **Message Status** — column for tracking (add if missing)

If only a plain list is provided, offer to convert to TSV.

### 2. Read Sender's LinkedIn Profile (mandatory)
Before writing any messages, navigate to `/in/me/` and read the sender's profile:
- **Name** and **current role/company**
- **Career history** — companies, roles, years
- **Education** — college, degree, batch years
- **Location**

Store these facts. They are used to identify relationship hooks with each connection.

### 3. Confirm the Pitch (once, upfront)
Ask the user:
> *"What's your pitch / product message? This will be the consistent part of every message. Describe it in 1–2 sentences."*

Then draft a polished pitch section (2–4 sentences max, punchy and clear). Show it to the user and get explicit approval. **Do not start sending until the pitch is confirmed.**

Example prompt: *"Here's the pitch I'll use for everyone — confirm or edit:*
> *'I'm building an AI calling agent — you give it a phone number + context, and it handles the call end-to-end. Think customer follow-ups, research calls, vendor coordination — anything phone-based that eats into your day. Happy to show you a demo if this sounds useful.'"*

### 4. Browser Setup
- **Option A — Chrome Browser Relay** (`profile="chrome"`): extension attached to LinkedIn tab (badge ON) — recommended for flagged accounts
- **Option B — OpenClaw Isolated Browser** (`profile="openclaw"`): openclaw-managed Chrome, LinkedIn logged in

### 5. CRM Sheet
Ask the user for a Google Sheet ID/URL to log outreach results. If they don't have one, offer to set one up (create tab + write headers). Confirm `gog` is authenticated (`gog auth list`).

If the user skips this, fall back to local `linkedin_dm_progress.json` but remind them the follow-up skill needs the sheet.

### 6. Ready Check
Only proceed once:
- ✅ List is ready
- ✅ Sender profile has been read
- ✅ Pitch is confirmed by user
- ✅ Browser is open with LinkedIn logged in
- ✅ Sheet ID confirmed (or sidecar fallback acknowledged)

---

## Relationship Analysis (per person)

Before writing a message, compare the connection's profile against the sender's profile to find the strongest hook. Use this hierarchy — pick the highest that applies:

| Priority | Hook | Example opener |
|---|---|---|
| 1 | **Same company** (current or past) | "You and I both spent time at CRED…" |
| 2 | **Same college + overlapping years** | "Fellow BITS Goa 2018 batch here…" |
| 3 | **Same college** (different years) | "BITS connect here — saw your journey from…" |
| 4 | **Same industry/function** | "Both been in fintech/product for a while…" |
| 5 | **Mutual connection** | "We're both connected to [Name]…" |
| 6 | **Their work context** (no personal hook) | "Seen what you've built at [Company]…" |

Combine the hook with a line about **their current work** to show you know what they do.

---

## Message Structure

Send as **two separate messages** per person, back to back:

**Message 1 — Personalized opener** (unique per person)
```
[Relationship hook — 1 sentence]
[Acknowledgement of their work/role — 1 sentence]
```
Target: 100–180 chars. Feels like a genuine reach-out from someone who knows them.

**Message 2 — Pitch** (identical for everyone, confirmed upfront)
```
[Product description — 1–2 sentences]
[Relevant use case for their role — 1 sentence]
[Soft CTA — 1 sentence]
```
Target: 150–250 chars. Clear, punchy, no filler.

**Why two messages?**
- Opener lands first — they see it before the pitch, feels more personal
- Pitch is clearly a separate thought, not buried at the end
- Mirrors how a human would actually message a connection

**Fallback:** If sending two messages is technically difficult (e.g. bubble re-focusing issues), use `Shift+Enter` twice between the opener and pitch to create a paragraph break within a single message.

**Do not:**
- Open with "I hope you're well" or "I came across your profile"
- Use the same opening for multiple people
- Change the pitch section per person

---

## Batch Preview Before Sending

Generate messages for the **entire list first**. Present them in a table:

| Name | Company | Relationship Hook Used | Message Preview |
|---|---|---|---|
| Shorya Saini | Razorpay | Same BITS batch | Hey Shorya, BITS Goa 2018 batch… |

Get user approval on the full batch before opening the browser. Allow edits per row.

---

## Sending Flow (Per Person)

1. **Navigate to `/feed/`** — mandatory, no exceptions, no skipping
2. **Wait 3–5 seconds**
3. **Search connections** at `linkedin.com/mynetwork/invite-connect/connections/` — type name in "Search by name"
4. **Handle results:**
   - 1 match → confirm name + headline → click to open profile
   - Multiple matches → show user, ask which one
   - 0 matches → mark `Not a Connection`, skip
5. **Read their profile** if not already done (for personalisation)
6. **Click Message button** on their profile
7. **Send Message 1** — personalized opener only, send it
8. **Send Message 2** — pitch only, send it immediately after
9. **Confirm both delivered**
10. **Log to CRM sheet** — append row via `gog sheets append` with all fields (see CRM Tracking section)

See `references/browser-workflow.md` for exact browser automation steps.

---

## Status Values

| Status | Meaning |
|---|---|
| `Sent` | Message delivered this session |
| `Already Messaged` | Recent conversation exists — skip |
| `Not a Connection` | No Message button or not in connections search |
| `Profile Not Found` | Could not identify the right person |
| `Skipped` | User chose to skip |
| `Failed` | Browser error — retry next session |

---

## Anti-Detection Rules

- `/feed/` before **every single profile** — non-negotiable
- 3–5 second wait after feed loads
- Max **15–20 messages per session**
- Stop immediately if LinkedIn warns about messaging rate — tell the user

---

## CRM Tracking — Google Sheet

After each message is sent, append a row to a Google Sheet. This sheet is the source of truth for all outreach — current session and future follow-up.

### Sheet Setup

Ask the user for a Google Sheet ID or URL at the start of the session (or offer to create a new one). The sheet should have a tab named `Outreach` with these columns:

| Col | Field | Notes |
|---|---|---|
| A | Date Sent | ISO date, e.g. `2026-02-13` |
| B | Person Name | Full name |
| C | Role / Title | Their current headline from LinkedIn |
| D | Company | Current company |
| E | LinkedIn URL | Profile URL |
| F | Relationship Hook | What hook was used (e.g. "Same batch BITS Goa 2018", "Both at CRED 2022–23") |
| G | Opener Sent | Exact text of Message 1 |
| H | Pitch Sent | Exact text of Message 2 |
| I | Campaign | Short label for this batch (e.g. "AI Calling - Feb 2026") |
| J | Status | Always `Sent` when first logged — updated by follow-up skill |
| K | Notes | Anything notable (prior conversation, context, mutual connection used) |
| L | Last Updated | Timestamp of last status change |

**Column I (Status) lifecycle** — only `Sent` is written by this skill. The follow-up skill will update to:
`Replied` · `Call Scheduled` · `Demo Done` · `Follow Up Sent` · `No Response` · `Closed Won` · `Closed Lost`

### Appending a Row

After each message pair is sent, run:

```bash
gog sheets append <SHEET_ID> "Outreach!A:L" \
  --values-json '[["<date>","<name>","<role>","<company>","<url>","<hook>","<opener>","<pitch>","<campaign>","Sent","<notes>","<timestamp>"]]' \
  --insert INSERT_ROWS
```

### First-Time Setup

If no sheet exists yet, tell the user:
> "I'll need a Google Sheet to track outreach. Share an existing sheet ID/URL, or I can create one with the right columns."

To create a new sheet, use Drive (or ask user to create one and share the ID). Then write the header row:

```bash
gog sheets update <SHEET_ID> "Outreach!A1:L1" \
  --values-json '[["Date Sent","Person Name","Role / Title","Company","LinkedIn URL","Relationship Hook","Opener Sent","Pitch Sent","Campaign","Status","Notes","Last Updated"]]' \
  --input USER_ENTERED
```

### Local Sidecar (fallback)

If Google Sheets is not set up, fall back to a local `linkedin_dm_progress.json`:
```json
{
  "campaign": "AI Calling - Feb 2026",
  "pitch": "confirmed pitch text",
  "rows": [
    {
      "date": "2026-02-13",
      "name": "Shorya Saini",
      "role": "Senior Analytics Specialist",
      "company": "Razorpay",
      "url": "https://linkedin.com/in/shorya-saini",
      "hook": "Same batch BITS Goa 2018",
      "opener": "Hey Shorya...",
      "pitch": "I'm building...",
      "status": "Sent",
      "notes": ""
    }
  ]
}
```
