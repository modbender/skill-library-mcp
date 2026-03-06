---
name: fadnote
version: 1.0.1
description: Create secure shareable self-destructing notes
license: MIT
metadata:
  openclaw:
    emoji: 🔥
    requires:
      bins: ["node"]
      env: ["FADNOTE_URL"]
    primaryEnv: "FADNOTE_URL"
    homepage: https://github.com/easyFloyd/fadnote
---

# FadNote Skill

**Secure self-destructing shareable notes for OpenClaw**

Create encrypted, one-time-read notes directly from OpenClaw. The server never sees your plaintext.

---

## Overview

| Property | Value |
|----------|-------|
| **Name** | fadnote |
| **Version** | 1.0.1 |
| **Author** | easyFloyd |
| **License** | MIT |
| **Open Source** | ✅ Yes — https://github.com/easyFloyd/fadnote |
| **Runtime** | Node.js 18+ |

---

## Installation

```bash
# Via ClawHub
claw install fadnote

# Manual
git clone https://github.com/easyFloyd/fadnote.git
ln -s $(pwd)/fadnote/openclaw-skill/scripts/fadnote.js ~/.claw/bin/fadnote
```

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FADNOTE_URL` | `https://fadnote.com` | FadNote server endpoint |

---

## Usage

### From OpenClaw

```
user: Secure this API key: sk-abc123xyz

claw: I'll create a secure, self-destructing note for that.
      [runs: echo "sk-abc123xyz" | fadnote]

      🔗 https://fadnote.com/n/abc123# decryption-key-here

      Share it with the recipient via any channel and this link will self-destruct after first view.
```

### CLI Usage

```bash
# Direct text
fadnote "my secret message"

# From stdin
echo "secret" | fadnote
cat file.txt | fadnote
pbpaste | fadnote  # macOS clipboard
```

**Output:** Single line with the shareable URL.

---

## Triggers

**I (OpenClaw) will automatically use the FadNote skill when you say any of:**

- "Secure this [content]"
- "FadNote this [content]"  
- "Create a secure link for [content]"
- "Share this securely: [content]"
- "One-time note: [content]"
- "Encrypt and share [content]"

**With email delivery (if email skill is present):**
- "Secure this and email to [recipient]: [content]"
- "FadNote this to [email]"
- "Send secure note to [email]"

**Examples:**
```
- Secure this API key: sk-live-12345

- FadNote this password for the server

- Create a secure link for these credentials

- Share this securely: my private SSH key

- One-time note: the meeting location
```

---

## Security

- **Client-side encryption** — AES-256-GCM with PBKDF2 (100k iterations)
- **Zero knowledge** — Server receives only encrypted blobs
- **One-time read** — Note deleted immediately after first fetch
- **Auto-expire** — Default 24 hour TTL
- **🔓 Open Source** — Server code is publicly auditable at https://github.com/easyFloyd/fadnote

The decryption key is embedded in the URL fragment (`#key`) and never sent to the server.

---

## Files

```
openclaw-skill/
├── SKILL.md           # This file
└── scripts/
    └── fadnote.js     # Main CLI script (~60 lines)
```

---

## Requirements

- Node.js 18+ (no external dependencies)

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `FADNOTE_URL not set` | Environment variable missing | `export FADNOTE_URL=https://fadnote.com` |
| `Empty note` | No input provided | Pipe text into fadnote: `echo "secret" \| fadnote` |
| `404 Not Found` | Server endpoint wrong | Check `FADNOTE_URL` points to a running FadNote instance |
| `Connection refused` | Server unreachable | Verify server is up or use the live service |
| `Crypto not available` | Node.js < 18 | Upgrade to Node.js 18+ |

---

## Links

- **Live Service:** https://fadnote.com
- **Source:** https://github.com/easyFloyd/fadnote
- **Issues:** https://github.com/easyFloyd/fadnote/issues
