---
name: stealthy-auto-browse
description: Browser automation that passes CreepJS, BrowserScan, Pixelscan, and Cloudflare — zero CDP exposure, OS-level input, persistent fingerprints. Use when standard browser skills get 403s or CAPTCHAs.
homepage: https://github.com/psyb0t/docker-stealthy-auto-browse
user-invocable: true
metadata:
  { "openclaw": { "emoji": "🕵️", "primaryEnv": "STEALTHY_AUTO_BROWSE_URL", "requires": { "bins": ["docker", "curl"] } } }
---

# stealthy-auto-browse

A stealth browser running in Docker. It uses Camoufox (a custom Firefox fork) instead of Chromium, so there are zero Chrome DevTools Protocol (CDP) signals for bot detectors to find. Mouse and keyboard input happens at the OS level via PyAutoGUI — the browser itself doesn't know it's being automated, which means behavioral analysis can't detect it either.

## Why This Exists

Standard browser automation (Playwright + Chromium, Puppeteer, Selenium) exposes CDP signals that bot detection services (Cloudflare, DataDome, PerimeterX, Akamai) catch instantly. Even with stealth plugins, the CDP protocol is still there and detectable. This skill eliminates that entirely by using Firefox (no CDP at all) and generating input events at the OS level rather than through the browser's automation API.

## When To Use This Skill

- Site has bot detection (Cloudflare challenge pages, DataDome, PerimeterX, Akamai)
- Site blocks headless browsers or serves CAPTCHAs
- You need a logged-in session that doesn't get banned
- Another browser skill is getting 403s or empty/blocked responses
- You're scraping a site that actively fights automation

## When NOT To Use This Skill

- Simple fetches with no bot protection — use `curl` or `WebFetch`
- Sites that don't care about automation — use a regular browser skill, it's faster to set up
- You only need static HTML — use `curl`

## Setup

**1. Start the container:**

```bash
docker run -d -p 8080:8080 -p 5900:5900 psyb0t/stealthy-auto-browse
```

Port 8080 is the HTTP API. Port 5900 is a noVNC web viewer where you can watch the browser in real time.

**2. Set the environment variable:**

```bash
export STEALTHY_AUTO_BROWSE_URL=http://localhost:8080
```

Or via OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "stealthy-auto-browse": {
        "env": {
          "STEALTHY_AUTO_BROWSE_URL": "http://localhost:8080"
        }
      }
    }
  }
}
```

**3. Verify:** `curl $STEALTHY_AUTO_BROWSE_URL/health` returns `ok` when the browser is ready.

## How It Works

The container runs a virtual X display (Xvfb at 1920x1080), the Camoufox browser, and an HTTP API server. You send JSON commands to the API and get JSON responses back. All commands go to `POST $STEALTHY_AUTO_BROWSE_URL/` with `{"action": "<name>", ...params}`.

Every response has this shape:

```json
{
  "success": true,
  "timestamp": 1234567890.123,
  "data": { ... },
  "error": "only present when success is false"
}
```

The `data` field contents vary by action — documented below for each one.

## Understanding the Two Input Modes

This is the most important concept. There are two ways to interact with pages:

### System Input (Undetectable)

Actions: `system_click`, `mouse_move`, `mouse_click`, `system_type`, `send_key`, `scroll`

These use PyAutoGUI to generate real OS-level mouse movements and keystrokes. The browser receives these as genuine user input — there is no way for any website JavaScript to distinguish these from a real human. **Use these for stealth.**

System input works with **viewport coordinates** (x, y pixel positions within the browser content area). Get these coordinates from `get_interactive_elements`.

### Playwright Input (Detectable)

Actions: `click`, `fill`, `type`

These use Playwright's DOM automation to interact with elements by CSS selector or XPath. They're faster and more reliable (no coordinate math), but they inject events through the browser's automation layer. Sophisticated behavioral analysis can potentially detect the timing patterns. **Use these when speed matters more than stealth, or when you have a selector but no coordinates.**

### When to Use Which

- **Stealth-critical sites** (Cloudflare, login forms, anything with bot detection): Always use system input.
- **Simple scraping** where the site isn't actively fighting you: Playwright input is fine and easier.
- **Form filling**: Use `system_click` to focus the field, then `system_type` to enter text. This is undetectable. Using `fill` is faster but detectable.
- **Clicking buttons**: If you have coordinates from `get_interactive_elements`, use `system_click`. If you only have a CSS selector, use `click`.

## Workflow

This is the typical sequence for interacting with a page:

1. **Navigate**: `goto` to load the URL
2. **Read the page**: `get_text` returns all visible text — usually enough to understand the page
3. **If text isn't clear**: `get_html` gives you the full DOM structure
4. **If still confused**: Take a screenshot (`GET /screenshot/browser?whLargest=512`)
5. **Find interactive elements**: `get_interactive_elements` returns all buttons, links, inputs with their x,y coordinates
6. **Interact**: `system_click` to click, `system_type` to type, `send_key` for Enter/Tab/Escape
7. **Wait for results**: `wait_for_element` or `wait_for_text` instead of sleeping
8. **Verify**: `get_text` again to confirm the page changed as expected

## Actions Reference

### Navigation

#### goto

Navigates to a URL. This is how you load pages.

```json
{"action": "goto", "url": "https://example.com"}
{"action": "goto", "url": "https://example.com", "wait_until": "networkidle"}
```

**Parameters:**
- `url` (required): The URL to navigate to.
- `wait_until` (optional, default `"domcontentloaded"`): When to consider the page loaded. Options: `"domcontentloaded"` (DOM parsed, fast), `"load"` (all resources loaded), `"networkidle"` (no network activity for 500ms, slowest but most complete).

**Response data:** `{"url": "https://example.com/", "title": "Example Domain"}`

**Note:** If a page loader matches the URL (see Page Loaders section), the loader's steps execute instead of the default navigation. The response will include `"loader": "loader name"` when this happens.

#### refresh

Reloads the current page.

```json
{"action": "refresh"}
{"action": "refresh", "wait_until": "networkidle"}
```

**Parameters:**
- `wait_until` (optional, default `"domcontentloaded"`): Same options as `goto`.

**Response data:** `{"url": "https://example.com/current-page", "title": "Current Page"}`

### System Input (Undetectable)

#### system_click

Moves the mouse to viewport coordinates with a human-like curve (random jitter, eased acceleration), then clicks. This is the primary way to click things stealthily.

```json
{"action": "system_click", "x": 500, "y": 300}
{"action": "system_click", "x": 500, "y": 300, "duration": 0.5}
```

**Parameters:**
- `x`, `y` (required): Viewport coordinates — get these from `get_interactive_elements`.
- `duration` (optional): How long the mouse movement takes in seconds. If omitted, a random duration between 0.2-0.6s is used for realism.

**Response data:** `{"system_clicked": {"x": 500, "y": 300}}`

**How it differs from `mouse_click`:** `system_click` always moves the mouse first (smooth human-like path), then clicks. `mouse_click` can click at a position instantly without the smooth movement, or click wherever the mouse currently is.

#### mouse_move

Moves the mouse to viewport coordinates with human-like movement (jitter, eased curve) but does NOT click. Use this to hover over elements (to trigger hover menus, tooltips) or to simulate natural mouse behavior between actions.

```json
{"action": "mouse_move", "x": 500, "y": 300}
{"action": "mouse_move", "x": 500, "y": 300, "duration": 0.4}
```

**Parameters:**
- `x`, `y` (required): Viewport coordinates.
- `duration` (optional): Movement time in seconds. Random 0.2-0.6s if omitted.

**Response data:** `{"moved_to": {"x": 500, "y": 300}}`

#### mouse_click

Clicks at a position or at the current mouse location. Unlike `system_click`, this does NOT do a smooth mouse movement first — it's a direct click via PyAutoGUI.

```json
{"action": "mouse_click"}
{"action": "mouse_click", "x": 500, "y": 300}
```

**Parameters:**
- `x`, `y` (optional): If provided, clicks at that viewport position directly. If omitted, clicks wherever the mouse currently is.

**Response data:** `{"clicked_at": {"x": 500, "y": 300}}` or `{"clicked_at": "current"}`

**When to use:** After a `mouse_move` when you want to separate the movement and click into two steps. Or when the mouse is already positioned and you just need to click.

#### system_type

Types text character-by-character via real OS keystrokes. Each keystroke has a randomized delay (jittered around the interval) to mimic human typing speed. Completely undetectable.

```json
{"action": "system_type", "text": "hello world"}
{"action": "system_type", "text": "hello world", "interval": 0.12}
```

**Parameters:**
- `text` (required): The text to type. Must click/focus an input field first.
- `interval` (optional, default `0.08`): Base delay between keystrokes in seconds. Actual delay is randomized +-30ms around this value.

**Response data:** `{"typed_len": 11}`

**Important:** You must click on the input field first (using `system_click` or `click`) before calling `system_type`. This action types into whatever is currently focused.

#### send_key

Sends a single keyboard key or key combination via OS-level input. Use this for pressing Enter to submit forms, Tab to move between fields, Escape to close dialogs, or any key combos like Ctrl+A, Ctrl+C, etc.

```json
{"action": "send_key", "key": "enter"}
{"action": "send_key", "key": "tab"}
{"action": "send_key", "key": "escape"}
{"action": "send_key", "key": "ctrl+a"}
{"action": "send_key", "key": "ctrl+shift+t"}
```

**Parameters:**
- `key` (required): Key name or combo with `+` separator. Key names follow PyAutoGUI naming: `enter`, `tab`, `escape`, `backspace`, `delete`, `up`, `down`, `left`, `right`, `home`, `end`, `pageup`, `pagedown`, `f1`-`f12`, `ctrl`, `alt`, `shift`, `space`, etc.

**Response data:** `{"send_key": "enter"}`

#### scroll

Scrolls the page using the mouse scroll wheel. Generates real OS-level scroll events.

```json
{"action": "scroll", "amount": -3}
{"action": "scroll", "amount": 5, "x": 500, "y": 300}
```

**Parameters:**
- `amount` (optional, default `-3`): Scroll amount. **Negative = scroll down**, positive = scroll up. Each unit is roughly one "click" of a mouse wheel.
- `x`, `y` (optional): If provided, moves the mouse to these viewport coordinates first, then scrolls. Useful for scrolling inside a specific scrollable element rather than the whole page.

**Response data:** `{"scrolled": -3}`

### Playwright Input (Detectable)

These are faster and more convenient but use Playwright's DOM event injection, which is detectable by sophisticated behavioral analysis.

#### click

Clicks an element by CSS selector or XPath. Playwright finds the element in the DOM, scrolls it into view if needed, and dispatches click events.

```json
{"action": "click", "selector": "#submit-btn"}
{"action": "click", "selector": "button.primary"}
{"action": "click", "selector": "xpath=//button[@id='submit-btn']"}
```

**Parameters:**
- `selector` (required): CSS selector or XPath (prefix with `xpath=`).

**Response data:** `{"clicked": "#submit-btn"}`

**When to use over system_click:** When you have a selector but don't want to bother getting coordinates. When the element might move around and coordinates aren't reliable. When stealth isn't critical.

#### fill

Fills an input field by selector. Clears any existing content first, then sets the value. This is the fastest way to fill forms but is detectable because it doesn't generate individual keystroke events.

```json
{"action": "fill", "selector": "input[name='email']", "value": "user@example.com"}
```

**Parameters:**
- `selector` (required): CSS selector or XPath of the input element.
- `value` (required): Text to fill in.

**Response data:** `{"filled": "input[name='email']"}`

#### type

Types text into an element character-by-character via Playwright (NOT the OS). Each keystroke has a configurable delay. This is a middle ground between `fill` (instant but obviously automated) and `system_type` (OS-level, undetectable). The typing pattern is more realistic than `fill` but still comes through Playwright's event system.

```json
{"action": "type", "selector": "#search", "text": "query", "delay": 0.05}
```

**Parameters:**
- `selector` (required): CSS selector or XPath of the element.
- `text` (required): Text to type.
- `delay` (optional, default `0.05`): Delay between keystrokes in seconds.

**Response data:** `{"typed": "#search"}`

### Screenshots

Screenshots are GET requests (not POST actions).

#### GET /screenshot/browser

Captures the browser viewport as a PNG image. This is what the page looks like to a user.

```bash
curl -s "$STEALTHY_AUTO_BROWSE_URL/screenshot/browser?whLargest=512" -o screenshot.png
```

**Always resize screenshots** to avoid huge images. Resize query parameters (all optional):

| Parameter | What it does |
|-----------|-------------|
| `whLargest=512` | Scales so the largest dimension is 512px, keeps aspect ratio. **Use this by default.** |
| `width=800` | Scales to 800px wide, keeps aspect ratio |
| `height=300` | Scales to 300px tall, keeps aspect ratio |
| `width=400&height=400` | Forces exact 400x400 dimensions |

#### GET /screenshot/desktop

Captures the entire virtual desktop (including window chrome, taskbar, etc.) using `scrot`. Same resize parameters as above. Useful when you need to see things outside the browser viewport.

```bash
curl -s "$STEALTHY_AUTO_BROWSE_URL/screenshot/desktop?whLargest=512" -o desktop.png
```

### Page Inspection

#### get_interactive_elements

Scans the page and returns every interactive element (buttons, links, inputs, selects, textareas, etc.) with their viewport coordinates. This is how you find what to click and where.

```json
{"action": "get_interactive_elements"}
{"action": "get_interactive_elements", "visible_only": true}
```

**Parameters:**
- `visible_only` (optional, default `true`): Only return elements that are currently visible on screen.

**Response data:**
```json
{
  "count": 5,
  "elements": [
    {
      "i": 0,
      "tag": "button",
      "id": "submit-btn",
      "text": "Submit",
      "selector": "#submit-btn",
      "x": 400,
      "y": 250,
      "w": 120,
      "h": 40,
      "visible": true
    },
    {
      "i": 1,
      "tag": "input",
      "id": null,
      "text": "",
      "selector": "input[name='email']",
      "x": 300,
      "y": 180,
      "w": 250,
      "h": 35,
      "visible": true
    }
  ]
}
```

The `x`, `y` are the center of the element — pass these directly to `system_click`. The `selector` can be used with Playwright actions like `click` or `fill`. The `w`, `h` give you the element dimensions.

**This is your primary tool for understanding what you can interact with on a page.** Call this before clicking anything.

#### get_text

Returns all visible text content of the page body. Text is truncated to 10,000 characters.

```json
{"action": "get_text"}
```

**Response data:** `{"text": "Page title\nSome content here...", "length": 1234}`

This is usually the first thing to call after navigating — it tells you what's on the page without needing a screenshot.

#### get_html

Returns the full HTML source of the current page.

```json
{"action": "get_html"}
```

**Response data:** `{"html": "<!DOCTYPE html>...", "length": 45678}`

Use when `get_text` doesn't give enough structure to understand the page layout, or when you need to find specific elements in the DOM.

#### eval

Executes arbitrary JavaScript in the page context and returns the result. The expression is evaluated via `page.evaluate()`.

```json
{"action": "eval", "expression": "document.title"}
{"action": "eval", "expression": "document.querySelectorAll('a').length"}
{"action": "eval", "expression": "JSON.stringify(performance.timing)"}
```

**Parameters:**
- `expression` (required): JavaScript expression to evaluate. Must return a JSON-serializable value.

**Response data:** `{"result": "Example Domain"}` — the result is whatever the expression returns.

### Wait Conditions

Use these instead of `sleep` to wait for page content. They're more reliable because they wait for the exact condition rather than an arbitrary time.

#### wait_for_element

Waits for an element matching a CSS selector or XPath to reach a certain state (visible, hidden, attached to DOM, detached).

```json
{"action": "wait_for_element", "selector": "#results", "timeout": 10}
{"action": "wait_for_element", "selector": "xpath=//div[@class='loaded']", "timeout": 15}
{"action": "wait_for_element", "selector": ".spinner", "state": "hidden", "timeout": 10}
```

**Parameters:**
- `selector` (required): CSS selector or XPath (prefix with `xpath=`).
- `state` (optional, default `"visible"`): What state to wait for. Options: `"visible"` (rendered and not hidden), `"hidden"` (not visible), `"attached"` (in DOM regardless of visibility), `"detached"` (removed from DOM).
- `timeout` (optional, default `30`): Max wait time in seconds. Throws error if exceeded.

**Response data:** `{"selector": "#results", "state": "visible"}`

#### wait_for_text

Waits for specific text to appear anywhere in the page body.

```json
{"action": "wait_for_text", "text": "Search results", "timeout": 10}
```

**Parameters:**
- `text` (required): Exact text to look for (substring match on `document.body.innerText`).
- `timeout` (optional, default `30`): Max wait time in seconds.

**Response data:** `{"text": "Search results", "found": true}`

#### wait_for_url

Waits for the page URL to match a pattern. Useful after form submissions or redirects.

```json
{"action": "wait_for_url", "url": "**/dashboard", "timeout": 10}
{"action": "wait_for_url", "url": "https://example.com/success*", "timeout": 15}
```

**Parameters:**
- `url` (required): URL pattern to match. Supports `*` (any chars except `/`) and `**` (any chars including `/`) glob patterns. Can also be a full URL for exact match.
- `timeout` (optional, default `30`): Max wait time in seconds.

**Response data:** `{"url": "https://example.com/dashboard"}`

#### wait_for_network_idle

Waits until there are no network requests in flight for 500ms. Useful for pages that load content dynamically after the initial page load.

```json
{"action": "wait_for_network_idle", "timeout": 30}
```

**Parameters:**
- `timeout` (optional, default `30`): Max wait time in seconds.

**Response data:** `{"idle": true}`

### Tab Management

The browser can have multiple tabs open. One tab is "active" at a time — all actions operate on the active tab.

#### list_tabs

Returns all open tabs with their URLs and which one is active.

```json
{"action": "list_tabs"}
```

**Response data:**
```json
{
  "count": 2,
  "tabs": [
    {"index": 0, "url": "https://example.com/", "active": false},
    {"index": 1, "url": "https://other.com/", "active": true}
  ]
}
```

#### new_tab

Opens a new browser tab. Optionally navigates it to a URL. The new tab becomes the active tab.

```json
{"action": "new_tab"}
{"action": "new_tab", "url": "https://example.com"}
```

**Parameters:**
- `url` (optional): URL to navigate to in the new tab.
- `wait_until` (optional, default `"domcontentloaded"`): Same as `goto`.

**Response data:** `{"index": 1, "url": "https://example.com/"}`

#### switch_tab

Switches the active tab by index (0-based). All subsequent actions will operate on this tab.

```json
{"action": "switch_tab", "index": 0}
```

**Parameters:**
- `index` (required): Tab index from `list_tabs`.

**Response data:** `{"index": 0, "url": "https://example.com/"}`

#### close_tab

Closes a tab. After closing, the last remaining tab becomes active.

```json
{"action": "close_tab"}
{"action": "close_tab", "index": 1}
```

**Parameters:**
- `index` (optional): Tab index to close. If omitted, closes the currently active tab.

**Response data:** `{"closed": true, "remaining": 1}`

### Dialog Handling

Browsers have modal dialogs (alert, confirm, prompt). By default, dialogs are auto-accepted (clicks OK). Use `handle_dialog` if you need to dismiss a dialog or provide text for a prompt.

#### handle_dialog

**Call BEFORE the action that triggers the dialog** if you want to dismiss it or provide prompt text. If you don't call this, the dialog is auto-accepted (clicks OK).

```json
{"action": "handle_dialog", "accept": true}
{"action": "handle_dialog", "accept": false}
{"action": "handle_dialog", "accept": true, "text": "my response"}
```

**Parameters:**
- `accept` (optional, default `true`): `true` clicks OK/Accept, `false` clicks Cancel/Dismiss.
- `text` (optional): Response text for prompt dialogs. Ignored for alert/confirm.

**Response data:** `{"configured": {"accept": true, "text": null}}`

**Example — handling a confirm dialog:**
```bash
# Step 1: Tell the browser to accept the next dialog
curl -X POST $API -H 'Content-Type: application/json' -d '{"action": "handle_dialog", "accept": true}'
# Step 2: Now click the button that triggers the confirm
curl -X POST $API -H 'Content-Type: application/json' -d '{"action": "system_click", "x": 300, "y": 200}'
```

#### get_last_dialog

Returns information about the most recent dialog that appeared.

```json
{"action": "get_last_dialog"}
```

**Response data:**
```json
{
  "dialog": {
    "type": "confirm",
    "message": "Are you sure you want to delete this?",
    "default_value": "",
    "buttons": ["ok", "cancel"]
  }
}
```

Returns `{"dialog": null}` if no dialog has appeared yet. The `type` field is one of: `"alert"`, `"confirm"`, `"prompt"`, `"beforeunload"`.

### Cookies

#### get_cookies

Returns all cookies for the browser context, or cookies for specific URLs.

```json
{"action": "get_cookies"}
{"action": "get_cookies", "urls": ["https://example.com"]}
```

**Parameters:**
- `urls` (optional): Array of URLs to filter cookies by. If omitted, returns all cookies.

**Response data:**
```json
{
  "count": 3,
  "cookies": [
    {"name": "session", "value": "abc123", "domain": ".example.com", "path": "/", "httpOnly": true, "secure": true, ...}
  ]
}
```

#### set_cookie

Sets a cookie in the browser context.

```json
{"action": "set_cookie", "name": "session", "value": "abc123", "url": "https://example.com"}
{"action": "set_cookie", "name": "pref", "value": "dark", "domain": ".example.com", "path": "/", "httpOnly": false, "secure": true}
```

**Parameters:** Any standard cookie fields — `name`, `value`, `url`, `domain`, `path`, `httpOnly`, `secure`, `sameSite`, `expires`. At minimum you need `name`, `value`, and either `url` or `domain`.

**Response data:** `{"set": "session"}`

#### delete_cookies

Clears all cookies from the browser context.

```json
{"action": "delete_cookies"}
```

**Response data:** `{"cleared": true}`

### Storage

Access the page's localStorage and sessionStorage. These are per-origin — you must be on the right page for the storage to be accessible.

#### get_storage

Returns all items from localStorage or sessionStorage as a key-value object.

```json
{"action": "get_storage", "type": "local"}
{"action": "get_storage", "type": "session"}
```

**Parameters:**
- `type` (optional, default `"local"`): `"local"` for localStorage, `"session"` for sessionStorage.

**Response data:** `{"items": {"theme": "dark", "lang": "en"}, "type": "local"}`

#### set_storage

Sets a single key-value pair in localStorage or sessionStorage.

```json
{"action": "set_storage", "type": "local", "key": "theme", "value": "dark"}
```

**Parameters:**
- `type` (optional, default `"local"`): `"local"` or `"session"`.
- `key` (required): Storage key.
- `value` (required): Storage value (string).

**Response data:** `{"set": "theme", "type": "local"}`

#### clear_storage

Clears all items from localStorage or sessionStorage.

```json
{"action": "clear_storage", "type": "local"}
{"action": "clear_storage", "type": "session"}
```

**Response data:** `{"cleared": "local"}`

### Downloads

The browser automatically tracks file downloads triggered by page interactions (clicking download links, form submissions that return files, etc.).

#### get_last_download

Returns information about the most recently downloaded file.

```json
{"action": "get_last_download"}
```

**Response data:**
```json
{
  "download": {
    "url": "https://example.com/file.pdf",
    "filename": "file.pdf",
    "path": "/tmp/playwright-downloads/abc123/file.pdf"
  }
}
```

Returns `{"download": null}` if nothing has been downloaded yet. The `path` is the local path inside the container where the file was saved. The `filename` is what the server suggested as the download name.

### Uploads

#### upload_file

Programmatically sets a file on an `<input type="file">` element without opening the OS file picker. The file must exist inside the container — use `docker cp` to copy files in if needed.

```json
{"action": "upload_file", "selector": "#file-input", "file_path": "/tmp/document.pdf"}
```

**Parameters:**
- `selector` (required): CSS selector of the file input element.
- `file_path` (required): Absolute path to the file inside the container.

**Response data:** `{"selector": "#file-input", "file": "document.pdf", "size": 12345}`

**Note:** After setting the file, you still need to submit the form (click the submit button) for the upload to actually happen.

### Network Logging

Capture all HTTP requests and responses the page makes. Useful for debugging, finding API endpoints the page calls, or verifying that certain resources loaded.

#### enable_network_log

Starts recording all HTTP requests and responses from the active page.

```json
{"action": "enable_network_log"}
```

**Response data:** `{"enabled": true}`

#### disable_network_log

Stops recording network activity. Already-captured entries remain.

```json
{"action": "disable_network_log"}
```

**Response data:** `{"enabled": false}`

#### get_network_log

Returns all captured network entries since logging was enabled (or last cleared).

```json
{"action": "get_network_log"}
```

**Response data:**
```json
{
  "count": 4,
  "log": [
    {"type": "request", "url": "https://api.example.com/data", "method": "GET", "resource_type": "fetch", "timestamp": 1234567890.123},
    {"type": "response", "url": "https://api.example.com/data", "status": 200, "timestamp": 1234567890.456},
    {"type": "request", "url": "https://cdn.example.com/style.css", "method": "GET", "resource_type": "stylesheet", "timestamp": 1234567890.789},
    {"type": "response", "url": "https://cdn.example.com/style.css", "status": 200, "timestamp": 1234567890.999}
  ]
}
```

Each entry is either a `"request"` or `"response"`. Requests include `method` and `resource_type` (fetch, document, stylesheet, script, image, etc.). Responses include `status` code.

#### clear_network_log

Deletes all captured network entries but keeps logging enabled if it was on.

```json
{"action": "clear_network_log"}
```

**Response data:** `{"cleared": true}`

### Scrolling

#### scroll_to_bottom

Scrolls the entire page from top to bottom using JavaScript `window.scrollBy()`. Scrolls one viewport height at a time with a fixed delay between scrolls. When it reaches the bottom (scroll position stops changing), it scrolls back to the top. Useful for triggering lazy-loaded content.

```json
{"action": "scroll_to_bottom"}
{"action": "scroll_to_bottom", "delay": 0.6}
```

**Parameters:**
- `delay` (optional, default `0.4`): Seconds to wait between each scroll step.

**Response data:** `{"scrolled": "bottom"}`

#### scroll_to_bottom_humanized

Same as `scroll_to_bottom` but uses real OS-level mouse wheel scrolling (via PyAutoGUI) with randomized scroll amounts and jittered delays to look like a human scrolling. Undetectable by behavioral analysis.

```json
{"action": "scroll_to_bottom_humanized"}
{"action": "scroll_to_bottom_humanized", "min_clicks": 3, "max_clicks": 8, "delay": 0.7}
```

**Parameters:**
- `min_clicks` (optional, default `2`): Minimum mouse wheel clicks per scroll step.
- `max_clicks` (optional, default `6`): Maximum mouse wheel clicks per scroll step. A random value between min and max is chosen each time.
- `delay` (optional, default `0.5`): Base delay between scroll steps. Actual delay is jittered +-30%.

**Response data:** `{"scrolled": "bottom_humanized"}`

### Display

#### calibrate

Recalculates the mapping between viewport coordinates (what `get_interactive_elements` returns) and screen coordinates (what PyAutoGUI uses). The browser has window chrome (title bar, address bar) that offsets the viewport from the screen origin.

```json
{"action": "calibrate"}
```

**Response data:** `{"window_offset": {"x": 0, "y": 74}}`

**When to call this:** After entering/exiting fullscreen, after the browser window is resized, or if `system_click` coordinates seem off. The offset is auto-calculated at startup, so you rarely need this.

#### get_resolution

Returns the virtual display resolution (from the XVFB_RESOLUTION environment variable).

```json
{"action": "get_resolution"}
```

**Response data:** `{"width": 1920, "height": 1080}`

#### enter_fullscreen / exit_fullscreen

Toggles browser fullscreen mode (hides address bar and window chrome). In fullscreen, the viewport takes up the entire screen, so coordinates map differently.

```json
{"action": "enter_fullscreen"}
{"action": "exit_fullscreen"}
```

**Response data:** `{"fullscreen": true, "changed": true}` — `changed` is `false` if already in the requested state.

**Important:** Call `calibrate` after entering/exiting fullscreen to update the coordinate mapping.

### Utility

#### ping

Health check that returns the current page URL. Use to verify the API is responding and the browser is alive.

```json
{"action": "ping"}
```

**Response data:** `{"message": "pong", "url": "https://example.com/"}`

#### sleep

Pauses execution for a specified duration. Prefer `wait_for_element` or `wait_for_text` when waiting for page content — use `sleep` only for fixed timing needs.

```json
{"action": "sleep", "duration": 2}
```

**Parameters:**
- `duration` (optional, default `1`): Seconds to sleep.

**Response data:** `{"slept": 2}`

#### close

Shuts down the browser. The container will stop after this.

```json
{"action": "close"}
```

**Response data:** `{"message": "closing"}`

### State Endpoints (GET)

#### GET /state

Returns the current browser state.

```bash
curl -s "$STEALTHY_AUTO_BROWSE_URL/state"
```

**Response:**
```json
{
  "status": "ready",
  "url": "https://example.com/",
  "title": "Example Domain",
  "window_offset": {"x": 0, "y": 74}
}
```

#### GET /health

Simple health check. Returns `ok` as plain text when the API is ready.

```bash
curl -s "$STEALTHY_AUTO_BROWSE_URL/health"
```

## Container Options

```bash
# Custom display resolution
docker run -d -p 8080:8080 -e XVFB_RESOLUTION=1280x720 psyb0t/stealthy-auto-browse

# Match timezone to your IP's geographic location (important for stealth — mismatched
# timezone is a common bot detection signal)
docker run -d -p 8080:8080 -e TZ=Europe/Bucharest psyb0t/stealthy-auto-browse

# Route browser traffic through an HTTP proxy
docker run -d -p 8080:8080 -e PROXY_URL=http://user:pass@proxy:8888 psyb0t/stealthy-auto-browse

# Persistent browser profile — cookies, sessions, and fingerprint survive container restarts
docker run -d -p 8080:8080 -v ./profile:/userdata psyb0t/stealthy-auto-browse

# Open a URL automatically on startup
docker run -d -p 8080:8080 psyb0t/stealthy-auto-browse https://example.com
```

## Page Loaders (URL-Triggered Automation)

Page loaders are like **Greasemonkey/Tampermonkey userscripts** but for the HTTP API. You define a set of actions that automatically run whenever the browser navigates to a matching URL. Instead of manually sending a sequence of commands every time you visit a site, you write it once as a YAML file and the container handles it.

This is useful for things like: removing cookie popups, dismissing overlays, waiting for dynamic content, cleaning up pages before scraping, or any repetitive setup you'd otherwise do manually every time.

### How They Work

1. You create YAML files that define URL patterns and a list of steps
2. Mount those files into the container at `/loaders`
3. Whenever `goto` navigates to a URL that matches a loader's pattern, the loader's steps run automatically instead of the default navigation

**The steps are the exact same actions as the HTTP API.** Every action you can send via `POST /` (goto, eval, click, system_click, sleep, scroll, wait_for_element, etc.) works as a loader step. Same names, same parameters.

### Setup

```bash
docker run -d -p 8080:8080 -p 5900:5900 \
  -v ./my-loaders:/loaders \
  psyb0t/stealthy-auto-browse
```

### Loader Format

```yaml
name: Human-readable name for this loader
match:
  domain: example.com         # Exact hostname match (www. is stripped automatically)
  path_prefix: /articles      # URL path must start with this
  regex: "article/\\d+"       # Full URL must match this regex
steps:
  - action: goto              # Same actions as the HTTP API
    url: "${url}"             # ${url} is replaced with the original URL
    wait_until: networkidle
  - action: eval
    expression: "document.querySelector('.cookie-banner')?.remove()"
  - action: wait_for_element
    selector: "#main-content"
    timeout: 10
```

### Match Rules

All match fields are **optional**, but at least one is required. If you specify multiple fields, **all** of them must match for the loader to trigger:

- **`domain`**: Exact hostname. `www.` is stripped from both sides before comparing, so `domain: example.com` matches `www.example.com` too.
- **`path_prefix`**: The URL path must start with this string. `path_prefix: /blog` matches `/blog`, `/blog/post-1`, `/blog/archive`, etc.
- **`regex`**: The full URL is tested against this regular expression.

### The `${url}` Placeholder

In any string value within a step, `${url}` is replaced with the original URL that was passed to `goto`. This lets you navigate to the URL with custom wait settings, or pass it to JavaScript:

```yaml
steps:
  - action: goto
    url: "${url}"
    wait_until: networkidle
  - action: eval
    expression: "console.log('Loaded:', '${url}')"
```

### Practical Example: Clean Scraping

Say you're scraping a news site that has cookie popups, newsletter modals, and lazy-loaded content. Without a loader, you'd send 5+ commands after every `goto`. With a loader:

```yaml
# loaders/news_site.yaml
name: News Site Cleanup
match:
  domain: news-site.com
steps:
  # Navigate with full network wait so everything loads
  - action: goto
    url: "${url}"
    wait_until: networkidle

  # Wait for the main content to be there
  - action: wait_for_element
    selector: "article"
    timeout: 10

  # Kill the cookie popup
  - action: eval
    expression: "document.querySelector('.cookie-consent')?.remove()"

  # Kill the newsletter modal
  - action: eval
    expression: "document.querySelector('.newsletter-overlay')?.remove()"

  # Scroll to trigger lazy-loaded images
  - action: scroll_to_bottom
    delay: 0.3

  # Small pause for everything to settle
  - action: sleep
    duration: 1
```

Now when you `goto` any URL on `news-site.com`, all of this happens automatically. Your response includes `"loader": "News Site Cleanup"` so you know it triggered.

### Response When a Loader Triggers

```json
{
  "success": true,
  "data": {
    "loader": "News Site Cleanup",
    "steps_executed": 6,
    "last_result": { "success": true, "timestamp": 1234567890.456, "data": { "slept": 1 } }
  }
}
```

## Pre-installed Extensions

The browser comes with these extensions pre-installed:

- **uBlock Origin**: Ad and tracker blocking
- **LocalCDN**: Serves common CDN resources locally to prevent tracking
- **ClearURLs**: Strips tracking parameters from URLs
- **Consent-O-Matic**: Automatically handles cookie consent popups (clicks "reject all" or minimal consent)

## Example: Full Login Flow (Undetectable)

```bash
API=$STEALTHY_AUTO_BROWSE_URL

# Navigate to login page
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "goto", "url": "https://example.com/login"}'

# See what's on the page
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "get_text"}'

# Find all interactive elements and their coordinates
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "get_interactive_elements"}'

# Click the email field (coordinates from get_interactive_elements)
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "system_click", "x": 400, "y": 200}'

# Type email with human-like keystrokes
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "system_type", "text": "user@example.com"}'

# Tab to password field
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "send_key", "key": "tab"}'

# Type password
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "system_type", "text": "secretpassword"}'

# Press Enter to submit
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "send_key", "key": "enter"}'

# Wait for redirect to dashboard
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "wait_for_url", "url": "**/dashboard", "timeout": 15}'

# Verify we're logged in
curl -s -X POST $API -H 'Content-Type: application/json' \
  -d '{"action": "get_text"}'
```

## Tips

1. **Always call `get_interactive_elements` before clicking** — don't guess coordinates
2. **Use system methods for stealth** — `system_click`, `system_type`, `send_key` are undetectable
3. **Use `get_text` first, screenshots second** — text is faster and smaller
4. **Match TZ to your IP location** — timezone mismatch is a common bot detection signal
5. **Resize screenshots with `?whLargest=512`** — full resolution is unnecessarily large
6. **Mount `/userdata`** for persistent sessions — cookies, fingerprint, and profile survive restarts
7. **Use wait conditions instead of `sleep`** — `wait_for_element`, `wait_for_text`, `wait_for_url`
8. **Call `handle_dialog` BEFORE the action that triggers it** — if you need to dismiss or provide prompt text (dialogs are auto-accepted otherwise)
9. **Call `calibrate` after fullscreen changes** — coordinate mapping shifts
10. **Add slight delays between actions for realism** — `sleep` with 0.5-1.5s between clicks looks more human
