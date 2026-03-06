# Access Control Models — Authorization

## ACL (Access Control Lists)

**Concept:** Each resource has a list of who can do what.

```
document_123:
  - alice: read, write
  - bob: read
  - public: none
```

**Pros:** Simple, intuitive, direct control
**Cons:** Doesn't scale — 1000 users × 1000 resources = 1M entries

**Use when:** Small systems, file permissions, ownership-based access.

---

## RBAC (Role-Based Access Control)

**Concept:** Users have roles, roles have permissions.

```
Roles:
  editor: [documents:read, documents:write]
  viewer: [documents:read]

Users:
  alice: [editor]
  bob: [viewer]
```

**Hierarchy:** Roles can inherit from other roles.
```
admin → manager → employee → guest
         ↑ inherits all permissions below
```

**Pros:** Scales with organization, easy to audit, maps to jobs
**Cons:** Role explosion when edge cases appear

**Use when:** Organizations with clear job functions.

---

## ABAC (Attribute-Based Access Control)

**Concept:** Policies evaluate attributes of subject, resource, action, context.

```json
{
  "effect": "allow",
  "action": "documents:write",
  "condition": {
    "subject.department": "equals",
    "resource.department": true
  }
}
```

**Attributes:**
- **Subject:** user.role, user.department, user.clearance
- **Resource:** doc.owner, doc.classification, doc.department  
- **Action:** read, write, delete, share
- **Context:** time, location, device, risk_score

**Pros:** Extremely flexible, handles dynamic rules
**Cons:** Complex to debug, policy conflicts

**Use when:** Complex organizations, context-dependent access, compliance requirements.

---

## ReBAC (Relationship-Based Access Control)

**Concept:** Access based on relationships between entities.

```
alice --(owner)--> document_123
bob --(member)--> team_alpha
team_alpha --(viewer)--> document_123
∴ bob can view document_123
```

**Graph traversal:** Follow relationships to determine access.

**Pros:** Natural for social apps, sharing, organizational hierarchies
**Cons:** Complex queries, graph must stay consistent

**Use when:** Social features, shared workspaces, Google Docs-style permissions.

---

## Hybrid Approaches

Most real systems combine models:

```
RBAC for baseline     → "editors can edit"
+ ABAC for context    → "during business hours"
+ ReBAC for sharing   → "if shared with them"
```

**Evaluation order:**
1. RBAC grants base permissions
2. ABAC adds/restricts based on context
3. ReBAC handles explicit shares
4. Explicit deny always wins

---

## Decision Matrix

| Question | If Yes → |
|----------|----------|
| Do users own resources? | ACL or ReBAC |
| Clear organizational roles? | RBAC |
| Rules depend on context? | ABAC |
| Social sharing needed? | ReBAC |
| Compliance/audit required? | ABAC |
| Need to start simple? | RBAC → evolve |
