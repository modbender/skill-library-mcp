# Config Pattern: Agent Bindings

**What:** Configure which agent responds in which channel/DM.

**When to use:** Adding agents, routing messages, preventing duplicate responses.

---

## Critical Pattern (v2026.2.9+)

### ✅ Correct Structure

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "model": "amazon-bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "bindings": [
          {
            "match": {
              "channel": "discord",
              "peer": { "kind": "channel", "id": "1469004697305092288" }
            }
          },
          {
            "match": {
              "channel": "telegram",
              "peer": { "kind": "dm", "id": "1325562130644205641" }
            }
          }
        ]
      }
    ]
  }
}
```

**Key points:**
- `match.channel` - Channel type (discord, telegram, etc.)
- `match.peer.kind` - "channel" or "dm"
- `match.peer.id` - Channel/user ID as string

---

## ❌ Common Mistakes

### Wrong: Using deprecated fields

```json
{
  "match": {
    "channelId": "1234567890",      // WRONG
    "guildId": "0987654321"         // WRONG
  }
}
```

**Why it fails:** These fields are not recognized by the binding matcher.

### Wrong: Missing peer structure

```json
{
  "match": {
    "channel": "discord",
    "id": "1234567890"               // WRONG
  }
}
```

**Why it fails:** ID must be inside `peer` object with `kind`.

### Wrong: Number instead of string

```json
{
  "match": {
    "channel": "discord",
    "peer": { "kind": "channel", "id": 1234567890 }  // WRONG (number)
  }
}
```

**Why it fails:** IDs must be strings, not numbers.

---

## Binding Types

### Discord Channel

```json
{
  "match": {
    "channel": "discord",
    "peer": { "kind": "channel", "id": "1469004697305092288" }
  }
}
```

### Discord DM

```json
{
  "match": {
    "channel": "discord",
    "peer": { "kind": "dm", "id": "1325562130644205641" }
  }
}
```

### Telegram DM

```json
{
  "match": {
    "channel": "telegram",
    "peer": { "kind": "dm", "id": "1325562130644205641" }
  }
}
```

### Telegram Group

```json
{
  "match": {
    "channel": "telegram",
    "peer": { "kind": "channel", "id": "-1001234567890" }
  }
}
```

---

## Multiple Bindings

One agent can respond in multiple places:

```json
{
  "id": "gilfoyle",
  "bindings": [
    {
      "match": {
        "channel": "discord",
        "peer": { "kind": "channel", "id": "1469004697305092288" }
      }
    },
    {
      "match": {
        "channel": "telegram",
        "peer": { "kind": "dm", "id": "1325562130644205641" }
      }
    }
  ]
}
```

---

## Removing Bindings

### Option 1: Remove entire binding (via config.patch)

```json
{
  "agents": {
    "list": [
      {
        "id": "decorly",
        "bindings": []   // Empty array removes all
      }
    ]
  }
}
```

### Option 2: Replace with new bindings

```json
{
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "bindings": [
          // Only include bindings you want to keep
        ]
      }
    ]
  }
}
```

**Note:** `config.patch` replaces the entire `bindings` array for that agent.

---

## Channel Access vs Bindings

**Two separate configs:**

1. **Channel allowed list** - Controls basic access (all agents can send)
2. **Agent bindings** - Controls auto-response routing

### Example: Shared errors channel

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1470269989671141479" }  // All agents can send here
      ]
    }
  },
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "bindings": []  // No binding = doesn't auto-respond, but can send
      }
    ]
  }
}
```

---

## Verification

After applying config:

```bash
# Check config loaded
openclaw status

# Test message routing
# Send test message to bound channel
```

---

## References

- OpenClaw docs: `concepts/routing.md`
- OpenClaw docs: `gateway/configuration.md`
- Related: `config-channel-management.md`

---

**Always use the correct structure.** Bindings are strict - typos cause silent routing failures.
