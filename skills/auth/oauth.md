# OAuth and Social Login - Auth

> **Reference patterns only.** Code examples show placeholders (SECRET, API_KEY, etc.) for developers to replace with their own values. The agent does not execute this code.


## OAuth 2.0 Flows

| Flow | Use Case | Security |
|------|----------|----------|
| **Authorization Code + PKCE** | Web apps, mobile, SPAs | [YES] Best |
| **Authorization Code** | Server-side web apps | [YES] Good |
| **Implicit** | [NO] Deprecated | [NO] Don't use |
| **Client Credentials** | Service-to-service | [YES] Good |

**Always use PKCE** - even for server-side apps.

---

## Authorization Code + PKCE

```typescript
import crypto from 'crypto';

// Step 1: Generate PKCE challenge
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto
    .createHash('sha256')
    .update(verifier)
    .digest('base64url');
  
  return { verifier, challenge };
}

// Step 2: Redirect to provider
app.get('/auth/google', (req, res) => {
  const { verifier, challenge } = generatePKCE();
  const state = crypto.randomBytes(16).toString('hex');
  
  // Store for verification
  req.session.oauthState = state;
  req.session.pkceVerifier = verifier;
  
  const params = new URLSearchParams({
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: 'https://myapp.com/auth/google/callback',
    response_type: 'code',
    scope: 'openid email profile',
    state,
    code_challenge: challenge,
    code_challenge_method: 'S256'
  });
  
  res.redirect(`https://accounts.google.com/o/oauth2/v2/auth?${params}`);
});

// Step 3: Handle callback
app.get('/auth/google/callback', async (req, res) => {
  const { code, state } = req.query;
  
  // Verify state
  if (state !== req.session.oauthState) {
    return res.status(400).json({ error: 'Invalid state' });
  }
  
  // Exchange code for tokens
  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: GOOGLE_CLIENT_ID,
      client_secret: GOOGLE_CLIENT_SECRET,
      code,
      grant_type: 'authorization_code',
      redirect_uri: 'https://myapp.com/auth/google/callback',
      code_verifier: req.session.pkceVerifier
    })
  });
  
  const tokens = await tokenResponse.json();
  
  // Get user info
  const userInfo = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
    headers: { Authorization: `Bearer ${tokens.access_token}` }
  }).then(r => r.json());
  
  // Create or link account
  const user = await findOrCreateUser({
    email: userInfo.email,
    name: userInfo.name,
    googleId: userInfo.sub,
    emailVerified: userInfo.email_verified
  });
  
  // Complete login
  await createSession(req, user);
  res.redirect('/dashboard');
});
```

---

## Social Login Providers

### Google
```typescript
const config = {
  authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenUrl: 'https://oauth2.googleapis.com/token',
  userInfoUrl: 'https://www.googleapis.com/oauth2/v3/userinfo',
  scopes: ['openid', 'email', 'profile']
};
```

### GitHub
```typescript
const config = {
  authUrl: 'https://github.com/login/oauth/authorize',
  tokenUrl: 'https://github.com/login/oauth/access_token',
  userInfoUrl: 'https://api.github.com/user',
  emailUrl: 'https://api.github.com/user/emails', // Email is separate
  scopes: ['read:user', 'user:email']
};
```

### Apple Sign In
```typescript
// Apple requires JWT client_secret
const clientSecret = jwt.sign({
  iss: APPLE_TEAM_ID,
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 86400 * 180,
  aud: 'https://appleid.apple.com',
  sub: APPLE_CLIENT_ID
}, APPLE_PRIVATE_KEY, { algorithm: 'ES256' });

const config = {
  authUrl: 'https://appleid.apple.com/auth/authorize',
  tokenUrl: 'https://appleid.apple.com/auth/token',
  scopes: ['name', 'email'] // name only on first login!
};
```

---

## Account Linking

**Handle same email from multiple providers:**

```typescript
async function findOrCreateUser(providerData: {
  email: string;
  provider: string;
  providerId: string;
  name?: string;
}) {
  const { email, provider, providerId, name } = providerData;
  
  // Check if provider link exists
  const linked = await db.oauthLinks.findOne({ provider, providerId });
  if (linked) {
    return db.users.findById(linked.userId);
  }
  
  // Check if email exists
  const existing = await db.users.findByEmail(email);
  
  if (existing) {
    // Link to existing account
    await db.oauthLinks.create({
      userId: existing.id,
      provider,
      providerId
    });
    return existing;
  }
  
  // Create new account
  const user = await db.users.create({
    email,
    name,
    emailVerified: true // Provider verified
  });
  
  await db.oauthLinks.create({
    userId: user.id,
    provider,
    providerId
  });
  
  return user;
}
```

---

## OpenID Connect (OIDC)

**OAuth + identity layer.** Adds:
- ID token (JWT with user info)
- UserInfo endpoint
- Standard claims

```typescript
// ID token contains user info directly
const idToken = tokens.id_token;
const payload = jwt.decode(idToken); // Verify signature in production!

// Standard claims
{
  sub: '123456789',        // Unique user ID
  email: 'user@example.com',
  email_verified: true,
  name: 'John Doe',
  picture: 'https://...',
  iss: 'https://accounts.google.com',
  aud: 'your-client-id',
  exp: 1234567890,
  iat: 1234567890
}
```

---

## Enterprise SSO

### SAML 2.0

```typescript
// Using passport-saml or saml2-js
import { SAML } from 'saml2-js';

const sp = new SAML.ServiceProvider({
  entity_id: 'https://myapp.com/saml/metadata',
  assert_endpoint: 'https://myapp.com/saml/acs',
  certificate: SP_CERTIFICATE,
  private_key: SP_PRIVATE_KEY
});

const idp = new SAML.IdentityProvider({
  sso_login_url: 'https://idp.customer.com/saml/login',
  certificates: [IDP_CERTIFICATE]
});

// Login redirect
app.get('/saml/login', (req, res) => {
  sp.create_login_request_url(idp, {}, (err, loginUrl) => {
    res.redirect(loginUrl);
  });
});

// Handle response
app.post('/saml/acs', (req, res) => {
  sp.post_assert(idp, { request_body: req.body }, (err, response) => {
    const email = response.user.email;
    // Create session...
  });
});
```

### OIDC for Enterprise

```typescript
// Each customer has their own OIDC config
const customerConfig = await db.ssoConfigs.findByDomain(email.split('@')[1]);

if (customerConfig) {
  // Redirect to their IdP
  const params = new URLSearchParams({
    client_id: customerConfig.clientId,
    redirect_uri: 'https://myapp.com/auth/oidc/callback',
    response_type: 'code',
    scope: 'openid email profile',
    state: encodeState({ customerId: customerConfig.id })
  });
  
  return res.redirect(`${customerConfig.authUrl}?${params}`);
}
```

---

## Security Checklist

- [ ] Always use PKCE (even server-side)
- [ ] Validate `state` parameter
- [ ] Verify ID token signature
- [ ] Check `aud` claim matches your client ID
- [ ] Check `iss` claim matches expected issuer
- [ ] Use short-lived authorization codes
- [ ] Store tokens encrypted at rest
- [ ] Refresh tokens before expiry
