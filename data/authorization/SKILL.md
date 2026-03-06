---
name: Authorization
slug: authorization
version: 1.0.0
homepage: https://clawic.com/skills/authorization
description: Build secure access control with RBAC, ABAC, permissions, policies, and scope-based authorization.
metadata: {"clawdbot":{"emoji":"🔐","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to control what actions users can perform. Agent handles permission design, role hierarchies, policy evaluation, and access control middleware.

## Quick Reference

| Topic | File |
|-------|------|
| RBAC vs ABAC comparison | `models.md` |
| Implementation patterns | `patterns.md` |
| Framework middleware | `middleware.md` |

## Core Rules

### 1. Auth ≠ Authorization
- **Authentication:** Who you are (login, OAuth, tokens)
- **Authorization:** What you can do (permissions, roles, policies)
- Never mix concerns — auth happens BEFORE authorization

### 2. Principle of Least Privilege
- Default deny — explicit grants only
- Users get minimum permissions for their job
- Audit permissions periodically (revoke unused)
- Temporary elevation over permanent grants

### 3. Choose the Right Model
| Model | Best For | Complexity |
|-------|----------|------------|
| ACL | Simple resource ownership | Low |
| RBAC | Organizational hierarchies | Medium |
| ABAC | Dynamic context-based rules | High |
| ReBAC | Social graphs, sharing | High |

Start simple → evolve when needed.

### 4. Role Design Patterns
- Roles represent jobs, not permissions
- Max 3 inheritance levels (admin → manager → user)
- Avoid role explosion — combine with ABAC for edge cases
- Document role definitions (what can this role DO?)

### 5. Permission Naming
```
resource:action:scope
documents:write:own     ← Can edit own documents
documents:write:team    ← Can edit team documents
documents:delete:all    ← Can delete any document
```

Consistent naming prevents ambiguity.

### 6. Policy Evaluation Order
1. Explicit deny → always wins
2. Explicit allow → checked second
3. No match → default deny
4. Log all denials for debugging

### 7. Never Hardcode
```javascript
// ❌ Bad — hardcoded role check
if (user.role === 'admin') { ... }

// ✅ Good — permission check
if (can(user, 'settings:update')) { ... }
```

Roles change. Permissions are stable.

## Common Traps

- Checking roles instead of permissions → brittle when roles change
- OR logic in permissions → "can edit OR is admin" creates backdoors
- Caching permissions too long → stale grants after role changes
- Frontend-only checks → always verify server-side
- God roles → split "admin" into specific permission sets
- Circular inheritance → A inherits B inherits A crashes system

## Security & Privacy

**Data that stays local:**
- All documentation and patterns are reference material
- No data collection or external requests

**This skill does NOT:**
- Access your codebase automatically
- Make network requests
- Store any user data

## Feedback

- If useful: `clawhub star authorization`
- Stay updated: `clawhub sync`
