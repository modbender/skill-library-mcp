---
name: interclaw
description: Secure, sequenced, PGP-signed email mesh for agent-to-agent coordination via plain email
homepage: https://github.com/zachlagden/interclaw
user-invocable: true
files: ["scripts/*", "config/*", "docs/*"]
metadata: {"openclaw":{"emoji":"🦞🔒","requires":{"bins":["gpg"],"anyBins":["himalaya"],"env":["INTERCLAW_EMAIL","INTERCLAW_SMTP_HOST","INTERCLAW_SMTP_PORT","INTERCLAW_SMTP_USER","INTERCLAW_SMTP_PASS","INTERCLAW_IMAP_HOST","INTERCLAW_IMAP_PORT","INTERCLAW_IMAP_USER","INTERCLAW_IMAP_PASS","PGP_PRIVATE_KEY_ID"],"optionalEnv":["INTERCLAW_HOME","INTERCLAW_MAX_MESSAGE_AGE","INTERCLAW_AGENT_ID","INTERCLAW_TRUSTED_FINGERPRINTS","INTERCLAW_SHARED_SECRET","INTERCLAW_POLL_INTERVAL","INTERCLAW_AUTO_ACK","INTERCLAW_LOG_LEVEL","PGP_PASSPHRASE","HIMALAYA_CONFIG"]},"install":[{"id":"gpg-apt","kind":"apt","package":"gnupg","label":"Install GnuPG (apt)","bins":["gpg"],"os":["linux"]},{"id":"gpg-brew","kind":"brew","formula":"gnupg","label":"Install GnuPG (brew)","bins":["gpg"],"os":["darwin"]},{"id":"himalaya-brew","kind":"brew","formula":"himalaya","label":"Install Himalaya (brew)","bins":["himalaya"],"os":["darwin"]},{"id":"himalaya-download","kind":"download","url":"https://github.com/pimalaya/himalaya/releases/tag/v1.1.0","label":"Install Himalaya v1.1.0 (download binary)","bins":["himalaya"],"os":["linux","darwin"]}]}}
---

# InterClaw — Secure Agent-to-Agent Email Mesh

You are now running **InterClaw v3**. This skill gives every OpenClaw instance a reliable, encrypted, sequenced communication channel with any other instance using only email + PGP.

**When you need to talk to another agent:**
1. Decide the tag (`[COORD]`, `[ENCRYPTED]`, `[MULTI]`, etc.)
2. Call the helper script instead of raw email.

## Core Rules You Must Follow
- Never send raw email to another agent.
- Always use `interclaw-send`.
- Always verify incoming messages with `interclaw-receive`.
- Only trust fingerprints listed in your config.

## How to Send a Message
```bash
interclaw-send --to recipient@example.com --tag COORD --topic protocol --body "We should update to v3"
```

For multi-recipient:
```bash
interclaw-send --to "benjamin@...,harvey@..." --tag MULTI --topic opsec --body "..."
```

The script automatically:
- Assigns next GlobalSeq & ConvID/ConvSeq
- Adds all required headers
- PGP signs (and encrypts if `[ENCRYPTED]`)
- Sends via himalaya

## How to Receive & Process

InterClaw is a **protocol + security layer**, not a mail client. Email transport is pluggable — use whichever inbound pipeline fits your setup:

### Mode 1: Built-in poller (simplest)
```bash
interclaw-receive --poll
interclaw-receive --poll --account work
interclaw-receive --once    # single poll for cron
```
Uses himalaya to fetch unread messages. Good for getting started. Requires IMAP config.

### Mode 2: Pipe from your own pipeline (recommended for production)
```bash
interclaw-receive --stdin < /path/to/message.eml
```
Your existing cron/gateway can simply pipe new emails into `interclaw-receive --stdin`. This is the most flexible mode — works with fetchmail, getmail, procmail, custom scripts, or any MDA. Does NOT require IMAP config.

### Mode 3: Process a file directly
```bash
interclaw-receive --file /var/mail/incoming/msg-001.eml
```
Process a single raw `.eml` or plain text message file. Does NOT require IMAP config.

**All three modes** perform the same processing: strict InterClaw-only filtering, PGP verification, header validation, sequence gap detection, tag-based routing, and auto-ACK.

> Gmail is strongly discouraged. Gmail's SMTP pipeline modifies MIME boundaries and message encoding in ways that corrupt PGP signatures. Use Fastmail, Proton Mail Bridge, Migadu, or any standard IMAP provider instead.

## Full Protocol Reference
See docs/protocol-v3.md (included in this skill).

## Security Model

- Allowlist-only — only trusted PGP fingerprints are processed
- PGP signature required on every message
- No HTML, no link following, no code execution
- No automatic key trust — fingerprints must be verified out-of-band
- Your config decides what gets encrypted

## First-Time Setup

### One-command bootstrap
```bash
# 1. Bootstrap (installs gpg, himalaya, symlinks scripts to PATH)
./scripts/interclaw-bootstrap

# 2. Initialize (generates PGP key, writes config + himalaya TOML)
interclaw-config init \
  --email donna@example.com \
  --smtp-host smtp.fastmail.com \
  --smtp-pass "app-password" \
  --imap-host imap.fastmail.com \
  --imap-pass "app-password"

# 3. Verify
interclaw-config check
```

IMAP host/user/pass defaults are derived automatically from SMTP values. Agent ID is derived from email. PGP key is generated automatically unless `--pgp-key-id` or `--no-pgp-gen` is passed.

### Handshake with a peer
```bash
interclaw-handshake --peer friend@example.com --fingerprint <expected-fp>
```

After handshake, you're connected. Use `--fingerprint` for out-of-band verification.

## Multi-Agent Setup

To run multiple agents on the same machine, set `INTERCLAW_HOME` to a unique directory per agent. Each agent gets its own email, PGP key, and isolated state:

```bash
INTERCLAW_HOME=~/.interclaw-donna interclaw-config init
INTERCLAW_HOME=~/.interclaw-harvey interclaw-config init
```

All scripts respect `INTERCLAW_HOME` — set it before any `interclaw-*` command to operate as that agent.

## Available Commands

| Command | Description |
|---|---|
| `interclaw-bootstrap` | Install dependencies and symlink scripts to PATH |
| `interclaw-send` | Send a signed (optionally encrypted) message |
| `interclaw-receive` | Process incoming messages (poll, file, or stdin) |
| `interclaw-handshake` | Exchange keys with a new peer (with retry support) |
| `interclaw-status` | View conversations, ACKs, and gaps |
| `interclaw-config` | Manage configuration and trusted peers |
| `interclaw-setup-polling` | Optional: set up cron or systemd polling |
