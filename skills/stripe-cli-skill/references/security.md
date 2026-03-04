# Security Checklist for Stripe CLI Skills

## 1) Environment Safety
- Default to `sk_test_` keys.
- Require explicit confirmation before any live-mode operation.
- Verify target account context before mutating commands.

## 2) Secret Handling
- Never commit keys (`sk_*`, `rk_*`, `whsec_*`).
- Never paste full secrets in issue trackers/chats.
- Redact secrets before sharing command output.

## 3) Webhook Safety
- Keep local endpoint private.
- Use generated `whsec_...` from current `stripe listen` session.
- Rotate webhook secrets when exposure is suspected.

## 4) Command Safety
- `stripe trigger` and `fixtures` have side effects.
- Use dedicated sandbox data and cleanup scripts.
- Avoid running broad delete/mutate commands without scoping IDs.

## 5) Community Publishing Safety
- Include no credentials in skill files/examples.
- Include explicit warnings for test vs live mode.
- Include safe defaults in scripts (`--events` filters, localhost target).
