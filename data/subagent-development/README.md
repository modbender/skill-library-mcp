# Subagent-Driven Development

Execute implementation plans by dispatching fresh subagents per task, with two-stage review after each: spec compliance review first, then code quality review. Ensures high quality and fast iteration.

## What's Inside

- When to use decision tree (have plan? tasks independent? stay in session?)
- The process flow (dispatch implementer → spec review → code quality review → next task)
- Prompt templates (implementer, spec reviewer, code quality reviewer)
- Example workflow walkthrough
- Advantages vs manual execution and executing-plans
- Red flags and rules for subagent interaction

## When to Use

- Have an implementation plan with mostly independent tasks
- Want to stay in the current session (vs. parallel sessions)
- Need fresh context per task to avoid context pollution
- Want automatic quality gates (spec compliance + code quality)
- Faster iteration without human-in-loop between tasks

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/subagent-development
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install subagent-development
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/subagent-development .cursor/skills/subagent-development
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/subagent-development ~/.cursor/skills/subagent-development
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/subagent-development .claude/skills/subagent-development
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/subagent-development ~/.claude/skills/subagent-development
```

## Related Skills

- `writing-plans` — Creates the plan this skill executes
- `requesting-code-review` — Code review template for reviewer subagents
- `finishing-a-development-branch` — Complete development after all tasks
- `test-driven-development` — Subagents follow TDD for each task
- `executing-plans` — Alternative for parallel session execution

---

Part of the [Meta](..) skill category.
