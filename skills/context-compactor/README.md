# Jasper Context Compactor

> Token-based context compaction for OpenClaw with local models (MLX, llama.cpp, Ollama)

## The Problem

Local LLMs don't report context overflow errors like cloud APIs do. When context gets too long, they either:
- Silently truncate your conversation
- Return garbage output
- Crash without explanation

OpenClaw's built-in compaction relies on error signals that local models don't provide.

## The Solution

Jasper Context Compactor estimates tokens client-side and proactively summarizes older messages before hitting your model's limit. No more broken conversations.

## Quick Start

```bash
npx jasper-context-compactor setup
```

**The setup will:**

1. ✅ **Back up your config** — Saves `openclaw.json` to `~/.openclaw/backups/` with restore instructions
2. ✅ **Ask permission** — Won't read your config without consent
3. ✅ **Detect local models** — Automatically identifies Ollama, llama.cpp, MLX, LM Studio providers
4. ✅ **Suggest token limits** — Based on your model's contextWindow from config
5. ✅ **Let you customize** — Enter your own values if auto-detection doesn't match
6. ✅ **Update config safely** — Adds the plugin with your chosen settings

### Supported Local Providers

The setup automatically detects these providers (primary or fallback):
- **Ollama** — Any provider with `ollama` in name or `:11434` in baseUrl
- **llama.cpp** — llamacpp provider
- **MLX** — mlx provider  
- **LM Studio** — lmstudio provider
- **friend-gpu** — Custom GPU servers
- **OpenRouter** — When routing to local models
- **Local network** — Any provider with localhost, 127.0.0.1, or Tailscale IP in baseUrl

Then restart OpenClaw:
```bash
openclaw gateway restart
```

## Privacy

🔒 **Everything runs 100% locally.** Nothing is sent to external servers.

The setup only reads your local `openclaw.json` file (with your permission) to detect your model and suggest appropriate limits.

## How It Works

1. Before each message, estimates total context tokens (chars ÷ 4)
2. If over `maxTokens`, splits messages into "old" and "recent"  
3. Summarizes old messages using your session model
4. Injects summary as context — conversation continues seamlessly

## Commands

After setup, use these in chat:

| Command | Description |
|---------|-------------|
| `/context-stats` | Show current token usage and limits |
| `/compact-now` | Clear cache and force fresh compaction |

## Configuration

The setup configures these values in `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "context-compactor": {
        "enabled": true,
        "config": {
          "maxTokens": 8000,
          "keepRecentTokens": 2000,
          "summaryMaxTokens": 1000,
          "charsPerToken": 4,
          "modelFilter": ["ollama", "lmstudio"]
        }
      }
    }
  }
}
```

| Option | Description |
|--------|-------------|
| `maxTokens` | Trigger compaction above this (set to ~80% of your model's context) |
| `keepRecentTokens` | Recent context to preserve (default: 25% of max) |
| `summaryMaxTokens` | Max tokens for the summary (default: 12.5% of max) |
| `charsPerToken` | Token estimation ratio (4 works for English) |
| `modelFilter` | (Optional) Only compact for these providers. If not set, compacts all sessions.

## Restoring Your Config

Setup always backs up first. To restore:

```bash
# List backups
ls ~/.openclaw/backups/

# Restore (use the timestamp from your backup)
cp ~/.openclaw/backups/openclaw-2026-02-11T08-00-00-000Z.json ~/.openclaw/openclaw.json

# Restart
openclaw gateway restart
```

## Uninstall

```bash
# Remove plugin files
rm -rf ~/.openclaw/extensions/context-compactor

# Remove from config (edit openclaw.json and delete the context-compactor entry)
# Or restore from backup
```

## Links

- **npm:** https://www.npmjs.com/package/jasper-context-compactor
- **GitHub:** https://github.com/E-x-O-Entertainment-Studios-Inc/openclaw-context-compactor
- **ClawHub:** https://clawhub.ai/skills/context-compactor

## License

MIT
