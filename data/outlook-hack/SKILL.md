---
name: outlook-hack
version: 5.0.0
description: "Your agent reads Outlook email all day. Drafts replies for you. Won't send a single one. 90 days per browser tap."
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "os": ["linux", "darwin"],
        "requires": { "capabilities": ["browser"] },
        "notes":
          {
            "security": "This skill captures a refresh token from Microsoft Teams' localStorage via browser tab sharing, then uses it to call Microsoft Graph API. No API keys or admin approval needed. SENDING IS CODE-DISABLED: the fetch script physically blocks /sendmail, /reply, /replyall, /forward. It reads, searches, and creates drafts only. Drafts land in the user's Drafts folder for manual review and sending. Tokens are stored at ~/.openclaw/credentials/outlook-msal.json with 0600 permissions. Refresh tokens auto-rotate and last 90+ days.",
          },
      },
  }
---

# Outlook Hack

**Your AI agent won't email the CEO at 3am.**

Not because there's a setting. Not because there's a policy. Because the code physically cannot send emails. We removed that capability the way you'd remove a chainsaw from a toddler — completely and without negotiation.

## What It Does

- 📧 Read, search, and bulk-fetch emails across all folders
- 📎 Index all attachments (name, type, size) per message
- 📊 Generate digest summaries with top senders, unread counts, full body text
- ✏️ Create email drafts (lands in Drafts folder — never sends)
- 📅 Access calendar events, 👥 Browse contacts

## Quick Start

### 1. Token Extraction (one-time, ~30 seconds)

Open **Microsoft Teams** (`teams.cloud.microsoft`) in Chrome with the OpenClaw browser relay attached. Then extract the refresh token from localStorage:

```javascript
// Extract the MSAL refresh token from Teams localStorage
const keys = Object.keys(localStorage).filter(k => k.includes('refreshtoken'));
const parsed = JSON.parse(localStorage.getItem(keys[0]));
// parsed.secret is the refresh token
```

Save credentials to `~/.openclaw/credentials/outlook-msal.json`:

```json
{
  "client_id": "5e3ce6c0-2b1f-4285-8d4b-75ee78787346",
  "tenant_id": "<your-tenant-id>",
  "refresh_token": "<the-secret-value>",
  "origin": "https://teams.cloud.microsoft",
  "scope": "https://graph.microsoft.com/.default offline_access",
  "api": "graph",
  "updated_at": "<iso-timestamp>"
}
```

### 2. Verify Access

```bash
node {baseDir}/scripts/outlook-mail-fetch.mjs --test
```

### 3. Bulk Fetch

```bash
# Last 6 months (default)
node {baseDir}/scripts/outlook-mail-fetch.mjs --fetch-all

# Custom range
node {baseDir}/scripts/outlook-mail-fetch.mjs --fetch-all --months 12
```

**Output:** `~/.openclaw/workspace/data/outlook-emails/`
- `raw-emails.jsonl` — full email data (subject, from, to, body text, preview)
- `attachments-index.jsonl` — every attachment per message
- `email-summary.md` — readable digest with stats and per-email summaries

## The Teams Refresh Token Hack

Microsoft killed the classic Outlook web app in 2026. The new Outlook (`outlook.cloud.microsoft`) uses PoP (Proof-of-Possession) tokens that are cryptographically bound to the browser — they cannot be extracted or replayed.

**The workaround:** Microsoft Teams stores a standard MSAL refresh token in `localStorage`. This refresh token can be exchanged for a Graph API access token that includes full mail scopes — no admin consent required, because Teams' first-party client ID already has those permissions pre-authorized.

The trick: the token endpoint requires a `Origin: https://teams.cloud.microsoft` header (SPA client enforcement), which curl/fetch happily provides.

### Why This Works Without Admin Consent

- Teams' client ID (`5e3ce6c0-2b1f-4285-8d4b-75ee78787346`) is a Microsoft first-party app
- First-party apps have pre-authorized access to Graph API scopes
- The refresh token inherits the user's existing session — no new consent prompt
- Your tenant admin never sees a consent request because there isn't one

## Token Lifetime & Refresh

- **Refresh tokens last 90+ days** and auto-rotate on each use
- The script stores the new refresh token after every token exchange
- As long as the script runs at least once every 90 days, **you never touch the browser again**
- Only breaks if: password change, Teams session revoked, or 90+ days of inactivity
- One browser tap per quarter at most. Realistically: once, ever.

## How It Works (Technical)

1. Share your **Teams** tab with OpenClaw via the Browser Relay (one time)
2. The agent reads `localStorage` to extract the MSAL refresh token
3. Token is saved to `~/.openclaw/credentials/outlook-msal.json` (0600 permissions)
4. The `outlook-mail-fetch.mjs` script exchanges the refresh token for a Graph API access token
5. Script makes REST calls to `https://graph.microsoft.com/v1.0/`
6. New refresh token is saved after each exchange — perpetual access

## Architecture Notes

- **Zero external dependencies** — pure Node.js (v18+), no npm packages
- **Send-blocked** — the script has no send/reply/forward functions. They don't exist.
- **Rate-limited** — fetches 50 emails per page with automatic pagination
- **Body text cleaned** — HTML stripped, whitespace normalized, truncated to 3000 chars per email
- **Graph API v1.0** — uses Microsoft's current, supported API (not the deprecated Outlook REST v2.0)

## Sibling Skill: Teams Hack

This skill shares the same MSAL refresh token with [**teams-hack**](https://clawhub.com/globalcaos/teams-hack). **One extraction covers both.** Extract the token once from Teams localStorage → get full email access (this skill) AND chat/channels/search access (Teams Hack).

Both skills read and write to the same credentials file:
```
~/.openclaw/credentials/outlook-msal.json
```

If either skill refreshes the token, the other benefits automatically. The token auto-rotates on every use and lasts 90+ days.

| Skill | What it does | Send-blocked? |
|-------|-------------|---------------|
| **outlook-hack** (this) | Email: read, search, draft, folders, attachments, calendar, contacts | ✅ Cannot send |
| **[teams-hack](https://clawhub.com/globalcaos/teams-hack)** | Chat: read, send, channels, search, presence, org directory | No (chat sending enabled) |

## The Full Stack

Pair with [**teams-hack**](https://clawhub.com/globalcaos/teams-hack) for chat, [**whatsapp-ultimate**](https://clawhub.com/globalcaos/whatsapp-ultimate) for messaging, and [**jarvis-voice**](https://clawhub.com/globalcaos/jarvis-voice) for voice.

👉 **[Clone it. Fork it. Break it. Make it yours.](https://github.com/globalcaos/clawdbot-moltbot-openclaw)**
