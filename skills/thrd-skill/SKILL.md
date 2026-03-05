---
name: thrd
description: "Provision a dedicated inbox for your AI agent and manage email safely via thrd.email. Includes instant onboarding, inbound polling, reply/send (idempotent + policy-gated), Proof of Reasoning for cold outbound, Human Claiming for verification, and trust/delivery tracking. Does not persist API keys to disk."
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "requires": { "bins": ["python3"], "env": ["THRD_API_KEY"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "exec",
              "command": "pip install -r requirements.txt",
              "label": "Install Python dependencies",
            },
          ],
      },
  }
---

# Thrd Email Skill

This skill helps you create and operate an isolated inbox for an AI agent using [thrd.email](https://thrd.email), without connecting your personal inbox.

Safety by default: don't connect your primary inbox to an agent; use a dedicated agent inbox.

## Workflows

### Sync API Contract (Recommended Before Tool Use)
To avoid stale assumptions, refresh the OpenAPI contract and read `info.version`:
```bash
python3 scripts/openapi_sync.py
python3 scripts/openapi_sync.py --print-version
```
This uses HTTP cache validators (`ETag`/`Last-Modified`) and only re-downloads when changed.

### Provision a New Email Account
To create a new email account, run the onboarding script:
```bash
python3 scripts/onboard.py --agent-name "My Agent" [--tenant-name "My Company"]
```
This prints a JSON payload to stdout that includes `api_key` and the new inbox address. Treat `api_key` as a secret.

Security note: **Do not write your API key to disk.** Store it in your runtime's secret manager and set `THRD_API_KEY` as an environment variable. (The rest of the tools require `THRD_API_KEY`; onboarding does not.)

### Upgrade Plan (Billing)
To start paid billing for your current tenant, use the checkout script:
```bash
python3 scripts/checkout.py <plan_name>
```
Plans:
- `sandbox` -> Sandbox Starter (9 EUR/month, raises Tier 1 monthly limit from 100 to 2,000 emails)
- `limited` -> Tier 2
- `verified` -> Tier 3

Forward the resulting Stripe URL to your human owner for payment.

### Human Claiming (Verification)
Tier 3 (Verified Outbound) requires a responsible human linked via X.
- Start the flow: `POST /v1/claim/x/start`
- Forward the `claim_url` to your human owner.
- Check status: `GET /v1/claim/x/status`

### Proof of Reasoning (PoR)
Cold outbound (Tier 3) may require a reasoning challenge to prevent spam.
- If you receive a `428 por_required` error, solve the logical challenge provided in the response.
- Re-send the request with `por_token` and `por_answer`.

### Manage Emails and Track Delivery
For detailed API usage (polling, sending, replying, trust scores, and checking delivery status), see [references/api.md](references/api.md).
Note: replies use reply-all behavior by default: they preserve historical CC and keep recipients from the latest inbound `To` line so participants are not dropped.
Tier2+ may add CC via `cc[]`. In Tier1, `cc[]` may only contain addresses already present in that thread's CC history.
Security note: when Prompt Shield marks an inbound email as high-risk, Tier2/3 flows may require creating a short-lived `security_ack_token` (`POST /v1/security/ack`) before `reply`/`send`.
Quota note: use `GET /v1/usage` to monitor monthly usage (`used`, `remaining`, `state`, `reset_at`) and avoid hitting hard limits mid-run.

### Wake-Up Strategy (Recommended)
Many LLM runtimes do not reliably maintain background polling. Use wake webhooks when possible:
- Configure webhook: `PUT /v1/wake/webhook`
- Read status: `GET /v1/wake/webhook`
- Disable webhook: `DELETE /v1/wake/webhook`

THRD sends signed `inbox.pending` pings, then your runtime should immediately pull with `GET /v1/events` and ACK.

Fallback when webhooks are not available:
```bash
python3 scripts/poll_daemon.py --cursor-file .thrd_cursor --on-events "echo inbound-ready"
```
This keeps pull-based delivery alive without requiring a public webhook endpoint.
Security note: `--on-events` runs in safe argv mode (no shell). Shell operators like `;`, `&&`, pipes, or redirects are not supported.

## Tools
- `scripts/onboard.py`: Instant provisioning of a new email inbox.
- `scripts/checkout.py`: Generate a Stripe Checkout URL for upgrades.
- `scripts/openapi_sync.py`: Refresh/cache latest OpenAPI and read current `info.version`.
- `scripts/poll_daemon.py`: Fallback long-poll daemon for runtimes without wake webhook support.
