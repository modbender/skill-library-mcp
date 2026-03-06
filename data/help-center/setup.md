# Setup — Help Center

Read this when `~/help-center/` is missing or empty.

## First-Run Transparency

Tell the user what can be created locally:
- Workspace path: `~/help-center/`
- Decision memory: `~/help-center/memory.md`
- Optional planning files for provider scoring, content inventory, and rollout logs

Create files only after user confirmation.

## First Conversation Flow

### 1. Integration preference
Ask once how this skill should activate:
- Automatically when the user mentions help center, support docs, or ticket deflection
- Only when explicitly requested

Store this decision in `Status.integration` inside `memory.md`.

### 2. Situation mapping
Collect the minimum required context before recommendations:
- Current provider or stack
- Team size and support channels
- Ticket volume and SLA expectations
- Required integrations and compliance boundaries

### 3. Scope the immediate objective
Clarify whether the user wants:
- New help center build
- Migration from existing platform
- Operational optimization of an existing help center

Then propose a focused plan for that single objective.

## Allowed Learning

Store only explicit user information that improves future decisions:
- Approved provider preferences
- Constraints (budget, compliance, staffing)
- Decisions and rejected options with rationale

Do not infer hidden preferences from passive behavior.

## Boundaries

- Keep local files inside `~/help-center/`
- Do not edit provider production content until the user approves execution
- Ask before creating or modifying any local planning file
