---
name: composio-connect
description: "Connect 850+ apps (Gmail, Slack, GitHub, Calendar, Notion, Jira, and more) to OpenClaw via Composio and mcporter. Use when the user asks to send emails, create issues, post messages, manage calendars, search documents, or interact with any third-party SaaS app. One skill, 11,000+ tools, managed OAuth."
homepage: https://composio.dev
metadata:
  {
    "openclaw":
      {
        "emoji": "🔗",
        "requires":
          {
            "env": ["COMPOSIO_API_KEY", "COMPOSIO_MCP_URL"],
            "bins": ["mcporter"],
          },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "mcporter",
              "bins": ["mcporter"],
              "label": "Install mcporter (npm)",
            },
          ],
      },
  }
---

# Check if composio MCP server is registered in mcporter

```bash
mcporter list
```

If composio does not appear you should add it with this command:

```bash
mcporter config add composio --url $COMPOSIO_MCP_URL
```

## Discovering Tools

Before attempting to call any composio MCP tool, you must perform a targeted search to identify the correct tool name and required parameters.

```bash
mcporter list composio --all-parameters | grep -niE -B 14 '^\s*function\s+SPOTIFY_.*(VOLUME|PLAYBACK)|^\s*function\s+.*(VOLUME|PLAYBACK).*SPOTIFY_'
```

## Executing Tools

Once you know the tool name from search, call it:

```bash
mcporter call 'composio.SPOTIFY_SET_PLAYBACK_VOLUME(volume_percent:"90")'
```

```bash
mcporter call 'composio.TODOIST_CREATE_TASK(content: "Pay electricity bill", due_string: "tomorrow at 4pm")'
```

```bash
mcporter call 'composio.GMAIL_CREATE_DRAFT(to: "name@example.com", subject: "Quick question", body: "Hey — ...")'
```
