---
name: loopuman
description: Route tasks to verified human workers worldwide via Loopuman. Use when AI alone can't handle verification, translation, content moderation, image labeling, local knowledge, or subjective judgment. Results in minutes, paid in 8-second cUSD payments on Celo.
metadata:
  {
    "openclaw":
      {
        "emoji": "🌍",
        "requires": { "bins": ["curl", "jq"] },
      },
  }
---

# Loopuman — The Human Layer for AI

Route tasks to verified human workers when AI alone isn't enough. Workers are paid in 8 seconds via cUSD on Celo blockchain. No app download required — workers operate via Telegram and WhatsApp.

## When to Use This Skill

Use Loopuman when the task requires **real human judgment, perception, or local knowledge** that AI cannot reliably provide:

- **Verification** — "Is this business address real?" "Does this photo match this listing?"
- **Translation** — Nuanced, culturally-aware translation (not just word-for-word)
- **Content moderation** — "Is this image appropriate?" "Does this review violate guidelines?"
- **Image labeling** — "What objects are in this photo?" "Rate this image quality 1-10"
- **Local knowledge** — "What's the current price of tomatoes in Nairobi?"
- **Surveys & opinions** — "Which logo design is better?" "Rate this product description"
- **Data collection** — "Find the phone number for this restaurant"
- **Quality assurance** — "Does this AI-generated text sound natural?"

**Do NOT use** for tasks AI can handle: math, code generation, summarization, web search, file operations.

## Setup

Create the config file with your Loopuman API key:

```bash
mkdir -p ~/.openclaw/skills/loopuman
cat > ~/.openclaw/skills/loopuman/config.json << 'EOF'
{
  "apiKey": "YOUR_API_KEY",
  "apiUrl": "https://api.loopuman.com"
}
EOF
```

Get your API key (one command, no auth needed):

```bash
curl -X POST https://api.loopuman.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "company_name": "Your Name", "promo_code": "LOBSTER"}'
```

This returns your `api_key` (starts with `lpm_`). Save it immediately — it cannot be retrieved later.

**Promo codes for free credits:**
- `CLAW500` — 500 VAE ($5.00) for first 10 OpenClaw testers
- `LOBSTER` — 100 VAE ($1.00) for early access (50 spots)
- No code — 25 VAE ($0.25) welcome bonus

To add more funds, message [@LoopumanBot](https://t.me/LoopumanBot) on Telegram and link your account.

## API Authentication

All requests use the `x-api-key` header:
```
x-api-key: YOUR_API_KEY
```

## Creating a Task

```bash
scripts/loopuman.sh create \
  --title "Verify business address" \
  --description "Check if this address exists on Google Maps: 123 Main St, Nairobi, Kenya. Reply with YES/NO and a screenshot." \
  --category other \
  --budget 50 \
  --estimated-seconds 120
```

**Parameters:**
- `--title` — Short task title (required)
- `--description` — Detailed instructions for the human worker (required, be specific!)
- `--category` — One of: `survey`, `labeling`, `translation`, `writing`, `research`, `content_creation`, `ai_training`, `micro`, `other` (default: `other`). Note: for verification tasks use `other`, for moderation use `other`, for data collection use `research`.
- `--budget` — Payment in VAE tokens. 100 VAE = $1 USD. (default: 100)
- `--estimated-seconds` — Expected time for worker to complete (required for fair pay calculation, default: 120)
- `--max-workers` — Number of workers (default: 1, max: 100)
- `--priority` — `normal` or `high` (high notifies workers immediately)
- `--webhook` — URL for push notifications on completion

**Category minimum budgets:**
- `survey`, `labeling`, `ai_training`, `micro`: 25 VAE ($0.25)
- `research`, `content_creation`: 75 VAE ($0.75)
- `writing`, `translation`: 100 VAE ($1.00)

**Fair pay enforcement:** Loopuman enforces a $6/hr minimum effective rate. If your budget divided by estimated time is below this, the API will suggest a higher budget.

**Writing good task descriptions:**
- Be specific about what you need ("Reply YES or NO" not "verify this")
- Include all context the worker needs
- Specify the expected format of the response
- Set clear success criteria

## Checking Task Status + Getting Results

```bash
scripts/loopuman.sh status --task-id <TASK_ID>
```

Returns full task details including:
- `status`: `active`, `completed`, `expired`, `cancelled`
- `progress`: count of approved, pending_review, in_progress submissions
- `submissions`: array of approved worker results with content
- `pending_submissions`: results awaiting your approval

## Polling for Completion

For tasks that need a result before continuing:

```bash
# Poll every 30 seconds, timeout after 10 minutes
scripts/loopuman.sh wait --task-id <TASK_ID> --interval 30 --timeout 600
```

Returns the result as soon as an approved submission is available.

## Listing Tasks

```bash
scripts/loopuman.sh list
```

## Cancelling a Task

```bash
scripts/loopuman.sh cancel --task-id <TASK_ID>
```

Refunds your balance if no workers have started.

## Task Types and Pricing

| Category | Description | Min Budget (VAE) | Typical Completion |
|----------|-------------|-----------------|-------------------|
| `survey` | Quick responses, opinions | 25 ($0.25) | 1-5 min |
| `labeling` | Tag images, categorize content | 25 ($0.25) | 1-5 min |
| `micro` | 5-second microtasks | 25 ($0.25) | <1 min |
| `ai_training` | RLHF, preference ranking | 25 ($0.25) | 1-5 min |
| `research` | Find info, investigate | 75 ($0.75) | 5-20 min |
| `content_creation` | Creative work | 75 ($0.75) | 5-20 min |
| `writing` | Articles, descriptions | 100 ($1.00) | 10-30 min |
| `translation` | Language translation | 100 ($1.00) | 5-15 min |
| `other` | Custom tasks | 25 ($0.25) | Varies |

## Examples

**Verify an address:**
"Create a Loopuman task to verify if '456 Kenyatta Ave, Nairobi' is a real business address"
→ `create --title "Verify address" --description "Check Google Maps for 456 Kenyatta Ave, Nairobi. Reply YES/NO with screenshot." --category other --budget 30 --estimated-seconds 120`

**Translate with cultural context:**
"Use Loopuman to translate 'We're excited to launch' into Swahili naturally"
→ `create --title "Translate to Swahili" --description "Translate to Swahili. Make it sound natural, not robotic: 'We're excited to launch our new product'" --category translation --budget 100 --estimated-seconds 180`

**Get a human opinion:**
"Ask a real person which logo looks more professional"
→ `create --title "Logo comparison" --description "Which logo looks more professional? A or B? Explain why in 2 sentences." --category survey --budget 25 --estimated-seconds 60`

**Check AI output:**
"Have a human verify this AI-generated product description"
→ `create --title "QA check on AI text" --description "Does this sound natural and accurate? Flag any issues: [paste text]" --category other --budget 30 --estimated-seconds 90`

## Error Handling

| HTTP Code | Meaning | Fix |
|-----------|---------|-----|
| 401 | Invalid API key | Check `x-api-key` in config.json |
| 400 | Missing fields or invalid category | Check required params |
| 402 | Insufficient VAE balance | Top up via @LoopumanBot |
| 404 | Task not found | Verify task ID |
| 429 | Rate limit exceeded | Wait and retry |

## Links

- Website: https://loopuman.com
- Telegram Bot: https://t.me/LoopumanBot
- ERC-8004 Agent: https://www.8004scan.io/agents/celo/17
- MCP: https://api.loopuman.com/.well-known/mcp.json
- A2A: https://api.loopuman.com/.well-known/agent-card.json

⚠️ **Budget Safety:** Tasks are paid to workers upon completion. Start with small budgets (25-50 VAE) when testing. Loopuman charges 20% commission on top of the budget you set.
