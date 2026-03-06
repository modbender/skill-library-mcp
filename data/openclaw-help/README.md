# openclaw-help

Enhanced `/help` command for OpenClaw.

## Security note

This plugin is intentionally **generic by default**. Do not hardcode personal commands, group names, phone numbers, or private workflow details into the repository.

Instead, customize the output via plugin config.

## Install (dev)

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-help
openclaw gateway restart
```

## ClawHub

```bash
clawhub install openclaw-help
```

## Configure

The repo stays placeholder-only. You customize `/help` locally via plugin config.

Example (using **public** projects as references):

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

Security reminder: keep private commands, phone numbers, group IDs, tokens, and internal workflows out of the repo. Store them only in local config.
