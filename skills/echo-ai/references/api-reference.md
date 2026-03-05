# Echo AI API Reference

## Base URL

```
https://auth.echoai.so/functions/v1/api
```

## Authentication

All requests require an API key via one of:

```
X-API-Key: ek_xxxxxxxxxxxxx
```

or

```
Authorization: Bearer ek_xxxxxxxxxxxxx
```

## Endpoints

### GET /assistants

List all assistants accessible with the current API key.

**Response:**
```json
{
  "assistants": [
    {
      "id": "uuid",
      "name": "My Assistant",
      "bio": "A helpful AI assistant",
      "avatar_url": "https://...",
      "slug": "my-assistant"
    }
  ]
}
```

**Credit cost:** 0

---

### GET /assistant/:id

Get detailed information about a specific assistant.

**Response:**
```json
{
  "assistant": {
    "id": "uuid",
    "name": "My Assistant",
    "bio": "A helpful AI assistant",
    "avatar_url": "https://...",
    "slug": "my-assistant",
    "tone": "friendly",
    "style": "conversational",
    "faqs": [
      { "question": "What do you do?", "answer": "I help with..." }
    ],
    "preset_questions": ["How can I help?", "Tell me about..."]
  }
}
```

**Credit cost:** 0

---

### POST /chat

Send a message to an assistant and receive a response.

**Request:**
```json
{
  "message": "Hello, what can you help me with?",
  "assistant_id": "uuid"
}
```

**Response:**
```json
{
  "response": "Hi! I can help you with..."
}
```

**Credit cost:** 1+ credits per message (varies by response length)

---

## Rate Limits

- Default: 60 requests per minute per API key
- Configurable by the API key owner (10, 30, 60, 120, or 300 req/min)
- Returns `429 Too Many Requests` when exceeded

## API Key Types

| Type | Scope | Use Case |
|------|-------|----------|
| Workspace Key | All owner's assistants | Multi-assistant apps |
| Assistant Key | Single assistant only | Focused integrations |

## Getting an API Key

1. Sign up at [echoai.so](https://echoai.so)
2. Go to Settings → API Keys (workspace) or Echo Editor → API (per-assistant)
3. Click "New API Key" and save the generated key securely
