# handsfree-windows CLI reference

Invoke via: `hf ...` or `python -m handsfree_windows.cli ...`

---

## Desktop (UIA) commands

### Window management
- `list-windows [--json] [--title-regex <regex>]`
- `focus --title <exact> | --title-regex <regex> | --handle <int>`

### Discovery (no guessing)
- `tree --title/--title-regex ... --depth <n> --max-nodes <n>` (JSON)
- `list-controls --title/--title-regex ... --depth <n>` (table)
- `inspect --json` (hover element, prints selector v2)
- `resolve --selector-file <file.json> [--title-regex ...]`

### Actions
- `click --title/... --name <exact> --control-type <type>`
- `click --title/... --name-regex <regex> --control-type <type>`
- `type --title/... --text <text> [--enter]`

### Launch / navigation
- `start --app "<Start search text>"`
- `open-path --path "C:\\..." [--direct false]`

### Mouse primitives
- `click-at --title/... --x <int> --y <int>`
- `drag --title/... --start-x ... --start-y ... --end-x ... --end-y ...`
- `drag-screen --start-x ... --start-y ... --end-x ... --end-y ... [--backend pywinauto|sendinput]`
- `drag-canvas --title/... [--x1 0.15] [--y1 0.20] [--x2 0.65] [--y2 0.55] [--backend sendinput]`

### Macros
- `record --out <macro.yaml> [--window-title-regex <regex>]`
- `run <macro.yaml>`

---

## Browser (Playwright) commands

Persistent profile: `~/.handsfree-windows/browser-profiles/<engine>/`
State file: `~/.handsfree-windows/browser-state.json`

### Session management
- `browser-open --url <url> [--browser chromium|firefox|webkit] [--headless]`
- `browser-navigate --url <url>`

### Inspection
- `browser-snapshot [--fmt aria|text]`
- `browser-links`
- `browser-eval --js "<javascript expression>"`

### Actions
- `browser-click [--selector <css>] [--text <visible text>] [--exact]`
- `browser-type --selector <css> --text <text> [--no-clear]`

### Output
- `browser-screenshot --out <file.png> [--full-page]`

---

## UIA Selector schema (v2)

```json
{
  "window": {"title": "...", "handle": 123, "pid": 999},
  "targets": [
    {"auto_id": "...", "control_type": "Button"},
    {"name": "OK", "control_type": "Button"},
    {"path": [{"control_type": "Pane", "name": "...", "index": 2}]}
  ]
}
```

Resolution strategy: try `targets[]` in order until one resolves.

---

## Macro YAML reference

Supported action types:
- `focus` - focus a window
- `start` - launch via Start menu
- `click` - UIA click
- `type` - UIA type
- `sleep` - pause
- `browser-open` - open URL in Playwright
- `browser-navigate` - navigate to URL
- `browser-click` - web click
- `browser-type` - web type
- `browser-eval` - evaluate JS

Example mixed macro:
```yaml
- action: start
  args:
    app: "Notepad"

- action: focus
  args:
    title_regex: "Notepad"

- action: type
  args:
    control: "Edit"
    text: "Hello from handsfree-windows!"

- action: browser-open
  args:
    url: "https://example.com"
    headless: false

- action: browser-click
  args:
    text: "More information..."

- action: sleep
  args:
    seconds: 1
```
