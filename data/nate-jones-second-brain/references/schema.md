# Database Schema

Run these SQL blocks in the Supabase **SQL Editor**. Each block can be run as a separate query.

> **Prerequisite:** Enable the pgvector extension first (Database > Extensions > pgvector ON).

## 1. Shared trigger function

This trigger auto-updates the `updated_at` timestamp on every row edit. All tables use it.

```sql
create or replace function update_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;
```

## 2. The thoughts table (Inbox Log)

Everything lands here first. This is the audit trail — the Receipt. Every captured thought is logged with its embedding, classification metadata, confidence score, and where it was routed.

```sql
create table thoughts (
  id uuid default gen_random_uuid() primary key,
  content text not null,
  embedding vector(1536),
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index on thoughts using hnsw (embedding vector_cosine_ops);
create index on thoughts using gin (metadata);
create index on thoughts (created_at desc);

create trigger thoughts_updated_at
  before update on thoughts
  for each row
  execute function update_updated_at();
```

### Metadata schema

The `metadata` JSONB column stores:

| Field | Type | Values |
|-------|------|--------|
| `type` | string | `observation`, `task`, `idea`, `reference`, `person_note` |
| `topics` | string[] | 1-3 short topic tags (always at least one) |
| `people` | string[] | People mentioned (empty if none) |
| `action_items` | string[] | Implied to-dos (empty if none) |
| `dates_mentioned` | string[] | Dates in YYYY-MM-DD format (empty if none) |
| `source` | string | Where it came from: `slack`, `signal`, `cli`, `manual`, etc. |
| `confidence` | float | LLM classification confidence (0-1). The Bouncer uses this. |
| `routed_to` | string | Which table the thought was filed into (`people`, `projects`, `ideas`, `admin`, or null if unrouted) |
| `routed_id` | string | UUID of the record in the destination table (null if unrouted) |

## 3. The people table

Relationship tracking. Each person gets one row that accumulates context over time. When the user mentions someone new, create a row. When they mention someone again, update the existing row with new context.

```sql
create table people (
  id uuid default gen_random_uuid() primary key,
  name text not null unique,
  context text default '',
  follow_ups jsonb default '[]'::jsonb,
  tags text[] default '{}',
  embedding vector(1536),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index on people using hnsw (embedding vector_cosine_ops);
create index on people (name);
create index on people (created_at desc);

create trigger people_updated_at
  before update on people
  for each row
  execute function update_updated_at();
```

### Column reference

| Column | Type | Notes |
|--------|------|-------|
| `name` | TEXT (unique) | Person's name. Used for upsert matching. |
| `context` | TEXT | How you know them, what they do, accumulated notes. Append new info over time. |
| `follow_ups` | JSONB array | Things to remember for next conversation. `[{"item": "Ask about college apps", "added": "2026-02-10"}]` |
| `tags` | TEXT[] | Freeform tags: `{"colleague", "investor", "friend"}` |
| `embedding` | VECTOR(1536) | Embedding of name + context for semantic search. Re-embed when context changes significantly. |

## 4. The projects table

Active work tracking. Each project has a status and a concrete next action — not a vague intention, but something executable.

```sql
create table projects (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  status text default 'active' check (status in ('active', 'waiting', 'blocked', 'someday', 'done')),
  next_action text default '',
  notes text default '',
  tags text[] default '{}',
  embedding vector(1536),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index on projects using hnsw (embedding vector_cosine_ops);
create index on projects (status);
create index on projects (created_at desc);

create trigger projects_updated_at
  before update on projects
  for each row
  execute function update_updated_at();
```

### Column reference

| Column | Type | Notes |
|--------|------|-------|
| `name` | TEXT | Project name |
| `status` | TEXT | One of: `active`, `waiting`, `blocked`, `someday`, `done` |
| `next_action` | TEXT | The concrete next step. "Email Sarah" not "work on website." |
| `notes` | TEXT | Accumulated project notes |
| `tags` | TEXT[] | Freeform tags |
| `embedding` | VECTOR(1536) | Embedding of name + notes for semantic search |

## 5. The ideas table

Captured insights, angles, concepts worth developing. Lightweight — a title, a summary, and optional elaboration.

```sql
create table ideas (
  id uuid default gen_random_uuid() primary key,
  title text not null,
  summary text default '',
  elaboration text default '',
  topics text[] default '{}',
  embedding vector(1536),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index on ideas using hnsw (embedding vector_cosine_ops);
create index on ideas using gin (topics);
create index on ideas (created_at desc);

create trigger ideas_updated_at
  before update on ideas
  for each row
  execute function update_updated_at();
```

### Column reference

| Column | Type | Notes |
|--------|------|-------|
| `title` | TEXT | Short name for the idea |
| `summary` | TEXT | One-liner that captures the core insight |
| `elaboration` | TEXT | Deeper notes, connections, implications |
| `topics` | TEXT[] | Topic tags: `{"ai", "productivity"}` |
| `embedding` | VECTOR(1536) | Embedding of title + summary for semantic search |

## 6. The admin table

Tasks with due dates. Things that need to get done — errands, emails, calls, deadlines.

```sql
create table admin (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  due_date date,
  status text default 'pending' check (status in ('pending', 'in_progress', 'done')),
  notes text default '',
  embedding vector(1536),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index on admin using hnsw (embedding vector_cosine_ops);
create index on admin (status);
create index on admin (due_date);
create index on admin (created_at desc);

create trigger admin_updated_at
  before update on admin
  for each row
  execute function update_updated_at();
```

### Column reference

| Column | Type | Notes |
|--------|------|-------|
| `name` | TEXT | What needs to be done |
| `due_date` | DATE | When it's due (null if no deadline) |
| `status` | TEXT | One of: `pending`, `in_progress`, `done` |
| `notes` | TEXT | Additional context |
| `embedding` | VECTOR(1536) | Embedding of name + notes for semantic search |

## 7. Semantic search functions

### match_thoughts (Inbox Log search)

```sql
create or replace function match_thoughts(
  query_embedding vector(1536),
  match_threshold float default 0.7,
  match_count int default 10,
  filter jsonb default '{}'::jsonb
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  select
    t.id,
    t.content,
    t.metadata,
    1 - (t.embedding <=> query_embedding) as similarity,
    t.created_at
  from thoughts t
  where 1 - (t.embedding <=> query_embedding) > match_threshold
    and (filter = '{}'::jsonb or t.metadata @> filter)
  order by t.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

### match_people

```sql
create or replace function match_people(
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 10
)
returns table (
  id uuid,
  name text,
  context text,
  follow_ups jsonb,
  tags text[],
  similarity float,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  select
    p.id, p.name, p.context, p.follow_ups, p.tags,
    1 - (p.embedding <=> query_embedding) as similarity,
    p.created_at
  from people p
  where p.embedding is not null
    and 1 - (p.embedding <=> query_embedding) > match_threshold
  order by p.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

### match_projects

```sql
create or replace function match_projects(
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 10
)
returns table (
  id uuid,
  name text,
  status text,
  next_action text,
  notes text,
  tags text[],
  similarity float,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  select
    pr.id, pr.name, pr.status, pr.next_action, pr.notes, pr.tags,
    1 - (pr.embedding <=> query_embedding) as similarity,
    pr.created_at
  from projects pr
  where pr.embedding is not null
    and 1 - (pr.embedding <=> query_embedding) > match_threshold
  order by pr.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

### match_ideas

```sql
create or replace function match_ideas(
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 10
)
returns table (
  id uuid,
  title text,
  summary text,
  elaboration text,
  topics text[],
  similarity float,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  select
    i.id, i.title, i.summary, i.elaboration, i.topics,
    1 - (i.embedding <=> query_embedding) as similarity,
    i.created_at
  from ideas i
  where i.embedding is not null
    and 1 - (i.embedding <=> query_embedding) > match_threshold
  order by i.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

### match_admin

```sql
create or replace function match_admin(
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 10
)
returns table (
  id uuid,
  name text,
  due_date date,
  status text,
  notes text,
  similarity float,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  select
    a.id, a.name, a.due_date, a.status, a.notes,
    1 - (a.embedding <=> query_embedding) as similarity,
    a.created_at
  from admin a
  where a.embedding is not null
    and 1 - (a.embedding <=> query_embedding) > match_threshold
  order by a.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

### search_all (cross-table search)

Search across all five tables at once. Returns unified results with a `table_name` column.

```sql
create or replace function search_all(
  query_embedding vector(1536),
  match_threshold float default 0.5,
  match_count int default 20
)
returns table (
  table_name text,
  record_id uuid,
  label text,
  detail text,
  similarity float,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  (
    select 'thoughts'::text, t.id, t.metadata->>'type', t.content,
      1 - (t.embedding <=> query_embedding), t.created_at
    from thoughts t
    where t.embedding is not null
      and 1 - (t.embedding <=> query_embedding) > match_threshold
  )
  union all
  (
    select 'people'::text, p.id, p.name, p.context,
      1 - (p.embedding <=> query_embedding), p.created_at
    from people p
    where p.embedding is not null
      and 1 - (p.embedding <=> query_embedding) > match_threshold
  )
  union all
  (
    select 'projects'::text, pr.id, pr.name, pr.notes,
      1 - (pr.embedding <=> query_embedding), pr.created_at
    from projects pr
    where pr.embedding is not null
      and 1 - (pr.embedding <=> query_embedding) > match_threshold
  )
  union all
  (
    select 'ideas'::text, i.id, i.title, i.summary,
      1 - (i.embedding <=> query_embedding), i.created_at
    from ideas i
    where i.embedding is not null
      and 1 - (i.embedding <=> query_embedding) > match_threshold
  )
  union all
  (
    select 'admin'::text, a.id, a.name, a.notes,
      1 - (a.embedding <=> query_embedding), a.created_at
    from admin a
    where a.embedding is not null
      and 1 - (a.embedding <=> query_embedding) > match_threshold
  )
  order by similarity desc
  limit match_count;
end;
$$;
```

## 8. Row Level Security

Lock all tables to service_role access only.

```sql
alter table thoughts enable row level security;
alter table people enable row level security;
alter table projects enable row level security;
alter table ideas enable row level security;
alter table admin enable row level security;

create policy "Service role full access" on thoughts for all using (auth.role() = 'service_role');
create policy "Service role full access" on people for all using (auth.role() = 'service_role');
create policy "Service role full access" on projects for all using (auth.role() = 'service_role');
create policy "Service role full access" on ideas for all using (auth.role() = 'service_role');
create policy "Service role full access" on admin for all using (auth.role() = 'service_role');
```

## Table Summary

| Table | Role | Semantic Search | Key Indexes |
|-------|------|-----------------|-------------|
| `thoughts` | Inbox Log / audit trail | `match_thoughts` | HNSW, GIN (metadata), B-tree (created_at) |
| `people` | Relationship tracking | `match_people` | HNSW, B-tree (name, created_at) |
| `projects` | Work tracking | `match_projects` | HNSW, B-tree (status, created_at) |
| `ideas` | Insight capture | `match_ideas` | HNSW, GIN (topics), B-tree (created_at) |
| `admin` | Task management | `match_admin` | HNSW, B-tree (status, due_date, created_at) |
| *all* | Cross-table search | `search_all` | Uses indexes above |

---

Built by Limited Edition Jonathan • natebjones.com
