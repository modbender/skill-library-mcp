---
name: stripe-cli
description: Stripe CLI operations for local development, webhook testing, fixture-based event simulation, API inspection, and sandbox resource management. Use when installing or verifying stripe CLI, logging in, forwarding webhook events (`stripe listen --forward-to`), triggering test events (`stripe trigger`), replaying/resending events, tailing request logs, or performing safe subscription/checkout debugging in Stripe sandbox environments.
---

# Stripe CLI

## Overview

Use this skill to run Stripe CLI workflows safely and reproducibly for local and staging environments.

Default posture: **sandbox-first, least privilege, no secret leakage, no destructive live-mode actions**.

## Quick Start

```bash
# check install
stripe version

# authenticate (browser flow)
stripe login

# verify account context
stripe config --list
```

If using API key auth in CI/local automation:

```bash
export STRIPE_API_KEY=sk_test_...
stripe customers list --limit 3
```

## Workflow Decision Tree

1. **Need to debug incoming webhooks locally?**
   - Use: `stripe listen --forward-to ...`
   - See: `references/workflows.md` → Webhook Local Loop

2. **Need test events quickly (checkout/subscription/invoice)?**
   - Use: `stripe trigger ...` or `stripe fixtures ...`
   - See: `references/workflows.md` → Trigger & Fixtures

3. **Need inspect API behavior/errors?**
   - Use: `stripe logs tail`, `stripe events list`, `stripe events resend`
   - See: `references/commands.md`

4. **Need plan change/proration diagnostics?**
   - Use: direct API calls via CLI (`stripe subscriptions update ...`, `stripe invoices create_preview ...`)
   - Always run in test mode first.

## Safe Defaults (Mandatory)

- Prefer **test keys** (`sk_test_...`) and sandbox account context.
- Never print full secrets in logs or commits.
- Avoid `--skip-verify` except when explicitly required in local-only environments.
- Confirm account context before sensitive operations:
  - `stripe config --list`
  - `stripe whoami` (if available)
- Treat `stripe trigger` as stateful: it creates objects and side effects in sandbox.

## Common Tasks

### 1) Forward webhooks to local app

```bash
stripe listen --forward-to localhost:4242/webhook
```

Filter events when needed:

```bash
stripe listen \
  --events checkout.session.completed,invoice.paid,invoice.payment_failed,customer.subscription.updated \
  --forward-to localhost:4242/webhook
```

Load event configuration from dashboard webhook endpoint:

```bash
stripe listen --load-from-webhooks-api --forward-to localhost:4242
```

### 2) Trigger test events

```bash
stripe trigger checkout.session.completed
stripe trigger invoice.paid
stripe trigger customer.subscription.updated
```

For complex scenarios, prefer fixtures:

```bash
stripe fixtures path/to/fixture.json
```

### 3) Tail logs and inspect events

```bash
stripe logs tail
stripe events list --limit 10
stripe events resend evt_... --webhook-endpoint=we_...
```

### 4) API version testing

```bash
stripe products create --name "Test Product" --latest
stripe products create --name "Pinned Version" --stripe-version 2026-01-28.clover
```

## Security Guardrails

Before running commands that mutate state, verify:

- Environment = sandbox/test
- Correct account/project
- No production webhook endpoint accidentally targeted
- No plaintext secrets in shell history/docs

If user asks for live-mode operation, require explicit confirmation and explain blast radius.

## Bundled Scripts

- `scripts/stripe-dev-listen.sh`
  - Starts `stripe listen` with safer defaults and event filters.
- `scripts/stripe-sanitize.sh`
  - Redacts API keys and webhook secrets from logs/files for sharing.

## References

- `references/workflows.md` - production-grade Stripe CLI workflows
- `references/commands.md` - high-value command cheatsheet
- `references/security.md` - security and compliance checklist for community use
