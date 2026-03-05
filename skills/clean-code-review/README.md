# Clean Code

Pragmatic coding standards for writing clean, maintainable code — naming, functions, structure, anti-patterns, and pre-edit safety checks. Every name reveals intent, every function does one thing, and every abstraction earns its place.

## What's Inside

- Core principles (SRP, DRY, KISS, YAGNI, Boy Scout Rule)
- Naming rules and naming anti-patterns
- Function rules (small, one thing, few args, guard clauses, parameter objects)
- Code structure patterns (composition, colocation, extract function)
- Return type consistency with discriminated unions
- Anti-patterns catalog (21 common mistakes)
- Pre-edit safety check (dependency impact analysis)
- Reference guides for code smells, anti-patterns, and refactoring catalog

## When to Use

- Writing new code and wanting to follow best practices
- Refactoring existing code for clarity and maintainability
- Reviewing code quality in pull requests
- Establishing coding standards for a team

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/testing/clean-code
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install clean-code-review
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/testing/clean-code .cursor/skills/clean-code
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/testing/clean-code ~/.cursor/skills/clean-code
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/testing/clean-code .claude/skills/clean-code
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/testing/clean-code ~/.claude/skills/clean-code
```

## Related Skills

- [code-review](../code-review/) — Structured code review checklists
- [reducing-entropy](../reducing-entropy/) — Minimize codebase size through simplification
- [testing-patterns](../testing-patterns/) — Testing patterns for verifying clean code

---

Part of the [Testing](..) skill category.
