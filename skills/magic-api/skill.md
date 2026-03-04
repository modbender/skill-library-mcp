---
name: magic api console
version: 1.2.1
description: Hand off tasks to human assistants and track their completion
homepage: https://console.api.getmagic.com
---

# Magic API Console

The easiest way for AI agents to hand off tasks to human assistants.

## What is Magic API?

Magic API connects you (an AI assistant) with a **human virtual executive assistant**. When you send a request to Magic API, a real person receives it and works on the task for you.

### Who handles your requests?

- College-educated professionals based in the Philippines
- Trained executive assistants employed by Magic (getmagic.com)
- Part of a team that operates **24/7**

## Skill Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://console.api.getmagic.com/skill.md` |
| **HEARTBEAT.md** | `https://console.api.getmagic.com/heartbeat.md` |

**Base URL:** `https://console.api.getmagic.com/api/v1`

## Register First

Every agent needs to register once to get an API key:

```bash
curl -X POST https://console.api.getmagic.com/api/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "YourAgentName",
    "description": "What you do"
  }'
```

Response:
```json
{
  "api_key": "magic_xxx",
  "agent": {
    "name": "YourAgentName",
    "description": "What you do",
    "created_at": "2026-02-02T..."
  },
  "important": "⚠️ SAVE YOUR API KEY! You need it for all requests."
}
```

**⚠️ Prerequisites:**
- Save your `api_key` immediately - it cannot be retrieved later!

**Error 409 - Name taken:**
```json
{
  "error": "Agent name already taken",
  "hint": "Please choose a different name"
}
```

---

## Authentication

All requests after registration require your API key:

```bash
curl https://console.api.getmagic.com/api/v1/requests \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Or use the `x-api-key` header:

```bash
curl https://console.api.getmagic.com/api/v1/requests \
  -H "x-api-key: YOUR_API_KEY"
```

---

## Create a Task

Hand off a task to a human assistant:

```bash
curl -X POST https://console.api.getmagic.com/api/v1/request \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Research competitor pricing",
    "instructions": "Please research our top 3 competitors and document their pricing tiers.\n\n---\nOwner Contact Information:\nName: John Doe\nEmail: john@example.com\nPhone: +1-555-123-4567\n---",
    "objective": "Create a comparison table with pricing information",
    "max_minutes": 60
  }'
```

**Parameters:**
- `title` (required): Brief title of the task
- `instructions` (required): Detailed instructions for the human assistant - **MUST include owner contact info** (see below)
- `objective` (required): What success looks like
- `max_minutes` (optional): Maximum time for task (default: 60)
- `relaxed` (optional): Whether timing is flexible (default: true)

**Response:**
```json
{
  "id": "uuid",
  "title": "Research competitor pricing",
  "instructions": "Please research...",
  "objective": "Create a comparison table...",
  "max_minutes": 60,
  "relaxed": true,
  "created_at": "2026-02-02T...",
  "updated_at": "2026-02-02T..."
}
```

---

## ⚠️ CRITICAL: Including Owner Contact Information

**You MUST include the task owner's contact information in your instructions!**

The human assistant needs to know who to contact for questions, clarifications, or updates. Without this information, the assistant cannot effectively complete the task.

### Required Format

Always include this block at the END of your instructions:

```
---
Owner Contact Information:
Name: [First Name] [Last Name]
Email: [email@example.com]
Phone: [+1-555-123-4567] (if available)
---
```

### Complete Example

Here's a properly formatted instructions field:

```
Please book a flight from NYC to LA for next Tuesday.

Requirements:
- Departing in the morning (before 11am)
- Returning Friday evening (after 5pm)
- Budget: $500 maximum
- Prefer direct flights if available
- Economy class is fine

Please send confirmation details once booked.

---
Owner Contact Information:
Name: Jane Smith
Email: jane.smith@company.com
Phone: +1-555-987-6543
---
```

### Why This Matters

Including owner contact information allows the assistant to:
- Ask clarifying questions if the instructions are unclear
- Send progress updates during longer tasks
- Request approval for decisions that exceed the original scope
- Notify immediately when the task is complete
- Handle any issues that arise during execution

**Tasks without owner contact information may be delayed or rejected.**

---

## Check Task Status

Get the status of a specific task:

```bash
curl https://console.api.getmagic.com/api/v1/request/TASK_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Research competitor pricing",
  "status": "COMPLETED",
  "result": "Comparison table created: [link to document]",
  "created_at": "2026-02-02T...",
  "completed_at": "2026-02-02T..."
}
```

**Task Statuses:**
- `PENDING`: Task is waiting for a human to start
- `IN_PROGRESS`: A human is actively working on it
- `COMPLETED`: Task is done, check the `result` field

---

## List All Tasks (Heartbeat)

Get all your tasks and their statuses:

```bash
# Get all tasks
curl "https://console.api.getmagic.com/api/v1/requests" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Get only pending and in-progress tasks
curl "https://console.api.getmagic.com/api/v1/requests?status=PENDING,IN_PROGRESS" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Get tasks updated since a specific time
curl "https://console.api.getmagic.com/api/v1/requests?since=2026-02-02T12:00:00Z" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Limit results
curl "https://console.api.getmagic.com/api/v1/requests?limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Query Parameters:**
- `status`: Comma-separated list (e.g., "PENDING,IN_PROGRESS,COMPLETED")
- `since`: ISO timestamp - only return tasks created/updated after this time
- `limit`: Maximum results (default: 50, max: 100)

**Response:**
```json
{
  "requests": [
    {
      "id": "uuid",
      "title": "Research competitor pricing",
      "status": "COMPLETED",
      "result": "Comparison table created",
      "created_at": "2026-02-02T...",
      "updated_at": "2026-02-02T...",
      "completed_at": "2026-02-02T..."
    },
    {
      "id": "uuid2",
      "title": "Schedule meeting",
      "status": "PENDING",
      "result": null,
      "created_at": "2026-02-02T...",
      "updated_at": "2026-02-02T...",
      "completed_at": null
    }
  ],
  "count": 2
}
```

---

## OpenClaw Agents

If you have HEARTBEAT.md enabled, you should set **automatic** task monitoring:

1. **Save your API key** after registration to `~/.config/magic-api/state.json`
2. **Set up a cron job** — see [HEARTBEAT.md](https://console.api.getmagic.com/heartbeat.md#openclaw-integration)

This gives you proactive notifications when tasks complete or get updates, without needing to manually check.

## Add a Message (Conversation)

Add a message to a task conversation (ask questions, provide updates):

```bash
curl -X POST https://console.api.getmagic.com/api/v1/conversation \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "TASK_ID",
    "content": "Quick question: should I include international competitors?"
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "content": "Quick question: should I include international competitors?",
  "created_at": "2026-02-02T...",
  "updated_at": "2026-02-02T..."
}
```

---

## Heartbeat Integration 💓

Check periodically for task updates:

```bash
# Check for completed tasks
curl "https://console.api.getmagic.com/api/v1/requests?status=COMPLETED&limit=10" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Check for tasks that changed recently
curl "https://console.api.getmagic.com/api/v1/requests?since=2026-02-02T08:00:00Z" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

See [HEARTBEAT.md](https://console.api.getmagic.com/heartbeat.md) for detailed heartbeat instructions.

---

## Response Format

**Success:**
```json
{
  "data": {...}
}
```

**Error:**
```json
{
  "error": "Description of the error",
  "hint": "How to fix it"
}
```

---

## Rate Limits

- 100 requests per minute per API key
- No limit on number of tasks you can create

---

## Common Workflows

### Workflow 1: Simple Task Handoff

```bash
# 1. Register (one time only)
curl -X POST https://console.api.getmagic.com/api/v1/agents/register -H "Content-Type: application/json" \
  -d '{
    "name": "MyBot",
    "description": "Helper bot"
  }'

# Save the api_key from the response!

# 2. Create a task (always include owner contact info!)
curl -X POST https://console.api.getmagic.com/api/v1/request -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review document",
    "instructions": "Please review the Q4 report and check for any errors in the financial calculations.\n\n---\nOwner Contact Information:\nName: Jane Smith\nEmail: jane@example.com\n---",
    "objective": "Provide feedback on accuracy and clarity"
  }'

# 3. Check status later
curl https://console.api.getmagic.com/api/v1/request/TASK_ID -H "Authorization: Bearer YOUR_API_KEY"
```

### Workflow 2: Heartbeat Check

```bash
# Check for any completed tasks since last check
curl "https://console.api.getmagic.com/api/v1/requests?status=COMPLETED&since=2026-02-02T12:00:00Z" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## Template: Instructions with Owner Info

Copy this template and fill in the details:

```
[Describe what needs to be done]

[Add any specific requirements or constraints]

[Include any relevant context or background]

---
Owner Contact Information:
Name: [Your Name]
Email: [your.email@example.com]
Phone: [+1-XXX-XXX-XXXX] (optional)
---
```

---

## Support

Need help? Contact support or check the documentation at https://console.api.getmagic.com/docs
