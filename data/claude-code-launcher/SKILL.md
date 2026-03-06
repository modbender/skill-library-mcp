---
name: claude-code-launcher
description: Launch Claude Code in a new terminal window with Remote Control enabled. Use when opening a project for interactive coding sessions where you need to access and control Claude from multiple devices. Handles terminal automation, project navigation, Claude Code startup, Remote Control activation, user prompts, and screenshot capture. Supports error recovery and logs all operations.
---

# Claude Code Launcher

## Overview

This skill automates the process of launching Claude Code in a new terminal window with Remote Control enabled. It streamlines the workflow of:

1. Opening a fresh terminal window
2. Navigating to a project directory
3. Starting Claude Code
4. Activating Remote Control mode
5. Handling user confirmations (if needed)
6. Capturing and displaying the final state

Perfect for switching between projects quickly or sharing Claude Code sessions across devices.

## Usage

### Basic Launch
```bash
claude-code-launcher /path/to/project
```

### With Options
```bash
claude-code-launcher /path/to/project --verbose --screenshot
```

### From OpenClaw Chat
Simply ask:
- "Launch Claude Code in proposal-generator with Remote Control"
- "Open the ai-native-lms project and enable Remote Control"
- "Start Claude Code in ~/dev/edikar-standalone"

## How It Works

### Step 1: Terminal Preparation
- Opens a new Terminal window using macOS automation
- Ensures fresh shell environment (`zsh`)
- Waits for the window to be ready

### Step 2: Project Navigation
- Changes directory to the specified project path
- Validates that the directory exists
- Reports any path resolution errors

### Step 3: Claude Code Launch
- Executes `claude code` command
- Waits for Claude Code interface to fully load (~5 seconds)
- Monitors for startup errors (missing dependencies, permission issues)

### Step 4: Remote Control Activation
- Types `/remote-control` command into Claude Code
- Presses Enter to submit
- Waits for Remote Control UI to appear (~3-6 seconds)

### Step 5: User Confirmation
- Detects the "Continue" option in Remote Control menu
- Presses Enter to confirm (or prompts user if needed)
- Validates that Remote Control is now active

### Step 6: Session Capture
- Takes a screenshot of the final state
- Displays the Remote Control session URL
- Extracts and displays QR code information
- Reports success or any errors encountered

## Error Handling

The skill handles these common scenarios:

| Issue | Recovery |
|-------|----------|
| Terminal fails to open | Retries once, then reports error |
| Project path doesn't exist | Displays helpful path resolution suggestions |
| Claude Code not installed | Reports missing dependency and suggests `brew install claude` |
| Claude Code hangs | Timeout after 15 seconds, allows manual intervention |
| Remote Control fails to activate | Logs error details, suggests checking Claude version |
| Terminal permissions denied | Requests user to enable Screen Recording in System Preferences |
| Network connectivity issue | Waits up to 10 seconds for reconnection |

## Resources

### scripts/launch_claude_code.sh
Main automation script using Peekaboo CLI for:
- Terminal window management
- Keyboard/text input automation
- Screenshot capture
- Error detection and recovery
- Logging all operations to `~/.openclaw/workspace/logs/claude-code-launcher.log`

### references/troubleshooting.md
Common issues and solutions:
- Permission setup (Screen Recording, Accessibility)
- Claude Code installation and updates
- Terminal app configuration
- Network troubleshooting

## Prerequisites

✅ **Installed:** `peekaboo` (for UI automation)  
✅ **Installed:** `claude` CLI (Claude Code)  
✅ **System:** macOS with Terminal.app  
✅ **Permissions:** Screen Recording + Accessibility enabled  

To enable permissions:
```
System Settings → Privacy & Security → Screen Recording → Enable OpenClaw
System Settings → Privacy & Security → Accessibility → Enable OpenClaw
```

## What You Get

After launching, you'll have:
- ✅ New Terminal window with Claude Code running
- ✅ Remote Control session active and shareable
- ✅ Session URL for accessing from other devices
- ✅ QR code for mobile devices (scan in Claude app)
- ✅ Full context of your project available to Claude
- ✅ Capability to pause/resume across devices

## Example Workflow

```
User: "Launch Claude Code in edikar-standalone with Remote Control"
↓
Skill opens new Terminal
↓
cd ~/dev/edikar-standalone
↓
claude code
↓
/remote-control
↓
[Confirms continuation]
↓
Screenshot captured
↓
User sees:
   - Session URL: https://claude.ai/code/session_...
   - QR code displayed
   - Ready to access from phone/tablet
```

## Related Commands

- `/remote-control` - Activate Remote Control in Claude Code
- `claude code` - Start Claude Code interactive session
- `peekaboo` - macOS UI automation (used internally)

---

**Need help?** See `references/troubleshooting.md` for common issues and solutions.
