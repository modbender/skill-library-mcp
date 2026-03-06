# OpenClaw Setup — MemePickup Wingman

Detailed setup guide for running the MemePickup Wingman skill on OpenClaw.

## Installation

```bash
npx clawhub@latest install memepickup/memepickup-wingman
```

Verify installation:

```bash
openclaw skills list
```

You should see `memepickup-wingman` in the list with status `enabled`.

## Configuration

### API Key via openclaw.json

Add your key to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "memepickup-wingman": {
        "enabled": true,
        "apiKey": "mp_your_api_key_here"
      }
    }
  }
}
```

The `apiKey` field maps to the `MEMEPICKUP_API_KEY` environment variable automatically.

### API Key via Environment Variable

Alternatively, export the key directly:

```bash
export MEMEPICKUP_API_KEY="mp_your_api_key_here"
```

Add this to your shell profile (`~/.zshrc`, `~/.bashrc`) to persist across sessions.

## Skill Management

```bash
# Update to latest version
npx clawhub@latest update memepickup-wingman

# Disable without removing
openclaw skills disable memepickup-wingman

# Re-enable
openclaw skills enable memepickup-wingman

# Uninstall
npx clawhub@latest uninstall memepickup-wingman
```

## Screen Interaction (Auto-Swipe)

OpenClaw performs auto-swipe using native screen interaction on iPhone/Mac:

1. Opens the dating app directly (Hinge, Tinder, Bumble, or Instagram)
2. Takes screenshots of each profile using native screen capture
3. Sends screenshots to the MemePickup API for analysis
4. Executes the recommended action (swipe, like, comment) via native tap/swipe gestures

### Requirements

- OpenClaw must have screen interaction permissions enabled
- The dating app must be installed and logged in on the device
- Works with: Hinge, Tinder, Bumble, Instagram

### Permissions

When auto-swipe is first activated, OpenClaw will request:
- Screen recording permission (for screenshots)
- Accessibility permission (for tap/swipe interaction)

Grant both for auto-swipe to function.

## Script Execution

OpenClaw runs `scripts/api.sh` on-device using the system's Bash shell. The script requires:
- `curl` (pre-installed on macOS)
- Internet access

No additional dependencies or installations needed.

## Troubleshooting

**"MEMEPICKUP_API_KEY not set" error:**
- Check `~/.openclaw/openclaw.json` for the `apiKey` field
- Or verify `echo $MEMEPICKUP_API_KEY` returns your key

**Skill not appearing in list:**
- Re-run the install command
- Check that `~/.openclaw/skills/memepickup-wingman/SKILL.md` exists

**Auto-swipe not interacting with app:**
- Verify screen interaction permissions in System Settings > Privacy
- Make sure the dating app is in the foreground when auto-swipe starts
