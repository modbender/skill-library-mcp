---
name: doubletick
description: Send tracked emails via Gmail and check if they were opened.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins:
        - npx
    emoji: "\u2714\ufe0f"
    homepage: https://doubletickr.com
    install:
      - kind: node
        package: doubletick-cli
        bins:
          - doubletick
---

# DoubleTick

Send tracked emails via Gmail and check if they were opened.

## Setup

1. Install and log in (one-time):

```bash
npx doubletick-cli login
```

2. Add to your MCP config:

```json
{
  "mcpServers": {
    "doubletick": {
      "command": "npx",
      "args": ["-y", "doubletick-cli"]
    }
  }
}
```

## What it does

DoubleTick injects a 1x1 tracking pixel into emails sent via the Gmail API. When the recipient opens the email, the pixel fires and the open is logged. You can then check the status to see if and when it was read.

## Tools

- **send_tracked_email** — Send an email with read tracking. Body accepts markdown (auto-converted to HTML).
- **check_tracking_status** — Check if a tracked email has been opened, with open count, device, and timing.
- **list_tracked_emails** — List recent tracked emails with open rates and stats.

## Examples

```
Send a tracked email to jane@company.com with subject "Q1 Planning" and body "Hi Jane, here are the numbers for Q1..."
```

```
Check if my last tracked email was opened
```

```
Show my tracked emails dashboard
```

## Requirements

- Node.js 18+
- A Gmail account
- A [DoubleTick](https://doubletickr.com) account (free tier: 5 tracked emails/week)

## Links

- npm: https://www.npmjs.com/package/doubletick-cli
- GitHub: https://github.com/cseguinlz/doubletick-cli
- Website: https://doubletickr.com
