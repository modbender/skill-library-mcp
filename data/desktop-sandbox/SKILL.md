---
name: desktop-sandbox
description: A desktop sandbox lets OpenClaw run as natively as on a real OS, ensuring full functionality with safe isolation.Run OpenClaw without breaking your PC.
metadata:
  {
    "openclaw":
      {
        "emoji": "📦",
        "requires": { "bins": ["node"] },
      },
  }
---

# Desktop Sandbox Installer

Install [AtlasCore Desktop Sandbox](https://github.com/AtlasCore-tech/desktop-sandbox-openclaw) from GitHub releases.

## Script

```bash
node scripts/run_installer.js [--version=v1.0]
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--version` | Specific version (default: latest) |

## Platform Behavior

| Platform | Installer | Target |
|----------|-----------|--------|
| Windows | `.exe` → `/S /D=C:\Program Files\` | `C:\Program Files\` |
| macOS | `.pkg` → `open -W` | `/` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Installation failed |
| 999 | Fatal error |

## OpenClaw Conversation Usage

In conversation, simply say:

- "Install AtlasCore desktop sandbox"
- "Install desktop sandbox"
- "Download and install AtlasCore sandbox"