---
name: mud
description: Operate and maintain the persistent MUD agent for OpenClaw. Use when running MUD engine commands, smoke-testing mud state behavior, validating save/restore, diagnosing MUD data issues, or handling MUD deployment operations.
---

# MUD

**Authors:** agigui and lia

Use this skill to run the local MUD engine safely and deterministically.

## Workflow

1. Locate the engine directory.
   - Prefer `C:\Users\openclaw\.openclaw\workspace-mud-dm\mud-agent`
   - Fallback: `C:\Users\openclaw\.openclaw\workspace\mud-agent`
2. Run a smoke test with `scripts/mud_cmd.py`.
3. Run requested MUD operations.
4. Use `references/ops.md` and `references/commands.md` for runbook details.

## Command runner

```powershell
python skills/mud/scripts/mud_cmd.py "<command>"
```

Examples (current CLI engine):

```powershell
python skills/mud/scripts/mud_cmd.py "list-races"
python skills/mud/scripts/mud_cmd.py "register-player --campaign demo --player u1 --name Hero"
python skills/mud/scripts/mud_cmd.py "new-character --campaign demo --player u1 --name Rook --race human --char-class rogue"
python skills/mud/scripts/mud_cmd.py "save --campaign demo"
python skills/mud/scripts/mud_cmd.py "check-image-cooldown --campaign demo"
python skills/mud/scripts/mud_cmd.py "generate-image --campaign demo --prompt \"A rain-soaked neon tavern\""
```

Legacy slash-command engine is auto-detected and still supported by the same wrapper.

## Notes

- Keep mechanics deterministic in engine code; use LLM for narration.
- Avoid hardcoded secrets/tokens in skill files.
- Image generation is available through engine commands (`check-image-cooldown`, `record-image`, `generate-image`) when the runtime image pipeline is configured.
- Keep this skill focused on operations and execution.
