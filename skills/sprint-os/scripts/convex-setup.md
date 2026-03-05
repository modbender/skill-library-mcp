# Convex Backend Setup for Sprint OS

Sprint OS can log every sprint to a Convex backend for persistent tracking across sessions. This is **optional** — the skill works fine with local file logging only.

## What You Get

- Sprint history across multiple sessions and agents
- Workstream breakdown reports (where is your time going?)
- Metric trend tracking (is the needle moving?)
- Content deduplication (avoid creating the same post twice)

## Prerequisites

- [Convex account](https://convex.dev) (free tier works)
- Node.js v18+
- `npm install convex`

## Setup Steps

### 1. Create a new Convex project

```bash
npx convex dev --new
# Follow prompts, name it something like "sprint-os"
# Note the deployment URL shown at the end (e.g., https://your-deployment.convex.site)
```

### 2. Create the schema

Create `convex/schema.ts`:

```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  sprints: defineTable({
    sprintId: v.number(),
    project: v.string(),
    workstream: v.string(),
    task: v.string(),
    artifact: v.optional(v.string()),
    metric: v.optional(v.string()),
    status: v.string(), // "completed" | "partial" | "blocked"
    owner: v.optional(v.string()),
    timestamp: v.number(),
  }).index("by_project", ["project"]),

  metrics: defineTable({
    metric: v.string(),
    value: v.number(),
    unit: v.optional(v.string()),
    project: v.optional(v.string()),
    timestamp: v.number(),
  }).index("by_metric", ["metric"]),

  contentLog: defineTable({
    project: v.string(),
    platform: v.optional(v.string()),
    content: v.string(),
    type: v.optional(v.string()),
    timestamp: v.number(),
  }).index("by_project", ["project"]),
});
```

### 3. Create the HTTP routes

Create `convex/http.ts`:

```typescript
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { api } from "./_generated/api";

const http = httpRouter();

// Log a sprint
http.route({
  path: "/sprints/log",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();
    await ctx.runMutation(api.sprints.log, body);
    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }),
});

// Get recent sprints
http.route({
  path: "/sprints/recent",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    const project = url.searchParams.get("project") ?? "";
    const limit = parseInt(url.searchParams.get("limit") ?? "10");
    const results = await ctx.runQuery(api.sprints.recent, { project, limit });
    return new Response(JSON.stringify(results), {
      headers: { "Content-Type": "application/json" },
    });
  }),
});

// Record a metric
http.route({
  path: "/metrics/record",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json();
    await ctx.runMutation(api.metrics.record, body);
    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" },
    });
  }),
});

// Content dedup search
http.route({
  path: "/content/search",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const url = new URL(request.url);
    const query = url.searchParams.get("query") ?? "";
    const results = await ctx.runQuery(api.content.search, { query });
    return new Response(JSON.stringify(results), {
      headers: { "Content-Type": "application/json" },
    });
  }),
});

export default http;
```

### 4. Deploy

```bash
npx convex deploy
```

Note the `Deployment URL` shown — this is your `CONVEX_SPRINT_URL`.

### 5. Configure Sprint OS

Add to your `.env` file:

```
CONVEX_SPRINT_URL=https://your-deployment.convex.site
```

Sprint OS will automatically start logging to Convex on every step 7.

## Cost

Convex free tier includes 1M function calls/month and 1GB storage. Sprint OS uses roughly 1–5 calls per sprint. Even at 100 sprints/day, you'll stay well within the free tier.
