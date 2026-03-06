---
name: claude-code-teams
description: "Production skill for orchestrating Claude Code's native agent
  teams feature. Use when: (1) Multi-lens reviews, (2) Competing hypotheses
  debugging, (3) Full-stack features, (4) Architecture debates, (5) Cross-domain
  investigations."
---


# Claude Code Agent Teams

Orchestrate multiple Claude Code agents working together on complex tasks. Agents coordinate through a shared task list, message each other directly, and work in parallel on independent scopes.

## When to Use

✅ **Use for parallel independent work:**
- Multi-lens code reviews (security, performance, tests in parallel)
- Debugging with competing hypotheses (test theories simultaneously)
- Full-stack features (frontend/backend/tests by separate specialists)
- Architecture decisions (adversarial debate produces stronger ADRs)
- Cross-domain investigations (bottleneck analysis across systems)
- Data-parallel work (inventory classification, bulk refactoring)

❌ **Don't use for:**
- Sequential work with tight dependencies
- Same-file edits (conflict risk)
- Simple tasks (coordination overhead > benefit)
- Learning/exploration (single agent with full context is better)

**Rule of thumb:** Teams multiply token cost 3-4x. Use only when parallelization benefit exceeds coordination overhead.

## Quick Start

### 1. Enable Feature

**Environment variable:**
```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

**Or settings file** (`~/.claude/settings.json`):
```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 2. Validate Setup

```bash
./scripts/validate-setup.sh
```

Checks for: env var set, `claude` CLI available, `tmux` installed (optional).

### 3. Pick Template

| Template | Use Case |
|----------|----------|
| `parallel-review.md` | Multi-lens code review (security + performance + tests) |
| `competing-hypotheses.md` | Debug by testing competing theories |
| `fullstack-feature.md` | Frontend/backend/tests coordination |
| `architecture-decision.md` | ADR with adversarial debate |
| `bottleneck-analysis.md` | Cross-domain performance investigation |
| `inventory-classification.md` | Data-parallel classification/refactoring |

Each template includes: when to use, team structure, copy-paste spawn prompt, expected outcomes.

### 4. Spawn Team

```bash
claude --pty
# Paste spawn prompt from template
```

Monitor with `./scripts/team-monitor.sh` (separate terminal) or `Ctrl+T` (in Claude Code).

## Core Principles

1. **Clear file boundaries** - Each teammate owns different files/directories (prevents conflicts)
2. **Use delegate mode** - Lead coordinates, teammates implement (include in spawn prompt)
3. **Size tasks appropriately** - 5-6 self-contained tasks per teammate
4. **Wait for completion** - Don't let lead merge results while teammates are mid-task
5. **Start with research** - Spawn researchers before builders to establish shared understanding

## Cost Management

Agent teams multiply token usage **3-4x** vs single session. Each teammate has its own context window.

**Optimize with:**
- **Model mixing** - Opus for lead (strategic), Sonnet for teammates (tactical) = ~40% savings
- **Minimize broadcasts** - Direct messages only (broadcasts copy to all teammates)
- **Right-size teams** - 3 teammates usually optimal; 6+ only for highly parallel work

See `references/cost-management.md` for detailed strategies.

## Troubleshooting

**Teammates not spawning?**
- Verify `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set
- Restart Claude Code after setting env var

**File conflicts?**
- Define explicit file boundaries in spawn prompt (directory-level ownership)

**Lead implementing instead of coordinating?**
- Add "Use delegate mode: coordinate but don't implement" to spawn prompt
- Or press Shift+Tab to cycle into delegate mode

See `references/troubleshooting.md` for full list.

## Automation

**Monitor progress:**
```bash
./scripts/team-monitor.sh
```

**Cleanup (graceful shutdown):**
```bash
./scripts/team-cleanup.sh
```

## Display Modes

**In-process** (default) - All teammates in main terminal
- `Shift+Up/Down` - Select teammate
- `Ctrl+T` - Toggle task list
- `Escape` - Interrupt teammate

**Split-pane** (requires tmux or iTerm2) - Each teammate gets own pane
- Set `teammateMode: "tmux"` in `~/.claude/settings.json`

## References

- **`templates/`** - 6 copy-paste ready spawn prompts with usage guidance
- **`scripts/`** - Automation helpers (validate, monitor, cleanup)
- **`references/best-practices.md`** - When to use teams, task sizing, file boundaries
- **`references/cost-management.md`** - Token optimization strategies
- **`references/troubleshooting.md`** - Common issues and solutions
- **`examples/`** - Real-world walkthroughs (PR review, bug hunt, feature build)

## Comparison

| Approach | Best For |
|----------|----------|
| Single session | Sequential work, exploration |
| Agent teams (this skill) | Parallel independent tasks with coordination |
| OpenClaw subagents | Background work, long-running tasks |

## Contributing

Found a useful pattern? Submit PR with:
1. Template or example
2. When to use + team structure
3. Spawn prompt + expected outcomes

## Credits

Built with insights from Claude Code documentation, ClaudeFast patterns, and OpenClaw community.

---

**Repository:** https://github.com/matthew-a-gordon/claude-code-teams  
**License:** MIT
