# Automation Examples

Collection of practical automation examples using the Desktop Control Skill.

## Example 1: Open and Configure Notepad

```bash
# Open Run dialog
python main.py keyboard hotkey "win,r"

# Small delay for dialog to appear (200ms)
# In actual automation, add sleep between steps

# Type notepad
python main.py keyboard write "notepad"

# Press Enter to open
python main.py keyboard press enter

# Wait for Notepad to open (500ms recommended)

# Type some text
python main.py keyboard write "Hello from Desktop Control Skill!"

# Select all
python main.py keyboard hotkey "ctrl,a"

# Change to uppercase (in many text editors)
python main.py keyboard hotkey "shift,f3"
```

## Example 2: Screenshot Workflow

```bash
# Get screen dimensions
python main.py screen size
# Output: Screen size: 1920x1080

# Take full screenshot
python main.py screen screenshot full_desktop.png

# Take screenshot of top-left quadrant
python main.py screen screenshot quadrant.png --region "0,0,960,540"

# Get pixel color at specific location
python main.py screen pixel 100 100
# Output: Pixel at (100, 100): RGB(45, 45, 48)
```

## Example 3: Form Filling Automation

Automate filling a form with tab navigation:

```bash
# Click first field (adjust coordinates for your form)
python main.py mouse click 300 200

# Fill first name
python main.py keyboard write "John"

# Tab to next field
python main.py keyboard press tab

# Fill last name
python main.py keyboard write "Doe"

# Tab to email field
python main.py keyboard press tab

# Fill email
python main.py keyboard write "john.doe@example.com"

# Tab to next field
python main.py keyboard press tab

# Fill phone
python main.py keyboard write "555-1234"

# Submit form (or click submit button)
python main.py keyboard press enter
```

## Example 4: Image-Based Button Clicking

Find and click a button using image recognition:

```bash
# First, save a screenshot of the button you want to click
# Name it 'button.png' and place it in the project directory

# Locate the button on screen
python main.py screen locate-center button.png --confidence 0.9
# Output: Center at: (450, 320)

# If found, click at those coordinates
python main.py mouse click 450 320
```

## Example 5: Copy File Path from Explorer

```bash
# Assuming file is already selected in Windows Explorer

# Copy path: Alt+D (focus address bar) then Ctrl+C
python main.py keyboard hotkey "alt,d"

# Small delay

# Copy address
python main.py keyboard hotkey "ctrl,c"

# Path is now in clipboard
```

## Example 6: Multiple Window Management

```bash
# Show all windows (Windows + Tab)
python main.py keyboard hotkey "win,tab"

# Navigate with arrow keys
python main.py keyboard press right
python main.py keyboard press right

# Select window
python main.py keyboard press enter

# Or use Alt+Tab for quick switching
python main.py keyboard hotkey "alt,tab"
```

## Example 7: Text Manipulation

```bash
# Select current line (Home, Shift+End)
python main.py keyboard press home
python main.py keyboard hotkey "shift,end"

# Copy it
python main.py keyboard hotkey "ctrl,c"

# Move to end of document
python main.py keyboard hotkey "ctrl,end"

# Paste
python main.py keyboard hotkey "ctrl,v"
```

## Example 8: Screen Region Analysis

```bash
# Capture specific region for analysis
python main.py screen screenshot taskbar.png --region "0,1040,1920,40"

# Get colors at multiple points
python main.py screen pixel 10 10
python main.py screen pixel 100 100
python main.py screen pixel 500 500

# Verify a coordinate is on screen before clicking
python main.py screen on-screen 2000 2000
# Output: (2000, 2000) is NOT on screen
```

## Example 9: User Interaction

```bash
# Ask for confirmation before proceeding
python main.py message confirm "Do you want to proceed with the operation?"
# User clicks OK or Cancel

# Get user input
python main.py message prompt "Enter the filename:" --default "document.txt"
# Returns user input

# Show completion message
python main.py message alert "Operation completed successfully!"
```

## Example 10: Drawing/Painting Automation

```bash
# Open Paint
python main.py keyboard hotkey "win,r"
python main.py keyboard write "mspaint"
python main.py keyboard press enter

# Wait for Paint to open

# Select pencil tool (keyboard shortcut)
python main.py keyboard press p

# Draw a square by dragging
python main.py mouse move 200 200
python main.py mouse drag 400 200 --duration 0.5
python main.py mouse drag 400 400 --duration 0.5
python main.py mouse drag 200 400 --duration 0.5
python main.py mouse drag 200 200 --duration 0.5
```

## Tips for Reliable Automation

1. **Add Delays**: Always add small delays between commands when automating UI
   - After opening applications: 500-1000ms
   - After clicking: 100-200ms
   - After typing: 50-100ms per character or use `--interval`

2. **Verify Before Acting**: 
   - Use `screen size` to calculate safe coordinates
   - Use `screen on-screen` to validate coordinates
   - Use `screen locate` to find UI elements

3. **Error Handling**:
   - Save screenshots before/after operations for debugging
   - Use `message confirm` for critical operations
   - Validate paths and files exist before using them

4. **Resolution Independence**:
   - Get screen size first
   - Calculate relative positions (e.g., center = width/2, height/2)
   - Use image recognition instead of fixed coordinates when possible

5. **Keyboard Shortcuts**:
   - Prefer keyboard shortcuts over mouse clicks when possible
   - More reliable and faster
   - Less dependent on screen resolution
