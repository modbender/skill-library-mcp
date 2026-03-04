---
name: vercel-to-cloudflare
description: Migrate Next.js projects from Vercel to Cloudflare Workers with Supabase/Hyperdrive support. Use when user wants to move a Next.js app off Vercel to reduce costs, deploy to Cloudflare Workers, configure Hyperdrive connection pooling, or fix Supabase connectivity issues on Cloudflare. Triggers on phrases like "migrate to Cloudflare", "Vercel too expensive", "deploy Next.js on Cloudflare Worker", "Cloudflare Hyperdrive setup", "Supabase on Cloudflare", "从Vercel迁移到Cloudflare", "Vercel太贵了", "部署到Cloudflare Worker".
---

# Vercel to Cloudflare Worker Migration

Migrate a Next.js + Supabase project from Vercel to Cloudflare Workers with Hyperdrive connection pooling.

## Quick Start

1. Run the analysis script to scan the project:
   ```bash
   python3 scripts/analyze_project.py <project-path>
   ```
2. Review the migration report
3. Run the migration script:
   ```bash
   python3 scripts/migrate.py <project-path>
   ```
4. Configure Hyperdrive: see [references/hyperdrive-setup.md](references/hyperdrive-setup.md)

## Core Migration Steps

### 1. Install @opennextjs/cloudflare adapter

```bash
npm install @opennextjs/cloudflare
```

Update `next.config.js` or `next.config.ts` if needed.

### 2. Rewrite environment variable access

All `process.env.XXX` for Cloudflare bindings (Hyperdrive, KV, D1, etc.) must use `getCloudflareContext()`:

```typescript
// BEFORE (Vercel/Node.js)
const url = process.env.DATABASE_URL;

// AFTER (Cloudflare Worker)
import { getCloudflareContext } from '@opennextjs/cloudflare';

function getConnectionInfo() {
  const env = getCloudflareContext().env;
  const hyperdrive = env.HYPERDRIVE as { connectionString?: string } | undefined;
  if (hyperdrive?.connectionString) {
    return { connectionString: hyperdrive.connectionString, source: 'hyperdrive' };
  }
  // Fallback for local dev
  const local = env.CLOUDFLARE_HYPERDRIVE_LOCAL_CONNECTION_STRING_HYPERDRIVE;
  if (local) {
    return { connectionString: local, source: 'hyperdrive-local' };
  }
  throw new Error('HYPERDRIVE is not configured');
}
```

### 3. Refactor global DB singleton to per-request pattern

```typescript
// BEFORE: Global singleton
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
const client = postgres(process.env.DATABASE_URL!);
export const db = drizzle(client);

// AFTER: Per-request with React cache
import { cache } from 'react';

export const getDb = cache(() => {
  const { connectionString, source } = getConnectionInfo();
  return createDatabase({
    connectionString,
    enableSSL: source === 'hyperdrive' ? false : 'require',
  });
});
```

Then replace all `import { db }` with `import { getDb }` and add `const db = getDb()` at the start of each function.

### 4. Configure wrangler.toml

```toml
name = "my-app"
main = ".open-next/worker.js"
compatibility_date = "2024-09-23"
compatibility_flags = ["nodejs_compat"]

[[hyperdrive]]
binding = "HYPERDRIVE"
id = "<your-hyperdrive-id>"
```

## Critical Pitfalls

1. **Hyperdrive must connect to Supabase Direct Connection** (port 5432), NOT the Pooler (port 6543). Hyperdrive IS a connection pooler — connecting pooler-to-pooler causes errors.

2. **SSL must be disabled for Hyperdrive connections** — Worker ↔ Hyperdrive is internal network. Only enable SSL for direct database connections (local dev, build stage).

3. **Cannot initialize DB at module top level** — `getCloudflareContext()` only works during request handling, not at module load time.

4. **Supabase Free Tier direct connection is IPv6 only** — local dev may fail if your network doesn't support IPv6. Use the Pooler URL (port 6543) for local development.

## Detailed References

- **Hyperdrive setup & Supabase config**: Read [references/hyperdrive-setup.md](references/hyperdrive-setup.md)
- **Environment variable patterns**: Read [references/env-patterns.md](references/env-patterns.md)
