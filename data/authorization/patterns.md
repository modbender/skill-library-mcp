# Implementation Patterns — Authorization

## Permission Check Function

**Core pattern:** Single function for all permission checks.

```typescript
// Central authorization function
async function can(
  user: User,
  action: string,
  resource?: Resource
): Promise<boolean> {
  // 1. Get user permissions (from roles + direct grants)
  const permissions = await getPermissions(user);
  
  // 2. Check explicit deny first
  if (permissions.denied.includes(action)) return false;
  
  // 3. Check wildcard (admin)
  if (permissions.allowed.includes('*')) return true;
  
  // 4. Check specific permission
  if (permissions.allowed.includes(action)) return true;
  
  // 5. Check resource-specific (ownership, team)
  if (resource && await checkResourceAccess(user, action, resource)) {
    return true;
  }
  
  // 6. Default deny
  return false;
}
```

---

## Permission Caching

**Problem:** DB query per permission check = slow.

```typescript
// Cache permissions in JWT claims (short-lived)
const token = jwt.sign({
  sub: user.id,
  permissions: ['docs:read', 'docs:write'],
  roles: ['editor'],
  exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour
}, secret);

// Or Redis cache (longer-lived, invalidatable)
await redis.setex(
  `permissions:${user.id}`,
  300, // 5 min TTL
  JSON.stringify(permissions)
);
```

**Invalidation triggers:**
- Role assignment changed
- User added/removed from team
- Resource sharing changed

---

## Scope Hierarchy

**Pattern:** Permissions have scope levels.

```
documents:read:own   → Only own documents
documents:read:team  → Own + team documents
documents:read:org   → Own + team + org documents
documents:read:all   → Everything (admin)
```

**Check with scope escalation:**
```typescript
function canWithScope(user, action, resource) {
  const scopes = ['own', 'team', 'org', 'all'];
  
  for (const scope of scopes) {
    if (user.permissions.includes(`${action}:${scope}`)) {
      if (matchesScope(user, resource, scope)) return true;
    }
  }
  return false;
}
```

---

## Policy as Code

**Pattern:** Define policies as data/code, not hardcoded conditionals.

```typescript
// policies.ts
export const policies = [
  {
    action: 'documents:delete',
    effect: 'allow',
    conditions: {
      'user.role': { in: ['admin', 'owner'] },
      'resource.status': { not: 'archived' }
    }
  },
  {
    action: 'documents:delete',
    effect: 'deny',
    conditions: {
      'context.isWeekend': true
    }
  }
];

// Evaluate against policies
function evaluate(user, action, resource, context) {
  const applicable = policies.filter(p => p.action === action);
  
  // Deny wins
  for (const policy of applicable) {
    if (policy.effect === 'deny' && matchConditions(policy, {user, resource, context})) {
      return false;
    }
  }
  
  // Then check allows
  for (const policy of applicable) {
    if (policy.effect === 'allow' && matchConditions(policy, {user, resource, context})) {
      return true;
    }
  }
  
  return false; // Default deny
}
```

---

## Resource-Level Checks

**Pattern:** Check at resource fetch, not just route.

```typescript
// ❌ Bad — only route protection
app.get('/documents/:id', requireAuth, async (req, res) => {
  const doc = await Document.findById(req.params.id);
  res.json(doc); // Anyone authenticated can see any doc!
});

// ✅ Good — resource-level check
app.get('/documents/:id', requireAuth, async (req, res) => {
  const doc = await Document.findById(req.params.id);
  
  if (!await can(req.user, 'documents:read', doc)) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  
  res.json(doc);
});
```

---

## Batch Permission Checks

**Pattern:** Check multiple resources efficiently.

```typescript
// Get all documents user can access
async function getAccessibleDocuments(user, documents) {
  // Single query for user's permissions + team memberships
  const access = await getUserAccessContext(user);
  
  return documents.filter(doc => {
    // Check ownership
    if (doc.ownerId === user.id) return true;
    
    // Check team access
    if (access.teamIds.includes(doc.teamId)) return true;
    
    // Check explicit shares
    if (access.sharedResourceIds.includes(doc.id)) return true;
    
    return false;
  });
}
```

---

## Audit Logging

**Pattern:** Log every authorization decision.

```typescript
async function can(user, action, resource) {
  const decision = await evaluate(user, action, resource);
  
  await auditLog.create({
    timestamp: new Date(),
    userId: user.id,
    action,
    resourceId: resource?.id,
    resourceType: resource?.type,
    decision: decision ? 'allow' : 'deny',
    reason: decision.reason, // "role:admin" or "denied:no_permission"
    context: {
      ip: request.ip,
      userAgent: request.headers['user-agent']
    }
  });
  
  return decision.allowed;
}
```

Essential for compliance (SOC2, HIPAA, GDPR).
