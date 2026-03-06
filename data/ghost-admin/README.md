# 👻 openclaw-skill-ghost

> OpenClaw skill - Ghost CMS content management via Admin API v5

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-ghost--admin-green)](https://clawhub.ai/Romain-Grosos/ghost-admin)

Full Ghost Admin API v5 client for OpenClaw agents. Covers posts, pages, tags, images, members, and newsletters. JWT auth and all HTTP calls via stdlib (urllib) - zero external dependencies. Includes interactive setup wizard, connection + permission validation, and a behavior restriction system via `config.json`.

## Install

```bash
clawhub install ghost-admin
```

Or manually:

```bash
git clone https://github.com/rwx-g/openclaw-skill-ghost \
  ~/.openclaw/workspace/skills/ghost
```

## Setup

```bash

python3 scripts/setup.py       # credentials + permissions + connection test
python3 scripts/init.py        # validate all configured permissions
```

You'll need a Ghost **Admin API Key**: Ghost Admin → Settings → Integrations → Add custom integration.

> init.py only runs write/delete tests when `allow_delete=true`. When `allow_delete=false`, write tests are skipped - no artifacts are created and none can be left on your instance.

## What it can do

| Category | Operations |
|----------|-----------|
| Posts | create, read, update, publish, unpublish, list |
| Pages | create, read, update, publish, unpublish, list |
| Tags | create, read, update, delete, list |
| Images | upload (jpg, png, gif, svg, webp) |
| Members | list, create, update, delete (opt-in) |
| Newsletters | list, read |
| Tiers | list |
| Site | read settings, version |

## Configuration

Credentials → `~/.openclaw/secrets/ghost_creds` (chmod 600, never committed)

Required variables (set by `setup.py` or manually):

```
GHOST_URL=https://your-site.com
GHOST_ADMIN_KEY=key_id:secret_hex
```

Behavior → `config.json` in skill directory (not shipped, created by `setup.py`):

```json
{
  "allow_publish": false,
  "allow_delete": false,
  "allow_member_access": false,
  "default_status": "draft",
  "default_tags": [],
  "readonly_mode": false
}
```

A `config.example.json` with safe defaults is included as reference. Copy it to `config.json` if you prefer not to run `setup.py`.

## Requirements

- Python 3.9+
- Network access to Ghost instance (self-hosted or Ghost Pro)
- No pip installs needed - stdlib only

## Documentation

- [SKILL.md](SKILL.md) - full skill instructions, CLI reference, templates
- [references/api.md](references/api.md) - Ghost Admin API endpoint reference + NQL filters
- [references/troubleshooting.md](references/troubleshooting.md) - common errors and fixes

## License

[MIT](LICENSE)
