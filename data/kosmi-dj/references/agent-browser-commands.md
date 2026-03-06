# agent-browser CLI Command Reference

Complete reference for the `agent-browser` CLI used by the Kosmi DJ skill. agent-browser wraps a persistent Chromium instance and exposes browser automation through accessibility-tree snapshots rather than fragile CSS selectors.

## Installation

```bash
npm install -g agent-browser
```

Requires Node.js 18+ and a Chromium-compatible environment.

## Core Commands

### open

Navigate to a URL.

```bash
agent-browser open "https://app.kosmi.io/room/XXXXX"
```

- Opens the URL in the managed browser instance
- Creates a new browser if none exists for the current session
- Waits for initial page load before returning

### snapshot

Capture the current page's accessibility tree as JSON.

```bash
# Full snapshot (all elements)
agent-browser snapshot --json

# Interactive elements only (recommended for automation)
agent-browser snapshot -i --json

# Interactive + cursor-interactive elements
agent-browser snapshot -i -C --json
```

**Flags:**

| Flag | Description |
|---|---|
| `--json` | Output as JSON (required for programmatic use) |
| `-i` | Interactive elements only (buttons, textboxes, links, etc.) |
| `-C` | Include cursor-interactive elements (hoverable items) |

**Output structure:**

```json
{
  "success": true,
  "data": {
    "refs": {
      "ref123": { "role": "button", "name": "Play" },
      "ref456": { "role": "textbox", "name": "Enter URL" },
      "ref789": { "role": "link", "name": "Settings" }
    }
  }
}
```

### click

Click an element by its ref ID.

```bash
agent-browser click @ref123
```

- The `@` prefix is required
- Ref IDs come from snapshot output
- Waits for the click to complete before returning

### fill

Fill a textbox with text.

```bash
agent-browser fill @ref456 "https://youtube.com/watch?v=xxx"
```

- Clears existing content before filling
- Triggers input/change events
- Works on `<input>`, `<textarea>`, and contenteditable elements

### press

Press a keyboard key.

```bash
agent-browser press Enter
agent-browser press Tab
agent-browser press Escape
agent-browser press "Control+a"
```

**Common keys:** Enter, Tab, Escape, Backspace, Delete, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Space, Control+a, Control+c, Control+v

### wait

Pause execution for a specified duration.

```bash
agent-browser wait 1000    # Wait 1 second
agent-browser wait 500     # Wait 500ms
```

- Duration in milliseconds
- Use after navigation or clicks to let the page settle
- Typical values: 300-500ms after clicks, 1000-2000ms after navigation

## Session Management

### Session persistence

Set via environment variable:

```bash
export AGENT_BROWSER_SESSION_NAME=kosmi-dj-session
```

- Persists cookies, localStorage, sessionStorage between runs
- The browser profile is stored on disk and reloaded on next launch
- Avoids re-login on every invocation

### Session encryption

```bash
export AGENT_BROWSER_ENCRYPTION_KEY=<64-char-hex-string>
```

- Encrypts stored session data at rest
- Generate a key: `openssl rand -hex 32`

### Session commands

```bash
# List sessions
agent-browser session list

# Delete a session (forces re-login)
agent-browser session delete kosmi-dj-session
```

## Automation Patterns

### Finding Elements by Role and Name

The snapshot `refs` map contains `{ role, name }` for each element. Match elements using:

1. **Exact role match** — `button`, `textbox`, `link`, `progressbar`, `video`, etc.
2. **Name substring match** — Case-insensitive substring of the element's accessible name

```bash
# In bash, parse with jq:
SNAP="$(agent-browser snapshot -i -C --json)"

# Find a button containing "play" in its name
echo "$SNAP" | jq -r '
  .data.refs | to_entries[]
  | select(.value.role == "button")
  | select((.value.name // "") | ascii_downcase | contains("play"))
  | "@\(.key)"
' | head -n1
```

### Waiting for Elements

Elements may not appear immediately after navigation or clicks. Pattern:

```bash
MAX_RETRIES=5
for i in $(seq 1 $MAX_RETRIES); do
  SNAP="$(agent-browser snapshot -i -C --json)"
  REF="$(find_ref "$SNAP" "button" "play")"
  if [[ -n "$REF" ]]; then
    break
  fi
  agent-browser wait 1000
done
```

### Modal Interaction

Modals (dialogs, popups) appear as new elements in the snapshot. After triggering a modal:

1. Wait 500-800ms for animation
2. Take a new snapshot
3. Find elements within the modal
4. Interact normally

### Form Submission

```bash
# Fill form fields
agent-browser fill @emailRef "user@example.com"
agent-browser wait 200
agent-browser fill @passwordRef "secret"
agent-browser wait 200

# Submit via button click OR Enter key
agent-browser click @submitBtn
# OR
agent-browser press Enter
```

## Timeouts

Most commands accept a timeout parameter in scripts via the shell `timeout` command:

```bash
timeout 60 agent-browser open "https://app.kosmi.io/room/XXX"
```

Default internal timeouts vary by command:

| Command | Default Timeout |
|---|---|
| open | 30s |
| snapshot | 10s |
| click | 10s |
| fill | 10s |
| press | 5s |

## Troubleshooting

### "No browser instance"

The browser hasn't been started yet. Run `agent-browser open <url>` first.

### "Element not found"

The ref ID is stale (page changed since last snapshot). Take a new snapshot and find the element again.

### "Snapshot empty"

The page may still be loading. Add a `wait 2000` before retrying.

### "Session corrupted"

Delete the session and re-authenticate:

```bash
agent-browser session delete kosmi-dj-session
```

### Display issues in headless environments

If running without a display (CI, cron):

```bash
export DISPLAY=:99
Xvfb :99 -screen 0 1280x720x24 &
```

Or use agent-browser's built-in headless mode if available.
