# Setup — Telegram Bot API

Read this when `~/telegram-bot-api/` doesn't exist. Start naturally by asking about their bot project.

## Your Attitude

Help them build something powerful. Telegram bots reach users directly — real-time messaging, inline queries, payments. Show enthusiasm.

## Priority Order

### 1. First: Understand Their Bot

Ask about what they're building:
- "What's your bot going to do?"
- "Is this for a personal project, community, or business?"
- "Do you have a bot token already, or should we create one with BotFather?"

**If they share a token:**
1. Ask permission: "Want me to save this token locally so I can help you test?"
2. If yes, save to `~/telegram-bot-api/bots/{botname}.md`
3. Confirm: "Saved to ~/telegram-bot-api/bots/{name}.md — I won't display it again"

**If they don't have one:** Guide them to @BotFather:
1. Open Telegram, search @BotFather
2. Send /newbot
3. Follow prompts for name and username
4. Copy the token (never share it publicly)

### 2. Then: Technical Preferences

Adapt based on their experience:
- **New to bots:** Focus on sendMessage, basic keyboards
- **Experienced:** Ask about webhooks vs polling, deployment plans
- **Building for production:** Discuss error handling, rate limits

### 3. Finally: Integration Preference

Ask how they want this skill to activate:
- "Should I help whenever you mention Telegram bots?"
- "Only when you're actively building something?"

## What Gets Saved

In `~/telegram-bot-api/memory.md`:
- Default parse_mode preference (HTML recommended)
- Whether they prefer curl examples or library code
- Their deployment environment (server, serverless, local)

In `~/telegram-bot-api/bots/{name}.md`:
- Bot token (only with explicit permission)
- Bot username
- Webhook URL if configured
- Default settings for that bot

**All data stays in `~/telegram-bot-api/` — nothing is shared externally.**
