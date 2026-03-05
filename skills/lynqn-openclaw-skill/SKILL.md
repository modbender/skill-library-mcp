# LYNQN Skill

**Share text, generate QR codes, and shorten URLs from any OpenClaw agent.**

- **Name**: lynqn
- **Version**: 1.0.1
- **Category**: Productivity
- **License**: MIT
- **Homepage**: https://lynqn.io/agents

## Install

```bash
openclaw skill install lynqn
```

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/lynqn share` | Create a shareable text or code snippet | `/lynqn share <text> [--syntax] [--expires 1d\|1w\|1m\|3m]` |
| `/lynqn qr` | Generate a QR code from text or URL | `/lynqn qr <content> [--size 200-800] [--error L\|M\|Q\|H]` |
| `/lynqn shorten` | Shorten a long URL | `/lynqn shorten <url>` |
| `/lynqn stats` | Get LYNQN platform statistics | `/lynqn stats` |

## Quick Examples

```bash
# Share text with a 1-week expiry
/lynqn share Hello from my agent!

# Share code with syntax highlighting
/lynqn share const x = 42; console.log(x); --syntax --expires 1w

# Generate a QR code
/lynqn qr https://lynqn.io --size 400 --error H

# Shorten a URL
/lynqn shorten https://example.com/very/long/path/to/resource

# Check platform stats
/lynqn stats
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LYNQN_API_URL` | `https://lynqn.io/api` | API endpoint |

## Permissions Required

- `network.http` — Make HTTP requests to LYNQN API

## Rate Limits

| Tier | Requests/hour | Expiration | Notes |
|------|--------------|------------|-------|
| Free | 100 | 90 days | No token required |
| Pro (100k+ $LYNQN) | 1,000 | 180 days | Analytics included |
| Premium (1M+ $LYNQN) | 10,000 | 365 days | Custom QR branding |

## API Endpoints

### POST /api/share
Create a shareable snippet.

```json
{
  "content": "Your text here",
  "format": "text",
  "expiresIn": 604800
}
```

### POST /api/shorten
Shorten a URL.

```json
{
  "url": "https://example.com/long/path"
}
```

### GET /api/stats
Returns platform statistics.

## Links

- Website: https://lynqn.io
- Agent Docs: https://lynqn.io/agents
- Tokenomics: https://lynqn.io/tokenomics
- Issues: https://github.com/lynqn/lynqn-openclaw-skill/issues
