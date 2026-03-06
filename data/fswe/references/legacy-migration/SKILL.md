# Legacy Code Migration

## Strangler Pattern

```
Before:                    After:
┌─────────────┐           ┌─────────────┐
│  PHP        │           │   New TS    │
│  Monolith   │           │   Service   │
└─────────────┘           └─────────────┘
      ↑                         ↑
      │     ┌─────────────┐      │
      ├────►│   Facade   │◄─────┤
      │     │  (Gateway) │      │
      │     └─────────────┘      │
      │            ↑            │
      │            │            │
      └────────────┴────────────┘
```

## Incremental Extraction

```typescript
// New service imports from legacy via API
// Once feature is migrated, point to new service

// Phase 1: API Gateway routes to PHP
router.get('/users', proxyToLegacy)

// Phase 2: Extract to new service
router.get('/users', userController.findAll)

// Phase 3: Remove legacy dependency
// DELETE /users from PHP
```

## Risk Mapping

| Feature | Complexity | Risk | Migration Order |
|---------|------------|------|-----------------|
| Auth | High | Critical | 1st |
| User Profile | Medium | Medium | 2nd |
| Dashboard | Low | Low | 3rd |
| Legacy Reports | High | Low | Last |

## Checklist

- [ ] Audit legacy codebase
- [ ] Map dependencies
- [ ] Identify bounded contexts
- [ ] Implement strangler facade
- [ ] Extract one feature at a time
- [ ] Run both systems in parallel
- [ ] Cut over gradually
