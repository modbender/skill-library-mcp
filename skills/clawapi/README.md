# ClawAPI — OpenClaw Skill

**Model Switcher & Key Manager for OpenClaw**

A native macOS app that lets you switch AI models and manage API keys for OpenClaw. Supports 16 providers including OpenAI, Anthropic, xAI, Google, Groq, Ollama, LM Studio, and more.

## Install

**Option 1 — Download from GitHub Releases (recommended):**
Download the latest `.zip` from [GitHub Releases](https://github.com/Gogo6969/clawapi/releases), unzip, and move `ClawAPI.app` to `/Applications`.

**Option 2 — Install script:**
```bash
curl -fsSL https://raw.githubusercontent.com/Gogo6969/clawapi/main/install.sh | bash
```
The script downloads the signed `.zip` from GitHub Releases, verifies the SHA-256 checksum, and installs the app. [Review the script source](https://github.com/Gogo6969/clawapi/blob/main/install.sh) before running.

## Features

- One-click model switching across 16 providers
- Touch ID authentication for adding/deleting keys (password fallback without Touch ID)
- API keys stored in macOS Keychain (master copy) with a sync copy written to OpenClaw's `auth-profiles.json`
- JSON validation and `.bak` backups for config safety
- Apple Developer ID signed and notarized by Apple

## Security & Privacy

- API keys are stored in the macOS Keychain with hardware encryption; a sync copy is written to `auth-profiles.json` so OpenClaw can read them
- Touch ID / password authentication for sensitive operations
- No telemetry, no analytics, no data leaves your machine
- Only network requests: update check (GitHub) and local model discovery (Ollama/LM Studio)

## Links

- [GitHub](https://github.com/Gogo6969/clawapi)
- [Wiki](https://github.com/Gogo6969/clawapi/wiki)
- [User Guide](https://github.com/Gogo6969/clawapi/blob/main/docs/USER_GUIDE.md)

## License

MIT
