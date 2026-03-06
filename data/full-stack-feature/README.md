# Full-Stack Feature Orchestration

Meta-skill for orchestrating end-to-end feature development from persona research through deployed, tested code — coordinating skills, commands, and agents across every stage.

## What's Inside

- Eight-stage orchestration flow (persona research → feature spec → UX/UI design → API design → frontend → backend → testing → documentation)
- Skill routing table for each stage
- Stage gate checks (what must pass before proceeding)
- Vertical slice strategy (thin slice → widen → polish)
- Complexity assessment (trivial to epic sizing)
- Coordination patterns (frontend/backend in parallel, handoff points, progress tracking)

## When to Use

- Building a new feature end-to-end — need the full pipeline from research to production
- Frontend + backend work together — the feature spans UI, API, and data layers
- User research should inform implementation — want personas and specs before code
- Coordinating multiple skills — unsure which skill or command to invoke at each step
- Onboarding a new feature area — need a structured approach, not ad hoc implementation

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/meta/full-stack-feature
```

### OpenClaw / Moltbot / Clawbot

```bash
npx clawhub@latest install full-stack-feature
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/meta/full-stack-feature .cursor/skills/full-stack-feature
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/meta/full-stack-feature ~/.cursor/skills/full-stack-feature
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/meta/full-stack-feature .claude/skills/full-stack-feature
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/meta/full-stack-feature ~/.claude/skills/full-stack-feature
```

## Related Skills

- `persona-docs` — Stage 1: Persona research
- `feature-specification` — Stage 2: Feature spec
- `api-design-principles` — Stage 4: API design
- `testing-workflow` — Stage 7: Testing
- `e2e-testing-patterns` — Stage 7: End-to-end testing
- `database-migration-patterns` — Stage 6: Backend implementation

---

Part of the [Meta](..) skill category.
