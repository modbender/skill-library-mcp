---
name: Encryption
description: Encrypt files, secure passwords, manage keys, and audit code for cryptographic best practices.
---

## When to Use
- Encrypting files, database fields, or app storage
- Password hashing (bcrypt, argon2)
- Key management, rotation, derivation
- TLS/certificate configuration
- Auditing code for crypto mistakes
- Mobile secure storage (Keychain, Keystore)

## Algorithm Selection

| Purpose | Use | Avoid |
|---------|-----|-------|
| Passwords | argon2id, bcrypt (cost≥12) | MD5, SHA1, plain SHA256 |
| Symmetric | AES-256-GCM, ChaCha20-Poly1305 | AES-ECB, DES, RC4 |
| Asymmetric | RSA-4096+OAEP, Ed25519, P-256 | RSA-1024, PKCS#1 v1.5 |
| Key derivation | PBKDF2 (≥600k), scrypt, argon2 | Single-pass hash |
| JWT signing | RS256, ES256 | HS256 with weak secret |
| TLS | 1.2+ only | TLS 1.0/1.1, SSLv3 |

## Critical Rules

1. **Never reuse IVs/nonces** — AES-GCM + repeated nonce = catastrophic
2. **Use authenticated encryption (AEAD)** — Plain CBC enables padding oracles
3. **Hash passwords, don't encrypt** — Hashing is one-way
4. **No hardcoded keys** — Use env vars, KMS, or Vault
5. **No Math.random() for crypto** — Use CSPRNG only
6. **Constant-time comparisons** — Prevent timing attacks on secrets
7. **Separate keys by purpose** — Encryption ≠ signing ≠ backup

## File Encryption (CLI)

```bash
# age (modern, simple)
age -p -o file.age file.txt
age -d -o file.txt file.age

# GPG
gpg -c --cipher-algo AES256 file.txt
```

## Platform-Specific

See `patterns.md` for code snippets:
- Password hashing (Node, Python, Go)
- Envelope encryption with KMS
- JWT with RS256 key rotation
- Secure token generation

See `mobile.md` for:
- iOS Keychain wrapper
- Android EncryptedSharedPreferences
- SQLCipher setup
- Biometric auth integration
- Certificate pinning

See `infra.md` for:
- TLS certificate auto-renewal
- HashiCorp Vault policies
- mTLS between services
- Backup encryption verification

## Audit Checklist

- [ ] No plaintext passwords in DB/logs/env
- [ ] No secrets in git history
- [ ] No hardcoded keys in source
- [ ] No Math.random() for security
- [ ] No deprecated algorithms (MD5, SHA1, DES)
- [ ] No disabled cert validation
- [ ] IVs/nonces never reused
- [ ] PBKDF2 iterations ≥600k / bcrypt cost ≥12
- [ ] TLS 1.2+ enforced, old protocols disabled
- [ ] Key rotation procedure documented
