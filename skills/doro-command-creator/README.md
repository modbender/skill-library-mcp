# Command Creator

Create Claude Code slash commands — reusable markdown workflows invoked with `/command-name`. Slash commands are markdown files in `.claude/commands/` (project) or `~/.claude/commands/` (global) that expand into prompts when invoked.

## What's Inside

- Command structure and frontmatter format
- Creation workflow (location, pattern, info gathering, generation, testing)
- Writing guidelines (imperative form, specificity, outcomes)
- Command patterns: Workflow Automation, Iterative Fixing, Agent Delegation, Simple Execution
- Quality checklist for finalizing commands
- Reference files for patterns, best practices, and examples

## When to Use

- User wants to create, make, or add a slash command
- User wants to automate a repetitive workflow
- User wants to document a consistent process for reuse
- Triggered by: "create a command", "make a slash command", "add a command", "new command", "/command", "automate this workflow", "make this repeatable"

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/tools/command-creator
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/tools/command-creator .cursor/skills/command-creator
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/tools/command-creator ~/.cursor/skills/command-creator
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/tools/command-creator .claude/skills/command-creator
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/tools/command-creator ~/.claude/skills/command-creator
```

## Related Skills

- **skill-creator** — For creating agent skills (broader than slash commands)
- **subagent-driven-development** — Uses commands within delegated workflows

---

Part of the [Tools](..) skill category.
