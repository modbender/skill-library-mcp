---
name: airpoint
description: Control a Mac through natural language — open apps, click buttons, read the screen, type text, manage windows, and automate multi-step tasks via Airpoint's AI computer-use agent.
metadata: {"openclaw": {"emoji": "🖐️", "homepage": "https://airpoint.app", "requires": {"bins": ["airpoint"]}, "os": ["darwin"]}}
---

# Airpoint — AI Computer Use for macOS

Airpoint gives you an AI agent that can **see and control a Mac** — open apps,
click UI elements, read on-screen text, type, scroll, drag, and manage windows.
You give it a natural-language instruction and it carries out the task
autonomously by perceiving the screen (accessibility tree + screenshots + visual
locator), planning actions, executing them, and verifying the result.

Everything runs through the `airpoint` CLI.

## Requirements

- **macOS** (Apple Silicon or Intel)
- **Airpoint app** — must be running. Download from [airpoint.app](https://airpoint.app).
- **Airpoint CLI** — the `airpoint` command must be on PATH. Install it from the Airpoint app: Settings → Plugins → Install CLI.

## Setup

Before using Airpoint's AI agent, the user must configure it in the Airpoint
app (Settings → Assistant):

1. **AI model API key (required).** Set an API key for the chosen provider:
   - **OpenAI (recommended):** model `gpt-5.1` with reasoning effort `low` gives
     the best balance of cost, speed, and quality.
   - Anthropic and Google Gemini are also supported.
2. **Gemini API key (recommended).** Even when using OpenAI or Anthropic as the
   primary model, a Google Gemini API key enables the visual locator — a
   secondary model (`gemini-3-flash-preview`) that finds UI targets on screen
   by analyzing screenshots. Without it, the agent relies on the accessibility
   tree only.
3. **macOS permissions.** The app prompts on first launch, but verify these are
   granted in System Settings → Privacy & Security:
   - **Accessibility** — required for mouse/keyboard control.
   - **Screen Recording** — required for screenshots and screen perception.
   - Camera is only needed for hand tracking (not for the AI agent).
4. **Custom instructions (optional).** In Settings → Assistant, add custom
   instructions to tailor the agent's behavior (e.g., preferred language,
   apps to avoid, workflows to follow).

If the user reports that `airpoint ask` fails or the agent can't see the
screen, ask them to verify steps 1–3 above.

## How to use

1. Run `airpoint ask "<your instruction>"` to send a task to the on-device agent.
2. The command blocks until the agent finishes (up to 5 minutes) and returns:
   - A text summary of what the agent did and the result.
   - One or more **screenshot file paths** showing the screen state after the task.
3. Read the text output to confirm whether the task succeeded.
4. If screenshots were returned, show the **last screenshot** to the user as
   visual confirmation of the result.
5. If something went wrong or the task is stuck, run `airpoint stop` to cancel.

Example flow:

```
> airpoint ask "open Safari and search for 'OpenClaw'"
Opened Safari, typed 'OpenClaw' into the address bar, and pressed Enter.
The search results page is now displayed.

1 screenshot(s) saved to session abc123
  └ screenshots/step_3.png (/Users/you/Library/Application Support/com.medhuelabs.airpoint/sessions/abc123/screenshots/step_3.png)
```

After receiving this, show the screenshot to the user so they can see what happened.

## Commands

### Ask the AI agent to do something (primary command)

This is the most important command. It sends a natural-language task to
Airpoint's built-in computer-use agent which can see the screen, move the
mouse, click, type, scroll, open apps via Spotlight, manage windows, and verify
its own actions.

```bash
# Synchronous — waits for the agent to finish (up to 5 min) and returns output
airpoint ask "open Safari and go to github.com"
airpoint ask "what's on my screen right now?"
airpoint ask "find the Slack notification and read it"
airpoint ask "open System Settings and enable Dark Mode"
airpoint ask "open Mail, find the latest email from John, and summarize it"

# Fire-and-forget — returns immediately
airpoint ask "open Spotify and play my liked songs" --no-wait

# Show the assistant panel on screen while running
airpoint ask "open System Settings and enable Dark Mode" --show-panel
```

### Stop a running task

```bash
airpoint stop
```

Cancels the currently running assistant task. Use this if a task is stuck or
taking too long.

### Capture a screenshot

```bash
airpoint see
```

Returns a screenshot of the current display. Useful for verifying state before
or after issuing an `ask` command.

### Check status

```bash
airpoint status
airpoint status --json
```

Returns app version and current state (tracking active, etc.).

### Hand tracking (secondary)

Airpoint also supports hands-free cursor control via camera-based hand tracking.
These commands start/stop that feature:

```bash
airpoint tracking on
airpoint tracking off
airpoint tracking        # show current state
```

### Read or change settings

```bash
airpoint settings list             # all current settings
airpoint settings list --json      # machine-readable
airpoint settings get cursor.sensitivity
airpoint settings set cursor.sensitivity 1.5
```

Common settings: `cursor.sensitivity` (default 1.0), `cursor.acceleration`
(default true), `scroll.sensitivity` (default 1.0), `scroll.inertia`
(default true).

### System vitals

```bash
airpoint vitals          # CPU, RAM, temperature
airpoint vitals --json
```

### Launch the app

```bash
airpoint open            # opens/focuses the Airpoint macOS app
```

## Tips

- **Use `airpoint ask` for almost everything.** The agent can read the screen,
  interact with any app, and chain multi-step workflows autonomously.
- Always use `--json` when you need to parse output programmatically.
- The agent can answer questions about what's on screen ("what app is in the
  foreground?", "read the error message in this dialog").
- Airpoint is a notarized, code-signed macOS app. Download it from
  [airpoint.app](https://airpoint.app).
