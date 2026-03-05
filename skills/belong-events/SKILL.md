---
name: belong-events
description: Create, discover, and manage events with NFT tickets on the Belong platform
metadata: {"openclaw": {"emoji": "🎫", "primaryEnv": "BELONG_EVENTS_API_KEY", "optionalEnv": ["BELONG_EVENTS_ENDPOINT"], "requires": {"bins": ["curl"]}}}
---

# Belong Events

Discover events, buy tickets, create events, and manage venue check-ins on Belong.

## How to call tools

Run `{baseDir}/invoke.sh <method> '<params-json>'` via `system.run`. The script calls the Belong skill API and returns JSON.

Example:
```
system.run {baseDir}/invoke.sh discover_events '{"city":"Miami","limit":5}'
```

All tool calls use this pattern. The `invoke.sh` script handles endpoint URL, authentication headers, and JSON-RPC framing automatically.

Default endpoint:
`https://join.belong.net/functions/v1/openclaw-skill-proxy`

Network disclosure:
- All JSON-RPC calls are sent to the endpoint above (or `BELONG_EVENTS_ENDPOINT` if overridden).
- If `BELONG_EVENTS_API_KEY` is set, it is sent to that endpoint as `X-OpenClaw-Key`.

## Account linking (required for protected tools)

Most tools require a linked Belong account. If any tool returns "Belong account not linked" or "BELONG_LINK_REQUIRED", run the OTP flow:

1. Ask the user for their email address.
2. Send OTP:
   ```
   system.run {baseDir}/invoke.sh belong_email_otp_send '{"email":"USER_EMAIL"}'
   ```
3. Ask for the 6-digit code from their email.
4. Verify OTP:
   ```
   system.run {baseDir}/invoke.sh belong_email_otp_verify '{"email":"USER_EMAIL","otp":"CODE"}'
   ```
5. The response includes `apiKey`. Store it — set it as `BELONG_EVENTS_API_KEY` env var or update `skills.entries.belong-events.apiKey` in `openclaw.json` so subsequent calls are authenticated.

Never ask end users for an API key. Always use the OTP flow.

## Available tools

### Public (no auth needed)
Public tools are rate-limited. If you hit a 429, wait and retry.

- **list_tools** — List available tools (no params)
- **discover_events** — Search events. Params: `city`, `category`, `startDate`, `endDate`, `limit`, `latitude`, `longitude` (all optional)
- **get_event_details** — Get event details. Params: `eventId` (required), `source`, `city`, `latitude`, `longitude` (optional)
- **buy_ticket** — Get checkout/event URL. Params: `eventId` (required), `tierId`, `quantity`
- **belong_email_otp_send** — Send OTP. Params: `email` (required)
- **belong_email_otp_verify** — Verify OTP. Params: `email` (required), `otp` (required)

### Account status (auth required)
- **whoami** — Check link status (no params)

### Attendee (auth required)
- **my_tickets** — List purchased tickets. Params: `status` (upcoming/past/all)

### Organizer (auth required)
- **create_event** — Create event. Params: `name` (required), `startDate` (required), `endDate` (required), `description`, `city`, `venue`, `category`
- **update_event** — Update event. Params: `eventId` (required), `name`, `description`, `startDate`, `endDate`
- **deploy_tickets** — Deploy NFT tickets. Params: `eventId` (required), `tierName` (required), `price` (required), `maxSupply`, `chainId`, `transferable`, `gasless`. Two-phase: first call returns tx params, second call with `collectionId`+`txHash` completes deployment.
- **my_events** — List owned events. Params: `status` (upcoming/past/draft/all)
- **event_analytics** — Event stats. Params: `eventId` (required)

### Venue (auth required)
- **check_in** — Process check-in. Params: `hubId` (required), `amount`, `latitude`, `longitude`, `customerWallet`, `listPending`, `checkinId`, `action`
- **list_pending_checkins** — List pending. Params: `hubId` (required), `limit`
- **approve_checkin** — Approve/reject. Params: `checkinId` (required), `action` (approve/reject)
- **setup_venue_rewards** — Configure rewards. Params: `hubId` (required), `visitBounty`, `cashbackPercent`
- **withdraw_earnings** — Withdrawal link. Params: `hubId` (required), `currency` (USDC/LONG)
