---
name: social-media-ops
description: Set up a complete multi-brand social media management team on OpenClaw. Scaffolds 7 specialized AI agents (Leader, Researcher, Content Strategist, Visual Designer, Operator, Engineer, Reviewer) in a star topology with persistent A2A sessions, 3-layer memory system, shared knowledge base, approval workflows, and brand isolation. Use when setting up a new social media operations team, adding the multi-agent framework to an existing OpenClaw instance, or when the user mentions social media management, multi-brand operations, or content team setup.
metadata:
  {
    "openclaw": {
      "emoji": "📱",
      "requires": {
        "bins": ["node"]
      }
    }
  }
---

# Social Media Ops

## Overview

This skill sets up a complete AI-powered social media operations team on OpenClaw. It creates:

- **7 specialized agents** in a star topology (Leader + 6 specialists)
- **Persistent A2A sessions** for context-preserving multi-agent workflows
- **3-layer memory system** (MEMORY.md + daily notes + shared knowledge base)
- **Shared knowledge base** with brand profiles, operations guides, and domain knowledge
- **Approval workflow** ensuring nothing publishes without owner approval
- **Brand isolation** with per-brand channels, content guidelines, and asset directories
- **Cron automation** for daily memory consolidation and weekly KB review

## Optional Dependencies

- **Image generation tool for Designer agent**: The Designer agent requires an image generation tool installed in its `workspace-designer/skills/` directory to produce images. Recommended: `nano-banana-pro` (Gemini-based, free tier). Without it, Designer produces text visual briefs only and cannot generate images.

## Prerequisites

Before installing, ensure:

1. OpenClaw v2026.2.26+ is installed and `openclaw onboard` has been completed
2. At least one auth profile exists (e.g., Anthropic API key)
3. The `~/.openclaw/` directory exists

## Quick Start

```
1. Install the skill (if not already in workspace/skills/)
2. Trigger setup: "Set up my social media operations team"
3. Follow the interactive onboarding (6 steps, ~10 minutes)
4. Start creating content!
```

## Onboarding Flow

When first triggered, this skill runs an interactive setup process.

### Step 1: Prerequisites Check

Verify the environment is ready:

- [ ] OpenClaw installed and `openclaw onboard` completed
- [ ] `~/.openclaw/` directory exists
- [ ] At least one auth profile configured

If any prerequisite is missing, guide the user to resolve it before continuing.

### Step 2: Team Setup

**All 7 agents are installed automatically.** Do not ask the user to choose a team size.

The full team:

| Agent | Role |
|-------|------|
| Leader | Orchestration, routing, quality gates |
| Researcher | Market research, competitor analysis |
| Content | Content strategy, copywriting |
| Designer | Visual briefs, image generation |
| Operator | Platform operations, scheduling |
| Engineer | Technical integrations, automation |
| Reviewer | Independent quality review |

**Model** — All agents inherit the model configured during `openclaw onboard` (at `agents.defaults.model`). No per-agent model setup is needed.

> **Advanced note:** If you later want to run a leaner team, re-run `scaffold.sh --agents leader,content,designer,engineer` to scaffold a subset.

### Step 3: Run Scaffold

Execute the setup scripts to create all directories and files first:

```bash
# 1. Create directories, copy templates, set up symlinks
bash scripts/scaffold.sh \
  --skill-dir "$(pwd)"

# 2. Merge agent configuration into openclaw.json
node scripts/patch-config.js \
  --config ~/.openclaw/openclaw.json
```

The scaffold creates:
- Agent workspace directories with SOUL.md, AGENTS.md, MEMORY.md
- Shared knowledge base with all template files
- Symlinks from each workspace to shared/
- Sub-skills (instance-setup, brand-manager) in Leader's skills/
- Cron job definitions

The config patcher merges into openclaw.json:
- Agent definitions with model assignments and tool restrictions
- A2A session configuration
- QMD memory paths (**only if QMD is installed** — otherwise skipped with a suggestion)
- Internal hooks

### Step 4: Telegram Setup

This step uses a **guided flow** — do not ask the user for raw chat IDs or thread IDs.

#### Phase A: Confirm Bot Token

1. Check `openclaw.json` for `channels.telegram.botToken`
2. If present → skip to Phase B
3. If missing → guide the user:
   - "Open Telegram, search for **@BotFather**"
   - "Send `/newbot` and follow the prompts to create a bot"
   - "Copy the bot token and paste it here"
   - Write the token into `openclaw.json` at `channels.telegram.botToken`

#### Phase B: Choose Channel Mode

Present the options in this order (Group+Topics first):

1. **Group+Topics (recommended)** — Best for most setups
   - Brands are topic threads inside a Telegram supergroup
   - Works for both solo operators and multi-person teams
   - Requires a supergroup with Topics enabled

2. **DM+Topics** — Private alternative, no group needed
   - Each brand gets its own topic thread inside the bot's DM
   - Requires enabling Thread Mode on the bot (guided below)

3. **DM-simple** — Minimal, no brand isolation
   - Single DM conversation with the bot
   - Context-based brand routing (no topics)

4. **Group-simple** — Group without brand isolation
   - Single group conversation
   - Context-based brand routing (no topics)

#### Phase C: Mode-Specific Setup

**If DM+Topics:**

1. Guide the user to enable Thread Mode on their bot:
   - "Open Telegram, find **@BotFather**"
   - "Tap the **Open** button (bottom-left) to open the BotFather MiniApp"
   - "Select your bot in the MiniApp"
   - "Go to **Bot Settings**"
   - "Find **Thread Mode** and enable it"
   - "Come back and tell me when it's done"
2. Once confirmed, use the bot token to get the user's chat ID:
   - "Send any message to your bot in Telegram"
   - Agent reads the incoming message context to extract the user's chat ID from `{{From}}`
   - Agent writes the chat ID into the channel config
3. Create the **Operations** topic automatically:
   ```bash
   node scripts/telegram-topics.js \
     --config ~/.openclaw/openclaw.json \
     --chat <USER_CHAT_ID> \
     --name "Operations"
   ```
4. Write the resulting thread ID into `shared/operations/channel-map.md`
5. Update `cron/jobs.json` — replace `{{OPERATIONS_CHANNEL}}` with the actual Operations channel address (format: `chatId:threadId`, e.g., `123456789:7`)

**If Group+Topics:**

1. Check if the user already has a supergroup:
   - If not: guide them to create one (Create Group → toggle "Topics" on)
2. Guide the user to add the bot to the group:
   - "Add your bot to the supergroup"
   - "Make the bot an **admin** with the **Manage Topics** permission"
   - "Send a message in the group"
3. Agent reads the incoming message context to extract:
   - Group chat ID from `{{To}}`
   - Agent writes the chat ID into the channel config
4. Create the **Operations** topic automatically:
   ```bash
   node scripts/telegram-topics.js \
     --config ~/.openclaw/openclaw.json \
     --chat <GROUP_CHAT_ID> \
     --name "Operations"
   ```
5. Write the resulting thread ID into `shared/operations/channel-map.md`
6. Update `cron/jobs.json` — replace `{{OPERATIONS_CHANNEL}}` with the actual Operations channel address (format: `chatId:threadId`, e.g., `-100XXXXXXXXXX:7`)

**If DM-simple:**

1. "Send any message to your bot in Telegram"
2. Agent reads the chat ID from the incoming message context
3. Write chat ID into channel config — done

**If Group-simple:**

1. Guide: "Add the bot to your group and send a message"
2. Agent reads the group chat ID from the incoming message context
3. Write chat ID into channel config — done

### Step 5: Instance Setup + First Brand

After scaffolding and Telegram configuration, run the sub-skills:

1. **Instance Setup** (`instance-setup` skill)
   - Owner name and timezone
   - Communication language (owner-facing)
   - Default content language
   - Bot identity (name, emoji, personality)
   - Updates: `shared/INSTANCE.md`, `workspace/IDENTITY.md`

2. **First Brand** (`brand-manager add`)
   - Brand ID, display name, domain
   - Target market and content language
   - **Topic creation** (for Topics modes):
     - Agent calls `scripts/telegram-topics.js` to create a topic named after the brand
     - The script returns the thread ID
     - Agent writes the thread ID into `shared/operations/channel-map.md` and the brand config
   - For simple modes: no topic needed, skip thread ID
   - Creates: brand profile, content guidelines, domain knowledge file, asset directories

### Step 6: Verification + Gateway Restart

1. **Restart gateway:**
   ```
   openclaw gateway restart
   ```

2. **Run diagnostics:**
   ```
   openclaw doctor
   ```
   This validates: agent config, DM allowlist inheritance, session health, model availability, and workspace integrity.

3. **Additional checks:**
   - [ ] Leader responds to messages
   - [ ] `sessions_send` to at least one agent succeeds

**Optional: Enable QMD semantic memory**

If `patch-config.js` reported "qmd binary not found" during Step 3, agents will use file-based memory (which works fine). To enable enhanced semantic search:
- Say **"Set up QMD"** to run the `qmd-setup` sub-skill, which guides you through installation and configuration.

**Suggested first tasks after setup:**
1. Fill in your brand profile: `shared/brands/{brand_id}/profile.md`
2. Test content creation: "Write a Facebook post for {brand}"
3. Add more brands: "Add a new brand"
4. Set up posting schedule: fill in `shared/operations/posting-schedule.md`

## Post-Installation

### Async Dispatch Model (v2.0.0+)

Leader uses **fully async dispatch** (`sessions_send` with `timeoutSeconds: 0`) for all agent communication. This means:

- Leader is **never blocked** waiting for an agent — always available to the owner.
- Agents **callback** to Leader via `sessions_send` when done (event-driven, not polling). Leader processes callbacks per the "Agent Callback Protocol" flow in AGENTS.md.
- Each task is tracked in a separate file: `tasks/T-{YYYYMMDD}-{HHMM}.md`. Completed tasks are archived to `tasks/archive/`.
- **Stale task detection** is handled by a cron job (`stale-task-check`, every 5 minutes) that scans `tasks/` for steps stuck in `[⏳]` state. Runs as Leader (not operator).
- **HEARTBEAT.md** ships empty by default — periodic checks are handled by cron jobs instead of heartbeat polls.

### Secrets Management (Optional)

For centralized API key management instead of scattered env vars:
```
openclaw secrets audit      # Check for plaintext secrets in config
openclaw secrets configure  # Set up secret entries
openclaw secrets apply      # Activate secrets
openclaw secrets reload     # Hot-reload without gateway restart
```

### Adding More Brands

Use the `brand-manager` sub-skill:
- "Add a new brand" — interactive brand creation (auto-creates topic for Topics modes)
- "List brands" — show all active brands
- "Archive {brand}" — deactivate a brand

### Customizing Agents

Each agent's behavior is defined in two files:
- **SOUL.md** — Persona, philosophy, boundaries, safety rules
- **AGENTS.md** — Operating procedures, data handling, brand scope, tools

Modify these files to tune agent behavior for your specific needs.

### Memory System

The 3-layer memory system works automatically:
- **MEMORY.md** — Long-term curated memory (auto-updated by cron)
- **memory/YYYY-MM-DD.md** — Daily activity logs
- **shared/** — Permanent knowledge base (grows over time)

**Optional enhancement:** Install QMD for semantic search across the knowledge base. Use the `qmd-setup` sub-skill or install manually (`bun install -g @tobilu/qmd`).

See `references/memory-system.md` for detailed documentation.

### Communication Signals

Agents use standardized signals to communicate status. See `references/signals-protocol.md` for the complete signal dictionary.

## Reference Documentation

| Document | Purpose | When to Read |
|----------|---------|-------------|
| `references/architecture.md` | Star topology, session model, parallelism | Understanding system design |
| `references/agent-roles.md` | Detailed agent capabilities and restrictions | Customizing team composition |
| `references/signals-protocol.md` | Complete signal dictionary | Debugging agent communication |
| `references/memory-system.md` | 3-layer memory + knowledge capture | Understanding memory behavior |
| `references/approval-workflow.md` | Approval pipeline + owner shortcuts | Content publishing workflow |
| `references/troubleshooting.md` | Known issues (IPv6, etc.) + solutions | When something breaks |

## Directory Structure

After installation, the following structure is created:

```
~/.openclaw/
├── openclaw.json                    # Updated with agent configs
├── workspace/                       # Leader
│   ├── SOUL.md, AGENTS.md, HEARTBEAT.md, IDENTITY.md
│   ├── memory/, skills/, assets/
│   └── shared/                      # Real directory (shared KB lives here)
│       ├── INSTANCE.md              # Instance configuration
│       ├── brand-registry.md        # Brand registry
│       ├── system-guide.md, brand-guide.md, compliance-guide.md
│       ├── team-roster.md
│       ├── brands/{id}/profile.md   # Per-brand profiles
│       ├── domain/{id}-industry.md  # Industry knowledge
│       ├── operations/              # Ops guides
│       └── errors/solutions.md      # Error KB
├── workspace-researcher/            # Researcher
│   ├── SOUL.md, AGENTS.md, MEMORY.md
│   ├── memory/, skills/
│   └── shared -> ../workspace/shared/
├── workspace-content/               # Content Strategist
│   └── (same structure)
├── workspace-designer/              # Visual Designer
│   └── (same structure)
├── workspace-operator/              # Operator
│   └── (same structure)
├── workspace-engineer/              # Engineer
│   └── (same structure)
├── workspace-reviewer/              # Reviewer (minimal, read-only)
│   ├── SOUL.md, AGENTS.md
│   └── shared -> ../workspace/shared/
└── cron/jobs.json                   # Scheduled tasks
```

## Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/scaffold.sh` | Create directories, copy templates, set up symlinks | During initial setup |
| `scripts/patch-config.js` | Merge agent config into openclaw.json | During initial setup |
| `scripts/telegram-topics.js` | Create forum topics in Telegram DM or supergroup | During setup and when adding brands |

## Sub-Skills

| Skill | Purpose |
|-------|---------|
| `instance-setup` | Configure owner info, language, bot identity |
| `brand-manager` | Add, edit, archive brands |
| `qmd-setup` | Install and configure QMD semantic search memory (optional) |
