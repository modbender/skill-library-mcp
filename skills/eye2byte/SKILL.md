---
name: eye2byte
description: Give your agent eyes — capture screenshots, voice, and annotations from any screen, monitor, or device via MCP.
version: 0.3.1
user-invocable: true
disable-model-invocation: true
metadata:
  openclaw:
    requires:
      bins:
        - python
      anyBins:
        - ffmpeg
      env:
        - EYE2BYTE_MCP_TOKEN
    primaryEnv: EYE2BYTE_MCP_TOKEN
    emoji: "\U0001F441"
    homepage: https://github.com/wolverin0/Eye2byte
    install:
      - kind: uv
        package: eye2byte
        bins: [eye2byte]
---

# Eye2byte — Screen Context for Your Agent

Eye2byte is an open-source MCP server ([GitHub](https://github.com/wolverin0/Eye2byte), [PyPI](https://pypi.org/project/eye2byte/)) that lets you **see the user's screen**. Use these MCP tools **only when the user explicitly asks** you to look at something, debug a visual issue, or capture their screen.

## Privacy & Data Storage

- **All data stays local.** Captures are stored in `~/.eye2byte/output/` on the user's machine. Nothing is sent to external servers (except the vision model API the user configured).
- **Auto-cleanup:** Captures are deleted after N days (default: 7, configurable in settings). Set to 0 to disable.
- **MCP token:** When using SSE remote transport, the `--token` flag sets a bearer token stored only in the user's `openclaw.json`. Treat it like any API secret. The token is never logged or transmitted beyond the Authorization header.
- **No telemetry.** Eye2byte collects zero analytics or usage data.

## Available MCP Tools

### `capture_and_summarize`
Screenshot the user's screen and get a structured analysis.

Parameters:
- `mode` — `"full"` (default), `"window"`, or `"region"`
- `monitor` — `0` = active monitor (default), `1`/`2`/`3` = specific monitor, `-1` = ALL monitors at once
- `delay` — seconds to wait before capturing (useful for menus/tooltips)
- `window_name` — capture a specific app window by name (e.g., `"chrome"`, `"code"`)

Use this when the user says things like "look at my screen", "what do you see", "debug this", or "what's wrong here".

### `capture_with_voice`
Screenshot + voice recording + transcription. Returns both visual analysis and what the user said.

Use when the user wants to describe something verbally while showing their screen.

### `record_clip_and_summarize`
Record a short screen clip, extract keyframes, and analyze the sequence.

Use when the user wants to show you something that changes over time (animations, workflows, step sequences).

### `summarize_screenshot`
Analyze an existing image file. Pass a file path to get a structured analysis.

### `transcribe_audio`
Local Whisper transcription of any audio file.

### `get_recent_context`
Retrieve recent Context Pack summaries from previous captures.

Use this to recall what you've seen recently without re-capturing.

## What You Get Back

Every capture returns a structured **Context Pack**:

```
Goal           — what the user appears to be doing
Environment    — OS, editor, repo, branch, language
Screen State   — visible panels, files, terminal output
Signals        — verbatim errors, stack traces, warnings
Likely Situation — what's probably happening
Suggested Next Info — what you should ask or do next
```

## When to Use Eye2byte

- User mentions something visual ("this button is broken", "the layout is wrong")
- User asks you to "look at" or "check" something on their screen
- You need to see error dialogs, UI bugs, or terminal output the user can't easily copy
- User is debugging and visual context would help your diagnosis
- User asks you to monitor or watch something
- You want to verify your changes had the intended visual effect

## Multi-Monitor Tips

- `monitor=-1` captures ALL monitors stitched together — useful for seeing the full workspace
- `monitor=1`, `2`, `3` for targeting specific displays
- Default (`monitor=0`) captures whichever monitor has the active window

## Setup

Eye2byte must be running on the machine whose screen you want to capture:

**Local (same machine):** Already configured if this skill loaded.

**Remote (different machine):** The user runs `eye2byte-mcp --sse --token <secret>` on their local machine, and configures the MCP connection URL in openclaw.json.
