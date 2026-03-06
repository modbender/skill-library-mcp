---
id: idfm-journey-skill
name: IDFM Journey
description: Query Île-de-France Mobilités (IDFM) PRIM/Navitia for Paris + suburbs public transport (Île-de-France) — place resolution, journey planning, and disruptions/incident checks.
env: ['IDFM_PRIM_API_KEY']
license: MIT
metadata:
  author: anthonymq
  category: "Transport"
  tags: ["idfm", "navitia", "paris", "transport"]
---

# IDFM Journey (PRIM/Navitia)

Use the bundled script to call PRIM/Navitia endpoints without extra dependencies.

## Prereqs / security

- **Required secret:** `IDFM_PRIM_API_KEY` (treat as a secret; don’t commit it).
- **Scope it:** set it only in the shell/session that runs the command.
- **Do not override `--base-url`** unless you fully trust the endpoint.
  The script sends `apikey: <IDFM_PRIM_API_KEY>` to whatever base URL you provide, so a malicious URL would exfiltrate your key.

## Quick commands

Run from anywhere (path is inside the skill folder):

- Resolve places (best match + list):
  - `python3 scripts/idfm.py places "Ivry-sur-Seine" --count 5`

- Journeys (free-text from/to; resolves place ids first):
  - `python3 scripts/idfm.py journeys --from "Ivry-sur-Seine" --to "Boulainvilliers" --count 3`

- Incidents / disruptions (by line id or filter):
  - `python3 scripts/idfm.py incidents --line-id line:IDFM:C01727`
  - `python3 scripts/idfm.py incidents --filter 'disruption.status=active'`

Add `--json` to print raw API output.

## Notes

- If place resolution is ambiguous, increase `--count` and choose the right `stop_area` id.
- For API details and examples, read: `references/idfm-prim.md`.
