# Auto-Context — Situational Awareness Protocol

Automatically read relevant context before major actions. Loads TODO.md, roadmap.md, handoffs, task plans, and other project context files so the AI operates with full situational awareness.

## What's Inside

- Trigger-based activation rules (when to load context automatically)
- Context files to read with priority levels (Critical, High, Medium, Low)
- Context loading strategy (three-step prioritized loading)
- Staleness detection (flag outdated files by age)
- Context summary format template
- Integration points with other workflow commands

## When to Use

- Starting a new task — understand priorities, avoid conflicts
- Implementing a feature — know the plan, constraints, recent changes
- Refactoring code — understand what changed recently, what's planned
- Debugging an issue — check recent changes, known issues, discoveries
- Planning or scoping work — full picture of roadmap, backlog, progress
- Session start or resume — rebuild mental model from last session state
- Before a handoff — ensure nothing is missed in transition

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/auto-context
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install auto-context
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/auto-context .cursor/skills/auto-context
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/auto-context ~/.cursor/skills/auto-context
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/auto-context .claude/skills/auto-context
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/auto-context ~/.claude/skills/auto-context
```

---

Part of the [Meta](..) skill category.
