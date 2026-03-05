# codehooks-openclaw-skill

Give your OpenClaw agent a serverless backend for REST APIs, webhooks, data storage, scheduled jobs, queue workers, and autonomous workflows.

## Why this exists

OpenClaw agents run locally. That's great for privacy, but tricky when you need:

- REST APIs with automatic OpenAPI documentation
- Webhook endpoints that work when your Mac is asleep
- Persistent storage beyond local files
- Scheduled jobs that run 24/7
- Reliable integrations with Stripe, Shopify, GitHub
- Multi-step workflows that run autonomously with retries and state management

This skill gives your agent everything it needs to deploy and manage serverless backends.

## Quick start

**Human does once:**
```bash
npm install -g codehooks
coho login
coho create my-backend
coho add-admintoken
```

Give the admin token to your agent.

**Agent uses:**
```bash
export CODEHOOKS_ADMIN_TOKEN="your-token-here"
coho deploy --admintoken $CODEHOOKS_ADMIN_TOKEN
```

Your agent now has a live webhook URL, database, and job runner. Codehooks has a free tier to get started, and paid plans have no extra charges for traffic or API calls.

## Give your agent the full context

Run this to get the complete development prompt:

```bash
coho prompt
```

This outputs everything your agent needs to build with codehooks-js — routes, database operations, queues, jobs, workflows. Feed it into your agent's context.

**macOS shortcut:**
```bash
coho prompt | pbcopy
```

## What's included

- **SKILL.md** — The skill file for OpenClaw
- **examples/** — Ready-to-use code templates
  - `webhook-handler.js` — Webhook with signature verification
  - `daily-job.js` — Scheduled task example
  - `queue-worker.js` — Async queue processing
  - `workflow-automation.js` — Multi-step autonomous workflows

## Commands reference

All commands accept `--admintoken $CODEHOOKS_ADMIN_TOKEN` for non-interactive use. [Full CLI reference](https://codehooks.io/docs/cli)

| Command | Description |
|---------|-------------|
| `coho prompt` | Get full development context |
| `coho deploy` | Deploy code (5 seconds) |
| `coho info --examples` | Get endpoint URL with example API calls |
| `coho log -f` | Stream logs |
| `coho query -c <collection> -q 'field=value'` | Query database |
| `coho import -c <collection> --file data.json` | Import data |
| `coho export -c <collection>` | Export data |

## Example: Stripe webhook handler

```javascript
import { app, Datastore } from 'codehooks-js';
import { verify } from 'webhook-verify';

// Allow webhook endpoint without JWT authentication
app.auth('/stripe-webhook', (req, res, next) => next());

app.post('/stripe-webhook', async (req, res) => {
  // Verify signature using rawBody (essential for HMAC validation)
  const isValid = verify('stripe', req.rawBody, req.headers, process.env.STRIPE_WEBHOOK_SECRET);
  if (!isValid) {
    return res.status(401).send('Invalid signature');
  }

  const conn = await Datastore.open();
  await conn.insertOne('payments', {
    event: req.body,
    receivedAt: new Date().toISOString()
  });
  res.json({ received: true });
});

export default app.init();
```

## Workflows for autonomous agents

Workflows let your agent kick off multi-step processes that run independently:

```javascript
// Agent starts a workflow
const { workflowId } = await fetch('/workflow/start', {
  method: 'POST',
  body: JSON.stringify({
    data: taskData,
    callbackUrl: 'https://my-agent/webhook' // Get notified on completion
  })
}).then(r => r.json());

// Workflow runs autonomously with retries, state persistence, and error handling
// Agent gets notified via callback when done
```

See `examples/workflow-automation.js` for a complete example.

## Resources

- [How to Give Your OpenClaw Agent a Backend](https://codehooks.io/blog/openclaw-backend) — Blog post walkthrough
- [Codehooks Documentation](https://codehooks.io/docs)
- [OpenAPI/Swagger Docs](https://codehooks.io/docs/openapi-swagger-docs)
- [AI development prompt](https://codehooks.io/docs/chatgpt-backend-api-prompt)
- [webhook-verify](https://www.npmjs.com/package/webhook-verify) — Signature verification for Stripe, GitHub, Shopify, etc.
- [More templates](https://github.com/RestDB/codehooks-io-templates)
- [MCP Server](https://github.com/RestDB/codehooks-mcp-server)

## License

MIT

---

**Your agent writes the code. Codehooks runs it.**
