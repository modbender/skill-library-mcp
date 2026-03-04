# Sophiie — OpenClaw Skill

Manage your [Sophiie](https://sophiie.ai) sales pipeline from any OpenClaw-compatible AI agent. Create and manage leads, view inquiries, send SMS and calls, manage FAQs and policies, and more — all via natural language.

## Setup

1. **Get your API key** from Sophiie Dashboard → Settings → API Keys
2. **Set the environment variable**:
   ```bash
   export SOPHIIE_API_KEY="sk_live_your_key_here"
   ```
3. **Install the skill**:
   ```bash
   clawhub install sophiie
   ```

## Requirements

- `curl` and `jq` (pre-installed on most systems)
- A valid Sophiie API key (Pro or Enterprise plan)

## Quick Examples

```
> Show me my leads
# Fetches your lead pipeline

> Add a new lead: John Smith from Sydney, email john@example.com
# Creates a lead with the provided details

> What inquiries came in today?
# Lists recent inquiries

> Text lead ld_abc123 "Hi, following up on your inquiry"
# Sends an SMS to the lead

> Update our refund policy to include a 30-day window
# Creates or updates a business policy

> What are our business hours?
# Shows availability schedules
```

## Commands

| Domain | Actions |
|--------|---------|
| **leads** | `list`, `get`, `create`, `update`, `delete`, `notes`, `activities` |
| **inquiries** | `list`, `get` |
| **faqs** | `list`, `create`, `update`, `delete` |
| **policies** | `list`, `create`, `update`, `delete` |
| **calls** | `send` |
| **sms** | `send` |
| **appointments** | `list` |
| **org** | `get`, `availability`, `members`, `services`, `products` |
| **members** | `list` |

**26 endpoints** covering the full Sophiie REST API (v1).

## Rate Limits

60 requests per minute. The skill handles pagination automatically — list endpoints default to 50 items per page (max 100).

## Links

- [Sophiie Documentation](https://docs.sophiie.ai)
- [Sophiie Dashboard](https://app.sophiie.ai)
- [API Reference](https://docs.sophiie.ai/api)
