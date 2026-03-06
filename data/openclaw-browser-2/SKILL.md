---
name: OpenClaw Native Browser
description: A stable native browser (WKWebView) for OpenClaw agents. Opens a visible window with tab management, URL bar, and login helpers — every website works, including Perplexity, Grok, Claude, and ChatGPT.
read_when:
  - Navigating web pages with a real browser
  - Interacting with authenticated web applications
  - Searching the web without API keys
  - Logging into websites (Perplexity, Grok, Claude, ChatGPT)
  - Taking screenshots of web pages
  - Managing multiple browser tabs
metadata:
  clawdbot:
    emoji: "🦞"
    requires:
      bins: ["python3", "pip"]
allowed-tools: Bash(python:*), Bash(pip:*)
---

# OpenClaw Native Browser

A real native browser (WKWebView) for OpenClaw agents. Opens a visible window with tab management, URL bar, and login helpers — every website works, including Perplexity, Grok, Claude, and ChatGPT.

**Replaces flaky relay-based browser controls with a stable native macOS browser.**

## Installation

Clone the repository and install:
```bash
git clone https://github.com/yungookim/openclaw-browser.git ~/clawd/openclaw-browser
cd ~/clawd/openclaw-browser
pip install -e .
```

Verify installation:
```bash
python -c "import sys; sys.path.insert(0, '/Users/$USER/clawd/openclaw-browser'); from src import OpenClawBrowserSkill, __version__; print(f'openclaw-browser v{__version__} ready')"
```

## Quick Start
```python
import sys
sys.path.insert(0, '/Users/<username>/clawd/openclaw-browser')
from src import OpenClawBrowserSkill

skill = OpenClawBrowserSkill()

# Load any website (native WKWebView — all sites work)
skill.load('https://perplexity.ai')

# Read page content
title = skill.get_title()
html = skill.get_dom('body')

# Execute JavaScript
result = skill.execute_js('document.title')

# Interact with page
skill.click('button.submit')
skill.type_text('input[name="query"]', 'Hello world')

# Tab management
tab_id = skill.browser.new_tab('https://example.com')
skill.browser.switch_tab(tab_id)
skill.browser.close_tab(tab_id)

# Close when done
skill.close()
```

## Why Use This?

By default, OpenClaw gateway uses the **Brave Search API** for web search, which:
- Requires a paid API key
- Only supports search (no interaction)
- Cannot log into websites
- Cannot interact with authenticated web apps

**openclaw-browser** solves this by providing:
- ✅ No API keys required
- ✅ Click, type, login, scrape
- ✅ Persistent cookies & multi-site sessions
- ✅ JavaScript execution
- ✅ Screenshot capture
- ✅ Works with Perplexity, Claude, ChatGPT, Grok

### Disable Built-in Web Tools (Recommended)

To avoid `missing_brave_api_key` errors and ensure OpenClaw routes web tasks through openclaw-browser, disable the built-in web tools:

Edit `~/.openclaw/openclaw.json`:
```json
{
  "tools": {
    "web": {
      "search": {
        "enabled": false
      },
      "fetch": {
        "enabled": false
      }
    }
  }
}
```

Or run:
```bash
openclaw configure --section tools
```

and disable both `web.search` and `web.fetch`.

## What It Does

- **Native WKWebView** — real macOS browser engine, every website works (no headless quirks)
- **Two-window architecture** — frameless toolbar (tab bar + URL bar) + native content windows per tab
- **Singleton browser** — one instance, reused across calls, with tab management
- **Login helpers** — built-in flows for Perplexity, Grok, Claude, ChatGPT
- **Subprocess isolation** — browser runs in a child process so it never blocks your agent

## Architecture
```
OpenClaw Agent
│
▼
OpenClawBrowserSkill (skill_wrapper.py)
│ - lazy init, login helpers, convenience methods
▼
NativeBrowser (browser_engine.py, singleton)
│ - IPC over stdin/stdout JSON
▼
Child Process (pywebview main thread)
├── Toolbar Window (frameless, always-on-top, chrome_ui.py)
│   ├── Tab bar
│   ├── URL bar
│   └── nav buttons
└── Content Windows (one native WKWebView per tab)
    ├── load_url()
    ├── execute_js()
    └── get_dom()
```

## API Reference

### Navigation & Page Interaction

| Method | Description |
|--------|-------------|
| `skill.load(url, wait=2.0)` | Load URL in active tab |
| `skill.execute_js(code)` | Run JavaScript, return result |
| `skill.get_dom(selector)` | Get innerHTML of element |
| `skill.get_title()` | Get page title |
| `skill.get_url()` | Get current URL |
| `skill.snapshot()` | Full page HTML + metadata dict |

### Interactions

| Method | Description |
|--------|-------------|
| `skill.click(selector, wait=1.0)` | Click element |
| `skill.type_text(selector, text)` | Type into input |
| `skill.wait_for_element(selector, timeout=10)` | Wait for element to appear |
| `skill.scroll_to_bottom()` | Scroll to page bottom |
| `skill.scroll_to_element(selector)` | Scroll element into view |

### Cookies & Session

| Method | Description |
|--------|-------------|
| `skill.get_cookies()` | Get all cookies |
| `skill.set_cookie(name, value)` | Set a cookie |

### Login Helpers

| Method | Description |
|--------|-------------|
| `skill.login_perplexity(email, pw)` | Login to Perplexity.ai |
| `skill.login_grok(user, pw)` | Login to Grok (X.com) |
| `skill.login_claude(email, pw)` | Login to Claude.ai |
| `skill.login_chatgpt(email, pw)` | Login to ChatGPT |

### Tab Management

| Method | Description |
|--------|-------------|
| `skill.browser.new_tab(url)` | Open new tab |
| `skill.browser.switch_tab(id)` | Switch to tab |
| `skill.browser.close_tab(id)` | Close tab |
| `skill.browser.get_tabs()` | List all tabs |

### Close

| Method | Description |
|--------|-------------|
| `skill.close()` | Close browser |

## Examples

### Example: Load and Read a Page
```python
from src import OpenClawBrowserSkill

skill = OpenClawBrowserSkill()
skill.load('https://example.com')

# Get page content
title = skill.get_title()
print(f"Page title: {title}")

# Execute JavaScript
result = skill.execute_js('document.querySelector("h1").textContent')
print(f"H1 text: {result}")

skill.close()
```

### Example: Fill a Form
```python
from src import OpenClawBrowserSkill

skill = OpenClawBrowserSkill()
skill.load('https://example.com/contact')

# Wait for form to load
skill.wait_for_element('input[name="email"]')

# Fill form
skill.type_text('input[name="email"]', 'user@example.com')
skill.type_text('textarea[name="message"]', 'Hello from OpenClaw!')
skill.click('button[type="submit"]')

# Wait for confirmation
skill.wait_for_element('.success-message')

skill.close()
```

### Example: Login to Perplexity
```python
from src import OpenClawBrowserSkill

skill = OpenClawBrowserSkill()

# Built-in login helper
skill.login_perplexity('your-email@example.com', 'your-password')

# Now you can use Perplexity
skill.load('https://perplexity.ai')
skill.type_text('textarea[placeholder="Ask anything..."]', 'What is quantum computing?')
skill.click('button[aria-label="Submit"]')

skill.close()
```

### Example: Multi-Tab Workflow
```python
from src import OpenClawBrowserSkill

skill = OpenClawBrowserSkill()

# Open multiple tabs
tab1 = skill.browser.new_tab('https://github.com')
tab2 = skill.browser.new_tab('https://stackoverflow.com')

# Switch between tabs
skill.browser.switch_tab(tab1)
title1 = skill.get_title()

skill.browser.switch_tab(tab2)
title2 = skill.get_title()

print(f"Tab 1: {title1}, Tab 2: {title2}")

# Close individual tabs
skill.browser.close_tab(tab1)
skill.browser.close_tab(tab2)

skill.close()
```

## Requirements

- macOS 10.14+ (Mojave or later)
- Python 3.12+
- pywebview >= 5.1 (the only dependency)

## Important Notes

- **The browser is a singleton** — calling `OpenClawBrowserSkill()` again reuses the same window. Use `new_tab()` for additional pages.
- **Subprocess isolation** — the browser runs in a child process, so it never blocks your agent.
- **CSS selectors** — all interaction methods use CSS selectors (e.g., `'button.submit'`, `'input[name="email"]'`)
- **Cookies persist** — login sessions are maintained across skill invocations

## Testing

Run the test suite:
```bash
# GUI test suite (9 tests, needs display)
python test_gui_browser.py

# pytest suite
pytest tests/ -v
```

## Troubleshooting

- **Browser doesn't appear**: Make sure you're running on macOS 10.14+
- **Element not found**: Use `execute_js()` to inspect the page structure
- **Login fails**: Check credentials and website changes
- **Performance issues**: The browser is a native app, so it should be fast. If slow, check system resources.

## Reporting Issues

Open an issue at: https://github.com/yungookim/openclaw-browser

## License

MIT — see LICENSE
