# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this skill, **do not open a public issue**. Instead, email us directly:

**security@web2labs.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected tool(s) or file(s)
- Potential impact

We will acknowledge receipt within 48 hours and provide a fix timeline within 5 business days.

## Security Posture

This skill is designed to meet OpenClaw's "treat tools as code" security expectations.

### What this skill does

- Communicates with `web2labs.com` over HTTPS to upload videos and retrieve results.
- Stores your API key locally in `~/.openclaw/openclaw.json` with `chmod 600` permissions.
- Downloads URL-based videos locally via `yt-dlp` — files never pass through third-party intermediaries.
- Sends signed webhook callbacks (HMAC-SHA256) when configured.

### What this skill never does

- Executes arbitrary shell commands.
- Uploads data to any service other than Web2Labs.
- Sends API keys or secrets to third-party domains (auth headers are stripped for non-Web2Labs URLs).
- Logs or displays full API key values.
- Uses your content for AI model training.

### Data retention

- **Free users:** uploads deleted 2 hours after processing.
- **Paid users:** retention per subscription plan.
- All processing happens on Web2Labs infrastructure; no data is shared with third parties.

### Dependency audit

This skill uses a minimal dependency set:

| Package | Purpose |
|---------|---------|
| `@modelcontextprotocol/sdk` | MCP protocol (required by OpenClaw) |
| `node-fetch` | HTTP client |
| `form-data` | Multipart file uploads |
| `socket.io-client` | Real-time progress updates |
| `zod` | Input schema validation |

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |
