# Security Model

This document explains the security design of the discord-voice plugin, addressing common static-analysis flags.

## Dynamic Loading of extensionAPI.js (`src/core-bridge.ts`)

The plugin dynamically imports `dist/extensionAPI.js` from the host OpenClaw package. This is the standard integration pattern for all OpenClaw plugins (identical to the official `voice-call` plugin).

**Mitigations:**

- **Package integrity verification**: Before importing, the loader reads the candidate directory's `package.json` and asserts `"name": "openclaw"`. Any mismatch aborts with an error.
- **Normalized paths**: Override paths (`OPENCLAW_ROOT` env var or `openclawRoot` config) are resolved via `path.resolve()` to prevent `../` traversal.
- **Bounded search**: Auto-discovery only walks a limited set of known locations (cwd, script directory, `import.meta.url` ancestors, `node_modules/openclaw`). It does not scan arbitrary filesystem paths.
- **Single-load cache**: The resolved root is cached after first successful load, preventing TOCTOU races on subsequent calls.

## System Prompt Injection (`extraSystemPrompt`)

The plugin supplies an `extraSystemPrompt` when invoking the embedded agent. This is **expected and required** for a voice assistant: it tells the agent to keep responses brief, conversational, and TTS-friendly.

The prompt is constructed from:

| Component | Source | Sanitization |
|-----------|--------|-------------|
| `agentName` | Core config (admin-controlled) | Control chars stripped, capped at 100 chars |
| `noEmojiHint` | Plugin config (admin-controlled) | Control chars stripped, capped at 500 chars; or uses a hardcoded default string |
| `userId` | Discord API | Validated against `/^\d{17,20}$/` (Discord snowflake format); replaced with `"unknown"` if invalid |

**Threat model**: All prompt components originate from admin-controlled configuration or platform APIs, not from end-user input at runtime. An attacker would need write access to the server's configuration files to inject prompt content, at which point they already have full control of the agent.

## `noEmojiHint` Configuration

This config field controls a TTS-friendly hint injected into the agent prompt:

- `true` (default): Injects `"Do not use emojis—your response will be read aloud by a TTS engine."`
- `false`: No hint injected
- `string`: Custom text (sanitized: control characters stripped, max 500 characters)

The custom string option exists so administrators can tailor TTS behavior (e.g., for different languages or output formats). It is not exposed to end users.

## System Dependencies

| Dependency | Purpose | Required By |
|-----------|---------|-------------|
| `ffmpeg` | Audio format conversion (PCM/Opus/MP3) for voice channel I/O | Discord voice streaming |
| `build-essential` | C/C++ compiler for native Node.js addons | `@discordjs/opus` (Opus codec), `sodium-native` (libsodium for Discord voice encryption) |

These are **declarative prerequisites** listed in plugin metadata. The plugin does not install or execute these tools at runtime; they must be pre-installed by the system administrator. `ffmpeg` is invoked only through the `prism-media` library for audio transcoding. Native modules are loaded through Node.js's standard addon system.

## Reporting Vulnerabilities

If you discover a security vulnerability, please open a private issue or contact the maintainers directly rather than filing a public issue.
