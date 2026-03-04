---
name: humanpages
description: "Search and hire real humans for tasks — photography, delivery, research, and more"
homepage: https://humanpages.ai
user-invocable: true
metadata:
  openclaw:
    primaryEnv: HUMANPAGES_AGENT_KEY
    requires:
      env:
        - HUMANPAGES_AGENT_KEY
      bins:
        - npx
---

# Human Pages — Hire Humans for Real-World Tasks

Human Pages is an AI-to-human marketplace. Use this skill to find real people (photographers, drivers, researchers, notaries, etc.) and hire them for tasks, paying directly in USDC with no platform fees.

## Setup

1. The MCP server must be running. Verify with `openclaw mcp list` — you should see `humanpages`.
2. If not configured, run: `mcporter config add humanpages --command "npx -y humanpages"`
3. `HUMANPAGES_AGENT_KEY` should contain your agent API key (starts with `hp_`). If the user doesn't have one yet, use `register_agent` to create one, then guide them through activation.

## Core Workflow

The typical lifecycle is: **Search** → **Register & Activate** → **Hire** → **Pay** → **Review**.

### 1. Search for Humans

Use `search_humans` to find people. Filter by:
- `skill` — e.g. "photography", "driving", "notary", "research"
- `equipment` — e.g. "car", "drone", "camera"
- `language` — ISO code like "en", "es", "zh"
- `location` — city or neighborhood name
- `lat`/`lng`/`radius` — GPS radius search in km
- `max_rate` — maximum hourly rate in USD
- `work_mode` — REMOTE, ONSITE, or HYBRID
- `verified` — set to "humanity" for identity-verified humans only

Use `get_human` for a detailed public profile (bio, skills, services, reputation).

### 2. Register & Activate Agent

If the user has no agent key yet:

1. Call `register_agent` with a name. Save the returned API key — it cannot be retrieved later.
2. Agent starts as PENDING. Must activate before creating jobs.

**Free activation (BASIC tier, 1 offer/2 days, 1 profile view/day):**
1. Call `request_activation_code` to get an HP-XXXXXXXX code
2. Ask user to post the code on social media (Twitter/X, LinkedIn, etc.)
3. Call `verify_social_activation` with the post URL

**Paid activation (PRO tier, 15 offers/day, 50 profile views/day):**
1. Call `get_payment_activation` for deposit address
2. User sends USDC payment on-chain
3. Call `verify_payment_activation` with tx hash and network

**x402 pay-per-use (no activation needed):**
Agents can pay per request via x402 (USDC on Base) — $0.05/profile view, $0.25/job offer. Include an `x-payment` header. Bypasses tier rate limits.

Use `get_activation_status` to check current tier and rate limits.

### 3. View Full Profiles

Once activated, use `get_human_profile` to see contact info, wallet addresses, fiat payment methods, and social links. Pass the `agent_key`.

### 4. Create a Job Offer

Call `create_job_offer` with:
- `human_id` — the human to hire
- `title` and `description` — what needs to be done
- `price_usdc` — agreed price
- `agent_id` and `agent_key` — your agent credentials

Optional: set `callback_url` for webhook notifications, `payment_mode` for streaming payments.

Wait for the human to ACCEPT the offer. Poll with `get_job_status`.

### 5. Pay

**One-time payment:**
1. Send USDC to the human's wallet (from `get_human_profile`)
2. Call `mark_job_paid` with the transaction hash, network, and amount

**Stream payment (ongoing work):**
1. Call `start_stream` after the human accepts
2. For MICRO_TRANSFER: call `record_stream_tick` for each payment
3. Use `pause_stream`, `resume_stream`, `stop_stream` to manage

### 6. Review

After the human marks the job complete, call `leave_review` with a 1-5 rating and optional comment.

## Additional Tools

- `get_agent_profile` — view any agent's public profile and reputation
- `verify_agent_domain` — verify domain ownership for a trust badge
- `check_humanity_status` — check if a human has Gitcoin Passport verification

## Error Handling

- If `create_job_offer` returns AGENT_PENDING, guide the user through activation first.
- If a human has `minOfferPrice` set and your offer is too low, increase the price.
- Rate limit errors mean the tier cap was hit. Upgrade to PRO tier, use x402 pay-per-use, or wait.

## Action Groups

| Action Group | Enabled | Description |
|---|---|---|
| search | Y | Search humans and view public profiles |
| register | Y | Register and activate agents |
| jobs | Y | Create job offers and manage job lifecycle |
| payments | Y | Record payments and manage streams |
| reviews | Y | Leave reviews for completed jobs |
