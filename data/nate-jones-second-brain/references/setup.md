# First-Time Setup

Get the two primitives running: Supabase (your database) and OpenRouter (your AI gateway).

## 1. Supabase

### Create a project

1. Go to **supabase.com** and sign up (GitHub login is fastest)
2. Click **New Project** in the dashboard
3. Pick your organization (default is fine)
4. Set a project name (e.g. `second-brain`)
5. Generate a strong **database password** — save it somewhere safe
6. Pick the **region** closest to you
7. Click **Create new project** — wait 1-2 minutes

### Save your credentials

You need two values. Find them at **Settings > API** in the Supabase dashboard:

| Credential | Where to find it |
|------------|-----------------|
| **Project URL** | Listed at the top as "URL" |
| **Service role key** | Under "Project API keys" — click reveal |

These become your `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` env vars.

> Treat the service role key like a password. Anyone with it has full access to your data.

### Enable pgvector

In the Supabase dashboard: **Database > Extensions** > search for "vector" > flip **pgvector ON**.

### Create the schema

Open **SQL Editor > New query** and run the SQL blocks from `{baseDir}/references/schema.md`. Run them in order — eight sections:

1. Shared `update_updated_at()` trigger function
2. The `thoughts` table (Inbox Log) with indexes and trigger
3. The `people` table with indexes and trigger
4. The `projects` table with indexes and trigger
5. The `ideas` table with indexes and trigger
6. The `admin` table with indexes and trigger
7. All semantic search functions (`match_thoughts`, `match_people`, `match_projects`, `match_ideas`, `match_admin`, `search_all`)
8. Row Level Security policies for all five tables

### Verify

- **Table Editor** should show five tables: `thoughts`, `people`, `projects`, `ideas`, `admin`
- **Database > Functions** should show: `match_thoughts`, `match_people`, `match_projects`, `match_ideas`, `match_admin`, `search_all`, `update_updated_at`

## 2. OpenRouter

### Create an account

1. Go to **openrouter.ai** and sign up
2. Go to **openrouter.ai/keys**
3. Click **Create Key**, name it `second-brain`
4. Copy the key immediately — this is your `OPENROUTER_API_KEY`
5. Add **$5 in credits** under Credits (lasts months at this usage level)

### Verify

Test that your key works:

```bash
curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "test"}'
```

You should get back a JSON response with `data[0].embedding` containing a 1536-element array.

## 3. Configure env vars

Set these three environment variables wherever your agent runs:

```
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENROUTER_API_KEY=your-openrouter-key
```

For OpenClaw, add them to `openclaw.json` under `skills.entries.nate-jones-second-brain.env`.

## 4. Security Notes

**Why service_role key?** Supabase has two keys: `anon` (public) and `service_role` (full access). We use `service_role` because this is a single-user personal knowledge base — your agent is the trusted server-side component. The RLS policy locks the table to service_role access only, which is the most restrictive option. Using the anon key would require opening access, which is less secure.

**Data handling:** Captured text is sent to OpenRouter for embedding and classification. Be mindful of what you capture — anything you store goes through OpenRouter's API.

**Key security:** Never commit keys to public repos. In OpenClaw, store them in `openclaw.json` under `skills.entries.nate-jones-second-brain.env`. Rotate keys periodically.

## 5. Test the full pipeline

Insert a test thought:

```bash
# 1. Get an embedding
EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "This is a test thought"}' \
  | jq -c '.data[0].embedding')

# 2. Insert into Supabase
curl -s -X POST "$SUPABASE_URL/rest/v1/thoughts" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "[{\"content\": \"This is a test thought\", \"embedding\": $EMBEDDING, \"metadata\": {\"type\": \"observation\", \"topics\": [\"test\"], \"source\": \"setup\"}}]"
```

Check your Supabase **Table Editor > thoughts** — you should see one row.

---

Built by Limited Edition Jonathan • natebjones.com
