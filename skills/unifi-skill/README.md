# UniFi Site Manager API (OpenClaw Skill)

This repository contains the OpenClaw skill definition in **[`SKILL.md`](./SKILL.md)**.

## ClawHub
- Skill page: https://clawhub.ai/skills/unifi-skill
- Install:
  ```bash
  clawhub install unifi-skill --registry "https://auth.clawdhub.com"
  ```

## Local development
- Set env var `UNIFI_API_KEY` **or** create a local `config.json` from `config.json.example` (this file is **gitignored**).
- Optional: `UNIFI_BASE_URL` (defaults to `https://api.ui.com`).
- Run scripts from the skill folder, e.g.:
  ```bash
  python3 scripts/unifi.py list-sites
  ```
