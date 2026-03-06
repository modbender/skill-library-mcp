# Tools Configuration

## Tool Profiles

```json
{
  "tools": {
    "profile": "full"
  }
}
```

| Profile | Tools Included |
|---------|----------------|
| `minimal` | read, write, edit |
| `coding` | minimal + exec, browser |
| `messaging` | minimal + message, cron |
| `full` | All tools ⭐ |

---

## Web Search

```json
{
  "tools": {
    "web": {
      "search": {
        "enabled": true,
        "provider": "brave",
        "apiKey": "${BRAVE_API_KEY}",
        "maxResults": 5,
        "cacheTtlMinutes": 30
      },
      "fetch": {
        "enabled": true,
        "maxChars": 50000,
        "timeoutSeconds": 30
      }
    }
  }
}
```

**providers:** `brave`, `perplexity`

---

## Browser Control

```json
{
  "browser": {
    "enabled": true,
    "headless": false,
    "defaultProfile": "openclaw",
    "profiles": {
      "openclaw": {
        "color": "#FF6B00",
        "cdpPort": 9222
      },
      "chrome": {
        "driver": "extension"
      }
    }
  }
}
```

**profiles:**
- `openclaw` — Managed browser (isolated, persistent)
- `chrome` — User's Chrome via extension relay

---

## Media Processing

### Image Understanding

```json
{
  "tools": {
    "media": {
      "image": {
        "enabled": true,
        "maxBytes": 20971520
      }
    }
  }
}
```

### Audio Transcription

```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true,
        "models": [
          {
            "provider": "openai",
            "model": "whisper-1"
          }
        ]
      }
    }
  }
}
```

### Video Understanding

```json
{
  "tools": {
    "media": {
      "video": {
        "enabled": true
      }
    }
  }
}
```

---

## Exec Tool

```json
{
  "tools": {
    "exec": {
      "host": "gateway",
      "security": "allowlist",
      "safeBins": [
        "cat", "ls", "head", "tail", "grep",
        "git", "npm", "node", "python"
      ],
      "timeoutSec": 300,
      "backgroundMs": 10000,
      "pathPrepend": ["/usr/local/bin"]
    }
  }
}
```

**host:** `gateway` (local), `sandbox` (Docker), `node` (remote)

---

## TTS (Text-to-Speech)

```json
{
  "messages": {
    "tts": {
      "enabled": true,
      "auto": "tagged",
      "provider": "elevenlabs",
      "elevenlabs": {
        "apiKey": "${ELEVENLABS_API_KEY}",
        "voiceId": "21m00Tcm4TlvDq8ikWAM"
      }
    }
  }
}
```

**auto modes:** `off`, `always`, `inbound`, `tagged`
**providers:** `elevenlabs`, `openai`, `edge`

---

## Skills

Install and configure skills:

```json
{
  "skills": {
    "load": {
      "extraDirs": ["~/my-skills"],
      "watch": true
    },
    "entries": {
      "github": {
        "enabled": true,
        "env": {
          "GITHUB_TOKEN": "${GITHUB_TOKEN}"
        }
      }
    }
  }
}
```

**CLI commands:**
```bash
clawhub search <query>
clawhub install <skill>
clawhub list
```

---

## Tool Allowlists

Fine-grained control:

```json
{
  "tools": {
    "allow": ["read", "write", "edit", "exec"],
    "deny": ["gateway"],
    "alsoAllow": ["browser"]
  }
}
```

Per-provider overrides:

```json
{
  "tools": {
    "byProvider": {
      "anthropic": {
        "profile": "full"
      },
      "openai": {
        "profile": "coding",
        "deny": ["exec"]
      }
    }
  }
}
```
