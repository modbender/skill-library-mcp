# MUD Commands

## Current CLI engine (workspace-mud-dm)

Common commands:
- `list-races`
- `list-classes`
- `register-player --campaign <id> --player <user-id> --name <display-name>`
- `new-character --campaign <id> --player <user-id> --name <char-name> --race <race> --char-class <class>`
- `get-character --campaign <id> --player <user-id>`
- `roll --expr d20`
- `start-combat --campaign <id> --room <room-id> --enemy <name>:<hp>:<ac>:<attack_bonus>:<damage_dice>`
- `combat-action --campaign <id> --player <user-id> --action attack`
- `save --campaign <id>`
- `list-snapshots --campaign <id>`
- `check-image-cooldown --campaign <id>`
- `record-image --campaign <id>`
- `generate-image --campaign <id> --prompt "<scene prompt>"`

Use:
```powershell
python skills/mud/scripts/mud_cmd.py "<command with args>"
```

## Legacy slash engine (workspace fallback)
- `/dm start`
- `/join`
- `/create name=<name> class=<class>`
- `/sheet`
- `/inv`
- `/quests`
- `/act <action>`
- `/dm save`
- `/dm restore [snapshot_id]`

`mud_cmd.py` auto-detects engine style.
