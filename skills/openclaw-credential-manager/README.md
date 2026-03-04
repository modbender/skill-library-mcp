# Credential Manager Skill

**Status:** ✅ Production Ready  
**Category:** 🔒 Core Security Infrastructure  
**Package:** `credential-manager.skill`  
**Version:** 2.0.0

## What This Is

**MANDATORY security foundation for OpenClaw.**

Consolidate scattered API keys and credentials into a secure `.env` file. Encrypt high-value secrets with GPG. Track credential rotation. Detect hardcoded secrets in source files.

This is not optional — it's a core requirement for secure OpenClaw deployments.

## What's New in v2.0.0

- 🔐 **GPG encryption** for private keys and wallet secrets (AES256)
- 🔍 **Deep scanning** for hardcoded secrets in source files
- 🔄 **Rotation tracking** with risk-based schedules
- 🛡️ **Backup hardening** (mode 600 files, 700 directories)
- 📊 **Entropy analysis** and private key detection in validation
- 🔗 **Symlink detection** for `.env` files
- 🐛 **Fixed** validate.py quote contradiction
- 🐛 **Fixed** backup permissions (were 644, now 600)

## Why This Matters

Scattered credentials = scattered attack surface. One `.env` file with proper permissions is:
- ✅ Easier to secure (one file, one permission)
- ✅ Easier to audit (one location to check)
- ✅ Easier to rotate (update once, everywhere works)
- ✅ Harder to leak (git-ignored by default)
- ✅ Encrypted at rest (private keys in GPG)

## Quick Start

```bash
# Navigate to the skill
cd /path/to/skills/credential-manager

# Step 1: Scan (find all credential files)
./scripts/scan.py --deep

# Step 2: Consolidate into .env
./scripts/consolidate.py

# Step 3: Validate security
./scripts/validate.py --fix

# Step 4: Setup GPG and encrypt private keys
./scripts/setup-gpg.sh
./scripts/encrypt.py --keys MAIN_WALLET_PRIVATE_KEY,CUSTODY_PRIVATE_KEY

# Step 5: Initialize rotation tracking
./scripts/rotation-check.py --init

# Step 6: Cleanup old files
./scripts/cleanup.py --confirm
```

## The Consolidation Rule

**ALL credentials MUST be in `~/.openclaw/.env` ONLY.**

No workspace, no skills, no scripts directories. Root only. No exceptions.

See `CONSOLIDATION-RULE.md` and `CORE-PRINCIPLE.md` for full rationale.

## Files Included

```
credential-manager/
├── SKILL.md                         # Full documentation + migration workflow
├── README.md                        # This file
├── CHANGELOG.md                     # Version history
├── CORE-PRINCIPLE.md                # Why centralized credentials are mandatory
├── CONSOLIDATION-RULE.md            # The single source principle
├── scripts/
│   ├── scan.py                      # Scan for credential files + deep scan
│   ├── consolidate.py               # Merge into .env with secure backups
│   ├── validate.py                  # Security validation + entropy analysis
│   ├── enforce.py                   # Fail-fast enforcement + GPG decryption
│   ├── encrypt.py                   # GPG encrypt/decrypt high-value secrets
│   ├── setup-gpg.sh                 # First-time GPG configuration
│   ├── rotation-check.py            # Credential rotation tracking
│   └── cleanup.py                   # Remove scattered credential files
└── references/
    ├── security.md                  # Security best practices
    └── supported-services.md        # Known service patterns
```

## Output Structure

After full migration:

```
~/.openclaw/
├── .env                     # All credentials (mode 600, private keys = GPG:*)
├── .env.secrets.gpg         # GPG-encrypted private keys (mode 600, AES256)
├── .env.meta                # Rotation tracking metadata (mode 600)
├── .env.example             # Template (safe to share)
├── .gitignore               # Protects .env, .env.secrets.gpg, .env.meta
└── backups/                 # (mode 700)
    └── credentials-old-YYYYMMDD/  # (mode 700)
        └── *.bak            # Backup files (mode 600)
```

## GPG Encryption

Private keys and wallet secrets should never exist as plaintext on disk:

```bash
# Encrypt (moves to .env.secrets.gpg, replaces with GPG: placeholder)
./scripts/encrypt.py --keys WALLET_PRIVATE_KEY,SIGNER_PRIVATE_KEY

# List encrypted keys
./scripts/encrypt.py --list

# Decrypt back to plaintext
./scripts/encrypt.py --decrypt --keys WALLET_PRIVATE_KEY
```

Scripts access encrypted credentials transparently:
```python
from enforce import get_credential
key = get_credential('WALLET_PRIVATE_KEY')  # Auto-decrypts from GPG
```

## Rotation Tracking

```bash
# Initialize (auto-classifies risk levels)
./scripts/rotation-check.py --init

# Check status
./scripts/rotation-check.py

# Record a rotation
./scripts/rotation-check.py --rotated API_KEY
```

Risk levels: Critical (90d), Standard (180d), Low (365d).

## Deep Scanning

```bash
# Scan source files for hardcoded secrets
./scripts/scan.py --deep
```

Detects: `sk_`/`pk_` prefixes, `0x` + 64 hex (private keys), hardcoded credential assignments, mnemonic phrases. Excludes `node_modules/` and `.git/`.

## Supported Services

- **Social:** X (Twitter), Farcaster, Molten, Moltbook, Botchan/4claw
- **AI:** OpenAI, Anthropic, Google/Gemini, OpenRouter
- **Web3:** Ethereum wallets, Coinbase/CDP, Farcaster custody/signer keys
- **Dev:** GitHub, GitLab
- **Communication:** Telegram, Discord, Slack
- **And many more...** (see `references/supported-services.md`)

## Security Features

✅ **File permissions** — `.env` at mode 600 (owner only)
✅ **Directory permissions** — Backups at mode 700 (owner only)
✅ **GPG encryption** — Private keys encrypted at rest (AES256)
✅ **Git protection** — `.env`, `.env.secrets.gpg`, `.env.meta` all git-ignored
✅ **Entropy analysis** — Flags weak/placeholder values for secret fields
✅ **Private key detection** — Flags plaintext `0x` + 64 hex values
✅ **Mnemonic detection** — Flags 12/24 word seed phrases
✅ **Deep scanning** — Finds hardcoded secrets in source files
✅ **Symlink detection** — Validates symlinked `.env` targets
✅ **Rotation tracking** — Risk-based rotation schedules with warnings
✅ **Backup hardening** — All backups secured with proper permissions
✅ **Fail-fast enforcement** — Skills refuse to run if credentials insecure

## Testing

Tested on a live OpenClaw deployment:

- ✅ Scanned and found 4 credential files (1 with insecure permissions)
- ✅ Deep scan caught 2 hardcoded test keys in scripts
- ✅ Consolidated Farcaster, Moltbook, Basecred credentials into `.env`
- ✅ GPG-encrypted 5 private keys (wallet + 4 Farcaster)
- ✅ Fixed 12 backup permission issues
- ✅ Initialized rotation tracking for 57 keys
- ✅ Updated 4 scripts to use `.env` with GPG decryption
- ✅ All validation checks pass

## Installation

### From ClawHub
```bash
clawhub install credential-manager
```

### Manual
```bash
# Copy to your skills directory
cp -r credential-manager/ ~/.openclaw/skills/
# or
cp -r credential-manager/ /path/to/openclaw/skills/
```

## License

Part of the OpenClaw project.

---

**Created:** 2026-02-05  
**Updated:** 2026-02-11  
**Author:** Mr. Tee (OpenClaw Agent)  
**Tested:** ✅ Production Ready (v2.0.0)
