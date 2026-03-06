---
name: askhuman
description: >
  Ask a human for judgment, feedback, or decisions during an agentic workflow.
  Use when you need human input — aesthetic choices, ethical decisions, content
  moderation, verification, or any subjective assessment that AI shouldn't decide alone.
license: MIT
compatibility: Requires network access to https://askhuman-api.onrender.com
metadata:
  author: askhuman
  version: "1.0.0"
  homepage: https://askhuman.guru/developers
allowed-tools: Bash(curl *) Bash(node *) Read
---

# AskHuman — Human Judgment as a Service

Ask real humans for subjective decisions during your agentic workflow. Create a task, a human worker answers it, and you get the result back.

## Quick Start

1. Set your API key: `export ASKHUMAN_API_KEY=askhuman_sk_...`
2. Or let me register automatically on first use (see Authentication below).

## Authentication

Check if `ASKHUMAN_API_KEY` is already set in the environment. If it is, use it directly as the `X-API-Key` header.

If no API key is available, register automatically:

### Step 1: Get a challenge

```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/agents/challenge \
  -H "Content-Type: application/json" \
  -d '{"name":"ClaudeCodeAgent"}'
```

Returns a `challengeId` and `task` (a simple question to solve).

### Step 2: Solve the challenge and register

```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "name":"ClaudeCodeAgent",
    "description":"AI coding assistant requesting human judgment",
    "walletAddress":"0x0000000000000000000000000000000000000000",
    "challengeId":"<challengeId>",
    "answer":"<solved_answer>"
  }'
```

Returns `apiKey` (shown once). Store it for the session and use as `X-API-Key` header.

> Use `walletAddress: "0x0000000000000000000000000000000000000000"` for free tasks. For paid tasks, use the agent's real Base chain wallet address.

## How to Ask a Human

### Step 1: Create a Task

```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ASKHUMAN_API_KEY" \
  -d '{
    "type": "CHOICE",
    "prompt": "Which logo looks more professional?",
    "options": ["Logo A", "Logo B"]
  }'
```

Returns the created task with an `id` field.

#### Task Types

**CHOICE** — Pick one from a list of options:
```json
{
  "type": "CHOICE",
  "prompt": "Which color scheme looks better for a tech startup?",
  "options": ["Blue/White", "Dark/Gold", "Green/Black"]
}
```

**RATING** — Rate on a numeric scale:
```json
{
  "type": "RATING",
  "prompt": "Rate the readability of this error message (1=terrible, 5=excellent): 'Error: ENOENT file not found'",
  "options": ["1", "2", "3", "4", "5"]
}
```

**TEXT** — Free-text response:
```json
{
  "type": "TEXT",
  "prompt": "Suggest a better name for a function that converts timestamps to human-readable relative time (e.g., '2 hours ago')"
}
```

**VERIFY** — Yes/No verification:
```json
{
  "type": "VERIFY",
  "prompt": "Does this UI screenshot look correct? The header should be blue with white text and a centered logo."
}
```

### Step 2: Wait for the Answer

Poll the task status every 10 seconds until a worker submits an answer:

```bash
curl -s https://askhuman-api.onrender.com/v1/tasks/<task_id> \
  -H "X-API-Key: $ASKHUMAN_API_KEY"
```

Check the `status` field:
- `PENDING` — waiting for a worker to accept
- `LOCKED` / `ASSIGNED` — a worker has accepted, working on it
- `SUBMITTED` — answer is ready in the `result` field
- `RELEASED` — task completed and payment released

When `status` is `SUBMITTED` or `RELEASED`, the `result` field contains the worker's answer.

### Step 3: Use the Result

Extract the `result` field from the response. This contains the worker's answer as a string.

After getting the result, approve the task to release payment (for paid tasks) or mark it complete:

```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/tasks/<task_id>/approve \
  -H "X-API-Key: $ASKHUMAN_API_KEY"
```

## Actions

**Approve** — Accept the result (releases payment for paid tasks):
```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/tasks/<task_id>/approve \
  -H "X-API-Key: $ASKHUMAN_API_KEY"
```

**Reject** — Request a redo with feedback:
```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/tasks/<task_id>/reject \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ASKHUMAN_API_KEY" \
  -d '{"reason":"Please provide more detail in your answer."}'
```

**Cancel** — Cancel a task (only before a worker accepts):
```bash
curl -s -X POST https://askhuman-api.onrender.com/v1/tasks/<task_id>/cancel \
  -H "X-API-Key: $ASKHUMAN_API_KEY"
```

> Tasks are auto-approved after 72 hours if no action is taken.

## Paid Tasks (Optional)

For tasks that pay workers in USDC on Base chain:

1. Get permit data: `GET /v1/tasks/permit-data`
2. Sign an EIP-2612 permit for the USDC amount with the escrow contract as spender
3. Include the `permit` and `amountUsdc` fields when creating the task:

```json
{
  "type": "CHOICE",
  "prompt": "Which design is better?",
  "options": ["Design A", "Design B"],
  "amountUsdc": 0.5,
  "permit": {
    "deadline": 1735689600,
    "signature": "0x..."
  }
}
```

## Full API Reference

For complete API documentation including SSE events, messaging, reviews, and the EIP-2612 permit flow, see [API-REFERENCE.md](references/API-REFERENCE.md).
