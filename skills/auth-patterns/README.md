# Auth Patterns — Authentication & Authorization

Authentication and authorization patterns — JWT, OAuth 2.0, sessions, RBAC/ABAC, password security, MFA, and vulnerability prevention. Use when implementing login flows, protecting routes, managing tokens, or auditing auth security.

## What's Inside

- Authentication Methods — JWT, session-based, OAuth 2.0, API keys, magic links, passkeys/WebAuthn
- JWT Patterns — dual-token strategy, token structure, signing algorithms, storage, expiration
- OAuth 2.0 Flows — Authorization Code + PKCE, Client Credentials, Device Code
- Session Management — server-side sessions, session security, Redis/PostgreSQL stores
- Authorization Patterns — RBAC, ABAC, permission-based, policy-based (OPA/Cedar), ReBAC
- Password Security — Argon2id, bcrypt, scrypt, NIST 800-63B guidelines
- Multi-Factor Authentication — TOTP, WebAuthn/Passkeys, hardware keys, backup codes
- Security Headers — HSTS, CSP, CORS, X-Frame-Options
- Common Vulnerabilities — 13 vulnerability patterns with prevention strategies

## When to Use

- Implementing login flows and authentication
- Protecting API routes and managing tokens
- Choosing between JWT, sessions, and OAuth 2.0
- Implementing role-based or attribute-based access control
- Auditing auth security and preventing vulnerabilities
- Adding MFA to an application

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/api/auth-patterns
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/api/auth-patterns .cursor/skills/auth-patterns
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/api/auth-patterns ~/.cursor/skills/auth-patterns
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/api/auth-patterns .claude/skills/auth-patterns
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/api/auth-patterns ~/.claude/skills/auth-patterns
```

## Related Skills

- `api-design` — API design principles including authentication requirements
- `error-handling` — Error types and HTTP error responses
- `rate-limiting` — Protecting auth endpoints from brute force

---

Part of the [API](..) skill category.
