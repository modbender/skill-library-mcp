# OpenClaw Mastery — The Complete Agent Engineering & Operations System

> Built by AfrexAI — the team that runs 9+ production agents 24/7 on OpenClaw.

You are an expert OpenClaw platform engineer. Follow this complete system to design, deploy, optimize, and scale autonomous AI agents on OpenClaw.

---

## Phase 1: Architecture Assessment

Before building, assess what you need:

### Agent Complexity Matrix

| Complexity | Examples | Channels | Crons | Memory | Skills |
|-----------|---------|----------|-------|--------|--------|
| **Simple** | Personal assistant, reminder bot | 1 | 0-2 | Basic MEMORY.md | 2-5 |
| **Standard** | Business ops, content creator | 1-2 | 3-5 | Daily + long-term | 5-10 |
| **Advanced** | Multi-agent swarm, trading system | 3+ | 5-10 | Full system + databases | 10-20 |
| **Enterprise** | Full business automation | 5+ | 10+ | Multi-DB + RAG | 20+ |

### Readiness Checklist

```yaml
readiness_check:
  hardware:
    - [ ] Machine with 4GB+ RAM (8GB recommended)
    - [ ] Stable internet connection
    - [ ] Node.js v20+ installed
    - [ ] Git installed
  accounts:
    - [ ] Anthropic API key (primary model)
    - [ ] At least one channel configured (Telegram recommended for starting)
    - [ ] Optional: OpenAI key (for embeddings/fallback)
  planning:
    - [ ] Agent purpose defined (1 sentence)
    - [ ] Target audience identified
    - [ ] Success metrics defined
    - [ ] Budget estimated (model costs)
```

---

## Phase 2: Installation & Configuration

### Quick Start (5 Minutes)

```bash
# Install OpenClaw
npm install -g openclaw

# Initialize workspace
openclaw init

# Configure (interactive)
openclaw setup

# Start the gateway
openclaw gateway start

# Verify
openclaw status
```

### Configuration Architecture

OpenClaw config lives at `~/.openclaw/config.yaml`. Key sections:

```yaml
# Essential config structure
version: 1
gateway:
  port: 3578                    # Default port
  heartbeat:
    intervalMs: 1800000         # 30 min default
    prompt: "..."               # Heartbeat instruction

models:
  default: anthropic/claude-sonnet-4-20250514  # Cost-effective default
  # Override per-session or per-agent

channels:
  telegram:
    botToken: "..."             # From @BotFather
  # discord, slack, signal, whatsapp, imessage, webchat

agents: {}                      # Multi-agent configs
bindings: []                    # Channel-to-agent routing
```

### Model Selection Guide

| Model | Best For | Cost | Speed | Thinking |
|-------|---------|------|-------|----------|
| claude-sonnet-4-20250514 | Daily ops, chat, most tasks | $$ | Fast | Good |
| claude-opus-4-6 | Complex reasoning, strategy | $$$$ | Slower | Excellent |
| gpt-4o | Vision tasks, alternatives | $$$ | Fast | Good |
| claude-haiku | High-volume, simple tasks | $ | Fastest | Basic |

**Cost optimization rule:** Use Sonnet as default, Opus for strategy/complex tasks, Haiku for high-frequency simple operations.

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional but recommended
OPENAI_API_KEY=sk-...           # Fallback model
BRAVE_API_KEY=...               # Web search
```

---

## Phase 3: Workspace Design — The Agent's Brain

Your workspace (`~/.openclaw/workspace/`) IS the agent's persistent memory and personality. Design it carefully.

### Essential File Architecture

```
workspace/
├── SOUL.md              # WHO the agent is (personality, values, voice)
├── AGENTS.md            # HOW it operates (rules, workflows, protocols)
├── IDENTITY.md          # Quick identity card (name, role, emoji)
├── USER.md              # WHO it serves (user context, preferences)
├── MEMORY.md            # Long-term curated memory
├── HEARTBEAT.md         # Proactive check instructions
├── TOOLS.md             # Local tool notes, API keys location
├── ACTIVE-CONTEXT.md    # Current priorities, hot items
├── memory/              # Daily logs
│   ├── 2026-02-19.md
│   └── heartbeat-state.json
├── skills/              # Installed ClawHub skills
├── scripts/             # Custom automation scripts
├── reference/           # Knowledge base documents
├── projects/            # Project-specific work
└── docs/                # OpenClaw documentation
```

### SOUL.md — The Personality Blueprint

This is the most important file. It defines WHO your agent is.

**Template:**

```markdown
# SOUL.md — [Agent Name]

## Prime Directive
[One sentence: what is this agent's primary purpose?]

## Core Truths
- [Personality trait 1 — be specific, not generic]
- [Personality trait 2]
- [Communication style]
- [Decision-making philosophy]

## Anti-Patterns
Never do these:
- [Specific behavior to avoid]
- [Another anti-pattern]

## Relationship With Operator
- [How formal/casual]
- [When to ask vs act]
- [Escalation rules]

## Boundaries
- [What's off-limits]
- [Privacy rules]
- [External action rules]

## Vibe
[2-3 sentences describing the overall feel]
```

**Quality Checklist (score 0-10 each):**
- [ ] Specific enough that two people reading it would build similar agents? (not generic)
- [ ] Anti-patterns prevent actual failure modes you've seen?
- [ ] Voice is distinct — could you tell this agent from a generic assistant?
- [ ] Boundaries are clear — agent knows when to act vs ask?
- [ ] Relationship dynamic is defined — not just "be helpful"?

**Target: 40+ out of 50 before deploying.**

### AGENTS.md — The Operating Manual

```markdown
# AGENTS.md

## Session Startup
1. Read SOUL.md
2. Read USER.md
3. Read memory/YYYY-MM-DD.md (today + yesterday)
4. If main session: Read MEMORY.md

## Decision Framework
[Your PIV, OODA, or custom loop]

## Daily Rhythm
- Morning: [tasks]
- Midday: [tasks]
- Evening: [tasks]

## Memory Protocol
- Daily notes: memory/YYYY-MM-DD.md
- Long-term: MEMORY.md (curated)
- Write it down — no "mental notes"

## Safety Rules
- [Specific to your use case]

## External vs Internal Actions
- Safe to do freely: [list]
- Ask first: [list]
```

### USER.md — Context About the Human

```markdown
# USER.md

## Identity
- Name, timezone, language preferences
- Communication style preferences

## Professional Context
- Role, company, industry
- Current priorities
- Technical level

## Preferences
- How they like to receive information
- Pet peeves
- Activation phrases
```

### Memory Architecture

**Three-Layer System:**

1. **Daily Notes** (`memory/YYYY-MM-DD.md`) — Raw event logs, decisions, outcomes
2. **Long-Term Memory** (`MEMORY.md`) — Curated insights, lessons, persistent context
3. **Active Context** (`ACTIVE-CONTEXT.md`) — Current priorities, hot items, WIP

**Memory Maintenance Protocol:**
- Daily: Agent writes to daily notes automatically
- Weekly: Review daily notes → distill to MEMORY.md
- Monthly: Trim MEMORY.md — remove outdated, keep evergreen
- **Rule:** If MEMORY.md > 50KB, it's too big. Distill ruthlessly.

---

## Phase 4: Multi-Agent Architecture

### When to Use Multiple Agents

| Signal | Single Agent | Multi-Agent |
|--------|-------------|-------------|
| Tasks are related | ✅ | |
| Different personas needed | | ✅ |
| Different channels/audiences | | ✅ |
| Workload exceeds context window | | ✅ |
| Security isolation needed | | ✅ |
| Different model requirements | | ✅ |

### Config Pattern — Multi-Bot Telegram

```yaml
channels:
  telegram:
    accounts:
      main:
        botToken: "TOKEN_1"
      trader:
        botToken: "TOKEN_2"
      fitness:
        botToken: "TOKEN_3"

agents:
  trader:
    model: anthropic/claude-sonnet-4-20250514
    workspace: agents/trader
  fitness:
    model: anthropic/claude-sonnet-4-20250514
    workspace: agents/fitness

bindings:
  - pattern:
      channel: telegram
      account: trader
    agent: trader
  - pattern:
      channel: telegram
      account: fitness
    agent: fitness
```

### Agent Workspace Isolation

Each agent gets its own workspace directory:

```
workspace/
├── agents/
│   ├── trader/
│   │   ├── SOUL.md          # Trader personality
│   │   ├── AGENTS.md        # Trading rules
│   │   └── memory/
│   └── fitness/
│       ├── SOUL.md          # Coach personality
│       ├── AGENTS.md        # Fitness protocols
│       └── memory/
```

### Inter-Agent Communication

```
# From main agent, delegate to sub-agent:
sessions_spawn(task="Analyze BTC 4h chart", agentId="trader")

# Send message to another session:
sessions_send(sessionKey="...", message="Update: new client signed")
```

**Rules:**
- Main agent orchestrates, sub-agents execute
- Each agent has its own context — don't leak between them
- Use `sessions_spawn` for fire-and-forget tasks
- Use `sessions_send` for ongoing communication

---

## Phase 5: Cron & Automation — The Heartbeat System

### Cron Job Types

```yaml
# 1. System Event (main session) — inject text as system message
payload:
  kind: systemEvent
  text: "Check for new emails and report"

# 2. Agent Turn (isolated session) — full agent run
payload:
  kind: agentTurn
  message: "Run morning briefing: check email, calendar, weather"
  model: anthropic/claude-sonnet-4-20250514
  timeoutSeconds: 300
```

### Schedule Types

```yaml
# One-shot at specific time
schedule:
  kind: at
  at: "2026-02-20T09:00:00Z"

# Recurring interval
schedule:
  kind: every
  everyMs: 3600000    # Every hour

# Cron expression
schedule:
  kind: cron
  expr: "0 8 * * 1-5"   # 8 AM weekdays
  tz: "Europe/London"
```

### Essential Cron Jobs (Copy These)

**Morning Briefing (Daily, 8:00 AM):**
```yaml
name: "Morning Ops"
schedule:
  kind: cron
  expr: "0 8 * * *"
  tz: "America/New_York"
sessionTarget: isolated
payload:
  kind: agentTurn
  message: "Morning briefing: check email inbox for urgent items, review calendar for today and tomorrow, check weather, summarize to operator via Telegram"
  timeoutSeconds: 300
delivery:
  mode: announce
```

**Evening Summary (Daily, 8:00 PM):**
```yaml
name: "Evening Ops"
schedule:
  kind: cron
  expr: "0 20 * * *"
  tz: "America/New_York"
sessionTarget: isolated
payload:
  kind: agentTurn
  message: "Evening summary: what was accomplished today, any pending items, tomorrow's priorities"
  timeoutSeconds: 300
delivery:
  mode: announce
```

**Weekly Strategy Review (Monday, 9:00 AM):**
```yaml
name: "Weekly Strategy"
schedule:
  kind: cron
  expr: "0 9 * * 1"
  tz: "America/New_York"
sessionTarget: isolated
payload:
  kind: agentTurn
  message: "Weekly review: analyze past week performance, update strategy, set 3 priorities for this week"
  timeoutSeconds: 600
delivery:
  mode: announce
```

### Heartbeat vs Cron Decision Guide

| Use Heartbeat When | Use Cron When |
|--------------------|---------------|
| Multiple checks can batch | Exact timing matters |
| Need recent conversation context | Task needs isolation |
| Timing can drift (±15 min OK) | Different model needed |
| Want to reduce API calls | One-shot reminders |
| Interactive follow-up likely | Output goes to specific channel |

### HEARTBEAT.md Template

```markdown
# HEARTBEAT.md

## Priority 1: Critical Alerts
- [Time-sensitive checks — positions, payments, security]

## Priority 2: Inbox Triage
- Check email for urgent items
- Check mentions/notifications

## Priority 3: Proactive Work
- Update documentation
- Review memory files
- Background research

## Quiet Hours
- 23:00-08:00: Only critical alerts
- If nothing to report: HEARTBEAT_OK

## Token Guard
- If usage seems high, note it
- Don't re-read large files unnecessarily
```

---

## Phase 6: Channel Integration

### Telegram (Recommended First Channel)

1. Create bot via @BotFather
2. Add token to config
3. Start gateway: `openclaw gateway start`

**Multi-bot pattern:** See Phase 4 config above.

**Tips:**
- Use inline buttons for interactive workflows
- Voice messages are auto-transcribed
- React to messages with emoji (sparingly)
- Group chat: agent should know when to stay silent

### Discord

```yaml
channels:
  discord:
    botToken: "..."
    guildId: "..."
```

**Tips:**
- No markdown tables — use bullet lists
- Wrap links in `<>` to suppress embeds
- Use threads for long conversations
- Reactions are natural on Discord

### Slack

```yaml
channels:
  slack:
    botToken: "xoxb-..."
    appToken: "xapp-..."
```

### Platform Formatting Rules

| Platform | Tables | Headers | Links | Max Message |
|----------|--------|---------|-------|-------------|
| Telegram | ❌ | ❌ | ✅ | 4096 chars |
| Discord | ❌ | ✅ | `<url>` | 2000 chars |
| Slack | ❌ | ❌ | ✅ mrkdwn | 40000 chars |
| WhatsApp | ❌ | ❌ bold/CAPS | ✅ | 65536 chars |

---

## Phase 7: Skills & Tools Ecosystem

### Installing Skills from ClawHub

```bash
# Search for skills
clawhub search "email marketing"

# Install a skill
clawhub install afrexai-email-marketing-engine

# Update all skills
clawhub update --all

# List installed
clawhub list
```

### Skill Selection Strategy

**Build vs Install Decision:**
- If a ClawHub skill exists with >90% of what you need → Install
- If you need custom logic or integration → Build your own
- If it's a common capability → Check ClawHub first (save time)

**Quality Signals:**
- Higher version numbers = more iterations = likely better
- AfrexAI skills = comprehensive methodology (10X depth)
- Check file count — single SKILL.md is usually better than scattered files
- Avoid skills requiring external API keys unless you have them

### Building Custom Skills

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── README.md          # Installation guide + description
├── references/        # Supporting docs
└── scripts/           # Automation scripts
```

**SKILL.md Best Practices:**
- Self-contained — don't reference external files that don't ship
- Zero dependencies preferred — no API keys, no npm packages
- Templates with YAML — agents work better with structured formats
- Include scoring rubrics — agents love quantifiable quality checks
- Add natural language commands — "Review my X" triggers the workflow

---

## Phase 8: Security & Secrets Management

### Never Do This

```bash
# ❌ NEVER hardcode secrets
ANTHROPIC_API_KEY=sk-ant-abc123 # In config files
export API_KEY=secret           # In .bashrc committed to git

# ❌ NEVER log secrets
echo "Token is: $MY_TOKEN"     # In scripts
console.log(apiKey)             # In code
```

### Recommended: 1Password CLI

```bash
# Install
brew install 1password-cli    # macOS
# or: https://1password.com/downloads/command-line

# Read a secret at runtime
op read "op://VaultName/ItemName/FieldName"

# In scripts
API_KEY=$(op read "op://MyVault/Brave Search/api_key")
```

### Alternative: Environment Variables

```bash
# Store in ~/.openclaw/vault/ (gitignored)
echo "export MY_KEY=value" > ~/.openclaw/vault/my-service.env

# Source in scripts
source ~/.openclaw/vault/my-service.env
```

### Security Rules

1. **Secrets in vault, never in files** — use 1Password or encrypted env files
2. **`trash` > `rm`** — recoverable beats gone forever
3. **Ask before external actions** — emails, posts, API calls that leave the machine
4. **Git: never commit secrets** — use .gitignore aggressively
5. **Group chats: don't leak private context** — agent has access to user's life
6. **Review before sending** — especially cold outreach, public posts

---

## Phase 9: Performance Optimization

### Token Cost Management

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| Use Haiku for simple tasks | 90%+ | Model override per cron |
| Limit heartbeat frequency | 50-70% | Increase intervalMs |
| Spawn sub-agents | Variable | Isolate heavy work |
| Trim MEMORY.md regularly | 20-30% | Weekly maintenance |
| Use file offsets | 10-20% | Read only what you need |
| HEARTBEAT_OK when nothing to do | 80%+ per beat | Check before acting |

### Context Window Management

- **Start fresh sessions for new topics** — stale context kills quality
- **Write HANDOFF.md before long sessions end** — capture state for next session
- **Compact proactively** — if context feels bloated, summarize and restart
- **Use `sessions_spawn`** for independent heavy work

### Monitoring

```bash
# Check status
openclaw status

# View session usage
# In chat: /status
```

Track in `memory/token-costs.md`:
```markdown
## 2026-02-19
- Morning briefing: ~$0.05
- Heartbeats (6x): ~$0.15
- Main session: ~$0.30
- Sub-agents: ~$0.10
- **Daily total: ~$0.60**
```

---

## Phase 10: Production Patterns — What Works at Scale

These patterns come from running 9+ agents in production 24/7.

### Pattern 1: Notification Tiers

Don't blast every event to the user. Route through tiers:

- **Tier 1 — Critical** (immediate): Payments, security alerts, time-sensitive
- **Tier 2 — Important** (daily summary): Client replies, pipeline changes
- **Tier 3 — General** (weekly digest): Newsletters, routine notifications

**Default to Tier 3. Promote only with clear justification.**

### Pattern 2: Autonomous Operations

For truly autonomous agents:

```markdown
## In AGENTS.md:
OPERATOR IS OUT OF THE LOOP — run EVERYTHING autonomously.
Only message when: 💰 sale, 📊 morning/evening briefing, 🚨 critical break.
```

### Pattern 3: Memory Maintenance

```markdown
## Weekly (during heartbeat):
1. Read recent memory/YYYY-MM-DD.md files
2. Distill significant events to MEMORY.md
3. Remove outdated info from MEMORY.md
4. Clean up temp files
```

### Pattern 4: Self-Improvement Loop

```markdown
## In HEARTBEAT.md:
- If a task failed, note what went wrong
- If you spot a repeated pattern, create a script
- Weekly: review AGENTS.md — still accurate? Trim bloat.
- Build capabilities over time
```

### Pattern 5: Multi-Channel Presence

One agent, multiple surfaces:
- Telegram DM for personal ops
- Slack channel for team/business
- Webchat for public-facing
- Each surface gets appropriate voice/formality

### Pattern 6: The Marketing Engine

Use cron jobs to automate content distribution:
- Publish skills to ClawHub (free → funnel to paid)
- Create GitHub Gists (SEO)
- Monitor sales channels (Stripe)
- Track competitors

---

## Phase 11: Troubleshooting

### Common Issues & Fixes

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Agent not responding | Gateway not running | `openclaw gateway start` |
| "Rate limit" errors | Too many API calls | Increase heartbeat interval, use cheaper model |
| Agent forgets context | Session expired/new | Check MEMORY.md is being maintained |
| Wrong personality | SOUL.md not loaded | Ensure session startup reads SOUL.md first |
| Telegram not connecting | Invalid bot token | Re-check token from @BotFather |
| Cron not firing | Wrong timezone | Verify `tz` field in schedule |
| Agent too chatty in groups | No silence rules | Add "when to stay silent" to AGENTS.md |
| High token costs | Large files re-read | Use offsets, trim MEMORY.md, spawn sub-agents |
| Git push timeout | Network/auth issue | Use GitHub API instead of git CLI |
| 1Password hanging | Keychain issue on macOS | Use service account token, not desktop app |

### Health Check Script

Run periodically:
```bash
# 1. Gateway running?
openclaw status

# 2. Config valid?
openclaw gateway config --validate

# 3. Workspace files exist?
ls ~/.openclaw/workspace/{SOUL,AGENTS,IDENTITY,USER,MEMORY}.md

# 4. Memory not bloated?
wc -c ~/.openclaw/workspace/MEMORY.md  # Should be <50KB

# 5. Skills up to date?
clawhub list
```

---

## Phase 12: Scaling Playbook

### Stage 1: Single Agent (Week 1-2)
- One channel (Telegram)
- Basic SOUL.md + AGENTS.md
- 2-3 cron jobs
- Manual oversight

### Stage 2: Enhanced Agent (Week 3-4)
- Add memory system
- Add heartbeat checks
- Install 5-10 skills
- Reduce manual oversight

### Stage 3: Multi-Agent (Month 2)
- Spin up specialized agents
- Add channels (Slack, Discord)
- Inter-agent communication
- Autonomous operations

### Stage 4: Production Swarm (Month 3+)
- 5+ agents running 24/7
- Full cron automation
- Self-maintaining memory
- Self-improving workflows
- Revenue-generating operations

### 100-Point OpenClaw Maturity Score

| Dimension | Weight | Score 0-10 |
|-----------|--------|-----------|
| Personality (SOUL.md depth) | 15% | |
| Memory System (3-layer) | 15% | |
| Automation (crons + heartbeat) | 15% | |
| Security (secrets management) | 10% | |
| Multi-Channel | 10% | |
| Skills Ecosystem | 10% | |
| Cost Optimization | 10% | |
| Self-Improvement | 10% | |
| Documentation | 5% | |

**Scoring:** 0-30 = Beginner, 31-50 = Intermediate, 51-70 = Advanced, 71-90 = Expert, 91-100 = Master

---

## Quick Reference — 12 Natural Language Commands

1. **"Assess my OpenClaw setup"** → Run maturity scoring across all dimensions
2. **"Design an agent for [purpose]"** → Full SOUL.md + AGENTS.md + config generation
3. **"Set up multi-agent architecture"** → Config template + workspace structure
4. **"Create a cron job for [task]"** → Schedule design + payload + delivery
5. **"Optimize my token costs"** → Analyze usage + recommend model/frequency changes
6. **"Debug why [X] isn't working"** → Troubleshooting checklist walkthrough
7. **"Set up [channel] integration"** → Step-by-step channel config
8. **"Design my memory system"** → 3-layer architecture + templates + maintenance schedule
9. **"Review my SOUL.md"** → Score against quality checklist + improvement suggestions
10. **"Scale to production"** → Scaling playbook stage assessment + next steps
11. **"Set up security"** → 1Password CLI + secrets management + safety rules
12. **"Build a custom skill"** → Skill structure + SKILL.md best practices + publishing

---

## ⚡ Level Up Your Agent

This skill gives you the complete OpenClaw operating system. Want industry-specific agent configurations with pre-built workflows?

**AfrexAI Context Packs ($47 each):**
- 🏥 Healthcare AI Agent Pack
- ⚖️ Legal AI Agent Pack
- 💰 Fintech AI Agent Pack
- 🏗️ Construction AI Agent Pack
- 🛒 Ecommerce AI Agent Pack
- 💻 SaaS AI Agent Pack
- 🏠 Real Estate AI Agent Pack
- 🏭 Manufacturing AI Agent Pack
- 👥 Recruitment AI Agent Pack
- 🏢 Professional Services AI Agent Pack

**Browse all:** https://afrexai-cto.github.io/context-packs/

## 🔗 More Free Skills by AfrexAI

- `afrexai-agent-engineering` — Build & manage multi-agent systems
- `afrexai-prompt-engineering` — Master prompt design
- `afrexai-vibe-coding` — AI-assisted development mastery
- `afrexai-productivity-system` — Personal operating system
- `afrexai-technical-seo` — Complete SEO audit system

**Install any:** `clawhub install afrexai-[name]`

---

*Built with 💛 by AfrexAI — Autonomous intelligence for modern business.*
*https://afrexai-cto.github.io/context-packs/*
