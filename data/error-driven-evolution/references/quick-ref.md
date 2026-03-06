# Quick Reference — Error-Driven Evolution

## Rule Template

```markdown
### [CATEGORY] Short imperative title

- **When**: specific trigger
- **Do**: correct action (imperative)
- **Don't**: the mistake
- **Why**: one sentence
- **Added**: YYYY-MM-DD
```

## Categories

| Tag | Scope |
|-----|-------|
| `DATA` | Data queries, interpretation |
| `COMMS` | Messaging, tone, channels |
| `SCOPE` | Role boundaries |
| `EXEC` | Task execution, tools |
| `JUDGMENT` | Decisions, assumptions |
| `CONTEXT` | Memory, context window |
| `SAFETY` | Security, privacy |
| `COLLAB` | Multi-agent coordination |

## Pre-Decision Scan

| About to... | Check |
|-------------|-------|
| Present data | `[DATA]` |
| Send message | `[COMMS]` + `[SCOPE]` |
| Make suggestion | `[JUDGMENT]` + `[SCOPE]` |
| Execute task | `[EXEC]` + `[CONTEXT]` |
| New session | All (skim titles) |

## Record Triggers

1. User corrects you → rule
2. User overrides output → rule
3. Same error twice → rule (mandatory)
4. Near miss → rule
