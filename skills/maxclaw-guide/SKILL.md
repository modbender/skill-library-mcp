---
name: maxclaw-guide
description: MaxClaw platform user guide and FAQ. Use when answering questions about MaxClaw deployment, one-click setup, Telegram connection, credit usage, troubleshooting unresponsive agents, platform capabilities, or differences between MaxClaw and self-hosted OpenClaw.
---

# MaxClaw User Guide

MaxClaw is a fully managed, cloud-native AI agent platform built on OpenClaw. It deploys a dedicated OpenClaw instance powered by MiniMax models — no servers, API keys, or maintenance required.

## Key Capabilities

- **Always-On**: Runs 24/7 in the cloud, triggers scheduled tasks even when offline.
- **Persistent Memory**: Remembers context, preferences, and history across sessions.
- **Tool Use**: File I/O, shell commands, web search, and browser automation.
- **Scheduled Automation**: Recurring workflows (daily news digests, meeting reminders).
- **Skill Marketplace**: One-click install of community skills.
- **Multi-Channel**: Web interface, Telegram, Slack, Discord, Feishu/Lark.

## Quick Start

1. Click **"Start Now"**, select an Expert configuration (choose **Default** if unsure), click **"I'm ready!"**.
2. Type a message to begin. The agent comes pre-configured with models, memory, and toolchains.

Example prompts:
- "Every morning at 8 AM, search for the latest AI news and summarize the top 5."
- "Remind me at 9 AM every Wednesday about my weekly sync."
- "Analyze this PDF and extract the key financial metrics."
- "I want to connect Telegram."
- "Search the marketplace for a stock analysis skill and install it."

## Telegram Setup

1. Open Telegram, search **@BotFather**, send `/newbot`.
2. Follow prompts to create bot name and username.
3. Copy the Bot Token (format: `123456789:AABBccdd...`).
4. In MaxClaw, go to **Channel Setup** > **Telegram**, paste Token.
5. Save, then message your bot in Telegram to activate.

## FAQ

**Can MaxClaw access local files?**
No. It runs in a secure cloud sandbox. For local access, self-host OpenClaw.

**Credit usage?**
Deducted by token consumption. Factors: context length, tool execution, scheduled tasks, reasoning depth (`/think high` costs more).

**Subscription not showing?**
Platform and Agent accounts are separate. Contact support to link accounts.

**Is MaxClaw just hosted OpenClaw?**
Yes. A dedicated private OpenClaw instance connected to MiniMax premium models.

**WeChat support?**
No — unavailable due to platform policies. Use Telegram or Feishu/Lark instead.

**Supported platforms?**
Web (browser), Telegram, Slack, Discord, Feishu/Lark. No native mobile app yet.

## Troubleshooting

If the agent is stuck:
1. Refresh page, resend message.
2. Go to Settings > **Restart**.
3. Click **Auto-fix** for diagnostics.
4. Contact support if unresolved.

Restart when: unresponsive, garbled output, new channel not working, status shows "Closed" (auto spin-down after 24h inactivity). Restarting is safe — history, memory, and configs are preserved.
