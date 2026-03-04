# macOS Permissions for Desktop Guardian

## Accessibility (Required for Full Mode)

Hammerspoon needs Accessibility permission to:
- Enumerate windows and their properties
- Detect dialog buttons via AXUIElement
- Click buttons to dismiss dialogs
- Close windows programmatically

### Granting Accessibility
1. System Settings → Privacy & Security → Accessibility
2. Click the lock to make changes
3. Add Hammerspoon.app (usually in /Applications/)
4. Toggle ON

### Verification
```bash
hs -c "hs.accessibilityState()"
# Returns: true
```

## Chrome DevTools Protocol (Optional)

For tab-level monitoring, Chrome needs `--remote-debugging-port=9222`:

### Method 1: Launch alias
```bash
alias chrome='open -a "Google Chrome" --args --remote-debugging-port=9222'
```

### Method 2: LaunchAgent wrapper
Create `~/Library/LaunchAgents/com.chrome.cdp.plist` to always launch Chrome with the flag.

### Method 3: Terminal launch
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

### Security Note
CDP exposes Chrome's internals on localhost:9222. Only local processes (same user) can connect. This is the same trust boundary as Hammerspoon's Accessibility access.

## No Other Permissions Needed

- **Screen Recording**: NOT required (Hammerspoon uses AX APIs, not screen capture)
- **Full Disk Access**: NOT required
- **Automation (AppleScript)**: NOT required (replaced by Hammerspoon)

## Degraded Mode (No Permissions)

Without Hammerspoon/Accessibility, the Swift fallback uses:
- `CGWindowListCopyWindowInfo` — no permission needed, lists windows
- `NSWorkspace` — no permission needed, lists apps

Limitations: no window titles, no dialog buttons, no auto-actions.
