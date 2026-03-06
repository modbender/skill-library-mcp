# Security Documentation

## Credential Loading

This skill uses **secure, hardcoded .env loading** — NOT directory traversal.

### Implementation

```javascript
// scripts/lib/basecred.mjs
import { homedir } from 'os';
import { join } from 'path';

const openclawEnvPath = join(homedir(), '.openclaw', '.env');
dotenv.config({ path: openclawEnvPath });
```

**Why this is secure:**

- Path is **dynamically constructed** from user's home directory (portable across users)
- No upward directory traversal (no risk of reading unrelated .env files)
- Resolves to `~/.openclaw/.env` for the current user (respects OpenClaw standard)
- Credentials are loaded from the centralized, permission-restricted `.env` (mode 600)
- Script runs in skill context with read-only access to credentials

### Required Credentials

**None** — Ethos Network requires no API key.

### Optional Credentials

Declared in `skill.json` manifest:

1. **TALENT_API_KEY** (optional)
   - Purpose: Enable Talent Protocol builder/creator scores
   - Scope: Read-only access to public Talent Protocol profiles
   - Get key: https://talentprotocol.com

2. **NEYNAR_API_KEY** (optional)
   - Purpose: Enable Farcaster quality scores
   - Scope: Read-only access to public Farcaster user data
   - Get key: https://neynar.com

**Graceful degradation:**
- Script works without these keys (Ethos data still available)
- Missing keys trigger warnings but do not fail execution
- Partial data responses are valid

## Upstream Dependency Audit

**@basecred/sdk v0.6.2**

- ✅ **Repository:** https://github.com/GeoartStudio/basecred-sdk
- ✅ **License:** MIT
- ✅ **Runtime Dependencies:** Only `dotenv@16.6.1` (no transitive deps)
- ✅ **No network access** outside declared API endpoints (Ethos, Talent, Neynar)
- ✅ **No filesystem access** except reading .env via dotenv

**Last audited:** 2026-02-11

## Data Flow

1. User invokes `check-reputation.mjs <address>`
2. Script dynamically resolves `.env` path: `${homedir()}/.openclaw/.env`
3. Credentials loaded from user's OpenClaw directory (portable across users)
4. Credentials passed to `@basecred/sdk` config builder
4. SDK makes HTTP requests to:
   - `https://api.ethos.network` (no auth)
   - `https://api.talentprotocol.com` (if TALENT_API_KEY present)
   - Neynar API (if NEYNAR_API_KEY present)
5. Responses assembled into unified profile
6. JSON output returned to stdout (no disk writes)

**No secrets are logged or persisted.**

## Isolation

This skill is **isolated by design:**

- Runs in its own directory (`~/.openclaw/workspace/skills/openclaw-basecred-sdk`)
- No access to sibling skill directories
- No write access to OpenClaw system files
- No ability to modify credentials or config

## Threat Model

**Risks mitigated:**

- ✅ Credential leakage → Dynamic path resolves to user's `.openclaw/.env` only
- ✅ Directory traversal → No upward path resolution (direct `join()` construction)
- ✅ Dependency injection → Locked to @basecred/sdk@0.6.2
- ✅ API key exposure → Keys never logged or written to disk
- ✅ Non-portability → Works for any user (not hardcoded to specific username)

**Residual risks:**

- ⚠️ Compromised upstream package → Pin version and audit before upgrading
- ⚠️ Man-in-the-middle → API calls use HTTPS but trust system CA store
- ⚠️ API key theft → If .env is compromised, keys can be stolen (standard OpenClaw risk)

## Recommendations

1. **Pin @basecred/sdk version** in `package.json` (currently 0.6.2)
2. **Audit before upgrading** — re-check upstream code for malicious changes
3. **Rotate API keys periodically** using `credential-manager` skill
4. **Run in isolated workspace** (already default behavior)
5. **Monitor API usage** for unexpected calls (Talent Protocol, Neynar)

## Reporting Issues

Security concerns? Contact:
- GitHub: https://github.com/Callmedas69/basecred/issues
- Skill maintainer: teeclaw

---

**Version:** 1.0.1  
**Last Updated:** 2026-02-11
