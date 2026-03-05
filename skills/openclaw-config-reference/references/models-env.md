# Models, Environment & Other Configuration Reference

Configuration for LLM providers, environment variables, auth profiles, logging, and miscellaneous settings.

---

## Table of Contents
1. [Models Block](#models-block)
2. [Environment Block](#environment-block)
3. [Auth Block](#auth-block)
4. [Logging](#logging)
5. [Miscellaneous Sections](#miscellaneous-sections)

---

## Models Block

Configure LLM providers and custom models.

```json5
models: {
  mode: "merge",                     // merge | replace
  providers: {
    "custom-provider": {
      baseUrl: "https://my-proxy.example.com/v1",
      apiKey: "...",
      api: "openai-completions",     // API format
      headers: {},                   // Extra HTTP headers
      models: [
        {
          id: "my-model-id",
          name: "My Model Display Name",
          contextWindow: 200000
        }
      ]
    }
  }
}
```

### Mode

| Mode | Behavior |
|------|----------|
| `merge` | Add custom providers alongside built-in providers (default) |
| `replace` | Replace all built-in providers with only your custom ones |

### Provider Configuration

| Field | Type | Description |
|-------|------|-------------|
| `baseUrl` | string | API endpoint URL |
| `apiKey` | string | API key (prefer env vars instead) |
| `api` | string | API format identifier |
| `headers` | object | Additional HTTP headers for requests |
| `models` | array | Custom model definitions |

### Model Definition

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Model ID used in config (e.g., `"custom-provider/my-model"`) |
| `name` | string | Human-readable display name |
| `contextWindow` | number | Context window size in tokens |

### Common Provider Examples

**OpenRouter:**
```json5
models: {
  providers: {
    "openrouter": {
      baseUrl: "https://openrouter.ai/api/v1",
      apiKey: "sk-or-...",
      api: "openai-completions"
    }
  }
}
```

**Local LLM (Ollama, LM Studio):**
```json5
models: {
  providers: {
    "local": {
      baseUrl: "http://localhost:11434/v1",
      api: "openai-completions",
      models: [
        { id: "llama3", name: "Llama 3", contextWindow: 8192 }
      ]
    }
  }
}
```

**Azure OpenAI:**
```json5
models: {
  providers: {
    "azure": {
      baseUrl: "https://my-resource.openai.azure.com/openai/deployments/my-deployment",
      apiKey: "...",
      api: "openai-completions",
      headers: { "api-version": "2024-02-01" }
    }
  }
}
```

### API Key Security

**Never hardcode API keys in config.** Use environment variables:

```bash
# ~/.openclaw/.env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```

The models block auto-detects standard env var names for built-in providers.

---

## Environment Block

Inject environment variables into agent processes.

```json5
env: {
  vars: {                            // Static env vars
    CUSTOM_VAR: "value",
    API_ENDPOINT: "https://api.example.com",
    TZ: "America/New_York"
  },
  shellEnv: true                     // Inherit current shell environment
}
```

### Env Var Precedence (highest wins)

1. Process environment (system-level)
2. `./.env` (local directory)
3. `~/.openclaw/.env`
4. `openclaw.json` `env.vars` block

### shellEnv

When `true`, the agent inherits all environment variables from the shell that started the Gateway. When `false`, only explicitly set variables are available.

---

## Auth Block

Authentication profiles for multi-user setups.

```json5
auth: {
  profiles: {},                      // Named auth profiles
  order: []                          // Profile evaluation order
}
```

Used in multi-user deployments where different users need different permission levels.

---

## Logging

OpenClaw logs can be configured for level, destination, and redaction.

```json5
logging: {
  level: "info",                     // error | warn | info | debug | trace
  file: "~/.openclaw/logs/gateway.log",
  consoleLevel: "info",
  consoleStyle: "pretty",           // pretty | json
  redactSensitive: true,            // Redact API keys in logs
  redactPatterns: []                 // Additional regex patterns to redact
}
```

| Field | Type | Description |
|-------|------|-------------|
| `level` | string | File log level |
| `file` | string | Log file path |
| `consoleLevel` | string | Console output log level |
| `consoleStyle` | string | `"pretty"` for human-readable, `"json"` for machine-parseable |
| `redactSensitive` | boolean | Auto-redact known API key patterns |
| `redactPatterns` | array | Additional regex patterns to redact |

### Viewing Logs

```bash
openclaw logs --follow              # Tail gateway logs
openclaw logs --agent-id main       # Agent-specific logs
```

---

## Miscellaneous Sections

These sections exist in the config schema but are typically left at defaults:

| Section | Purpose |
|---------|---------|
| `bindings` | Advanced routing bindings |
| `talk` | Voice/speech configuration |
| `ui` | UI customization settings |
| `canvas` | Canvas/drawing tool settings |
| `discovery` | mDNS/Bonjour discovery settings |
| `wizard` | Onboarding wizard configuration |

These are primarily used by native apps and advanced deployments. Most users don't need to touch them.
