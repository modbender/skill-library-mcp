---
name: Desktop Control
description: Control mouse, keyboard, and screen for desktop automation tasks
---

# Desktop Control Skill

This skill provides comprehensive desktop automation capabilities through PyAutoGUI, allowing AI agents to control the mouse, keyboard, take screenshots, and interact with the desktop environment.

## How to Use This Skill

As an AI agent, you can invoke desktop automation commands using the `uvx desktop-agent` CLI.

### Command Structure

All commands follow this pattern:

```bash
uvx desktop-agent <category> <command> [arguments] [options]
```

**Categories:**
- `mouse` - Mouse control
- `keyboard` - Keyboard input
- `screen` - Screenshots and screen analysis
- `message` - User dialogs
- `app` - Application control (open, focus, list windows)

## Available Commands

### 🖱️ Mouse Control (`mouse`)

Control cursor movement and clicks.

```bash
# Move cursor to coordinates
uvx desktop-agent mouse move <x> <y> [--duration SECONDS]

# Click at current position or specific coordinates
uvx desktop-agent mouse click [x] [y] [--button left|right|middle] [--clicks N]

# Specialized clicks
uvx desktop-agent mouse double-click [x] [y]
uvx desktop-agent mouse right-click [x] [y]
uvx desktop-agent mouse middle-click [x] [y]

# Drag to coordinates
uvx desktop-agent mouse drag <x> <y> [--duration SECONDS] [--button BUTTON]

# Scroll (positive=up, negative=down)
uvx desktop-agent mouse scroll <clicks> [x] [y]

# Get current mouse position
uvx desktop-agent mouse position
```

**Examples:**
```bash
# Move to center of 1920x1080 screen
uvx desktop-agent mouse move 960 540 --duration 0.5

# Right-click at specific location
uvx desktop-agent mouse right-click 500 300

# Scroll down 5 clicks
uvx desktop-agent mouse scroll -5
```

### ⌨️ Keyboard Control (`keyboard`)

Type text and execute keyboard shortcuts.

```bash
# Type text
uvx desktop-agent keyboard write "<text>" [--interval SECONDS]

# Press keys
uvx desktop-agent keyboard press <key> [--presses N] [--interval SECONDS]

# Execute hotkey combination (comma-separated)
uvx desktop-agent keyboard hotkey "<key1>,<key2>,..."

# Hold/release keys
uvx desktop-agent keyboard keydown <key>
uvx desktop-agent keyboard keyup <key>
```

**Examples:**
```bash
# Type text with natural delay
uvx desktop-agent keyboard write "Hello World" --interval 0.05

# Copy selected text
uvx desktop-agent keyboard hotkey "ctrl,c"

# Open Task Manager
uvx desktop-agent keyboard hotkey "ctrl,shift,esc"

# Press Enter 3 times
uvx desktop-agent keyboard press enter --presses 3
```

**Common Key Names:**
- Modifiers: `ctrl`, `shift`, `alt`, `win`
- Special: `enter`, `tab`, `esc`, `space`, `backspace`, `delete`
- Function: `f1` through `f12`
- Arrows: `up`, `down`, `left`, `right`

### 🖼️ Screen & Screenshots (`screen`)

Capture screenshots and analyze screen content. Supports targeting specific windows.

```bash
# Take screenshot
uvx desktop-agent screen screenshot <filename> [--region "x,y,width,height"] [--window <title>] [--active]

# Locate image on screen or within window
uvx desktop-agent screen locate <image_path> [--confidence 0.0-1.0] [--window <title>] [--active]
uvx desktop-agent screen locate-center <image_path> [--confidence 0.0-1.0] [--window <title>] [--active]

# Locate text using OCR within window
uvx desktop-agent screen locate-text-coordinates <text> [--window <title>] [--active]
uvx desktop-agent screen read-all-text [--window <title>] [--active]

# Utility commands
uvx desktop-agent screen pixel <x> <y>
uvx desktop-agent screen size
uvx desktop-agent screen on-screen <x> <y>
```

**Examples:**
```bash
# Screenshot of active window
uvx desktop-agent screen screenshot active.png --active

# Screenshot of a specific application
uvx desktop-agent screen screenshot chrome.png --window "Google Chrome"

# Locate image within Notepad
uvx desktop-agent screen locate-center button.png --window "Notepad"
```

### 💬 Message Dialogs (`message`)

Display user interaction dialogs.

```bash
# Show alert
uvx desktop-agent message alert "<text>" [--title TITLE] [--button BUTTON]

# Show confirmation dialog
uvx desktop-agent message confirm "<text>" [--title TITLE] [--buttons "OK,Cancel"]

# Prompt for input
uvx desktop-agent message prompt "<text>" [--title TITLE] [--default TEXT]

# Password input
uvx desktop-agent message password "<text>" [--title TITLE] [--mask CHAR]
```

**Examples:**
```bash
# Simple alert
uvx desktop-agent message alert "Task completed!"

# Get user confirmation
uvx desktop-agent message confirm "Continue with operation?"

# Ask for user input
uvx desktop-agent message prompt "Enter your name:"
```

### 📱 Application Control (`app`)

Control applications across Windows, macOS, and Linux.

```bash
# Open an application by name
uvx desktop-agent app open <name> [--arg ARGS...]

# Focus on a window by title/name
uvx desktop-agent app focus <name>

# List all visible windows
uvx desktop-agent app list
```

**Examples:**
```bash
# Windows: Open Notepad
uvx desktop-agent app open notepad

# Windows: Open Chrome with a URL
uvx desktop-agent app open "chrome" --arg "https://google.com"

# macOS: Open Safari
uvx desktop-agent app open "Safari"

# Focus on a specific window
uvx desktop-agent app focus "Untitled - Notepad"

# List all open windows
uvx desktop-agent app list
```

## Common Automation Workflows

### Workflow 1: Open Application and Type

```bash
# Open notepad directly (cross-platform)
uvx desktop-agent app open notepad

# Wait for app to open, then focus it
uvx desktop-agent app focus notepad

# Type some text
uvx desktop-agent keyboard write "Hello from Desktop Skill!"
```

### Workflow 2: Screenshot + Analysis

```bash
# Get screen size first
uvx desktop-agent screen size

# Take full screenshot
uvx desktop-agent screen screenshot current_screen.png

# Check if specific UI element is visible
uvx desktop-agent screen locate save_button.png
```

### Workflow 3: Form Filling

```bash
# Click first field
uvx desktop-agent mouse click 300 200

# Fill field
uvx desktop-agent keyboard write "John Doe"

# Tab to next field
uvx desktop-agent keyboard press tab

# Fill second field
uvx desktop-agent keyboard write "john@example.com"

# Submit form (Enter)
uvx desktop-agent keyboard press enter
```

### Workflow 4: Copy/Paste Operations

```bash
# Select all text
uvx desktop-agent keyboard hotkey "ctrl,a"

# Copy
uvx desktop-agent keyboard hotkey "ctrl,c"

# Click destination
uvx desktop-agent mouse click 500 600

# Paste
uvx desktop-agent keyboard hotkey "ctrl,v"
```

## Safety Considerations

When using this skill, AI agents should:

1. **Verify coordinates**: Use `screen size` and `on-screen` before clicking
2. **Add delays**: Insert appropriate delays between commands for UI responsiveness
3. **Validate images**: Ensure image files exist before using `locate` commands
4. **Handle failures**: Commands may fail if windows change or elements move
5. **User safety**: Always confirm destructive actions with user via `message confirm`

## Troubleshooting

### PyAutoGUI Fail-Safe
PyAutoGUI has a fail-safe: moving mouse to screen corner aborts operations. This is a safety feature.

### Image not found
When using `screen locate`, ensure:
- Image file exists and path is correct
- Adjust `--confidence` (try 0.7-0.9)
- Image matches exact screen appearance (resolution, colors)

## Getting Help

```bash
# Show all available commands
uvx desktop-agent --help

# Show commands for specific category
uvx desktop-agent mouse --help
uvx desktop-agent keyboard --help
uvx desktop-agent screen --help
uvx desktop-agent message --help

# Show help for specific command
uvx desktop-agent mouse move --help
```

## Integration Tips for AI Agents

1. **Always check screen size first** when working with absolute coordinates
2. **Use relative positioning** when possible (e.g., get current position, calculate offset)
3. **Combine commands** for complex workflows
4. **Validate before executing** (e.g., check if image exists on screen)
5. **Provide user feedback** using message dialogs for important operations
6. **Handle errors gracefully** - commands may fail if UI state changes

## Performance Notes

- Mouse movements with `--duration` are animated and take time
- Image location (`locate`) can be slow on large screens - use regions when possible
- Keyboard commands are generally fast (< 100ms)
- Screenshots depend on screen resolution and region size

## Output Format

All commands output structured JSON by default, ideal for programmatic use by AI agents:

```bash
uvx desktop-agent mouse position
# Output: {"success": true, "command": "mouse.position", "timestamp": "2026-01-31T10:00:00Z", "duration_ms": 5, "data": {"position": {"x": 960, "y": 540}}}
```

### Response Schema

All JSON responses follow this schema:

```json
{
  "success": true,
  "command": "category.command",
  "timestamp": "2026-01-31T10:00:00Z",
  "duration_ms": 150,
  "data": { ... },
  "error": null
}
```

### Error Response Schema

```json
{
  "success": false,
  "command": "category.command",
  "timestamp": "2026-01-31T10:00:00Z",
  "duration_ms": 50,
  "data": null,
  "error": {
    "code": "image_not_found",
    "message": "Image file 'button.png' not found",
    "details": {},
    "recoverable": true
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `success` | Command succeeded |
| `invalid_argument` | Invalid command arguments |
| `coordinates_out_of_bounds` | Coordinates outside screen |
| `image_not_found` | Image file not found or not on screen |
| `window_not_found` | Target window not found |
| `ocr_failed` | OCR operation failed |
| `application_not_found` | Application not found |
| `permission_denied` | Permission denied |
| `platform_not_supported` | Platform not supported |
| `timeout` | Operation timed out |
| `unknown_error` | Unknown error |

**Mouse move:**
```bash
uvx desktop-agent mouse move 960 540
```
```json
{"success": true, "command": "mouse.move", "timestamp": "...", "duration_ms": 150, "data": {"x": 960, "y": 540, "duration": 0}, "error": null}
```

**Screen size:**
```bash
uvx desktop-agent screen size
```
```json
{"success": true, "command": "screen.size", "timestamp": "...", "duration_ms": 5, "data": {"size": {"width": 1920, "height": 1080}}, "error": null}
```

**Locate image:**
```bash
uvx desktop-agent screen locate button.png
```
```json
{"success": true, "command": "screen.locate", "timestamp": "...", "duration_ms": 250, "data": {"image_found": true, "bounding_box": {"left": 100, "top": 200, "width": 50, "height": 30, "center_x": 125, "center_y": 215}}, "error": null}
```

**List windows:**
```bash
uvx desktop-agent app list
```
```json
{"success": true, "command": "app.list", "timestamp": "...", "duration_ms": 100, "data": {"windows": ["Untitled - Notepad", "Google Chrome", "Visual Studio Code"]}, "error": null}
```

**Error example:**
```bash
uvx desktop-agent screen locate missing.png
```
```json
{"success": false, "command": "screen.locate", "timestamp": "...", "duration_ms": 50, "data": null, "error": {"code": "image_not_found", "message": "Image file 'missing.png' not found", "details": {}, "recoverable": true}}
```

## Effective Usage Guide for AI Agents

This section teaches AI agents how to use this skill effectively with optimal command sequences and best practices.

### 🎯 Core Strategy: Observe First, Then Act

**Always** understand the current state before performing actions. This avoids clicking wrong coordinates or typing in the wrong window.

**Recommended Initial Sequence:**
```bash
# 1. Get screen dimensions to understand your workspace
uvx desktop-agent screen size
uvx desktop-agent app list
uvx desktop-agent mouse position
```

### 📋 Recommended Command Sequences by Task

#### Open and Interact with Application

```bash
# ✅ CORRECT: Open, wait, verify, then interact
uvx desktop-agent app open notepad              # Step 1: Open app
uvx desktop-agent app list
uvx desktop-agent app focus "Notepad"
uvx desktop-agent keyboard write "Hello World"  # Step 4: Now safe to type

# ❌ WRONG: Type immediately without verification
uvx desktop-agent app open notepad
uvx desktop-agent keyboard write "Hello World"  # May type in wrong window!
```

#### Find and Click UI Element (Image-Based)

```bash
# ✅ CORRECT: Locate first, click if found
uvx desktop-agent screen locate-center button.png --confidence 0.8
# Check if success=true and coordinates are valid
uvx desktop-agent mouse click 125 215  # Use returned coordinates

# ❌ WRONG: Click without verifying element exists
uvx desktop-agent mouse click 125 215  # Might click wrong area!
```

#### Find and Click UI Element (Text-Based with OCR)

```bash
# ✅ CORRECT: Read screen text, then locate specific text
uvx desktop-agent screen read-all-text --active
uvx desktop-agent screen locate-text-coordinates "Save" --active
# Use returned coordinates to click

# For window-specific OCR:
uvx desktop-agent screen locate-text-coordinates "OK" --window "Dialog Title"
```

#### Fill a Form with Multiple Fields

```bash
# ✅ CORRECT: Click each field explicitly before typing
uvx desktop-agent mouse click 300 200           # Click first field
uvx desktop-agent keyboard write "John Doe"
uvx desktop-agent mouse click 300 250           # Click second field (more reliable)
uvx desktop-agent keyboard write "john@example.com"
uvx desktop-agent mouse click 300 300           # Click third field
uvx desktop-agent keyboard write "555-1234"

# OR use Tab navigation (less reliable if field order changes)
uvx desktop-agent mouse click 300 200
uvx desktop-agent keyboard write "John Doe"
uvx desktop-agent keyboard press tab
uvx desktop-agent keyboard write "john@example.com"
uvx desktop-agent keyboard press tab
uvx desktop-agent keyboard write "555-1234"
uvx desktop-agent keyboard press enter          # Submit
```

#### Take Targeted Screenshots for Analysis

```bash
# ✅ CORRECT: Screenshot specific windows for faster processing
uvx desktop-agent app list --json                           # Find exact window title
uvx desktop-agent screen screenshot app.png --window "Google Chrome"

# For active window only
uvx desktop-agent screen screenshot active.png --active

# Full screen only when necessary (slower, larger file)
uvx desktop-agent screen size
uvx desktop-agent screen screenshot full.png
```

#### Safe Drag and Drop

```bash
# ✅ CORRECT: Move to start, verify position, then drag
uvx desktop-agent mouse move 100 200                 # Move to source
uvx desktop-agent mouse position              # Verify position
uvx desktop-agent mouse drag 500 400 --duration 0.5  # Drag to destination

# For precision, use slower duration
uvx desktop-agent mouse drag 500 400 --duration 1.0
```

### 🔄 Error Recovery Patterns

#### When Window Not Found

```bash
# Pattern: List windows, find closest match, retry
uvx desktop-agent app focus "Chrome"             # Fails with window_not_found
uvx desktop-agent app list                # See actual window titles
# Output shows: "Google Chrome - My Page"
uvx desktop-agent app focus "Google Chrome"      # Use correct title
```

#### When Image Not Found

```bash
# Pattern: Adjust confidence or take new screenshot
uvx desktop-agent screen locate button.png --confidence 0.9
uvx desktop-agent screen locate button.png --confidence 0.7
# If still failing, capture current state for analysis
uvx desktop-agent screen screenshot current.png --active
```

#### When Click Seems to Miss

```bash
# Pattern: Verify coordinates are on screen
uvx desktop-agent screen size             # Get screen bounds
uvx desktop-agent screen on-screen 1500 900      # Check if coords are valid
uvx desktop-agent mouse move 1500 900            # Move first to visualize
uvx desktop-agent mouse click                    # Then click at current position
```

### ⚡ Performance Optimization

#### Minimize Screenshots

```bash
# ✅ GOOD: Screenshot only the region you need
uvx desktop-agent screen screenshot button_area.png --region "100,200,200,100"

# ✅ GOOD: Screenshot specific window instead of full screen  
uvx desktop-agent screen screenshot chrome.png --window "Google Chrome"

# ❌ SLOW: Full screen capture when you only need a small area
uvx desktop-agent screen screenshot full.png
```

#### Batch Keyboard Input

```bash
# ✅ FASTER: Write entire text at once
uvx desktop-agent keyboard write "This is a complete sentence with all the text."

# ❌ SLOWER: Multiple write commands
uvx desktop-agent keyboard write "This is "
uvx desktop-agent keyboard write "a complete "
uvx desktop-agent keyboard write "sentence."
```

#### Use Hotkeys Over Mouse When Possible

```bash
# ✅ FASTER: Use keyboard shortcuts
uvx desktop-agent keyboard hotkey "ctrl,s"       # Save
uvx desktop-agent keyboard hotkey "ctrl,a"       # Select all
uvx desktop-agent keyboard hotkey "ctrl,shift,s" # Save as

# ❌ SLOWER: Navigate menu with mouse
uvx desktop-agent mouse click 50 30              # Click File menu
uvx desktop-agent mouse click 60 80              # Click Save option
```

### 🛡️ Defensive Programming Patterns

#### Always Verify Critical Actions

```bash
# Before destructive action, confirm with user
uvx desktop-agent message confirm "This will delete all files. Continue?" --title "Warning"
# Check output: if "Cancel" was clicked, abort operation
```

#### Use JSON Mode for Reliable Parsing

```bash
# ✅ RELIABLE: Parse structured JSON output
uvx desktop-agent screen locate button.png
# Parse: {"success": true, "data": {"center_x": 125, "center_y": 215}}

# ❌ FRAGILE: Parse text output
uvx desktop-agent screen locate button.png
# Parse: "Found at: Box(left=100, top=200, width=50, height=30)"
```

#### Validate Before Multi-Step Operations

```bash
# Multi-step file operation with validation
uvx desktop-agent app list
uvx desktop-agent screen locate-text-coordinates "File" --active
uvx desktop-agent mouse click <returned_x> <returned_y>
uvx desktop-agent screen locate-text-coordinates "Save As" --active
uvx desktop-agent mouse click <returned_x> <returned_y>
```

### 🎮 Platform-Specific Considerations

#### Windows

```bash
# Common Windows shortcuts
uvx desktop-agent keyboard hotkey "win,d"        # Show desktop
uvx desktop-agent keyboard hotkey "win,e"        # Open Explorer
uvx desktop-agent keyboard hotkey "alt,tab"      # Switch windows
uvx desktop-agent keyboard hotkey "win,r"        # Run dialog

# Open apps by name
uvx desktop-agent app open notepad
uvx desktop-agent app open calc
uvx desktop-agent app open mspaint
```

#### macOS

```bash
# Common macOS shortcuts (use 'command' for Cmd key)
uvx desktop-agent keyboard hotkey "command,space"   # Spotlight
uvx desktop-agent keyboard hotkey "command,tab"     # App switcher
uvx desktop-agent keyboard hotkey "command,q"       # Quit app
uvx desktop-agent keyboard hotkey "command,shift,3" # Screenshot

# Open apps
uvx desktop-agent app open "Safari"
uvx desktop-agent app open "TextEdit"
```

#### Linux

```bash
# Open apps (uses xdg-open or direct command)
uvx desktop-agent app open firefox
uvx desktop-agent app open gedit

# Common shortcuts may vary by DE
uvx desktop-agent keyboard hotkey "alt,f2"       # Run dialog (many DEs)
```

### 📊 Decision Tree: Choosing the Right Command

```
 Want to interact with an app?
├── App not running → `app open <name>`
├── App running but not focused → `app focus <name>` 
└── Need to verify windows → `app list`

Want to find a UI element?
├── Have reference image → `screen locate-center <image>`
├── Know the text label → `screen locate-text-coordinates "<text>"`
└── Need to see all text → `screen read-all-text --active`

Want to click something?
├── Know exact coordinates → `mouse click <x> <y>`
├── Need to find first → Use locate commands above, then click returned coords
└── Not sure if on screen → `screen on-screen <x> <y>` first

Want to type something?
├── Regular text → `keyboard write "<text>"`
├── Keyboard shortcut → `keyboard hotkey "<key1>,<key2>"`
├── Single key press → `keyboard press <key>`
└── Multiple of same key → `keyboard press <key> --presses N`
```

## Integration Tips for AI Agents

1. **Always check screen size first** when working with absolute coordinates
2. **Use relative positioning** when possible (e.g., get current position, calculate offset)
3. **Combine commands** for complex workflows
4. **Validate before executing** (e.g., check if image exists on screen)
5. **Provide user feedback** using message dialogs for important operations
6. **Handle errors gracefully** - commands may fail if UI state changes
