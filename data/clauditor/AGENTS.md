# AGENTS.md — Clauditor

## 1. Mission (North Star)

**What we're building:** A tamper-resistant audit watchdog that makes it *hard* for a compromised AI agent to operate without leaving a trail or cover tracks.

**Goals (numbered):**
1. Separate user (`sysaudit`) runs daemon — can't be killed/manipulated by monitored agent
2. Append-only logs with HMAC hash chains — tamper-evident audit trail
3. Real-time detection of suspicious patterns — exfil, injection, persistence, tamper attempts
4. Sentinel process detects if watchdog is killed/deleted
5. <3 minute install via interactive wizard
6. Stealth deployment — blends with system services to avoid obvious detection

---

## 2. Core Architecture

```
clauditor/
├── AGENTS.md           # This file — agent instructions
├── CONTINUITY.md       # State ledger — read/update every turn
├── PLAN.md             # Detailed architecture, threat model, beads
├── Cargo.toml          # Workspace manifest
├── Cargo.lock          # Dependency lock
├── crates/
│   ├── schema/         # Event types + HMAC hash chain
│   │   └── src/lib.rs
│   ├── detector/       # Rule-based detection engine
│   │   ├── src/lib.rs
│   │   └── src/rules.rs
│   ├── collector/      # Event capture (inotify/fanotify/eBPF)
│   │   └── src/lib.rs  # TODO: Bead 3-4
│   └── clauditor/      # Main binary + CLI
│       └── src/main.rs # TODO: Bead 5+
└── target/             # Build artifacts (gitignored)
```

**No backend/frontend/DB** — this is a standalone Rust daemon:
- **Input:** filesystem events, process events, shell history
- **Output:** append-only log files with HMAC chain
- **Alerts:** syslog/journald integration, optional webhook

---

## 3. Tech Stack

| Layer | Choice | Specifics |
|-------|--------|-----------|
| **Language** | Rust | 2021 edition, workspace with multiple crates |
| **Build** | Cargo | `cargo build`, `cargo test`, `cargo build --release` |
| **Event capture (dev)** | inotify | `inotify` crate for unprivileged dev mode |
| **Event capture (prod)** | fanotify + eBPF | Privileged mode with UID filtering |
| **Hashing** | HMAC-SHA256 | `hmac` + `sha2` crates, key stored root-owned |
| **Serialization** | JSON | `serde_json` for events, human-readable logs |
| **Service** | systemd | Hardened unit file with sandboxing |
| **Testing** | `cargo test` | Unit tests in each crate |

---

## 4. Agent Prototypes

When spawning sub-agents for clauditor work, use these roles:

### Architect (Opus)
- Reviews bead outputs for quality and security implications
- Makes architectural decisions
- Writes CONTINUITY.md updates
- Sends summaries to chat
- Commits after each bead

### Engineer (Sonnet via Codex)
- Implements beads according to PLAN.md
- Writes tests that prove functionality
- Follows Rust idioms and error handling
- Must pass `cargo test` before completing

### Analyst (Sonnet)
- Reviews threat model assumptions
- Identifies edge cases in detection rules
- Validates security properties

---

## 5. Branching & Commits

### Branch Convention
- `main` — stable, all tests pass
- `bead-N-description` — feature branches for individual beads (optional)

### Commit Convention
```
<type>(bead-N): <description>

<body with details>

Run: <run_id if applicable>
```

**Types:**
- `feat` — new functionality
- `fix` — bug fix
- `test` — test additions
- `docs` — documentation
- `chore` — maintenance, cleanup

**Examples:**
```
feat(bead-1): schema crate with HMAC hash chain
feat(bead-2): detector crate with 20+ rules
feat(bead-3): collector dev mode with inotify
```

---

## 6. Continuity Ledger

### Protocol
**Read CONTINUITY.md at start of every turn. Update it before committing.**

### CONTINUITY.md Format (exact headings)
```markdown
# CONTINUITY.md — Clauditor

## Goal (incl. success criteria)
[What we're building and how we'll know it's done]

## Constraints/Assumptions
[Key constraints, environment assumptions]

## Key Decisions
[Numbered list — append only, never delete]

## State

### Done
- [x] Completed beads with brief description

### Now
- Current bead being worked on

### Next
- Upcoming beads in order

## Open Questions
[Things that need resolution — mark UNCONFIRMED if uncertain]

## Working Set
[Key files, commands, paths for current work]
```

### Beads vs Ledger
| Concept | Purpose | Lifetime |
|---------|---------|----------|
| **Bead** | Discrete unit of work (session, commit) | Short-term execution |
| **CONTINUITY.md** | State across all beads | Long-term, persists across sessions |

### Ledger Snapshot
Every reply from the orchestrating agent (Opus) should start with:
```
📒 Ledger Snapshot
- Now: Bead N — [description]
- Done: N of M beads
- Tests: ✅ passing / ❌ failing
- Blockers: [any blockers or "none"]
```

### UNCONFIRMED Rule
If uncertain about any state, mark it:
```
## Open Questions
- UNCONFIRMED: Does fanotify require CAP_SYS_ADMIN or just CAP_PERFMON?
```

---

## 7. Workflow

### Every Turn (Orchestrator/Opus)
1. **Read** CONTINUITY.md — understand current state
2. **Spawn** Engineer sub-agent for current bead (via Codex `--full-auto`)
3. **Wait** for bead completion
4. **Review** the output:
   - Read changed files
   - Run `cargo test`
   - Check for quality, completeness, security
5. **Summarize** to chat:
   ```
   🔵 Bead N Complete: [title]
   
   **Changes:** [files modified]
   **Tests:** [pass/fail count]
   **Summary:** [2-3 sentences]
   **Status:** ✅ Approved / ⚠️ Concerns / ❌ Failed
   ```
6. **Commit** with structured message
7. **Update** CONTINUITY.md — move bead from Now → Done, advance Next → Now
8. **Push** to GitHub

### Every Bead (Engineer/Codex)
1. Read CONTINUITY.md and PLAN.md
2. Implement the bead
3. Write tests that prove it works
4. Run `cargo test` — all must pass
5. Report completion

---

## 8. Orchestration

### Multi-Agent Coordination
```
┌─────────────────────────────────────────────────┐
│  Orchestrator (Opus 4.5 / Grace)                │
│  - Reviews, summarizes, commits                 │
│  - Updates CONTINUITY.md                        │
│  - Sends progress to chat                       │
└──────────────────┬──────────────────────────────┘
                   │ spawns
                   ▼
┌─────────────────────────────────────────────────┐
│  Engineer (Codex --full-auto)                   │
│  - Implements current bead                      │
│  - Writes tests                                 │
│  - Reports completion                           │
└─────────────────────────────────────────────────┘
```

### Bead Execution Protocol
1. Orchestrator reads CONTINUITY.md, identifies current bead
2. Orchestrator spawns Engineer with task: "Implement Bead N: [description]"
3. Engineer works in `/home/clawdbot/clawd/skills/clauditor/`
4. Engineer completes, returns summary
5. Orchestrator reviews output, runs tests
6. If pass: commit, update ledger, notify chat, advance to next bead
7. If fail: retry or escalate to user

### GitHub Integration
- **Repo:** `apollostreetcompany/clauditor`
- **Push after each bead** — never batch multiple beads
- **Author:** Configured in git config or commit with `--author`

---

## Quick Reference

```bash
# Setup
cd /home/clawdbot/clawd/skills/clauditor
source ~/.cargo/env

# Build & Test
cargo build
cargo test

# Check state
cat CONTINUITY.md

# Current bead
grep "### Now" -A 2 CONTINUITY.md
```

---

*Last updated: 2026-01-26*
