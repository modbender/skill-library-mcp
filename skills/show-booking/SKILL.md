---
name: show-booking
description: Book real estate showing tours from emailed or pasted listing details, including extracting listing data, preparing outbound call jobs, coordinating a calling sub-agent, creating calendar invites, and returning confirmations. Use when the user asks to book showings for one or more properties, coordinate preferred windows for a client, or automate office calls instead of manual BrokerBay login flows.
---

# Show Booking

## Overview

Execute an end-to-end workflow for showing requests:
1. Parse intake from free-form prompt or email text.
2. Build per-listing call jobs.
3. Hand off call execution to the `tour-booking` sub-agent.
4. Generate calendar invite files from confirmed slots.
5. Return a concise confirmation summary.

## Inputs

Collect these fields before running outbound calls:
- Client full name.
- Listings (address, listing ID if present, office phone, listing office/agent name if present).
- Preferred windows and timezone.
- Booking constraints (lockbox notes, occupants, minimum notice).
- Confirmation target (email/SMS destination for status updates).

If any listing is missing a phone number, flag it as `blocked` and do not place calls for that listing.

## Workflow

### 1) Parse intake

Run:

```bash
python3 scripts/intake_request.py --input-file /path/to/intake.txt --output /tmp/showing-intake.json
```

Or pass inline text:

```bash
python3 scripts/intake_request.py --input-text "Book showings for ..." --output /tmp/showing-intake.json
```

### 2) Build call queue

Run:

```bash
python3 scripts/orchestrate_showings.py --intake /tmp/showing-intake.json --output /tmp/showing-plan.json
```

This produces:
- `call_queue`: listings with phone numbers ready for calls.
- `blocked`: listings missing required data.
- `calendar_candidates`: records ready for invite creation after call confirmation.

### 3) Delegate calling to `tour-booking`

For each `call_queue` record, invoke `tour-booking/scripts/place_outbound_call.py` with:
- Listing metadata.
- Preferred windows.
- Client identity.
- Callback instructions.

If live calling is not approved, run with `--dry-run` and return the generated payload.

### 4) Create invites for confirmed slots

When a listing returns a confirmed date/time:

```bash
python3 scripts/create_invite_ics.py \
  --input /tmp/confirmed-showings.json \
  --output-dir /tmp/showing-invites
```

The script emits one `.ics` file per confirmed showing. Import into Google Calendar or send directly as attachments.

### 5) Return status

Report:
- Confirmed showings with time, address, and invite file path.
- Pending callbacks.
- Blocked listings and the missing field(s).
- Total calls attempted and success/failure counts.

## Guardrails

- Explicitly identify the caller as an AI assistant acting for the brokerage/realtor.
- Respect local telemarketing and consent requirements.
- Keep a full audit trail: request payload, call result, booking outcome, and timestamps.
- Never claim a showing is confirmed until the call result explicitly indicates confirmation.
