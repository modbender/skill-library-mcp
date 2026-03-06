---
license: Apache-2.0
name: email-resend
version: "1.0.14"
metadata:
  clawdbot:
    requires:
      env:
        - RESEND_API_KEY
      bins:
        - python3
        - openclaw
      python:
        - requests
        - pyyaml
triggers:
  - "send email"
  - "check emails"
  - "email me"
  - "email notification"
  - "download attachment"
description: >
  Send and receive emails using the Resend API. Use for: (1) sending emails directly
  via Resend API, (2) receiving email notifications via cron, (3) drafting replies with
  proper threading, (4) downloading attachments from inbound emails.

  **Required env vars:** RESEND_API_KEY (API key).
  **Optional env vars:** DEFAULT_FROM_EMAIL, DEFAULT_FROM_NAME (fall back to preferences file if not set).
  **License: Apache-2.0** — See LICENSE file for details.
---

## License

**Apache License 2.0** — See LICENSE file for full text.

# Email via Resend

Send and receive emails using the Resend API.

## Configuration

**No config file needed.** The skill auto-discovers settings from:

1. **Environment variables** — RESEND_API_KEY (required), DEFAULT_FROM_EMAIL/NAME (optional)
2. **Preferences file** — `memory/email-preferences.md` (from_email, from_name, telegram target)
3. **OpenClaw context** — channel, chat_id, thread_id (for cron delivery)

### Required Environment Variables

```bash
export RESEND_API_KEY="re_123456789"        # Resend API key (required)
# DEFAULT_FROM_EMAIL and DEFAULT_FROM_NAME are optional - loaded from preferences file if not set
```

### Preferences File

The skill reads sender info from `memory/email-preferences.md`:

```yaml
---
from_email: you@company.com
from_name: Your Name
telegram:
  target: "CHAT_ID"
  threadId: "THREAD_ID"
---
```

Scripts check env vars first, then fall back to preferences file.

### First-Time Setup

When the skill is first invoked, the sub-agent should:

1. **Check context** — OpenClaw context already has:
   - `context.user.email` (from USER.md)
   - `context.channel` (from current session)
   - `context.chat_id`
   - `context.thread_id` (for topics)

2. **Check memory** — Use `memory_get` tool:
   - Try: `memory_get path="memory/email-preferences.md"`
   - If not found, ask user to create `memory/email-preferences.md` (NO fallback scanning)

3. **If missing, ask user** — Via chat message (IMPORTANT for cron jobs):
   - "Which email should I send from?" (from_email)
   - "What's your display name for sent emails?" (from_name)
   - "Which channel/topic should I notify you on?" (telegram target + threadId)
   
   Then create `memory/email-preferences.md` with their answers using the format above.

4. **Commit to memory** — Write preferences to persist across sessions:
   ```bash
   write path="memory/email-preferences.md" content="---
   from_email: $EMAIL
   from_name: $NAME
   telegram:
     target: \"$CHAT_ID\"
     threadId: \"$THREAD_ID\"
   ---

   # Email Notification Preferences
   Saved auto-configured
   "
   ```
   This ensures memory_get finds it in future sessions. Use MD format with YAML frontmatter.

**Format (MD with YAML frontmatter):**
```markdown
---
from_email: you@company.com
from_name: Your Name
telegram:
  target: \"123456789\"
  threadId: \"334\"
---

# Email Notification Preferences
- **Updated:** 2026-01-01
- **Purpose:** Default notification channel for email alerts
```
**Important:** Store in `memory/email-preferences.md` (NOT MEMORY.md) - isolated cron jobs can read this file via memory_get but NOT MEMORY.md.

### Context Fields (Available in Sub-Agent)

| Field | Source | Example |
|-------|--------|---------|
| `user.email` | USER.md | `you@company.com` |
| `user.name` | USER.md | `Your Name` |
| `channel` | OpenClaw | from context |
| `chat_id` | OpenClaw | `123456789` |
| `thread_id` | OpenClaw | `334` |

The skill uses these directly from OpenClaw context — no parsing needed.

## Usage

## Inbound (Receive)

### Cron Setup

There are two ways to configure the cron:

#### Option 1: Static (Hardcoded Target)

Use this if you always want the same delivery target:

```bash
openclaw cron add \
  --name "email-resend-inbound" \
  --cron "*/15 * * * *" \
  --message "Follow instructions in skills/email-resend/cron-prompts/email-inbound.md exactly. If new emails found, include them in your reply." \
  --session isolated \
  --announce \
  --channel telegram \
  --to "-1003748898773:topic:334"
```

#### Option 2: Dynamic (From Preferences) — Recommended

This reads your notification preferences from `memory/email-preferences.md` and configures the cron automatically.

Run:

```bash
python3 ~/.openclaw/workspace/skills/email-resend/scripts/configure-cron.py
```

What it does:
1. Reads `memory/email-preferences.md` for your telegram target/threadId
2. Deletes any existing `email-resend-inbound` cron
3. Creates a new cron with your preferred delivery target

**First-time setup:** If preferences don't exist, it will tell you what to configure.

**Parameters:**
- `--schedule "cron */15 * * * *"` — Run every 15 minutes
- `--session isolated` — Required for agentTurn payloads
- `--announce` — Enable delivery of results to chat
- `--channel telegram` — Delivery channel
- `--to` — Telegram target (format: `chat_id:topic:thread_id`)

**Note:** The cron prompt reads notification preferences from `memory/email-preferences.md`. On first run, if preferences are missing, it will ask you for:
- Which channel for notifications (telegram, discord, etc.)
- Chat ID and Thread ID (for topics)

### Manual Check

```bash
python3 ~/.openclaw/workspace/skills/email-resend/scripts/inbound.py
```

### Notification Format

Each new email triggers a notification with:
- From, Subject, Date
- Body preview (~2000 chars)
- Attachment list (if any)
- Importance: 🔥 HIGH / 📅 MEETING / 📬 NORMAL

### Acknowledge Flow (CRITICAL)

**NEVER auto-acknowledge emails.** Only the user can acknowledge by:
- Replying to the notification message, OR
- Typing: `done` / `ack`

Emails must remain in pending state until user explicitly acknowledges.

Use `draft-reply.py` to compose replies with proper quoting.

**Important:** Always use inline replies (`[[reply_to_current]]`) to keep messages linked in the thread. This enables:
- Proper custody chain tracking
- Reply-to-email tracing
- Better conversation flow

**CRITICAL:** When responding via OpenClaw message tool, use `replyTo` parameter (not `[[reply_to_current]]` tag):
```python
message(action="send", channel="<from-context>", replyTo="<msg_id>", ...)
```

## Scripts

| Script | Purpose |
|--------|---------|
| `inbound.py` | Check emails, send notifications |
| `draft-reply.py` | Draft reply workflow with quoting & threading |
| `outbound.py` | Send emails directly |
| `download_attachment.py` | Download attachments from inbound emails |

### Downloading Attachments

To download attachments from an inbound email:

```bash
# List attachments (shows IDs)
python3 scripts/download_attachment.py <email_id> --list

# Download all to directory
python3 scripts/download_attachment.py <email_id> --output-dir ./attachments

# Download specific attachment
python3 scripts/download_attachment.py <email_id> --attachment-id <attachment_id>
```

**Note:** The API path is `/emails/receiving/{email_id}/attachments` (not the standard `/emails/` path).

## State Files

- `memory/email-resend-inbound-notified.json` — pending/acknowledged emails
- `memory/email-message-map.json` — notification message_id → email_id (legacy)
- `memory/email-custody-chain.json` — Full DAG of email → notification → actions
- `memory/email-msg-to-chain.json` — notification message_id → chain lookup
- `memory/email-draft-state.json` — Active draft state (email_id, status, reply_content)

See `docs/custody-chain.md` for DAG design.

## Outbound (Send)

```bash
python3 ~/.openclaw/workspace/skills/email-resend/scripts/outbound.py \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "Message text"

# With attachments
python3 ~/.openclaw/workspace/skills/email-resend/scripts/outbound.py \
  --to "recipient@example.com" \
  --subject "Here's the file" \
  --body "See attachment" \
  --attachment ./file.pdf \
  --attachment ./image.png
```

## ⚠️ CRITICAL: Email Threading Rule (2026-02-22)

**MANDATORY: Always use `draft-reply.py` for replying to emails.**

This is non-negotiable. Failure to follow this rule will result in broken Gmail threading.

### Why This Matters
- Gmail threads emails based on `In-Reply-To` AND `References` headers
- Using wrong headers = reply appears as NEW thread = context lost
- There's no way to fix this after sending

### ✅ Correct Workflow (ALWAYS USE THIS)

```bash
# Step 1: Start draft (fetches Message-ID automatically)
python3 ~/.openclaw/workspace/skills/email-resend/scripts/draft-reply.py start <email_id>

# Step 2: Set reply content
python3 ~/.openclaw/workspace/skills/email-resend/scripts/draft-reply.py content "Your reply"

# Step 3: Send
python3 ~/.openclaw/workspace/skills/email-resend/scripts/draft-reply.py send
```

### ⚠️ CRITICAL: Approval Execution Rule (2026-02-22)

**When user approves a draft, you MUST execute the send command immediately.**

**The mistake to avoid:**
- ❌ Show draft for approval → User says "send" → Only acknowledge, don't execute
- ✅ Show draft for approval → User says "send" → RUN `draft-reply.py send` → Then confirm

**Correct workflow:**
```
1. Show draft for approval
2. User replies "approve", "send", "yes", or "ok"
3. IMMEDIATELY run: draft-reply.py send
4. Only THEN confirm to user
```

**Never:**
- Only acknowledge the approval without executing
- Ask for confirmation after user already approved
- Wait to send - do it immediately

### ❌ NEVER Do These Things

**NEVER use `outbound.py` for replies:**
```bash
# WRONG - will break threading
python3 ~/.openclaw/workspace/skills/email-resend/scripts/outbound.py \
  --to "x@y.com" --subject "Re: Original" --body "Reply"
```

**NEVER manually construct `--reply-to` flags:**
```bash
# WRONG - guessing Message-ID format never works
python3 ~/.openclaw/workspace/skills/email-resend/scripts/outbound.py \
  --to "x@y.com" --subject "Re: Original" --body "Reply" \
  --reply-to "<some-guess>@resend"
```

**NEVER skip the workflow when subject starts with "Re:":**
```bash
# WRONG - replying without threading headers breaks thread
python3 ~/.openclaw/workspace/skills/email-resend/scripts/outbound.py \
  --to "x@y.com" --subject "Re: Previous Thread" --body "Quick reply"
```

### outbound.py Only For New Emails

`outbound.py` is for **new emails only** (not replies):
- First contact
- Announcements
- Emails where you intentionally want a NEW thread

For anything that could be a reply, use `draft-reply.py`.

## Requirements

- `RESEND_API_KEY` environment variable set
- Python `requests` library

## Draft Reply Best Practices

When composing a reply via `draft-reply.py`:

1. **Always quote the original** — Include the original message with `>` prefix so recipient knows what you're responding to

2. **Use proper threading** — Set `In-Reply-To` and `References` headers using the original email's Message-ID

3. **Keep subject line** — Start with `Re: ` prefix to maintain thread (but avoid "Re: Re:")

4. **Structure:**
   ```
   Your reply here

   ---

   On [date] [original sender] wrote:
   > quoted original message
   > continues here
   ```

5. **Multiple replies supported** — After sending, draft is marked as "sent" so you can reply again to the same thread. Use `resume` command to continue.

6. **No double Re:** — If original subject already starts with "Re:", don't add another

7. **Custody Chain** — Track full lineage:
   - Email → notification → All replies/actions
   - DAG structure with parent links
   - Any message traces back to original email

## Draft Reply Commands

| Command | Purpose |
|---------|---------|
| `start <email_id>` | Start a draft reply to an email |
| `resume` | Continue a sent thread to reply again |
| `content "text"` | Set reply content |
| `send` | Send the reply |
| `cancel` | Cancel the draft |
| `status` | Show current draft status |

After sending, use `resume` to reply again to the same thread — threading headers are preserved.

Run tests:
```bash
python3 skills/email-resend/tests/test_inbound.py
```

Expected: 43+ tests total (test_inbound.py: 37, test_threading.py: 6, test_attachments.py: varies).

If tests fail:
1. Check which test failed and why
2. Fix the feature/code to match expected behavior
3. Or update tests if feature intentionally changed

---

## ⚠️ Privacy & Security Considerations

### Required Credentials
- **RESEND_API_KEY** — Required. Get from https://resend.com API settings. Create with minimal permissions.
- **DEFAULT_FROM_EMAIL** / **DEFAULT_FROM_NAME** — Optional. If not set, loaded from `memory/email-preferences.md`.

### Memory File Access
The skill reads ONLY from explicit preferences file:
- `memory/email-preferences.md` — Required for telegram target/threadId
- **No fallback scanning** of MEMORY.md, USER.md, TOOLS.md, or memory/*.md

This restricted approach prevents information leakage from sensitive files.

### Cron Job
The `configure-cron.py` script will create/delete a cron job named `email-resend-inbound` via OpenClaw CLI.

### Recommendations
- Run tests with a dummy RESEND_API_KEY before enabling in production
- If you only need outbound email, don't enable inbound/cron
- Audit `memory/email-preferences.md` to ensure it contains only necessary fields
- Keep preferences file minimal - only include required fields (target, threadId)
