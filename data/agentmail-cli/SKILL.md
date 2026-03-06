---
name: agentmail-cli
description: Manage email inboxes and messages via AgentMail API. Create disposable inboxes, send/receive emails, and list messages. Use when the agent needs to send or receive email, create temporary inboxes, or check for incoming messages.
metadata: {"openclaw":{"emoji":"📧","requires":{"bins":["agentmail"],"env":["AGENTMAIL_API_KEY"]},"primaryEnv":"AGENTMAIL_API_KEY","install":[{"id":"npm","kind":"node","package":"@stepandel/agentmail-cli","bins":["agentmail"],"label":"Install agentmail-cli via npm"}]}}
homepage: https://github.com/stepandel/agentmail-cli
---

CLI for [AgentMail](https://agentmail.to) — create inboxes, send messages, and read email.

## API Key Setup

The API key MUST be configured before any command will work. Two methods:

1. **Config file (preferred for persistent agents):**
```
agentmail config set-key YOUR_API_KEY
```
This stores the key at `~/.agentmail/config.json` and persists across sessions.

2. **Environment variable:**
```
export AGENTMAIL_API_KEY=YOUR_API_KEY
```

Verify configuration:
```
agentmail config show
```

If commands fail with auth errors, re-run `agentmail config set-key` — the env var alone may not persist between shell sessions.

## Always Use --json

Always pass `--json` to every command for machine-readable output. Parse with `jq` when needed.

## Inbox Commands

Create an inbox:
```
agentmail inbox create --json
agentmail inbox create --domain example.com --json
agentmail inbox create --username support --domain example.com --display-name "Support Team" --json
```

List inboxes:
```
agentmail inbox list --json
agentmail inbox list --limit 10 --json
```

Get inbox details:
```
agentmail inbox get <inbox-id> --json
```

Delete an inbox:
```
agentmail inbox delete <inbox-id>
```

## Message Commands

Send a message:
```
agentmail message send --from <inbox-id> --to recipient@example.com --subject "Subject" --text "Body text" --json
```

Send with HTML:
```
agentmail message send --from <inbox-id> --to recipient@example.com --subject "Subject" --html "<h1>Hello</h1>" --json
```

Multiple recipients, CC, BCC:
```
agentmail message send --from <inbox-id> --to "a@example.com,b@example.com" --cc "cc@example.com" --bcc "bcc@example.com" --subject "Subject" --text "Body" --json
```

List messages in an inbox:
```
agentmail message list <inbox-id> --json
agentmail message list <inbox-id> --limit 20 --json
```

Get a specific message:
```
agentmail message get <inbox-id> <message-id> --json
```

Delete a message (deletes entire thread):
```
agentmail message delete <inbox-id> <message-id>
```

## Common Workflow

```bash
# 1. Create inbox, capture ID
INBOX_ID=$(agentmail inbox create --json | jq -r '.inboxId')

# 2. Send email
agentmail message send --from "$INBOX_ID" --to user@example.com --subject "Hello" --text "Message body" --json

# 3. Check for replies
agentmail message list "$INBOX_ID" --json
```

## Notes

- Get an API key at https://agentmail.to
- Config file location: `~/.agentmail/config.json`
- Env var `AGENTMAIL_API_KEY` takes precedence over config file
- Deleting a message deletes the entire thread containing it