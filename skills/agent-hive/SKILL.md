---
name: agent-hive
description: "Create and manage multi-agent teams in OpenClaw with shared workspace, budget governance, and mesh networking. Use when: (1) adding a new agent to an existing team, (2) setting up a multi-agent workspace from scratch, (3) configuring agent-to-agent spawn permissions (mesh/hub-spoke), (4) implementing budget governance for agent teams, (5) auditing agent spend and enforcing demotions. NOT for: single-agent setups or modifying agent personalities (edit SOUL.md directly)."
metadata:
  version: 1.0.0
  openclaw:
    requires:
      bins: []
      env: []
    network:
      outbound: []
    primaryEnv: ""
---

# Agent Hive

Create and manage multi-agent teams with shared memory, budget governance, and configurable spawn permissions.

## Architecture

```
Main Workspace (~/.openclaw/workspace/)
├── MEMORY.md, TOOLS.md, USER.md, IDENTITY.md   ← shared brain (real files)
├── agents/<name>/                                ← per-agent outbox, inbox, budget
├── agents/governance/                            ← governance rules + audit log
├── memory/, projects/, scripts/, skills/         ← shared resources
└── content/                                      ← shared content

Agent Workspace (~/.openclaw/workspace-<id>/)
├── SOUL.md              ← unique personality (local file)
├── AGENTS.md            ← unique instructions (local file)
├── HEARTBEAT.md         ← agent-specific heartbeat (local file)
├── .openclaw/           ← agent-specific config dir
└── everything else      ← SYMLINKS to main workspace
```

## Adding a New Agent

### Step 1: Create workspace with symlinks

```bash
AGENT_ID="<id>"
MAIN="$HOME/.openclaw/workspace"
WS="$HOME/.openclaw/workspace-$AGENT_ID"

mkdir -p "$WS/.openclaw"

# Symlink shared brain
for f in .learnings IDENTITY.md MEMORY.md ROADMAP.md TOOLS.md USER.md; do
  ln -sf "../workspace/$f" "$WS/$f"
done
for d in agents content memory projects scripts skills; do
  ln -sf "../workspace/$d" "$WS/$d"
done
```

### Step 2: Create unique files

Create `$WS/SOUL.md` — the agent's personality. This is theirs alone.

Create `$WS/AGENTS.md` — agent-specific instructions. Must include:
- Session startup checklist (read SOUL.md, check BUDGET.json, check INBOX.md)
- Communication rules (INBOX/OUTBOX pattern)
- What the agent does and doesn't do
- Budget rules section (see references/budget-rules.md)

Create `$WS/HEARTBEAT.md` — minimal heartbeat config.

### Step 3: Create agent directory in shared workspace

```bash
mkdir -p "$MAIN/agents/$AGENT_ID"
touch "$MAIN/agents/$AGENT_ID/INBOX.md"
touch "$MAIN/agents/$AGENT_ID/OUTBOX.md"
```

### Step 4: Create budget file

Copy `scripts/create_budget.sh` output or create manually:

```json
{
  "daily_limit_output_tokens": 50000,
  "today": "YYYY-MM-DD",
  "used_output_tokens": 0,
  "spawns": [],
  "status": "active",
  "warnings": [],
  "consecutive_overbudget_days": 0
}
```

Save to `$MAIN/agents/$AGENT_ID/BUDGET.json`.

### Step 5: Register in openclaw.json

Add to `agents.list[]`:

```json
{
  "id": "<id>",
  "name": "<Name>",
  "workspace": "/absolute/path/to/workspace-<id>",
  "identity": { "name": "<Name>", "emoji": "<emoji>" },
  "model": {
    "primary": "anthropic/claude-sonnet-4-6",
    "fallbacks": ["<fallback-model-1>", "<fallback-model-2>"]
  },
  "subagents": { "allowAgents": ["<peer1>", "<peer2>"] }
}
```

Update existing agents' `allowAgents` to include the new agent.

### Step 6: Validate and restart

```bash
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json')); print('JSON valid')"
openclaw doctor  # check for schema errors
launchctl stop ai.openclaw.gateway && sleep 2 && launchctl start ai.openclaw.gateway
```

Wait 15 seconds before testing.

## Spawn Permission Models

### Hub-and-spoke (conservative)
Only the orchestrator (main) can spawn agents. Agents route requests through OUTBOX.

```json
"subagents": { "allowAgents": [] }  // for all non-main agents
```

### Full mesh with budget (recommended)
All agents can spawn peers. Budget governance prevents abuse.

```json
// Each agent can spawn all peers (not themselves)
"subagents": { "allowAgents": ["<all other agent ids>"] }
```

### Earned mesh (progressive trust)
Start hub-and-spoke. Promote to mesh after demonstrating budget responsibility.
Demote back to hub-and-spoke after repeated overspend.

## Budget Governance

See `references/governance.md` for the full framework.

Run the audit script on heartbeat:

```bash
python3 scripts/budget_audit.py
```

Thresholds: Green (<80%), Yellow (80-100%), Red (>100%), Emergency demotion (>200%).
3 consecutive overbudget days → automatic demotion (mesh privileges revoked).

Add step 4.5 to your HEARTBEAT.md — see `references/heartbeat-snippet.md`.

## Committee Pattern

For project work, compose agent committees:
1. Identify which agents are needed (e.g., content + marketing + design review)
2. Spawn them in parallel with clear, scoped tasks
3. Each writes to their OUTBOX.md
4. Orchestrator collects results and synthesizes
5. Budget tracked per-agent across the project

## Verification Checklist

After adding an agent, verify:
- [ ] `workspace-<id>/` has SOUL.md + AGENTS.md as local files
- [ ] All other files are symlinks to main workspace
- [ ] `agents/<id>/BUDGET.json` exists with correct schema
- [ ] Agent appears in `openclaw doctor` output
- [ ] Gateway restarts without errors
- [ ] Agent can be spawned: `sessions_spawn(agentId="<id>", task="Say hello")`
- [ ] Budget audit includes the new agent: `python3 scripts/budget_audit.py`
