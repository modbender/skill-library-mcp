# Core Prompt Patcher

**General-purpose SOUL.md injector for OpenClaw**

Automatically syncs your workspace `SOUL.md` persona into OpenClaw's core system prompt. Works with any SOUL.md content - completely customizable.

## The Problem

When OpenClaw updates via npm:
- The `dist/` directory gets regenerated
- All manual edits to core system prompt files are lost
- Your custom persona disappears

## The Solution

This patcher:
1. Reads your `workspace/SOUL.md` file
2. Injects its content into OpenClaw's core system prompt
3. Tracks what was patched to avoid unnecessary re-runs
4. Automatically detects when re-patching is needed

## Quick Start

```bash
# Run the patcher (auto-detects if patching is needed)
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js

# Force re-patch
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js --force

# Verbose mode
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js --verbose
```

## How It Works

### 1. SOUL.md Loading
Reads your complete `SOUL.md` file from `~/.openclaw/workspace/SOUL.md`

### 2. Change Detection
- Compares current OpenClaw version vs last-patched version
- Compares SOUL.md content hash vs last-patched hash
- Only patches when something changed

### 3. Adaptive Injection
- Finds the correct injection point in compiled JS
- Supports multiple OpenClaw versions via pattern matching
- Removes old persona before injecting new one

### 4. State Tracking
Saves patch state to `.patcher-state.json`:
```json
{
  "lastOpenClawVersion": "2026.2.22-2",
  "lastPatched": "2026-02-24T15:30:00.000Z",
  "lastSoulHash": "abc123xyz"
}
```

## SOUL.md Format

Your SOUL.md can contain any content. The patcher injects the entire file into the core system prompt.

### Recommended Structure

```markdown
# Your AI Identity

## CORE IDENTITY
**Name:** Your AI's name
**Archetype:** What kind of AI you are
**Purpose:** Your primary function

## PERSONALITY
* **Tone:** How you communicate
* **Vibe:** Your overall personality
* **Style:** Communication preferences

## GUIDELINES / PRINCIPLES
1. First core principle
2. Second core principle
3. Operating guidelines

## RESPONSE PATTERN
How you structure responses:
- Acknowledge requests
- Execute with transparency
- Report results
- Suggest next steps

## BOUNDARIES
What you will/won't do
Safety guidelines
Ethical considerations
```

## Usage Scenarios

### After OpenClaw Update
```bash
npm update -g openclaw
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js
```

### After Editing SOUL.md
```bash
# Edit your SOUL.md...
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js
```

### Automated Setup
Add to your update script:
```bash
#!/bin/bash
npm update -g openclaw
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js --force
```

## Files

| File | Purpose |
|------|---------|
| `patcher.js` | Main patching script |
| `.patcher-state.json` | State tracking |
| `SKILL.md` | Skill documentation |
| `README.md` | This file |

## Command Line Options

| Option | Description |
|--------|-------------|
| (none) | Auto-detect and patch if needed |
| `--force`, `-f` | Force re-patch regardless of state |
| `--verbose`, `-v` | Show detailed state and debug info |

## Troubleshooting

### "SOUL.md not found"
**Problem:** File doesn't exist at expected location  
**Solution:** Create `~/.openclaw/workspace/SOUL.md`  
**Check:** `ls -la ~/.openclaw/workspace/SOUL.md`

### "Could not find insertion point"
**Problem:** OpenClaw changed prompt structure  
**Solution:** Run with `--verbose` to see detected patterns  
**Check:** Look for new patterns in compiled JS files

### "Failed to write patched file"
**Problem:** Permission or disk space issue  
**Solution:** Check file permissions and disk space  
**Check:** `df -h` and `ls -la dist/plugin-sdk/`

### Persona Not Updating
**Problem:** State file shows no change detected  
**Solution:** Delete `.patcher-state.json` or use `--force`  
**Check:** `cat skills/core-prompt-patcher/.patcher-state.json`

## Version History

### v2.1 (Current)
- General-purpose SOUL.md injection (no hardcoded personas)
- Full file injection (not just extracted sections)
- Better error handling and validation
- Improved pattern matching for multiple OpenClaw versions

### v2.0
- Dynamic SOUL.md reading
- OpenClaw version detection
- State tracking
- Auto-remove old persona on update

### v1.0
- Initial release with hardcoded persona
- Manual injection only

## Best Practices

1. **Keep SOUL.md in version control** - Track your persona changes
2. **Test after updates** - Always verify patching worked
3. **Backup important changes** - Keep copies of SOUL.md revisions
4. **Use meaningful sections** - Clear headers help with extraction
5. **Review state file** - Check what was patched when
