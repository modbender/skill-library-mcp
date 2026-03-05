# Recommendations by Use Case

## Personal Assistant (Single User)

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/clawd",
      "model": { "primary": "anthropic/claude-sonnet-4-20250514" },
      "heartbeat": { "every": "30m", "target": "telegram" }
    }
  },
  "channels": {
    "telegram": {
      "dmPolicy": "allowlist",
      "allowFrom": ["YOUR_USER_ID"]
    }
  },
  "tools": {
    "profile": "full",
    "exec": { "security": "full" }
  }
}
```

**Key points:**
- Full tool access for yourself
- Heartbeat for proactive check-ins
- Strict allowlist (only you)

---

## Multi-User Bot (Team/Community)

```json
{
  "channels": {
    "telegram": {
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "groups": {
        "-100GROUPID": {
          "enabled": true,
          "requireMention": true,
          "allowFrom": ["123", "456", "789"]
        }
      }
    }
  },
  "tools": {
    "exec": { "security": "allowlist" }
  },
  "session": {
    "dmScope": "per-peer"
  }
}
```

**Key points:**
- Pairing for unknown users
- Per-peer sessions (privacy)
- Restricted exec (allowlist only)
- Mention required in groups

---

## Developer Workstation

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/projects",
      "model": { "primary": "anthropic/claude-opus-4-5-20251101" }
    }
  },
  "tools": {
    "profile": "full",
    "exec": {
      "security": "full",
      "safeBins": ["git", "npm", "pnpm", "node", "python", "docker"]
    }
  },
  "browser": {
    "enabled": true,
    "defaultProfile": "openclaw"
  },
  "skills": {
    "entries": {
      "github": { "enabled": true },
      "coding-agent": { "enabled": true }
    }
  }
}
```

**Key points:**
- Opus for complex tasks
- Full exec access
- Browser for web automation
- Coding skills enabled

---

## Remote/Cloud Deployment

```json
{
  "gateway": {
    "bind": "lan",
    "auth": { "mode": "token", "token": "${GATEWAY_TOKEN}" },
    "tls": { "enabled": true, "autoGenerate": true }
  },
  "agents": {
    "defaults": {
      "sandbox": { "mode": "non-main" }
    }
  },
  "tools": {
    "exec": {
      "security": "allowlist",
      "host": "sandbox"
    }
  }
}
```

**Key points:**
- TLS required
- Token auth required
- Sandbox sub-agents
- Exec in sandbox only

---

## High-Volume Production

```json
{
  "agents": {
    "defaults": {
      "maxConcurrent": 10,
      "subagents": { "maxConcurrent": 20 },
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": ["anthropic/claude-haiku"]
      }
    }
  },
  "cron": { "maxConcurrentRuns": 5 },
  "messages": {
    "queue": { "mode": "steer", "cap": 20 }
  },
  "tools": {
    "media": { "concurrency": 4 }
  }
}
```

**Key points:**
- Model fallbacks
- Concurrent limits tuned
- Haiku for high-volume tasks
- Queue mode: steer

---

## Privacy-Focused

```json
{
  "channels": {
    "signal": {
      "dmPolicy": "allowlist",
      "allowFrom": ["YOUR_UUID"]
    }
  },
  "agents": {
    "defaults": {
      "memorySearch": { "enabled": false }
    }
  },
  "session": {
    "reset": { "mode": "idle", "idleMinutes": 30 }
  },
  "logging": { "level": "warn" }
}
```

**Key points:**
- Signal (E2E encrypted)
- Memory search disabled
- Short session retention
- Minimal logging

---

## Voice-First

```json
{
  "messages": {
    "tts": {
      "enabled": true,
      "auto": "inbound",
      "provider": "elevenlabs",
      "elevenlabs": {
        "voiceId": "21m00Tcm4TlvDq8ikWAM"
      }
    }
  },
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [{ "provider": "openai", "model": "whisper-1" }]
      }
    }
  },
  "plugins": {
    "entries": {
      "voice-call": { "enabled": true }
    }
  }
}
```

**Key points:**
- TTS auto on inbound audio
- Audio transcription enabled
- Voice-call plugin for phone

---

## Minimal/Cheap

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-haiku" },
      "subagents": { "model": "anthropic/claude-haiku" }
    }
  },
  "tools": {
    "profile": "minimal"
  },
  "agents": {
    "defaults": {
      "contextTokens": 32000
    }
  }
}
```

**Key points:**
- Haiku everywhere (cheapest)
- Minimal tools
- Reduced context window
