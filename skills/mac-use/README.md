# mac-use

An [OpenClaw](https://github.com/openclaw/openclaw) skill that gives your AI agent eyes and hands on macOS. It can see what's on screen, read text via OCR, click buttons, scroll, type, and press keys — enabling your agent to operate any Mac desktop application through its GUI.

## What it does

mac-use bridges AI agents and macOS desktop apps using a **screenshot → OCR → act → verify** loop:

1. **Screenshot** a window — captures it, runs Apple Vision OCR to detect all text, draws numbered annotations on the image
2. **Identify** the target — the agent reads both the annotated image and the element list to decide what to click
3. **Act** — click a numbered element, type text, press keys, or scroll
4. **Verify** — take another screenshot to confirm the result

All coordinates use a normalized 1000x1000 canvas, so the skill works consistently across different screen sizes and resolutions.

## How it works

The core is a single Python script (`scripts/mac_use.py`) that uses:

- **Apple Vision framework** (via pyobjc) for on-device OCR — supports English, Chinese, and other languages. No cloud API needed.
- **Quartz / CoreGraphics** for window enumeration, display scaling, and low-level mouse events
- **PyAutoGUI** for mouse movement and scrolling
- **Pillow** for image processing (crop, resize, annotation drawing)
- **screencapture** (macOS built-in) for screen capture

The script exposes 7 subcommands: `list`, `screenshot`, `clicknum`, `click`, `scroll`, `type`, `key`. Each returns structured JSON so the agent can parse the results programmatically.

### Text detection and annotation

When you run `screenshot`, the script:

1. Captures the full screen via `/usr/sbin/screencapture`
2. Crops to the target window and fits it onto a 1000x1000 canvas
3. Runs Vision OCR to find all text regions
4. Filters out noise (single digits, punctuation, grid artifacts)
5. Numbers the remaining elements top-to-bottom, left-to-right
6. Draws green bounding boxes and blue number badges
7. Returns both the annotated image and a JSON element list

The agent uses `clicknum N` to click element N — the script looks up the saved coordinates and translates them from canvas space to absolute screen coordinates, accounting for display scaling (Retina).

## Requirements

- **macOS** (Sonoma 14+ recommended; requires Apple Vision framework)
- **Python 3.10+** (via Homebrew: `brew install python`)

### macOS permissions

This skill requires two system permissions, granted to the **host process** that runs the script (e.g. Terminal, iTerm, or the OpenClaw gateway process):

| Permission | Why | How to grant |
|---|---|---|
| **Screen Recording** | `screencapture` needs it to capture window contents. Without it, screenshots will be blank or show only the desktop wallpaper. | System Settings > Privacy & Security > Screen Recording > toggle on for Terminal / your host app |
| **Accessibility** | `pyautogui` and `osascript` need it to move the mouse, click, type, and send keystrokes. Without it, all interaction commands will silently fail. | System Settings > Privacy & Security > Accessibility > toggle on for Terminal / your host app |

macOS will prompt you the first time each permission is needed. If you run the script from a **LaunchAgent** (like the OpenClaw gateway), the host process is the Node.js binary — you'll need to add it manually in System Settings since there's no interactive prompt.

> **Privacy note**: All processing is local. Screenshots are saved to `/tmp/` and OCR runs on-device via Apple Vision. No data is sent to any external service.

### Python dependencies

```bash
pip3 install --break-system-packages -r requirements.txt
```

Or in a virtualenv:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Packages: `pyobjc-framework-Vision` (pulls in Quartz + Cocoa), `pyautogui`, `Pillow`

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all visible app windows (JSON) |
| `screenshot <app> [--id N]` | Capture + OCR + annotate a window |
| `clicknum <N>` | Click numbered element from last screenshot |
| `click --app <app> [--id N] <x> <y>` | Click at canvas coordinates (fallback for icons without text) |
| `scroll --app <app> [--id N] <dir> <amount>` | Scroll inside a window |
| `type [--app <app>] "text"` | Type text via clipboard paste (Unicode-safe) |
| `key [--app <app>] <combo>` | Press key combo (e.g. `return`, `cmd+v`, `cmd+shift+s`) |

## Limitations

- **macOS only** — depends on Apple Vision framework, Quartz, and `screencapture`
- **Text-based detection only** — OCR finds text elements, not icons. Icon-only buttons (close, minimize, unlabeled toolbar icons) need coordinate-based clicking as a fallback
- **No password/secret entry** — the `type` command uses the system clipboard; do not type sensitive data
- **Single display** — optimized for the main display; multi-monitor setups may need `--id` targeting
- **Screen Recording + Accessibility permissions required** — first run will trigger macOS permission prompts; the host app (Terminal, OpenClaw gateway) must be granted both
- **Vision OCR accuracy** — works well for standard UI text but may miss very small text, heavily stylized fonts, or text embedded in complex graphics
- **Window must be visible** — the target window is raised automatically, but fully minimized windows need to be un-minimized first
- **Retina scaling** — handled automatically, but unusual DPI configurations may affect coordinate mapping

## File structure

```
mac-use/
  SKILL.md          # OpenClaw skill definition (frontmatter + agent instructions)
  README.md         # This file
  requirements.txt  # Python dependencies
  scripts/
    mac_use.py      # Core automation script
```

## License

MIT
