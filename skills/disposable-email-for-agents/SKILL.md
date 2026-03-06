---
name: myagentinbox
description: Disposable email inboxes for AI agents. Create a temporary email
  address, receive emails, read messages, and download attachments — all through
  MCP tools. Inboxes auto-delete after 24 hours.
---

# myagentinbox

Disposable email inboxes for AI agents. Create a temporary email address, receive emails, read messages, and download attachments — all through MCP tools. Inboxes auto-delete after 24 hours.

## MCP Configuration

```json
{
  "mcpServers": {
    "myagentinbox": {
      "command": "npx",
      "args": ["mcp-remote", "https://myagentinbox.com/mcp"]
    }
  }
}
```

## Tools

### create_inbox

Create a disposable email inbox that expires in 24 hours. Returns the generated email address.

### check_inbox

Check for messages in an inbox.

- `address` (string): The inbox email address

### read_message

Read the full content of a specific email message including sender, subject, body, and attachment info.

- `address` (string): The inbox email address
- `message_id` (string): The message ID

### download_attachment

Download an email attachment. Returns images as base64, text files inline, and binary files as download URLs.

- `address` (string): The inbox email address
- `message_id` (string): The message ID
- `filename` (string): The attachment filename

## REST API

Alternatively, use the REST API directly:

- `POST /api/inboxes` — Create inbox
- `GET /api/inboxes/:address/messages` — List messages
- `GET /api/inboxes/:address/messages/:id` — Read message
- `GET /api/inboxes/:address/messages/:id/attachments/:filename` — Download attachment

## Limits

- Inbox creation: 10 per minute
- API reads: 60 per minute
- Inbox lifetime: 24 hours
- Max email size: 10 MB

## Example Usage

1. Use `create_inbox` to get a disposable `@myagentinbox.com` address
2. Sign up for a service or trigger an email to that address
3. Use `check_inbox` to see incoming messages
4. Use `read_message` to read the full email content
5. Use `download_attachment` if the email has attachments

No accounts, no API keys, no setup required.
