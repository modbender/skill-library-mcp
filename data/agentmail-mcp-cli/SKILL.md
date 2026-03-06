---
name: agentmail-mcp-cli
description: Manage AI agent email accounts via AgentMail API. Create inboxes, send/receive/reply to emails, manage threads and attachments. Use for "email", "agentmail", "inbox", "send email", "reply email", "forward email", "email agent", "mail api", "agent inbox".
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - AGENTMAIL_API_KEY
      bins:
        - node
        - agentmail
    primaryEnv: AGENTMAIL_API_KEY
    install:
      - kind: node
        package: openclaw-agentmail-cli
        bins:
          - agentmail
    homepage: https://agentmail.to
    docs: https://docs.agentmail.to
    repository: https://github.com/FloHiwg/agentmail-cli
---

# AgentMail MCP CLI

Email management for AI agents via the AgentMail API.

**Documentation:** https://docs.agentmail.to
**Get API Key:** https://agentmail.to

## Prerequisites

**Required:**
- Node.js >= 20.0.0
- AgentMail API key from [agentmail.to](https://agentmail.to)

**Installation:**
```bash
npm install -g openclaw-agentmail-cli
```

This installs the `agentmail` command globally.

## Authentication

Set your API key (get one from [agentmail.to](https://agentmail.to)):

```bash
# Option 1: Environment variable (recommended)
export AGENTMAIL_API_KEY="your_api_key"
agentmail inboxes list

# Option 2: CLI parameter
agentmail --api-key "your_api_key" inboxes list
```

## Quick Reference

### Inbox Management

```bash
# List all inboxes
agentmail inboxes list

# List with limit
agentmail inboxes list --limit 5

# Create a new inbox
agentmail inboxes create --display-name "My Agent"

# Create with username and domain
agentmail inboxes create --username myagent --domain agentmail.to --display-name "My Agent"

# Get inbox details
agentmail inboxes get <inbox-id>

# Delete an inbox (destructive!)
agentmail inboxes delete <inbox-id>
```

### Thread Management

```bash
# List threads in inbox
agentmail threads list <inbox-id>

# List with options
agentmail threads list <inbox-id> --limit 10

# Filter by labels
agentmail threads list <inbox-id> --labels '["unread"]'

# Filter by date
agentmail threads list <inbox-id> --after "2024-01-01" --before "2024-12-31"

# Get thread details (includes all messages)
agentmail threads get <inbox-id> <thread-id>
```

### Send Messages

```bash
# Send a simple email
agentmail messages send <inbox-id> \
  --to user@example.com \
  --subject "Hello" \
  --text "Email body here"

# Send to multiple recipients
agentmail messages send <inbox-id> \
  --to user1@example.com \
  --to user2@example.com \
  --subject "Team Update" \
  --text "Hello team..."

# Send with CC and BCC
agentmail messages send <inbox-id> \
  --to primary@example.com \
  --cc copy@example.com \
  --bcc hidden@example.com \
  --subject "Important" \
  --text "Please review..."

# Send HTML email
agentmail messages send <inbox-id> \
  --to user@example.com \
  --subject "Newsletter" \
  --html "<h1>Hello</h1><p>HTML content</p>"

# Send with labels
agentmail messages send <inbox-id> \
  --to user@example.com \
  --subject "Outreach" \
  --text "Hello..." \
  --labels '["campaign","outbound"]'
```

### Reply & Forward

```bash
# Reply to a message
agentmail messages reply <inbox-id> <message-id> \
  --text "Thank you for your email."

# Reply with HTML
agentmail messages reply <inbox-id> <message-id> \
  --html "<p>Thank you!</p>"

# Reply all
agentmail messages reply <inbox-id> <message-id> \
  --text "Replying to everyone..." \
  --reply-all

# Forward a message
agentmail messages forward <inbox-id> <message-id> \
  --to forward-to@example.com \
  --text "FYI - see below"

# Forward to multiple
agentmail messages forward <inbox-id> <message-id> \
  --to team@example.com \
  --cc manager@example.com \
  --subject "Fwd: Customer Inquiry" \
  --text "Please review"
```

### Labels & Organization

```bash
# Add labels to a message
agentmail messages update <inbox-id> <message-id> \
  --add-labels '["important","needs-review"]'

# Remove labels
agentmail messages update <inbox-id> <message-id> \
  --remove-labels '["unread"]'

# Add and remove simultaneously
agentmail messages update <inbox-id> <message-id> \
  --add-labels '["processed"]' \
  --remove-labels '["unread","pending"]'
```

### Attachments

```bash
# Get attachment details and download URL
agentmail attachments get <thread-id> <attachment-id>
```

## Available Commands

| Command | Description |
|---------|-------------|
| `inboxes list` | List all inboxes |
| `inboxes get <id>` | Get inbox details |
| `inboxes create` | Create new inbox |
| `inboxes delete <id>` | Delete inbox |
| `threads list <inbox-id>` | List threads |
| `threads get <inbox-id> <thread-id>` | Get thread with messages |
| `messages send <inbox-id>` | Send new email |
| `messages reply <inbox-id> <msg-id>` | Reply to email |
| `messages forward <inbox-id> <msg-id>` | Forward email |
| `messages update <inbox-id> <msg-id>` | Update labels |
| `attachments get <thread-id> <att-id>` | Get attachment |

## Command Options Reference

### inboxes list
- `-l, --limit <n>` - Max items (default: 10)
- `--page-token <token>` - Pagination token

### inboxes create
- `-u, --username <name>` - Email username
- `-d, --domain <domain>` - Email domain
- `-n, --display-name <name>` - Display name

### threads list
- `-l, --limit <n>` - Max items (default: 10)
- `--page-token <token>` - Pagination token
- `--labels <json>` - Filter by labels (JSON array)
- `--before <datetime>` - Before date (ISO 8601)
- `--after <datetime>` - After date (ISO 8601)

### messages send
- `--to <email>` - Recipient (repeatable)
- `--cc <email>` - CC recipient (repeatable)
- `--bcc <email>` - BCC recipient (repeatable)
- `-s, --subject <text>` - Subject line
- `-t, --text <body>` - Plain text body
- `--html <body>` - HTML body
- `--labels <json>` - Labels (JSON array)

### messages reply
- `-t, --text <body>` - Plain text body
- `--html <body>` - HTML body
- `--reply-all` - Reply to all recipients
- `--labels <json>` - Labels (JSON array)

### messages forward
- `--to <email>` - Recipient (repeatable)
- `--cc <email>` - CC recipient (repeatable)
- `--bcc <email>` - BCC recipient (repeatable)
- `-s, --subject <text>` - Subject line
- `-t, --text <body>` - Plain text body
- `--html <body>` - HTML body
- `--labels <json>` - Labels (JSON array)

### messages update
- `--add-labels <json>` - Labels to add (JSON array)
- `--remove-labels <json>` - Labels to remove (JSON array)

## Common Workflows

### Check for New Emails

```bash
# List unread threads
agentmail threads list <inbox-id> --labels '["unread"]' --limit 20
```

### Process and Archive Email

```bash
# 1. Get thread
agentmail threads get <inbox-id> <thread-id>

# 2. Process content (your logic)

# 3. Mark as processed
agentmail messages update <inbox-id> <message-id> \
  --add-labels '["processed"]' \
  --remove-labels '["unread"]'
```

### Auto-Reply Workflow

```bash
# 1. Check for emails needing reply
agentmail threads list <inbox-id> --labels '["needs-reply"]'

# 2. Get thread details
agentmail threads get <inbox-id> <thread-id>

# 3. Send reply
agentmail messages reply <inbox-id> <message-id> \
  --text "Thank you for reaching out. We will respond within 24 hours."

# 4. Update labels
agentmail messages update <inbox-id> <message-id> \
  --add-labels '["auto-replied"]' \
  --remove-labels '["needs-reply","unread"]'
```

### Create Inbox and Send First Email

```bash
# 1. Create inbox
agentmail inboxes create --display-name "Sales Bot"
# Note the inboxId from response

# 2. Send email
agentmail messages send <new-inbox-id> \
  --to prospect@example.com \
  --subject "Introduction" \
  --text "Hello! I wanted to reach out..."
```

## Error Handling

If commands fail, check:

1. **API Key**: Ensure `AGENTMAIL_API_KEY` is set
2. **IDs**: Verify inbox/thread/message IDs exist
3. **JSON**: Use proper JSON for array options: `'["value"]'`

## Alternative: MCPorter Syntax

If the MCP compatibility is restored, you can also use MCPorter:

```bash
# List inboxes
npx mcporter call agentmail.list_inboxes

# Send message
npx mcporter call agentmail.send_message \
  inboxId:<inbox-id> \
  to:'["user@example.com"]' \
  subject:"Hello" \
  text:"Body"
```

## Links

- **API Documentation:** https://docs.agentmail.to
- **Get API Key:** https://agentmail.to
- **MCP Server:** https://github.com/agentmail-to/agentmail-mcp
- **Node SDK:** https://github.com/agentmail-to/agentmail-node
