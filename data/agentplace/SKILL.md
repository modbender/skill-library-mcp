---
name: agentplace
description: AI Agent Marketplace for OpenClaw. Browse and discover 60+ free & premium agents — developer tools, content, automation, video, research, and more.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env: []
    optional:
      env:
        - AGENTPLACE_API_KEY
---

# Agentplace — AI Agent Marketplace for OpenClaw

Agentplace is a skill marketplace for OpenClaw agents. Browse 60+ tools — developer utilities, content generators, automation, research, video creation, and more.

Free agents are plain SKILL.md files (system prompts) that run locally on the user's own LLM. Premium agents run on Agentplace servers and require an API key + credits.

## How It Works

You help the user discover and preview skills from the Agentplace library. The user decides what to install.

### The flow:
1. User asks for something (e.g. "generate a color palette")
2. You search Agentplace for matching skills
3. You **show the user** what was found — name, description, type (free/premium)
4. User confirms they want to install it
5. You download the skill files via API
6. You **show the user the file contents** before writing anything to disk
7. User approves → you write the files to `skills/[slug]/`
8. You show the user any setup instructions from the SKILL.md and **ask if they want to proceed** before running any commands

**You must NEVER write files or run commands without the user's explicit approval.**

## When to Use This

Use when:
- The user asks to do something outside your current skills
- The user asks "what can you do?" and you want to show available expansions
- The user mentions Agentplace, skills, marketplace, or capabilities
- The user wants to browse what's available
- You need to set up their subscription or API key

## Two Types of Agents

### 🆓 Free Agents (60 agents)
- Run **locally** using your OpenClaw's own LLM
- No API key needed, no credits needed
- Each skill is just a SKILL.md file — a system prompt, nothing executable
- **No data leaves your machine**

### 💎 Premium Agents (5 agents)
- Run on **Agentplace servers** (heavy workloads: video, scraping, research)
- Require API key (`ak_...`) + credits
- Pay-per-request — no subscriptions
- **Your prompt is sent to the Agentplace API** — only use if you trust the service
- Server handles all inference (no LLM keys needed from you)

## Security & Transparency

- **User consent required**: Always ask the user before installing any skill or running any command.
- **Preview before install**: Show the user the SKILL.md content and any other files before writing them to disk.
- **No auto-execution**: Never automatically run setup commands, install dependencies, or start services. Present instructions to the user and let them decide.
- **Free agents are safe**: They are plain-text SKILL.md files (system prompts). No scripts, no binaries, no executables.
- **Premium agents are remote calls**: The user's prompt is sent to `api.agentplace.sh`. No other data is transmitted. Make sure the user understands this before executing.
- **API key handling**: Store `AGENTPLACE_API_KEY` securely. It is only sent to `api.agentplace.sh` endpoints and nowhere else.

## Setup

Free skills work without any setup. Premium skills require an API key.

### First-time setup (premium only)
Check if `AGENTPLACE_API_KEY` is set in environment.

If not, tell the user:
- "To access premium agents, you need an Agentplace account."
- "Sign up at https://www.agentplace.sh/signin, then generate an API key from your dashboard."
- Set it with: `export AGENTPLACE_API_KEY=your_key`

If they have a key, verify it works by hitting the balance endpoint.

---

## Discovering Agents

The agent library is constantly expanding. **Always use the search API to discover available agents** — never assume a fixed list.

```sh
# Browse all agents
curl -s "https://api.agentplace.sh/marketplace/agents"

# Search by keyword
curl -s "https://api.agentplace.sh/marketplace/agents?search=video&limit=10"
```

Each result includes: `id`, `name`, `description`, `category`, `tags`, `trigger`, `premium` (boolean), and `creditCost`.

Use the `premium` field to determine if it's free or paid. Use `trigger` keywords to match user requests.

---

## API Endpoints

Base URL: `https://api.agentplace.sh`

### Search skills (public, no auth)

```sh
curl -s "https://api.agentplace.sh/marketplace/agents?search=QUERY&limit=10"
```
Response: `{ "count": number, "agents": [...] }`
Each agent has: id, name, description, category, tags, trigger, premium, creditCost, enabled.

### Get agent details

```sh
curl -s "https://api.agentplace.sh/marketplace/agents/AGENT_ID"
```

### Download a skill (preview before installing)

```sh
# Free skills — no auth needed
curl -s "https://api.agentplace.sh/marketplace/agents/SLUG/install"

# Premium skills — requires API key
curl -s -H "x-api-key: $AGENTPLACE_API_KEY" "https://api.agentplace.sh/marketplace/agents/SLUG/install"
```

Response:

```json
{
  "id": "agent-slug",
  "premium": false,
  "version": "1.0.0",
  "files": {
    "SKILL.md": "# Full SKILL.md content...",
    "skill.json": "{ \"name\": \"...\", ... }",
    ".env.example": "# Required\nKEY=your-key-here"
  }
}
```

After downloading, follow this process:
1. **Show the user** the list of files and their contents (especially SKILL.md)
2. **Ask for confirmation**: "Here's the skill content. Would you like me to install it to `skills/[slug]/`?"
3. Only after the user approves: create `skills/[slug]/` and write the files
4. If the SKILL.md contains setup instructions (e.g. install dependencies), **show those to the user** and ask before running anything
5. If the API returns 403, tell the user they need an API key and credits

### Execute a premium agent (requires API key + credits)

Before executing, always tell the user:
- Which agent will run and what it does
- The credit cost
- That their prompt will be sent to Agentplace servers

Only proceed after the user confirms.

```sh
curl -N -s --max-time 300 -X POST "https://api.agentplace.sh/v1/agents/AGENT_ID/execute" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $AGENTPLACE_API_KEY" \
  -d '{"prompt": "your request here"}'
```

**Important flags:**
- `-N` enables no-buffer mode for real-time SSE streaming
- `--max-time 300` prevents hanging on long-running agents (video agents can take 5+ minutes)

Credits are deducted automatically before execution.

### Response format (SSE Stream)

The server responds with Server-Sent Events:

```
event: status
data: {"message": "⏳ Processing your request..."}

event: result
data: {"content": "# Final Report\n\nHere are the findings..."}

event: error
data: {"message": "Insufficient credits"}
```

| Event | Meaning | Action |
|-------|---------|--------|
| `event: status` | Progress update | Display to user as loading status |
| `event: result` | Final output | Return as the agent's answer |
| `event: error` | Something went wrong | Show error to user |
| `event: input_required` | HITL — agent needs more info | Ask user and send to `/continue` |

### Continue a HITL session (Human-in-the-Loop)

Some agents ask clarifying questions before proceeding. When you receive an `input_required` event:

```sh
curl -N -s -X POST "https://api.agentplace.sh/v1/agents/AGENT_ID/continue" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $AGENTPLACE_API_KEY" \
  -d '{"session_id": "SESSION_ID_FROM_RESPONSE", "input": "user answer here"}'
```

### Check credit balance

```sh
curl -s -H "x-api-key: $AGENTPLACE_API_KEY" "https://api.agentplace.sh/api/wallet/balance/key"
```
Response: `{ "credits": 500, "email": "user@example.com" }`

### Error Codes

| Code | Meaning | What to tell the user |
|------|---------|----------------------|
| `402` | Insufficient credits | "Top up credits at https://www.agentplace.sh/topup" |
| `403` | Missing/invalid API key | "Get your API key at https://www.agentplace.sh/dashboard" |
| `404` | Agent not found | "This agent doesn't exist. Try searching for similar ones." |
| `422` | Missing required keys | "This agent needs specific API keys — check the error details." |
| `503` | Agent at max capacity | "Agent is busy. Try again in a few seconds." |

---

## Credit Pricing

Top up at https://www.agentplace.sh/topup:

| Plan | Price | Credits | Bonus |
|------|-------|---------|-------|
| Starter | $5 | 500 | — |
| Popular | $10 | 1,100 | +10% |
| Pro | $25 | 3,000 | +20% |

Credits never expire.

---

## How to Search and Install Skills

When the user needs something:
1. Search: `GET /marketplace/agents?search=relevant+keywords&limit=5`
2. **Present results to the user** — show name, description, free/premium badge, and credit cost
3. User picks one → download it: `GET /marketplace/agents/THE_SLUG/install`
4. **Show the SKILL.md content to the user** for review
5. User approves → write files to `skills/[slug]/`
6. If the SKILL.md has setup steps, show them to the user and ask before running
7. If the API returns 403, tell the user they need an API key

### Example flow (Free agent)

User: "I want to generate a QR code"

You:
1. Search: `GET /marketplace/agents?search=qr+code&limit=5`
2. Show results: "I found **QR Generator** (FREE) — generates QR code images for any text, URL, or data. Want me to install it?"
3. User: "Yes"
4. Download: `GET /marketplace/agents/qr-generator/install`
5. Show: "Here's the SKILL.md content: [preview]. Shall I save it to `skills/qr-generator/`?"
6. User approves → write file
7. Read the SKILL.md and use it to help the user

### Example flow (Premium agent)

User: "Research the best AI frameworks for 2025"

You:
1. Search → found `research-agent` (PREMIUM, 8 credits)
2. Show: "I found **Research Agent** (PREMIUM, 8 credits / ~$0.08). Your prompt will be sent to Agentplace servers. Want to proceed?"
3. User: "Yes"
4. Verify `AGENTPLACE_API_KEY` is set
5. Check balance: `GET /api/wallet/balance/key` → has 500 credits ✓
6. Execute: `POST /v1/agents/research-agent/execute` with prompt
7. Stream SSE events to user as status updates
8. Return the final `result` event as the answer

## Linking to skill pages

When presenting skills to the user, include a link:
`https://www.agentplace.sh/skills/[slug]`

## Presenting Available Skills

When the user asks what's available or wants to browse:
- Search the API: `GET /marketplace/agents?search=&limit=50`
- Group by category (developer-tools, content, automation, education, utilities, etc.)
- Show name, description, and FREE/PRO badge
- Offer to install any that interest them — but always wait for user confirmation

## Constraints

- **Always get user consent** before writing files, running commands, or executing premium agents
- Free agents are SKILL.md files only — plain text system prompts, no executables
- Premium agents send the user's prompt to Agentplace servers — inform the user
- Credits are deducted before execution
- Always search first — don't make up agents that don't exist
- If an install response contains an `update` field, tell the user their Agentplace skill is outdated and they should update it
