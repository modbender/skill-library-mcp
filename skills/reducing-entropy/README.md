# Reducing Entropy

Minimize total codebase size through ruthless simplification. Measure success by the final code amount, not effort. Bias toward deletion — more code begets more code, and entropy accumulates.

## What's Inside

- The goal: less total code in the final codebase
- Three guiding questions (smallest codebase, less total code, what to delete)
- Red flags and challenge phrases ("adds flexibility", "better separation", "we might need this later")
- Deletion checklist for every refactor
- Quick wins table (inline wrappers, delete single-implementation interfaces, merge abstract classes)
- Reference mindsets (simplicity vs easy, design is taking apart, data over abstractions, expensive to add later)
- The Grug perspective on complexity

## When to Use

- Refactoring code and considering options
- Adding a new feature and choosing implementation approach
- Reviewing PRs to challenge unnecessary complexity
- Paying down tech debt and prioritizing what to simplify
- Explicitly asked for code reduction or simplification

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/testing/reducing-entropy
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/testing/reducing-entropy .cursor/skills/reducing-entropy
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/testing/reducing-entropy ~/.cursor/skills/reducing-entropy
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/testing/reducing-entropy .claude/skills/reducing-entropy
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/testing/reducing-entropy ~/.claude/skills/reducing-entropy
```

## Related Skills

- [clean-code](../clean-code/) — Coding standards with YAGNI and KISS principles
- [code-review](../code-review/) — Review PRs with a simplification lens

---

Part of the [Testing](..) skill category.
