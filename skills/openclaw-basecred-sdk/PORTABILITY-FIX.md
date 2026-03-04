# Portability Fix - Critical User Path Issue

**Date:** 2026-02-11  
**Reported by:** 0xdas  
**Severity:** 🔴 CRITICAL (skill unusable by other users)

---

## Problem

Initial security hardening introduced a **non-portable hardcoded path**:

```javascript
// ❌ BEFORE (security hardening commit d3790b5)
dotenv.config({ path: '/home/phan_harry/.openclaw/.env' });
```

**Impact:**
- Skill would only work for user `phan_harry`
- Any other OpenClaw installation would fail with "ENOENT: .env not found"
- Not distributable via ClawHub or other package managers
- Violated OpenClaw's portability principles

---

## Root Cause

During security audit response, the focus was on proving "no directory traversal" by showing a concrete path. The path was documented correctly in SECURITY.md, but the **implementation was overly specific**.

The audit report claimed the script "walks up directories to find .env" — to disprove this, I showed the exact hardcoded path... but made it TOO hardcoded by including the specific username.

---

## Solution

Replace hardcoded path with **dynamic user home resolution**:

```javascript
// ✅ AFTER (portability fix commit 92ef3ea)
import { homedir } from 'os';
import { join } from 'path';

const openclawEnvPath = join(homedir(), '.openclaw', '.env');
dotenv.config({ path: openclawEnvPath });
```

**Benefits:**
- ✅ Works for ANY user on ANY system
- ✅ Still secure (no traversal, direct path construction)
- ✅ Respects OpenClaw standard (`~/.openclaw/.env`)
- ✅ Distributable via ClawHub
- ✅ Follows Node.js best practices (`os.homedir()`)

---

## Verification

### Test for portability:
```bash
cd /home/phan_harry/.openclaw/workspace/skills/basecred-sdk-skill
./test-isolation.sh
```

**Expected output:**
```
✓ Test 1: Verify dynamic .env path (user-agnostic)
  ✅ PASS: Uses homedir() for portable path resolution
```

### Functional test (any user):
```bash
./scripts/check-reputation.mjs 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045 --summary
```

Should return valid JSON with reputation data (regardless of username).

---

## Lesson Learned

**Security AND portability must coexist.**

When proving "no directory traversal," showing a specific path in documentation is fine. But the **implementation must remain user-agnostic**.

Correct approach:
1. **Code:** Use dynamic resolution (`homedir()`)
2. **Docs:** Show example resolved path for clarity
3. **Tests:** Verify both security and portability

---

## Affected Versions

- **v1.0.1:** ❌ User-specific (unusable by others)
- **v1.0.2:** ✅ Portable (works for all users)

---

## Related Commits

- `d3790b5` - Security hardening (introduced issue)
- `92ef3ea` - Portability fix (resolved issue)

---

## Thanks

Credit to **0xdas** for catching this critical oversight during code review. 🙏

Without this catch, the skill would have shipped with a show-stopping portability bug.

---

**Status:** ✅ RESOLVED  
**Current version:** 1.0.2 (portable + secure)
