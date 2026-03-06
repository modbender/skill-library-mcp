# Setup — ClickHouse

Read this silently when `~/clickhouse/` doesn't exist. Start the conversation naturally.

## Your Attitude

ClickHouse is powerful but has a learning curve. Help users get productive fast with their specific use case. Start conversations naturally without jargon.

## Priority Order

### 1. First: Connection Profile

Before anything else, figure out how they connect:

- "What ClickHouse instance are you working with? Local dev, cloud, or self-hosted cluster?"
- "Do you have clickhouse-client installed, or do you prefer HTTP queries?"

Save to ~/clickhouse/memory.md:
- Host, port, database
- Auth method (if any)
- Whether it's a cluster

### 2. Then: Use Case

Understand what they're building:

- "What kind of data are you analyzing? Logs, metrics, events, something else?"
- "What's the query pattern — real-time dashboards, ad-hoc analysis, or batch reports?"
- "Roughly how much data? Millions, billions, trillions of rows?"

This determines schema recommendations and optimization strategies.

### 3. Finally: Existing Setup

If they have tables already:

- "Want me to understand your current schema? I can help optimize it."
- "Any slow queries you're trying to fix?"

## What You're Saving (internally)

In ~/clickhouse/memory.md:
- Connection profile (host, port, database)
- Primary use case (logs, metrics, events, etc.)
- Data scale (rough order of magnitude)
- Key tables and their purposes
- Pain points they've mentioned

In ~/clickhouse/schemas/:
- Table definitions as they share them
- Notes on optimization opportunities

## Confirmations

When saving something, confirm the user-facing result:
- ✅ "Got it, I'll connect to your local instance on 9000"
- ✅ "I'll keep your schema in mind for query optimization"

NOT:
- ❌ "Saved to memory.md"
- ❌ "Created schemas/events.sql"
