# Chat Protocol

## Overview

Agents communicate via `.workplace/chat.md`, a plain-text append-only log. The Rust file-watcher server monitors this file and outputs parsed messages as JSON lines to stdout.

## Message Format

### Direct Message

```
[sender-to-recipient]: message content here
```

Example:
```
[coder-to-reviewer]: Please review changes in src/auth.rs — added JWT validation
```

### Broadcast Message

```
[sender-to-recipient] @ [target1, target2]: message content here
```

Example:
```
[reviewer-to-coder] @ [developer, manager]: Approved with minor suggestions — see inline comments
```

The broadcast targets receive the message as observers. The primary recipient is expected to act.

### Acknowledgment

Use the broadcast syntax to acknowledge receipt:

```
[reviewer-to-coder] @ [developer]: Acknowledged — starting review
```

## Parsing Rules

1. Lines must start with `[` to be treated as messages
2. Sender and recipient names: alphanumeric + hyphens + underscores
3. The `-to-` separator is required between sender and recipient
4. Broadcast targets are comma-separated inside `@ [...]`
5. Everything after `: ` is the message body
6. Empty lines and lines not matching the pattern are ignored (can be used for comments)

## Regex Pattern

```
^\[([a-zA-Z0-9_-]+)-to-([a-zA-Z0-9_-]+)\](?:\s*@\s*\[([^\]]*)\])?\s*:\s*(.+)$
```

## JSON Output (from Rust server)

The file-watcher server outputs one JSON object per line for each detected message:

```json
{
  "timestamp": "2026-02-17T10:05:00.123Z",
  "sender": "coder",
  "recipient": "reviewer",
  "broadcast": [],
  "message": "Please review changes in src/auth.rs",
  "line_number": 42
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO-8601 when the message was detected |
| `sender` | string | Name of the sending agent |
| `recipient` | string | Name of the target agent |
| `broadcast` | string[] | Additional agents who should see this message |
| `message` | string | Message content |
| `line_number` | number | Line number in chat.md |

## Multi-line Messages

For longer messages, use continuation lines (indented):

```
[coder-to-reviewer]: Review needed for auth module
  Changes:
  - Added JWT validation in src/auth.rs
  - Updated middleware in src/middleware.rs
  - Added tests in tests/auth_test.rs
```

Note: The current server implementation treats each non-empty line independently. Multi-line messages are a convention — the first line is parsed as the message, continuation lines are ignored by the parser but visible in the raw file.

## Best Practices

1. **Be specific** — include file paths, line numbers, context
2. **Summarize context** — don't assume the recipient knows what you did
3. **Use broadcast for visibility** — keep stakeholders informed
4. **Acknowledge receipt** — confirm you're working on a handoff
5. **Keep it append-only** — don't edit or delete previous messages
6. **Use comments for notes** — lines not matching the pattern are ignored

## File Management

- `chat.md` is append-only during a session
- Clear/archive between sessions if needed
- The kernel agent may archive old messages to `.workplace/memory/`
