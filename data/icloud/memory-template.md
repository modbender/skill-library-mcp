# Memory Template - iCloud

Create `~/icloud/memory.md` with this structure:

```markdown
# iCloud Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | complete | paused | never_ask

## Account Scope
- Apple account alias approved for operations (never include secrets).
- Allowed operation areas: findmy | drive | photos.

## Safety Mode
- Confirmation level: strict | standard.
- Session behavior: persistent | session_only.

## Verified Assets
- Stable device IDs and labels.
- Verified iCloud Drive roots and paths.

## Last Good Workflows
- Last successful auth/session refresh pattern.
- Last successful read and write verification pattern.

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Context still being established | Keep validating scope and constraints |
| `complete` | Stable setup and patterns verified | Execute faster with existing safeguards |
| `paused` | User paused memory updates | Read-only memory usage |
| `never_ask` | User does not want setup prompts | Never ask for persistence again |

## Key Principles

- Never store passwords, 2FA codes, tokens, or recovery keys.
- Keep only operational context needed for reliable execution.
- Update `last` on each confirmed memory write.
