---
name: mirroir
description: Control a real iPhone through macOS iPhone Mirroring — screenshot, tap, swipe, type, launch apps, record video, OCR, and run multi-step scenarios. Works with any app on screen, no source code or jailbreak required.
homepage: https://mirroir.dev
metadata:
  {
    "openclaw":
      {
        "emoji": "📱",
        "os": ["darwin"],
        "requires": { "bins": ["iphone-mirroir-mcp"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "jfarcand/tap/iphone-mirroir-mcp",
              "bins": ["iphone-mirroir-mcp"],
              "label": "Install mirroir via Homebrew",
            },
            {
              "id": "node",
              "kind": "node",
              "package": "iphone-mirroir-mcp",
              "bins": ["iphone-mirroir-mcp"],
              "label": "Install mirroir (npx)",
            },
          ],
      },
  }
---

# Mirroir — iPhone Control via iPhone Mirroring

Use `mirroir` to control a real iPhone through macOS iPhone Mirroring. Screenshot, tap, swipe, type, launch apps, record video, OCR the screen, and run multi-step automation scenarios — all from the terminal. Works with any app on screen, no source code or jailbreak required.

## When to Use

✅ **USE this skill when:**

- User wants to interact with their iPhone (tap, swipe, type, navigate)
- Sending an iMessage, WhatsApp, or any messaging app message on the iPhone
- Adding calendar events, reminders, or notes on the iPhone
- Testing a mobile app (Expo Go, TestFlight, App Store apps)
- Taking a screenshot of the iPhone screen
- Recording a video of an iPhone interaction
- Reading what's on the iPhone screen (OCR)
- Automating a multi-step iPhone workflow (login flows, app navigation)
- Checking iPhone settings or toggling network modes
- Launching an app on the iPhone
- User says "on my phone", "on my iPhone", "on iOS"

## When NOT to Use

❌ **DON'T use this skill when:**

- User wants to send iMessage from macOS Messages.app → use `imsg` skill
- User wants to manage Apple Reminders on macOS → use `apple-reminders` skill
- User wants to manage Apple Notes on macOS → use `apple-notes` skill
- User wants to automate macOS UI → use `peekaboo` skill
- User wants to control a camera → use `camsnap` skill
- The task can be done entirely on macOS without the iPhone
- iPhone Mirroring is not connected (check with `mirroir status` first)

## Requirements

- macOS 15+ (Sequoia or later)
- iPhone connected via [iPhone Mirroring](https://support.apple.com/en-us/105071)
- Karabiner-Elements (installed automatically by the mirroir installer)
- Screen Recording and Accessibility permissions granted

## Setup

After installing, run the setup to configure the helper daemon and Karabiner:

```bash
# One-line install (recommended)
/bin/bash -c "$(curl -fsSL https://mirroir.dev/get-mirroir.sh)"

# Or via Homebrew
brew tap jfarcand/tap && brew install iphone-mirroir-mcp

# Or via npx
npx -y iphone-mirroir-mcp install
```

Approve the Karabiner DriverKit extension if prompted: **System Settings > General > Login Items & Extensions** — enable all toggles under Karabiner-Elements.

## MCP Server Configuration

Mirroir is an MCP server. Configure it in your OpenClaw MCP settings:

```json
{
  "mirroir": {
    "command": "npx",
    "args": ["-y", "iphone-mirroir-mcp"]
  }
}
```

Or if installed via Homebrew, use the binary path directly:

```json
{
  "mirroir": {
    "command": "iphone-mirroir-mcp"
  }
}
```

## Core Workflow

The typical workflow for any iPhone task:

1. **Check status**: `mirroir status` — verify iPhone Mirroring is connected
2. **See the screen**: `mirroir describe_screen` — OCR the screen to find tap targets
3. **Act**: tap, swipe, type, launch apps based on what's visible
4. **Verify**: take a screenshot or describe the screen again to confirm

## Available Tools (26 total)

### Screen & Vision

- `screenshot` — Capture the iPhone screen as PNG
- `describe_screen` — OCR the screen, returns text elements with exact tap coordinates plus a grid-overlaid screenshot
- `get_orientation` — Report portrait/landscape and window dimensions
- `status` — Connection state, window geometry, device readiness
- `check_health` — Full diagnostic: mirroring, helper, Karabiner, screen capture

### Input

- `tap x y` — Tap at coordinates
- `double_tap x y` — Two rapid taps (zoom, text selection)
- `long_press x y` — Hold tap for context menus (default 500ms)
- `swipe from_x from_y to_x to_y` — Swipe between two points
- `drag from_x from_y to_x to_y` — Slow drag for icons, sliders
- `type_text "text"` — Type text via Karabiner virtual keyboard
- `press_key key [modifiers]` — Send special keys (return, escape, tab, arrows) with optional modifiers (command, shift, option, control)
- `shake` — Trigger shake gesture (Ctrl+Cmd+Z) for undo/dev menus

### Navigation

- `launch_app "AppName"` — Open app via Spotlight search
- `open_url "https://..."` — Open URL in Safari
- `press_home` — Go to home screen
- `press_app_switcher` — Open app switcher
- `spotlight` — Open Spotlight search
- `scroll_to "label"` — Scroll until a text element becomes visible via OCR
- `reset_app "AppName"` — Force-quit app via App Switcher

### Recording & Measurement

- `start_recording` — Start video recording of the mirrored screen
- `stop_recording` — Stop recording and return the .mov file path
- `measure action until [max_seconds]` — Time a screen transition

### Network & Scenarios

- `set_network mode` — Toggle airplane/Wi-Fi/cellular via Settings
- `list_scenarios` — List available YAML automation scenarios
- `get_scenario "name"` — Read a scenario file

## Coordinates

Coordinates are in points relative to the mirroring window's top-left corner. **Always use `describe_screen` first** to get exact tap coordinates via OCR. The grid overlay helps target unlabeled icons (back arrows, gears, stars).

## Examples

### Send an iMessage on iPhone

```
1. launch_app "Messages"
2. describe_screen → find "New Message" button coordinates
3. tap [x] [y] on "New Message"
4. type_text "Alice"
5. describe_screen → find Alice in suggestions
6. tap [x] [y] on Alice
7. tap [x] [y] on the message field
8. type_text "Running 10 min late"
9. press_key return
10. screenshot → confirm sent
```

### Test a login flow

```
1. launch_app "MyApp"
2. describe_screen → find Email field
3. tap [x] [y] on Email
4. type_text "${TEST_EMAIL}"
5. tap [x] [y] on Password
6. type_text "${TEST_PASSWORD}"
7. tap [x] [y] on "Sign In"
8. describe_screen → verify "Welcome" appears
```

### Running late — check Waze ETA and notify the team on Slack

```
1. launch_app "Waze"
2. describe_screen → read ETA to current destination (e.g. "23 min")
3. press_home
4. launch_app "Slack"
5. describe_screen → find target channel
6. tap [x] [y] on "#standup"
7. tap [x] [y] on message field
8. type_text "Heads up — Waze says 23 min out, be there by 9:25"
9. press_key return
10. screenshot → confirm sent
```

### Record a bug reproduction

```
1. start_recording
2. launch_app "Settings"
3. scroll_to "General"
4. tap [x] [y] on "General"
5. scroll_to "About"
6. tap [x] [y] on "About"
7. stop_recording → returns path to .mov file
```

## Scenarios (YAML Automation)

Mirroir supports YAML scenario files for multi-step automation flows. Scenarios describe intents, not coordinates — the AI reads the steps and executes them using the MCP tools above, adapting to what's actually on screen.

```yaml
name: Expo Go Login Flow
app: Expo Go
description: Test the login screen of an Expo Go app with valid credentials

steps:
  - launch: "Expo Go"
  - wait_for: "${APP_SCREEN:-LoginDemo}"
  - tap: "${APP_SCREEN:-LoginDemo}"
  - wait_for: "Email"
  - tap: "Email"
  - type: "${TEST_EMAIL}"
  - tap: "Password"
  - type: "${TEST_PASSWORD}"
  - tap: "Sign In"
  - assert_visible: "Welcome"
  - screenshot: "login_success"
```

The step labels (`launch`, `wait_for`, `tap`, `type`, `assert_visible`, `screenshot`) are semantic intents — the AI interprets each one and calls the appropriate MCP tools (`launch_app`, `describe_screen`, `tap`, `type_text`, `screenshot`, etc.) to carry them out.

Use `list_scenarios` to discover available scenarios and `get_scenario` to load them.

## Tips

- Always call `describe_screen` before tapping — never guess coordinates.
- Use `scroll_to "label"` to find off-screen elements instead of manual swiping.
- After typing, iOS autocorrect may alter text — type carefully or disable autocorrect on the iPhone.
- Use `reset_app` before `launch_app` to ensure a fresh app state.
- For keyboard shortcuts in apps, use `press_key` with modifiers (e.g., `press_key n [command]` for new message in Mail).
- `describe_screen` with `skip_ocr: true` returns only the grid screenshot, letting your vision model identify icons and images OCR can't read.

## Troubleshooting

- **"iPhone Mirroring not found"** → Open iPhone Mirroring.app manually, ensure your iPhone is paired
- **Taps not registering** → Check Karabiner DriverKit extension is approved in System Settings
- **Screenshot permission denied** → Grant Screen Recording permission to your terminal
- **Helper not running** → Run `npx iphone-mirroir-mcp setup` to reinstall the helper daemon
