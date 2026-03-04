# RelayPlane

**Intelligent AI model routing. Save 50-80% on LLM costs.**

Route LLM requests through RelayPlane to automatically use the optimal model for each task.

---

## Why RelayPlane?

- **100% Local** — All data in SQLite, zero cloud dependency required
- **Zero Friction** — Install, start, done
- **5 Providers** — Anthropic, OpenAI, Gemini, xAI, Moonshot
- **Smart Routing** — Task classification picks the right model
- **Full Streaming** — Works with all providers

---

## Quick Start

```bash
# 1. Install
npm install -g @relayplane/cli @relayplane/proxy

# 2. Check setup
relayplane doctor

# 3. Start proxy
relayplane proxy start

# 4. Point your tools
export ANTHROPIC_BASE_URL=http://localhost:3001
export OPENAI_BASE_URL=http://localhost:3001
```

All API calls now route through RelayPlane. Works with OpenClaw, Cursor, Aider, Claude Code — any tool using standard SDKs.

---

## Skill Commands

| Command | Description |
|---------|-------------|
| `/relayplane stats` | Usage statistics and cost savings |
| `/relayplane status` | Proxy health and configuration |
| `/relayplane doctor` | Diagnose configuration issues |
| `/relayplane proxy [start\|stop]` | Manage the proxy |
| `/relayplane models` | List routing aliases |
| `/relayplane dashboard` | Cloud dashboard link |

---

## Model Routing Aliases

Use these in your API calls for smart routing:

| Alias | Routes To |
|-------|-----------|
| `rp:auto` | Best model for the task |
| `rp:cost` | Cheapest model (GPT-4o-mini) |
| `rp:fast` | Fastest model (Claude Haiku) |
| `rp:best` | Best quality (Claude Sonnet 4) |
| `rp:balanced` | Balance of cost & quality |

---

## Supported Providers

| Provider | Streaming | Tool Calling |
|----------|-----------|--------------|
| Anthropic (Claude) | ✅ | ✅ |
| OpenAI (GPT-4) | ✅ | ✅ |
| Google Gemini | ✅ | ✅ |
| xAI (Grok) | ✅ | ✅ |
| Moonshot | ✅ | ✅ |

---

## Requirements

- Node.js 18+
- API key for at least one provider

---

## Links

- [Documentation](SKILL.md) — Full setup guide
- [RelayPlane.com](https://relayplane.com) — Cloud features
- [GitHub](https://github.com/RelayPlane) — Source & issues

---

## License

MIT
