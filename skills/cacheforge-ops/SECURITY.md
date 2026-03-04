# Security

## Safety Posture

- This skill is API-driven account management.
- No destructive filesystem actions are performed.

## Billing Safety

- Top-up actions generate payment links; they do not directly charge cards from the CLI.
- Auto top-up enablement requires an existing saved payment method.

## Secrets Handling

- Requires `CACHEFORGE_API_KEY` in environment.
- Never commit credentials.
