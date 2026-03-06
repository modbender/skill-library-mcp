---
name: multi-agent-blueprint
version: 2.0.0
description: Production-tested blueprint for building 5-10 agent teams in OpenClaw with cross-agent routing, Telegram integration, and role-based architecture
emoji: 🏗️
tags:
  - multi-agent
  - team
  - orchestration
  - blueprint
  - telegram
  - routing
  - cost-optimization
---

# Multi-Agent Blueprint — Build Your AI Team

A production-tested template for setting up **5-10 specialized AI agents** that work together as a team. Based on a real deployment running 10 agents across Telegram with cross-agent routing, model tiering, and centralized file management.

## What You Get

- **Agent role templates** with SOUL.md, AGENTS.md, IDENTITY.md, USER.md
- **Cross-agent routing** via `sessions_send` with working session keys
- **Model tiering** strategy (Opus/Sonnet/Haiku) for cost optimization
- **Telegram multi-bot** setup with DM isolation and group @mentions
- **File Master pattern** — centralize file ops through one agent
- **Notion Master pattern** — centralize database ops through one agent
- **Fallback chains** — resilient multi-provider model routing
- **Cost optimization** config (caching, heartbeats on local models, context pruning)
- **RAG/Memory** setup for persistent knowledge across sessions
- **Group chat brainstorming** — multiple agents in one conversation

## Architecture

```
┌─────────────────────────────────────────────┐
│                   USER                       │
│         (Telegram / Discord / WhatsApp)      │
└──────────┬──────────────────────┬───────────┘
           │ DM                   │ @mention
     ┌─────▼─────┐         ┌─────▼─────┐
     │ CENTRAL   │         │  GROUP    │
     │ (Coordi-  │◄───────►│  CHAT     │
     │  nator)   │ routes  │ (all bots)│
     └─────┬─────┘         └───────────┘
           │ sessions_send
     ┌─────┼─────┬──────┬──────┬──────┐
     ▼     ▼     ▼      ▼      ▼      ▼
   TECH  FINANCE SALES HEALTH MKTG  DATA
    │                                  │
    ▼                                  ▼
   NAS                             NOTION
  (File Master)                  (DB Master)
```

## Quick Start

### 1. Plan Your Team

Pick 3-10 roles based on your needs:

| Role | Model Tier | Example Tasks |
|------|-----------|---------------|
| Coordinator | Opus | Route tasks, oversee projects, daily briefings |
| Tech/Infra | Opus/Sonnet | DevOps, file management, system admin |
| Finance | Sonnet | Invoices, budgets, tax prep, contracts |
| Sales | Haiku | Lead gen, outreach scripts, deal tracking |
| Marketing | Haiku | Content creation, SEO, social media |
| Health | Sonnet | Fitness tracking, meal plans, habit coaching |
| Data/Notion | Sonnet | Database ops, reporting, documentation |
| DevOps | Haiku | Monitoring, alerts, uptime checks |
| E-Commerce | Sonnet | Store audits, product strategy, analytics |
| Social/Brand | External* | Twitter/X, LinkedIn, content scheduling |

*Social agents can use specialized providers like xAI/Grok for platform-native tone.

### 2. Create Agent Directories

```bash
# For each agent:
mkdir -p ~/.openclaw/workspace-{agentname}/memory
mkdir -p ~/.openclaw/agents/{agentname}/agent
```

### 3. Configure OpenClaw

Add each agent to `openclaw.json` → `agents.list`:

```json5
{
  "id": "finance",
  "name": "finance",
  "workspace": "~/.openclaw/workspace-finance",
  "agentDir": "~/.openclaw/agents/finance/agent",
  "model": "anthropic/claude-sonnet-4-5"
}
```

Enable cross-agent communication:

```json5
{
  "agentToAgent": { "enabled": true }
}
```

### 4. Create Agent Files

Each agent needs 4 files in their `agentDir`:

#### IDENTITY.md
```markdown
# IDENTITY.md
- **Name:** Atlas
- **Creature:** AI Finance & Legal Advisor
- **Vibe:** Professional, precise, trustworthy
```

#### SOUL.md (Personality & Rules)
```markdown
# SOUL.md
You are Atlas. Finance & Legal specialist.

PERSONALITY:
- Professional but approachable
- Numbers-driven, always backs claims with data
- Proactively flags risks and deadlines

EXPERTISE:
- Invoice management, expense tracking
- Tax preparation and compliance
- Contract review and negotiation support

RESPONSE LENGTH:
- DEFAULT: 2-5 sentences. Telegram, not blog posts.
- Short question = short answer. "Done.", "Yes.", "Sent." are fine.
- Longer responses ONLY for: financial breakdowns, step-by-step guides, or when explicitly asked.
- No introductions. Get to the point.
- No repeating the question back.
```

#### AGENTS.md (Routing Table)
```markdown
# AGENT OPERATING SYSTEM — Atlas

## My Role
Finance & Legal. Invoices, budgets, contracts, tax.

## Cross-Agent Routing
| What | Where | How |
|------|-------|-----|
| Coordination | Central | sessions_send(sessionKey="agent:central:main", ...) |
| File Storage | Tech | sessions_send(sessionKey="agent:techops:main", ...) |
| Database/Notion | Data | sessions_send(sessionKey="agent:data:main", ...) |
| Sales Numbers | Sales | sessions_send(sessionKey="agent:sales:main", ...) |

## What I Handle
- Invoice creation and tracking
- Budget reports and forecasts
- Contract review
- Tax document preparation

## What I DON'T Handle
- File storage → Tech agent (File Master)
- Database updates → Data agent (Notion Master)
- Marketing spend analysis → Marketing agent
```

#### USER.md
```markdown
# USER.md
- **Name:** [Your name]
- **Timezone:** Europe/Berlin
- **Business:** [Your business]
- **Language:** English (casual)
```

### 5. Telegram Multi-Bot Setup

Create a Telegram bot per agent via @BotFather, then configure:

```json5
// openclaw.json
{
  // CRITICAL: This prevents session collision between bots
  "session": { "dmScope": "per-account-channel-peer" },

  "channels": {
    "telegram": {
      // DO NOT put botToken here at top level — causes double responses
      "accounts": {
        "finance": {
          "botToken": "YOUR_BOT_TOKEN",
          "dmPolicy": "allowlist",
          "allowFrom": ["YOUR_TELEGRAM_ID"],
          "groups": {
            "-YOUR_GROUP_ID": { "requireMention": true }
          }
        }
      }
    }
  },

  "bindings": [
    {
      "agentId": "finance",
      "match": { "channel": "telegram", "accountId": "finance" }
    }
  ]
}
```

**Critical settings:**
- `dmScope: "per-account-channel-peer"` — prevents session collision between bots
- `requireMention: true` — bots only respond when @mentioned in groups
- NO top-level `botToken` — causes duplicate responses
- Each bot needs its own `accountId` matching a binding

### 6. Model Tiering & Fallback Chains

```json5
{
  "models": {
    "fallbackOrder": [
      "anthropic/claude-opus-4-6",
      "anthropic/claude-sonnet-4-5",
      "google-gemini-cli/gemini-2.5-flash",
      "ollama/llama3.2:3b",
      "openrouter/anthropic/claude-sonnet-4"
    ]
  }
}
```

**Why fallback chains matter:**
- Primary provider down? Auto-switches to next.
- Claude rate-limited? Falls back to Gemini.
- Internet out? Local Ollama keeps heartbeats alive.
- OpenRouter as last resort (pay-per-token).

### 7. Cost Optimization Config

```json5
{
  "agents": {
    "defaults": {
      // Heartbeats on FREE local model — saves hundreds of API calls/day
      "heartbeat": { "every": "30m", "model": "ollama/llama3.2:3b" },

      // Auto-prune old context to reduce token usage
      "contextPruning": { "mode": "cache-ttl", "ttl": "5m" },

      // Memory search with caching
      "memorySearch": { "enabled": true, "cache": { "enabled": true } },

      // Enable prompt caching (huge savings on Anthropic)
      "models": {
        "anthropic/claude-opus-4-6": { "params": { "cacheRetention": "long" } },
        "anthropic/claude-sonnet-4-5": { "params": { "cacheRetention": "long" } },
        "anthropic/claude-haiku-4-5": { "params": { "cacheRetention": "none" } }
      }
    }
  }
}
```

### 8. RAG/Memory Setup

Give agents persistent memory across session resets:

```json5
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "providers": ["local"],   // local = free, no API costs
        "search": { "mode": "hybrid" },  // BM25 + vector
        "cache": { "enabled": true, "maxEntries": 50000 }
      }
    }
  }
}
```

Agents store important context in `memory/*.md` files before session compaction. On next session, `memory_search` retrieves relevant snippets automatically.

## Design Patterns

### File Master Pattern
Route ALL file operations through ONE agent:
- Other agents never touch filesystem/NAS directly
- File Master handles storage, retrieval, backups
- Single point of truth for file locations
- Only one agent needs SSH/NAS credentials

```
Agent → sessions_send → File Master → SSH → NAS
                              ↓
                        Confirmation back
```

### Notion/Database Master Pattern
Route ALL database operations through ONE agent:
- Centralizes API credentials
- Prevents conflicting writes
- One agent knows the full schema

```
Agent → sessions_send → DB Master → Notion API → Database
                              ↓
                        Confirmation back
```

### Coordinator Pattern
One central agent acts as router:
- Receives all user requests first
- Routes to specialist agents via `sessions_send`
- Collects results and reports back
- Best for users who want one "front door"

### Specialist Direct Pattern
User talks directly to specialist when they know what they need:
- DM Finance Agent for invoice questions
- DM Sales Agent for deal strategy
- DM Health Agent for fitness advice
- Fastest path — no routing overhead

### Group Brainstorm Pattern
Multiple agents in one Telegram group with `requireMention: true`:
- @mention specific agents for their expertise
- Agents can see each other's responses
- Great for strategy sessions, planning, reviews

## Cross-Agent Communication

Agents talk to each other via `sessions_send`:

```javascript
// From any agent's tool call:
sessions_send({
  sessionKey: "agent:techops:main",
  message: "Store this file on NAS: quarterly-report.pdf at /finance/reports/"
})
```

**Session key format:** `agent:{agentId}:main`

**Important:** The receiving agent processes the message in its own session with its own tools and permissions. Responses route back automatically.

## Model Tiering Strategy

| Tier | Model | Monthly Cost* | Best For |
|------|-------|--------------|----------|
| **Premium** | Opus 4.6 | $$$ | Coordinator + Tech Lead (complex reasoning, multi-step) |
| **Standard** | Sonnet 4.5 | $$ | Finance, Health, Data (good reasoning, cheaper) |
| **Economy** | Haiku 4.5 | $ | Sales, Marketing, DevOps (simple tasks, fast) |
| **Free** | Ollama local | $0 | Heartbeats, health checks |
| **External** | xAI Grok / GPT | Varies | Specialized tasks (social media, research) |

*With Claude subscription, most usage is covered. Haiku agents are nearly free.

**Rule of thumb:** Use the cheapest model that gets the job done. You can always upgrade individual agents later.

## Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | All agents on Opus | Use tiering — Haiku handles 70% of tasks fine |
| 2 | No `dmScope: per-account-channel-peer` | Session collision — bots share state incorrectly |
| 3 | No `requireMention: true` in groups | Bots respond to every message (chaos) |
| 4 | Top-level `botToken` in telegram config | Causes double responses — put tokens in `accounts` only |
| 5 | Missing `agentToAgent.enabled: true` | Cross-agent routing silently fails |
| 6 | No memory flush before compaction | Context lost on session reset |
| 7 | Multiple agents doing file ops directly | Inconsistent state, race conditions |
| 8 | Same workspace for multiple agents | File conflicts and memory collision |
| 9 | No fallback chain | Single provider outage = all agents down |
| 10 | Forgetting to sync agentDir ↔ workspace | Config drift between the two locations |

## Scaling Guide

### Solo Founder — Start Small (3 Agents)
```
Coordinator (Opus) → Tech (Sonnet) → Sales (Haiku)
```
Covers 80% of needs. Add more only when a clear role gap appears.

### Growing Business (5-7 Agents)
```
Coordinator → Tech → Finance → Sales → Marketing
                                    → Data/Notion
```

### Full Team (8-10 Agents)
```
Coordinator → Tech (File Master)
           → Finance/Legal
           → Sales
           → Marketing
           → Health/Personal
           → Data/Notion (DB Master)
           → DevOps (Monitoring)
           → E-Commerce
           → Social/Brand
```

### Cost Estimates
| Team Size | Claude Subscription | Extra API Costs | Total |
|-----------|-------------------|-----------------|-------|
| 3 agents | ~$20/mo | ~$0-5 | ~$20-25/mo |
| 5 agents | ~$20/mo | ~$5-10 | ~$25-30/mo |
| 10 agents | ~$20/mo | ~$10-20 | ~$30-40/mo |

*Heartbeats on Ollama = $0. Haiku agents barely register. Prompt caching reduces costs 50-90%.*

## Session Management

### Auto-Reset
Configure session resets to prevent context overflow:
```json5
{
  "session": {
    "maxIdleMinutes": 45,
    "dailyResetUtc": "04:00"
  }
}
```

### Memory Persistence
Agents should save important context before reset:
```markdown
<!-- In agent's BOOTSTRAP.md -->
## Memory Flush
Before session compaction, save key decisions, dates, and action items
to memory/*.md files using the write tool.
```

## FAQ

**Q: Do all agents need their own Telegram bot?**
A: Only if you want to DM them directly. Agents can work purely via `sessions_send` (backend-only) without a Telegram bot.

**Q: Can agents share a workspace?**
A: No. Each agent needs its own workspace to avoid file conflicts and memory collision.

**Q: What happens when context fills up?**
A: OpenClaw auto-compacts sessions. Enable memory flush so agents save important context to `memory/*.md` before compaction.

**Q: Can I mix providers (Anthropic + Google + Ollama + xAI)?**
A: Yes. Each agent can have a different model and provider. Use fallback chains for resilience.

**Q: How do I debug cross-agent routing?**
A: Check `agentToAgent.enabled: true` in config. Test with a simple ping:
```
sessions_send(sessionKey="agent:techops:main", message="ping — reply pong")
```

**Q: How do I add a new agent to an existing team?**
A: Create workspace + agentDir, add to `agents.list`, create 4 .md files, add Telegram bot (optional), add to other agents' routing tables, restart gateway.

**Q: Can agents call external APIs?**
A: Yes, via `exec` (curl/scripts) or dedicated skills. Keep API keys in `.env`, not in agent files.

**Q: What about rate limits?**
A: Fallback chains handle this automatically. If Claude rate-limits, the request falls back to the next provider. Prompt caching also reduces token consumption significantly.

## Changelog

### v2.0.0
- Added Notion/Database Master pattern
- Added RAG/Memory setup guide
- Added fallback chain configuration
- Added session management section
- Expanded cost estimates with real numbers
- Added 10 common mistakes (was 7)
- Added group brainstorm pattern
- Added FAQ entries for new agents, external APIs, rate limits
- All examples fully in English
- Improved scaling guide with cost table

### v1.1.0
- Generalized all agent names and examples
- Removed specific setup references

### v1.0.0
- Initial release
