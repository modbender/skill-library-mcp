---
name: Prisma
description: Write efficient Prisma queries, design schemas, and avoid common ORM pitfalls.
metadata:
  category: database
  skills: ["prisma", "orm", "database", "typescript", "nodejs"]
---

## Schema Design Traps

- `@default(cuid())` over `@default(uuid())` for IDs—shorter, URL-safe, still unique
- `@updatedAt` doesn't update on nested writes—must touch parent record explicitly
- Implicit many-to-many creates join table you can't customize—use explicit for extra fields
- `@unique` on nullable field allows multiple NULLs—intended behavior but often surprising
- Enum changes require migration—can't add values without downtime unless using String

## Query Patterns I Forget

- `findUniqueOrThrow` / `findFirstOrThrow`—cleaner than null check after findUnique
- `createMany` skips hooks and returns count only—use `create` in loop if you need records back
- `upsert` requires unique field in where—can't upsert on non-unique compound conditions
- `connectOrCreate` in nested writes—avoids separate existence check
- `select` and `include` are mutually exclusive—can't mix; use nested select inside include

## N+1 Query Prevention

- Default queries don't include relations—every access triggers new query
- `include` everything you'll access—check logs for unexpected queries
- Middleware can't see includes—adding includes in middleware doesn't help
- `findMany` + `include` better than loop of `findUnique`—single query vs N queries
- Dataloader pattern for GraphQL resolvers—Prisma doesn't batch automatically

## Transaction Gotchas

- `$transaction([])` array syntax rolls back all on any failure—use for atomic operations
- Interactive transactions `$transaction(async (tx) => {})` hold connection—keep short
- Default 5s timeout on interactive transactions—increase for long operations
- Nested writes are already transactional—don't wrap single create with relations in transaction
- `$transaction` doesn't retry on conflict—implement retry logic for optimistic locking

## Type Safety Gaps

- `include` result type doesn't narrow—TypeScript thinks relations might be undefined
- Raw queries return `unknown[]`—need manual type assertion or Prisma.$queryRaw<Type>
- JSON fields are `JsonValue`—cast needed; consider using typed JSON libraries
- `Prisma.validator` for reusable query fragments with correct types
- Return types of `$executeRaw` is count—not the affected rows

## Migration Issues

- `prisma db push` for prototyping—`prisma migrate dev` for version control
- `db push` can drop data silently—never use in production
- Shadow database required for `migrate dev`—needs create permission or separate DB
- Renaming field = drop + create by default—use `@map` to keep data
- Large table migrations lock table—consider running raw SQL with concurrent indexes

## Performance Traps

- `findMany` without `take` can return millions—always paginate
- `count()` scans table—expensive on large tables; consider approximate or cached counts
- `include` with large relations loads everything—use cursor pagination for big lists
- Relation counts: `_count: { select: { posts: true } }`—single query, not N+1
- `orderBy` on non-indexed field = slow—ensure indexes match sort patterns

## Raw Query Patterns

- `$queryRaw` for reads, `$executeRaw` for writes—different return types
- Use `Prisma.sql` template for safe interpolation—never string concatenation
- Raw queries bypass Prisma hooks and middleware—intentional but easy to forget
- `$queryRawUnsafe` exists but name is a warning—use only for dynamic column names
- Raw results use database column names—not Prisma field names if `@map` used

## Connection Management

- Default pool size 5—too low for production; set `connection_limit` in URL
- PlanetScale/serverless needs `?pool_timeout=0`—prevents connection exhaustion
- `$disconnect()` in scripts and tests—lambda/serverless should manage differently
- Prisma Accelerate or Data Proxy for edge/serverless—direct DB connections don't scale

## Middleware Patterns

- Soft delete via middleware: intercept `delete`, convert to `update`—but `deleteMany` needs handling
- Audit logging: `$use` captures all queries—but adds latency to every operation
- Middleware runs in order added—earlier middleware sees raw params
- Can't modify `include` in middleware—transform happens before middleware

## Common Mistakes

- Forgetting `await`—Prisma returns promises; queries don't execute without await
- `update` without where = error—unlike some ORMs, Prisma requires explicit where
- Decimal fields return strings—Prisma Decimal type, not JavaScript number
- `@relation` names must match—cryptic error if they don't
- Schema drift: production differs from migrations—run `prisma migrate deploy` in CI
