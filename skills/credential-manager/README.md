# Credential Manager Skill

**Status:** ✅ Production Ready  
**Category:** 🔒 Core Security Infrastructure  
**Package:** `credential-manager.skill`  
**Version:** 1.3.0

## What This Is

**MANDATORY security foundation for OpenClaw.**

This skill consolidates scattered API keys and credentials into a secure, centralized `.env` file. This is not optional — it's a core requirement for secure OpenClaw deployments.

## Why This Matters

Scattered credentials = scattered attack surface. One `.env` file with proper permissions is:
- ✅ Easier to secure (one file, one permission)
- ✅ Easier to audit (one location to check)
- ✅ Easier to rotate (update once, everywhere works)
- ✅ Harder to leak (git-ignored by default)

## 🎯 The Consolidation Rule (v1.3.0)

**ALL credentials MUST be in `~/.openclaw/.env` ONLY.**

No workspace, no skills, no scripts directories. Root only. No exceptions.

**Why?**
- **Security:** One file to secure (mode 600), one file to audit
- **Simplicity:** Scripts know exactly where to look
- **Git safety:** Single .gitignore rule protects everything
- **Backup:** One file to backup/restore
- **Portability:** Copy one file = entire credential set moves

This skill now actively **enforces** this rule by:
1. Scanning workspace, skills, and scripts directories for scattered `.env` files
2. Consolidating everything into root `.env` with backups
3. Cleaning up scattered files after migration
4. Validating no scattered credentials remain

See `CONSOLIDATION-RULE.md` and `CORE-PRINCIPLE.md` for full rationale.

## 🔐 Crypto-Specific Detection (New in v1.2.0)

Enhanced detection for blockchain and cryptocurrency credentials:

- **Private keys** (`private_key`, `private-key`)
- **Passphrases** (`passphrase`)
- **Mnemonics** (`mnemonic`)
- **Seed phrases** (`seed_phrase`, `seed-phrase`)
- **Signing keys** (`signing_key`, `signing-key`)
- **Wallet keys** (`wallet_key`, `wallet-key`)

**Why it matters:** Crypto credentials are permanent secrets. Once leaked, funds can be drained instantly with no recovery. These patterns ensure wallet keys and seed phrases get the same security treatment as API keys.

## What It Does

1. **Scans** for credentials across common locations
2. **Backs up** existing credential files safely  
3. **Consolidates** everything into `~/.openclaw/.env`
4. **Secures** with proper permissions (600)
5. **Validates** security and format
6. **Cleans up** old files after migration

## Quick Start

```bash
# Install from ClawHub
clawhub install credential-manager

# Or manually copy credential-manager/ to your OpenClaw skills directory

# Navigate to the skill
cd ~/.openclaw/skills/credential-manager  # or your skills directory

# Scan for credentials
./scripts/scan.py

# Consolidate into .env
./scripts/consolidate.py

# Validate security
./scripts/validate.py

# (Optional) Clean up old files
./scripts/cleanup.py --confirm
```

## Files Included

```
credential-manager/
├── SKILL.md                         # Main skill documentation
├── CORE-PRINCIPLE.md                # Why centralized credentials are mandatory
├── CONSOLIDATION-RULE.md            # The single source principle (NEW v1.3.0)
├── scripts/
│   ├── scan.py                      # Scan for credential files
│   ├── consolidate.py               # Merge into .env
│   ├── validate.py                  # Security validation
│   ├── enforce.py                   # Fail-fast security enforcement
│   └── cleanup.py                   # Remove scattered files
└── references/
    ├── security.md                  # Security best practices
    └── supported-services.md        # Known service patterns
```

## Supported Services

- **Social:** X (Twitter), Molten, Moltbook, Botchan/4claw
- **AI:** OpenAI, Anthropic, Google/Gemini, OpenRouter
- **Dev:** GitHub, GitLab
- **Cloud:** AWS, GCP, Azure
- **Databases:** PostgreSQL, MongoDB, Redis
- **Communication:** Telegram, Discord, Slack, WhatsApp
- **Payment:** Stripe, PayPal
- **Web3:** Ethereum, Solana
- **Storage:** S3, R2, IPFS/Pinata
- **And many more...**

See `references/supported-services.md` for the full list.

## Security Features

✅ **File permissions** - Sets .env to mode 600 (owner only)  
✅ **Git protection** - Creates/updates .gitignore  
✅ **Backups** - Timestamped backups before changes  
✅ **Validation** - Checks format, permissions, duplicates  
✅ **Template** - Creates .env.example (safe to share)  
✅ **Documentation** - Comprehensive security guide

## Usage Examples

### Scan Only
```bash
./scripts/scan.py
```

### Consolidate with Confirmation
```bash
./scripts/consolidate.py
# (Prompts before making changes)
```

### Auto-Confirm Mode
```bash
./scripts/consolidate.py --yes
```

### Validate
```bash
./scripts/validate.py
```

### Fix Issues Automatically
```bash
./scripts/validate.py --fix
```

### Cleanup (Dry Run)
```bash
./scripts/cleanup.py
# Shows what would be deleted
```

### Cleanup (Actually Delete)
```bash
./scripts/cleanup.py --confirm
```

## Testing

The skill has been tested on the current OpenClaw installation and successfully:

- ✅ Scans existing .env file and workspace directories
- ✅ Detects scattered .env files in skills/scripts/workspace
- ✅ Consolidates credentials with backup
- ✅ Validates format (23 keys found after consolidation)
- ✅ Validates permissions (600)
- ✅ Validates .gitignore protection
- ✅ No security warnings
- ✅ Enforces consolidation rule (root .env only)

## Distribution

The skill is packaged as `credential-manager.skill` (a zip file with .skill extension).

To share:
1. Send the `.skill` file
2. Recipient extracts to their OpenClaw skills directory
3. Scripts are immediately usable

## Migration Story

This skill was created based on a real migration where we:
1. Found credentials scattered across 4 locations
2. Consolidated into `~/.openclaw/.env`
3. Created unified API scripts (x_post.py, molten.sh, moltbook.sh)
4. Validated security
5. Cleaned up old files

The process took ~10 minutes and consolidated credentials for X, Molten, Moltbook, and Botchan.

## Future Enhancements

Potential additions:
- Interactive TUI for easier navigation
- Integration with secret managers (1Password, etc.)
- Automatic key rotation reminders
- Multi-environment support (.env.dev, .env.prod)
- Encryption at rest option

## Support

For issues or questions:
- Read SKILL.md for detailed documentation
- Check references/ for security guides
- All scripts support --help flag

## License

Part of the OpenClaw project.

---

**Created:** 2026-02-05  
**Author:** Mr. Tee (OpenClaw Agent)  
**Tested:** ✅ Production Ready
