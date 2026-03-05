# Changelog

All notable changes to openclaw-basecred-sdk will be documented in this file.

## [1.0.4] - 2026-02-11

### 🚨 SECURITY INCIDENT & CLEANUP

#### Critical Security Fix
- **REMOVED:** `BUILD-SUMMARY.md` and `AUDIT-SUMMARY.md` files containing leaked API keys
- **SCRUBBED:** Git history to remove all traces of exposed credentials (13 commits rewritten)
- **FIXED:** Hardcoded `/home/phan_harry/` paths replaced with `~/` in all documentation
- **ROTATED:** All exposed API keys (Talent Protocol, Neynar)

#### Schema Fix
- **FIXED:** `--full` output now returns correct schema (unwrapped profile object)
- Schema now matches documented spec: `{ identity, availability, ethos, talent, farcaster, recency }`

#### Incident Summary
- API keys were accidentally included in documentation files
- Exposed on GitHub and ClawHub v1.0.3 for ~3 hours (2026-02-11 04:00-07:00 UTC)
- Git history completely cleaned using `git filter-branch`
- All affected credentials rotated
- No evidence of unauthorized use

#### Documentation Updates
- Updated `SKILL.md` to use portable paths (`~/.openclaw/`)
- Updated `SECURITY.md` to remove user-specific paths
- Removed all placeholder keys from documentation

**Reported by:** ClawHub security review  
**Fixed by:** Mr. Tee & 0xdas

## [1.0.3] - 2026-02-11

### Package Rename
- **Renamed:** `basecred-sdk-skill` → `openclaw-basecred-sdk` for consistency
- **Updated:** package.json name and repository URL
- **Published:** To ClawHub with updated slug

No functional changes from v1.0.2.

## [1.0.2] - 2026-02-11

### Security Audit & Fixes

#### 🔐 Security Hardening
- **Added:** Comprehensive `skill.json` manifest with proper credential declarations
- **Added:** `SECURITY.md` documentation with full security audit results
- **Added:** Automated `test-isolation.sh` test suite for security verification
- **Added:** `PATCH-NOTES.md` documenting all security improvements
- **Updated:** SKILL.md with security section and credential metadata

#### 🔴 CRITICAL: Portability Fix
- **Fixed:** Hardcoded `/home/phan_harry/.openclaw/.env` path (would fail for other users)
- **Changed:** Now uses dynamic `os.homedir()` + `path.join()` resolution
- **Impact:** Skill now works for ANY OpenClaw user (portable across installations)
- **Added:** `PORTABILITY-FIX.md` documenting the issue and fix

#### 🛡️ Security Audit Results
- ✅ **Upstream audit:** `@basecred/sdk@0.6.2` verified clean (MIT, minimal deps)
- ✅ **Credential loading:** Secure, no directory traversal
- ✅ **Portability:** User-agnostic path resolution
- ✅ **Isolation:** Read-only credential access, no disk writes
- ✅ **API scope:** Only reads public reputation data

#### Audit Findings Summary
- ❌ **FALSE:** Original audit claim of "directory traversal" - actually uses direct path construction
- ✅ **FIXED:** Missing credential declarations in manifest
- ✅ **FIXED:** Non-portable hardcoded username in path
- ✅ **VERIFIED:** Upstream dependency clean and safe

### Testing
- **Added:** Automated isolation test suite verifying 5 security properties
- **Verified:** All tests passing (portability, security, functionality)
- **Verified:** Skill works for any user on any system

### Documentation
- **Added:** Complete security documentation (SECURITY.md)
- **Added:** Portability fix incident report (PORTABILITY-FIX.md)
- **Added:** Security patch notes (PATCH-NOTES.md)
- **Updated:** SKILL.md with security guarantees
- **Updated:** README.md with audit information

### Commits
- `e795737` Add portability fix documentation
- `92ef3ea` CRITICAL: Fix non-portable hardcoded user path
- `b7cbd63` Add automated isolation test suite
- `d3790b5` Security hardening: Add skill.json manifest, SECURITY.md, and credential declarations

**Reported by:** 0xdas (audit review)  
**Fixed by:** Mr. Tee (OpenClaw agent)

---

## [1.0.1] - 2026-02-10

### Changed
- Updated `@basecred/sdk` from v0.6.1 to v0.6.2
- **Bug fix:** Neynar/Farcaster scores now return actual decimal values (e.g., 0.43) instead of rounded integers
- This provides more accurate Farcaster quality scores

### Verified
- ✅ All tests passing with v0.6.2
- ✅ Decimal precision working correctly (e.g., 0.43 instead of 0)
- ✅ No breaking changes to skill code
- ✅ Output format unchanged

## [1.0.0] - 2026-02-10

### Added
- Initial release
- CLI interface for checking reputation via Ethos, Talent Protocol, and Farcaster
- Summary and full profile output modes
- Human-readable and JSON output formats
- Graceful degradation with partial data sources
- Comprehensive documentation (SKILL.md, README.md)
- Test suite with known addresses
- Integration library for other skills
