#!/bin/bash
# LLM Cost Monitor - Cron Examples
# Add these to your crontab (crontab -e)

PROJECT_DIR="/path/to/llm-cost-monitor"
cd "$PROJECT_DIR"

# ============================================
# Option 1: System Cron (crontab -e)
# ============================================

# ----------------------------------------
# Daily: Fetch yesterday's usage at 11 PM
# ----------------------------------------
# 0 23 * * * cd "$PROJECT_DIR" && python3 scripts/fetch_usage.py --yesterday >> /tmp/llm-cost.log 2>&1

# ----------------------------------------
# Daily: Budget check at 11:30 PM
# Exit code 2 = exceeded (can trigger external alerts)
# ----------------------------------------
# 0 23 * * * cd "$PROJECT_DIR" && python3 scripts/alert.py --budget-usd 10 --period yesterday

# ----------------------------------------
# Weekly: Send report every Monday at 9 AM
# ----------------------------------------
# 0 9 * * 1 cd "$PROJECT_DIR" && python3 scripts/report.py --period week --json >> /tmp/llm-cost-week.json

# ----------------------------------------
# Monthly: Send report on 1st of each month
# ----------------------------------------
# 0 9 1 * * cd "$PROJECT_DIR" && python3 scripts/report.py --period month


# ============================================
# Option 2: OpenClaw Cron (JSON)
# ============================================
# Add these to your OpenClaw config or via CLI

# ----------------------------------------
# Job 1: Daily fetch (recommended)
# ----------------------------------------
# {
#   "name": "llm-cost-daily-fetch",
#   "schedule": {"kind": "cron", "expr": "0 23 * * *", "tz": "Asia/Shanghai"},
#   "payload": {
#     "kind": "agentTurn",
#     "message": "Run: cd $HOME/llm-cost-monitor && python3 scripts/fetch_usage.py --yesterday"
#   },
#   "sessionTarget": "isolated",
#   "delivery": {"mode": "none"}
# }

# ----------------------------------------
# Job 2: Daily budget check + notification
# ----------------------------------------
# {
#   "name": "llm-cost-daily-alert",
#   "schedule": {"kind": "cron", "expr": "30 23 * * *", "tz": "Asia/Shanghai"},
#   "payload": {
#     "kind": "agentTurn", 
#     "message": "Run: cd $HOME/llm-cost-monitor && python3 scripts/alert.py --budget-usd 10 --period yesterday --mode warn",
#     "timeoutSeconds": 60
#   },
#   "sessionTarget": "isolated",
#   "delivery": {"mode": "announce", "channel": "feishu"}
# }

# ----------------------------------------
# Job 3: Weekly image report
# ----------------------------------------
# {
#   "name": "llm-cost-weekly-report",
#   "schedule": {"kind": "cron", "expr": "0 9 * * 1", "tz": "Asia/Shanghai"},
#   "payload": {
#     "kind": "agentTurn",
#     "message": "Run: cd $HOME/llm-cost-monitor && python3 scripts/html_report.py --period week && python3 scripts/notify.py --message 'Weekly Report' --channel feishu --image /tmp/llm-cost-report.png"
#   },
#   "sessionTarget": "isolated",
#   "delivery": {"mode": "announce", "channel": "feishu"}
# }


# ============================================
# Option 3: OpenClaw CLI
# ============================================

# Add cron job via OpenClaw CLI:
# openclaw cron add --name llm-cost-daily --schedule "0 23 * * *" --payload 'Run: python3 ~/llm-cost-monitor/scripts/fetch_usage.py --yesterday'

# List cron jobs:
# openclaw cron list

# Remove cron job:
# openclaw cron remove llm-cost-daily


# ============================================
# Environment Variables (for notifications)
# ============================================

# Feishu:
# export FEISHU_APP_ID="cli_xxx"
# export FEISHU_APP_SECRET="xxx"
# export FEISHU_USER_ID="ou_xxx"

# Telegram:
# export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
# export TELEGRAM_CHAT_ID="123456789"

# Discord:
# export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxx"

# Slack:
# export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxx"

# Custom Webhook:
# export CUSTOM_WEBHOOK_URL="https://your-webhook.com/endpoint"
