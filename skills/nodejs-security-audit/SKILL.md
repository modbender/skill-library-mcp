---
name: nodejs-security-audit
description: Audit Node.js HTTP servers and web apps for security vulnerabilities. Checks OWASP Top 10, CORS, auth bypass, XSS, path traversal, hardcoded secrets, missing headers, rate limiting, and input validation. Use when reviewing server code before deployment or after changes.
---

# Node.js Security Audit

Structured security audit for Node.js HTTP servers and web applications.

## Audit Checklist

### Critical (Must Fix Before Deploy)

**Hardcoded Secrets**
- Search for: API keys, passwords, tokens in source code
- Pattern: `grep -rn "password\|secret\|token\|apikey\|api_key" --include="*.js" --include="*.ts" | grep -v node_modules | grep -v "process.env\|\.env"`
- Fix: Move to env vars, fail if missing: `if (!process.env.SECRET) process.exit(1);`

**XSS in Dynamic Content**
- Search for: `innerHTML`, template literals injected into DOM, unsanitized user input in responses
- Fix: Use `textContent`, or escape: `str.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[c]))`

**SQL/NoSQL Injection**
- Search for: String concatenation in queries, `eval()`, `Function()` with user input
- Fix: Parameterized queries, input validation

### High (Should Fix)

**CORS Misconfiguration**
- Search for: `Access-Control-Allow-Origin: *`
- Fix: Allowlist specific origins: `const origin = ALLOWED.has(req.headers.origin) ? req.headers.origin : ALLOWED.values().next().value`

**Auth Bypass**
- Check: Every route that should require auth actually checks it
- Common miss: Static file routes, agent/webhook endpoints, health checks that expose data

**Path Traversal**
- Check: `path.normalize()` + `startsWith(allowedDir)` on all file-serving routes
- Extra: Resolve symlinks with `fs.realpathSync()` and re-check

### Medium (Recommended)

**Security Headers**
```javascript
const HEADERS = {
  'X-Frame-Options': 'SAMEORIGIN',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
};
// Apply to all responses
```

**Rate Limiting**
```javascript
const attempts = new Map(); // ip -> { count, resetAt }
const LIMIT = 5, WINDOW = 60000;
function isLimited(ip) {
  const now = Date.now(), e = attempts.get(ip);
  if (!e || now > e.resetAt) { attempts.set(ip, {count:1, resetAt:now+WINDOW}); return false; }
  return ++e.count > LIMIT;
}
```

**Input Validation**
- Body size limits: `if (bodySize > 1048576) { req.destroy(); return; }`
- JSON parse in try/catch
- Type checking on expected fields

### Low (Consider)

**Dependency Audit:** `npm audit`
**Error Leakage:** Don't send stack traces to clients in production
**Cookie Security:** `HttpOnly; Secure; SameSite=Strict`

## Report Format

```
## Security Audit: [filename]

### Critical
1. **[Category]** Description — File:Line — Fix: ...

### High
...

### Medium
...

### Low
...

### Summary
X critical, X high, X medium, X low
```
