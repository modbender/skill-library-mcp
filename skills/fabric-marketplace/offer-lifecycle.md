# Offer Lifecycle

Offers are Fabric's core transaction primitive. Understanding the state machine, hold mechanics, and idempotency discipline prevents bugs, wasted credits, and stuck negotiations.

## State machine

```
                     ┌──── rejected (terminal)
                     │
pending ─────┬──── accepted_by_a ──── mutually_accepted (terminal success)
             │              │
             │    accepted_by_b ──── mutually_accepted (terminal success)
             │
             ├──── countered (terminal — follow new offer via thread_id)
             ├──── cancelled (terminal — creator only)
             └──── expired (terminal — automatic at expires_at)
```

**Key rules:**
- Both parties must accept for `mutually_accepted`. One-sided acceptance moves to `accepted_by_a` or `accepted_by_b`.
- Countering creates a *new* offer in the same thread. The old offer becomes `countered` (terminal). Follow `thread_id` to find the latest.
- Only the creator can cancel. Only the recipient can reject.
- Expiry is automatic and server-enforced.

## Hold mechanics

When an offer is created, Fabric places **holds** on the specified units.

| Event | Hold effect |
|---|---|
| Offer created | Holds created, `hold.expires_at = offer.expires_at` |
| Offer rejected | Holds released |
| Offer cancelled | Holds released |
| Offer countered | Old holds released, new holds created on counter's units |
| Offer expired | Holds released |
| Mutual acceptance | Holds committed; units auto-unpublished |

**Treat `hold_expires_at` as a hard deadline.** If you need more time, cancel and re-offer with a longer TTL (this releases and re-acquires holds).

Holds prevent double-selling: while a hold exists on a unit, other offers targeting that unit will show it in `unheld_unit_ids` (the offer still proceeds, but without a hold guarantee on that specific unit).

## Idempotency discipline

Every non-GET request requires an `Idempotency-Key` header.

### The rules

1. **Same key + same payload = safe replay.** If your request times out or you get a 5xx, retry with the *exact same* key and body. Fabric returns the cached response.

2. **Same key + different payload = 409 conflict.** This is intentional — it prevents accidental double-submits with mutated data. Generate a new key if your payload has changed.

3. **New action = new key.** Each distinct business action (create offer, accept offer, counter offer) gets its own idempotency key.

### Key naming convention

Use descriptive, unique keys:
```
fabric_offer_create:<node_id>:<target_unit_id>:<timestamp>
fabric_offer_accept:<offer_id>:<timestamp>
fabric_offer_counter:<offer_id>:<timestamp>
fabric_search:<query_hash>:<timestamp>
```

### Retry strategy

```
attempt 1: POST with Idempotency-Key: K1
  → timeout or 5xx
attempt 2: POST with Idempotency-Key: K1 (same key, same body)
  → returns cached response or processes if first attempt didn't complete
attempt 3: if still failing, wait and retry with K1
  → after 3 failures with the same key, stop and investigate
```

**Never generate a new key for a retry.** That creates a duplicate action.

## Optimistic concurrency

PATCH endpoints require `If-Match: <version>` where `version` is the `row_version` from the last read.

If someone else modified the resource between your read and your write:
- You get `409 stale_write_conflict`
- Re-read the resource to get the new version
- Decide if your update is still valid given the new state
- Retry with the updated `If-Match` value and a **new idempotency key** (because the payload may have changed)

## Common lifecycle patterns

### Pattern: create → wait → respond

For passive participants (publish and wait strategy):
1. Publish units
2. Configure webhook
3. Receive `offer_created` event
4. Read the offer: `GET /v1/offers/<offer_id>`
5. Decide: accept, counter, or reject

### Pattern: search → offer → negotiate → close

For active participants:
1. Search for what you need
2. Create an offer targeting specific units
3. Monitor for counterparty response (webhook or poll)
4. Accept, counter, or let expire based on terms
5. On mutual acceptance, reveal contact

### Pattern: counter-offer thread

```
Node A creates offer O1 → pending
Node B counters O1 with offer O2 → O1 becomes "countered", O2 is "pending"
Node A counters O2 with offer O3 → O2 becomes "countered", O3 is "pending"
Node B accepts O3 → accepted_by_b
Node A accepts O3 → mutually_accepted
```

All offers share the same `thread_id`. Always follow the latest offer in the thread.

### Pattern: multi-party composition

For complex deals requiring multiple counterparties:
1. Create independent offers to each Node (separate idempotency keys)
2. Track each offer's lifecycle independently
3. If one deal falls through, the others continue unaffected
4. Manage dependencies in your own logic (Fabric doesn't support conditional offers)
