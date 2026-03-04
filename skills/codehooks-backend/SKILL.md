---
name: codehooks-backend
description: Deploy serverless backends for REST APIs, webhooks, data storage, scheduled jobs, queue workers, and autonomous workflows.
metadata: { "openclaw": { "emoji": "🪝", "requires": { "bins": ["coho"], "env": ["CODEHOOKS_ADMIN_TOKEN"] } } }
---

# Codehooks Backend Skill

Give your OpenClaw agent a serverless backend for REST APIs, webhooks, data storage, scheduled jobs, queue workers, and autonomous workflows.

## Your agent can deploy code

With this skill, your agent can write JavaScript/TypeScript code and deploy it to a live serverless backend in 5 seconds. No human intervention required — the agent iterates autonomously.

Codehooks has a free tier to get started, and paid plans have no extra charges for traffic or API calls — let your agent deploy without worrying about usage costs.

⚠️ **Warning:** This gives your agent the ability to deploy and run code on a live server. Review your agent's actions, set appropriate permissions, and monitor usage. You are responsible for any code your agent deploys.

## What this skill enables

- **REST APIs** with automatic OpenAPI/Swagger documentation
- **Instant CRUD APIs** using `crudlify()` with schema validation
- **Webhook endpoints** that external services can call (Stripe, GitHub, Shopify, etc.)
- **Persistent storage** beyond local memory (NoSQL + key-value)
- **Background jobs** and scheduled tasks that run 24/7
- **Queue workers** for async processing
- **Autonomous workflows** with retries, branching, and state management

## Setup

**Human does once:**
```bash
npm install -g codehooks
coho login
coho create openclaw-backend
coho add-admintoken
```

Give the admin token to your agent.

**Agent uses:**
```bash
export CODEHOOKS_ADMIN_TOKEN="your-token-here"
coho deploy --admintoken $CODEHOOKS_ADMIN_TOKEN
```

The agent can now deploy code, query data, and manage the backend.

---

## Essential: Load the development context

Before building anything, run:

```bash
coho prompt
```

This outputs the complete Codehooks development prompt — routing, database, queues, jobs, workflows, and the full codehooks-js API. Copy it into your context to build any backend feature correctly.

**macOS shortcut:**
```bash
coho prompt | pbcopy
```

## Understand existing projects

Before modifying an existing project, get the full picture:

```bash
# Returns JSON with collections, stats, recent deploys, and error logs
coho doctor

# Describe the app structure — collections, schemas, queues, files
coho describe
```

`coho doctor` is the most powerful diagnostic command — it returns structured JSON covering database collections with document counts, deployment history, queue and worker status, and recent error logs. Always run it when joining an existing project or debugging issues.

`coho describe` complements doctor by showing the structural overview: what collections exist, their schemas, registered queues, and deployed files.

---

## Commands your agent can use

All commands accept `--admintoken $CODEHOOKS_ADMIN_TOKEN` for non-interactive use. Full CLI reference: https://codehooks.io/docs/cli

| Command | What it does |
|---------|--------------|
| `coho prompt` | Get the full development context |
| `coho doctor` | Diagnose project state — collections, stats, deploys, error logs |
| `coho describe` | Describe app structure — collections, schemas, queues, files |
| `coho deploy` | Deploy code (5 seconds to live) |
| `coho info --examples` | Get endpoint URLs with cURL examples |
| `coho log -f` | Stream logs in real-time |
| `coho query -c <collection> -q 'field=value'` | Query the database |
| `coho queue-status` | Check queue status |
| `coho workflow-status` | Check workflow status |
| `coho import -c <collection> --file data.json` | Import data |
| `coho export -c <collection>` | Export data |

---

## Code examples

### Instant CRUD API with validation

```javascript
import { app } from 'codehooks-js';
import * as Yup from 'yup';

const productSchema = Yup.object({
  name: Yup.string().required(),
  price: Yup.number().positive().required(),
  category: Yup.string().required()
});

// Creates GET, POST, PUT, DELETE endpoints automatically
// OpenAPI docs available at /.well-known/openapi
app.crudlify({ product: productSchema });

export default app.init();
```

### Webhook that stores incoming data

```javascript
import { app, Datastore } from 'codehooks-js';

// Allow webhook endpoint without JWT authentication
app.auth('/webhook', (req, res, next) => {
  next();
});

app.post('/webhook', async (req, res) => {
  const conn = await Datastore.open();
  await conn.insertOne('events', {
    ...req.body,
    receivedAt: new Date().toISOString()
  });
  res.json({ ok: true });
});

export default app.init();
```

### Scheduled job (runs daily at 9am)

```javascript
import { app, Datastore } from 'codehooks-js';

app.job('0 9 * * *', async (_, { jobId }) => {
  console.log(`Running job: ${jobId}`);
  const conn = await Datastore.open();
  const events = await conn.getMany('events', {}).toArray();
  console.log('Daily summary:', events.length, 'events');
});

export default app.init();
```

### Queue worker for async processing

```javascript
import { app, Datastore } from 'codehooks-js';

app.worker('processTask', async (req, res) => {
  const { task } = req.body.payload;
  const conn = await Datastore.open();
  await conn.updateOne('tasks', { _id: task.id }, { $set: { status: 'completed' } });
  res.end();
});

export default app.init();
```

### Autonomous workflow (multi-step with retries)

```javascript
import { app } from 'codehooks-js';

const workflow = app.createWorkflow('myTask', 'Process tasks autonomously', {
  begin: async function (state, goto) {
    console.log('Starting task:', state.taskId);
    goto('process', state);
  },
  process: async function (state, goto) {
    // Do work here - workflow handles retries and state
    state = { ...state, result: 'processed' };
    goto('complete', state);
  },
  complete: function (state, goto) {
    console.log('Done:', state.result);
    goto(null, state); // End workflow
  }
});

// Agent starts workflow via API
app.post('/start', async (req, res) => {
  const result = await workflow.start(req.body);
  res.json(result);
});

export default app.init();
```

---

## Important patterns

- **`getMany()` returns a stream** — use `.toArray()` when you need to manipulate data (sort, filter, map)
- **Webhook signatures:** Use `req.rawBody` for signature verification, not `req.body`
- **No filesystem access:** `fs`, `path`, `os` are not available — this is a serverless environment
- **Secrets:** Use `process.env.VARIABLE_NAME` for API keys and secrets
- **Static files:** `app.static({ route: '/app', directory: '/public' })` serves static sites from deployed source
- **File storage:** `app.storage({ route: '/docs', directory: '/uploads' })` serves uploaded files

---

## Development workflow: Let your agent build new endpoints

1. Agent runs `coho prompt` and loads the development context
2. For existing projects, agent runs `coho doctor` and `coho describe` to understand what's deployed
3. Agent writes code using codehooks-js patterns
4. Agent runs `coho deploy` (5 seconds to live)
5. Agent verifies with `coho log -f` or tests endpoints with `coho info --examples`
6. Agent iterates — the fast deploy loop enables rapid development

---

## When to use this skill

- You need a reliable webhook URL for Stripe, GitHub, Shopify, etc.
- You want persistent storage outside your local machine
- You need scheduled jobs that run even when your device is off
- You want to offload sensitive API integrations to a sandboxed environment
- You need queues for async processing
- You want autonomous multi-step workflows that run independently with retries

---

## Resources

- **Documentation:** https://codehooks.io/docs
- **CLI reference:** https://codehooks.io/docs/cli
- **AI prompt:** Run `coho prompt` or visit https://codehooks.io/llms.txt
- **Templates:** https://github.com/RestDB/codehooks-io-templates
- **MCP Server:** https://github.com/RestDB/codehooks-mcp-server
