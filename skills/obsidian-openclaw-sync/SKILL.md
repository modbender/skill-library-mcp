---
name: obsidian-openclaw-sync
description: Sync Obsidian OpenClaw config across multiple iCloud devices. Manages symlinks for seamless multi-device sync.
compatibility: darwin
metadata:
  version: 1.0.1
---

# Obsidian OpenClaw Sync

Helper tool for syncing OpenClaw configuration between iCloud Drive and local Obsidian vaults.

## Purpose

This skill solves the problem of **syncing OpenClaw configuration across multiple devices via iCloud**:
- Automatically detects all iCloud vaults with OpenClaw configs
- Creates symlinks from local to iCloud for seamless sync
- Supports multi-agent workspace templates (workspace_*, workspace-*)
- Manages `openclaw.json` sync with overwrite control

## Dependencies

| Dependency | Required | Description |
|------------|----------|-------------|
| `python3` | Yes | Python 3.x (macOS comes with Python pre-installed) |
| `macOS` | Yes | This skill only works on macOS (iCloud Drive integration) |
| `obsidian-icloud-sync` | Yes | Obsidian must be set up to sync vaults via iCloud Drive |

### Check Dependencies

```bash
# Check Python availability
python3 --version

# Check iCloud Obsidian path exists
ls -ld ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents
```

## Usage

```bash
/obsidian-openclaw-sync [command] [options]
```

## Commands

| Command | Description |
|---------|-------------|
| `status` | Show all iCloud vaults with agents and skills, indicates sync status |
| `setup` | Interactive setup to sync a vault to local |
| `unset` | List and remove local symlinks |

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--vault N` | `-v N` | Pre-select vault by index (default: interactive) |
| `--overwrite` | `-w` | Overwrite local `openclaw.json` with symlink to iCloud version |
| `--no-confirm` | `-y` | Skip confirmation prompt (auto-confirm) |

## Examples

```bash
# Check sync status (shows all iCloud vaults)
/obsidian-openclaw-sync

# Interactive setup (select vault, create symlinks)
/obsidian-openclaw-sync setup

# Setup with overwrite (replace local openclaw.json with iCloud symlink)
/obsidian-openclaw-sync setup --overwrite

# Setup without confirmation prompt (auto-confirm)
/obsidian-openclaw-sync setup --no-confirm

# Setup specific vault without prompts
/obsidian-openclaw-sync setup --vault 1 --no-confirm

# List and remove local symlinks
/obsidian-openclaw-sync unset
```

## Output Format

```
✓ iCloud Obsidian: /Users/.../iCloud~md~obsidian/Documents

✓ Valid Vaults (N):
  ✓ <vault-name>
      Agents (N): <agent1>, <agent2>, ...
      Skills (N): <skill1>, <skill2>, ...
  ○ <vault-name> [openclaw.json not found (recommended)]

✗ Invalid Vaults (N):
  ✗ <vault-name> (missing: .obsidian/)

Local Config: .openclaw
  Agents (N): <agent1>, <agent2>, ...
  Skills (N): <skill1>, <skill2>, ...
```

## Synced Directories

| Source (iCloud) | Target (Local) |
|-----------------|----------------|
| `media/` | `./media/` |
| `projects/` | `./projects/` |
| `team/` | `./team/` |
| `skills/` | `./skills/` |
| `workspace-*/` | `./workspace-*/` |
| `.openclaw/*.json` | `./.openclaw/*.json` |
| `openclaw.json` | `./openclaw.json` (with --overwrite) |

## Multi-Device Sync Flow

1. **Device 1**: Run `setup` to create symlinks to iCloud vault
2. **Device 2**: Run `setup --overwrite` to replace local config with iCloud symlink
3. **All devices**: Changes sync via iCloud Drive automatically

## References

- [Sync Helper Script](scripts/sync_helper.py) - Core Python script for vault detection
