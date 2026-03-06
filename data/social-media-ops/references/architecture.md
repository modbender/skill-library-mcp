# Architecture — Star Topology & A2A Sessions

## System Design

The social-media-ops system uses a strict **star topology** with persistent A2A (Agent-to-Agent) sessions. The Leader agent is the sole hub; all other agents are spokes. No spoke-to-spoke communication exists.

```
                    +-----------+-----------+
                    |       LEADER          |
                    |                       |
                    |  - Orchestration      |
                    |  - Task decomposition |
                    |  - Quality control    |
                    |  - Owner interface    |
                    |  - shared/ writes     |
                    +-----------+-----------+
                         /  |  |  \  \  \
                  sessions_send (persistent)
                       /    |  |    \  \  \
              +------+  +---+  +--+  +--+--+  +------+  +--------+
              |Rsrchr|  |Cont| |Des| |Oper |  | Engr |  |Reviewer|
              +------+  +----+ +---+ +-----+  +------+  +--------+
```

## Why Star Topology?

1. **Single point of accountability** — Leader owns all owner-facing communication.
2. **Context control** — Leader curates what context each agent receives.
3. **Quality gate** — All output is reviewed before reaching the owner.
4. **Audit trail** — Every delegation and result flows through one node.
5. **Centralized knowledge writes** — All shared/ updates go through Leader (via `[KB_PROPOSE]`).

## Session Model

| Property | Value |
|----------|-------|
| Communication method | `sessions_send` (persistent sessions) |
| Session key format | `agent:{id}:main` |
| Same-agent concurrency | Serial (one task at a time) |
| Cross-agent concurrency | Parallel |
| Ping-pong limit | 3 rounds per `sessions_send` |
| Context preservation | Full — survives across tasks and feedback loops |
| Compaction handling | Agent sends `[CONTEXT_LOST]`; Leader re-sends from `tasks/T-{id}.md` |

## Maintenance Commands (v2026.2.26+)

| Command | Purpose |
|---------|---------|
| `openclaw agents bindings` | View agent-to-channel route bindings |
| `openclaw agents bind/unbind` | Manage agent routing |
| `openclaw sessions cleanup --fix-missing` | Prune stale session entries |
| `openclaw secrets audit` | Check for plaintext secrets |
| `openclaw doctor` | Validate config, DM allowlist, sessions |

## Request Lifecycle

```
Owner sends message → Leader receives → Analyzes intent →
  Decomposes into atomic subtasks → Routes to agents (parallel when possible) →
  Agents work and return results → Leader consolidates →
  Quality check (optional Reviewer) → Present to owner [PENDING APPROVAL] →
  Owner approves → Final action (publish/execute)
```

## Parallelism Strategy

- **Independent tasks** → run in parallel across different agents (e.g., Content writes copy while Designer creates visuals)
- **Dependent tasks** → run in sequence (e.g., Research → Content → Review)
- **Same agent** → always serial (one task at a time per agent)
- **Cross-agent** → parallel by default

## Workspace Isolation

Each agent has its own workspace directory. The shared knowledge base is symlinked in:

```
workspace/                           # Leader
├── SOUL.md, AGENTS.md, HEARTBEAT.md, IDENTITY.md
├── memory/, skills/, assets/
└── shared/                          # Real directory (shared KB lives here)

workspace-{agent}/                   # Sub-agents
├── SOUL.md              # Agent persona, tone, and boundaries
├── AGENTS.md            # Operating instructions and behavioral rules
├── MEMORY.md            # Agent-specific long-term memory
├── memory/              # Agent-specific daily notes
├── skills/              # Agent-specific skill packages
└── shared -> ../workspace/shared/   # Symlink to Leader's shared KB
```
