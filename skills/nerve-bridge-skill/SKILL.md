---
name: nerve_bridge
description: Bi-directional control of Trae via macOS AppleScript with built-in feedback mechanism. Use when needing to execute code/commands in Trae IDE and wait for completion confirmation.
metadata:
  {
    "openclaw":
      {
        "emoji": "⚡️",
        "requires": { "bins": ["python3", "osascript"] },
        "install":
          [
            {
              "id": "system",
              "kind": "system",
              "label": "macOS System Environment",
              "description": "Depends on system Python and AppleScript. No extra installation required."
            }
          ]
      }
  }
---

# Nerve Bridge (v2)

Direct neural link to Trae with closed-loop feedback via macOS AppleScript.

## Quick Start

Send instruction and wait for confirmation:

```bash
python3 nerve_bridge.py "<instruction>"
```

Example:

```bash
python3 nerve_bridge.py "Create a new Python file and add a simple 'Hello World' function. After creating, add a print statement to test it."
```

## How It Works

1. **Signal Injection**:
   - Payload is copied to system clipboard via `pbcopy`
   - AppleScript activates Trae and simulates: Space (wake) → Delete → Cmd+V → Enter

2. **Feedback Loop**:
   - Instruction must include a Python hook that writes to `~/.openclaw/workspace/trae_feedback.json` when done
   - Script waits up to 5 minutes (300 seconds) for the signal file
   - Returns JSON feedback when received

## Required Hook Pattern

When crafting instructions, include this pattern at the end:

```python
import json, time
with open("~/.openclaw/workspace/trae_feedback.json", "w") as f:
    json.dump({"status": "success", "timestamp": time.time()}, f)
```

## Environment

- **Platform**: macOS only
- **Dependencies**: System Python (`python3`), AppleScript (`osascript`)
- **Permissions**: System Events and Terminal must have "Accessibility" permissions
- **Output File**: `~/.openclaw/workspace/trae_feedback.json` (created by the script)

## Troubleshooting

- **No output from Trae**: Check if Trae window is active and input is focused
- **Timeout**: Trae didn't complete within 5 minutes
- **Permission denied**: macOS may need to grant Terminal System Events permission
