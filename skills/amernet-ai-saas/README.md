# AI SaaS Skill for OpenClaw

Connect your [AI SaaS](https://saas.salesbay.ai) chatbot to any messaging channel via [OpenClaw](https://openclaw.ai) — WhatsApp, Telegram, Slack, Discord, iMessage, and more.

## Prerequisites

- [OpenClaw](https://openclaw.ai) installed and running (`npm install -g openclaw@latest`)
- An AI SaaS account with at least one active chatbot
- An API key from the AI SaaS portal

## Installation

### 1. Get your credentials from the AI SaaS portal

1. Open **Settings → API Keys** and create a key with **All** permissions. Copy the key.
2. Open the **Chatbots** page and copy the ID of the chatbot you want to route messages to.

You can also visit **Settings → OpenClaw** in the portal for a guided setup that generates the config for you.

### 2. Install the skill

```bash
# Clone into your OpenClaw workspace skills folder
git clone https://github.com/your-org/openclaw-skill-ai-saas \
  ~/.openclaw/workspace/skills/ai-saas

# Or copy manually
cp -r /path/to/openclaw-skill ~/.openclaw/workspace/skills/ai-saas
```

### 3. Configure credentials

Add the following to `~/.openclaw/openclaw.json` under the `skills` key:

```json
{
  "skills": {
    "entries": {
      "ai-saas": {
        "enabled": true,
        "env": {
          "AI_SAAS_API_KEY": "sk_live_your_api_key_here",
          "AI_SAAS_CHATBOT_ID": "your-chatbot-uuid-here",
          "AI_SAAS_BASE_URL": "https://saas.salesbay.ai"
        }
      }
    }
  }
}
```

### 4. Restart OpenClaw

```bash
openclaw restart
```

## Usage

Once installed, all messages sent through your connected channels (WhatsApp, Telegram, Slack, etc.) are automatically forwarded to your AI SaaS chatbot and responses are returned to the user.

### Special Commands

| Command | Action |
|---|---|
| `/reset` | Clear conversation history for the current user |
| `/status` | Check if the AI SaaS chatbot is active |

## How It Works

```
User (WhatsApp/Telegram/Slack/...)
        ↓ message
   OpenClaw Gateway
        ↓ skill routing
   AI SaaS Skill (SKILL.md)
        ↓ POST /api/v1/chatbots/:id/chat
   AI SaaS Backend (LLM + Knowledge Base)
        ↓ response
   OpenClaw Gateway
        ↓ reply
User receives AI response
```

Each user gets a persistent conversation session keyed by `<channel>:<user_id>`, so context is maintained across messages.

## Conversation Reset

Send "reset", "start over", or `/reset` to clear the conversation history and start fresh.

## Support

- AI SaaS portal: https://saas.salesbay.ai
- OpenClaw docs: https://docs.openclaw.ai
