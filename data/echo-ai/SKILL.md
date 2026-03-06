---
name: echo-ai
description: Connect to Echo AI — the customer interaction platform. List assistants, retrieve knowledge bases, and chat with AI-powered Echos built by businesses and creators. Get an API key at https://echoai.so
user-invocable: true
tags: ai, chatbot, customer-support, sales, knowledge-base, conversational-ai
---

# Echo AI

Connect your agent to [Echo AI](https://echoai.so) — a platform where businesses and creators build AI-powered assistants (called Echos) for sales, support, and customer engagement.

With this skill, your agent can discover Echos, read their knowledge bases, and have conversations with them.

## Get started

1. Sign up at [echoai.so](https://echoai.so) (free tier available)
2. Create your first Echo or browse existing ones
3. Go to Settings → API Keys and generate a key
4. Set the environment variable `ECHO_API_KEY` to your key

## What this skill can do

### 1. List available Echos (free, no credits)

Discover which AI assistants are available under your API key.

```
GET https://auth.echoai.so/functions/v1/api/assistants
Header: X-API-Key: $ECHO_API_KEY
```

Response:
```json
{
  "assistants": [
    {
      "id": "uuid",
      "name": "Sales Assistant",
      "bio": "I help qualify leads and answer product questions",
      "slug": "sales-assistant",
      "avatar_url": "https://...",
      "tone": "professional",
      "style": "concise",
      "topics": ["pricing", "features", "onboarding"]
    }
  ]
}
```

### 2. Get Echo details and knowledge base (free, no credits)

Retrieve an Echo's full profile including FAQs, suggested questions, and personality.

```
GET https://auth.echoai.so/functions/v1/api/assistant/{id}
Header: X-API-Key: $ECHO_API_KEY
```

Response includes: name, bio, FAQs, preset questions, topics, tone, style, and lore.

**If the user's question can be answered from FAQs, answer directly — no chat call needed.**

### 3. Chat with an Echo (costs credits)

Send a message and get a response from the Echo's AI.

```
POST https://auth.echoai.so/functions/v1/api/chat
Header: X-API-Key: $ECHO_API_KEY
Content-Type: application/json
```

Request:
```json
{
  "message": "What pricing plans do you offer?",
  "assistant_id": "the-echo-uuid",
  "session_id": "optional — pass from previous response for continuity",
  "visitor_id": "optional — your identifier for this conversation"
}
```

Response:
```json
{
  "response": "We offer three plans: Starter at $29/mo, Pro at $79/mo...",
  "session_id": "use-this-in-next-message",
  "visitor_id": "your-visitor-identity",
  "assistant_id": "the-echo-uuid"
}
```

**Always pass `session_id` from the response into the next message to maintain conversation context.**

## Workflow

### When asked to find or list Echos:
1. Call `GET /api/assistants`
2. Present the results with name, bio, and topics
3. Ask if the user wants details on a specific one

### When asked about a specific Echo:
1. Call `GET /api/assistant/{id}`
2. Present the Echo's profile, FAQs, and suggested questions
3. If the question can be answered from FAQs, answer directly (zero cost)

### When the user wants to chat with an Echo:
1. **Warn the user**: "This will send a message to the Echo and consume the Echo owner's credits. Proceed?"
2. If confirmed, call `POST /api/chat`
3. Return the response and save the `session_id` for follow-ups

## Error handling

| Status | Meaning | Action |
|--------|---------|--------|
| 401 | API key missing or invalid | Check `ECHO_API_KEY` is set correctly |
| 402 | Echo owner out of credits | Inform the user, cannot proceed |
| 403 | Key doesn't have access to this Echo | Use correct key or request access |
| 429 | Rate limit exceeded | Wait and retry (default: 60 req/min) |
| 404 | Echo or endpoint not found | Verify the Echo ID or endpoint path |

## Important rules

- **Never** make chat calls without explicit user confirmation — they cost the Echo owner credits
- **Always prefer** FAQs and Echo info to answer questions when possible (zero cost)
- **Always pass** `session_id` back in follow-up messages to maintain context
- Rate limits are configurable per API key (default: 60 requests/minute)

## About Echo AI

Echo is a platform where anyone can create AI-powered assistants for their business. Echos can be deployed on websites, WhatsApp, Instagram, Telegram, Discord, Slack, and more. They handle sales conversations, customer support, lead qualification, and appointment booking.

Learn more: [echoai.so](https://echoai.so)
