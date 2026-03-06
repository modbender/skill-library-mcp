# Multi-Factor Authentication - Auth

> **Reference patterns only.** Code examples show placeholders (SECRET, API_KEY, etc.) for developers to replace with their own values. The agent does not execute this code.


## Methods Comparison

| Method | Security | UX | Phishing Resistant | Use Case |
|--------|----------|----|--------------------|----------|
| **WebAuthn/Passkeys** | 5/5 | 5/5 | [YES] Yes | Best option, offer when possible |
| **TOTP (Authenticator)** | 4/5 | 3/5 | [NO] No | Good default, widely supported |
| **Push notification** | 4/5 | 4/5 | [NO] No | Mobile apps with own auth app |
| **Email OTP** | 3/5 | 3/5 | [NO] No | Low-friction option |
| **SMS OTP** | 2/5 | 4/5 | [NO] No | [!] Avoid - SIM swapping |

---

## TOTP (Time-Based One-Time Password)

**Setup flow:**
```typescript
import { authenticator } from 'otplib';
import qrcode from 'qrcode';

// Generate secret
const secret = authenticator.generateSecret();

// Generate QR code for authenticator apps
const otpauthUrl = authenticator.keyuri(user.email, 'MyApp', secret);
const qrCodeDataUrl = await qrcode.toDataURL(otpauthUrl);

// Store secret temporarily until verified
await redis.setex(`mfa_setup:${user.id}`, 600, secret);

return { qrCode: qrCodeDataUrl, secret }; // secret for manual entry
```

**Verification:**
```typescript
// Verify setup (user enters code from app)
app.post('/mfa/verify-setup', requireAuth, async (req, res) => {
  const { code } = req.body;
  const secret = await redis.get(`mfa_setup:${req.user.id}`);
  
  if (!authenticator.verify({ token: code, secret })) {
    return res.status(400).json({ error: 'Invalid code' });
  }
  
  // Generate backup codes
  const backupCodes = generateBackupCodes();
  const hashedCodes = backupCodes.map(c => bcrypt.hashSync(c, 10));
  
  // Enable MFA
  await db.users.update(req.user.id, {
    mfaEnabled: true,
    mfaSecret: encrypt(secret), // Encrypt at rest
    backupCodes: hashedCodes
  });
  
  await redis.del(`mfa_setup:${req.user.id}`);
  
  return res.json({ 
    success: true, 
    backupCodes // Show ONCE
  });
});

// Verify during login
function verifyTOTP(secret: string, code: string): boolean {
  return authenticator.verify({ 
    token: code, 
    secret,
    window: 1 // Allow 1 step tolerance (30 sec each way)
  });
}
```

---

## WebAuthn / Passkeys

**The gold standard.** Phishing-resistant, no shared secrets.

**Registration:**
```typescript
import { generateRegistrationOptions, verifyRegistrationResponse } from '@simplewebauthn/server';

// Step 1: Generate challenge
app.post('/webauthn/register/start', requireAuth, async (req, res) => {
  const options = await generateRegistrationOptions({
    rpName: 'My App',
    rpID: 'myapp.com',
    userID: user.id,
    userName: user.email,
    attestationType: 'none',
    authenticatorSelection: {
      residentKey: 'preferred',
      userVerification: 'preferred'
    }
  });
  
  await redis.setex(`webauthn:${user.id}`, 300, JSON.stringify(options));
  res.json(options);
});

// Step 2: Verify response
app.post('/webauthn/register/finish', requireAuth, async (req, res) => {
  const expectedOptions = JSON.parse(await redis.get(`webauthn:${user.id}`));
  
  const verification = await verifyRegistrationResponse({
    response: req.body,
    expectedChallenge: expectedOptions.challenge,
    expectedOrigin: 'https://myapp.com',
    expectedRPID: 'myapp.com'
  });
  
  if (verification.verified) {
    await db.credentials.create({
      userId: user.id,
      credentialId: verification.registrationInfo.credentialID,
      publicKey: verification.registrationInfo.credentialPublicKey,
      counter: verification.registrationInfo.counter
    });
  }
  
  res.json({ verified: verification.verified });
});
```

**Authentication similar pattern** - generate challenge, verify signature.

---

## Backup Codes

**For MFA recovery when device lost:**

```typescript
// Generate 10 codes on MFA setup
function generateBackupCodes(): string[] {
  return Array.from({ length: 10 }, () =>
    crypto.randomBytes(4).toString('hex').toUpperCase() // e.g., "A1B2C3D4"
  );
}

// Verify backup code (single use)
async function verifyBackupCode(userId: string, code: string): Promise<boolean> {
  const user = await db.users.findById(userId);
  
  for (let i = 0; i < user.backupCodes.length; i++) {
    if (await bcrypt.compare(code.toUpperCase(), user.backupCodes[i])) {
      // Remove used code
      user.backupCodes.splice(i, 1);
      await db.users.update(userId, { backupCodes: user.backupCodes });
      
      // Warn if running low
      if (user.backupCodes.length <= 2) {
        await sendEmail(user.email, 'Generate new backup codes', '...');
      }
      
      return true;
    }
  }
  
  return false;
}
```

---

## MFA Login Flow

```
1. User enters email + password
     |
2. Verify credentials (don't complete login yet)
     |
3. Check if MFA enabled
     | (yes)
4. Issue temporary "MFA pending" token (5 min expiry)
     |
5. Return { mfaRequired: true, mfaToken }
     |
6. User enters MFA code
     |
7. Verify MFA token + code
     |
8. Complete login, issue session/JWT
```

```typescript
// Step 1: Password verification
app.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await verifyCredentials(email, password);
  
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  if (user.mfaEnabled) {
    // Don't complete login yet
    const mfaToken = jwt.sign(
      { sub: user.id, purpose: 'mfa' },
      MFA_SECRET,
      { expiresIn: '5m' }
    );
    return res.json({ mfaRequired: true, mfaToken });
  }
  
  // No MFA, complete login
  return completeLogin(res, user);
});

// Step 2: MFA verification
app.post('/auth/mfa', async (req, res) => {
  const { mfaToken, code } = req.body;
  
  const payload = jwt.verify(mfaToken, MFA_SECRET);
  if (payload.purpose !== 'mfa') {
    return res.status(401).json({ error: 'Invalid token' });
  }
  
  const user = await db.users.findById(payload.sub);
  const secret = decrypt(user.mfaSecret);
  
  // Try TOTP first
  if (verifyTOTP(secret, code)) {
    return completeLogin(res, user);
  }
  
  // Try backup code
  if (await verifyBackupCode(user.id, code)) {
    return completeLogin(res, user);
  }
  
  return res.status(401).json({ error: 'Invalid code' });
});
```

---

## Step-Up Authentication

**Require MFA for sensitive operations even if already logged in:**

```typescript
// Middleware for sensitive routes
async function requireRecentMFA(req, res, next) {
  const lastMFA = req.session.lastMFAVerification;
  const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
  
  if (!lastMFA || lastMFA < fiveMinutesAgo) {
    return res.status(403).json({ 
      error: 'MFA required',
      action: 'step_up_mfa'
    });
  }
  
  next();
}

// Use on sensitive endpoints
app.post('/account/delete', requireAuth, requireRecentMFA, deleteAccount);
app.post('/transfer/large', requireAuth, requireRecentMFA, transferFunds);
```
