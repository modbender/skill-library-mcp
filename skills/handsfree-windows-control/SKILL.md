---
name: handsfree-windows-control
description: "Guide skill for controlling native Windows apps (UIA) and web browsers (Playwright) via the handsfree-windows CLI. Use when you need to automate or test desktop applications or websites on a Windows machine: launching apps from Start menu, discovering UI controls without guessing, clicking/typing in native apps, opening/snapshotting/clicking in browsers, recording and replaying YAML macros that mix desktop and web steps. REQUIRES handsfree-windows CLI (auto-installed on first use via setup.py)."
---

# Handsfree Windows Control

A guide skill for automating native Windows apps (UIA) and web browsers (Playwright)
via the `handsfree-windows` CLI.

## First use: auto-setup

On first use, run setup before issuing any other commands:

```powershell
python scripts/setup.py
```

This will:
1. Clone `handsfree-windows` from GitHub into `~/.handsfree-windows/cli/` (public repo, read-only)
2. Install it via `pip install -e` (standard pip editable install)
3. Install Playwright + Chromium browser binaries (~200 MB one-time download from cdn.playwright.dev)
4. Run `check_setup.py` to verify everything is working

To skip browser installation (browser-* commands will not work):
```powershell
python scripts/setup.py --no-browser
```

To install to a custom directory:
```powershell
python scripts/setup.py --install-dir "C:\your\preferred\path"
```

Already installed? Verify anytime:
```powershell
python scripts/check_setup.py
```

### What is written to disk (transparent)
- CLI source code: `~/.handsfree-windows/cli/` (or --install-dir)
- pip editable link: standard site-packages egg-link (pip managed)
- Browser persistent profiles: `~/.handsfree-windows/browser-profiles/<engine>/`
  Contains cookies and login sessions. Delete to reset browser auth.
- Browser session state: `~/.handsfree-windows/browser-state.json` (last visited URL)
- Playwright browser binaries: `~\AppData\Local\ms-playwright\` (~800 MB, Windows)

To fully remove everything:
```powershell
pip uninstall handsfree-windows -y
Remove-Item -Recurse -Force "$env:USERPROFILE\.handsfree-windows"
```

---

## Core rules
- Do not guess UI controls. Run `hf tree` or `hf inspect` first, then act on what is actually there.
- Do not type credentials. Navigate to login screens; let the human complete auth.
- Prefer UIA selectors (name + control_type) over raw coordinates.
- Use `drag-canvas` only for canvas/ink surfaces (Paint, drawing apps, etc.).
- For destructive actions (delete, submit, send), ask the human for confirmation first.

---

## Workflow: Desktop app (UIA)

```powershell
# Launch any installed app
hf start --app "Outlook"

# Find the window
hf list-windows --json

# Discover controls (no guessing)
hf tree --title-regex "Outlook" --depth 10 --max-nodes 30000

# Act on what was found
hf click --title "Outlook" --name "New mail" --control-type "Button"

# Inspect element under cursor
hf inspect --json
```

## Workflow: Browser (Playwright)

```powershell
# Open URL - login sessions saved in profile automatically
hf browser-open --url "https://example.com"

# Inspect page before acting
hf browser-snapshot --fmt text

# Act
hf browser-click --text "Sign in"
hf browser-type --selector "#email" --text "user@example.com"

# Verify
hf browser-screenshot --out result.png
```

## Mixed macro (desktop + web in one YAML)

```yaml
- action: start
  args:
    app: "My Desktop App"

- action: browser-open
  args:
    url: "https://app.example.com"
    headless: false

- action: browser-click
  args:
    text: "Get Started"

- action: sleep
  args:
    seconds: 1
```

Run with: `hf run macro.yaml`

---

## References
- Full command reference + selector schema: references/api_reference.md
