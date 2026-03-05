---
name: x-twitter-by-altf1be
description: "Post tweets, threads, and media to X/Twitter via API v2 — secure OAuth 1.0a, no external npm dependencies."
homepage: https://github.com/ALT-F1-OpenClaw/openclaw-skill-x-twitter
metadata:
  {"openclaw": {"emoji": "🐦", "requires": {"env": ["X_CONSUMER_KEY", "X_CONSUMER_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]}, "primaryEnv": "X_CONSUMER_KEY"}}
---

# X/Twitter by @altf1be

Post tweets, threads, and media to X/Twitter via the X API v2 with secure OAuth 1.0a signing.

## Setup

1. Get API keys from https://developer.x.com
2. Set environment variables (or create `.env` in `{baseDir}`):

```
X_CONSUMER_KEY=your-api-key
X_CONSUMER_SECRET=your-api-secret
X_ACCESS_TOKEN=your-access-token
X_ACCESS_TOKEN_SECRET=your-access-token-secret
```

3. Install dependencies: `cd {baseDir} && npm install`

## Commands

```bash
# Verify connection
node {baseDir}/scripts/xpost.mjs verify

# Post a tweet
node {baseDir}/scripts/xpost.mjs tweet "Hello from OpenClaw! 🦞"

# Post with image
node {baseDir}/scripts/xpost.mjs tweet "Check this out!" --media ./screenshot.png

# Reply to a tweet
node {baseDir}/scripts/xpost.mjs tweet "Great point!" --reply 1234567890

# Post a thread (inline)
node {baseDir}/scripts/xpost.mjs thread "First tweet" "Second tweet" "Third tweet"

# Post a thread (from file, tweets separated by ---)
node {baseDir}/scripts/xpost.mjs thread --file ./thread.md
```

## Thread file format

Create a file with tweets separated by `---`:

```
🚀 Announcing something cool!
---
Here's why it matters...
---
Check it out: https://example.com
#OpenSource #AI
```

## Security

- OAuth 1.0a user context signing (no app-only auth for write operations)
- No credentials printed to stdout
- API calls use pure Node.js `fetch` + built-in `node:crypto` (no third-party HTTP or OAuth libraries)
- Minimal dependencies: only `commander` (CLI framework) and `dotenv` (env loading)

## Author

Abdelkrim BOUJRAF — [ALT-F1 SRL](https://www.alt-f1.be), Brussels 🇧🇪
X: [@altf1be](https://x.com/altf1be)
