# Gas Town Architecture

## Overview

Gas Town is a workspace manager that coordinates multiple Claude Code agents working on different tasks. Instead of losing context when agents restart, Gas Town persists work state in git-backed hooks, enabling reliable multi-agent workflows.

## Problem & Solution

| Challenge | Gas Town Solution |
|-----------|-------------------|
| Agents lose context on restart | Work persists in git-backed hooks |
| Manual agent coordination | Built-in mailboxes, identities, and handoffs |
| 4-10 agents become chaotic | Scale comfortably to 20-30 agents |
| Work state lost in agent memory | Work state stored in Beads ledger |

## Component Overview

```
         ┌─────────────────────────────────────────────────────┐
         │                    TOWN (~/gt/)                     │
         │                                                     │
         │   ┌─────────┐    ┌─────────┐    ┌─────────┐        │
         │   │  Mayor  │    │ Deacon  │    │  Boot   │        │
         │   │   🦊    │    │   ⚙️    │    │         │        │
         │   └────┬────┘    └────┬────┘    └────┬────┘        │
         │        │              │              │              │
         │        └──────────────┼──────────────┘              │
         │                       │                             │
         │   ┌───────────────────┼───────────────────┐        │
         │   │              RIG (vtuber/)             │        │
         │   │                   │                    │        │
         │   │   ┌───────────────┼───────────────┐   │        │
         │   │   │               │               │   │        │
         │   │   ▼               ▼               ▼   │        │
         │   │ Witness 🦅    Refinery 🦡    Polecats │        │
         │   │                               🦨🦨🦨   │        │
         │   │                                       │        │
         │   │   ┌─────────────────────────────┐    │        │
         │   │   │         .beads/             │    │        │
         │   │   │   formulas/ → ../../.beads/ │    │        │
         │   │   │   issues.jsonl              │    │        │
         │   │   └─────────────────────────────┘    │        │
         │   └───────────────────────────────────────┘        │
         └─────────────────────────────────────────────────────┘
```

## Agents

### Mayor 🦊
Primary AI coordinator. A Claude Code instance with full context about workspace, projects, and agents.
- Dispatches work, coordinates across rigs
- Creates convoys, slings beads to polecats
- **Must send SWARM_START** when dispatching batches for completion tracking

### Witness 🦅
Per-rig worker monitor.
- Watches polecats for stuck/completed state
- Runs patrol cycles checking worker health
- Sends SWARM_COMPLETE to Mayor when batch finishes
- Escalates issues to Mayor

### Refinery 🦡
Merge queue processor.
- Processes polecat branches from merge queue
- Merges to main after review
- Closes beads after successful merge
- Handles conflict resolution

### Polecats 🦨
Ephemeral worker agents.
- Spawned by Mayor via `gt sling`
- Follow `mol-polecat-work` lifecycle (9 steps)
- Self-destruct after submitting to merge queue
- Work on feature branches, never main directly

### Deacon ⚙️
Infrastructure daemon.
- Background patrol loop
- Health checks, session monitoring
- Nudges agents periodically

### Dogs 🐕
Cross-rig infrastructure workers.
- Diagnostics and health checks
- Recovery operations

## Work Flow

```
1. You describe work to Mayor
         │
         ▼
2. Mayor creates beads + convoy
         │
         ▼
3. Mayor slings beads to polecats
   ├── Sends SWARM_START to Witness
   └── Polecats get mol-polecat-work formula
         │
         ▼
4. Polecats execute 9-step lifecycle
   ├── Branch setup
   ├── Implement
   ├── Self-review
   ├── Tests
   └── Submit to merge queue
         │
         ▼
5. Refinery merges branches to main
         │
         ▼
6. Witness detects completion
   └── Sends SWARM_COMPLETE to Mayor
         │
         ▼
7. Mayor dispatches dependent work
```

## Key Mechanisms

### Hooks 🪝
Git worktree-based persistent storage.
- Each agent has a hook where work lands
- Survives crashes and restarts
- **GUPP**: If there's work on your hook, you RUN IT

### Formulas 📜
Workflow templates (TOML files).
- `mol-polecat-work` — Standard 9-step polecat lifecycle
- `mol-witness-patrol` — Witness monitoring loop
- `mol-refinery-patrol` — Merge queue processing

**Critical**: Rigs need formulas symlinked from town level:
```bash
cd ~/gt/<rig>/.beads && ln -s ../../.beads/formulas formulas
```

### Convoys 🚚
Work tracking bundles.
- Group related beads together
- Track progress across multiple polecats
- Auto-close when all beads complete

### Mail System 📬
Inter-agent communication.
- `gt mail send <target> -s "subject" -m "message"`
- `gt mail inbox` to check messages
- Special messages: SWARM_START, SWARM_COMPLETE, POLECAT_DONE, MERGED

## The Propulsion Principle (GUPP)

**Gas Town Universal Propulsion Principle:**
> If your hook has work, RUN IT.

No waiting. No asking. Work lands on hook → work runs.

Molecules (work units) survive crashes. Any worker can continue where another left off. The engine never stops as long as there's fuel.

## Scaling

Gas Town comfortably scales to 20-30 concurrent agents:
- Each polecat is independent Claude Code process
- Git-backed state means work persists if agents crash
- Witness monitors all polecats in a rig
- Mayor coordinates across rigs
