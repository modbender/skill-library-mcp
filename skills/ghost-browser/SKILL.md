---
name: ghost-browser
description: Automated Chrome browser using nodriver for AI agent web tasks. Full CLI control with LLM-optimized commands — text-based interaction, markdown output, session management, and smart element matching.
metadata:
  openclaw:
    emoji: "👻"
    requires:
      bins: ["python3", "google-chrome||chromium||/Applications/Google Chrome.app"]
      pip: ["nodriver>=0.38"]
---

# Ghost Browser

Automated Chrome browser for AI agent web tasks. Powered by [nodriver](https://github.com/nicedayzhu/nodriver) for reliable browser control. Every command is designed to minimize token usage and maximize accuracy.

Use for: web automation, screenshots, page reading, form filling, scraping, cookie/session management, and persistent browser profiles.

## How to Browse — Follow This Workflow

**ALWAYS use this workflow. Never use raw `content` (HTML) or CSS-selector `click`/`type` as your first choice.**

### Step 1: Navigate and understand the page

```bash
ghost-browser navigate https://example.com
ghost-browser wait-ready
ghost-browser page-summary
```

`page-summary` returns: page title, URL, element counts (links/buttons/inputs/forms), whether there's a login form, and a short text preview. Costs ~10 tokens.

### Step 2: See what you can interact with

```bash
ghost-browser elements              # Numbered list of ALL interactive elements
ghost-browser elements --form-only  # Just form inputs (for login/signup/search)
```

Output:
```
[0] link "Home" → /
[1] link "Products" → /products
[2] button "Sign In"
[3] input[email] "Email address"
[4] input[password] "Password"
[5] submit "Log In"
```

### Step 3: Interact by visible text (NOT CSS selectors)

```bash
ghost-browser interact click "Sign In"
ghost-browser interact type "Email" --type-text "user@example.com"
ghost-browser interact type "Password" --type-text "secret123"

# Or fill entire forms at once
ghost-browser fill-form '{"email":"user@example.com","password":"secret123"}' --submit
```

### Step 4: Read page content as markdown

```bash
ghost-browser readable                    # Full page as clean markdown
ghost-browser readable --max-length 5000  # Limit length to save tokens
```

**Never use `content`** — it returns raw HTML which wastes thousands of tokens. Use `readable` instead.

### Step 5: Wait for dynamic pages

```bash
ghost-browser wait-ready             # Wait for network idle + DOM stable
ghost-browser wait-ready --timeout 10
```

### Complete Login Example

```bash
ghost-browser start
ghost-browser navigate https://mysite.com/login
ghost-browser wait-ready
ghost-browser elements --form-only
ghost-browser fill-form '{"email":"me@example.com","password":"mypass"}' --submit
ghost-browser wait-ready
ghost-browser page-summary           # Verify login succeeded
ghost-browser session save mysite    # Save auth state for later
```

### Restore a Previous Session

```bash
ghost-browser start --profile mysite
ghost-browser session load mysite
ghost-browser navigate https://mysite.com/dashboard
ghost-browser page-summary
```

## Command Reference

### Preferred Commands (use these first)

| Command | What it does | Token cost |
|---------|-------------|------------|
| `page-summary` | Page overview: title, URL, element counts, flags | ~10 |
| `elements` | Numbered list of buttons, links, inputs | ~50-200 |
| `elements --form-only` | Just form inputs | ~10-50 |
| `readable` | Full page as clean markdown | ~500-10000 |
| `readable --max-length N` | Page markdown capped at N chars | controlled |
| `interact click "text"` | Click by visible text | action |
| `interact type "label" --type-text "value"` | Type by label/placeholder text | action |
| `fill-form '{"field":"value"}' --submit` | Fill and submit a form | action |
| `hover "text" --by-text` | Hover by visible text | action |
| `wait-ready` | Wait for page to finish loading | ~5 |
| `session save <name>` | Save cookies + localStorage + sessionStorage | ~10 |
| `session load <name>` | Restore full auth state | ~10 |

### Lifecycle

```bash
ghost-browser start                          # Start browser daemon
ghost-browser start --headless               # Run without visible window
ghost-browser start --profile work           # Use named profile (persistent data)
ghost-browser start --extension /path/ext    # Load unpacked Chrome extension
ghost-browser start --proxy socks5://host:port  # Use proxy
ghost-browser stop                           # Graceful shutdown
ghost-browser status                         # Check if running
ghost-browser status --json                  # Machine-readable status
ghost-browser health                         # Quick health check
```

### Navigation & Tabs

```bash
ghost-browser navigate <url>                 # Navigate current tab (or reuse matching tab)
ghost-browser navigate <url> --force-new     # Always open new tab
ghost-browser tabs                           # List open tabs with IDs
ghost-browser tabs --json                    # Machine-readable tab list
ghost-browser activate-tab <ID>              # Switch to a tab by ID
ghost-browser close-tab <ID>                 # Close a tab by ID
ghost-browser wait-ready                     # Wait for page to fully load
ghost-browser wait-ready --timeout 10        # Custom timeout in seconds
```

After `navigate`, all commands automatically target the navigated tab.

### Page Understanding

```bash
ghost-browser page-summary                   # Quick overview (~10 tokens)
ghost-browser elements                       # All interactive elements (numbered)
ghost-browser elements --form-only           # Form inputs only
ghost-browser elements --limit 50            # Cap at 50 elements
ghost-browser readable                       # Full page as markdown
ghost-browser readable --max-length 5000     # Limit output length
ghost-browser content                        # Raw HTML (avoid — use readable instead)
```

### Text-Based Interaction (preferred)

```bash
ghost-browser interact click "Sign In"       # Click by button/link text
ghost-browser interact type "Email" --type-text "user@example.com"  # Type by label
ghost-browser interact click "Products" --index 1  # Click 2nd match if multiple
ghost-browser fill-form '{"email":"a@b.com","password":"x"}' --submit
ghost-browser hover "Menu" --by-text         # Hover by visible text
```

### CSS Selector Interaction (fallback)

Use these only when text-based interaction fails.

```bash
ghost-browser click "button.submit"          # Click by CSS selector
ghost-browser type "input#email" "a@b.com"   # Type by CSS selector
ghost-browser find "h1"                      # Find elements by selector
ghost-browser hover ".dropdown"              # Hover by CSS selector
ghost-browser wait ".loaded" --timeout 10    # Wait for element to appear
ghost-browser scroll --down                  # Scroll down
ghost-browser scroll --up                    # Scroll up
ghost-browser scroll --to 500               # Scroll to Y position
ghost-browser eval "document.title"          # Execute arbitrary JavaScript
```

### Cookies & Storage

```bash
ghost-browser cookies                        # List all cookies
ghost-browser cookies --domain example.com   # Filter by domain
ghost-browser set-cookie name value          # Set a cookie
ghost-browser set-cookie name value --domain .example.com  # Set with domain
ghost-browser clear-cookies                  # Clear all cookies
ghost-browser clear-cookies --domain example.com  # Clear for domain
ghost-browser save-cookies --file cookies.json  # Export cookies to JSON
ghost-browser load-cookies cookies.json      # Import cookies from JSON
ghost-browser storage list                   # List localStorage entries
ghost-browser storage list --session         # List sessionStorage entries
ghost-browser storage get <key>              # Get a value
ghost-browser storage set <key> <value>      # Set a value
ghost-browser storage delete <key>           # Delete a key
ghost-browser storage clear                  # Clear all localStorage
```

### Session Management

```bash
ghost-browser session save <name>            # Save cookies + localStorage + sessionStorage
ghost-browser session load <name>            # Restore full auth state
```

Sessions are saved locally under `state/sessions/<name>.json`. They contain cookies and storage data needed to restore an authenticated state. Delete session files when no longer needed.

### Files & Media

```bash
ghost-browser screenshot                         # Screenshot to auto-named file
ghost-browser screenshot --output ./page.png     # Screenshot to specific file
ghost-browser pdf --output page.pdf              # Save page as PDF
ghost-browser pdf --output page.pdf --landscape  # Landscape PDF
ghost-browser upload photo.jpg                   # Upload file (auto-detect file input)
ghost-browser upload doc.pdf --selector "#file"  # Upload to specific file input
ghost-browser download <url> --output file.pdf   # Download a file
```

### Debugging

```bash
ghost-browser network-log                    # View recent network requests
ghost-browser network-log --limit 20         # Limit entries
ghost-browser network-log --filter api       # Filter by URL substring
ghost-browser network-log --clear            # Clear the log
ghost-browser console-log                    # View JS console output
ghost-browser console-log --level error      # Show only errors
ghost-browser console-log --clear            # Clear the log
ghost-browser eval "document.title"          # Execute JavaScript and return result
```

Network and console logging run automatically in the background.

### Window

```bash
ghost-browser window --size 1920x1080        # Resize window
ghost-browser window --position 0x0          # Reposition window
```

### Profile Management

Profiles persist browser data (history, cookies, extensions) across sessions.

```bash
ghost-browser profile list                   # List profiles with sizes
ghost-browser profile create <name>          # Create new profile
ghost-browser profile delete <name>          # Delete a profile and its data
ghost-browser profile default                # Show default profile
ghost-browser profile default <name>         # Set default profile
ghost-browser profile clone <src> <dst>      # Clone a profile
```

### Extension Management

```bash
ghost-browser install-extension <source>     # Install from Web Store URL/ID or .crx file
ghost-browser install-extension <source> --name custom-name  # Install with custom folder name
ghost-browser list-extensions                # List all installed extensions
ghost-browser remove-extension <name>        # Remove an installed extension
ghost-browser load-extension <name>          # Load extension into running browser
ghost-browser load-extension                 # Load all extensions
ghost-browser unload-extension <name>        # Unload extension from running browser
```

### Challenge Handling

```bash
ghost-browser cf-solve                       # Handle Cloudflare challenges (all tabs)
ghost-browser cf-solve --tab <ID>            # Handle on specific tab
```

Challenges are also detected and handled automatically in the background.

## Decision Guide

| I want to... | Use this |
|--------------|----------|
| Understand what's on a page | `page-summary` then `elements` if needed |
| Read page text content | `readable` (NOT `content`) |
| Click a button | `interact click "Button Text"` |
| Fill a login form | `fill-form '{"email":"...","password":"..."}' --submit` |
| Type into a specific field | `interact type "Field Label" --type-text "value"` |
| Wait for page to load | `wait-ready` |
| See what I can click/type | `elements` or `elements --form-only` |
| Save login for later | `session save sitename` |
| Restore a saved login | `session load sitename` |
| Debug a failing request | `network-log --filter domain.com` |
| Check for JS errors | `console-log --level error` |
| Take a screenshot | `screenshot --output ./page.png` |
| Run custom JavaScript | `eval "your code here"` |

## JSON Output

All commands support `--json` for machine-readable output:

```bash
ghost-browser page-summary --json
ghost-browser elements --json
ghost-browser readable --json
ghost-browser status --json
```

## Installation

After installing the skill, run the setup script:

```bash
bash setup.sh
```

This creates a Python virtual environment and installs dependencies automatically.

## Requirements

- Python 3.8+
- Google Chrome installed on the system
- nodriver (installed automatically by `setup.sh`)

## Data & Privacy

This skill stores the following data locally under its `state/` directory:

| Data | Location | Contains |
|------|----------|----------|
| Browser state | `state/browser.json` | Port numbers, process ID |
| Logs | `state/browser.log` | Daemon debug logs |
| Profiles | `state/profiles/` | Chrome user data (history, cookies) |
| Sessions | `state/sessions/` | Saved auth state (cookies, localStorage) |

**To clean up:** delete the `state/` directory to remove all persistent data. Use `ghost-browser profile delete <name>` to remove individual profiles.

Session and cookie files may contain authentication tokens. Handle them carefully and delete when no longer needed.

## Security

- Browser control server binds to 127.0.0.1 only (localhost, not network-accessible)
- The skill does not modify any files outside its own directory
- No environment variables or external credentials are required
- All persistent data is stored under the skill's `state/` directory

### Capability Disclosure

This skill is a full browser automation tool. By design, it includes capabilities that security scanners may flag:

- **`eval`** — Executes arbitrary JavaScript in the browser context. This is standard for any browser automation tool (equivalent to Playwright's `page.evaluate()` or Puppeteer's `page.evaluate()`).
- **`upload` / `download`** — Reads local files for upload and saves downloaded files to disk. Required for any browser that handles file inputs or downloads.
- **`session save/load`** — Persists cookies, localStorage, and sessionStorage to JSON files under `state/sessions/`. These files may contain authentication tokens. Delete sessions you no longer need.
- **`install-extension` / `load-extension`** — Loads Chrome extensions programmatically. On macOS, extension installation from .crx files may use `osascript` for Chrome Web Store installs.
- **Anti-detection** — Uses nodriver (instead of Playwright/Puppeteer) to avoid setting `navigator.webdriver=true`. Blocks detectable CDP domains (`Runtime.enable`, `Console.enable`). Patches mouse event coordinates to avoid synthetic click detection. These are stealth features for bypassing bot detection on websites — not evasion of security tools on your machine.

None of these capabilities access data outside the browser or the skill's own `state/` directory. The skill does not phone home, collect telemetry, or transmit data to any third party.
