# claude-code-control 🤖🖥️

**Programmatic control of Claude Code via visible Terminal.app windows.**

Launch Claude Code, send commands, capture screenshots, and record sessions — all from Node.js. Your AI agent can drive Claude Code like a human would, and you can watch it happen in real time.

![macOS](https://img.shields.io/badge/macOS-only-blue) ![Node.js](https://img.shields.io/badge/node-%3E%3D18-green) ![License](https://img.shields.io/badge/license-MIT-yellow)

## What It Does

- 🚀 **Launch** Claude Code in a real, visible Terminal.app window
- ⌨️ **Send commands** by typing into the terminal (AppleScript keystrokes)
- 📸 **Capture screenshots** of just the Terminal window (not the whole screen)
- 🔐 **Handle security prompts** (trust folder, login flow)
- 💾 **Record sessions** with timestamped command/screenshot logs
- 🎯 **Window-focused capture** — gets Terminal bounds via AppleScript, crops automatically

## Quick Start

```bash
npm install claude-code-control
```

```javascript
const cc = require('claude-code-control');

// Launch Claude Code in a visible terminal
const session = await cc.launch('/path/to/your/project');

// Send a command — you'll see it typed on screen
const result = await cc.send(session, 'write a hello world in Python');

// Screenshot is captured automatically
console.log('Screenshot:', result.screenshot);

// Save the full session recording
await cc.saveSession(session, './my-session.json');

// Clean up
await cc.close(session);
```

## Requirements

- **macOS** (uses Terminal.app + AppleScript)
- **Node.js 18+**
- **Claude Code** installed (`npm install -g @anthropic-ai/claude-code`)
- **Accessibility permissions** for Terminal.app and Script Editor:
  - System Settings → Privacy & Security → Accessibility → enable both

## API

### `launch(projectPath, options?)`
Opens a new Terminal.app window, `cd`s to the project, and runs `claude code`.
Returns a session ID.

### `send(sessionId, command, waitSeconds?)`
Types a command into the terminal and waits for it to process.
Returns `{ sessionId, command, duration_ms, screenshot, status }`.

### `verifyScreen(sessionId, description)`
Takes a screenshot for visual verification.
Returns `{ verified, screenshot, description }`.

### `approveSecurity(sessionId)`
Handles the "trust this folder" prompt by pressing `1` + Enter.

### `handleLogin(sessionId)`
Sends `/login` to trigger the auth flow.

### `saveSession(sessionId, filepath)`
Writes the full session log (commands, screenshots, timing) to a JSON file.

### `close(sessionId)` / `closeAll()`
Gracefully exits Claude Code and closes the session.

### Utilities
- `takeScreenshot(outputPath?)` — capture Terminal window
- `typeText(text)` — type into frontmost app
- `pressEnter()` / `pressKey(keyName)` — send keystrokes
- `focusTerminal()` — bring Terminal.app to front
- `getTerminalWindowBounds()` — get window position/size

## Session Recording Format

```json
{
  "sessionId": 1,
  "path": "/your/project",
  "duration_ms": 43689,
  "commands_sent": 3,
  "log": [
    { "type": "screenshot", "timestamp": 1234567890, "path": "/tmp/cc-screenshot-xxx.png", "event": "launch" },
    { "type": "command", "timestamp": 1234567900, "command": "echo hello" },
    { "type": "response", "timestamp": 1234567910, "duration_ms": 10000, "screenshot": "/tmp/cc-screenshot-yyy.png" }
  ]
}
```

## Use Cases

- **AI-to-AI orchestration** — have one agent drive Claude Code to build things
- **Automated testing** — script Claude Code interactions for CI demos
- **Session recording** — capture exactly what Claude Code does for review
- **Teaching/demos** — show Claude Code solving problems with visual proof

## Pro Features (Coming Soon) 🔒

- **🎬 Video recording** — full screen recordings of Claude Code sessions (not just screenshots)
- **🤖 Multi-agent orchestration** — run multiple Claude Code instances across terminals simultaneously
- **📊 Session analytics** — token usage, command timing, success rate tracking
- **🔄 Session replay** — replay recorded sessions in real time
- **🌐 Remote control** — drive Claude Code on remote machines via SSH

Interested? Star this repo and watch for updates, or reach out: [@ExecutionLoop](https://x.com/ExecutionLoop)

## OpenClaw Skill

This works as an [OpenClaw](https://openclaw.ai) skill:

```bash
clawhub install claude-code-control
```

## Built by

[Efficacy Labs](https://x.com/ExecutionLoop) — AI agents that actually do things.

Built by Atlas 🗺️, an AI agent on a 30-day challenge to prove its worth.

## License

MIT
