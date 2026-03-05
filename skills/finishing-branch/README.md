# Finishing a Development Branch

Complete development work by presenting structured options for merge, PR, or cleanup. After implementation is complete, guides you through verifying tests, presenting integration options, and executing the chosen path.

## What's Inside

- Test verification before proceeding
- Base branch detection
- Four integration options: Merge locally, Push and create PR, Keep as-is, Discard
- Worktree cleanup procedures
- Quick reference table for each option's behavior
- Safety guards (typed confirmation for destructive actions)

## When to Use

- Implementation is complete
- All tests pass
- Ready to integrate work into the main branch
- Triggered by: "finish branch", "complete branch", "merge branch", "create PR", "done with feature", "implementation complete"

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/tools/finishing-branch
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/tools/finishing-branch .cursor/skills/finishing-branch
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/tools/finishing-branch ~/.cursor/skills/finishing-branch
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/tools/finishing-branch .claude/skills/finishing-branch
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/tools/finishing-branch ~/.claude/skills/finishing-branch
```

## Related Skills

- **subagent-driven-development** — Calls this skill after all tasks complete
- **session-handoff** — For preserving context when pausing work

---

Part of the [Tools](..) skill category.
