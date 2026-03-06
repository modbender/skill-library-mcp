# Authentication Strategies - Auth

> **Reference patterns only.** Code examples show placeholders (SECRET, API_KEY, etc.) for developers to replace with their own values. The agent does not execute this code.


## Sessions (Server-Side)

**How it works:**
1. User logs in -> server creates session in store (Redis, DB)
2. Server sends session ID in httpOnly cookie
3. Each request sends cookie -> server validates session
4. Logout destroys server session

```typescript
// Session creation
const sessionId = crypto.randomUUID();
await redis.setex(`session:${sessionId}`, 86400, JSON.stringify({
  userId: user.id,
  createdAt: Date.now(),
  ip: request.ip
}));
res.cookie('session', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'lax',
  maxAge: 86400000
});
```

**Pros:** Instant revocation, simple, server controls everything
**Cons:** Requires session store, harder to scale horizontally

**Best for:** Traditional web apps, admin panels, internal tools

---

## JWT (Stateless Tokens)

**How it works:**
1. User logs in -> server creates signed JWT
2. Client stores JWT (memory or secure storage)
3. Each request includes JWT in Authorization header
4. Server validates signature, no DB lookup needed

```typescript
// Token creation
const accessToken = jwt.sign(
  { sub: user.id, email: user.email },
  SECRET,
  { expiresIn: '15m' }
);

const refreshToken = jwt.sign(
  { sub: user.id, type: 'refresh' },
  REFRESH_SECRET,
  { expiresIn: '7d' }
);
```

**Pros:** Stateless, scales horizontally, works across services
**Cons:** Can't revoke until expiry (without blacklist), larger payload

**Best for:** APIs, microservices, mobile apps

---

## Access + Refresh Token Pattern

**The standard approach for JWT:**

```
+-----------------------------------------------------+
|  Access Token (15min)    Refresh Token (7 days)     |
|  - In memory             - httpOnly cookie          |
|  - Sent in header        - Sent only to /refresh    |
|  - Short-lived           - Rotated on use           |
+-----------------------------------------------------+
```

**Refresh flow:**
1. Access token expires -> client calls /refresh
2. Server validates refresh token
3. Server issues new access token + rotates refresh token
4. If refresh token reused -> revoke all tokens (breach detected)

```typescript
// Refresh endpoint
app.post('/auth/refresh', async (req, res) => {
  const { refreshToken } = req.cookies;
  
  // Validate and check not revoked
  const payload = jwt.verify(refreshToken, REFRESH_SECRET);
  const stored = await redis.get(`refresh:${payload.jti}`);
  
  if (!stored || stored.used) {
    // Token reuse detected - revoke all
    await revokeAllUserTokens(payload.sub);
    return res.status(401).json({ error: 'Token reuse detected' });
  }
  
  // Mark as used, issue new pair
  await redis.set(`refresh:${payload.jti}`, { used: true });
  const { accessToken, refreshToken: newRefresh } = generateTokens(payload.sub);
  
  res.cookie('refreshToken', newRefresh, { httpOnly: true, secure: true });
  res.json({ accessToken });
});
```

---

## Hybrid (Sessions + Tokens)

**Best of both worlds:**
- Web app: Sessions (simple, secure cookies)
- Mobile/API: JWT (no cookies needed)
- Same auth service, different delivery

```typescript
// Login endpoint serves both
app.post('/auth/login', async (req, res) => {
  const user = await validateCredentials(req.body);
  
  if (req.headers['x-client-type'] === 'mobile') {
    // Mobile: return tokens
    const tokens = generateTokens(user.id);
    return res.json(tokens);
  }
  
  // Web: create session
  const sessionId = await createSession(user.id);
  res.cookie('session', sessionId, { httpOnly: true, secure: true });
  res.json({ user: sanitize(user) });
});
```

---

## Token Storage (Client-Side)

| Storage | XSS Safe | CSRF Safe | Persists | Best For |
|---------|----------|-----------|----------|----------|
| Memory (JS variable) | [NO] | [YES] | [NO] | Access tokens (SPA) |
| httpOnly cookie | [YES] | [NO]* | [YES] | Refresh tokens, sessions |
| localStorage | [NO] | [YES] | [YES] | [NO] Never for auth |
| Secure enclave (mobile) | [YES] | [YES] | [YES] | Mobile apps |

*Use SameSite=Lax + CSRF tokens for cookie protection

**SPA Pattern:**
```typescript
// Access token in memory
let accessToken = null;

// Refresh token in httpOnly cookie (set by server)
// On app load, call /refresh to get access token

async function getAccessToken() {
  if (!accessToken || isExpired(accessToken)) {
    const res = await fetch('/auth/refresh', { credentials: 'include' });
    accessToken = (await res.json()).accessToken;
  }
  return accessToken;
}
```

---

## Decision Matrix

| Question | If Yes -> |
|----------|----------|
| Traditional server-rendered app? | Sessions |
| Single Page Application? | JWT (memory) + refresh (cookie) |
| Mobile app? | JWT + secure storage |
| Multiple backend services? | JWT (stateless) |
| Need instant logout? | Sessions or JWT + blacklist |
| Enterprise customers? | Add SSO (SAML/OIDC) |
