# Multi-Device Sync via GitHub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Synchronize OpenClaw workspace data across multiple machines using a private GitHub repository.

## Features

- 🔄 **Automatic push** - File changes trigger immediate git commit + push
- ⏱️ **Periodic pull** - Configurable interval (default: 5 minutes)
- ⚠️ **Conflict detection** - Manual resolution required on conflicts
- 🖥️ **Multi-device support** - Each device uses distinct file prefixes
- 🌐 **Cross-platform** - Works on Linux (inotifywait) and macOS (fswatch)
- 📁 **Selective sync** - Choose which files to synchronize
- 💬 **Interactive setup** - Guided installation with customization options
- 🔒 **Safety first** - Built-in protections against data loss

## Installation

### Recommended: Git Clone (Secure)

```bash
# 1. Clone the repository
git clone https://github.com/RegulusZ/multi-device-sync-github.git
cd multi-device-sync-github

# 2. Run the installer locally
./install.sh
```

This method is **safer** than `curl | bash` because:
- You can review the code before running
- The script runs locally, not from a remote source
- You can verify the repository integrity

### Quick Install (Convenience)

For trusted environments, one-line install:

```bash
curl -fsSL https://raw.githubusercontent.com/RegulusZ/multi-device-sync-github/main/install.sh | bash
```

> ⚠️ **Security Note**: This method executes remote code. Only use if you trust the source.

## Requirements

- Git
- **Linux**: `inotify-tools`
- **macOS**: `fswatch`

## Documentation

- [SKILL.md](./SKILL.md) - Full documentation
- [troubleshooting.md](./references/troubleshooting.md) - Common issues and solutions

## Safety Features

- **Backup before replace**: Existing files are backed up before creating symlinks
- **Confirmation prompts**: Destructive operations require user confirmation
- **Selective git operations**: Only configured files are committed and pushed
- **Local-only notifications**: No data sent to external services

## License

MIT License - See [LICENSE.txt](./LICENSE.txt) for details.
