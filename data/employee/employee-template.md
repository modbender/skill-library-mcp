# Employee Template

Copy this structure to initialize the employee system.

## Initial Setup

```bash
mkdir -p ~/employee/employees ~/employee/shared
echo '{"employees":{}}' > ~/employee/registry.json
touch ~/employee/shared/protocols.md
```

## Registry Template

For `~/employee/registry.json`:

```json
{
  "employees": {},
  "lastUpdated": null
}
```

After hiring employees:

```json
{
  "employees": {
    "luna": {"role": "Research Assistant", "status": "active"},
    "max": {"role": "Code Reviewer", "status": "active"}
  },
  "lastUpdated": "2026-02-15T21:00:00Z"
}
```

## Employee Config Template

For `~/employee/employees/{name}/employee.json`:

```json
{
  "id": "luna",
  "name": "Luna",
  "role": "Research Assistant",
  "status": "active",
  "created": "2026-02-15T10:00:00Z",
  "skill": {
    "type": "linked",
    "path": "~/clawd/skills/researcher/",
    "model": "anthropic/claude-sonnet-4-20250514"
  },
  "personality": {
    "tone": "professional, concise",
    "style": "bullet points, asks clarifying questions"
  },
  "permissions": {
    "canSpawn": false,
    "canMessage": false,
    "fileAccess": ["~/Documents/research/"],
    "autonomyLevel": "draft-only"
  },
  "escalation": [
    "legal mentions → human",
    "budget >$100 → human",
    "uncertainty >medium → ask"
  ],
  "stats": {
    "tasksCompleted": 0,
    "lastActive": null,
    "totalTokens": 0
  }
}
```

## Skill Linking Modes

| Mode | Use Case | Config |
|------|----------|--------|
| linked | Uses existing skill | `"type": "linked", "path": "~/path/to/skill/"` |
| embedded | Skill inside employee folder | `"type": "embedded"` (uses `./skill/SKILL.md`) |
| clawhub | Published skill | `"type": "clawhub", "slug": "author/skill-name"` |

## Memory Template

For `~/employee/employees/{name}/memory/context.md`:

```markdown
# {Name} - Context Memory

## Confirmed Knowledge
<!-- Facts and preferences confirmed by user -->

## Project Context
<!-- Current project state and history -->

## Communication Style
<!-- How this employee should communicate -->
```

## Log Template

For `~/employee/employees/{name}/logs/YYYY-MM-DD.md`:

```markdown
# {Name} - YYYY-MM-DD

## Tasks Completed
- [HH:MM] Task description → outcome

## Escalations
- [HH:MM] Why escalated → resolution

## Learnings
- Added to memory: X

## Stats
- Tokens used: N
- Tasks: N completed, N escalated
```
