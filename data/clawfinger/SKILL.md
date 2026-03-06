---
name: clawfinger
description: OpenClaw plugin that bridges to the Clawfinger voice gateway. Provides tools for live call takeover, TTS injection, outbound dialing, hangup, context/knowledge injection, instruction management, and call policy configuration — all over a persistent WebSocket connection.
metadata:
  openclaw:
    emoji: "\U0001F4DE"
    skillKey: clawfinger
    pluginId: clawfinger
---

# Clawfinger — OpenClaw Voice Gateway Plugin

> **Requires**: [Trac-Systems/clawfinger](https://github.com/Trac-Systems/clawfinger) — the local voice gateway and Android phone app. Install and run the gateway before using this plugin.

OpenClaw plugin that gives agents full control over the Clawfinger local voice gateway and its active phone calls.

## What It Does

- **Call control**: Dial outbound calls, hang up, inject spoken messages into live calls
- **LLM takeover**: Replace the gateway's local LLM with agent-driven responses in real time
- **Context injection**: Push knowledge into the LLM context so the phone assistant has facts you provide
- **Instruction management**: Set system prompts at global, session, or one-shot turn scope
- **Call policy**: Read and update greetings, auto-answer, caller filtering, max duration
- **Observation**: Query session state, conversation history, and gateway health

## Dependencies

- **Gateway**: A running Clawfinger voice gateway (`app.py` on `127.0.0.1:8996`)
- **Node**: `@sinclair/typebox` (install via `npm install` in plugin directory)
- **Phone**: Android phone with the PhoneBridge app, connected via ADB reverse port forwarding

## Configuration

In `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "load": { "paths": ["/path/to/gateway/openclaw/clawfinger"] },
    "entries": {
      "clawfinger": {
        "enabled": true,
        "config": {
          "gatewayUrl": "http://127.0.0.1:8996",
          "bearerToken": "localdev"
        }
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `clawfinger_status` | Gateway health, active sessions, bridge status |
| `clawfinger_sessions` | List active call session IDs |
| `clawfinger_call_state` | Full call state: history, instructions, takeover status |
| `clawfinger_dial` | Dial outbound call via ADB |
| `clawfinger_hangup` | Force hang up active call and end session |
| `clawfinger_inject` | Inject TTS message into a live call |
| `clawfinger_takeover` | Take over LLM control for a session |
| `clawfinger_turn_wait` | Wait for the next caller turn during takeover (returns transcript + request_id) |
| `clawfinger_turn_reply` | Send your reply text for a takeover turn (requires request_id) |
| `clawfinger_release` | Release LLM control back to local LLM |
| `clawfinger_context_set` | Inject knowledge into session LLM context |
| `clawfinger_context_clear` | Clear injected knowledge |
| `clawfinger_instructions_set` | Set LLM system instructions (global/session/turn) |
| `clawfinger_call_config_get` | Read call policy settings |
| `clawfinger_call_config_set` | Update call policy settings |

## Slash Commands

`/clawfinger status`, `/clawfinger dial <number>`, `/clawfinger hangup`, `/clawfinger inject <text>`, `/clawfinger takeover <sid>`, `/clawfinger release <sid>`, `/clawfinger end <sid>`, `/clawfinger context get|set|clear <sid>`, `/clawfinger config call|tts|llm`, `/clawfinger instructions <text>`.

## Related Skills

- **agent-takeover**: Full takeover lifecycle guide with timing model and test case
- **voice-gateway**: Gateway installation, API reference, and operations
