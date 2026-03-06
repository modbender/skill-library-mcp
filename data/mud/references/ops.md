# MUD Ops Runbook

## Locate deployment
- Primary runtime: `C:\Users\openclaw\.openclaw\workspace-mud-dm\mud-agent`
- Fallback runtime: `C:\Users\openclaw\.openclaw\workspace\mud-agent`

## Smoke test
```powershell
python skills/mud/scripts/mud_cmd.py "list-races"
python skills/mud/scripts/mud_cmd.py "register-player --campaign demo --player u1 --name Hero"
python skills/mud/scripts/mud_cmd.py "new-character --campaign demo --player u1 --name Rook --race human --char-class rogue"
python skills/mud/scripts/mud_cmd.py "get-character --campaign demo --player u1"
```

## Save/restore checks
```powershell
python skills/mud/scripts/mud_cmd.py "save --campaign demo"
python skills/mud/scripts/mud_cmd.py "list-snapshots --campaign demo"
```

## Image generation checks
```powershell
python skills/mud/scripts/mud_cmd.py "check-image-cooldown --campaign demo"
python skills/mud/scripts/mud_cmd.py "generate-image --campaign demo --prompt \"Cinematic party reveal in torchlight\""
```

## Troubleshooting
1. If import/command fails, verify `mud_agent.py` exists in chosen mud directory.
2. If JSON output is empty or malformed, run command directly in mud directory: `python mud_agent.py --help`.
3. If state is suspect, snapshot first (`save`) before manual edits.
4. If group routing fails, validate OpenClaw bindings/channel status.
