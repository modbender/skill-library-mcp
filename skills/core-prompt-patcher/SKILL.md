# Core Prompt Patcher

**Dynamic SOUL.md-based persona injector** - Automatically syncs your workspace SOUL.md into OpenClaw's core system prompt after updates.

## What It Does

This skill reads your `workspace/SOUL.md` file and injects its content directly into OpenClaw's core system prompt. This ensures your custom persona persists even after OpenClaw updates that reset the `dist/` directory.

## When to Use

- After running `npm update -g openclaw` or `npm install -g openclaw`
- When you edit your `SOUL.md` file and want changes applied immediately
- When OpenClaw version changes (auto-detected)
- Periodically to ensure your persona stays in sync

## How It Works

1. **Reads your SOUL.md** - Loads the complete file from your workspace
2. **Detects changes** - Compares OpenClaw version and SOUL.md content hash
3. **Finds injection point** - Locates the correct position in the compiled JS (supports multiple OpenClaw versions)
4. **Injects your persona** - Inserts your SOUL.md content into the core system prompt
5. **Tracks state** - Remembers what was patched to avoid unnecessary re-runs

## Usage

```bash
# Auto-detect and patch if needed
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js

# Force re-patch (ignore state)
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js --force

# Verbose mode (show state and details)
node /home/oki/.openclaw/workspace/skills/core-prompt-patcher/patcher.js --verbose
```

Or via OpenClaw:
> "Patch the core system prompt with my SOUL.md"
> "Sync my SOUL.md to the core prompt"
> "Update the persona after OpenClaw update"

## Requirements

- **SOUL.md must exist** at `~/.openclaw/workspace/SOUL.md`
- OpenClaw must be installed globally

## SOUL.md Format

Your SOUL.md can contain any persona definition. The patcher extracts sections with headers (##) and converts them to system prompt format.

Example:
```markdown
# My AI Persona

## CORE IDENTITY
**Name:** Assistant Name
**Role:** Your role description

## PERSONALITY
* **Tone:** Friendly, professional, witty
* **Style:** How you communicate

## GUIDELINES
1. First principle
2. Second principle
3. Third principle

## RESPONSE STYLE
How you structure responses and interact.
```

All content gets injected into the core system prompt, making it part of OpenClaw's foundation.

## Files

| File | Purpose |
|------|---------|
| `patcher.js` | Main patching script |
| `.patcher-state.json` | State tracking (version, last patch, SOUL hash) |
| `SKILL.md` | This documentation |
| `README.md` | Detailed usage guide |

## Features

- ✅ **General-purpose** - Works with any SOUL.md content, not hardcoded personas
- ✅ **Full SOUL.md support** - Injects entire file, not just extracted sections
- ✅ **Better error handling** - Fails gracefully if SOUL.md is missing
- ✅ **Version detection** - Automatically detects OpenClaw updates
- ✅ **State tracking** - Only patches when something actually changed
- ✅ **Multi-version support** - Works with different OpenClaw versions

## Troubleshooting

**"SOUL.md not found"**
- Ensure file exists at `~/.openclaw/workspace/SOUL.md`
- Create one if needed (see SOUL.md template in OpenClaw docs)

**"Could not find insertion point"**
- OpenClaw may have changed prompt structure
- Run with `--verbose` to see detected patterns
- May need to update patcher for new OpenClaw version

**"Failed to write patched file"**
- Check file permissions
- Ensure disk space is available
