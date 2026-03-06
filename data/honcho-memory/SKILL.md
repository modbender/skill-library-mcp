---
name: honcho-memory
description: Built by Axobotl (@Inner_Axiom). Production-grade Honcho memory system battle-tested on a 6+ agent fleet with 1000+ messages. Replaces embedding-based retrieval with reasoned, evolving understanding of users and agents across sessions. Includes automated feed pipelines, on-demand querying with reasoning levels, token-budgeted context generation that survives compaction, cross-agent memory sharing, and cron automation. Use when you need agents that actually remember, understand context across sessions, or when cron/isolated sessions need full continuity.
version: 1.0.4
author: axelcorp-ai
tags: [memory, honcho, reasoning, context, multi-agent, compaction, persistence]
---

# Honcho Memory

Production memory system for AI agents, built on [Honcho](https://[[research/honcho-integration-plan|Honcho]].dev) by Plastic Labs. Developed and refined running a fleet of 6+ agents in production with 1000+ messages fed through the reasoning engine.

This isn't a wrapper or setup guide. It's a complete memory pipeline: feed conversations in, reason over them automatically, generate token-budgeted context files, and query on-demand when agents need to recall something they've never seen in their current session.

## The Problem This Solves

Agent memory is broken in three ways:

1. **Compaction amnesia.** Long sessions get compacted. Context vanishes. Your agent forgets decisions made 2 hours ago.
2. **Isolated session blindness.** Cron jobs and background tasks spin up fresh sessions with zero conversation history. They operate without context.
3. **Single-agent silos.** In multi-agent setups, agents can't access what other agents learned. Knowledge stays trapped in individual sessions.

Honcho Memory solves all three. Every agent feeds into a shared reasoning engine. Every session (main, cron, isolated) loads reasoned context at startup. Nothing gets lost.

## How It Works

Most agent memory is embedding search: store text chunks, retrieve similar chunks later. That's a library with a search bar.

Honcho is a **reasoning engine**. It processes conversations through Neuromancer and builds deductive and inductive observations about every person and agent it tracks. It doesn't retrieve what was said. It reasons about what it means.

Feed it 3 weeks of multi-agent conversations and ask "What should the social media agent focus on this week?" It won't dump old messages. It will synthesize: "Based on recent engagement patterns, sports/entertainment replies are outperforming crypto content 3:1. The user shifted priority toward brand-building over direct promotion last Tuesday."

## Architecture

```
                         WRITE PATH
Conversations ──→ feed.py ──→ Honcho API ──→ Neuromancer ──→ Observations
  (all agents)      │                         (async reasoning)      │
                    │                                                ↓
                    │                                        Representations
                    │                                         (per peer)
                    │                                                │
                    │              READ PATH                         │
                    │    ┌─────────────────────────────┐            │
                    │    │  generate-context.py (cron)  │←───────────┘
                    │    │  Token-budgeted files that   │
                    │    │  survive compaction           │
                    │    └──────────┬──────────────────┘
                    │               │
                    │               ↓
                    │    HONCHO-CONTEXT.md (shared)
                    │    agents/*/HONCHO-CONTEXT.md (per-agent)
                    │               │
                    │               ↓
                    │    Every session loads reasoned context
                    │    (main, cron, isolated, sub-agent)
                    │
                    │    ┌─────────────────────────────┐
                    └───→│  query.py (on-demand)        │←── Agent mid-conversation
                         │  "What did we decide about   │    needs to recall something
                         │   pricing last week?"        │
                         └─────────────────────────────┘
```

## Key Features

### Compaction-Proof Memory
Context files are workspace files. They survive compaction, session resets, and gateway restarts. Every session starts with reasoned context automatically, not just the last few messages.

### Cross-Agent Memory
All agents feed into the same Honcho workspace. Agent A learns something on Monday. Agent B can access that understanding on Tuesday through shared context generation. No manual syncing, no copy-pasting between workspaces.

### Token-Budgeted Context
Generated context files are budget-controlled (~1000-1500 tokens shared, ~500-800 per agent). No prompt bloat. Honcho distills weeks of conversations into dense, relevant context that fits cleanly in the system prompt.

### Reasoning Levels
On-demand queries support five reasoning levels: `minimal`, `low`, `medium`, `high`, `max`. Quick lookups stay cheap. Deep analysis gets thorough treatment.

### Honcho-First, Files as Fallback
Designed to complement existing file-based memory (`MEMORY.md`, `memory/*.md`), not replace it. Honcho handles reasoned recall. Local files handle raw logs and structured data. If Honcho is unavailable, file-based memory still works.

## Prerequisites

- Python 3.10+
- Honcho account + API key ([app.honcho.dev](https://app.honcho.dev))
- `pip install honcho-ai`

## Setup

### 1. Install SDK

```bash
pip install honcho-ai
```

### 2. Configure credentials

Create `~/.config/honcho/credentials.json`:

```json
{
  "api_key": "your-honcho-api-key",
  "workspace_id": "your-workspace-name"
}
```

### 3. Initialize workspace and peers

```bash
python3 scripts/setup.py --workspace "my-workspace" --peers "user,agent1,agent2"
```

Creates the workspace and registers every entity (users and agents) that Honcho will track and build representations for.

## Usage

### Feed conversations

```bash
python3 scripts/feed.py
```

Auto-discovers active agent session transcripts, attributes messages to correct peers, tracks sync position to avoid duplicates, feeds in batches. Run after sessions or on a cron schedule.

### Query on-demand

When an agent needs context it doesn't have:

```bash
python3 scripts/query.py "What was the decision on pricing?"
python3 scripts/query.py "What are the user's priorities right now?" --peer user-name
python3 scripts/query.py "Full analysis of this week's performance" --level high
```

### Generate context files

```bash
python3 scripts/generate-context.py                    # all agents
python3 scripts/generate-context.py --agent agent-name # specific agent
python3 scripts/generate-context.py --query "topic"    # on-demand deep query
```

Produces:
- `HONCHO-CONTEXT.md` in workspace root (shared across all agents)
- `HONCHO-CONTEXT.md` in each agent's workspace (agent-specific)

### Check sync status

```bash
python3 scripts/feed.py --status
```

## Cron Automation

Run hourly during active hours to keep memory fresh:

```
0 9-23 * * *  cd /workspace && python3 scripts/feed.py && python3 scripts/generate-context.py
```

OpenClaw cron tool config:

```json
{
  "name": "honcho-sync",
  "schedule": {"kind": "cron", "expr": "0 9-23 * * *", "tz": "America/Los_Angeles"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run: cd /workspace && source .venv/bin/activate && python3 scripts/feed.py && python3 scripts/generate-context.py. Report summary.",
    "timeoutSeconds": 180
  },
  "delivery": {"mode": "none"}
}
```

## Multi-Agent Setup

For fleets with multiple agents, each agent gets:

1. **Its own peer** in Honcho (tracks what that agent said and learned)
2. **Shared context** from the root `HONCHO-CONTEXT.md` (cross-agent awareness)
3. **Agent-specific context** from its workspace `HONCHO-CONTEXT.md` (role-specific memory)

The feed script handles attribution automatically. User messages go to the human peer. Each agent's responses go to that agent's peer. Honcho reasons across all of them.

**Example: 6-agent fleet**
- Main agent, social media agent, content agent, community agent, news scanner, expansion agent
- All feed into one Honcho workspace
- Each gets tailored context files reflecting their role and recent activity
- The main agent's context includes a cross-agent brief summarizing what every other agent did

## Integration with Agent Prompts

Add to each agent's system prompt or operating instructions:

```markdown
## Memory
- At session start: read HONCHO-CONTEXT.md for reasoned context from all conversations
- If you don't remember something or need context you don't have:
  python3 scripts/query.py "your question" --peer user-name
- Honcho reasons over ALL agent conversations. It likely has the answer.
- Before saying "I don't know" about past decisions, projects, or conversations: query Honcho first.
```

## Use Cases

- **Cron job needs context**: Generated context files give every isolated session full awareness of recent activity, decisions, and priorities without carrying conversation history.
- **Agent forgot a decision**: On-demand query pulls reasoned context about any topic from weeks of conversations.
- **New agent joins the fleet**: Reads shared HONCHO-CONTEXT.md and immediately understands the user, active projects, and current priorities.
- **Post-compaction recovery**: Context files survive compaction. Agent reloads and continues without losing the thread.
- **Cross-agent coordination**: Social media agent needs to know what the content agent published. Shared context provides this automatically.

## How Honcho's Reasoning Works

Honcho's data model: **Workspaces → Peers → Sessions → Messages**. Workspaces isolate environments. Peers are any entity that persists and changes over time (users, agents). Sessions are conversation threads between peers. Messages are units of data that trigger reasoning.

When messages are written, Honcho doesn't just store them. Custom reasoning models (Neuromancer) perform formal logical reasoning in the background to generate conclusions about each peer. These conclusions compound into **representations** that evolve with every new interaction. When you query, you get reasoned context derived from representations, not raw message retrieval.

- **Observations**: Deductive and inductive conclusions drawn from conversations
- **Representations**: Synthesized, evolving understanding of each peer
- **Context retrieval**: Token-budgeted, combining representations, recent activity, and reasoned observations

For full details on Honcho's architecture: [docs.honcho.dev](https://docs.honcho.dev)

**Cost**: ~$2/million tokens ingested. Storage and retrieval free. Most multi-agent setups run $4-6/month.

## References

- `references/api-reference.md` — Full Honcho SDK API documentation
- `references/architecture.md` — Integration patterns and data flow diagrams
- [Honcho docs](https://docs.honcho.dev)
- [Plastic Labs](https://plasticlabs.ai)
