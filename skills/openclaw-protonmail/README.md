# ProtonMail Skill for OpenClaw

[![CI](https://github.com/rvacyber/openclaw-protonmail-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/rvacyber/openclaw-protonmail-skill/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://www.typescriptlang.org/)

Connect your OpenClaw agent to ProtonMail via Proton Mail Bridge for secure email management.

> ⚠️ **Beta Software**: This skill is in active development with limited production testing. Core functionality (read, send, search) is working, but edge cases and real-world usage patterns are still being validated. We're actively seeking feedback from early adopters to identify issues and improve reliability before a stable 1.0 release. Please report bugs and share your experience!

> ✅ **Security Feedback Response (2026-02-26)**: We reviewed community scanner feedback and shipped hardening updates:
> - Removed insecure TLS bypass config (`rejectUnauthorized: false`)
> - Enforced localhost-only Bridge hosts (`127.0.0.1`, `localhost`, `::1`)
> - Hardened IMAP query parsing with strict input validation/sanitization
> 
> See [CHANGELOG.md](./CHANGELOG.md) and PR #2 for full details.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Upgrade Notice (Security Patch)](#upgrade-notice-security-patch)
- [Development](#development)
- [Security Feedback Response](#security-feedback-response)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Overview

This skill enables OpenClaw to read, send, and manage emails through your ProtonMail account using the official Proton Mail Bridge. Bridge provides local IMAP/SMTP access to your encrypted ProtonMail account while maintaining end-to-end encryption.

## Features

- ✉️ Read emails (inbox, sent, folders)
- 📤 Send emails (plain text and HTML)
- 💬 Reply to emails
- 🔍 Search emails (from, subject, body, date filters)
- 📎 Read attachments (sending attachments: coming soon)
- 🔒 Secure: Uses official Proton Bridge, credentials stored locally

## Requirements

- **Proton Mail Bridge** — [Download from Proton](https://proton.me/mail/bridge)
- **ProtonMail account** (Free or paid)
- **OpenClaw** v2024.1.0+
- **Node.js** 18+ (for development)

## Installation

### 1. Install Proton Mail Bridge

#### macOS (Homebrew)
```bash
brew install --cask proton-mail-bridge
```

#### Linux / Windows
Download from https://proton.me/mail/bridge

### 2. Configure Proton Mail Bridge

1. **Launch Proton Mail Bridge**
   ```bash
   open -a "Proton Mail Bridge"  # macOS
   # or launch from Applications
   ```

2. **Sign in with your ProtonMail account**
   - Enter your ProtonMail email and password
   - Complete any 2FA if enabled

3. **Skip email client setup**
   - Bridge will show "Select your email client" (Apple Mail, Outlook, Thunderbird, Other)
   - **Click "Setup later"** — we're connecting OpenClaw directly, not a desktop email client

4. **Get your Bridge credentials**
   - Open Bridge settings/preferences
   - Select your account (e.g., `your-email@pm.me`)
   - Go to "Mailbox configuration" or "IMAP/SMTP settings"
   - Click "Show password" to reveal the Bridge-generated password
   - **Important:** This is NOT your ProtonMail password — it's a separate password Bridge generates

5. **Note your connection settings:**
   - IMAP: `127.0.0.1:1143`
   - SMTP: `127.0.0.1:1025`
   - Username: `your-email@pm.me`
   - Password: Bridge-generated password (from step 4)

### 3. Install the Skill

```bash
# Clone the repo
git clone https://github.com/rvacyber/openclaw-protonmail-skill.git
cd openclaw-protonmail-skill

# Install dependencies
npm install

# Link to OpenClaw skills directory
npm run install-skill
```

### 4. Configure OpenClaw

Add to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "protonmail": {
        "enabled": true,
        "env": {
          "PROTONMAIL_ACCOUNT": "your-email@pm.me",
          "PROTONMAIL_BRIDGE_PASSWORD": "bridge-generated-password"
        }
      }
    }
  }
}
```

**Important Notes:**
- Use `skills.entries.protonmail` (not `skills.protonmail`)
- Credentials are stored locally in your OpenClaw config
- Never commit your config with real credentials to version control
- The Bridge password is separate from your ProtonMail password

## Usage

Once installed, OpenClaw can use ProtonMail commands:

```
You: Check my ProtonMail inbox
Agent: [uses protonmail skill to fetch recent emails]

You: Send an email to alice@example.com about the meeting
Agent: [drafts and sends email via ProtonMail]
```

## Commands

The skill provides these tool functions to OpenClaw:

- `protonmail-list-inbox` — List recent inbox messages
- `protonmail-search` — Search emails by query
- `protonmail-read` — Read a specific email by ID
- `protonmail-send` — Send a new email
- `protonmail-reply` — Reply to an email thread


## Upgrade Notice (Security Patch)

If you installed version `0.1.0`, upgrade to `0.1.1` when released.

- `0.1.0` contains security-hardening gaps identified by scanner feedback
- `0.1.1` remediates these findings
- Advisory details: [docs/SECURITY-ADVISORY-2026-02-26.md](./docs/SECURITY-ADVISORY-2026-02-26.md)

## Development

### Setup

```bash
git clone https://github.com/rvacyber/openclaw-protonmail-skill.git
cd openclaw-protonmail-skill
npm install
npm run dev
```

### Testing

```bash
npm test
```

### Project Structure

```
openclaw-protonmail-skill/
├── SKILL.md          # OpenClaw skill manifest
├── README.md         # This file
├── package.json      # Node.js dependencies
├── src/
│   ├── index.ts      # Main skill entry point
│   ├── imap.ts       # IMAP client for reading emails
│   ├── smtp.ts       # SMTP client for sending emails
│   └── tools.ts      # Tool definitions for OpenClaw
├── test/
│   └── integration.test.ts
└── examples/
    └── config-example.json
```

## Security Feedback Response

We take security findings seriously and act on them quickly.

On **2026-02-26**, we reviewed scanner feedback that flagged two potential risks and implemented fixes:

1. **TLS Configuration Hardening**
   - Removed insecure TLS override settings.
   - Clarified and enforced localhost-only Bridge networking.

2. **IMAP Search Input Hardening**
   - Added input validation (length limits, control-character blocking).
   - Added value allowlisting for parsed search filters.
   - Limited parsing to supported filter operators only.

If you spot additional concerns, open a GitHub issue with reproduction steps and we’ll triage promptly.

## Security

- **Proton Bridge runs locally** — No third-party services involved
- **End-to-end encryption maintained** — Bridge decrypts locally, encrypted in transit to Proton servers
- **Credentials never leave your machine** — Stored in OpenClaw config, never logged or transmitted
- **Localhost-only connections** — IMAP/SMTP traffic stays on your machine (unencrypted localhost is acceptable)
- **Open source** — Audit the code yourself

### Security Notes

- Bridge uses ports 1143 (IMAP) and 1025 (SMTP) on `127.0.0.1` (localhost only)
- Current implementation uses plain connections (no TLS) because traffic never leaves your machine
- Bridge password is separate from ProtonMail password (defense in depth)
- Never commit `openclaw.json` with real credentials to version control

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Created by **Jim Staley** ([@rvacyber](https://github.com/rvacyber)) — contact: info@rvacyber.com.

Inspired by the [gog](https://github.com/steipete/gog) skill for Google Workspace.

## Support

- 🐛 **Issues:** https://github.com/rvacyber/openclaw-protonmail-skill/issues
- 💬 **Discussions:** https://github.com/openclaw/openclaw/discussions
- 📖 **OpenClaw Docs:** https://docs.openclaw.ai

---

**Made with 🔐 for the OpenClaw community**
