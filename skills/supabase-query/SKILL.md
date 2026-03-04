---
name: supabase
description: Query Supabase projects - count users, list signups, check stats. Use for database queries and user analytics.
user-invocable: true
disable-model-invocation: true
triggers:
  - supabase
  - database
  - how many users
  - new signups
  - user count
metadata:
  clawdbot:
    emoji: "⚡"
    primaryEnv: SUPABASE_SERVICE_KEY
    requires:
      bins: [python3]
      env: [SUPABASE_URL, SUPABASE_SERVICE_KEY]
---

# Supabase ⚡

Query your Supabase projects directly from chat.

## Setup

### 1. Get your credentials

Go to **Supabase Dashboard → Project Settings → API**

You'll see two tabs:
- **"Publishable and secret API keys"** - New format (limited functionality)
- **"Legacy anon, service_role API keys"** - JWT format (full functionality)

**⚠️ Use the Legacy JWT key for full access!**

The `service_role` JWT key (starts with `eyJ...`) gives full admin access including:
- Listing users with details
- Counting signups
- Accessing auth.users

The new `sb_secret_...` keys have limited functionality and can't access the Admin API.

### 2. Find your keys

1. Go to: **Project Settings → API**
2. Click the **"Legacy anon, service_role API keys"** tab
3. Find `service_role` (marked with red "secret" badge)
4. Click **Reveal** and copy the `eyJ...` token

Direct link: `https://supabase.com/dashboard/project/YOUR_PROJECT_REF/settings/api`

### 3. Configure

**Option A: Interactive setup**
```bash
python3 {baseDir}/scripts/supabase.py auth
```

**Option B: Manual config**
Create `~/.supabase_config.json`:
```json
{
  "url": "https://xxxxx.supabase.co",
  "service_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Option C: Environment variables**
```bash
export SUPABASE_URL="https://xxxxx.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbG..."
```

## Commands

### User Analytics
```bash
# Count total users
python3 {baseDir}/scripts/supabase.py users

# Count new users (24h)
python3 {baseDir}/scripts/supabase.py users-today

# Count new users (7 days)  
python3 {baseDir}/scripts/supabase.py users-week

# List users with details (name, email, provider, signup date)
python3 {baseDir}/scripts/supabase.py list-users

# List new users from last 24h
python3 {baseDir}/scripts/supabase.py list-users-today

# Limit results
python3 {baseDir}/scripts/supabase.py list-users --limit 5
```

### Project Info
```bash
# Show project info and key type
python3 {baseDir}/scripts/supabase.py info

# List tables exposed via REST API
python3 {baseDir}/scripts/supabase.py tables
```

### JSON Output
```bash
python3 {baseDir}/scripts/supabase.py list-users --json
```

## Key Types Explained

| Key Type | Format | User Listing | User Count | REST Tables |
|----------|--------|--------------|------------|-------------|
| JWT service_role | `eyJ...` | ✅ Yes | ✅ Yes | ✅ Yes |
| New secret | `sb_secret_...` | ❌ No | ❌ No | ✅ Yes |

**Recommendation:** Always use the JWT `service_role` key for Clawdbot integration.

## Daily Reports

Set up automated daily user reports via Clawdbot cron.

### Example: Daily 5 PM Report

Ask Clawdbot:
```
Send me a report of how many new users signed up at 5 PM every day, 
show the last 5 signups with their names
```

This creates a cron job like:
```json
{
  "name": "Daily Supabase User Report",
  "schedule": {
    "kind": "cron",
    "expr": "0 17 * * *",
    "tz": "America/Los_Angeles"
  },
  "payload": {
    "message": "Supabase daily report: Count new user signups in the last 24 hours, and list the 5 most recent signups with their name and email."
  }
}
```

### Sample Report Output

```
📊 Supabase Daily Report

New signups (last 24h): 2

Last 5 signups:
• Jane Smith <jane@example.com> (google) - 2026-01-25
• Alex Johnson <alex.j@company.com> (google) - 2026-01-25
• Sam Wilson <sam@startup.io> (email) - 2026-01-24
• Chris Lee <chris.lee@email.com> (google) - 2026-01-23
• Jordan Taylor <jordan@acme.co> (github) - 2026-01-22
```

## GraphQL API (pg_graphql)

⚠️ **pg_graphql is disabled by default** on new Supabase projects (as of late 2025).

If you need the GraphQL API:

### Enable pg_graphql
```sql
-- Run in SQL Editor
create extension if not exists pg_graphql;
```

### Endpoint
```
https://<PROJECT_REF>.supabase.co/graphql/v1
```

### Example Query
```bash
curl -X POST https://<PROJECT_REF>.supabase.co/graphql/v1 \
  -H 'apiKey: <API_KEY>' \
  -H 'Content-Type: application/json' \
  --data-raw '{"query": "{ accountCollection(first: 1) { edges { node { id } } } }"}'
```

Note: GraphQL automatically reflects your database schema. Tables/views in `public` schema become queryable. See [Supabase GraphQL docs](https://supabase.com/docs/guides/graphql) for configuration.

## Troubleshooting

### "list-users requires a JWT service_role key"
You're using an `sb_secret_...` key. Get the JWT key from:
**Project Settings → API → Legacy tab → service_role → Reveal**

### "No API key found in request"  
The new `sb_secret_` keys don't work with all endpoints. Switch to the JWT key.

### Keys not showing
Make sure you're on the **"Legacy anon, service_role API keys"** tab, not the new API keys tab.

## Security & Permissions

The `service_role` key has **full admin access** to your database. This skill requires it for the Auth Admin API (listing/counting users).

**What this skill does:**
- Makes GET requests to your Supabase project's Auth Admin API
- Reads user metadata (email, name, provider, signup date)
- All requests stay between your machine and your Supabase instance

**What this skill does NOT do:**
- Does not write, modify, or delete any data
- Does not send credentials to any third party
- Does not access any endpoints outside your Supabase project
- Cannot be invoked autonomously by the agent (`disable-model-invocation: true`)

**Least-privilege alternative:** Create a read-only Postgres role scoped to `auth.users` and use the Supabase SQL API instead of the Admin API.

**Key safety:**
- Never commit keys to git
- Don't expose in client-side code
- Only use on trusted machines
- Config file is automatically set to mode 600 (owner read/write only)
- Review `scripts/supabase.py` before first use
