---
name: amernet-ai-saas
description: Connect your AI SaaS intelligent agent to any messaging channel via OpenClaw (WhatsApp, Telegram, Slack, Discord, iMessage, and more)
homepage: https://saas.salesbay.ai
user-invocable: false
---

## AI SaaS Chatbot

This skill forwards user messages to an AI SaaS chatbot and returns its response. It maintains conversation context per user by using their channel and user identifier as a session key.

### Required Configuration

These environment variables must be set in your `~/.openclaw/openclaw.json` under `skills.entries.amernet-ai-saas.env`:

| Variable | Description |
|---|---|
| `AI_SAAS_API_KEY` | Your API key from the portal (Settings → API Keys). Needs `all` permission. |
| `AI_SAAS_CHATBOT_ID` | The chatbot ID to route all messages to (copy from the Chatbots page). |
| `AI_SAAS_BASE_URL` | Base URL of your AI SaaS instance. Default: `https://saas.salesbay.ai` |

### Message Routing

When the user sends ANY message through any connected channel:

1. Identify the current channel name (e.g. `whatsapp`, `telegram`, `slack`, `discord`) and the user's identifier on that channel (phone number, user ID, or username).

2. Construct a `sender_id` combining both: `<channel>:<user_identifier>`
   - WhatsApp example: `whatsapp:+15551234567`
   - Telegram example: `telegram:123456789`
   - Slack example: `slack:U012AB3CD`
   - Discord example: `discord:123456789012345678`

3. Send a POST request to the chatbot API:

```
POST ${AI_SAAS_BASE_URL}/api/v1/chatbots/${AI_SAAS_CHATBOT_ID}/chat
Authorization: Bearer ${AI_SAAS_API_KEY}
Content-Type: application/json

{
  "sender_id": "<constructed sender_id>",
  "message": "<user message text>"
}
```

4. Parse `data.responses` from the JSON response. Return each item's `text` field as a separate message to the user. If multiple responses exist, send them in order.

5. If the API returns an error or is unreachable, reply: "Sorry, the AI assistant is temporarily unavailable. Please try again in a moment."

### Conversation Reset

If the user explicitly says "reset", "start over", "clear chat", or "/reset":

```
DELETE ${AI_SAAS_BASE_URL}/api/v1/chatbots/${AI_SAAS_CHATBOT_ID}/conversations/<sender_id>
Authorization: Bearer ${AI_SAAS_API_KEY}
```

Then confirm: "Conversation cleared. How can I help you?"

### Status Check

If the user says "/status" or "/ping":

```
GET ${AI_SAAS_BASE_URL}/api/v1/chatbots/${AI_SAAS_CHATBOT_ID}
Authorization: Bearer ${AI_SAAS_API_KEY}
```

Report the chatbot name and whether it is active.
