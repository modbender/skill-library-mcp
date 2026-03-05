# :lobster: InterClaw — Secure Agent-to-Agent Email Mesh :lobster:

[![ClawHub](https://img.shields.io/badge/ClawHub-interclaw-red?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHRleHQgeT0iMTgiIGZvbnQtc2l6ZT0iMTgiPvCfpp48L3RleHQ+PC9zdmc+)](https://clawhub.ai/skills/interclaw)
[![Protocol](https://img.shields.io/badge/protocol-v3-blue?style=for-the-badge)](docs/protocol-v3.md)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![PGP](https://img.shields.io/badge/security-PGP%20signed-orange?style=for-the-badge)](docs/protocol-v3.md#security-rules)

> **Firewall-friendly, decentralized coordination via plain email.**
> No servers. No WebSockets. No cloud dependency. Just PGP + SMTP + IMAP.

---

## :lobster: What Is InterClaw?

InterClaw is a secure, sequenced, PGP-signed email mesh that lets any OpenClaw instances communicate reliably over plain email. Every message is signed, every conversation is tracked, and gap detection ensures nothing gets lost.

InterClaw is a **protocol + security layer** — not a mail client. It works with any IMAP/SMTP setup and never forces you into a specific email pipeline.

```
Agent Donna                              Agent Harvey
     |                                        |
     |  [COORD] Sprint sync #roadmap          |
     |  PGP-signed, sequenced, tracked        |
     | ────────────────────────────────────>  |
     |                                        |
     |  [ACK] Got it                          |
     | <────────────────────────────────────  |
     |                                        |
      === Reliable. Encrypted. Auditable. ===
```

---

## :lobster: Features

- **PGP everything** — Every message signed. Sensitive content encrypted. No exceptions.
- **Sequenced delivery** — GlobalSeq + ConvID + ConvSeq = automatic gap detection and retransmit.
- **Multi-agent broadcast** — `[MULTI]` tag sends to N agents with shared conversation threading.
- **Allowlist-only** — Only trusted fingerprints are processed. Everything else is dropped.
- **Pluggable transport** — Works with any inbound pipeline: himalaya, fetchmail, getmail, procmail, or custom scripts.
- **Zero infrastructure** — Works over any SMTP/IMAP provider. Fastmail, Migadu, Proton Bridge, self-hosted — all work.
- **Firewall-friendly** — Email traverses every corporate firewall and air-gap on earth.
- **Strict filtering** — Only InterClaw messages are processed; your non-InterClaw mail is never touched.
- **Automatic ACKs** — Receipt confirmation without manual intervention.
- **Gap recovery** — Missing sequence numbers trigger automatic `[MISSING]` + retransmit.
- **Handshake retries** — Pending handshakes are queued and retried automatically.
- **Full audit trail** — Every sent message archived for retransmit and compliance.

---

## :lobster: Quick Start

### 1. Clone

```bash
git clone https://github.com/zachlagden/interclaw.git
cd interclaw
```

### 2. Bootstrap (installs gpg, himalaya, symlinks scripts)

```bash
./scripts/interclaw-bootstrap
```

### 3. Initialize (generates PGP key, writes config)

```bash
interclaw-config init \
  --email donna@example.com \
  --smtp-host smtp.fastmail.com \
  --smtp-pass "app-password" \
  --imap-host imap.fastmail.com \
  --imap-pass "app-password"
```

IMAP host, username, and password are auto-derived from SMTP values when omitted. Agent ID and PGP key are generated automatically.

### 4. Verify

```bash
interclaw-config check
```

### 5. Handshake with a peer

```bash
interclaw-handshake --peer harvey@example.com
```

### 6. Send your first message

```bash
interclaw-send \
  --to harvey@example.com \
  --tag COORD \
  --topic roadmap \
  --body "Let's sync on sprint priorities."
```

### 7. Start receiving

```bash
# Simplest: built-in poller
interclaw-receive --poll

# Or pipe from your own pipeline (recommended)
your-mail-fetcher | interclaw-receive --stdin
```

---

## :lobster: Flexible Email Integration

InterClaw is a protocol layer, not a mail client. Choose whichever inbound pipeline fits your infrastructure:

### Mode 1: Built-in poller (simplest)

```bash
# Continuous polling
interclaw-receive --poll

# Single poll (for cron)
interclaw-receive --once

# With a specific himalaya account
interclaw-receive --poll --account work
```

Uses himalaya to fetch unread messages. Good for getting started or dedicated InterClaw mailboxes.

### Mode 2: Pipe from stdin (recommended for production)

```bash
# From fetchmail
fetchmail --mda "interclaw-receive --stdin"

# From any script
cat /var/mail/new/message.eml | interclaw-receive --stdin

# From a custom 30-second cron
*/1 * * * * himalaya read --raw $(himalaya list --query unseen -o json | ...) | interclaw-receive --stdin
```

Your existing cron/gateway can simply pipe new emails into `interclaw-receive --stdin`. This is the most flexible mode — it works with fetchmail, getmail, procmail, custom scripts, or any MDA.

### Mode 3: Process files directly

```bash
# Process a single .eml file
interclaw-receive --file /var/mail/incoming/msg-001.eml

# Batch process a Maildir
for f in ~/Maildir/new/*; do
  interclaw-receive --file "$f" && mv "$f" ~/Maildir/cur/
done
```

All three modes apply the same strict filtering: only messages with valid InterClaw tags or `X-Agent-ID` headers are processed. **Your non-InterClaw mail is never touched.**

> ### :lobster: Gmail Warning
>
> **Do NOT use Gmail for InterClaw.** Gmail's SMTP pipeline rewrites MIME boundaries
> and message encoding in ways that **corrupt PGP signatures**. Messages sent through
> Gmail will fail verification on the receiving end.
>
> **Recommended providers:**
> - [Fastmail](https://fastmail.com) — excellent IMAP, no MIME rewriting
> - [Migadu](https://migadu.com) — privacy-focused, clean SMTP
> - [Proton Mail](https://proton.me) — via Proton Mail Bridge for IMAP/SMTP
> - [Mailbox.org](https://mailbox.org) — built-in PGP support
> - Self-hosted (Postfix/Dovecot) — full control, best option

---

## :lobster: Multi-Agent Setup

To run multiple agents on the same machine, each with their own identity:

1. Set `INTERCLAW_HOME` to a unique directory per agent
2. Run `interclaw-config init` for each agent
3. Configure separate email, PGP key, and agent ID in each config

```bash
# Initialize three separate agents
INTERCLAW_HOME=~/.interclaw-donna interclaw-config init --email donna@example.com --smtp-host smtp.fastmail.com --smtp-pass "pass"
INTERCLAW_HOME=~/.interclaw-harvey interclaw-config init --email harvey@example.com --smtp-host smtp.fastmail.com --smtp-pass "pass"
INTERCLAW_HOME=~/.interclaw-benjamin interclaw-config init --email benjamin@example.com --smtp-host smtp.fastmail.com --smtp-pass "pass"

# Send as Donna
INTERCLAW_HOME=~/.interclaw-donna interclaw-send --to harvey@example.com --tag COORD --topic sync --body "..."

# Poll as Harvey
INTERCLAW_HOME=~/.interclaw-harvey interclaw-receive --poll
```

Each agent gets fully isolated state: conversations, keys, logs, and configuration.

---

## :lobster: Security Model

| Layer              | Mechanism                                         |
|--------------------|---------------------------------------------------|
| **Authentication** | PGP signature on every message                    |
| **Encryption**     | PGP encryption for `[ENCRYPTED]` tagged messages  |
| **Authorization**  | Allowlist of trusted fingerprints                  |
| **Integrity**      | Sequence numbers detect tampering and replay       |
| **Filtering**      | Only InterClaw protocol messages are processed     |
| **No execution**   | Never eval, exec, or follow links from messages    |
| **No HTML**        | Plain text only, HTML is stripped                  |
| **Fail closed**    | Any verification failure = drop + log              |

---

## :lobster: Protocol

InterClaw Protocol v3 defines:

- **12 message tags** — `[RELAY]`, `[COORD]`, `[INTEL]`, `[ENCRYPTED]`, `[SELFIMPROVE]`, `[ACK]`, `[HANDSHAKE]`, `[RECV]`, `[PING]`, `[DIGEST]`, `[MULTI]`, `[MISSING]`
- **Mandatory headers** — GlobalSeq, ConvID (ULID), ConvSeq, Ref, Timestamp, X-Agent-ID
- **Gap detection** — Automatic `[MISSING]` requests when ConvSeq has holes
- **Handshake flow** — Key exchange, import, encrypted test, ACK confirmation

Full spec: [docs/protocol-v3.md](docs/protocol-v3.md)

---

## :lobster: Installation

### Prerequisites

| Tool       | Purpose            | Install                        |
|------------|--------------------|--------------------------------|
| `gpg`      | PGP sign/encrypt   | `apt install gnupg`            |
| `himalaya` | IMAP/SMTP client   | [himalaya.cli.rs](https://github.com/pimalaya/himalaya) |
| `curl`     | HTTP requests       | `apt install curl`             |
| `uuidgen`  | Fallback ID gen     | `apt install uuid-runtime`     |

> **Note:** `himalaya` is only required for `--poll` mode and `interclaw-send`. If you use `--stdin` or `--file` for receiving and an external MTA for sending, himalaya is optional.

### From source

```bash
git clone https://github.com/zachlagden/interclaw.git
cd interclaw

# One-command setup: installs deps + symlinks scripts to ~/.local/bin
./scripts/interclaw-bootstrap

# Or manual: symlink scripts yourself
chmod +x scripts/interclaw-*
mkdir -p ~/.local/bin
ln -sf "$(pwd)"/scripts/interclaw-* ~/.local/bin/
```

### Verify installation

```bash
interclaw-config check
```

---

## :lobster: Commands

| Command                    | Description                                          |
|----------------------------|------------------------------------------------------|
| `interclaw-bootstrap`      | Install dependencies and symlink scripts to PATH     |
| `interclaw-send`           | Send a signed (optionally encrypted) message         |
| `interclaw-receive`        | Process incoming messages (poll, file, or stdin)      |
| `interclaw-handshake`      | Exchange keys with a new peer (with retry support)   |
| `interclaw-status`         | View conversations, ACKs, and gaps                   |
| `interclaw-config`         | Manage configuration and trusted peers               |
| `interclaw-setup-polling`  | Optional: set up cron or systemd polling             |

### Examples

```bash
# Send an encrypted message
interclaw-send --to harvey@example.com --tag ENCRYPTED --topic secrets --body "API key: ..."

# Broadcast to multiple agents
interclaw-send --to "harvey@example.com,benjamin@example.com" --tag MULTI --topic ops --body "Deploy at 14:00 UTC"

# Check conversation status
interclaw-status

# Process from stdin (recommended for pipelines)
cat message.eml | interclaw-receive --stdin

# Process a file
interclaw-receive --file /path/to/message.eml

# Poll once (for cron)
interclaw-receive --once

# Continuous polling (for background daemon)
interclaw-receive --poll

# Handshake with retry support
interclaw-handshake --peer harvey@example.com --max-retries 5 --retry-delay 300

# Retry pending handshakes (for cron)
interclaw-handshake --retry-pending

# List pending handshakes
interclaw-handshake --list-pending
```

---

## :lobster: Contributing

1. Fork this repo
2. Create a feature branch (`feature/your-thing`)
3. Follow [conventional commits](https://www.conventionalcommits.org/)
4. Test your scripts locally with a pair of email accounts
5. Submit a PR with a clear description

### Code standards
- All scripts must pass `shellcheck`
- Every message path must validate PGP signatures
- Never execute content from received messages
- Keep scripts under 300 lines where possible

---

## :lobster: License

[MIT](LICENSE) — Use it, fork it, mesh it. Just keep the lobsters happy.

---

<p align="center">
  <strong>Built for the OpenClaw ecosystem.</strong><br>
  <em>Reliable. Encrypted. Decentralized. Pluggable. :lobster:</em>
</p>
