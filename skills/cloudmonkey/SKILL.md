---
name: cloudmonkey
description: Manage Apache CloudStack infrastructure using the cloudmonkey (cmk) CLI — list/start/stop/destroy VMs, manage networks, volumes, snapshots, and run any CloudStack API command.
metadata: {"openclaw": {"requires": {"bins": ["cmk"]}, "emoji": "☁️🐵"}}
---

# CloudMonkey (cmk) Skill

You have access to `cmk`, the Apache CloudStack CLI. Use it to manage CloudStack infrastructure by running shell commands via the exec tool.

## Basic usage
```
cmk <verb> <noun> [parameters]
```

Examples:
- `cmk list virtualmachines` — list all VMs
- `cmk list virtualmachines state=Running` — filter by state
- `cmk start virtualmachine id=<uuid>` — start a VM
- `cmk stop virtualmachine id=<uuid>` — stop a VM
- `cmk destroy virtualmachine id=<uuid>` — destroy a VM
- `cmk list zones` — list availability zones
- `cmk list templates templatefilter=featured` — list templates
- `cmk list volumes` — list storage volumes
- `cmk create snapshot volumeid=<uuid>` — snapshot a volume
- `cmk list networks` — list networks
- `cmk list publicipaddresses` — list public IPs

## Profiles

CloudMonkey supports multiple profiles (e.g. for different CloudStack environments).
- `cmk set profile <name>` — switch profile
- `cmk list profiles` — list configured profiles
- Config is stored in `~/.cmk/config`

## Output format

- `cmk set display json` — switch to JSON output
- `cmk set display table` — switch to table output (default)
- `cmk set display text` — plain text

## Tips

- Always confirm destructive operations (destroy, expunge) with the user before running.
- Use `cmk list apis` to discover all available CloudStack API commands.
- UUIDs are required for most operations — use list commands first to find them.
- Filter results using key=value pairs after the command (e.g. `name=myvm`)
