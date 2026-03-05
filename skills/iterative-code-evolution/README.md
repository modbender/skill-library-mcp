# Iterative Code Evolution

A Claude Code skill that replaces ad-hoc "try and fix" coding with structured improvement cycles. Adapted from the [ALMA](https://yimingxiong.me/alma) (Automated meta-Learning of Memory designs for Agentic systems) research framework.

## Installation

### OpenClaw

Search for **Iterative Code Evolution** on [OpenClaw](https://clawhub.ai) and click **Install**, or run:

```bash
openclaw install iterative-code-evolution
```

### Claude Code (CLI)

Copy `SKILL.md` into your Claude Code skills directory:

```bash
# Global (available in all projects)
cp SKILL.md ~/.claude/skills/iterative-code-evolution.md

# Per-project (available only in that project)
mkdir -p your-project/.claude/skills
cp SKILL.md your-project/.claude/skills/iterative-code-evolution.md
```

### Claude Desktop / Claude.ai

1. Copy the contents of `SKILL.md`
2. Open **Claude Desktop** or **Claude.ai**
3. Navigate to **Settings** > **Custom Instructions**
4. Paste the contents into the custom instructions field
5. Save

## What It Does

When activated, Claude follows a disciplined loop instead of making random fixes:

```
ANALYZE → PLAN → MUTATE → VERIFY → SCORE → ARCHIVE → repeat
```

Each cycle:

1. **Analyze** — Reviews past attempts, labels each component (Working / Fragile / Broken / Redundant / Missing), checks for cross-cutting issues
2. **Plan** — Picks 1-3 evidence-based changes (no speculative fixes allowed)
3. **Mutate** — Implements only the planned changes
4. **Verify** — Runs the code; up to 3 retries on crashes, then reverts
5. **Score** — Measures improvement against the parent variant, not just the baseline
6. **Archive** — Logs everything to `.evolution/log.json`, including failures and lessons learned

## When to Use It

- Code that isn't working well enough after initial attempts
- Performance or correctness optimization across multiple rounds
- Persistent bugs where simple fixes keep failing
- Evolving a design through structured experimentation
- Any situation where you've tried 2+ approaches and need a more disciplined strategy

## How It Tracks Progress

The skill maintains an `.evolution/` directory in your project:

```
.evolution/
  log.json              # Full history of every variant, score, and lesson
  variants/             # Snapshots of alternative approaches (when branching)
```

The log accumulates **principles learned** that are specific to your codebase, making each cycle smarter than the last.

## Key Rules

- **Max 3 changes per cycle** — keeps cause and effect clear
- **Every change must link to an observation** — no "this might help" guesses
- **Failures are logged, not discarded** — prevents re-attempting broken approaches
- **Explore when stuck** — if 2+ cycles on the same component show diminishing returns, switch focus
- **Revert after 3 failed retries** — don't spiral on a broken approach
