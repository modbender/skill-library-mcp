# ☁️ openclaw-skill-nextcloud

> OpenClaw skill - Nextcloud file management via WebDAV + OCS API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-blue)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-nextcloud--files-green)](https://clawhub.ai/Romain-Grosos/nextcloud-files)

Nextcloud client for OpenClaw agents. Covers file/folder management (WebDAV), tags, favorites, and user info (OCS). Includes interactive setup wizard, connection + permission validation, and a behavior restriction system via `config.json`.

> **Share capability** is not included by default. This keeps the skill's security surface minimal - no public links can be created autonomously. See [Restoring share capability](#restoring-share-capability) if you need it.

## Install

```bash
clawhub install nextcloud-files
```

Or manually:

```bash
git clone https://github.com/rwx-g/openclaw-skill-nextcloud \
  ~/.openclaw/workspace/skills/nextcloud
```

## Setup

```bash
python3 scripts/setup.py       # credentials + permissions + connection test
python3 scripts/init.py        # validate all configured permissions
```

You'll need a Nextcloud **App Password**: Settings → Security → App passwords.

> init.py only runs write/delete tests when both `allow_write=true` and `allow_delete=true`. When `allow_delete=false`, write tests are skipped - no artifacts are created and none can be left on your instance.

## What it can do

| Category | Operations |
|----------|-----------|
| Files | create, read, write, append, rename, move, copy |
| Folders | create, rename, move, copy |
| Search | search by filename (DASL) |
| Tags | list, create, assign, remove (system tags) |
| Favorites | toggle |
| Account | quota, user info, server capabilities |

## Configuration

Credentials → `~/.openclaw/secrets/nextcloud_creds` (chmod 600, never committed)

Required variables (set by `setup.py` or manually):

```
NC_URL=https://your-nextcloud.com
NC_USER=your_username
NC_APP_KEY=your_app_password
```

Behavior → `config.json` in skill directory (not shipped, created by `setup.py`):

```json
{
  "base_path": "/Jarvis",
  "allow_write": false,
  "allow_delete": false,
  "readonly_mode": false
}
```

A `config.example.json` with safe defaults is included as reference. Copy it to `config.json` if you prefer not to run `setup.py`.

> **Safe defaults:** both `allow_write` and `allow_delete` are `false` by default. Enable each explicitly only when needed. The skill operates read-only until you grant write access.

## Requirements

- Python 3.9+
- No external dependencies (stdlib only)
- Network access to Nextcloud instance

## Documentation

- [SKILL.md](SKILL.md) - full skill instructions, CLI reference, templates
- [references/api.md](references/api.md) - WebDAV + OCS endpoint reference
- [references/troubleshooting.md](references/troubleshooting.md) - common errors and fixes

## Restoring share capability

Share functionality (public links, user shares) is intentionally excluded from the default build to minimize the skill's security surface and avoid false positives from security scanners.

If you need it, open a GitHub issue or PR - or add it manually by implementing the following in `scripts/nextcloud.py`:

- `_check_share()` guard method (reads `allow_share` from config)
- `create_share_link()`, `create_user_share()`, `get_shares()`, `update_share()`, `delete_share()` using the OCS endpoint `{base_url}/ocs/v2.php/apps/files_sharing/api/v1/shares`
- `allow_share`, `share_default_permissions`, `share_default_expire_days` keys in `_DEFAULT_CONFIG` and `config.json`

All share methods call `self._check_share()` as first guard and `self._enforce_base(path)` for scope restriction.

> When re-enabling share, set `allow_share=true` in `config.json` and keep `share_default_permissions=1` (read-only) as a safe default.

## License

[MIT](LICENSE)
