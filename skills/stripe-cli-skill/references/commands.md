# Stripe CLI Command Reference (High-Value)

## Core
```bash
stripe version
stripe --help
stripe <command> --help
```

## Auth & Config
```bash
stripe login
stripe logout
stripe config --list
```

## Webhooks
```bash
stripe listen --forward-to localhost:4242/webhook
stripe listen --events payment_intent.succeeded,checkout.session.completed --forward-to localhost:4242/webhook
stripe listen --load-from-webhooks-api --forward-to localhost:4242
```

## Testing
```bash
stripe trigger payment_intent.succeeded
stripe trigger checkout.session.completed
stripe fixtures path/to/fixture.json
```

## Logs / Events
```bash
stripe logs tail
stripe events list --limit 20
stripe events retrieve evt_xxx
stripe events resend evt_xxx --webhook-endpoint=we_xxx
```

## API via CLI
```bash
stripe products create --name "My Product"
stripe prices create --unit-amount 3000 --currency brl --product prod_xxx
stripe customers list --limit 5
stripe subscriptions list --customer cus_xxx
stripe subscriptions update sub_xxx -d "items[0][id]=si_xxx" -d "items[0][price]=price_xxx"
```

## API Version Flags
```bash
stripe products create --name "Latest API" --latest
stripe products create --name "Pinned API" --stripe-version 2026-01-28.clover
```
