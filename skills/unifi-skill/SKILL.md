---
name: unifi
description: Monitor UniFi network infrastructure via the UniFi Site Manager API. Use to list hosts/sites/devices/APs and get high-level client/device counts.
metadata:
  openclaw:
    requires:
      env: ["UNIFI_API_KEY"]
      optionalEnv: ["UNIFI_BASE_URL"]
---

# UniFi Site Manager API

## Setup
- **Required:** `UNIFI_API_KEY` (set env var) *or* create `config.json` next to this file (gitignored). Start from `config.json.example`.
- Optional: `UNIFI_BASE_URL` (defaults to `https://api.ui.com`).
- This skill currently uses the **Site Manager API** (infrastructure/aggregates). It does not provide per-client tracking unless extended with the local Network API.

## Commands
- `python3 scripts/unifi.py list-hosts`
- `python3 scripts/unifi.py list-sites`
- `python3 scripts/unifi.py list-devices`
- `python3 scripts/unifi.py list-aps`
- Add `--json` for raw output.
