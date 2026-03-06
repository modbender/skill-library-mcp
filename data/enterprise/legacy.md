# Legacy Integration — Enterprise

## Assessment Framework

Before touching legacy systems:

| Question | Why |
|----------|-----|
| Who owns it? | Political cover needed |
| When last deployed? | Deployment risk gauge |
| What depends on it? | Blast radius mapping |
| Any documentation? | Knowledge extraction priority |
| What's the SLA? | Downtime tolerance |

## Integration Patterns

### Strangler Fig
Gradually replace legacy by routing traffic through new system.

```
[Client] → [Router] → [New Service] (growing)
                   ↘ [Legacy] (shrinking)
```

Best when: can intercept traffic, incremental value.

### Anti-Corruption Layer
Translate between legacy and new domain models.

```
[New Domain] ← [ACL] ← [Legacy Domain]
```

Best when: legacy concepts don't map cleanly.

### Database Sync
Keep legacy and new databases in sync during transition.

```
[Legacy DB] ↔ [CDC/ETL] ↔ [New DB]
```

Best when: data migration is the hard part.

## Common Traps

- Assuming legacy is "simple" because it's old → hidden complexity
- Rewriting without understanding → repeating old bugs
- Tight coupling to sync mechanism → new single point of failure
- No rollback plan → one-way door decisions

## Decision Tree

```
Can you wrap it?
├─ Yes → Strangler Fig
└─ No
   ├─ Is the interface stable? → Anti-Corruption Layer
   └─ No → Full migration with parallel run
```
