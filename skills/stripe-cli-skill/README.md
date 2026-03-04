# stripe-cli skill

Community skill for safe and productive usage of the **Stripe CLI** with OpenClaw agents.

## What this skill does

This skill provides:

- Safe Stripe CLI workflows for local/staging environments
- Webhook forwarding (`stripe listen --forward-to`)
- Event simulation (`stripe trigger`, `stripe fixtures`)
- API debugging (`stripe logs tail`, event inspect/resend)
- Subscription/proration diagnostic workflows
- Security guardrails for community usage (sandbox-first, secret redaction, least privilege)

## Who should use it

Use this skill when you need to:

- Test webhook handlers locally
- Reproduce billing/subscription event flows quickly
- Debug Stripe API behavior from terminal
- Run Stripe CLI safely without leaking secrets

## Included files

- `SKILL.md` — trigger + operational instructions for agents
- `references/workflows.md` — practical end-to-end workflows
- `references/commands.md` — high-value command reference
- `references/security.md` — security checklist
- `scripts/stripe-dev-listen.sh` — safer local listener wrapper
- `scripts/stripe-sanitize.sh` — redact Stripe secrets from output/logs

## Security defaults

- Prefer `sk_test_*` and sandbox context
- Never commit or share secrets (`sk_*`, `rk_*`, `whsec_*`)
- Treat `trigger/fixtures` as stateful operations
- Require explicit confirmation for live-mode operations

## Quick examples

```bash
# start local webhook listener with recommended event filters
./scripts/stripe-dev-listen.sh localhost:4242/webhook

# trigger common test event
stripe trigger checkout.session.completed

# redact secrets before sharing logs
cat stripe.log | ./scripts/stripe-sanitize.sh
```

## Related docs

- Stripe CLI docs: https://docs.stripe.com/stripe-cli
- CLI usage: https://docs.stripe.com/stripe-cli/use-cli
- CLI reference: https://docs.stripe.com/cli
