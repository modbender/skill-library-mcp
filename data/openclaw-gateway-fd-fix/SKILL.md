---
name: openclaw-gateway-fd-fix
description: >
  Fix OpenClaw Gateway "spawn EBADF" / "RPC probe failed" / "EMFILE too many open files" errors caused by file descriptor exhaustion from too many files in workspace.
  One-click detection and repair for the most common OpenClaw crash issue.
version: 1.0.0
author: thomas-jian-zhang
license: MIT
tags:
  - openclaw
  - gateway
  - troubleshooting
  - fd-exhaustion
  - emfile
  - spawn-ebadf
  - maintenance
---

# OpenClaw Gateway File Descriptor Exhaustion Fix

## Problem
OpenClaw Gateway crashes or hangs with these errors:
- `spawn EBADF` when running exec commands
- `RPC probe failed` / gateway timeout
- Logs show `EMFILE: too many open files, watch`
- Gateway process is running but unresponsive

## Root Cause
The Gateway automatically watches **all files** under `~/.openclaw/workspace/` for changes. If you place virtual environments (`.venv`), `node_modules`, large datasets, or tens of thousands of small files inside workspace, the file watcher will exceed macOS's default file descriptor limit (256), causing the process to hang.

## Usage

### Auto-Fix (Recommended)
Run the one-click repair script:
```bash
bash fix.sh
```
What it does:
1. Detects workspace file count
2. Finds and removes unnecessary dependency directories (`.venv`, `node_modules`) inside workspace
3. Backs up your existing LaunchAgent plist
4. Updates LaunchAgent to set file descriptor limit to 524,288
5. Restarts the Gateway service
6. Verifies service health

### Manual Fix Steps
If you prefer to fix manually:
1. **Remove large directories from workspace**:
   ```bash
   # Never put these inside ~/.openclaw/workspace/:
   rm -rf ~/.openclaw/workspace/*/.venv
   rm -rf ~/.openclaw/workspace/*/node_modules
   # Move datasets/models/venvs to ~/Downloads/ or /tmp/
   ```
2. **Update LaunchAgent resource limits**:
   Edit `~/Library/LaunchAgents/ai.openclaw.gateway.plist` and add inside the root `<dict>`:
   ```xml
   <key>HardResourceLimits</key>
   <dict>
     <key>NumberOfFiles</key>
     <integer>524288</integer>
   </dict>
   <key>SoftResourceLimits</key>
   <dict>
     <key>NumberOfFiles</key>
     <integer>524288</integer>
   </dict>
   ```
3. **Restart Gateway**:
   ```bash
   launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.gateway.plist
   sleep 10 && openclaw gateway status
   ```

## Permanent Rule (NEVER BREAK)
✅ **Do NOT put these inside `~/.openclaw/workspace/`:**
- Python virtual environments (`.venv`, `venv`)
- Node.js `node_modules` directories
- Large datasets (>1000 files)
- AI model weights (.pt, .bin, .pth files)
- Cache directories with thousands of small files

✅ **Put these outside workspace:** `/tmp/`, `~/Downloads/`, or any directory outside `~/.openclaw/workspace/`

## Verification
After fix, run:
```bash
openclaw gateway status
```
You should see `RPC probe: ok` in the output.

## Troubleshooting
If fix fails:
1. Check logs: `tail -50 ~/.openclaw/logs/gateway.err.log`
2. Verify no large directories remain in workspace: `find ~/.openclaw/workspace -type f | wc -l` (should be < 1000)
3. Manually restart Gateway: `openclaw gateway stop && openclaw gateway install`
