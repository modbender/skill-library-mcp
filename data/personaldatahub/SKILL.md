---
name: PersonalDataHub
description: Pull personal data (emails, issues) and propose outbound actions (drafts, replies) through the PersonalDataHub access control gateway. Data is filtered, redacted, and shaped by the owner's policy before reaching the agent.
version: 0.1.0
skillKey: personaldatahub
emoji: 🔐
homepage: https://github.com/AISmithLab/PersonalDataHub
os: darwin, linux, win32
install: cd ../../ && pnpm install && pnpm build && npx pdh init "OpenClaw Agent" && npx pdh start
metadata: {}
always: false
---

# PersonalDataHub

Access personal data from Gmail, GitHub, and other sources through the PersonalDataHub access control gateway. The data owner controls what the agent can see, which fields are visible, what gets redacted, and which actions are allowed.

## MCP Setup (Recommended)

PersonalDataHub provides an MCP server for native tool discovery. Add to your Claude Code config (`.claude/settings.json`):

```json
{
  "mcpServers": {
    "personaldatahub": {
      "command": "npx",
      "args": ["pdh", "mcp"]
    }
  }
}
```

This registers source-specific tools dynamically — only sources with connected OAuth tokens get tools.

## Tools

### read_emails
*(Gmail — requires connected Gmail OAuth)*

Pull emails from Gmail. Data is filtered and redacted according to the owner's access control policy.

**Parameters:**
- `purpose` (required) — Why this data is needed (logged for audit)
- `query` (optional) — Gmail search query (e.g., `"is:unread from:alice newer_than:7d"`)
- `limit` (optional) — Maximum number of results

**Example:**
```
Pull my recent unread emails about the Q4 report.
```

### draft_email
*(Gmail — requires connected Gmail OAuth)*

Draft an email via Gmail. The draft is staged for the data owner to review — it does NOT send until approved.

**Parameters:**
- `to` (required) — Recipient email address
- `subject` (required) — Email subject
- `body` (required) — Email body
- `purpose` (required) — Why this action is being proposed (logged for audit)
- `in_reply_to` (optional) — Message ID for threading

### send_email
*(Gmail — requires connected Gmail OAuth)*

Send an email via Gmail. The action is staged for the data owner to review — it does NOT execute until approved.

**Parameters:**
- `to` (required) — Recipient email address
- `subject` (required) — Email subject
- `body` (required) — Email body
- `purpose` (required) — Why this action is being proposed (logged for audit)
- `in_reply_to` (optional) — Message ID for threading

### reply_to_email
*(Gmail — requires connected Gmail OAuth)*

Reply to an email via Gmail. The reply is staged for the data owner to review — it does NOT send until approved.

**Parameters:**
- `to` (required) — Recipient email address
- `subject` (required) — Email subject
- `body` (required) — Email body
- `in_reply_to` (required) — Message ID of the email being replied to
- `purpose` (required) — Why this action is being proposed (logged for audit)

### search_github_issues
*(GitHub — requires connected GitHub OAuth)*

Search GitHub issues. Data is filtered according to the owner's access control policy.

**Parameters:**
- `purpose` (required) — Why this data is needed (logged for audit)
- `query` (optional) — Search query for issues
- `limit` (optional) — Maximum number of results

### search_github_prs
*(GitHub — requires connected GitHub OAuth)*

Search GitHub pull requests. Data is filtered according to the owner's access control policy.

**Parameters:**
- `purpose` (required) — Why this data is needed (logged for audit)
- `query` (optional) — Search query for pull requests
- `limit` (optional) — Maximum number of results

## Direct API Fallback

If the MCP tools above are not available, you can call the PersonalDataHub API directly via HTTP.

**Config:** Read `~/.pdh/config.json` to get `hubUrl`.

**Pull data:**
```bash
curl -X POST <hubUrl>/app/v1/pull \
  -H "Content-Type: application/json" \
  -d '{"source": "gmail", "purpose": "reason for pulling data"}'
```

**Propose an action:**
```bash
curl -X POST <hubUrl>/app/v1/propose \
  -H "Content-Type: application/json" \
  -d '{"source": "gmail", "action_type": "draft_email", "action_data": {"to": "...", "subject": "...", "body": "..."}, "purpose": "reason for action"}'
```

## Troubleshooting

If calls fail, check if the PersonalDataHub server is running:
```bash
curl <hubUrl>/health
```

If the server is not running, find and start it:
```bash
# Check where PersonalDataHub is installed
cat ~/.pdh/config.json   # look at hubDir
# Start the server
cd <hubDir> && node dist/index.js
```

## Setup

The install hook bootstraps PersonalDataHub automatically:
1. Installs dependencies, builds the project, initializes the database
2. Saves hub URL and directory to `~/.pdh/config.json`
3. Starts the server in the background

After installation, open `http://localhost:3000` to connect Gmail/GitHub via OAuth.

Agents read config automatically from `~/.pdh/config.json` — no manual configuration needed.

## Query Syntax (Gmail)

- `is:unread` — unread emails
- `from:alice` — emails from Alice
- `newer_than:7d` — emails from the last 7 days
- `subject:report` — emails with "report" in subject
- Combine: `is:unread from:alice newer_than:7d`

## Important Notes

- **Data is filtered**: The owner controls which fields you see. Some fields may be missing or redacted.
- **Actions require approval**: All outbound actions (emails, drafts) go to a staging queue. The owner must approve before execution.
- **Everything is audited**: Every pull and propose is logged with your purpose string.
