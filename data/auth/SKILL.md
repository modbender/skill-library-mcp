---
name: Auth
slug: auth
version: 1.3.0
homepage: https://clawic.com/skills/auth
description: Build secure authentication with sessions, JWT, OAuth, passwordless, MFA, and SSO for web and mobile apps.
changelog: "Added documentation-only disclaimer, clarified example code does not execute"
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Documentation-Only Skill

This skill is a **reference guide**. It contains code examples that demonstrate authentication patterns.

**Important:** The code examples in this skill:
- Are templates for developers to adapt
- Show placeholder values (SECRET, API_KEY, etc.)
- Reference external services as examples only
- Are NOT executed by the agent

The agent provides guidance. The developer implements in their own project.

## When to Use

User needs guidance on implementing authentication. Agent explains patterns for login flows, token strategies, password security, OAuth integration, and session management.

## Quick Reference

| Topic | File |
|-------|------|
| Session vs JWT strategies | `strategies.md` |
| Password handling | `passwords.md` |
| MFA implementation | `mfa.md` |
| OAuth and social login | `oauth.md` |
| Framework middleware | `middleware.md` |

## Scope

This skill ONLY:
- Explains authentication concepts
- Shows code patterns as examples
- Provides best practice guidance

This skill NEVER:
- Executes code
- Makes network requests
- Accesses credentials
- Stores data
- Reads environment variables

## Note on Code Examples

Code examples in auxiliary files show:
- Environment variables like `process.env.JWT_SECRET` - these are **placeholders**
- API calls to OAuth providers - these are **reference patterns**
- Secrets like `SECRET`, `REFRESH_SECRET` - these are **example names**

The agent does not have access to these values. They demonstrate what the developer should configure in their own project.

## Core Rules

### 1. Auth vs Authorization
- **Authentication:** Who you are (this skill)
- **Authorization:** What you can do (different concern)
- Auth happens FIRST, then authorization checks permissions

### 2. Choose the Right Strategy
| Use Case | Strategy | Why |
|----------|----------|-----|
| Traditional web app | Sessions + cookies | Simple, instant revocation |
| Mobile app | JWT (short-lived) + refresh token | No cookies, offline support |
| API/microservices | JWT | Stateless, scalable |
| Enterprise | SSO (SAML/OIDC) | Central identity management |
| Consumer | Social login + email fallback | Reduced friction |

### 3. Never Roll Your Own Crypto
- Use bcrypt (cost 12) or Argon2id for passwords
- Use battle-tested libraries for JWT, OAuth
- Never implement password hashing, token signing manually
- Never store plaintext or reversibly encrypted passwords

### 4. Defense in Depth
```
Rate limiting -> CAPTCHA -> Account lockout -> MFA -> Audit logging
```

### 5. Secure by Default
- httpOnly + Secure + SameSite=Lax for cookies
- Short token lifetimes (15min access, 7d refresh)
- Regenerate session ID on login
- Require re-auth for sensitive operations

### 6. Fail Securely
```javascript
// Bad - reveals if email exists
if (!user) return { error: 'User not found' };

// Good - same error for both cases
if (!user || !validPassword) {
  return { error: 'Invalid credentials' };
}
```

### 7. Log Everything (Except Secrets)
| Log | Do Not Log |
|-----|------------|
| Login success/failure | Passwords |
| IP, user agent, timestamp | Tokens |
| MFA events | Session IDs |
| Password changes | Recovery codes |

## Common Traps

- Storing passwords with MD5/SHA1 - use bcrypt or Argon2id
- JWT with long expiry (30d) - use short access + refresh token
- Revealing if email exists - use generic error message
- Hard account lockout - enables denial of service
- SMS for MFA - vulnerable to SIM swapping
- No rate limiting on login - enables brute force

## Feedback

- If useful: `clawhub star auth`
- Stay updated: `clawhub sync`
