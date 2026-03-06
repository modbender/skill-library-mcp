# Environment Variable Patterns on Cloudflare Workers

## The Core Problem

Cloudflare Workers do NOT use `process.env`. Bindings (Hyperdrive, KV, D1, R2) are injected via request context.

With `@opennextjs/cloudflare`, use `getCloudflareContext()`:

```typescript
import { getCloudflareContext } from '@opennextjs/cloudflare';

// ✅ Inside a function (request context available)
export async function GET() {
  const env = getCloudflareContext().env;
  const value = env.MY_VAR;
}

// ❌ At module top level (no request context)
const env = getCloudflareContext().env; // THROWS ERROR
```

## What Still Works with process.env

`NEXT_PUBLIC_*` variables set in `wrangler.toml [vars]` are inlined at build time and available via `process.env.NEXT_PUBLIC_*` in client components.

Server-side `process.env` for simple string vars (set in `[vars]`) MAY work depending on the adapter version, but bindings (Hyperdrive, KV, etc.) NEVER appear in `process.env`.

## Migration Checklist

1. Find all `process.env.DATABASE_URL` or similar DB connection env vars
2. Replace with `getCloudflareContext().env.HYPERDRIVE.connectionString`
3. Find all top-level DB initialization → move inside functions
4. Replace `export const db = ...` with `export const getDb = cache(() => ...)`
5. Update all imports: `{ db }` → `{ getDb }` and add `const db = getDb()` in each function
6. Test locally with `wrangler dev` (uses `.dev.vars` for local connection strings)
