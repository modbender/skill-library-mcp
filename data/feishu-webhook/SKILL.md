---
name: feishu-webhook
description: Send messages to Feishu via Webhook with heredoc input support
---

# Feishu Webhook Skill

Send messages to Feishu via Webhook with heredoc input.

## Quick Start

```bash
python3 /home/yuhiri/workspace/skills/feishu-webhook/send-feishu.py << 'EOF'
# Write your Markdown content here (avoid level 1 and 2 headings; levels 3-6 are acceptable)
- Lists
- **Bold text**
EOF
```

## Features

- 📝 Heredoc input
- 📄 Markdown support (all Feishu card styles)
- ⚙️ Environment variables from OpenClaw config

## Config (OpenClaw)

Add to `~/.openclaw/openclaw.json` under `env.vars`:

```json
{
  "env": {
    "vars": {
      "FEISHU_WEBHOOK_URL": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx",
      "FEISHU_WEBHOOK_SECRET": "your_secret"
    }
  }
}
```

## Files

- `send-feishu.py` - Main sender

## Version

- **1.2.1**
