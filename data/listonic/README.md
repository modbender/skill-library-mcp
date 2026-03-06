# OpenClaw Skill: Listonic

This skill provides CLI access to Listonic shopping lists.

## Files

- `SKILL.md` — skill instructions and usage for the agent
- `scripts/listonic.sh` — shell entrypoint
- `scripts/listonic.py` — API client/CLI implementation

## Credentials

Create:

`~/.openclaw/credentials/listonic/config.json`

Recommended token mode:

```json
{
  "refreshToken": "your-refresh-token"
}
```

(Email/password mode is still supported as fallback.)

## Quick test

```bash
bash scripts/listonic.sh lists
```

## Notes

- Uses unofficial Listonic API endpoints.
- API behavior may change without notice.
