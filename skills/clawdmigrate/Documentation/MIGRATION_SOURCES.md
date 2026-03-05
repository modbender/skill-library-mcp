# Migration Sources (moltbot / clawdbot) – Feature Tracking

## Overview

**clawd_migrate** supports upgrading from **moltbot** or **clawdbot** to **openclaw**. The tool is generalized for any user's system: no machine-specific paths, no user-specific references. Safe to publish and use anywhere.

## Status

- **Added:** 2025-02-01
- **Source systems:** moltbot, clawdbot (discovery and migration for both)

## What Was Generalized

| Before | After |
|--------|--------|
| Clawdbot-only discovery | Unified discovery for moltbot + clawdbot |
| `discover_clawdbot_assets` | `discover_source_assets` (canonical); `discover_clawdbot_assets` kept as alias |
| Backup prefix `clawdbot_backup_` | `openclaw_migrate_backup_` (generic) |
| User-specific comments (e.g. PipelineGPT) | Generic descriptions only |
| Config: CLAWDBOT_* only | Config: SOURCE_* (union of moltbot + clawdbot paths) |

## Source Layouts Supported

- **Memory/identity:** SOUL.md, USER.md, TOOLS.md, IDENTITY.md, AGENTS.md, MEMORY.md (either system).
- **Config (clawdbot):** `.config/moltbook/`, `.config/moltbook/credentials.json`.
- **Config (moltbot):** `.config/moltbot/`, `.config/moltbot/credentials.json`; moltbook paths also checked.
- **Extra:** `projects/` (both systems).
- **Clawdbook/Moltbook:** Credentials and API keys from moltbook/moltbot paths are kept separate under `.config/clawdbook` in openclaw.

## Files Touched

- `config.py` – SOURCE_* names, moltbot paths, generic backup prefix, no machine-specific paths.
- `discover.py` – `discover_source_assets()`, uses SOURCE_*; `discover_clawdbot_assets` alias.
- `migrate.py` – Uses `discover_source_assets`; `is_clawdbook` includes moltbot paths.
- `backup.py` – Uses `discover_source_assets`.
- `__init__.py` – Exports `discover_source_assets` and `discover_clawdbot_assets`.
- `__main__.py` – Help/description text: "moltbot or clawdbot"; "Source root".
- `tui.py` – Banner and discover copy: "moltbot or clawdbot", "any user's system".

## Backward Compatibility

- `discover_clawdbot_assets(root)` still works; it calls `discover_source_assets(root)`.
- Existing CLI flags and behavior unchanged; only copy and discovery scope updated.

## Notes

- Adding a new source system (e.g. another bot) only requires extending `SOURCE_*` in `config.py` and any path logic in `discover.py` / `migrate.py`.
- No absolute paths or user names; all paths are relative to the chosen root (default: cwd).
