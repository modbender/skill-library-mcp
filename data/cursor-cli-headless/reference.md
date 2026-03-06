# Output Format Reference

Detailed schemas for Cursor CLI headless output. Use with `--output-format json` or `--output-format stream-json`.

## JSON format (single object on success)

Use `--output-format json`. One JSON object (one line) when the run completes successfully.

### Success response

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 1234,
  "result": "<full assistant text>",
  "session_id": "<uuid>",
  "request_id": "<optional request id>"
}
```

| Field | Description |
|-------|-------------|
| `type` | Always `"result"` |
| `subtype` | Always `"success"` for success |
| `is_error` | Always `false` for success |
| `duration_ms` | Total execution time (ms) |
| `duration_api_ms` | API time (ms); currently same as `duration_ms` |
| `result` | Full assistant response text (all text deltas concatenated) |
| `session_id` | Session identifier |
| `request_id` | Optional request id |

On failure: process exits non-zero, error on stderr, no JSON object emitted.

---

## Stream-JSON format (NDJSON)

Use `--output-format stream-json`. Each line is one JSON object (NDJSON). Optionally use `--stream-partial-output` for character-level text deltas.

### Event types

#### 1. System initialization (once per run)

```json
{
  "type": "system",
  "subtype": "init",
  "apiKeySource": "env|flag|login",
  "cwd": "/absolute/path",
  "session_id": "<uuid>",
  "model": "<model display name>",
  "permissionMode": "default"
}
```

#### 2. User message

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [{ "type": "text", "text": "<prompt>" }]
  },
  "session_id": "<uuid>"
}
```

#### 3. Assistant message

One event per complete message segment (between tool calls). With `--stream-partial-output`, multiple events per segment with small text deltas; concatenate `message.content[].text` to get full text.

```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [{ "type": "text", "text": "<message text>" }]
  },
  "session_id": "<uuid>"
}
```

#### 4. Tool call — started

```json
{
  "type": "tool_call",
  "subtype": "started",
  "call_id": "<string id>",
  "tool_call": { "<tool type>": { "args": { ... } } },
  "session_id": "<uuid>"
}
```

#### 5. Tool call — completed

```json
{
  "type": "tool_call",
  "subtype": "completed",
  "call_id": "<string id>",
  "tool_call": {
    "<tool type>": {
      "args": { ... },
      "result": { "success": { ... } }
    }
  },
  "session_id": "<uuid>"
}
```

#### 6. Terminal result (end of stream on success)

```json
{
  "type": "result",
  "subtype": "success",
  "duration_ms": 1234,
  "duration_api_ms": 1234,
  "is_error": false,
  "result": "<full assistant text>",
  "session_id": "<uuid>",
  "request_id": "<optional request id>"
}
```

---

## Tool call types

### readToolCall

- **Started**: `tool_call.readToolCall.args` → `{ "path": "file.txt" }`
- **Completed**: `tool_call.readToolCall.result.success` → `{ "content": "...", "isEmpty": false, "exceededLimit": false, "totalLines": 54, "totalChars": 1254 }`

### writeToolCall

- **Started**: `tool_call.writeToolCall.args` → `{ "path": "file.txt", "fileText": "content...", "toolCallId": "id" }`
- **Completed**: `tool_call.writeToolCall.result.success` → `{ "path": "/absolute/path", "linesCreated": 19, "fileSize": 942 }`

### Other tools

May use `tool_call.function` with `{ "name": "tool_name", "arguments": "..." }`.

---

## Example NDJSON sequence

```json
{"type":"system","subtype":"init","apiKeySource":"login","cwd":"/Users/user/project","session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff","model":"Claude 4 Sonnet","permissionMode":"default"}
{"type":"user","message":{"role":"user","content":[{"type":"text","text":"Read README.md and create a summary"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"I'll read the README.md file"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"started","call_id":"toolu_xxx","tool_call":{"readToolCall":{"args":{"path":"README.md"}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"completed","call_id":"toolu_xxx","tool_call":{"readToolCall":{"args":{"path":"README.md"},"result":{"success":{"content":"# Project\n\n...","isEmpty":false,"exceededLimit":false,"totalLines":54,"totalChars":1254}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Based on the README, I'll create a summary"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"started","call_id":"toolu_yyy","tool_call":{"writeToolCall":{"args":{"path":"summary.txt","fileText":"# README Summary\n\n...","toolCallId":"toolu_yyy"}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"tool_call","subtype":"completed","call_id":"toolu_yyy","tool_call":{"writeToolCall":{"args":{"path":"summary.txt",...},"result":{"success":{"path":"/Users/user/project/summary.txt","linesCreated":19,"fileSize":942}}},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"assistant","message":{"role":"assistant","content":[{"type":"text","text":"Done! I've created the summary in summary.txt"}]},"session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff"}
{"type":"result","subtype":"success","duration_ms":5234,"duration_api_ms":5234,"is_error":false,"result":"I'll read...Based on the README...Done!...","session_id":"c6b62c6f-7ead-4fd6-9922-e952131177ff","request_id":"..."}
```

---

## Implementation notes

- Each event is one line, terminated by `\n`.
- `thinking` events are suppressed in print mode.
- Session IDs are constant for one run; `call_id` correlates tool started/completed.
- Consumers should ignore unknown fields (backward compatibility).
