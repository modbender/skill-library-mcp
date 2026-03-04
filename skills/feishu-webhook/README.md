# Feishu Webhook - Heredoc Edition

Send messages to Feishu via Webhook with heredoc input.

## Usage

```bash
python3 send-feishu.py << 'EOF'
💓 心跳报告
- 时间: 2026-02-08 03:00
- 状态: 运行正常
- 任务: 已完成
EOF
```

## Features

- 📝 Heredoc input
- 🎯 First line = title
- 📄 Rest = content (Markdown)
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

**v1.2.0** - Environment variables from OpenClaw config
