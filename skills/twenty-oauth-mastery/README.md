# Twenty CRM OAuth Mastery Skill - Created

## What Was Created

A comprehensive expertise skill for Twenty CRM OAuth integration, troubleshooting, and best practices based on extensive session analysis.

## Skill Location

**Primary File**: `/home/agent/fratres/custom-skills/twenty-oauth-mastery.skill.md`

**Draft Documentation**: `/home/agent/fratres/.sisyphus/drafts/twenty-oauth-mastery-skill.md`

## Skill Overview

**Name**: `twenty-oauth-mastery`

**Expertise Level**: Expert/Mastery

**Applicable To**:
- Twenty CRM authentication
- Google/Microsoft OAuth
- Token refresh management
- Domain restrictions
- Email/Calendar sync integration

---

## Key Components

### 1. Architecture Knowledge

**File Structure**: `twenty/packages/twenty-server/src/engine/core-modules/auth/`

```
auth/
├── strategies/         # Passport strategies (Google, Microsoft)
├── controllers/        # OAuth endpoints and callbacks
├── services/          # Auth logic, sync setup, token management
├── guards/            # Auth guards and validation
└── utils/             # Scope configuration, utilities
```

### 2. 5 Major Issues with Solutions

| Issue | Quick Fix |
|-------|-----------|
| **Redirect Loop** | Rebuild: `npx nx build twenty-server` |
| **.co Domain Blocked** | Add to allowlist in 3 places |
| **Sync Not Starting** | Return tokens in validate() method |
| **Cookie Not Readable** | Set `httpOnly: false` |
| **Infinite Loop** | Track processed token signatures |

### 3. Critical Code Patterns

**Passport Strategy** (MUST FOLLOW):
```typescript
passReqToCallback: true, // Required
return { ..., accessToken, refreshToken }; // Must preserve tokens
```

**Token Refresh**:
```typescript
// Preserve original refresh token (Google may not return new one)
return { accessToken: token, refreshToken: refreshToken };
```

### 4. Testing Strategies

- Unit testing for token refresh
- Playwright for cookie injection testing
- Database verification for sync issues

### 5. Deployment Checklist

**Before Deploy**:
- TypeScript source updated
- Tests passing
- Build completed
- Verify compiled JavaScript

**After Deploy**:
- Test OAuth flow manually
- Check browser console
- Verify redirect to dashboard
- Check database for connected accounts

### 6. Troubleshooting Workflow

6-step systematic approach:
1. Verify container running new code
2. Check Google Cloud Console
3. Check environment variables
4. Test OAuth entry point
5. Check database (sync issues)
6. Check logs

---

## How to Use This Skill

### When Working on OAuth Issues

1. **Consult Quick Reference Table** for immediate symptom-to-fix mapping
2. **Read Relevant Issue Section** for detailed root cause analysis
3. **Follow Troubleshooting Workflow** step-by-step
4. **Verify with Testing Strategies** before deploying

### When Implementing New OAuth Features

1. **Review Architecture Knowledge** to understand code structure
2. **Follow Critical Code Patterns** for consistency
3. **Use Testing Strategies** to ensure reliability
4. **Follow Deployment Checklist** for deployment

### When Debugging Existing OAuth Issues

1. **Identify symptom** from Common Issues section
2. **Check file locations** specified for your issue
3. **Apply recommended fixes** in order
4. **Verify with database queries** (if sync-related)
5. **Test with OAuth flow** before considering complete

---

## Session Knowledge Sources

This skill compiles knowledge from **8 sessions** spanning **December 2025 - February 2026**:

### Key Sessions Reviewed

| Session | Focus | Key Learnings |
|---------|-------|---------------|
| `ses_3cbfedbc1ffe3jSWb8qlglnis4` | Frontend token fix | Backend source not compiled, cookie attributes |
| `ses_3df1d0a33ffeylAsT2AYJY3ywW` | Enrichment testing | Container networking, environment variables |
| `ses_3e5fad76dffeMjB0CuX1p9QgfY` | OAuth 500 error RCA | Endpoint validation, error handling |
| `ses_3c19f4278ffeiqxcjgYJ7dy6tn` | OAuth codebase exploration | Comprehensive file analysis |

### Plans Review

| Plan | Focus | Key Insights |
|------|-------|--------------|
| `oauth-frontend-token-fix.md` | Cookie processing | Frontend token reading, infinite loops |
| `oauth-jnguyen-rca-plan.md` | Domain enforcement | .co domain blocking, allowlist strategy |
| `oauth-sync-integration.md` | Automatic sync | Token capture, channel creation, scope expansion |
| `oauth-redirect-domain-fix.md` | Redirect logic | isSingleDomainMode, cookie domain |
| `twenty-oauth-billing-fix.md` | OAuth billing | Billing feature gating, redirect URLs |

---

## Expert Insights Included

### Real-World Issues Discovered

1. **Source-Compiled Code Mismatch**: Backend fixes in TypeScript source but not in compiled JavaScript running in container
2. **Domain Restriction Pitfalls**: Hardcoded domains blocking legitimate users with .co TLD
3. **Token Loss in Validation**: Missing accessToken/refreshToken in validate() return object breaks automatic sync
4. **Cookie Attribute Errors**: `httpOnly: true` prevents frontend from reading tokenPair cookie
5. **Infinite Processing Loops**: Same token signature processed repeatedly causing API spam

### Proven Solutions

Each issue includes:
- Symptom description
- Root cause analysis
- File locations to check
- Step-by-step fixes
- Verification methods

---

## Quick Reference Commands

```bash
# Build
npx nx build twenty-server      # Backend
npx nx build twenty-front       # Frontend
npx nx typecheck twenty-server  # Type check

# Deployment
docker restart fratres-twenty   # Restart container

# Verification
curl -f https://yourdomain.com/healthz           # Health check
curl -v https://yourdomain.com/auth/google       # Test OAuth

# Debugging
docker logs fratres-twenty --tail 100            # View logs
docker exec fratres-twenty env | grep AUTH_GOOGLE # Check env vars
```

---

## Next Steps

### To Use This Skill

1. **Load skill** when working on OAuth-related tasks
2. **Reference** relevant sections based on your issue
3. **Follow** the systematic troubleshooting workflow
4. **Apply** critical code patterns for consistency

### To Improve This Skill

1. **Add new issues** discovered during debugging
2. **Update code patterns** as Twenty CRM evolves
3. **Additional testing strategies** as you discover them
4. **New deployment insights** from production updates

---

## Summary

This skill represents **expert-level OAuth knowledge** distilled from extensive real-world debugging sessions. It provides:

- **Immediate fixes** for 5+ common OAuth issues
- **Systematic workflows** for troubleshooting
- **Battle-tested code patterns** for consistency
- **Production-ready deployment checklist**
- **Database verification queries** for sync issues

**Use this skill whenever working with Twenty CRM OAuth** to avoid common pitfalls and solve issues efficiently.

---

**Created**: 2026-02-08
**Based On**: 8 sessions, 5 plans, extensive codebase exploration
**Maintained**: `/home/agent/fratres/custom-skills/twenty-oauth-mastery.skill.md`
