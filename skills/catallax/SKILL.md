---
name: catallax
description: >
  Interact with the Catallax decentralized contract work protocol on Nostr.
  Use when the user mentions tasks, bounties, contract work, arbiters, escrow,
  labor market, gigs, or Catallax. Supports browsing open tasks, creating task
  proposals, discovering arbiter services, submitting work deliveries, and
  managing the full task lifecycle (kinds 33400, 33401, 3402).
---

# Catallax Skill

Interact with Catallax — a decentralized contract work protocol on Nostr using Lightning/Cashu payments and trusted escrow arbiters.

## Protocol Overview

Read `references/NIP-3400.md` for the full spec. Key concepts:

- **Patron**: Creates tasks, funds escrow, assigns workers
- **Arbiter**: Escrow agent who judges work and handles payment
- **Free Agent**: Applies for tasks, delivers work, gets paid
- **Kinds**: 33400 (arbiter service), 33401 (task proposal), 3402 (task conclusion)
- **Status flow**: proposed → funded → in_progress → submitted → concluded

## Querying Tasks

Use `nak` to query kind 33401 events from relays:

```bash
# List all task proposals (limit 50)
nak req -k 33401 -l 50 wss://relay.damus.io

# Filter by tag (e.g. tasks tagged "development")
nak req -k 33401 -t development -l 50 wss://relay.damus.io

# Filter by status (open tasks only)
nak req -k 33401 -l 100 wss://relay.damus.io | \
  while read -r event; do
    status=$(echo "$event" | jq -r '.tags[] | select(.[0]=="status") | .[1]')
    if [ "$status" = "proposed" ] || [ "$status" = "funded" ]; then
      echo "$event"
    fi
  done
```

Parse the content field as JSON to get title, description, requirements. Parse tags for amount, status, categories.

### Display Format

When presenting tasks to the user, show:
- **Title** (from content.title)
- **Bounty** (from `amount` tag, in sats — show "?" if missing)
- **Status** (from `status` tag)
- **Date** (from created_at)
- **Categories** (from `t` tags)
- **Description** (from content.description, truncated)
- **Funding type** (from `funding_type` tag: "patron" or "crowdfunding")

## Querying Arbiters

```bash
# List arbiter services
nak req -k 33400 -l 50 wss://relay.damus.io
```

Parse content for name, about, policy. Parse tags for fee_type, fee_amount, min/max amounts, categories.

### Display Format

When presenting arbiters:
- **Name** (from content.name)
- **Fee** (fee_type + fee_amount — e.g. "5%" or "1000 sats flat")
- **Min/Max** (from min_amount/max_amount tags)
- **Categories** (from `t` tags)
- **About** (from content.about)

## Creating a Task Proposal

To create a task as a Patron, publish a kind 33401 event:

```bash
# Build and publish task proposal
nak event -k 33401 \
  --tag d="<unique-slug>" \
  --tag p="<your-pubkey>" \
  --tag amount="<bounty-in-sats>" \
  --tag t="<category>" \
  --tag status="proposed" \
  --tag funding_type="patron" \
  -c '{"title":"Task Title","description":"Detailed description...","requirements":"What must be delivered"}' \
  --sec "<nsec>" \
  wss://relay.damus.io wss://nos.lol wss://relay.primal.net
```

Generate the d-tag slug from the title (lowercase, hyphenated, with random suffix for uniqueness).

**Important**: The content field must be valid JSON with title, description, and optionally requirements and deadline.

## Updating Task Status

Since kind 33401 is addressable replaceable, publish a new event with the same d-tag to update. Include all original tags plus changes:

```bash
# Update to funded (add zap receipt reference)
nak event -k 33401 \
  --tag d="<same-d-tag>" \
  --tag status="funded" \
  --tag e="<zap-receipt-event-id>" \
  # ... all other original tags ...
  --sec "<nsec>" \
  wss://relay.damus.io
```

## Submitting Work (as Free Agent)

Work delivery is coordinated out-of-band per the protocol. However, agents may use kind 951 (work delivery) as a convention:

```bash
nak event -k 951 \
  --tag e="<task-event-id>" \
  --tag p="<patron-pubkey>" \
  -c '{"delivery":"Description of completed work","evidence":"Link or proof"}' \
  --sec "<nsec>" \
  wss://relay.damus.io
```

## Task Conclusion (Arbiter only)

```bash
nak event -k 3402 \
  --tag e="<payout-zap-receipt-id>" \
  --tag e="<task-event-id>" \
  --tag p="<patron-pubkey>" \
  --tag p="<arbiter-pubkey>" \
  --tag p="<worker-pubkey>" \
  --tag resolution="successful" \
  --tag a="33401:<patron-pubkey>:<task-d-tag>" \
  -c '{"resolution_details":"Work met all requirements"}' \
  --sec "<nsec>" \
  wss://relay.damus.io
```

## Common Queries

| User says | Action |
|-----------|--------|
| "find bounties" / "show tasks" | Query kind 33401, filter status=proposed or funded |
| "create a task" / "post a bounty" | Build and publish kind 33401 |
| "find arbiters" | Query kind 33400 |
| "submit work" / "deliver" | Publish kind 951 referencing the task |
| "check my tasks" | Query kind 33401 filtered by user's pubkey in p-tags |
| "what's the status" | Fetch specific task by d-tag, report status |

## Reference Client

For visual browsing: https://catallax-reference-client.netlify.app/catallax

## Key Relays

Query multiple relays for best coverage:
- wss://relay.damus.io
- wss://nos.lol
- wss://relay.primal.net

**Note**: Some relays may not return results for `nak req -k 33401` due to kind filtering. If `nak` returns empty results, fall back to a WebSocket script approach — open a WebSocket connection, send a REQ with `{"kinds":[33401],"limit":50}`, and collect EVENT responses until EOSE.

## Edge Cases

- **Missing amount tag**: Some tasks use crowdfunding (funding_type=crowdfunding) with a NIP-75 goal tag instead of a fixed amount. Display bounty as "crowdfunded" in this case.
- **Content format**: Content should be JSON but some early tasks used plain text. Try JSON.parse first, fall back to treating content as description.
- **Stale tasks**: Tasks with status=proposed older than 30 days may be abandoned. Note age when displaying.
- **Multiple relays**: Always publish to 3+ relays for discoverability. Query from multiple relays and deduplicate by event id.
