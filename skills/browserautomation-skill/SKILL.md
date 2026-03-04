---
name: browser-automation-skill
description: Advanced headless browser automation skill for OpenClaw agents. Enables intelligent web navigation, form filling, data extraction, and UI testing with structured commands and semantic element targeting.
read_when:
  - Automating web interactions or browser tasks
  - Extracting data from websites
  - Filling and submitting web forms
  - Testing web user interfaces
  - Scraping structured content from pages
  - Logging into web applications
  - Taking screenshots or PDF snapshots
  - Recording browser sessions
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["node","npm"]},"priority":"high"}}
allowed-tools: Bash(agent-browser:*)
---

# OpenClaw Browser Automation Skill

## IMPORTANT: Before You Start

**READ THE PROJECT README.md FIRST!**

Before executing any browser automation tasks:
1. Read the project's README.md to understand the context and requirements
2. Identify target URLs, credentials (if any), and expected outcomes
3. Plan your automation workflow before running commands
4. Check if authentication/session state exists that can be reused

## Installation

### Quick Install (Recommended)

```bash
npm install -g agent-browser
agent-browser install --with-deps
```

### Verify Installation

```bash
agent-browser --version
```

If installation fails, try:
```bash
npx agent-browser install --with-deps
```

## Core Workflow Pattern

Every browser automation task follows this pattern:

```
1. OPEN    -> Navigate to target URL
2. SNAPSHOT -> Analyze page structure, get element refs
3. INTERACT -> Click, fill, select using refs
4. VERIFY   -> Re-snapshot to confirm changes
5. REPEAT   -> Continue until task complete
6. CLOSE    -> Clean up browser session
```

## Quick Reference

### Navigation

| Command | Description |
|---------|-------------|
| `agent-browser open <url>` | Navigate to URL |
| `agent-browser back` | Go back in history |
| `agent-browser forward` | Go forward |
| `agent-browser reload` | Reload current page |
| `agent-browser close` | Close browser session |

### Page Analysis

| Command | Description |
|---------|-------------|
| `agent-browser snapshot -i` | **Most used**: Interactive elements with refs |
| `agent-browser snapshot -i -c` | Compact interactive snapshot |
| `agent-browser snapshot -s "#main"` | Scope to specific container |
| `agent-browser snapshot -d 3` | Limit tree depth |

### Element Interaction (use @refs from snapshot)

| Command | Description |
|---------|-------------|
| `agent-browser click @e1` | Click element |
| `agent-browser fill @e1 "text"` | Clear field and type (preferred for inputs) |
| `agent-browser type @e1 "text"` | Type without clearing |
| `agent-browser press Enter` | Press keyboard key |
| `agent-browser press Control+a` | Key combination |
| `agent-browser select @e1 "value"` | Select dropdown option |
| `agent-browser check @e1` | Check checkbox |
| `agent-browser uncheck @e1` | Uncheck checkbox |
| `agent-browser hover @e1` | Hover over element |
| `agent-browser upload @e1 file.pdf` | Upload file |

### Data Extraction

| Command | Description |
|---------|-------------|
| `agent-browser get text @e1` | Get element text content |
| `agent-browser get html @e1` | Get inner HTML |
| `agent-browser get value @e1` | Get input field value |
| `agent-browser get attr @e1 href` | Get specific attribute |
| `agent-browser get title` | Get page title |
| `agent-browser get url` | Get current URL |
| `agent-browser get count ".selector"` | Count matching elements |

### Waiting (Critical for Reliability)

| Command | Description |
|---------|-------------|
| `agent-browser wait @e1` | Wait for element to appear |
| `agent-browser wait 2000` | Wait milliseconds |
| `agent-browser wait --text "Success"` | Wait for text to appear |
| `agent-browser wait --url "/dashboard"` | Wait for URL change |
| `agent-browser wait --load networkidle` | Wait for network idle |

### Screenshots & PDF

| Command | Description |
|---------|-------------|
| `agent-browser screenshot out.png` | Save screenshot |
| `agent-browser screenshot --full out.png` | Full page screenshot |
| `agent-browser pdf output.pdf` | Save page as PDF |

## Common Task Recipes

### Recipe 1: Login Flow

```bash
# 1. Open login page
agent-browser open https://example.com/login

# 2. Get interactive elements
agent-browser snapshot -i
# Output: textbox "Email" [ref=e1], textbox "Password" [ref=e2], button "Sign in" [ref=e3]

# 3. Fill credentials
agent-browser fill @e1 "user@example.com"
agent-browser fill @e2 "secure_password"

# 4. Submit
agent-browser click @e3

# 5. Wait for redirect
agent-browser wait --url "/dashboard"
agent-browser wait --load networkidle

# 6. Save session for reuse
agent-browser state save session.json

# 7. Verify success
agent-browser snapshot -i
```

### Recipe 2: Data Extraction Loop

```bash
# Navigate to listing page
agent-browser open https://example.com/products

# Get initial snapshot
agent-browser snapshot -i

# Extract data from each item
agent-browser get text @e1
agent-browser get attr @e2 href

# Check for pagination
agent-browser snapshot -s ".pagination"

# Click next if exists
agent-browser click @e5
agent-browser wait --load networkidle

# Re-snapshot for new content
agent-browser snapshot -i
```

### Recipe 3: Form Submission with Validation

```bash
# Open form
agent-browser open https://example.com/contact

# Analyze form structure
agent-browser snapshot -i

# Fill all required fields
agent-browser fill @e1 "John Doe"
agent-browser fill @e2 "john@example.com"
agent-browser fill @e3 "Hello, this is my message."

# Select dropdown if present
agent-browser select @e4 "support"

# Check required checkbox
agent-browser check @e5

# Submit form
agent-browser click @e6

# Wait and verify submission
agent-browser wait --text "Thank you"
agent-browser snapshot -i
```

### Recipe 4: Session Persistence

```bash
# First time: Login and save state
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "username"
agent-browser fill @e2 "password"
agent-browser click @e3
agent-browser wait --url "/home"
agent-browser state save auth-session.json

# Later: Restore session and continue
agent-browser state load auth-session.json
agent-browser open https://app.example.com/dashboard
# Already logged in!
```

### Recipe 5: Multi-Tab Workflow

```bash
# Open first site
agent-browser open https://site-a.com

# Open second tab
agent-browser tab new https://site-b.com

# List tabs
agent-browser tab
# Output: Tab 1: site-a.com, Tab 2: site-b.com (active)

# Switch between tabs
agent-browser tab 1
agent-browser snapshot -i
# Work on tab 1...

agent-browser tab 2
agent-browser snapshot -i
# Work on tab 2...
```

### Recipe 6: Debugging Failed Automation

```bash
# Enable headed mode to see what's happening
agent-browser open https://example.com --headed

# Check for JavaScript errors
agent-browser errors

# View console output
agent-browser console

# Highlight element to verify selection
agent-browser highlight @e1

# Take screenshot for debugging
agent-browser screenshot debug.png

# Start trace for detailed analysis
agent-browser trace start
# ... perform actions ...
agent-browser trace stop trace.zip
```

## Semantic Locators (Alternative to Refs)

When refs are unstable or you need more readable selectors:

```bash
# Find by role
agent-browser find role button click --name "Submit"

# Find by text content
agent-browser find text "Sign In" click

# Find by label
agent-browser find label "Email" fill "user@test.com"

# Find first matching selector
agent-browser find first ".item" click

# Find nth element
agent-browser find nth 2 "a" text
```

## Network Control

```bash
# Mock API response
agent-browser network route "*/api/user" --body '{"name":"Test User"}'

# Block analytics/ads
agent-browser network route "*google-analytics*" --abort
agent-browser network route "*facebook.com*" --abort

# View captured requests
agent-browser network requests --filter api

# Remove routes
agent-browser network unroute
```

## Browser Configuration

```bash
# Set viewport for responsive testing
agent-browser set viewport 1920 1080
agent-browser set viewport 375 667  # Mobile

# Emulate device
agent-browser set device "iPhone 14"
agent-browser set device "Pixel 5"

# Set geolocation
agent-browser set geo 40.7128 -74.0060  # New York

# Dark mode testing
agent-browser set media dark
```

## Best Practices

### 1. Always Snapshot After Navigation
```bash
agent-browser open https://example.com
agent-browser wait --load networkidle
agent-browser snapshot -i  # ALWAYS do this after navigation
```

### 2. Use fill Instead of type for Inputs
```bash
# GOOD: Clears existing text first
agent-browser fill @e1 "new text"

# BAD: Appends to existing text
agent-browser type @e1 "new text"
```

### 3. Add Explicit Waits for Reliability
```bash
# After clicking that triggers navigation
agent-browser click @e1
agent-browser wait --load networkidle

# After AJAX updates
agent-browser click @e1
agent-browser wait --text "Updated"
```

### 4. Handle Iframes Explicitly
```bash
# Switch to iframe before interacting
agent-browser frame "#iframe-id"
agent-browser snapshot -i
agent-browser click @e1

# Return to main frame
agent-browser frame main
```

### 5. Save Session State Early
```bash
# Save immediately after successful login
agent-browser state save session.json
# Can reload if something breaks later
```

## Error Recovery

### Element Not Found
```bash
# Re-snapshot to get updated refs
agent-browser snapshot -i

# Try semantic locator
agent-browser find text "Button Text" click

# Check if element is in iframe
agent-browser frame "#iframe"
agent-browser snapshot -i
```

### Page Not Loading
```bash
# Increase timeout
agent-browser open https://slow-site.com --timeout 60000

# Wait explicitly
agent-browser wait --load networkidle
agent-browser wait 5000
```

### Session Lost
```bash
# Reload saved state
agent-browser state load session.json
agent-browser reload
```

### Debug Mode
```bash
# Visual debugging
agent-browser open https://example.com --headed
agent-browser screenshot debug.png
agent-browser errors
agent-browser console
```

## Parallel Sessions

For working with multiple isolated browsers:

```bash
# Session 1
agent-browser --session user1 open https://app.com
agent-browser --session user1 snapshot -i

# Session 2 (completely isolated)
agent-browser --session user2 open https://app.com
agent-browser --session user2 snapshot -i

# List all sessions
agent-browser session list

# Each session has separate cookies, storage, and state
```

## JSON Output for Parsing

Add `--json` flag to get machine-readable output:

```bash
agent-browser snapshot -i --json | jq '.elements[]'
agent-browser get text @e1 --json
agent-browser get url --json
```

## Video Recording

```bash
# Start recording from current page
agent-browser record start ./demo.webm

# Perform your automation
agent-browser click @e1
agent-browser fill @e2 "text"

# Stop and save
agent-browser record stop
```

## Troubleshooting Checklist

1. **Command not found**: Run `agent-browser install --with-deps`
2. **Element not found**: Run `agent-browser snapshot -i` to refresh refs
3. **Page timeout**: Add `--timeout 60000` for slow pages
4. **Can't see what's happening**: Add `--headed` flag
5. **Login not persisting**: Use `agent-browser state save/load`
6. **Refs changed**: Always re-snapshot after navigation
7. **Iframe content**: Use `agent-browser frame` to switch context