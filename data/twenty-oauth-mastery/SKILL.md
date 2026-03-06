---
name: Twenty CRM OAuth Mastery Skill
description: "You should use this skill when working on:"
---

# Twenty CRM OAuth Mastery Skill

**Author**: Generated from extensive OAuth debugging sessions in OpenCode  
**Last Updated**: 2026-02-08  
**Version**: 1.0

---

## Skill Metadata

```yaml
name: twenty-oauth-mastery
description: Expert-level OAuth authentication knowledge for Twenty CRM including implementation, troubleshooting, and best practices
expertise_level: Expert/Mastery
category: Authentication
applicable_to:
  - Twenty CRM authentication
  - Google/Microsoft OAuth
  - Token refresh management
  - Domain restrictions
  - Email/Calendar sync integration
prerequisites:
  - Knowledge of TypeScript/JavaScript
  - Understanding of OAuth 2.0 protocol
  - Familiarity with NestJS framework
keywords:
  - oauth
  - authentication
  - twenty-crm
  - google-oauth
  - microsoft-oauth
  - token-refresh
  - sync-integration
  - domain-restriction
```

---

## Quick Start

### When to Use This Skill

You should use this skill when working on:

✅ **Implementing** new OAuth providers  
✅ **Fixing** OAuth login issues  
✅ **Setting up** automatic Gmail/Calendar sync after OAuth  
✅ **Debugging** token refresh failures  
✅ **Configuring** domain restrictions  
✅ **Troubleshooting** redirect loops  

### Quick Reference for Common Issues

| Issue | File to Check | Quick Fix |
|-------|---------------|-----------|
| Redirect loop | `auth.service.ts` | Rebuild: `npx nx build twenty-server` |
| .co domain blocked | `google-auth.controller.ts` | Add to allowlist: `['company.com', 'company.co']` |
| Sync not starting | `google.auth.strategy.ts` | Return tokens in validate() |
| Cookie not readable | Controller cookie settings | Set `httpOnly: false` |
| Infinite loop | `SignInUpGlobalScopeFormEffect.tsx` | Track processed token signatures |

---

## Core Knowledge

### 1. Twenty CRM OAuth Architecture

**Key Files**: `twenty/packages/twenty-server/src/engine/core-modules/auth/`

**Structure**:
```
auth/
├── strategies/         # Passport strategies (Google, Microsoft)
├── controllers/        # OAuth endpoints and callbacks
├── services/          # Auth logic, sync setup, token management
├── guards/            # Auth guards and validation
└── utils/             # Scope configuration, utilities
```

---

### 2. Critical Code Patterns

#### Passport Strategy Pattern (MUST FOLLOW)

```typescript
@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor(twentyConfigService: TwentyConfigService) {
    super({
      clientID: twentyConfigService.get('AUTH_GOOGLE_CLIENT_ID'),
      clientSecret: twentyConfigService.get('AUTH_GOOGLE_CLIENT_SECRET'),
      callbackURL: twentyConfigService.get('AUTH_GOOGLE_CALLBACK_URL'),
      scope: getGoogleApisOauthScopes(),
      passReqToCallback: true, // 🔴 CRITICAL: Required for request state
    });
  }

  async validate(
    request: GoogleRequest,
    _accessToken: string,
    _refreshToken: string,
    profile: GoogleProfile,
  ) {
    // 🔴 CRITICAL: Include tokens in return object
    // Without this, automatic sync setup fails
    return {
      ...profile,
      accessToken: _accessToken,
      refreshToken: _refreshToken,
      hostedDomain: request.query.hosted_domain || profile.emails?.[0]?.value?.split('@')[1],
    };
  }
}
```

**Why This Matters**:
- `passReqToCallback: true`: Enables access to request state
- Token preservation: Required for OAuthSyncService to work

---

### 3. Common Issues & Solutions

#### Issue 1: Redirect Loop After OAuth

**Symptoms**: OAuth completes but user stuck on welcome page

**Root Causes**:

1. **Backend not compiled**: Source has fix, container running old JavaScript
  
   **Fix**:
   ```bash
   npx nx build twenty-server
   docker restart fratres-twenty
   ```

2. **Missing isSingleDomainMode**: Redirect logic not in compiled code

   **Check**:
   ```bash
   docker exec fratres-twenty cat /app/dist/engine/core-modules/auth/services/auth.service.js | grep isSingleDomainMode
   ```

3. **Cookie domain mismatch**: Cookie not accessible

   **Fix**:
   ```typescript
   // auth.service.ts - Remove explicit domain attribute
   res.cookie('tokenPair', JSON.stringify(authTokens), {
     path: '/',
     secure: true,
     sameSite: 'lax',
     httpOnly: false, // 🔴 Must be false for JavaScript access
   });
   ```

---

#### Issue 2: Domain Enforcement Blocking .co Users

**Symptoms**: `@company.co` rejected, only `@company.com` allowed

**Three Places to Fix**:

1. **Google Strategy** (`google.auth.strategy.ts`):
   ```typescript
   // ❌ WRONG - Hardcoded
   hd: 'company.com'
   
   // ✅ CORRECT - Remove hd parameter
   // (no hd parameter)
   ```

2. **Controller** (`google-auth.controller.ts`):
   ```typescript
   // ❌ WRONG - Hardcoded check
   if (hostedDomain !== 'company.com') { throw ... }
   
   // ✅ CORRECT - Allowlist
   const allowedOAuthDomains = ['company.com', 'company.co'];
   if (!hostedDomain || !allowedOAuthDomains.includes(hostedDomain)) {
     throw new UnauthorizedException(
       `Only ${allowedOAuthDomains.map(d => `@${d}`).join(', ')} allowed`
     );
   }
   ```

3. **Database** (`workspaceMetadata` table):
   ```sql
   INSERT INTO "workspaceMetadata" ("id", "workspaceId", "key", "value", "createdAt", "updatedAt")
   VALUES (gen_random_uuid(), 'workspace-id', 'approvedAccessDomains', '["company.com", "company.co"]', NOW(), NOW());
   ```

---

#### Issue 3: Automatic Sync Not Triggered

**Symptoms**: User logs in but connected account/sync channels not created

**Root Cause**: Tokens lost in validate() method

**Fix**:
```typescript
// google.auth.strategy.ts validate()
async validate(request, accessToken, refreshToken, profile) {
  // ❌ WRONG - Tokens lost
  return { ...profile };
  
  // ✅ CORRECT - Tokens preserved
  return {
    ...profile,
    accessToken,
    refreshToken,
  };
}
```

**Additional Checks**:

1. Verify `auth.service.ts` calls `oauthSyncService.setupSyncForOAuthUser()` after login
2. Verify tokens are passed to sync service
3. Check Google scopes include `gmail.readonly` and `calendar.events`
4. Verify `CALENDAR_PROVIDER_GOOGLE_ENABLED=true`

---

#### Issue 4: Frontend Token Processing Loop

**Symptoms**: `SignInUpGlobalScopeFormEffect` runs repeatedly, infinite API calls

**Root Cause**: Same token processed multiple times

**Fix**:
```typescript
// SignInUpGlobalScopeFormEffect.tsx
useEffect(() => {
  const tokenPairFromUrl = getAuthPairFromUrl();
  
  if (tokenPairFromUrl) {
    const tokenSignature = JSON.stringify(tokenPairFromUrl);
    
    // 🔴 CRITICAL: Skip if already processed
    if (processedTokenSignatures.current.has(tokenSignature)) {
      return;
    }
    
    // Track this signature
    processedTokenSignatures.current.add(tokenSignature);
    
    // Now process the token
    setAuthTokens(tokenPairFromUrl);
  }
}, []);
```

---

### 4. OAuth Sync Integration

**When to Use**: Users should have Gmail/Calendar auto-connected after OAuth login

**Implementation**:

1. **Create OAuthSyncService**:
   ```typescript
   async setupSyncForOAuthUser(input: {
     workspaceId: string;
     userId: string;
     workspaceMemberId: string;
     email: string;
     accessToken: string;
     refreshToken: string;
     scopes: string[];
   }) {
     // 1. Create/update connected account with tokens
     // 2. Create message channel
     // 3. Create calendar channel (if enabled)
     // 4. Queue initial sync jobs
   }
   ```

2. **Integrate into AuthService**:
   ```typescript
   // auth.service.ts:signInUpWithSocialSSO()
   const { redirectUrl, authTokens } = await this.generateTokens(...);
   
   // 🔴 CRITICAL: Call sync setup BEFORE redirect
   if (provider === 'google') {
     try {
       await this.oauthSyncService.setupSyncForOAuthUser({
         workspaceId,
         userId,
         email: user.email,
         accessToken: authTokens.authToken.accessToken,
         refreshToken: authTokens.authToken.refreshToken,
         scopes: user.scopes || [],
       });
     } catch (error) {
       // Log error but don't fail login
       this.logger.error('Failed to setup OAuth sync', error);
     }
   }
   
   return { redirectUrl, authTokens };
   ```

**Critical**:
- Use try/catch to prevent sync setup from failing login
- Check for existing channels (prevent duplication)
- Only run for specific providers/domains if needed

---

### 5. Token Refresh Management

**Token Refresh Pattern**:
```typescript
async refreshTokens(refreshToken: string): Promise<ConnectedAccountTokens> {
  const oAuth2Client = new google.auth.OAuth2(clientId, clientSecret);
  oAuth2Client.setCredentials({ refresh_token: refreshToken });
  
  try {
    const { token } = await oAuth2Client.getAccessToken();
    
    // 🔴 CRITICAL: Preserve original refresh token
    // Google may not return a new one
    return {
      accessToken: token,
      refreshToken: refreshToken,
    };
  } catch (error) {
    throw parseGoogleOAuthError(error);
  }
}
```

**Error Handling**:
```typescript
export const parseGoogleOAuthError = (error: unknown) => {
  const gaxiosError = error as GaxiosError;
  const code = gaxiosError.response?.status;
  const reason = gaxiosError.response?.data?.error;
  
  switch (code) {
    case 400:
      if (reason === 'invalid_grant') {
        // 🔴 FATAL: Refresh token expired/revoked
        return new ConnectedAccountRefreshAccessTokenException(
          'invalid_grant',
          ConnectedAccountRefreshAccessTokenExceptionCode.INVALID_REFRESH_TOKEN,
        );
      }
      break;
    case 401:
      return new ConnectedAccountRefreshAccessTokenException(
        'unauthorized',
        ConnectedAccountRefreshAccessTokenExceptionCode.UNAUTHORIZED,
      );
    case 429:
      // 🔴 RETRYABLE: Rate limit error
      return new ConnectedAccountRefreshAccessTokenException(
        'rate_limit',
        ConnectedAccountRefreshAccessTokenExceptionCode.RATE_LIMIT_ERROR,
      );
  }
  
  return new ConnectedAccountRefreshAccessTokenException('unknown', ...);
};
```

---

### 6. Testing Strategies

#### Unit Testing (Token Refresh)
```typescript
describe('GoogleAPIRefreshAccessTokenService', () => {
  it('should refresh token successfully', async () => {
    const mockRefreshToken = 'valid-refresh-token';
    const mockNewAccessToken = 'new-access-token';
    
    jest.spyOn(google.auth, 'OAuth2').mockImplementation(() => ({
      setCredentials: jest.fn(),
      getAccessToken: jest.fn().mockResolvedValue({ token: mockNewAccessToken }),
    }));
    
    const result = await service.refreshTokens(mockRefreshToken);
    
    expect(result.accessToken).toBe(mockNewAccessToken);
    expect(result.refreshToken).toBe(mockRefreshToken); // Original preserved
  });
});
```

#### Cookie Injection Test (Playwright)
```typescript
// Test: frontend reads and processes cookie
await context.addCookies([{
  name: 'tokenPair',
  value: JSON.stringify({ authToken: { accessToken: 'fake-token' } }),
  domain: 'isearch.1791technology.com',
  path: '/',
  secure: true,
  sameSite: 'Lax',
}]);

await page.goto('https://isearch.1791technology.com');

// Check console logs
const logs = await page.evaluate(() => window.tokenPairLogs || []);
assert(logs.includes('tokenPairPayload from cookies: found'));
assert(logs.includes('Setting auth tokens...'));
```

---

### 7. Configuration

**Required Environment Variables**:
```bash
# Google OAuth
AUTH_GOOGLE_ENABLED=true
AUTH_GOOGLE_CLIENT_ID=849758856044-54v9md2rt6ucthch26p8g4etotcb8gth.apps.googleusercontent.com
AUTH_GOOGLE_CLIENT_SECRET=GOCSPX-...
AUTH_GOOGLE_CALLBACK_URL=https://yourdomain.com/auth/google/redirect

# Calendars/Email
CALENDAR_PROVIDER_GOOGLE_ENABLED=true
MESSAGING_PROVIDER_GMAIL_ENABLED=true

# Billing (disable for self-hosted)
IS_BILLING_ENABLED=false
```

**Google Cloud Console**:
- Redirect URIs: `https://yourdomain.com/auth/google/redirect`
- Authorized Origins: `https://yourdomain.com`

---

### 8. Deployment Checklist

**Before Deploying**:
- [ ] TypeScript source updated
- [ ] Unit tests passing
- [ ] Type check: `npx nx typecheck twenty-server`
- [ ] Build: `npx nx build twenty-server`
- [ ] Verify compiled JavaScript has changes (check dist/ folder)
- [ ] Copy dist/ to container
- [ ] Restart container
- [ ] Check health: `curl -f /healthz`

**After Deploying**:
- [ ] Test OAuth flow manually
- [ ] Check browser console
- [ ] Verify redirect to dashboard (not welcome)
- [ ] Check connected account in database
- [ ] Verify sync channels created (if applicable)

---

### 9. Troubleshooting Workflow

**Step 1: Verify Container Running New Code**
```bash
docker ps | grep fratres-twenty
docker exec fratres-twenty cat /app/dist/engine/core-modules/auth/services/auth.service.js | grep isSingleDomainMode
```

**Step 2: Check Google Cloud Console**
- Redirect URIs match production URL
- Client ID and secret correct
- OAuth consent screen configured

**Step 3: Check Environment**
```bash
docker exec fratres-twenty env | grep AUTH_GOOGLE
docker exec fratres-twenty env | grep CALENDAR_PROVIDER
```

**Step 4: Test OAuth Entry Point**
```bash
curl -v https://yourdomain.com/auth/google | grep Location
# Should redirect to accounts.google.com with correct client_id
```

**Step 5: Check Database (Sync Issues)**
```sql
-- Check connected accounts
SELECT id, handle, provider, "accessToken" IS NOT NULL
FROM "connectedAccount"
WHERE handle = 'user@example.com';

-- Check sync channels
SELECT id, "syncStatus"
FROM "messageChannel"
WHERE "connectedAccountId" = 'account-id';
```

**Step 6: Check Logs**
```bash
docker logs fratres-twenty --tail 100 | grep -i oauth
```

---

### 10. Common Pitfalls ❌

1. **Forgetting to rebuild** - Source changes don't auto-compile
2. **Hardcoding domains** - Use allowlists instead
3. **Setting httpOnly: true** - Frontend can't read tokenPair cookie
4. **Losing tokens in validate()** - Must return accessToken/refreshToken
5. **Not preserving refresh tokens** - Google may not return new ones
6. **Missing passReqToCallback: true** - Can't access request state
7. **Not testing with real OAuth** - Mock tests miss edge cases
8. **Skipping health checks** - Container running old code unnoticed

---

## Expert Insights

### When OAuth Works But Sync Doesn't

**Debug Path**:
1. Check `oauth-sync.service.ts` exists and is called
2. Verify tokens passed through validate()
3. Check scopes include `gmail.readonly` and `calendar.events`
4. Verify `CALENDAR_PROVIDER_GOOGLE_ENABLED=true`
5. Check connected account in database
6. Verify sync channels with `syncStatus=ONGOING`

**Common Fix**: Return tokens in validate() method

---

### When .co Domain Users Can't Login

**Debug Path**:
1. Check `google.auth.strategy.ts` for hardcoded `hd` parameter
2. Check `google-auth.controller.ts` domain validation
3. Check `auth.service.ts` domain allowlist
4. Check `workspaceMetadata.approvedAccessDomains` in database

**Common Fixes**:
- Remove hardcoded `hd` parameter
- Update controller/service allowlists
- Insert domain into database

---

### When Frontend Gets Stuck on Welcome Page

**Debug Path**:
1. Check `isSingleDomainMode` logic in `auth.service.ts`
2. Check compiled `auth.service.js` has logic
3. Check `computeRedirectURI` returns `AppPath.Index`
4. Check cookie `httpOnly` attribute

**Common Fixes**:
- Rebuild backend: `npx nx build twenty-server`
- Ensure redirect to dashboard: `AppPath.Index`
- Set `httpOnly: false` on cookie

---

## Quick Commands

```bash
# Build backend
npx nx build twenty-server

# Build frontend
npx nx build twenty-front

# Typecheck
npx nx typecheck twenty-server

# Restart container
docker restart fratres-twenty

# Check logs
docker logs fratres-twenty --tail 100

# Health check
curl -f https://yourdomain.com/healthz

# Test OAuth redirect
curl -v https://yourdomain.com/auth/google
```

---

## Summary

This skill provides expert-level OAuth knowledge for Twenty CRM covering:

1. **Architecture**: Twenty's OAuth using Passport strategies
2. **Common Issues**: 5+ major issues with detailed fixes
3. **Automatic Sync**: Gmail/Calendar sync after OAuth
4. **Token Management**: Refresh patterns and error handling
5. **Testing**: Unit and integration test patterns
6. **Configuration**: Required environment variables
7. **Deployment**: Step-by-step checklist
8. **Troubleshooting**: Systematic workflow

**Use this skill when**:
- Implementing new OAuth provider
- Fixing OAuth login issues
- Setting up automatic sync integration
- Debugging token refresh failures
- Configuring domain restrictions
- Troubleshooting redirect loops
