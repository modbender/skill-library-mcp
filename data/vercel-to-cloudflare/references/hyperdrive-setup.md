# Hyperdrive + Supabase Setup Guide

## Create Hyperdrive

```bash
# Use Supabase DIRECT connection (port 5432), NOT Pooler (6543)
npx wrangler hyperdrive create my-hyperdrive \
  --connection-string="postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres"
```

Copy the returned Hyperdrive ID into `wrangler.toml`.

## wrangler.toml Configuration

```toml
name = "my-app"
main = ".open-next/worker.js"
compatibility_date = "2024-09-23"
compatibility_flags = ["nodejs_compat"]

[[hyperdrive]]
binding = "HYPERDRIVE"
id = "abc123..."

[vars]
# Non-sensitive env vars here
NEXT_PUBLIC_SITE_URL = "https://myapp.com"
```

## Local Development

For local dev, Hyperdrive is not available. Use Supabase Pooler URL directly:

```toml
# .dev.vars (local only, gitignored)
CLOUDFLARE_HYPERDRIVE_LOCAL_CONNECTION_STRING_HYPERDRIVE = "postgresql://postgres.[ref]:[pwd]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true"
```

## Why Direct Connection, Not Pooler?

Hyperdrive itself IS a connection pooler. Connecting a pooler (Hyperdrive) to another pooler (Supabase Transaction Pooler) causes protocol handshake failures.

- **Production**: Hyperdrive → Supabase Direct (5432) ✅
- **Local dev**: App → Supabase Pooler (6543) ✅
- **Production**: Hyperdrive → Supabase Pooler (6543) ❌ Fails

## SSL Configuration

| Environment | SSL Setting | Reason |
|------------|-------------|--------|
| Hyperdrive (production) | `false` | Internal Cloudflare network |
| Direct connection (build/migrate) | `'require'` | Public internet |
| Local dev via Pooler | `'require'` | Public internet |
