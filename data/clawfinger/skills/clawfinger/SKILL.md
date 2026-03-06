---
name: clawfinger
description: Clawfinger voice gateway plugin — real-time call takeover, TTS injection, context injection, and live observation via the agent WebSocket bridge.
metadata:
  openclaw:
    emoji: "\U0001F4DE"
    skillKey: clawfinger
    requires:
      - plugin:clawfinger
---

# Clawfinger Plugin

Real-time bridge to the Clawfinger voice gateway. Gives you full control over active phone calls: take over the LLM, inject speech, push context, observe transcripts, and manage call policy.

## Available Tools

### Status and Observation

| Tool | Description |
|------|-------------|
| `clawfinger_status` | Gateway health, active sessions, bridge connection status |
| `clawfinger_sessions` | List active call session IDs |
| `clawfinger_call_state` | Full call state for a session: conversation history, instructions, takeover status |

### Call Control

| Tool | Description |
|------|-------------|
| `clawfinger_dial` | Dial an outbound phone call (phone must be connected via ADB) |
| `clawfinger_hangup` | Force hang up the active phone call via ADB and end the gateway session |
| `clawfinger_inject` | Inject a TTS message into the active call — text is synthesized and played to the caller |
| `clawfinger_takeover` | Take over LLM control for a session — then use turn_wait/turn_reply to handle turns |
| `clawfinger_turn_wait` | Wait for the next caller turn during takeover (returns transcript + request_id) |
| `clawfinger_turn_reply` | Send your reply text for a takeover turn (requires request_id from turn_wait) |
| `clawfinger_release` | Release LLM control back to the local gateway LLM |
| `clawfinger_session_end` | Mark a call session as ended (hung up) — moves it from active to ended state |

### Context and Instructions

| Tool | Description |
|------|-------------|
| `clawfinger_context_set` | Inject knowledge into a session — the LLM sees this before each user turn. Replaces existing context. |
| `clawfinger_context_clear` | Clear injected knowledge from a session |
| `clawfinger_instructions_set` | Set LLM system instructions. Scope: `global`, `session`, or `turn` (one-shot). |

### Configuration

| Tool | Description |
|------|-------------|
| `clawfinger_call_config_get` | Read call policy: auto-answer, greetings, caller filtering, max duration, auth |
| `clawfinger_call_config_set` | Update call policy settings (pass only fields to change). Allowed fields: `greeting_incoming`, `greeting_outgoing`, `greeting_owner`, `max_duration_sec`, `max_duration_message`, `call_auto_answer`, `call_auto_answer_delay_ms`, `keep_history`, `tts_voice`, `tts_speed`. **Not allowed**: `tts_lang` (language is control-center-only), `piper_*` settings. |

## WS Bridge

The plugin maintains a persistent WebSocket connection to the gateway at `/api/agent/ws`. The bridge:

- Auto-reconnects with exponential backoff (1s -> 30s max)
- Sends ping heartbeats every 15s
- Receives all gateway events (`turn.*`, `agent.*`, `config.*`, etc.)
- Handles `request_id` correlation for takeover turn replies

The bridge starts automatically when the plugin loads and stops when it unloads.

## WS Event Envelope Format

**All events from the gateway use a nested envelope.** The top-level JSON has `type`, `timestamp`, `session_id`, and a `data` object containing the event-specific fields:

```json
{
  "type": "turn.transcript",
  "timestamp": 1708700000.123,
  "session_id": "abc123def456",
  "data": {
    "transcript": "what the caller actually said"
  }
}
```

**Common event payloads** (fields inside `data`):

| Event | `data` fields |
|-------|---------------|
| `turn.started` | `session_id` |
| `turn.transcript` | `transcript` |
| `turn.reply` | `reply` |
| `turn.complete` | `metrics`, `transcript`, `reply`, `model` |
| `turn.request` | `session_id`, `transcript`, `request_id` (takeover only) |
| `turn.stale` | `session_id`, `reason` |
| `turn.error` | `error` |
| `turn.authenticated` | `session_id` |
| `turn.auth_failed` | `session_id`, `attempt` |
| `turn.caller_rejected` | `number`, `reason` |
| `agent.connected` | *(empty)* |
| `config.updated` | `key`, `value` |

**Important:** Always read event-specific fields from `event.data`, not from the top level. For example, to get the transcript text: `event.data.transcript`, **not** `event.transcript`.

## Takeover Lifecycle

1. **Observe** — Use `clawfinger_status` and `clawfinger_sessions` to see active calls.
2. **Inspect** — Use `clawfinger_call_state` to read conversation history and current instructions.
3. **Prepare** — Optionally use `clawfinger_context_set` to inject knowledge the LLM should have.
4. **Take over** — Call `clawfinger_takeover` with the session ID. The gateway will now route caller transcripts to you instead of the local LLM.
5. **Respond** — When you receive a `turn.request` event with a transcript, the bridge sends your reply back with `request_id` correlation for reliable matching.
6. **Release** — Call `clawfinger_release` to hand control back to the local LLM.

During takeover, if you fail to reply within 30 seconds, the gateway falls back to the local LLM for that turn.

## Example Workflows

### Monitor and inject context

```
1. clawfinger_status          -> check gateway is healthy
2. clawfinger_sessions        -> get active session IDs
3. clawfinger_call_state      -> read conversation history
4. clawfinger_context_set     -> push relevant knowledge
   (LLM now has your context for all subsequent turns)
```

### Full call takeover

```
1. clawfinger_sessions        -> find the active session
2. clawfinger_takeover        -> take LLM control
3. clawfinger_turn_wait       -> blocks until caller speaks, returns transcript + request_id
4. clawfinger_turn_reply      -> send your response with the request_id
   (repeat 3-4 for each turn)
5. clawfinger_release         -> hand back to local LLM
```

### Outbound call with greeting

```
1. clawfinger_instructions_set  -> set instructions for the call
2. clawfinger_dial              -> dial the number
3. clawfinger_sessions          -> find the new session
4. clawfinger_context_set       -> push context for the LLM
```

## Slash Command

All gateway operations are also available as direct `/clawfinger` subcommands that bypass the LLM:

| Command | Description |
|---------|-------------|
| `/clawfinger` | Show help with all subcommands |
| `/clawfinger status` | Gateway health, bridge connection, sessions, uptime, LLM status |
| `/clawfinger sessions` | List active session IDs |
| `/clawfinger state <session_id>` | Full call state: history, instructions, takeover status |
| `/clawfinger dial <number>` | Dial outbound call (e.g. `+49123456789`) |
| `/clawfinger hangup [session_id]` | Force hang up the active call and end gateway session |
| `/clawfinger inject <text>` | Inject TTS into active call (uses first session) |
| `/clawfinger inject <session_id> <text>` | Inject TTS into a specific session |
| `/clawfinger takeover <session_id>` | Take over LLM control for a session |
| `/clawfinger release <session_id>` | Release LLM control back to local LLM |
| `/clawfinger context get <session_id>` | Read injected knowledge for a session |
| `/clawfinger context set <session_id> <text>` | Inject/replace knowledge for a session |
| `/clawfinger context clear <session_id>` | Clear injected knowledge |
| `/clawfinger config call` | Show call policy settings (auto-answer, greetings, filtering) |
| `/clawfinger config tts` | Show TTS settings (voice, speed, language, Piper params if German) |
| `/clawfinger config llm` | Show LLM model and generation params |
| `/clawfinger instructions <text>` | Set global LLM system instructions |
| `/clawfinger instructions <session_id> <text>` | Set per-session LLM instructions |
| `/clawfinger end <session_id>` | Mark a session as ended (hung up) |
