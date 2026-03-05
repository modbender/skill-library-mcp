---
name: openclaw-help
description: OpenClaw plugin providing a config-driven /help command (safe placeholder-only defaults).
---

# openclaw-help

Adds a `/help` command to your OpenClaw agent.

The key design goal is **safety for public repos**: the plugin ships with **generic placeholder help text**. You inject your real shortcuts locally via config (e.g., in `~/.openclaw/openclaw.json`).

## What it does

- Registers `/help`
- Prints:
  - generic default sections (Shortcuts / Memory / TODO)
  - optional tips
  - optional custom sections from config

## Why this exists

People tend to hardcode personal commands, phone numbers, group IDs, and internal workflow notes into README files. If you publish plugins to GitHub/ClawHub, that can leak private info.

This plugin avoids that by:

- keeping the repository content placeholder-only
- moving the real, personal mapping into local config

## Install

From ClawHub:

```bash
clawhub install openclaw-help
```

For local development:

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-help
openclaw gateway restart
```

## Configure

Example config (safe, generic):

```json
{
  "plugins": {
    "entries": {
      "openclaw-help": {
        "enabled": true,
        "config": {
          "includeTips": true,
          "sections": [
            {
              "title": "Public example projects",
              "lines": [
                "- AAHP - protocol + handoff structure example",
                "- BMAS - research project example"
              ]
            },
            {
              "title": "Your shortcuts (fill in locally)",
              "lines": [
                "- /<project> - your project shortcut",
                "- /<command> - your custom command"
              ]
            }
          ]
        }
      }
    }
  }
}
```

## OPSEC rule

- Never put private commands, phone numbers, group IDs, tokens, domains, or internal workflows into this repo.
- Keep that data in local config only.
