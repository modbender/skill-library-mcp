---
name: control4-home
description: Control a Control4 smart home via pyControl4 (lights, relays, room media) using local Python wrappers. Use when the user asks to control devices, set levels, toggle relays, switch room media sources, or inspect Control4 device mappings.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "pycontrol4",
              "kind": "python",
              "packages": ["pyControl4==1.6.0"],
              "venv": ".venv-control4",
              "label": "Install pyControl4 in local virtualenv"
            }
          ]
      }
  }
---

# Control4 Home

Use the scripts in `scripts/` to control Control4 locally.

## Files

- `scripts/control4_cli.py` — low-level Control4 commands (discover/list/light/relay/room/media + generic method calls)
- `scripts/nl_control4.py` — natural language command wrapper (lights, relays, room media, mute/unmute, volume)
- `scripts/device_map.example.json` — alias template for mapping names to Control4 IDs

## Setup

1. Create a Python venv (example):
   - `python3 -m venv .venv-control4`
2. Install dependency:
   - `.venv-control4/bin/pip install pyControl4`
3. Create `scripts/.env` (or export env vars) with:
   - `CONTROL4_USERNAME`
   - `CONTROL4_PASSWORD`
   - `CONTROL4_CONTROLLER_IP`
   - `CONTROL4_CONTROLLER_NAME` (optional if only one)
4. Copy and customize alias map:
   - `cp scripts/device_map.example.json scripts/device_map.json`

## Common commands

- Discover controller/account:
  - `.venv-control4/bin/python scripts/control4_cli.py discover`
- List items:
  - `.venv-control4/bin/python scripts/control4_cli.py list-items --compact`
- Set light:
  - `.venv-control4/bin/python scripts/control4_cli.py light-set --id 229 --level 40`
- Toggle relay:
  - `.venv-control4/bin/python scripts/control4_cli.py relay-toggle --id 571`
- Natural language:
  - `.venv-control4/bin/python scripts/nl_control4.py "turn kitchen lights off"`
  - `.venv-control4/bin/python scripts/nl_control4.py "watch apple tv in master bedroom"`
  - `.venv-control4/bin/python scripts/nl_control4.py "mute master bedroom"`
- List all exposed methods for an entity:
  - `.venv-control4/bin/python scripts/control4_cli.py methods --entity room --id 45`
- Call any exposed pyControl4 method:
  - `.venv-control4/bin/python scripts/control4_cli.py call --entity climate --id 752 --method getCurrentTemperatureC`
  - `.venv-control4/bin/python scripts/control4_cli.py call --entity light --id 229 --method rampToLevel --args-json "[25,1000]"`
  - Sensitive methods require explicit override:
    - `.venv-control4/bin/python scripts/control4_cli.py call --entity security-panel --id <id> --method setArm --allow-sensitive`

## Safety

- Treat gate/door/alarm relays as sensitive actions.
- Confirm before running high-risk commands if user intent is ambiguous.
- Do not commit secrets (passwords/tokens) into git.
