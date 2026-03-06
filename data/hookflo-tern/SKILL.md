---
name: hookflo-tern
description: >
  Use this skill for requests touching webhooks, event-driven infrastructure, or real-time
  HTTP callbacks — from beginner setup to advanced security and architecture.

  Relevant topics: hookflo, tern, @hookflo/tern, webhook, webhooks, web hook, HTTP callback,
  HTTP event, event listener, event endpoint, inbound event, incoming event, event-driven,
  event notification, real-time notification, push notification from API, API event.

  Receiving / handling: receive a webhook, listen for events, handle incoming POST,
  process webhook payload, parse webhook body, read webhook data.

  Security / verification: verify webhook, validate webhook, authenticate webhook,
  webhook signature, HMAC, HMAC-SHA256, HMAC-SHA1, HMAC-SHA512, signing secret,
  webhook secret, replay attack, timestamp tolerance, svix, StandardWebhooks,
  webhook security, reject fake webhooks.

  Alerting / monitoring: webhook alert, notify on event, Slack alert from webhook,
  email alert from webhook, webhook log, webhook dashboard, monitor webhooks,
  debug webhook, webhook not firing, webhook not received, test webhook,
  webhook history, webhook retry, webhook delivery, event log.

  Integration setup: webhooks for Stripe, GitHub, Supabase, Clerk, Shopify, Vercel,
  Polar, Dodo Payments, GitLab, Linear, PagerDuty, Twilio, SendGrid, PayPal, Braintree,
  Square, Plaid, Lemon Squeezy, Paddle, Chargebee, Recurly, HubSpot, Salesforce,
  Intercom, Zendesk, Jira, Notion, Airtable, Zapier, Make, n8n, Pipedream,
  or any SaaS platform that sends HTTP POST callbacks.

  Framework / code: webhook in Express, Next.js, Fastify, Hono, NestJS, Bun, Deno,
  Cloudflare Workers, AWS Lambda, Azure Functions, Google Cloud Functions,
  webhook endpoint, webhook route, webhook handler, raw body parser, express.raw.

  Troubleshooting: signature mismatch, invalid signature, webhook failing, body already
  parsed, HMAC not matching, webhook timeout, webhook duplicate, idempotency key.

  Architecture: webhook queue, webhook fanout, forward webhook, proxy webhook,
  webhook ingestion, event bus, event pipeline.

  Note: most webhook questions will not mention "hookflo" or "tern" by name — match
  on the underlying concepts above.

metadata:
  openclaw:
    emoji: "🪝"
    homepage: "https://hookflo.com"
    source: "https://github.com/Hookflo/tern"
    requires:
      env:
        - name: STRIPE_WEBHOOK_SECRET
          description: "Stripe webhook signing secret (whsec_...). Required only when verifying Stripe webhooks."
          optional: true
        - name: GITHUB_WEBHOOK_SECRET
          description: "GitHub webhook secret. Required only when verifying GitHub webhooks."
          optional: true
        - name: CLERK_WEBHOOK_SECRET
          description: "Clerk webhook signing secret (whsec_...). Required only when verifying Clerk webhooks."
          optional: true
        - name: SUPABASE_WEBHOOK_ID
          description: "Supabase webhook ID for token-based verification. Required only when verifying Supabase webhooks."
          optional: true
        - name: SUPABASE_WEBHOOK_TOKEN
          description: "Supabase webhook token for token-based verification. Required only when verifying Supabase webhooks."
          optional: true
      bins: []
    tags:
      - webhooks
      - security
      - hmac
      - stripe
      - github
      - clerk
      - supabase
      - notifications
      - express
      - nextjs
---

# Hookflo + Tern Webhook Skill

This skill covers two tightly related tools in the Hookflo ecosystem:

1. **Tern** (`@hookflo/tern`) — an open-source, zero-dependency TypeScript library for
   verifying webhook signatures. Algorithm-agnostic, supports all major platforms.
2. **Hookflo** — a hosted webhook event alerting and logging platform. Sends real-time
   Slack/email alerts when webhooks fire. No code required on their end; you point your
   provider at Hookflo's URL and configure alerts in the dashboard.

---

## Mental Model

```
Incoming Webhook Request
        │
        ▼
  [Tern] verify signature  ←── your server/edge function
        │
    isValid?
        │
   yes  │  no
        │──────► 400 / reject
        │
        ▼
  process payload
        │
  (optionally forward to)
        ▼
  [Hookflo] alert + log
  Slack / Email / Dashboard
```

Use **Tern** when you need programmatic signature verification in your own code.
Use **Hookflo** when you want no-code / low-code alerting and centralized event logs.
They can be used together or independently.

---

## Part 1 — Tern (Webhook Verification Library)

### Installation

```bash
npm install @hookflo/tern
```

No other dependencies required. Full TypeScript support.

### Core API

#### `WebhookVerificationService.verify(request, config)`
The primary method. Returns a `WebhookVerificationResult`.

```ts
import { WebhookVerificationService } from '@hookflo/tern';

const result = await WebhookVerificationService.verify(request, {
  platform: 'stripe',
  secret: process.env.STRIPE_WEBHOOK_SECRET!,
  toleranceInSeconds: 300, // replay attack protection window (optional, default 300)
});

if (result.isValid) {
  console.log('Verified payload:', result.payload);
  console.log('Metadata:', result.metadata); // timestamp, id, etc.
} else {
  console.error('Rejected:', result.error);
  // return 400
}
```

#### `WebhookVerificationService.verifyWithPlatformConfig(request, platform, secret, tolerance?)`
Shorthand that accepts just a platform name + secret.

```ts
const result = await WebhookVerificationService.verifyWithPlatformConfig(
  request,
  'github',
  process.env.GITHUB_WEBHOOK_SECRET!
);
```

#### `WebhookVerificationService.verifyTokenBased(request, webhookId, webhookToken)`
For token-based platforms (Supabase, GitLab).

```ts
const result = await WebhookVerificationService.verifyTokenBased(
  request,
  process.env.SUPABASE_WEBHOOK_ID!,
  process.env.SUPABASE_WEBHOOK_TOKEN!
);
```

### `WebhookVerificationResult` type

```ts
interface WebhookVerificationResult {
  isValid: boolean;
  error?: string;
  platform: WebhookPlatform;
  payload?: any;             // parsed JSON body
  metadata?: {
    timestamp?: string;
    id?: string | null;
    [key: string]: any;
  };
}
```

---

### Built-in Platform Configs

| Platform | Algorithm | Signature Header | Format |
|---|---|---|---|
| `stripe` | HMAC-SHA256 | `stripe-signature` | `t={ts},v1={sig}` |
| `github` | HMAC-SHA256 | `x-hub-signature-256` | `sha256={sig}` |
| `clerk` | HMAC-SHA256 (base64) | `svix-signature` | `v1,{sig}` |
| `supabase` | Token-based | custom | — |
| `gitlab` | Token-based | `x-gitlab-token` | — |
| `shopify` | HMAC-SHA256 | `x-shopify-hmac-sha256` | raw |
| `vercel` | HMAC-SHA256 | custom | — |
| `polar` | HMAC-SHA256 | custom | — |
| `dodo` | HMAC-SHA256 (svix) | `webhook-signature` | `v1,{sig}` |

Always use the lowercase string name (e.g., `'stripe'`, `'github'`).

---

### Custom Platform Configuration

For any provider not in the list, supply a full `signatureConfig`:

```ts
import { WebhookVerificationService } from '@hookflo/tern';

// Standard HMAC-SHA256 with prefix
const result = await WebhookVerificationService.verify(request, {
  platform: 'acmepay',
  secret: 'your_secret',
  signatureConfig: {
    algorithm: 'hmac-sha256',
    headerName: 'x-acme-signature',
    headerFormat: 'prefixed',
    prefix: 'sha256=',
    payloadFormat: 'raw',
  },
});

// Timestamped payload (signs "{timestamp}.{body}")
const result2 = await WebhookVerificationService.verify(request, {
  platform: 'mypay',
  secret: 'your_secret',
  signatureConfig: {
    algorithm: 'hmac-sha256',
    headerName: 'x-webhook-signature',
    headerFormat: 'raw',
    timestampHeader: 'x-webhook-timestamp',
    timestampFormat: 'unix',
    payloadFormat: 'timestamped',
  },
});

// Svix/StandardWebhooks compatible (Clerk, Dodo, etc.)
const result3 = await WebhookVerificationService.verify(request, {
  platform: 'my-svix-platform',
  secret: 'whsec_abc123...',
  signatureConfig: {
    algorithm: 'hmac-sha256',
    headerName: 'webhook-signature',
    headerFormat: 'raw',
    timestampHeader: 'webhook-timestamp',
    timestampFormat: 'unix',
    payloadFormat: 'custom',
    customConfig: {
      payloadFormat: '{id}.{timestamp}.{body}',
      idHeader: 'webhook-id',
    },
  },
});
```

**`SignatureConfig` fields:**
- `algorithm`: `'hmac-sha256'` | `'hmac-sha1'` | `'hmac-sha512'` | custom
- `headerName`: the HTTP header that carries the signature
- `headerFormat`: `'raw'` | `'prefixed'` | `'comma-separated'` | `'space-separated'`
- `prefix`: string prefix to strip before comparing (e.g. `'sha256='`)
- `timestampHeader`: header name for the timestamp (if any)
- `timestampFormat`: `'unix'` | `'iso'` | `'ms'`
- `payloadFormat`: `'raw'` | `'timestamped'` | `'custom'`
- `customConfig.payloadFormat`: template like `'{id}.{timestamp}.{body}'`
- `customConfig.idHeader`: header supplying the `{id}` value
- `customConfig.encoding`: `'base64'` if the provider base64-encodes the key

---

### Framework Integration

#### Express.js

```ts
import express from 'express';
import { WebhookVerificationService } from '@hookflo/tern';

const app = express();

// IMPORTANT: use raw body parser for webhook routes
app.post(
  '/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const result = await WebhookVerificationService.verifyWithPlatformConfig(
      req,
      'stripe',
      process.env.STRIPE_WEBHOOK_SECRET!
    );

    if (!result.isValid) {
      return res.status(400).json({ error: result.error });
    }

    const event = result.payload;
    // handle event.type, e.g. 'payment_intent.succeeded'

    res.json({ received: true });
  }
);
```

> **Common mistake**: Express's default `json()` middleware consumes and re-serializes
> the body, breaking HMAC. Always use `express.raw()` on webhook endpoints.

#### Next.js App Router (Route Handler)

```ts
// app/api/webhooks/github/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { WebhookVerificationService } from '@hookflo/tern';

export async function POST(req: NextRequest) {
  const result = await WebhookVerificationService.verifyWithPlatformConfig(
    req,
    'github',
    process.env.GITHUB_WEBHOOK_SECRET!
  );

  if (!result.isValid) {
    return NextResponse.json({ error: result.error }, { status: 400 });
  }

  const event = req.headers.get('x-github-event');
  // handle event

  return NextResponse.json({ received: true });
}

// Disable body parsing so Tern gets the raw body
export const config = { api: { bodyParser: false } };
```

#### Cloudflare Workers

```ts
addEventListener('fetch', (event) => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request: Request): Promise<Response> {
  if (request.method === 'POST' && new URL(request.url).pathname === '/webhooks/clerk') {
    const result = await WebhookVerificationService.verifyWithPlatformConfig(
      request,
      'clerk',
      CLERK_WEBHOOK_SECRET
    );

    if (!result.isValid) {
      return new Response(JSON.stringify({ error: result.error }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ received: true }));
  }

  return new Response('Not Found', { status: 404 });
}
```

---

### Platform Manager (Advanced)

```ts
import { platformManager } from '@hookflo/tern';

// Verify using the platform manager directly
const result = await platformManager.verify(request, 'stripe', 'whsec_...');

// Get the config for a platform (for inspection)
const config = platformManager.getConfig('stripe');

// Get docs/metadata for a platform
const docs = platformManager.getDocumentation('stripe');

// Run built-in tests for a platform
const passed = await platformManager.runPlatformTests('stripe');
```

---

### Testing

```bash
npm test                       # run all tests
npm run test:platform stripe   # test one platform
npm run test:all               # test all platforms
```

---

## Part 2 — Hookflo (Hosted Alerting Platform)

Hookflo requires **no library installation**. The integration is:
1. Create a webhook endpoint in the Hookflo Dashboard → get a Webhook URL + Secret
2. Point your provider (Stripe, Supabase, Clerk, GitHub, etc.) at that URL
3. Configure Slack/email notifications in the dashboard

### How to Set Up a Hookflo Integration

**Step 1** — Go to [hookflo.com/dashboard](https://hookflo.com/dashboard/webhooks) and create a new webhook.
You'll receive:
- **Webhook URL** — paste into your provider's webhook settings
- **Webhook ID** — used for token-based platforms
- **Secret Token** — used by Hookflo to verify incoming events
- **Notification channel settings** — configure Slack or email

**Step 2** — Set up the provider to send to that Hookflo URL:

| Provider | Where to paste the URL |
|---|---|
| Stripe | Dashboard → Developers → Webhooks → Add endpoint |
| Supabase | Dashboard → Database → Webhooks → Create webhook |
| Clerk | Dashboard → Webhooks → Add endpoint |
| GitHub | Repo/Org Settings → Webhooks → Add webhook |

**Step 3** — In the Hookflo dashboard, configure:
- Which event types to alert on (e.g., `payment_intent.succeeded`, `user.created`)
- Notification channels (Slack workspace/channel, email addresses)
- Digest frequency if you want batched summaries instead of per-event alerts

### Hookflo Platform Docs

- **Stripe**: [docs.hookflo.com/webhook-platforms/stripe](https://docs.hookflo.com/webhook-platforms/stripe)
- **Supabase**: [docs.hookflo.com/webhook-platforms/supabase](https://docs.hookflo.com/webhook-platforms/supabase)
- **Clerk**: [docs.hookflo.com/webhook-platforms/clerk](https://docs.hookflo.com/webhook-platforms/clerk)
- **GitHub**: [docs.hookflo.com/webhook-platforms/github](https://docs.hookflo.com/webhook-platforms/github)
- **Slack notifications**: [docs.hookflo.com/notification-channels/slack](https://docs.hookflo.com/notification-channels/slack)

### Hookflo + Tern Together

If you want both programmatic verification (Tern) AND logging/alerting (Hookflo), use a proxy pattern:

```ts
// Your server receives the webhook, verifies it with Tern, then forwards to Hookflo
app.post('/webhooks/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  // 1. Verify with Tern
  const result = await WebhookVerificationService.verifyWithPlatformConfig(
    req, 'stripe', process.env.STRIPE_WEBHOOK_SECRET!
  );
  if (!result.isValid) return res.status(400).json({ error: result.error });

  // 2. Process locally
  handleStripeEvent(result.payload);

  // 3. Forward to Hookflo for alerting/logging (optional)
  await fetch(process.env.HOOKFLO_WEBHOOK_URL!, {
    method: 'POST',
    headers: { ...req.headers, 'Content-Type': 'application/json' },
    body: req.body,
  });

  res.json({ received: true });
});
```

Alternatively, point Stripe directly at your Hookflo URL and keep Tern for a different endpoint.

---

## Common Pitfalls & Best Practices

### Raw Body Requirement
HMAC signatures are computed over the **exact raw bytes** of the request body. Any
re-serialization (e.g., by a JSON body parser) will break verification. Always ensure:
- Express: use `express.raw({ type: 'application/json' })` on webhook routes
- Next.js Pages Router: set `export const config = { api: { bodyParser: false } }`
- Next.js App Router: Tern reads the body directly from the `Request` object

### Replay Attack Protection
Always pass `toleranceInSeconds` (default is 300 = 5 minutes). This rejects requests
with timestamps too far in the past, preventing replay attacks.

### Secrets Management
- Never hardcode secrets in source code
- Use environment variables: `process.env.STRIPE_WEBHOOK_SECRET`
- For Cloudflare Workers: use `wrangler secret put STRIPE_WEBHOOK_SECRET`
- For Vercel: add secrets in project settings

### Error Responses
Always return HTTP 400 (not 500) for failed verification — this signals to the sender
that the request was rejected (not that your server crashed).

### HTTPS Only
Webhook endpoints must use HTTPS in production. Never accept webhook traffic over HTTP.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `isValid: false`, error about signature | Body was parsed before Tern | Use raw body parser |
| `isValid: false`, error about timestamp | Clock skew or replay attack | Check server clock; increase tolerance if dev |
| `isValid: false` for Clerk | Missing svix headers | Ensure `svix-id`, `svix-timestamp`, `svix-signature` are forwarded |
| `isValid: false` for GitHub | Wrong secret | Re-copy secret from GitHub Webhooks settings |
| Tern not finding platform | Typo in platform name | Use lowercase: `'stripe'`, `'github'`, `'clerk'` |
| Hookflo not receiving events | Wrong URL pasted | Re-copy URL from Hookflo dashboard |

---

## Key Links

- **Tern GitHub**: https://github.com/Hookflo/tern
- **Tern npm**: https://www.npmjs.com/package/@hookflo/tern
- **Tern docs**: https://tern.hookflo.com
- **Hookflo homepage**: https://hookflo.com
- **Hookflo dashboard**: https://hookflo.com/dashboard
- **Hookflo docs**: https://docs.hookflo.com
- **Hookflo Discord**: https://discord.com/invite/SNmCjU97nr
