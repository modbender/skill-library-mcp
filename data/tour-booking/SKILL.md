---
name: tour-booking
description: Sub-agent for outbound listing-office calls to request and confirm property showing slots using a provided call script and structured payloads. Use when a parent workflow needs call execution for one or more listings, including dry-run payload generation, live ElevenLabs call requests, and parsing call outcomes into booking statuses.
---

# Tour Booking

## Overview

Handle the call execution layer for property showing bookings:
1. Build a consistent call prompt from listing and client data.
2. Send outbound call request to ElevenLabs (or dry-run).
3. Normalize call outcome into structured status fields.

## Inputs

Each call job should include:
- `job_id`
- `client_name`
- `listing.address`
- `listing.office_phone`
- `preferred_windows_text`
- `timezone`

## Runbook

### 1) Build payload

```bash
python3 scripts/prepare_call_payload.py \
  --job /tmp/job.json \
  --output /tmp/call-payload.json
```

### 2) Place call

Dry-run (default safe mode):

```bash
python3 scripts/place_outbound_call.py \
  --payload /tmp/call-payload.json \
  --output /tmp/call-result.json \
  --dry-run
```

Live mode:

```bash
python3 scripts/place_outbound_call.py \
  --payload /tmp/call-payload.json \
  --output /tmp/call-result.json \
  --live
```

### 3) Parse outcome

```bash
python3 scripts/parse_call_result.py \
  --input /tmp/call-result.json \
  --output /tmp/booking-outcome.json
```

## Call Guardrails

- State clearly that the caller is an AI assistant calling on behalf of the realtor.
- Ask for available slots inside the requested window first; request alternatives if unavailable.
- Confirm final slot with exact date and local time before ending the call.
- If the office cannot confirm, mark as `pending_callback` and capture callback requirements.
