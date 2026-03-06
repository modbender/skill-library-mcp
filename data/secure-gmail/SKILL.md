---
name: secure-gmail
description: Secure Gmail skill using Composio brokered OAuth — no raw tokens stored locally. Reads, searches, and drafts emails with least-privilege enforcement. Blocks send and delete at the Composio API gateway level, not just in code. Use when user asks to check inbox, find specific emails by sender or subject, summarize unread threads, or create reply drafts without sending. Requires COMPOSIO_API_KEY in .env and Gmail connected at app.composio.dev. Do NOT use for sending emails — use a send-confirmed skill with human approval instead.
metadata:
  moltbot:
    requires:
      bins: ["python3"]
      env: ["COMPOSIO_API_KEY"]
---

# Secure Gmail Skill (Composio-backed)

Provides read-only + draft Gmail access through Composio's managed authentication layer. OAuth tokens never touch your local filesystem or agent memory — Composio brokers every API call on its backend.

## When to Use This Skill

Activate this skill when the user says any of the following:

- "Check my emails" / "What's in my inbox?"
- "Did [person] reply?" / "Find emails from [sender]"
- "Summarize unread emails from today/this week"
- "Draft a reply to [email]" — creates draft, does NOT send
- "What did [person] send me about [topic]?"
- "Search for emails about [subject]"

Do NOT activate for:
- "Send an email" → use a human-approved send skill
- "Delete emails" → blocked at API level, will fail gracefully
- "Access Google Drive or Calendar" → use /gog or /google-drive skill

## Prerequisites (must be done before first use)

1. Composio account at app.composio.dev (free tier works)
2. Gmail connected under Connected Accounts in Composio dashboard
3. COMPOSIO_API_KEY set in ~/clawd/skills/secure-gmail/.env
4. Python packages installed: `pip install python-dotenv composio`

If COMPOSIO_API_KEY is missing the skill will exit with:
`Error: COMPOSIO_API_KEY not found in environment`
Direct the user to add it to the .env file before retrying.

## Exact Commands

### Fetch recent emails
```bash
cd ~/clawd/skills/secure-gmail && python3 agent.py "fetch last 10 emails"
```

### Search by sender
```bash
python3 agent.py "find emails from sarah@example.com this week"
```

### Search by subject keyword
```bash
python3 agent.py "find emails about quarterly budget"
```

### Read a specific email
```bash
python3 agent.py "read email with id MESSAGE_ID_HERE"
```

### Create a draft reply
```bash
python3 agent.py "draft a reply to the last email from John saying I will review by Friday"
```

## What Each Action Does Internally

| User Request | Composio Action Called | Result |
|---|---|---|
| Check inbox | GMAIL_FETCH_EMAILS | Returns last N emails with sender, subject, date |
| Find email | GMAIL_SEARCH_MESSAGES | Returns matching threads |
| Read email | GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID | Returns full email body |
| Draft reply | GMAIL_CREATE_EMAIL_DRAFT | Creates draft, confirms saved not sent |
| Profile check | GMAIL_GET_PROFILE | Returns authenticated email address |

## Blocked Actions (Composio rejects these at gateway)

The following are not in the allowed list and are rejected before reaching Gmail — even if the agent tries to call them due to hallucination or ambiguous instructions:

- GMAIL_SEND_EMAIL
- GMAIL_DELETE_MESSAGE
- GMAIL_MODIFY_LABELS
- GMAIL_EMPTY_TRASH

If a user asks to send or delete, respond:
"This skill is read and draft only. To send, please review the draft in Gmail and send it yourself, or install a send-enabled skill with human approval confirmation."

## Output Format

The agent returns JSON. Parse and present it like this:

For email list:
```
📬 Found 5 emails:
1. From: sarah@co.com | Subject: Q4 Budget | Date: Mar 1
2. From: mike@co.com  | Subject: Meeting Notes | Date: Feb 28
...
```

For drafts:
```
✅ Draft saved (not sent):
To: john@example.com
Subject: Re: Project Update
Preview: "Hi John, I'll review this by Friday..."
Review it at: mail.google.com/mail/#drafts
```

## Error Handling

| Error | Cause | Fix |
|---|---|---|
| `COMPOSIO_API_KEY not found` | Missing .env key | Add key to .env file |
| `Gmail not connected` | OAuth not completed | Go to app.composio.dev → Connected Accounts |
| `Token expired` | OAuth needs refresh | Reconnect Gmail in Composio dashboard |
| `Action not permitted` | Tried blocked action | Expected — tell user it's read/draft only |
| `Rate limit exceeded` | Too many requests | Wait 60 seconds and retry |

## Security Architecture

This skill uses Composio's brokered authentication model:

1. User connects Gmail via OAuth at app.composio.dev
2. Composio stores access_token and refresh_token in encrypted vault
3. OpenClaw receives only a connected_account_id reference
4. Every API call goes: OpenClaw → Composio → Gmail
5. Raw credentials never enter agent memory or local filesystem
6. Every call is logged in Composio dashboard with timestamp and action
7. Access revocable instantly via Composio dashboard kill switch

This protects against three attack vectors:
- Prompt injection stealing .env credentials (token not local)
- Context window leaks exposing OAuth tokens (token not in memory)
- Malicious skills reading credential files (nothing to read)

## Audit Your Agent

After running, check app.composio.dev → Logs to see:
- Exact timestamp of every Gmail action
- Which action was called (fetch, search, draft)
- Whether it succeeded or was blocked
- No action goes unrecorded

---
name: secure-gmail
description: Read emails, search inbox, and create drafts using Composio managed authentication. Use when user asks to check emails, read mail, search inbox, or draft replies. CANNOT send or delete emails (least privilege enforced by Composio).
metadata:
  moltbot:
    requires:
      bins: ["python3"]
      env: ["COMPOSIO_API_KEY"]
---

# Secure Gmail Skill

Gmail access via Composio brokered auth.
The agent never sees your raw OAuth tokens.
