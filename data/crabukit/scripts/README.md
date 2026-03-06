# 🔒 Claw Safe Install Scripts

## claw-safe-install.sh

A bash wrapper that makes installing OpenClaw skills safer by combining Clawdex database checks with Crabukit behavior analysis.

### Installation

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
source /path/to/claw-safe-install.sh
```

Or copy directly:
```bash
cp scripts/claw-safe-install.sh ~/.claw-safe-install.sh
echo "source ~/.claw-safe-install.sh" >> ~/.zshrc
```

### Usage

```bash
# Install a skill safely
claw-safe-install youtube-summarize

# Or use the short alias
csi youtube-summarize

# Change security threshold (default: high)
claw-safe-install some-skill critical
```

### How It Works

1. **Downloads skill** to temporary location
2. **Layer 1**: Checks Clawdex database (if installed) for known malicious skills
3. **Layer 2**: Runs Crabukit behavior analysis for zero-day detection
4. **Installs only if safe**, otherwise blocks with warning

### Compatibility

- ✅ Works **with or without Clawdex** installed
- ✅ If Clawdex is installed → Both database + behavior checks
- ✅ If Clawdex not installed → Behavior analysis only
- ✅ Auto-installs crabukit if not found in PATH

### Requirements

- clawdhub CLI (for skill installation)
- crabukit (auto-installed if missing)
- curl (for Clawdex API calls, if Clawdex is installed)
