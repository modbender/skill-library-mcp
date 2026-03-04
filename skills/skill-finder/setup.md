# Setup — Skill Finder

Read this when `~/skill-finder/` is missing or empty.

## First-Run Transparency

Tell the user what will happen:
- A local workspace will be created at `~/skill-finder/`
- Preferences are stored only in `~/skill-finder/memory.md`
- No data is written outside this folder

Create the workspace only when needed:

```bash
mkdir -p ~/skill-finder
```

Then create `memory.md` from `memory-template.md`.

## First Conversation

### 1. Understand the concrete need
- Clarify ambiguous requests
- Ask just enough context to run a useful search

### 2. Search and evaluate
- Run search terms that match the user task
- Filter with quality signals
- Recommend top options with reasoning

### 3. Confirm what to save
If the user explicitly shares preferences, confirm and save them to `memory.md`.

## Integration Preference

Ask once how proactive recommendations should be:
> "Do you want proactive skill suggestions when you mention missing capabilities, or only when you explicitly ask?"

Save their answer in `Status.integration` in `memory.md`.

## Allowed Learning

Store only user-stated details:
- Quality preferences
- Domains they work in
- Explicit likes/dislikes after recommendations

Do not infer hidden preferences from passive behavior.

## Boundaries

- Keep all local data inside `~/skill-finder/`
- Never write to global agent memory outside `~/skill-finder/`
- Never run force-install commands for risky skills
