---
name: team-builder
description: Deploy a multi-agent SaaS growth team on OpenClaw with shared workspace, async inbox communication, cron-scheduled tasks, and optional Telegram integration. Use when user wants to create an AI agent team, build a multi-agent system, set up a growth/marketing/product team, or deploy agents for a SaaS product matrix. Supports customizable team name, agent roles, models, timezone, and Telegram bots.
---

# Team Builder

Deploy a 7-agent SaaS growth team on OpenClaw in one shot.

## System Impact & Prerequisites

> **Read before running.** This skill creates files and modifies system config.

### What it creates
- A new workspace directory with ~40 files (agent configs, shared knowledge, inboxes, kanban)
- `apply-config.js` -- script that **modifies `~/.openclaw/openclaw.json`** (adds agents, bindings, agentToAgent config). Auto-backs up before writing.
- `create-crons.ps1` / `create-crons.sh` -- scripts that **create cron jobs** via `openclaw cron add`
- After running these scripts you must **restart the gateway** (`openclaw gateway restart`)

### What it does NOT do automatically
- Does not modify openclaw.json directly -- you run `apply-config.js` yourself
- Does not create cron jobs directly -- you run the cron script yourself
- Does not restart the gateway -- you do that manually

### Optional: Telegram
- If you provide bot tokens during setup, `apply-config.js` will also add Telegram account configs and bindings
- Requires: Telegram bot tokens from @BotFather, your Telegram user ID
- Requires: network access to Telegram API (proxy configurable)

### Optional: ACP / Claude Code
- The fullstack-dev agent is configured to spawn Claude Code via ACP for complex coding tasks
- Requires: ACP-compatible coding agent configured in your OpenClaw environment
- No extra setup needed if you don't use this feature

### Credentials involved
- **Telegram bot tokens** (optional) -- stored in openclaw.json, used for agent-to-Telegram binding
- **Model API keys** -- must already be configured in your OpenClaw model providers (not handled by this skill)

### Recommended
- Review generated `apply-config.js` before running
- Check the backup of openclaw.json after running
- Test with 2-3 agents before enabling all cron jobs

## Team Architecture

Default 7-agent SaaS growth team (customizable to 2-10 agents):

```
CEO
 |-- Chief of Staff (dispatch + strategy + efficiency)
 |-- Data Analyst (data + user research)
 |-- Growth Lead (GEO + SEO + community + social media)
 |-- Content Chief (strategy + writing + copywriting + i18n)
 |-- Intel Analyst (competitor monitoring + market trends)
 |-- Product Lead (product management + tech architecture)
 |-- Fullstack Dev (full-stack dev + ops, spawns Claude Code with role-based prompts)
```

### Multi-Team Support

One OpenClaw instance can run multiple teams:

```bash
node <skill-dir>/scripts/deploy.js                  # default team
node <skill-dir>/scripts/deploy.js --team alpha      # named team "alpha"
node <skill-dir>/scripts/deploy.js --team beta       # named team "beta"
```

Named teams use prefixed agent IDs (`alpha-chief-of-staff`, `beta-growth-lead`) to avoid conflicts. Each team gets its own workspace subdirectory.

### Flexible Team Size

The wizard lets you select 2-10 agents from the available roles. Skip roles you don't need. The 7-agent default covers most SaaS scenarios, but you can run leaner (3-4 agents) or expand with custom roles.

### Model Auto-Detection

The wizard scans your `openclaw.json` for registered model providers and auto-suggests models by role type:

| Role Type | Best For | Auto-detect Pattern |
|-----------|----------|-------------------|
| Thinking | Strategic roles (chief, growth, content, product) | /glm-5\|opus\|o1\|deepthink/i |
| Execution | Operational roles (data, intel, fullstack) | /glm-4\|sonnet\|gpt-4/i |
| Fast | Lightweight tasks | /flash\|haiku\|mini/i |

You can always override with manual model IDs.

## Deployment Flow

### Step 1: Collect Configuration

Ask the user for these inputs (use defaults if not provided):

| Parameter | Default | Description |
|-----------|---------|-------------|
| Team name | Alpha Team | Used in all docs and configs |
| Workspace dir | `~/.openclaw/workspace-team` | Shared workspace root |
| Timezone | Asia/Shanghai | For cron schedules |
| Morning brief hour | 8 | Chief's morning report |
| Evening brief hour | 18 | Chief's evening report |
| Thinking model | zai/glm-5 | For strategic roles |
| Execution model | zai/glm-4.7 | For execution roles |
| CEO title | Boss | How agents address the CEO |

Optional: Telegram user ID, proxy, and 7 bot tokens.

### Step 2: Run Deploy Script

```bash
node <skill-dir>/scripts/deploy.js
```

Interactive -- asks all questions from Step 1, generates the full workspace.

### Step 3: Apply Config

```bash
node <workspace-dir>/apply-config.js
```

Adds agents to openclaw.json, preserving existing config.

### Step 4: Create Cron Jobs

```bash
# Windows
powershell <workspace-dir>/create-crons.ps1

# Linux/Mac
bash <workspace-dir>/create-crons.sh
```

### Step 5: Restart Gateway

```bash
openclaw gateway restart
```

### Step 6: Fill Business Info

User must edit:
- `shared/decisions/active.md` -- strategy, priorities
- `shared/products/_index.md` -- products, keywords, competitors
- `shared/knowledge/competitor-map.md` -- competitor analysis
- `shared/knowledge/tech-standards.md` -- coding standards

## Cron Schedule

| Offset | Agent | Task | Frequency |
|--------|-------|------|-----------|
| H-1 | Data Analyst | Data + user feedback | Daily |
| H-1 | Intel Analyst | Competitor scan | Mon/Wed/Fri |
| H | Chief of Staff | Morning brief (announced) | Daily |
| H+1 | Growth Lead | GEO + SEO + community | Daily |
| H+1 | Content Chief | Weekly content plan | Monday |
| H+10 | Chief of Staff | Evening brief (announced) | Daily |

(H = morning brief hour)

## Generated File Structure

```
<workspace>/
├── AGENTS.md, SOUL.md, USER.md  (auto-injected)
├── apply-config.js, create-crons.ps1/.sh, README.md
├── agents/<7 agent dirs>/       (SOUL.md + MEMORY.md + memory/)
└── shared/
    ├── briefings/, decisions/, inbox/
    ├── data/                        (public data pool, data-analyst writes, all read)
    ├── kanban/, knowledge/, products/
```



## Knowledge Governance

Each shared knowledge file has a designated owner. Only the owner agent updates it; others read only.

| File | Owner | Update Trigger |
|------|-------|---------------|
| geo-playbook.md | growth-lead | After GEO experiments/discoveries |
| seo-playbook.md | growth-lead | After SEO experiments |
| competitor-map.md | intel-analyst | After each competitor scan |
| content-guidelines.md | content-chief | After proven writing patterns |
| user-personas.md | data-analyst | After new user insights |
| tech-standards.md | product-lead | After architecture decisions |

### Update Protocol
When updating a knowledge file, the owner must:
1. Add a dated entry at the top: `## [YYYY-MM-DD] <what changed>`
2. Include the reason and data evidence
3. Never delete existing entries without CEO approval (append, don't replace)

### Chief of Staff Governance
The chief-of-staff monitors knowledge file health during weekly reviews:
- Are files being updated regularly?
- Any conflicting information between files?
- Any stale entries that should be archived?

## Self-Evolution Pattern

Agents improve their own strategies over time through a feedback loop:

```
1. Execute task (cron or inbox triggered)
2. Collect results (data, metrics, outcomes)
3. Analyze: what worked vs what didn't
4. Update knowledge files with proven strategies (with evidence)
5. Next execution reads updated knowledge → better performance
```

This is NOT the agent randomly changing rules. Updates must be:
- **Data-driven**: backed by metrics or concrete outcomes
- **Incremental**: append new findings, don't rewrite everything
- **Traceable**: dated with evidence so others can verify

### What Agents Can Self-Update
- Their own knowledge files (per ownership table above)
- Their own MEMORY.md (lessons learned, decisions)
- shared/data/ outputs (data-analyst only)

### What Requires CEO Approval
- shared/decisions/active.md (strategy changes)
- Adding/removing agents or changing team architecture
- External publishing or spending decisions

## Public Data Layer

The `shared/data/` directory serves as a read-only data pool for all agents:

- **data-analyst** writes: daily metrics, user feedback summaries, anomaly alerts
- **All agents** read: to inform their own decisions
- Format: structured markdown or JSON, dated filenames (e.g., `metrics-2026-03-01.md`)
- Retention: keep 30 days, archive older files

## Key Design Decisions

- **Shared workspace** so qmd indexes everything for all agents
- **Async inbox** (shared/inbox/to-*.md) instead of agentToAgent (saves tokens, audit trail)
- **Chief as hub** between CEO and team
- **GEO as #1 priority** (AI search = blue ocean)
- **Fullstack Dev spawns Claude Code** via ACP for complex tasks

## Customization

Edit ROLES array in `scripts/deploy.js` to add/remove agents.
Edit `references/soul-templates.md` for SOUL.md templates.
Edit `references/shared-templates.md` for shared file templates.
