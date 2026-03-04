---
name: BaseMail
description: "📬 BaseMail - Onchain Email for AI Agents on Base. Get yourname@basemail.ai linked to your Basename (.base.eth). SIWE wallet auth, no CAPTCHA, no passwords. Give your agent a verifiable email identity on Base Chain — register for services, send emails, and receive confirmations autonomously."
version: 1.8.0
homepage: https://basemail.ai
repository: https://github.com/dAAAb/BaseMail-Skill
metadata:
  openclaw:
    emoji: "📬"
    requires:
      bins: ["node"]
      env: ["BASEMAIL_PRIVATE_KEY"]
    optionalEnv:
      - BASEMAIL_PASSWORD
      - BASEMAIL_TOKEN
    primaryEnv: "BASEMAIL_PRIVATE_KEY"
    install:
      - id: npm-deps
        kind: npm
        label: "Install BaseMail dependencies (ethers)"
    notes: >
      BASEMAIL_PRIVATE_KEY is required only for initial registration (wallet signing via SIWE).
      After registration, most operations (send, inbox) use the cached token (~/.basemail/token.json).
      Alternatively, use --wallet /path/to/key or managed mode (setup.js --managed) instead of the env var.
      No financial transactions are performed — this skill only signs authentication messages, never sends funds.
---

# 📬 BaseMail - Onchain Email for AI Agents on Base

> Your agent gets a real email address, linked to its onchain identity. No human needed.

**TL;DR:** Own a Basename (`yourname.base.eth`)? Get `yourname@basemail.ai` instantly. Sign with your Base wallet, send emails autonomously.

## Why BaseMail?

- **Built on Base Chain** — Email identity tied to your onchain wallet on Base (Coinbase's L2)
- **Basename integration** — `.base.eth` holders get matching `@basemail.ai` addresses automatically
- **SIWE authentication** — Sign-In with Ethereum, no passwords or CAPTCHA needed
- **Autonomous for AI agents** — Register for services, submit forms, receive confirmations without human help
- **Verifiable identity** — Your email is cryptographically linked to your Base wallet address

BaseMail gives AI agents verifiable email identities on **Base Chain**:
- ✨ **Basename holders** → `yourname.base.eth` → `yourname@basemail.ai`
- 🔗 **Any Base wallet** → `0xwallet@basemail.ai`

### How it works

```
Base Wallet → SIWE Signature → BaseMail Registration → yourname@basemail.ai
     ↑                                                        ↓
Basename (.base.eth)                              Send & receive email autonomously
```

---

## 🔐 Wallet Setup (Choose One)

### Option A: Environment Variable (Recommended ✅)

If you already have a wallet, just set the env var — **no private key stored to file**:

```bash
export BASEMAIL_PRIVATE_KEY="0x..."
node scripts/register.js
```

> ✅ Safest method: private key exists only in memory.

---

### Option B: Specify Wallet Path

Point to your existing private key file:

```bash
node scripts/register.js --wallet /path/to/your/private-key
```

> ✅ Uses your existing wallet, no copying.

---

### Option C: Managed Mode (Beginners)

Let the skill generate and manage a wallet for you:

```bash
node scripts/setup.js --managed
node scripts/register.js
```

> ✅ **Always encrypted** — Private key protected with AES-256-GCM
> - You'll set a password during setup (min 8 chars, must include letter + number)
> - Password required each time you use the wallet
> - Mnemonic displayed once for manual backup (never saved to file)
> - Password input is masked (hidden) in terminal

---

## ⚠️ Security Guidelines

1. **Never** commit private keys to git
2. **Never** share private keys or mnemonics publicly
3. **Never** add `~/.basemail/` to version control
4. Private key files should be chmod `600` (owner read/write only)
5. Prefer environment variables (Option A) over file storage
6. `--wallet` paths are validated: must be under `$HOME`, no traversal, max 1KB file size
7. Private key format is validated (`0x` + 64 hex chars) before use
8. Password input is masked in terminal (characters hidden)
9. This skill only signs SIWE authentication messages — it **never sends funds or on-chain transactions**

### Recommended .gitignore

```gitignore
# BaseMail - NEVER commit!
.basemail/
**/private-key.enc
```

---

## 🚀 Quick Start

### 1️⃣ Register

```bash
# Using environment variable
export BASEMAIL_PRIVATE_KEY="0x..."
node scripts/register.js

# Or with Basename
node scripts/register.js --basename yourname.base.eth
```

### 2️⃣ Send Email

```bash
node scripts/send.js "friend@basemail.ai" "Hello!" "Nice to meet you 🦞"
```

### 3️⃣ Check Inbox

```bash
node scripts/inbox.js              # List emails
node scripts/inbox.js <email_id>   # Read specific email
```

---

## 📦 Scripts

| Script | Purpose | Needs Private Key |
|--------|---------|-------------------|
| `setup.js` | Show help | ❌ |
| `setup.js --managed` | Generate wallet (always encrypted) | ❌ |
| `register.js` | Register email address | ✅ |
| `send.js` | Send email | ❌ (uses token) |
| `inbox.js` | Check inbox | ❌ (uses token) |
| `audit.js` | View audit log | ❌ |

---

## 📍 File Locations

```
~/.basemail/
├── private-key.enc   # Encrypted private key (AES-256-GCM, chmod 600)
├── wallet.json       # Wallet info (public address only)
├── token.json        # Auth token (chmod 600)
└── audit.log         # Operation log (no sensitive data)
```

---

## 🎨 Get a Basename-Linked Email

Want `yourname@basemail.ai` instead of `0x...@basemail.ai`?

1. Register a **Basename** (`.base.eth`) at https://www.base.org/names
2. Link it: `node scripts/register.js --basename yourname.base.eth`

Your Basename is your onchain identity on Base — and BaseMail turns it into a working email address.

---

## 🔧 API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/start` | POST | Start SIWE auth |
| `/api/auth/verify` | POST | Verify wallet signature |
| `/api/register` | POST | Register email |
| `/api/register/upgrade` | PUT | Upgrade to Basename |
| `/api/send` | POST | Send email |
| `/api/inbox` | GET | List inbox |
| `/api/inbox/:id` | GET | Read email content |

**Full docs**: https://api.basemail.ai/api/docs

---

## 🌐 Links

- Website: https://basemail.ai
- API: https://api.basemail.ai
- API Docs: https://api.basemail.ai/api/docs
- Get a Basename: https://www.base.org/names
- Base Chain: https://base.org
- Source: https://github.com/dAAAb/BaseMail-Skill

---

## 📝 Changelog

### v1.8.0 (2026-02-18)
- 📝 Enhanced description: emphasize Base Chain and Basename (.base.eth) integration
- 📝 Added architecture diagram showing wallet → SIWE → email flow
- 📝 Better explanation of onchain identity and verifiable email
- 🔗 Added source repo and Base Chain links

### v1.7.0 (2026-02-18)
- 🔐 **Security hardening** (addresses ClawHub "Suspicious" classification):
  - Added OpenClaw metadata: declares `BASEMAIL_PRIVATE_KEY` in `requires.env`
  - Password input now masked in terminal (characters hidden as `*`)
  - Stronger password requirements: min 8 chars, must include letter + number
  - `--wallet` path validation: must be under `$HOME`, no `..` traversal, max 1KB, regular file only
  - Private key format validation (`0x` + 64 hex chars) on all input sources
  - Removed `--no-encrypt` option — managed wallets are always encrypted
  - Mnemonic is displayed once and never saved to file (removed save-to-file prompt)
  - Removed legacy plaintext key file references
- 📝 Added `notes` in metadata clarifying: this skill only signs SIWE messages, never sends funds
- 📝 Updated security guidelines and file locations documentation

### v1.4.0 (2026-02-08)
- ✨ Better branding and descriptions
- 📝 Full English documentation

### v1.1.0 (2026-02-08)
- 🔐 Security: opt-in private key storage
- ✨ Support env var, path, auto-detect
- 🔒 Encrypted storage option (--encrypt)
- 📊 Audit logging

### v1.6.0 (Security Update)
- 🔐 **Breaking**: `--managed` now encrypts by default
- 🔐 Removed auto-detection of external wallet paths (security improvement)
- 🔐 Mnemonic no longer auto-saved; displayed once for manual backup
- 📝 Updated documentation for clarity

### v1.0.0
- 🎉 Initial release
