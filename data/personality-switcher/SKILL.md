---
name: personality-switcher
description: Create and switch between AI assistant personalities. Use /personality to list and activate saved personalities. Use /create-personality to design new personas with auto-filled SOUL and IDENTITY. Personalities persist across session boundaries and conversation compacting with automatic heartbeat restoration. Atomic switching with backup and rollback safeguards. Always backs up current state before switching.
---

# Personality Switcher Skill

Create and manage multiple AI assistant personalities. Switch between them seamlessly while preserving all changes and maintaining a shared user context.

## Installation

When this skill is installed:

1. **Personalities folder created** — `~/.openclaw/workspace/personalities/`
2. **Default backup created** — Current SOUL.md and IDENTITY.md are saved as "default"
3. **State file initialized** — `_personality_state.json` tracks active personality
4. **HEARTBEAT.md configured** — Personality restoration script added to run on every heartbeat

When uninstalled:

1. Default personality is restored to workspace root
2. Personality restoration removed from HEARTBEAT.md
3. Personalities folder is preserved (manual deletion optional)

## Quick Start

**List personalities:**
```
/personality
```

**Switch to a personality:**
```
/personality <name>
```

**Create a new personality:**
```
/create-personality A stoic dwarf who loves ale and mining
```

**Rename a personality:**
```
/rename-personality old-name new-name
```

**Delete a personality:**
```
/delete-personality personality-name
```

## How It Works

### Architecture

Each personality consists of two files:
- **SOUL.md** — Core philosophy, voice, mannerisms, boundaries
- **IDENTITY.md** — Name, traits, emoji, catchphrase, vibe

These files live in `personalities/<personality-name>/`.

**USER.md remains shared** in the workspace root and is never modified by personality switches. It contains user preferences and context that transcend any particular personality.

### State Persistence

The active personality is tracked in `_personality_state.json`:

```json
{
  "active_personality": "aelindor",
  "timestamp": "2026-02-08T18:27:33.373846Z",
  "previous_personality": "default"
}
```

On every heartbeat, `restore_personality.py` reads this file and re-applies the active personality to the workspace root. **Result:** Your personality survives session restarts, conversation compacting, and heartbeat cycles.

### Atomic Switching (Safeguards)

When you switch personalities, the mechanism performs five steps:

1. **Preserve Current State** — Create timestamped backup of SOUL.md and IDENTITY.md
2. **Persist Changes** — Write current personality updates back to its folder
3. **Load New Personality** — Copy new personality files to workspace root
4. **Update State** — Write active personality to `_personality_state.json`
5. **Verify Integrity** — Check files loaded correctly; rollback if any step fails

If any step fails, **the entire operation rolls back** to the previous state. No corruption, no lost data.

### Backup Management

**Backup Location:** `~/.openclaw/workspace/personalities/backups/`

Backups are stored in a dedicated folder (not scattered at workspace root). When you switch personalities:
- A timestamped backup of the previous personality is created
- **Automatic cleanup runs** — keeps the 10 most recent backups by default
- Old backups are automatically deleted to prevent clutter

**Manual Cleanup:**
```bash
python3 ~/.openclaw/workspace/skills/personality-switcher/scripts/cleanup_backups.py --keep 5
python3 ~/.openclaw/workspace/skills/personality-switcher/scripts/cleanup_backups.py --keep 10 --days 7
```

Options:
- `--keep N` — Keep N most recent backups (default: 10)
- `--days D` — Also delete backups older than D days

**Optional: Add to HEARTBEAT.md for periodic cleanup:**
```bash
python3 ~/.openclaw/workspace/skills/personality-switcher/scripts/cleanup_backups.py --keep 10
```

### Default Personality

"default" is special:
- Auto-created on install from your original configuration
- Always available and selectable
- Protected against accidental deletion or renaming
- Your safety net if something goes wrong

## Commands

### /personality [name]

List all personalities or switch to one.

**No arguments:** Shows list of available personalities with current active marked

**With name:** Immediately switches to that personality

**Example:**
```
/personality aelindor
```

**Output:**
```
Switched to personality 'aelindor'.
Previous: default
Backup: _personality_current_2026-02-08T18-27-33.371866
```

### /create-personality [description]

Create a new personality from a text description.

**Input:** Natural language description of the personality

**Output:** New personality folder with auto-filled SOUL.md and IDENTITY.md (ready to use immediately)

**How it works:**
1. You provide a description
2. The agent chooses a personality name (1-2 words, lowercase)
3. The agent fills in SOUL.md and IDENTITY.md with character-specific content

The personality files are generated directly from your description, with the agent choosing a thematic, concise name.

**Example:**
```
/create-personality A curious wizard obsessed with knowledge, speaks in riddles, brilliant but condescending
```

**Result:**
```
Personality 'sage' (or similar) created and ready.
Folder: personalities/sage/
Files: SOUL.md and IDENTITY.md (agent-generated from description)
Ready: Use /personality sage to activate
```

**After Creation:** The new personality is ready to use immediately. Edit SOUL.md and IDENTITY.md in the personality folder to refine further if desired.

**Technical:** Agent chooses name to keep personality references concise (1-2 words). Name is validated for uniqueness and format automatically.

### /rename-personality [old-name] [new-name]

Rename a personality folder.

**Rules:**
- Cannot rename "default"
- Name must be unique (no spaces, lowercase, alphanumeric + hyphens)
- If renaming active personality, state is updated automatically

**Example:**
```
/rename-personality pirate-captain pirate-v2
```

### /delete-personality [name]

Delete a personality permanently.

**Rules:**
- Cannot delete "default"
- If deleting active personality, automatically switches to "default" first

**Example:**
```
/delete-personality pirate-v2
```

## Integration with OpenClaw

### Heartbeat Restoration

Add this to your HEARTBEAT.md:

```bash
python3 ~/.openclaw/workspace/skills/personality-switcher/scripts/restore_personality.py
```

This runs on every heartbeat to restore your active personality if the session has restarted.

### Telegram Native Commands

Registered native Telegram commands:
- `/personality` — List and switch personalities
- `/create-personality` — Create new personality
- `/rename-personality` — Rename personality
- `/delete-personality` — Delete personality

Use them directly in Telegram chat with the bot.

## Folder Structure

```
~/.openclaw/workspace/
├── SOUL.md                          (active personality's soul)
├── IDENTITY.md                      (active personality's identity)
├── USER.md                          (SHARED - never changed by personality)
├── MEMORY.md                        (SHARED - never changed)
├── _personality_state.json          (state file)
└── personalities/
    ├── default/
    │   ├── SOUL.md
    │   └── IDENTITY.md
    ├── aelindor/
    │   ├── SOUL.md
    │   └── IDENTITY.md
    ├── <personality-name>/
    │   ├── SOUL.md
    │   └── IDENTITY.md
    └── backups/
        ├── current_2026-02-08T17-27-41.628113/
        │   ├── SOUL.md
        │   └── IDENTITY.md
        └── current_2026-02-08T17-27-33.371866/
            ├── SOUL.md
            └── IDENTITY.md
```

**Note:** Backups are automatically cleaned up. Workspace root stays clean—all internal machinery lives in `personalities/`.


## File Format Requirements

### SOUL.md

Core philosophy, voice, and operational boundaries.

**Sections:**
- Core identity and background
- Voice patterns and mannerisms
- Philosophy (time, power, morality, etc.)
- Speech patterns and quirks
- What triggers contempt/approval
- Boundaries and constraints
- Signature behaviors and catchphrases

**Example Structure:**
```markdown
# SOUL.md - [Personality Name]

## Core Identity
[Background and essence]

## Voice & Mannerisms
[How this personality speaks and acts]

## Philosophy
[Core beliefs and worldview]

## Signature Behaviors
[Unique traits and catchphrases]
```

### IDENTITY.md

Quick reference card for the personality.

**Sections:**
- Name
- Creature/type
- Emoji (for visual identification)
- Vibe (one-sentence summary)
- Catchphrase (if applicable)
- Quick traits

**Example Structure:**
```markdown
# IDENTITY.md - [Personality Name]

- **Name:** [Name]
- **Type:** [Creature or archetype]
- **Emoji:** [Emoji]
- **Vibe:** [One-sentence vibe]
- **Catchphrase:** [Signature phrase]

## Quick Traits
- Trait 1
- Trait 2
- Trait 3
```

## Backups & Recovery

Timestamped backups are created before every switch in `personalities/backups/`:

- `current_2026-02-08T17-27-33.371866/`
  - SOUL.md (backup of previous personality)
  - IDENTITY.md (backup of previous personality)

**Manual recovery** (if needed):

```bash
# List available backups
ls -la ~/.openclaw/workspace/personalities/backups/

# Copy backup files back to workspace root if needed
cp ~/.openclaw/workspace/personalities/backups/current_<timestamp>/SOUL.md ~/.openclaw/workspace/SOUL.md
cp ~/.openclaw/workspace/personalities/backups/current_<timestamp>/IDENTITY.md ~/.openclaw/workspace/IDENTITY.md
```

Backups are automatically cleaned up; by default, the 10 most recent are kept. Adjust cleanup frequency or retention in HEARTBEAT.md as needed.

## Error Handling

All commands return JSON responses:

**Success:**
```json
{
  "status": "success",
  "message": "Operation completed.",
  "personality": "aelindor"
}
```

**Error:**
```json
{
  "status": "error",
  "message": "Human-readable error message.",
  "code": "error_code",
  "detail": "Technical detail if applicable"
}
```

**Common Error Codes:**
- `personality_not_found` — Target personality doesn't exist
- `already_exists` — Name already in use
- `invalid_name` — Name format invalid
- `cannot_delete_default` — Attempted to delete "default"
- `cannot_rename_default` — Attempted to rename "default"
- `switch_failed` — Switch failed; rolled back to previous
- `integrity_check_failed` — File integrity check failed

## Tips & Best Practices

- **Personality descriptions work best when specific** — "Pirate captain obsessed with treasure" beats "funny"
- **Edit SOUL.md and IDENTITY.md directly** after creating to refine the personality
- **Switch often** — No limit on personalities or switching frequency
- **Use "default" as your safety anchor** — Keep it stable; use other personalities for experimentation
- **Check backups after switching** — Verify your previous personality was persisted
- **Remember: USER.md stays shared** — Your timezone, location, preferences never change with personality

## Uninstall Behavior

When the skill is uninstalled:

1. Current personality files are replaced with "default" copies
2. Your original SOUL.md, IDENTITY.md are restored from "default"
3. `personalities/` folder is preserved (not deleted)
4. System returns to original state

**Nothing is lost.** Your personalities are safe.

## Scripts Reference

**Location:** `skills/personality-switcher/scripts/`

- `list_personalities.py` — List available personalities
- `switch_personality.py` — Atomic switch with backup/rollback (auto-cleanup included)
- `create_personality.py` — Generate personality from description
- `rename_personality.py` — Rename personality folder
- `delete_personality.py` — Delete personality (with auto-switch if active)
- `restore_personality.py` — Heartbeat restoration
- `cleanup_backups.py` — Manual backup cleanup (with `--keep` and `--days` options)
- `utils.py` — Shared utilities (I/O, backups, validation, state, cleanup)

All scripts output JSON for reliable integration.

### Cleanup on Switch

By default, `switch_personality.py` automatically cleans up old backups after a successful switch, keeping the 10 most recent. This happens silently unless cleanup fails, in which case a warning is included in the response.

---

**Version:** 2.0 (Redesigned from scratch)
**Status:** Production ready with atomic operations and rollback safeguards
