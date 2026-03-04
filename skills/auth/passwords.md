# Password Handling - Auth

> **Reference patterns only.** Code examples show placeholders (SECRET, API_KEY, etc.) for developers to replace with their own values. The agent does not execute this code.


## Hashing

**Only use:**
- **bcrypt** (cost 10-12) - battle-tested, widely supported
- **Argon2id** - modern, memory-hard, recommended for new projects
- **scrypt** - good alternative to Argon2

**Never use:** MD5, SHA1, SHA256 (without salt/iterations), plaintext, reversible encryption

```typescript
// bcrypt
import bcrypt from 'bcrypt';
const hash = await bcrypt.hash(password, 12); // cost 12
const valid = await bcrypt.compare(password, hash);

// Argon2id
import argon2 from 'argon2';
const hash = await argon2.hash(password, { type: argon2.argon2id });
const valid = await argon2.verify(hash, password);
```

**Cost factor:** Should take 100-500ms to hash. Increase cost as hardware improves.

---

## Password Requirements

**Don't do:**
- Arbitrary complexity rules ("1 uppercase, 1 number, 1 symbol")
- Maximum length limits (allow 64+ chars)
- Periodic forced rotation

**Do:**
- Minimum 8 characters (12+ recommended)
- Check against breached password lists
- Show password strength meter
- Allow all characters including spaces

```typescript
// Check against HaveIBeenPwned
import crypto from 'crypto';

async function isBreached(password: string): Promise<boolean> {
  const hash = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
  const prefix = hash.slice(0, 5);
  const suffix = hash.slice(5);
  
  const res = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
  const text = await res.text();
  
  return text.includes(suffix);
}
```

---

## Password Reset

**Secure flow:**

```
1. User requests reset (email)
     |
2. Generate cryptographically random token
     |
3. Store HASHED token with expiry (1h max)
     |
4. Email link with token (HTTPS only)
     |
5. User clicks link, enters new password
     |
6. Verify token hash, check expiry
     |
7. Update password, invalidate token
     |
8. Invalidate ALL sessions
     |
9. Notify user via email
```

```typescript
// Generate reset token
const token = crypto.randomBytes(32).toString('hex');
const tokenHash = crypto.createHash('sha256').update(token).digest('hex');

await db.passwordResets.create({
  userId: user.id,
  tokenHash,
  expiresAt: new Date(Date.now() + 3600000) // 1 hour
});

// Send email with: https://app.com/reset?token=<token>

// Verify reset token
async function verifyResetToken(token: string) {
  const tokenHash = crypto.createHash('sha256').update(token).digest('hex');
  
  const reset = await db.passwordResets.findOne({
    tokenHash,
    expiresAt: { $gt: new Date() },
    used: false
  });
  
  if (!reset) throw new Error('Invalid or expired token');
  
  return reset;
}
```

**After password change:**
- Mark token as used
- Invalidate all user sessions
- Send confirmation email
- Log the event

---

## Account Recovery

**Options (from most to least secure):**

| Method | Security | UX | Recommendation |
|--------|----------|----|----|
| Email link | High | Good | [YES] Default |
| Backup codes | High | Poor | [YES] For MFA recovery |
| SMS code | Medium | Good | [!] Only if email unavailable |
| Security questions | Low | OK | [NO] Avoid |
| Support manual | Varies | Poor | [YES] Last resort with strong verification |

**Backup codes (for MFA recovery):**
```typescript
// Generate on MFA setup
function generateBackupCodes(count = 10): string[] {
  return Array.from({ length: count }, () =>
    crypto.randomBytes(4).toString('hex').toUpperCase()
  );
}

// Store hashed
const codes = generateBackupCodes();
const hashedCodes = codes.map(c => bcrypt.hashSync(c, 10));
await db.users.update(userId, { backupCodes: hashedCodes });

// Show codes ONCE to user, never again
return { codes, message: 'Save these. They will not be shown again.' };
```

---

## Password Change (Authenticated)

**Requirements:**
1. Require current password verification
2. Apply same validation as registration
3. Invalidate other sessions
4. Notify via email

```typescript
app.post('/account/password', requireAuth, async (req, res) => {
  const { currentPassword, newPassword } = req.body;
  
  // Verify current password
  const user = await db.users.findById(req.user.id);
  if (!await bcrypt.compare(currentPassword, user.passwordHash)) {
    return res.status(401).json({ error: 'Current password incorrect' });
  }
  
  // Validate new password
  if (newPassword.length < 12) {
    return res.status(400).json({ error: 'Password too short' });
  }
  if (await isBreached(newPassword)) {
    return res.status(400).json({ error: 'Password found in data breach' });
  }
  
  // Update password
  const newHash = await bcrypt.hash(newPassword, 12);
  await db.users.update(req.user.id, { passwordHash: newHash });
  
  // Invalidate other sessions (keep current)
  await invalidateSessionsExcept(req.user.id, req.sessionId);
  
  // Notify
  await sendEmail(user.email, 'Password changed', '...');
  
  res.json({ success: true });
});
```

---

## Timing Attack Prevention

**Problem:** Different response times reveal if user exists.

```typescript
// [NO] Vulnerable
async function login(email, password) {
  const user = await db.users.findByEmail(email);
  if (!user) return { error: 'Invalid credentials' }; // Fast return
  
  const valid = await bcrypt.compare(password, user.passwordHash); // Slow
  if (!valid) return { error: 'Invalid credentials' };
  
  return { success: true };
}

// [YES] Safe - constant time
async function login(email, password) {
  const user = await db.users.findByEmail(email);
  
  // Always compare against something
  const hashToCompare = user?.passwordHash || '$2b$12$fake.hash.here';
  const valid = await bcrypt.compare(password, hashToCompare);
  
  if (!user || !valid) {
    return { error: 'Invalid credentials' };
  }
  
  return { success: true };
}
```
