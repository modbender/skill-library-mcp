# Changelog

## Version 1.3.0 (2026-02-07)

### 🎯 Consolidation Rule - Single Source Enforcement

**Major update:** Formal enforcement of the single source principle — all credentials MUST be in `~/.openclaw/.env` ONLY.

### Added

**CONSOLIDATION-RULE.md** - New comprehensive documentation:
- The single source principle explained
- Why root-only (no workspace, skills, scripts .env files)
- Enforcement workflow (scan → consolidate → cleanup → validate)
- Security rationale (one file to secure, audit, backup)
- Developer guidance (how to load from root .env)
- Exception handling (node_modules .env files are harmless)

**Enhanced scan.py detection patterns:**
- `~/.openclaw/workspace/.env`
- `~/.openclaw/workspace/.env.*`
- `~/.openclaw/workspace/skills/*/.env`
- `~/.openclaw/workspace/skills/*/repo/.env`
- `~/.openclaw/workspace/scripts/.env`

**Enhanced cleanup.py:**
- Updated header to explicitly mention rule enforcement
- Removes scattered .env files from workspace/skills/scripts
- Preserves backups for safety

**Updated SKILL.md:**
- Prominently references CONSOLIDATION-RULE.md
- Added "THE RULE" section upfront
- Emphasizes root-only requirement

### Changed

**Documentation structure:**
- README.md now includes "The Consolidation Rule" section
- Files included list updated with CONSOLIDATION-RULE.md
- Testing section reflects enhanced detection

### Why This Matters

Scattered `.env` files across workspace, skills, and scripts directories create:
- Multiple attack surfaces (multiple files to secure)
- Confusion (which .env has the current keys?)
- Git leaks (harder to protect multiple locations)
- Backup gaps (easy to miss scattered files)

**The rule:** One file. One location. One source of truth. No exceptions.

### Technical Details

**New files:** 1 (CONSOLIDATION-RULE.md)
**Modified files:** 4 (scan.py, cleanup.py, SKILL.md, README.md)
**Detection patterns:** +5 workspace-specific patterns
**Package size:** ~26 KB

### Enforcement Flow

```bash
# 1. Scan for scattered credentials
./scripts/scan.py

# 2. Consolidate to root (with backup)
./scripts/consolidate.py --yes

# 3. Clean up scattered files
./scripts/cleanup.py --confirm

# 4. Validate security
./scripts/validate.py
```

### Migration Story

This update was prompted by discovering scattered `.env` files in a live OpenClaw deployment:
- Root: `~/.openclaw/.env` (secure)
- Workspace: `~/.openclaw/workspace/.env` (scattered)
- Moltbook: `~/.config/moltbook/credentials.json` (insecure permissions)

After consolidation:
- ✅ Single .env with 23 keys
- ✅ Mode 600 permissions
- ✅ Git-ignored
- ✅ All scattered files removed (backed up first)
- ✅ All scripts already pointed to root (no fixes needed)

---

## Version 1.2.0 (2026-02-06)

### 🔐 Crypto-Specific Credential Detection

**Enhanced detection patterns** for blockchain and cryptocurrency credentials.

### Added

**New sensitive key patterns in scan.py:**
- `private_key` / `private-key` - Wallet private keys
- `passphrase` - Seed passphrases
- `mnemonic` - BIP39 recovery phrases
- `seed_phrase` / `seed-phrase` - Wallet seed phrases
- `signing_key` / `signing-key` - Transaction signing keys
- `wallet_key` / `wallet-key` - Wallet access keys

**Documentation:**
- Added "Detection Parameters" section to SKILL.md
- High-level overview of file patterns, sensitive keys, and security checks

### Why This Matters

Crypto credentials (private keys, mnemonics, seed phrases) are **permanent secrets** — once leaked, funds can be drained instantly with no recovery. Previous detection focused on API keys (revocable), missing the most critical crypto patterns.

This update ensures wallet keys and seed phrases are treated with the same security rigor as other credentials.

### Technical Details

**Pattern count:** 15 sensitive patterns (up from 9)
**Detection coverage:** Now includes crypto-native credential types
**Backward compatible:** Existing scans continue to work

---

## Version 1.1.0 (2026-02-05)

### 🔒 SECURITY FOUNDATION UPDATE

**Major philosophical shift:** This is now positioned as **mandatory core infrastructure**, not an optional convenience tool.

### Added

**CORE-PRINCIPLE.md** - New document establishing:
- `.env` is MANDATORY, not optional
- Why centralized credential management is non-negotiable
- The security rationale for this approach
- Implementation requirements for all skills
- Zero exceptions policy

**enforce.py** - New validation script:
- `require_secure_env()` - Enforce .env security before running
- `get_credential()` - Safe credential loading with validation
- Fail-fast system: refuses to run if credentials insecure
- Can be imported by other skills to enforce standard

### Changed

**SKILL.md:**
- Updated description to emphasize "MANDATORY" status
- Added "This Is Not Optional" warning
- New "The Foundation" section explaining requirements
- Added "For Skill Developers" section showing enforcement usage
- Clearer security messaging throughout

**README.md:**
- Repositioned as "Core Security Infrastructure"
- Added "Why This Matters" section upfront
- Emphasized mandatory nature in opening
- Updated status badge to reflect infrastructure role

### Technical Details

**Package size:** 22 KB (was 15 KB)
**Files:** 10 total
- 3 documentation files (SKILL.md, README.md, CORE-PRINCIPLE.md)
- 5 scripts (scan, consolidate, validate, enforce, cleanup)
- 2 references (security, supported-services)

### Philosophy

**Before:** "Use this skill to organize your credentials"
**After:** "Your OpenClaw deployment is non-compliant until credentials are consolidated"

This isn't a feature request. It's a security requirement.

---

## Version 1.0.0 (2026-02-05)

Initial release with core functionality:
- Credential scanning
- .env consolidation
- Security validation
- Old file cleanup
- Comprehensive documentation
