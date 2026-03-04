# Security Incident Report & Remediation

**Date:** 2026-02-14  
**Reporter:** VirusTotal (scan of ClawHub skill)  
**Skill:** curated-search v1.0.3  
**Classification:** Suspicious (attack surface: unused network server component)  

---

## Issue

The published skill bundle contained `src/search-api.js`, a fully functional HTTP/Unix socket server that is:
- **Not referenced** by the skill's `package.json` (main entry is `scripts/search.js`)
- **Not used** by the CLI tool or OpenClaw integration
- **Documented** in README as "legacy — not used"
- **Present** in the distributed package due to `.clawhubignore` not excluding `src/` files

If a user misconfigured their skill handler to use this server, it would expose a network listener with potential SSRF/other risks. While the code itself includes SSRF prevention, the *presence* of an unused server is a security liability and causes false-positive "suspicious" flags.

---

## Root Cause

- Legacy refactoring: `search-api.js` was replaced by CLI tool but not deleted
- `.clawhubignore` excluded only build artifacts, not source files or specific internal docs
- The file remained in the repository and was included in published tarballs

---

## Actions Taken

### 1. Immediate Containment
- ✅ Deleted `src/search-api.js` from repository
- ✅ Removed legacy reference in README.md
- ✅ Updated `.clawhubignore` to exclude:
  - `*AUDIT*.md`, `*CRITICAL*.md`, `*GAP*.md`
  - `SYS_*`, `YACY_*` (internal audit/research docs)
  - `securityaudit/`
- ✅ Prepared clean publish version 1.0.4

### 2. Registry Cleanup
- ✅ Deleted duplicate skill `curated-search-skill` (v1.0.0)
- ⚠️ Published v1.0.3 (first attempt succeeded but later registry checks showed "not found")
- ⏳ Rate limit prevented immediate republish; will retry with v1.0.4 after cooldown

### 3. Documentation
- ✅ Updated `CHANGELOG.md` with security fixes
- ✅ Created `SECURITY_INCIDENT_2026-02-14.md` (this file)
- ✅ Updated `IMPLEMENTATION_PLAN.md` to add security review step for future publishes

---

## Current State

| File | Status |
|------|--------|
| `src/search-api.js` | DELETED |
| `README.md` | Cleaned (no legacy reference) |
| `.clawhubignore` | Updated with comprehensive exclusions |
| `package.json` | Version bumped to 1.0.4 |
| `CHANGELOG.md` | Updated with security fixes |

**ClawHub status:**
- `curated-search-skill` → DELETED
- `curated-search` → *pending clean publish* (rate limited)

---

## Next Steps

1. **Wait for rate limit** (~1-2 hours from 08:49 PST)
2. **Run publish script** (see `scripts/publish-clean.sh`) or manually:
   ```bash
   clawhub publish /home/q/.openclaw/workspace/skills/curated-search \
     --slug curated-search \
     --name "Curated Search" \
     --version 1.0.4 \
     --changelog "Security: removed unused search-api.js server component and related references. Cleaned .clawhubignore to exclude all internal audit files." \
     --no-input
   ```
3. **Verify** published bundle does NOT contain `search-api.js` or any internal audit files
4. **Update MEMORY.md** with this incident and resolution

---

## Prevention

Going forward, before any `clawhub publish`:
- Run `git status` to check for unexpected files
- Review `.clawhubignore` coverage
- Inspect the tarball: `tar -tzf $(clawhub pack ...)` if needed
- Ensure only `scripts/`, `src/` (excluding legacy), `config.yaml` (template), `README.md`, `SKILL.md`, `CHANGELOG.md` are included

---

**Resolved by:** Lieutenant Qrusher  
**Approved by:** Captain JAQ
