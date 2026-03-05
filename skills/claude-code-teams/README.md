# 🎭 Claude Code Agent Teams

**Production-ready orchestration for Claude Code's native agent teams feature.**

> Coordinate multiple Claude Code agents working together on complex tasks. Multi-lens code reviews, parallel debugging, and full-stack coordination with templates for common patterns.

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Why This Skill?

Claude Code's agent teams feature lets you spawn multiple AI agents that coordinate through a shared task list and mailbox. But knowing *when* and *how* to use teams effectively is non-trivial.

This skill provides:
- ✅ **6 templates** for common patterns (code review, debugging, full-stack builds)
- ✅ **Automation scripts** for validation, monitoring, and cleanup
- ✅ **Cost optimization** guidance (model mixing, team sizing)
- ✅ **Real-world examples** with step-by-step walkthroughs
- ✅ **Best practices** from Claude Code docs + ClaudeFast patterns

---

## Quick Start

### 1. Install

```bash
# Install via ClawHub
clawhub install claude-code-teams
```

### 2. Enable Agent Teams

**Option A: Environment Variable**

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Add to your shell profile (`~/.zshrc`, `~/.bashrc`) to persist.

**Option B: Claude Settings File**

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 3. Validate Setup

```bash
cd ~/.openclaw/workspace/skills/claude-code-teams
./scripts/validate-setup.sh
```

### 4. Pick a Template

Choose from 6 templates:

| Template | Use When |
|----------|----------|
| **parallel-review** | Need multi-lens code review (security + performance + tests) |
| **competing-hypotheses** | Debugging with multiple plausible theories |
| **fullstack-feature** | Building frontend + backend + tests in parallel |
| **architecture-decision** | Making ADR with adversarial debate |
| **bottleneck-analysis** | Investigating performance across systems |
| **inventory-classification** | Bulk refactoring/classification (data-parallel) |

### 5. Spawn Team

```bash
# Start Claude Code in PTY mode
claude --pty

# Paste spawn prompt from template
# Example from templates/parallel-review.md:
"I need a code review with 3 perspectives: security, performance, and test coverage.

Spawn 3 teammates:
- Security Reviewer: Check for vulnerabilities, auth issues, input validation
- Performance Reviewer: Identify bottlenecks, inefficient queries, scaling issues
- Test Coverage Reviewer: Assess test quality, missing edge cases, flaky tests

Target: ./src directory

Each reviewer should:
1. Analyze assigned domain independently
2. Document findings in findings-{domain}.md
3. Report critical issues immediately

Use delegate mode: I coordinate, teammates review."
```

---

## When to Use Agent Teams

### ✅ Strong Use Cases

**Multi-lens code reviews** → Parallel reviews from security, performance, test coverage perspectives

**Debugging with competing hypotheses** → Multiple agents test different theories simultaneously

**Full-stack features** → Frontend, backend, and test specialists work in parallel

**Architecture decisions** → Adversarial debate produces stronger ADRs

**Cross-domain investigations** → Bottleneck analysis across database, network, application layers

**Data-parallel work** → Inventory classification, bulk refactoring across independent files

### ❌ Poor Fit

**Simple tasks** → Single agent is faster

**Sequential dependencies** → Task B can't start until A completes

**Same-file edits** → Conflict risk when multiple agents edit same file

**Tight loops** → Frequent back-and-forth better in single session

**Learning/exploration** → Single agent with full context learns faster

**Budget constraints** → Teams multiply token costs

---

## Templates

### 1. Parallel Review

**Pattern:** Spawn 3 reviewers (security, performance, tests) who work independently, then synthesize findings.

**Speedup:** ~3x faster than sequential review

**Example output:**
```
findings-security.md    → SQL injection risk in user-input.ts
findings-performance.md → N+1 query in posts endpoint
findings-tests.md       → Missing edge case tests for pagination
```

[View template →](templates/parallel-review.md)

---

### 2. Competing Hypotheses

**Pattern:** Spawn 2-3 agents, each investigating a different hypothesis. They report findings, then debate.

**Speedup:** Identifies root cause faster than sequential investigation

**Example:**
```
Hypothesis A: Database connection pool exhausted
Hypothesis B: Memory leak in worker process
Hypothesis C: Network latency to external API
```

[View template →](templates/competing-hypotheses.md)

---

### 3. Full-Stack Feature

**Pattern:** Spawn frontend, backend, and test specialists with clear interface contracts.

**Speedup:** ~2-3x faster than sequential implementation

**Example:**
```
Frontend: React component + API integration
Backend: FastAPI endpoint + business logic
Tests: Integration + unit tests for both layers
```

[View template →](templates/fullstack-feature.md)

---

### 4. Architecture Decision

**Pattern:** Spawn 2 agents with opposing positions. They debate, then synthesize into ADR.

**Outcome:** Stronger decisions with explored alternatives

**Example:**
```
Agent A: Advocate for PostgreSQL (relational benefits)
Agent B: Advocate for MongoDB (flexibility benefits)
Output: ADR with trade-offs and recommendation
```

[View template →](templates/architecture-decision.md)

---

### 5. Bottleneck Analysis

**Pattern:** Spawn domain experts (DB, network, app, frontend) to investigate in parallel.

**Speedup:** Faster identification across full stack

**Example:**
```
DB Analyst: Check slow queries, connection pool
Network Analyst: Check latency, packet loss
App Analyst: Check CPU/memory usage
Frontend Analyst: Check render performance, bundle size
```

[View template →](templates/bottleneck-analysis.md)

---

### 6. Inventory Classification

**Pattern:** Divide items across N agents, each processes their subset independently.

**Speedup:** Linear (3 agents = ~3x faster)

**Example:**
```
Agent 1: Process files 1-100
Agent 2: Process files 101-200
Agent 3: Process files 201-300
```

[View template →](templates/inventory-classification.md)

---

## Scripts

### validate-setup.sh

Check prerequisites before spawning teams.

```bash
./scripts/validate-setup.sh
```

Checks:
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true` is set
- `claude` CLI is available
- `tmux` is installed (for split-pane display)

---

### team-monitor.sh

Monitor task list and teammate status in real-time.

```bash
./scripts/team-monitor.sh
```

Shows:
- Task list (pending → in progress → complete)
- Active teammates and current work
- Recent inter-agent messages

---

### team-cleanup.sh

Gracefully shut down teammates before exiting.

```bash
./scripts/team-cleanup.sh
```

Ensures teammates complete current tasks, then shuts down in order.

---

## Cost Management

Agent teams multiply token usage. Optimize with:

### Model Mixing

Use Opus for lead (strategic decisions), Sonnet for teammates (tactical work).

```bash
claude --model opus

# Then in spawn prompt:
"Spawn 3 teammates using Sonnet"
```

**Impact:** ~40% cost reduction vs all-Opus team

### Right-Size Teams

- **3 teammates:** Usually optimal (parallelism without excessive coordination)
- **6 teammates:** Only for highly parallelizable work
- **1 teammate:** Just use single session instead

### Estimated Costs

| Team Size | Duration | Model Mix | Cost |
|-----------|----------|-----------|------|
| 1 lead + 3 teammates | 30 min | Opus lead, Sonnet team | $15-25 |
| 1 lead + 3 teammates | 30 min | All Opus | $25-40 |
| 1 lead + 6 teammates | 30 min | Opus lead, Sonnet team | $25-40 |

See [references/cost-management.md](references/cost-management.md) for detailed strategies.

---

## Examples

### PR Review ([examples/pr-review-example.md](examples/pr-review-example.md))

Step-by-step walkthrough of parallel PR review:
1. Security reviewer checks auth + input validation
2. Performance reviewer profiles queries + rendering
3. Test reviewer assesses coverage + edge cases
4. Lead synthesizes findings into review comment

**Speedup:** 3x faster than sequential review

---

### Bug Hunt ([examples/bug-hunt-example.md](examples/bug-hunt-example.md))

Competing hypotheses pattern for root cause analysis:
1. Spawn 3 agents with different theories
2. Each investigates independently (logs, metrics, traces)
3. Report findings + confidence level
4. Debate and converge on root cause

**Outcome:** Faster diagnosis through parallel investigation

---

### Feature Build ([examples/feature-build-example.md](examples/feature-build-example.md))

Full-stack coordination for user authentication:
1. Backend agent builds FastAPI endpoint + JWT logic
2. Frontend agent builds React login form + API integration
3. Test agent writes integration + unit tests
4. Lead reviews integration points, merges code

**Speedup:** 2-3x faster than sequential implementation

---

## Best Practices

### Clear File Boundaries

```markdown
❌ Bad: "Alice and Bob both work on user-service.ts"
✅ Good: "Alice owns user-service.ts, Bob owns user-repository.ts"
```

### Use Delegate Mode

```markdown
"You are the lead coordinator. Use delegate mode: assign tasks but don't implement yourself."
```

### Size Tasks Appropriately

- **Too small:** High coordination overhead
- **Just right:** 5-6 self-contained tasks per teammate
- **Too large:** Risk of context loss

### Wait for Completion

```markdown
"Wait for all teammates to finish before synthesizing results."
```

See [references/best-practices.md](references/best-practices.md) for detailed guidance.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Teammates not spawning | Check `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true`, restart Claude Code |
| Same-file conflicts | Fix file boundaries in spawn prompt |
| Lead implementing instead of coordinating | Add "Use delegate mode" to spawn prompt |
| High costs | Use model mixing, reduce team size, minimize broadcasts |

See [references/troubleshooting.md](references/troubleshooting.md) for full list.

---

## Comparison with Alternatives

| Approach | Best For | Limitations |
|----------|----------|-------------|
| **Single Claude Code session** | Sequential work, learning | Can't parallelize |
| **Claude Code teams** (this skill) | Parallel independent tasks | Coordination overhead |
| **OpenClaw subagents** | Background work | No shared state |
| **Multiple terminals** | Isolated tasks | No coordination |

---

## Contributing

Found a useful pattern? Contributions welcome!

1. Fork this repo
2. Add template to `templates/` or example to `examples/`
3. Include: when to use, team structure, spawn prompt, expected outcomes
4. Submit PR with example output

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Credits

Built with insights from:
- [Claude Code official documentation](https://github.com/anthropics/claude-code)
- ClaudeFast best practices
- OpenClaw community patterns

---

**Questions?** Open an issue or see [references/troubleshooting.md](references/troubleshooting.md)

**Want to contribute?** See [examples/](examples/) for template format
