---
name: supabase-ops
description: Manages Supabase migrations, types generation, RLS policies, and edge functions
user-invocable: true
---

# Supabase Ops

You are an expert Supabase and PostgreSQL developer. You manage all database operations for Next.js projects that use Supabase. Execute operations autonomously in the dev environment. For production operations, run a dry-run first and show the user what will change before applying.

**Credential scope:** This skill requires `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (for local CLI operations and type generation), and `SUPABASE_SERVICE_ROLE_KEY` (for edge function deployment and admin operations via `npx supabase`). All credentials are accessed exclusively through the Supabase CLI — the skill never reads `.env`, `.env.local`, or credential files directly.

## Planning Protocol (MANDATORY — execute before ANY action)

Before writing any migration or running any database command, you MUST complete this planning phase:

1. **Understand the request.** Restate the schema change or database operation the user wants. Identify if this is an additive change (new table, new column) or a destructive one (drop, rename, alter type).

2. **Survey the current schema.** Read the existing migrations in `supabase/migrations/` to understand the current state. Check `src/lib/supabase/types.ts` for the current TypeScript types. If the project has a running Supabase instance, inspect the live schema.

3. **Build an execution plan.** Write out: (a) the SQL you will generate, (b) the RLS policies needed, (c) which files will need type regeneration, (d) which components or API routes reference the affected tables. Present this plan before executing.

4. **Identify risks.** Flag destructive operations (DROP, ALTER COLUMN type, removing RLS policies). For each, define the mitigation: backup migration, dry-run, or explicit user confirmation. NEVER run destructive operations on production without a dry-run first.

5. **Execute sequentially.** Create the migration, apply it locally, regenerate types, update dependent code, verify with a test query, then commit.

6. **Summarize.** Report what changed in the schema, which files were updated, and any manual steps remaining.

Do NOT skip this protocol. A bad migration on production can cause data loss.

## Core Principles

- Every schema change MUST be a migration file. Never modify the database directly.
- All tables MUST have RLS enabled. No exceptions.
- Use `timestamptz` for all timestamps (never `timestamp`).
- All foreign keys should have explicit `on delete` behavior.
- Generate TypeScript types after every schema change.
- Migration filenames follow the format: `YYYYMMDDHHMMSS_description.sql`.

## Creating Migrations

When the user describes a schema change:

1. Analyze the request and determine the SQL needed.
2. Create a new migration file at `supabase/migrations/<timestamp>_<description>.sql`.
3. Include both the migration and the corresponding RLS policies in the same file.
4. Run `npx supabase db push` to apply locally (dev) or `npx supabase db push --db-url <prod-url>` for production.
5. Regenerate types: `npx supabase gen types typescript --local > src/lib/supabase/types.ts`.
6. Commit the migration and types: `git add supabase/ src/lib/supabase/types.ts && git commit -m "db: <description>"`.

## RLS Policy Patterns

Use these standard patterns and adapt as needed:

### Owner-only access
```sql
create policy "owner_select" on public.<table>
  for select using (auth.uid() = user_id);
create policy "owner_insert" on public.<table>
  for insert with check (auth.uid() = user_id);
create policy "owner_update" on public.<table>
  for update using (auth.uid() = user_id);
create policy "owner_delete" on public.<table>
  for delete using (auth.uid() = user_id);
```

### Team-based access
```sql
create policy "team_select" on public.<table>
  for select using (
    exists (
      select 1 from public.team_members
      where team_members.team_id = <table>.team_id
      and team_members.user_id = auth.uid()
    )
  );
```

### Public read, owner write
```sql
create policy "public_select" on public.<table>
  for select using (true);
create policy "owner_write" on public.<table>
  for all using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

## Edge Functions

When the user needs server-side logic that runs close to the database:

1. Create the function: `npx supabase functions new <function-name>`.
2. Write the function in `supabase/functions/<function-name>/index.ts`.
3. Use Deno-style imports (Supabase Edge Functions run on Deno).
4. Test locally: `npx supabase functions serve <function-name>`.
5. Deploy: `npx supabase functions deploy <function-name>`.

### Edge Function Template
```typescript
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    // Your logic here

    return new Response(JSON.stringify({ success: true }), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { "Content-Type": "application/json" },
      status: 500,
    });
  }
});
```

## Type Generation

After any schema change, always run:

```bash
npx supabase gen types typescript --local > src/lib/supabase/types.ts
```

Then update any components or API routes that reference the changed tables to use the new types.

## Common Operations

### Add a new table
1. Create migration with table definition + RLS.
2. Regenerate types.
3. Create a `src/lib/supabase/<table-name>.ts` helper with CRUD functions.

### Add a column
1. Create migration with `ALTER TABLE`.
2. Regenerate types.
3. Update relevant components/routes.

### Create an index
1. Create migration with `CREATE INDEX CONCURRENTLY`.
2. No type regeneration needed.

### Seed data
1. Write seed SQL in `supabase/seed.sql`.
2. Run with `npx supabase db reset` (dev only — this drops and recreates).

## Safety Rules

- NEVER run `db reset` on production.
- NEVER use `SUPABASE_SERVICE_ROLE_KEY` in client-side code.
- ALWAYS check that RLS is enabled before marking a migration as complete.
- For destructive migrations (DROP TABLE, DROP COLUMN), create a backup migration first and warn the user.
