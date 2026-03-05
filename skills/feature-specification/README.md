# Feature Specification

Convert persona docs into detailed feature specifications with acceptance criteria. Bridges persona documentation and development by translating user needs into implementable specs.

## What's Inside

- Feature spec template (metadata, problem statement, user stories, acceptance criteria, edge cases, NFRs, dependencies)
- Writing effective user stories with INVEST criteria
- Acceptance criteria patterns (happy path, boundary conditions, error cases, state transitions, negative/security)
- Priority framework (MoSCoW anchored to persona impact)
- Specification anti-patterns
- Integration with development workflow

## When to Use

- After persona docs exist and before development begins
- When a feature request lacks clear acceptance criteria
- When stakeholders disagree on what "done" means
- When converting user feedback into development work

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/feature-specification
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install feature-specification
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/feature-specification .cursor/skills/feature-specification
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/feature-specification ~/.cursor/skills/feature-specification
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/feature-specification .claude/skills/feature-specification
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/feature-specification ~/.claude/skills/feature-specification
```

## Related Skills

- `persona-docs` — Source of truth for user needs (input to this skill)

---

Part of the [Meta](..) skill category.
