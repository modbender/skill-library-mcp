# Config Pattern: Channel Management

**What:** Enable/disable channels, configure channel-specific settings.

**When to use:** Adding channels, disabling channels, configuring channel behavior.

---

## Critical Pattern: Disabling Channels

### ✅ Correct: Explicit `allow: false`

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1469004697305092288", "allow": true },
        { "id": "1468623929550835766", "allow": false }  // Disabled
      ]
    }
  }
}
```

**Key point:** Must explicitly set `"allow": false` to disable.

---

## ❌ Common Mistakes

### Wrong: Just removing from list

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1469004697305092288" }
        // Removed 1468623929550835766 - STILL ENABLED!
      ]
    }
  }
}
```

**Why it fails:** OpenClaw merges config. Removing from patch doesn't remove from active config.

### Wrong: Setting to null

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1468623929550835766", "allow": null }  // WRONG
      ]
    }
  }
}
```

**Why it fails:** Must be explicit boolean `false`.

---

## Enabling Channels

### Adding new channel

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1234567890" }  // Default: allow = true
      ]
    }
  }
}
```

### Re-enabling disabled channel

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1468623929550835766", "allow": true }
      ]
    }
  }
}
```

---

## Channel-Specific Settings

### Discord: Require mention

```json
{
  "channels": {
    "discord": {
      "allowed": [
        {
          "id": "1469004697305092288",
          "requireMention": true  // Only respond when @mentioned
        }
      ]
    }
  }
}
```

### Telegram: Thread ID

```json
{
  "channels": {
    "telegram": {
      "allowed": [
        {
          "id": "-1001234567890",
          "threadId": "123"  // Specific thread in group
        }
      ]
    }
  }
}
```

---

## Multiple Channels

```json
{
  "channels": {
    "discord": {
      "token": "...",
      "allowed": [
        { "id": "1469004697305092288", "requireMention": false },
        { "id": "1468623929550835766", "allow": false },
        { "id": "1470269989671141479" }  // Errors channel
      ]
    },
    "telegram": {
      "token": "...",
      "allowed": [
        { "id": "1325562130644205641" }  // DM
      ]
    }
  }
}
```

---

## Channel vs Binding

**Two separate concepts:**

1. **Channel allowed list** - Controls which channels are accessible (any agent can send)
2. **Agent bindings** - Controls which agent auto-responds in which channel

### Example: Shared errors channel

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1470269989671141479" }  // Errors channel - all can send
      ]
    }
  },
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "bindings": [
          // No binding for errors channel = can send, won't auto-respond
        ]
      }
    ]
  }
}
```

---

## Common Patterns

### Enable channel for all agents (no auto-response)

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1470269989671141479" }  // No bindings = manual use only
      ]
    }
  }
}
```

### Enable channel with specific agent binding

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1469004697305092288" }
      ]
    }
  },
  "agents": {
    "list": [
      {
        "id": "gilfoyle",
        "bindings": [
          {
            "match": {
              "channel": "discord",
              "peer": { "kind": "channel", "id": "1469004697305092288" }
            }
          }
        ]
      }
    ]
  }
}
```

### Disable channel completely

```json
{
  "channels": {
    "discord": {
      "allowed": [
        { "id": "1468623929550835766", "allow": false }
      ]
    }
  },
  "agents": {
    "list": [
      {
        "id": "decorly",
        "bindings": []  // Remove binding too
      }
    ]
  }
}
```

---

## Verification

```bash
# Check config loaded
openclaw status

# View active channels
openclaw gateway config.get | jq '.channels'

# Test message
# Send message to channel - should see response if bound
```

---

## References

- OpenClaw docs: `channels/discord.md`
- OpenClaw docs: `channels/telegram.md`
- OpenClaw docs: `gateway/configuration.md`
- Related: `config-bindings.md`

---

**Always set `allow: false` explicitly.** Omitting from config doesn't disable channels.
