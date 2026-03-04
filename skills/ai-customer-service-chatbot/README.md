# Chaterimo OpenClaw Skill

OpenClaw/ClawHub skill for [Chaterimo](https://www.chaterimo.com) - AI Customer Service for Shopify & E-commerce.

## What is Chaterimo?

Chaterimo is an AI-powered customer service platform that integrates with **Shopify**, **Shoptet**, **Upgates**, and **eshop-rychle.cz** e-commerce platforms. It provides 24/7 automated customer support powered by leading LLM models: **ChatGPT**, **Claude**, **Gemini**, and **Grok**.

Use your own API keys (BYOK) or choose a custom plan with included AI credits.

📖 **Shopify Setup Guide:** [How to connect Chaterimo with Shopify](https://www.chaterimo.com/en/blog/shopify-ai-customer-service/)

## Features

- **List Chatbots** - View all your configured AI chatbots
- **Browse Conversations** - Search and filter customer service conversations
- **Read Transcripts** - Get full conversation history with PII automatically redacted:
  - Email addresses → `[EMAIL]`
  - Phone numbers → `[PHONE]`

## Data Security

- **Hashed API keys** - Keys stored as SHA256 hashes, never in plain text
- **Tenant isolation** - Access only your organisation's data
- **Rate limiting** - 60 req/min to prevent abuse
- **Audit logging** - All API calls logged for security
- **HTTPS only** - All traffic encrypted

## Quick Start

1. Sign up at [chaterimo.com](https://www.chaterimo.com)
2. Connect your Shopify store in Integrations section (or Shoptet, Upgates, eshop-rychle.cz)
3. Go to **API Keys** in your dashboard
4. Create an API key and set it as an environment variable:

```bash
export CHATERIMO_API_KEY=cha_your_key_here
```

## Example Usage

```
User: Show me my chatbots
Assistant: You have 2 chatbots configured:
1. Main Store Support (GPT-4) - Active
2. Czech Support (Claude) - Active

User: Show conversations from last week
Assistant: Found 47 conversations...
```

## Links

- Website: [chaterimo.com](https://www.chaterimo.com)
- Shopify Guide: [How to connect Chaterimo with Shopify](https://www.chaterimo.com/en/blog/shopify-ai-customer-service/)

## License

MIT
