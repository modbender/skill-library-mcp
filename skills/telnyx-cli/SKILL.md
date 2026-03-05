---
name: telnyx-cli
description: "Telnyx API integration for Clawdbot. Send SMS/email/WhatsApp messages, manage phone numbers, query call logs, debug webhooks, and access your Telnyx account. Use when you need to interact with Telnyx APIs via CLI, manage phone numbers and messaging, debug webhooks, or access account data."
metadata:
  clawdbot:
    emoji: "📞"
    requires:
      bins: ["telnyx"]
      env: []
    notes: "API key stored in ~/.config/telnyx/config.json after 'telnyx auth setup'"
---

# Telnyx CLI

Telnyx API integration for Clawdbot: messaging, phone numbers, webhooks, and account management.

## Setup

### 1. Install CLI

```bash
npm install -g @telnyx/api-cli
```

### 2. Configure API Key

```bash
telnyx auth setup
```

Paste your API key from: https://portal.telnyx.com/#/app/api-keys

Saves to `~/.config/telnyx/config.json` (persistent).

### 3. Verify

```bash
telnyx number list
```

## Commands

| Category | Command | Description |
|----------|---------|-------------|
| **Messaging** | `telnyx message send` | Send SMS/email/WhatsApp |
| | `telnyx message list` | List messages |
| | `telnyx message get` | Get message status |
| **Phone Numbers** | `telnyx number list` | Your phone numbers |
| | `telnyx number search` | Search available numbers |
| | `telnyx number buy` | Purchase a number |
| | `telnyx number release` | Release a number |
| **Calls** | `telnyx call list` | View calls |
| | `telnyx call get` | Get call details |
| **Webhooks** | `telnyx webhook list` | List webhooks |
| | `telnyx debugger list` | View webhook events |
| | `telnyx debugger retry` | Retry failed webhooks |
| **Account** | `telnyx account get` | Account info & balance |

## Usage

### Messaging

```bash
# Send SMS
telnyx message send --from +15551234567 --to +15559876543 --text "Hello!"

# List messages
telnyx message list

# Get status
telnyx message get MESSAGE_ID
```

### Phone Numbers

```bash
# List
telnyx number list

# Search
telnyx number search --country US --npa 415

# Buy
telnyx number buy --number "+15551234567"

# Release
telnyx number release "+15551234567"
```

### Webhooks & Debugging

```bash
# List webhooks
telnyx webhook list

# View failed deliveries
telnyx debugger list --status failed

# Retry failed
telnyx debugger retry EVENT_ID
```

### Account

```bash
# Account info
telnyx account get

# Check balance
telnyx account get --output json | jq '.balance'
```

## Output Formats

```bash
# Table (default)
telnyx number list

# JSON
telnyx number list --output json

# CSV
telnyx number list --output csv
```

## Examples

### Bulk Messaging

```bash
#!/bin/bash
while read phone; do
  telnyx message send --from +15551234567 --to "$phone" --text "Hello!"
  sleep 1  # Rate limiting
done < recipients.txt
```

### Monitor Webhooks

```bash
#!/bin/bash
while true; do
  FAILED=$(telnyx debugger list --status failed --output json | jq '.data | length')
  [ "$FAILED" -gt 0 ] && echo "⚠️  $FAILED failed webhooks"
  sleep 300
done
```

### Export Data

```bash
# CSV export
telnyx call list --limit 1000 --output csv > calls.csv

# JSON export
telnyx number list --output json > numbers.json
```

## Tips

- Rate limit: 100 req/s — add `sleep 1` for bulk operations
- Use `--output json` or `--output csv` to change format
- Get help: `telnyx COMMAND --help` (e.g., `telnyx message --help`)
- API Key location: `~/.config/telnyx/config.json`

## Integration with Clawdbot

```bash
# In cron jobs
0 9 * * * telnyx call list --limit 10 > /tmp/daily-calls.txt

# In heartbeat
telnyx debugger list --status failed

# In scripts
BALANCE=$(telnyx account get --output json | jq '.balance')
echo "Balance: $BALANCE"
```

## Companion Skills

This skill is the primary Telnyx interface. Two companion skills handle account lifecycle steps that this skill cannot:

| Skill | Purpose | Install |
|-------|---------|---------|
| **telnyx-bot-signup** | Create a new account OR sign into an existing one (generates API key) | `clawhub install telnyx-bot-signup` |
| **telnyx-freemium-upgrade** | Upgrade freemium account to professional tier | `clawhub install telnyx-freemium-upgrade` |

> **Note:** `telnyx-bot-signup` handles both signup and signin. The `bot_signup` endpoint accepts both new and existing emails — it sends a magic sign-in link either way. The flow is identical: PoW challenge → email → magic link → session token → API key.

### Pre-flight: Before Any Telnyx Operation

Before executing a Telnyx CLI command, run through this checklist:

```
1. Is `telnyx` CLI installed?
   NO  → npm install -g @telnyx/api-cli

2. Does ~/.config/telnyx/config.json exist with an api_key?
   NO  → Hand off to **telnyx-bot-signup** (see below)
         Works for both new AND existing accounts.

3. Does `telnyx account get` succeed?
   NO (401 auth error)  → API key is invalid/expired.
                           Hand off to **telnyx-bot-signup** to generate a fresh key.
   NO (network error)   → Check connectivity.
   YES                  → Proceed with the requested operation.
```

### When to Hand Off to telnyx-bot-signup

Hand off to the **telnyx-bot-signup** skill when ANY of these are true:

- No API key exists (`~/.config/telnyx/config.json` missing or empty, no `TELNYX_API_KEY` env var)
- API key exists but `telnyx account get` returns 401 (key invalid/expired/revoked)
- User says they lost their API key or can't access the portal
- User wants to create a new Telnyx account

**Do NOT ask whether the user has an account or not.** The `bot_signup` endpoint handles both cases transparently — just ask for their email and proceed.

**What telnyx-bot-signup does:** PoW challenge → submit email → magic sign-in link sent to email → session token → `POST /v2/api_keys` → fresh API key. Works identically for new and existing accounts.

**After signup/signin completes:**

1. Store the returned API key:
   ```bash
   mkdir -p ~/.config/telnyx
   echo '{"api_key":"<KEY_FROM_SIGNUP>"}' > ~/.config/telnyx/config.json
   ```
2. Also export it for the current session:
   ```bash
   export TELNYX_API_KEY="<KEY_FROM_SIGNUP>"
   ```
3. If the account is new, it starts on **freemium** tier. Return here and proceed with the original operation. If it hits a freemium wall, the upgrade flow below will trigger automatically.

### When to Hand Off to telnyx-freemium-upgrade

Hand off to the **telnyx-freemium-upgrade** skill when a CLI command fails with a freemium restriction. Detect these scenarios:

| Trigger | How you see it | Example |
|---------|---------------|---------|
| **Error 10039** | SMS send fails: "destination not verified" | `telnyx message send --to +39... --text "test"` |
| **Error D60** | Voice call fails: "destination not verified" | Outbound call to unverified number |
| **Error 10038** | Feature blocked: "not available on current plan" | Porting, short codes, SIM, managed accounts |
| **Number limit hit** | Second `telnyx number buy` fails | Already have 1 number (freemium max) |
| **Cannot add funds** | Balance top-up or payment method rejected | Freemium accounts cannot add balance |
| **Account inactive/deactivated** | Account shows deactivated due to $0 balance | `telnyx account get` shows inactive status |

**Also trigger proactively** when the user's intent clearly requires professional tier before even making the API call:

| User says | Why it needs upgrade |
|-----------|---------------------|
| "Send SMS to +39..." (international) | Unverified destination (10039) |
| "Port my number from AT&T" | Porting blocked on freemium (10038) |
| "Buy 5 phone numbers" | 1 number limit on freemium |
| "Set up a SIP trunk" | SIP blocked on freemium (10038) |
| "Create a managed account" | Managed accounts blocked (10038) |
| "Add $50 to my balance" | Freemium can't add funds |

Before handing off, check if the upgrade was already attempted:

```
1. Read ~/.telnyx/upgrade.json (cache from the upgrade skill)

2. If decision == "APPROVED"
   → Account is already upgraded. Do NOT hand off.
     Retry the operation directly. If it still fails, the API key
     may need to be refreshed: telnyx auth setup

3. If decision == "REJECTED" and used_methods includes "github_oauth"
   → GitHub method exhausted. Do NOT hand off.
     Tell the user: "Your upgrade was not approved. Contact
     support at https://support.telnyx.com or try LinkedIn
     verification when available."

4. If decision == "PASS_TO_HUMAN"
   → Under manual review. Do NOT hand off.
     Tell the user: "Your upgrade is under review. I'll check
     back periodically." (The upgrade skill's cron job handles this.)

5. If no cache or status is "failed" / "polling_timeout"
   → Hand off to **telnyx-freemium-upgrade**.
```

**After upgrade completes (APPROVED):**

1. Retry the original operation that triggered the upgrade.

2. If the retry still fails with the same error, the API key needs to be refreshed to pick up professional-tier permissions. Use **telnyx-bot-signup** to generate a fresh key (same email, sign-in flow) — this is easier than asking the user to visit the portal.

### Full Lifecycle Flow

```
User: "Send SMS to +393406879636"
│
├── telnyx CLI installed? ──NO──→ npm install -g @telnyx/api-cli
│
├── API key configured? ──NO──→ **telnyx-bot-signup** (ask for email)
│                                 → PoW → magic link → API key
│                                 → Store key → continue
│
├── API key valid? (`telnyx account get`)
│   └── NO (401) → **telnyx-bot-signup** (ask for email)
│                   → PoW → magic link → fresh API key
│                   → Store key → continue
│
├── telnyx message send --from ... --to +39... --text "..."
│   │
│   ├── Success → Done
│   │
│   └── Error 10039 (destination not verified)
│       │
│       ├── Check upgrade cache (~/.telnyx/upgrade.json)
│       │   ├── APPROVED → Retry (key may need refresh)
│       │   ├── REJECTED → Inform user, suggest support
│       │   ├── PASS_TO_HUMAN → Inform user, wait for review
│       │   └── No cache / failed → Continue to upgrade
│       │
│       └── **telnyx-freemium-upgrade** → GitHub verification → poll
│           │
│           ├── APPROVED → retry SMS (key may need refresh via bot-signup)
│           ├── REJECTED → Inform user
│           └── PASS_TO_HUMAN → Cron job polls, notify on resolution
```

### Companion Skill Not Installed

If you need to hand off but the companion skill is not installed:

**telnyx-bot-signup missing:**
> I need to set up your Telnyx API key. Install the signup/signin skill:
> ```
> clawhub install telnyx-bot-signup
> ```
> Or get your API key manually from https://portal.telnyx.com/#/app/api-keys and run `telnyx auth setup`

**telnyx-freemium-upgrade missing:**
> Your account is on the freemium tier, which doesn't support this operation. Install the upgrade skill:
> ```
> clawhub install telnyx-freemium-upgrade
> ```
> Or upgrade manually via https://portal.telnyx.com/#/account/account-levels/upgrade

---

## Troubleshooting

### CLI not found
```bash
npm install -g @telnyx/api-cli
```

### API key not configured
```bash
# Reconfigure
telnyx auth setup

# Or check existing config
cat ~/.config/telnyx/config.json
```

### Connection issues
```bash
# Test connection
telnyx account get
```

## Resources

- Telnyx Docs: https://developers.telnyx.com
- API Portal: https://portal.telnyx.com
- Telnyx CLI: https://github.com/team-telnyx/telnyx-api-cli
