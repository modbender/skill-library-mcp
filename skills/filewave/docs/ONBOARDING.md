# FileWave Skill — Onboarding & Installation

## The Key Point: Onboarding Runs AUTOMATICALLY During Installation

When a user installs the FileWave skill via clayhub, they do **not** need to manually run onboarding. It happens automatically as part of installation.

---

## User Experience Flow

### Scenario: First-Time Installation

```
$ clawhub install filewave

[Installation starting...]

============================================================================
✓ FileWave Skill Installed Successfully
============================================================================

The FileWave UEM API skill lets you query device inventory across
multiple FileWave servers...

Profile name (e.g., 'lab'): 
> lab

Server hostname/URL (e.g., 'filewave.company.com'):
> filewave.company.com

API Token (from FileWave Admin Console):
> (paste token)

Description (optional):
> Lab environment

✓ Profile 'lab' created and set as default
✓ Config saved to: ~/.filewave/config

============================================================================
✓ FileWave Skill is Ready!
============================================================================

Next steps:
  filewave profiles
  filewave query --query-id 1

$ filewave query --query-id 1
[Works immediately - no additional setup needed]
```

---

## Installation Steps

### Via clayhub (Recommended)
```bash
clayhub install filewave
```

**What happens automatically:**
1. FileWave skill is downloaded
2. **Onboarding wizard runs in the same terminal**
3. You're prompted to add your first server (name, URL, token)
4. Config file is created at `~/.filewave/config`
5. Skill is ready to use immediately

Then you can immediately use:
```bash
filewave query --query-id 1
```

### Manual Installation (Advanced)

If installing manually without clayhub:

```bash
# 1. Clone or copy skill to ~/.openclaw/workspace/skills/filewave/
# 2. Run onboarding:
python3 ~/.openclaw/workspace/skills/filewave/lib/onboarding.py

# 3. Test:
filewave profiles
```

---

## What If They Skip or Interrupt?

**User presses Ctrl+C during onboarding:**
```
Setup cancelled by user.

You can configure later with:
  filewave setup
```

**User tries to use skill without config:**
```
$ filewave query --query-id 1

⚠️  No FileWave servers configured yet.

Quick setup:
  filewave setup

Or for guided installation:
  clayhub install filewave (includes automatic onboarding)
```

The skill **checks for config** and guides them to setup if missing.

---

## Behind the Scenes: How It Works

### manifest.json Integration

```json
{
  "installation": {
    "onInstall": "python3 lib/onboarding.py",
    "onUpgrade": "echo 'FileWave skill updated'",
    "postInstallMessage": "Run 'filewave setup' to add more servers"
  }
}
```

**What clayhub does:**
1. Downloads FileWave skill
2. Extracts to `~/.openclaw/workspace/skills/filewave/`
3. Reads `manifest.json`
4. Sees `onInstall` field
5. **Automatically runs:** `python3 lib/onboarding.py` in the same terminal session
6. Waits for completion
7. Reports installation success

### onboarding.py (Post-Install Hook)

Located at: `lib/onboarding.py`

**What it does:**
1. Check if config already exists
2. If missing: run interactive setup wizard
3. Collect server details (name, hostname, token)
4. Create `~/.filewave/config` with secure permissions (chmod 600)
5. Print ready-to-use message
6. Exit

**Code flow:**
```python
def run_onboarding():
    config = FileWaveConfig()
    profiles = config.list_profiles()
    
    if profiles:
        # Already configured - ask if adding another
        response = input("Add another server? (yes/no): ")
        if response != "yes":
            return True
    
    # Run setup wizard
    setup_wizard()
    print_ready_message()
    return True
```

---

## Configuration Management

### Config File Location
```
~/.filewave/config
```

### Format (INI)
```ini
[default]
profile = lab

[lab]
server = filewave.company.com
token = your_api_token_here
description = Lab environment

[production]
server = filewave.company.com
token = production_token_here
description = Production
```

### Permissions
Config file is automatically created with secure permissions:
```
chmod 600 ~/.filewave/config
```

Only your user can read/write. No other users can access your API tokens.

---

## Adding More Servers After Installation

Once installed, add servers anytime with:

```bash
filewave setup
```

This will:
1. Show existing profiles
2. Ask if you want to add another
3. Prompt for new server details
4. Save to config

---

## Using Environment Variables (CI/CD)

For automated/script environments, override config with env vars:

```bash
export FILEWAVE_SERVER="https://filewave.company.com"
export FILEWAVE_TOKEN="your_token_here"
filewave query --query-id 1
```

The CLI will use env vars instead of reading config file.

---

## First-Use Safety

The skill has a safety net for users who run it without config:

```python
# In filewave CLI
if args.command == "query":
    config = FileWaveConfig()
    profile = config.get_profile(args.profile)
    
    if not profile:
        print("⚠️  No FileWave servers configured yet.")
        print("\nQuick setup:")
        print("  filewave setup")
        sys.exit(1)
```

This prevents silent failures and guides users to setup.

---

## Success Criteria

After onboarding, user should be able to:

- ✅ See configured servers: `filewave profiles`
- ✅ Query device inventory: `filewave query --query-id 1`
- ✅ Add more servers: `filewave setup`
- ✅ See all commands: `filewave --help`
- ✅ View documentation: `README.md`, `BULK_UPDATE.md`, etc.

---

## Troubleshooting

### "No profiles configured"
**Solution:** Run `filewave setup` or reinstall with onboarding

### "Failed to authenticate"
**Causes:**
- Token is expired or invalid
- Server hostname is incorrect
- Network connectivity issue

**Solution:**
- Get fresh token from FileWave Admin Console
- Verify server hostname
- Check network access

### "Permission denied on config"
**Solution:** Manually fix permissions
```bash
chmod 600 ~/.filewave/config
```

### "Want to reinstall without onboarding?"
```bash
# Remove config (starts fresh)
rm ~/.filewave/config

# Reinstall
clayhub install filewave
```

---

## For Developers: Extending the Skill

The onboarding flow is designed to be:
- **Extensible** — Add fields via `setup_wizard()` in `config_manager.py`
- **Reusable** — Users can run onboarding anytime with `filewave setup`
- **Safe** — Validates input before saving config
- **Clear** — Helpful prompts and error messages

To customize onboarding, edit:
- `lib/config_manager.py` — `setup_wizard()` function
- `lib/onboarding.py` — Post-install hook

---

## Next Steps

1. **After installation:** `filewave profiles` (verify config)
2. **First query:** `filewave query --query-id 1`
3. **Add servers:** `filewave setup`
4. **Full reference:** `filewave --help` or `CLI_REFERENCE.md`
5. **Bulk updates:** `BULK_UPDATE.md`
