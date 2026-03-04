# Desktop Control Skill

🤖 **AI Agent Skill** for desktop automation using PyAutoGUI.

Control mouse, keyboard, and screen programmatically through a simple CLI interface.

## ⚡ Quick Install

### For AI Agents

Add this skill to your AI coding agent with a single command:

```bash
npx skills add patrickporto/desktop-agent
```

### For Users

Install the CLI with pipx (recommended):

```bash
pipx install desktop-agent
```

Or run without installing using uvx:

```bash
uvx desktop-agent --help
```

Or using pip:

```bash
pip install desktop-agent
```

---

## 🎯 For AI Agents

This project is packaged as an **AI Agent Skill**. To use it:

1. **Read the skill documentation**: [SKILL.md](SKILL.md)
2. **Install the CLI**: Use `pip install desktop-agent` or `pipx install desktop-agent`
3. **Invoke commands**: Use `desktop-agent <category> <command>`

**Quick Reference for Agents:**
- All commands documented in [SKILL.md](SKILL.md)
- Practical examples in [examples/automation_examples.md](examples/automation_examples.md)
- Help system: `desktop-agent --help`
- All commands return JSON output by default

---

## 📦 Installation

### Using pipx (Recommended)

```bash
pipx install desktop-agent
```

### Using pip

```bash
pip install desktop-agent
```

### Run without installing (using uvx)

```bash
uvx desktop-agent
```


## Usage

The CLI is organized into command categories:

### 🖱️ Mouse (`mouse`)

```bash
# Move mouse to coordinates
desktop-agent mouse move 100 200

# Move with duration (animation)
desktop-agent mouse move 100 200 --duration 1.0

# Click at current position
desktop-agent mouse click

# Click at specific coordinates
desktop-agent mouse click 500 500

# Right click
desktop-agent mouse right-click

# Double click
desktop-agent mouse double-click 300 400

# Drag to coordinates
desktop-agent mouse drag 200 300

# Scroll (positive = up, negative = down)
desktop-agent mouse scroll 5
desktop-agent mouse scroll -3

# Get current mouse position
desktop-agent mouse position
```

### ⌨️ Keyboard (`keyboard`)

```bash
# Write text
desktop-agent keyboard write "Hello World"

# Write with interval between keys
desktop-agent keyboard write "Slow typing" --interval 0.1

# Press a key
desktop-agent keyboard press enter

# Press multiple times
desktop-agent keyboard press a --presses 5

# Execute keyboard shortcut
desktop-agent keyboard hotkey "ctrl,c"
desktop-agent keyboard hotkey "ctrl,shift,esc"

# Hold/release key
desktop-agent keyboard keydown shift
desktop-agent keyboard keyup shift
```

### 🖼️ Screen (`screen`)

```bash
# Capture screenshot (full screen)
desktop-agent screen screenshot my_screen.png

# Take screenshot of active window
desktop-agent screen screenshot active_window.png --active

# Take screenshot of specific window
desktop-agent screen screenshot notepad.png --window "Notepad"

# Screenshot of specific region (x,y,width,height)
desktop-agent screen screenshot region.png --region "100,100,500,400"

# Locate image within active window
desktop-agent screen locate button.png --active

# Locate center of image on screen
desktop-agent screen locate-center button.png --confidence 0.8

# Find text coordinates within active window
desktop-agent screen locate-text-coordinates "OK" --active

# Find text in specific image
desktop-agent screen locate-text-coordinates "Confirm" --image screenshot.png

# Case-sensitive search
desktop-agent screen locate-text-coordinates "Login" --case-sensitive

# Read all text from screen
desktop-agent screen read-all-text

# Read text from image
desktop-agent screen read-all-text --image capture.png

# Specify languages for OCR (default: pt,en)
desktop-agent screen locate-text-coordinates "Button" --lang "en"
```

### 💬 Messages (`message`)

```bash
# Show alert
desktop-agent message alert "Hello!"

# Confirmation
desktop-agent message confirm "Are you sure?"

# Input prompt
desktop-agent message prompt "Enter your name:"

# Password
desktop-agent message password "Enter your password:"
```

### 📱 Applications (`app`)

```bash
# Open an application (cross-platform)
desktop-agent app open notepad
desktop-agent app open "Google Chrome"

# Open with arguments
desktop-agent app open chrome --arg "https://google.com"

# Focus on a window by title
desktop-agent app focus "Untitled - Notepad"

# List all visible windows
desktop-agent app list
```

## Automation Examples

### Open Notepad and write

```bash
desktop-agent app open notepad
desktop-agent app focus notepad
desktop-agent keyboard write "Hello from Desktop Skill!"
```

### Capture screenshot and analyze

```bash
desktop-agent screen screenshot full_screen.png
desktop-agent screen pixel 500 500
```

## Available Commands

Run `desktop-agent --help` to see all commands:

```bash
desktop-agent --help
desktop-agent mouse --help
desktop-agent keyboard --help
desktop-agent screen --help
desktop-agent message --help
```

## Project Structure

```
desktop-skill/
├── desktop_agent/       # Main package
│   ├── __init__.py
│   ├── commands/        # Command modules
│   │   ├── __init__.py
│   │   ├── mouse.py    # Mouse commands
│   │   ├── keyboard.py # Keyboard commands
│   │   ├── screen.py   # Screen/screenshot/OCR commands
│   │   └── message.py  # Message boxes
├── pyproject.toml      # Project configuration
└── README.md           # This documentation
```

## Technologies

- **PyAutoGUI**: GUI automation
- **EasyOCR**: Optical character recognition
- **Typer**: Modern CLI framework
