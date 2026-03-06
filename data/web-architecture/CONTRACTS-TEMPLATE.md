# API Contracts

> Define all data shapes BEFORE implementation. All agents reference this document.

---

## Users

### Schema
```typescript
// convex/schema.ts
users: defineTable({
  clerkId: v.string(),
  email: v.string(),
  name: v.string(),
  imageUrl: v.optional(v.string()),
  tier: v.union(v.literal("free"), v.literal("pro"), v.literal("premium")),
  stripeCustomerId: v.optional(v.string()),
  createdAt: v.number(),
})
  .index("by_clerk_id", ["clerkId"])
  .index("by_email", ["email"]),
```

### Queries

#### users.get
- **Args:** `{ id: Id<"users"> }`
- **Returns:** `User | null`
- **Used by:** User detail page, settings, profile

#### users.getByClerkId
- **Args:** `{ clerkId: string }`
- **Returns:** `User | null`
- **Used by:** Auth sync, session lookup

#### users.list
- **Args:** `{ limit?: number, cursor?: string }`
- **Returns:** `{ users: User[], nextCursor: string | null }`
- **Used by:** Admin user list

### Mutations

#### users.create
- **Args:** `{ clerkId: string, email: string, name: string }`
- **Returns:** `Id<"users">`
- **Used by:** Clerk webhook, sign-up flow

#### users.update
- **Args:** `{ id: Id<"users">, name?: string, imageUrl?: string }`
- **Returns:** `void`
- **Used by:** Settings form, admin edit

#### users.delete
- **Args:** `{ id: Id<"users"> }`
- **Returns:** `void`
- **Used by:** Admin, account deletion

---

## [Entity Name]

### Schema
```typescript
// convex/schema.ts
entityName: defineTable({
  // fields
})
  .index("by_x", ["x"]),
```

### Queries

#### entityName.get
- **Args:** `{ id: Id<"entityName"> }`
- **Returns:** `EntityName | null`
- **Used by:** [list pages/components that use this]

#### entityName.list
- **Args:** `{ filter?: string, limit?: number }`
- **Returns:** `EntityName[]`
- **Used by:** [list pages/components]

### Mutations

#### entityName.create
- **Args:** `{ ... }`
- **Returns:** `Id<"entityName">`
- **Used by:** [list pages/components]

#### entityName.update
- **Args:** `{ id: Id<"entityName">, ... }`
- **Returns:** `void`
- **Used by:** [list pages/components]

#### entityName.delete
- **Args:** `{ id: Id<"entityName"> }`
- **Returns:** `void`
- **Used by:** [list pages/components]

---

## Shared Types

```typescript
// lib/types.ts

export type User = {
  _id: Id<"users">;
  clerkId: string;
  email: string;
  name: string;
  imageUrl?: string;
  tier: "free" | "pro" | "premium";
  stripeCustomerId?: string;
  createdAt: number;
};

export type EntityName = {
  _id: Id<"entityName">;
  // ... fields matching schema
};
```

---

## Frontend → Backend Contract

| Component | Queries Used | Mutations Used |
|-----------|--------------|----------------|
| UserProfile | users.get | users.update |
| UserList | users.list | - |
| Settings | users.get | users.update |
| AdminUsers | users.list | users.update, users.delete |

---

## Notes

- All timestamps are Unix milliseconds (`Date.now()`)
- All IDs are Convex `Id<"tableName">` types
- Pagination uses cursor-based pattern
- Auth context available via `ctx.auth.getUserIdentity()`
