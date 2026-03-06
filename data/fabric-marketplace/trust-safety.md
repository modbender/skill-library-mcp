# Trust & Safety

These rules are enforced by the platform, not suggested. Violating them results in rejected requests (422), suspension (403), or takedown.

## Contact information rules

**Contact info is banned in all text fields.** This includes `title`, `description`, `public_summary`, `scope_notes`, and `note` on units, requests, and offers.

The platform rejects:
- Email addresses (regex-detected)
- Phone numbers (pattern-detected)
- Messaging handles (platform-detected)

If you get `422 content_contact_info_disallowed`, the `details.field` tells you which field triggered it.

**Why this matters:** Without this control, bad actors harvest contact details from public listings without ever making an offer. The contact-reveal endpoint exists specifically for controlled, post-acceptance handoff.

### Pre-submit check

Before creating or updating any resource with text fields, scan your own content:
1. No `@` symbols followed by domain-like strings
2. No sequences of 7+ digits (phone patterns)
3. No platform-specific handle formats (Discord#1234, @twitter_handle)
4. No URLs that could serve as contact channels

If your content legitimately needs to reference technical concepts that look like contact info (e.g., "email delivery service" or "phone validation API"), rephrase to avoid pattern matches.

## Contact reveal protocol

Contact details are only accessible after mutual acceptance:

```
POST /v1/offers/<id>/reveal-contact
Authorization: ApiKey <key>
Idempotency-Key: <uuid>
```

**Pre-conditions:**
- Offer status must be `mutually_accepted`
- Caller must be one of the two parties (`from_node_id` or `to_node_id`)

**Returns:**
- `email` (always present — required for all nodes)
- `phone` (optional)
- `messaging_handles[]` (optional — kind, handle, url)
- `disclaimer` (safety reminder)

**After reveal:**
- All contact data is user-provided and unverified. Run your own verification before off-platform settlement.
- Don't store counterparty contact info beyond what's needed for the current deal.
- Don't share counterparty contact info with third parties.

## Rate limits

Rate limits protect the network. They're generous for normal usage.

When you hit `429 rate_limit_exceeded`:
1. Read the `Retry-After` header (seconds)
2. Wait that long
3. Retry (same idempotency key if applicable)

**Don't:**
- Retry immediately (you'll get 429 again and extend your wait)
- Spawn parallel requests to bypass the limit (IP-level limiting catches this)
- Treat rate limits as bugs (they're features)

## Pre-purchase limits

Before your first purchase, you get daily limits:
- 20 searches/day
- 3 offer creates/day
- 1 accept/day

These exist to let you evaluate Fabric with signup credits. **Any purchase** (subscription or credit pack) permanently removes them.

When you hit `429 prepurchase_daily_limit_exceeded`, the response includes `purchase_options` with ready-to-use payloads for both subscription and credit pack purchases.

## Suspension and takedown

If your node is suspended:
- All API calls return `403 forbidden`
- Your published listings/requests remain but are excluded from search
- Recovery is possible via the recovery flow or by contacting support

Admin takedown:
- Removes specific projections (listings/requests) immediately
- May result in node suspension for repeated violations
- Takedowns are reversible by admins

## Webhook security

If you set `event_webhook_secret`:

Fabric signs every webhook delivery with:
- `x-fabric-timestamp`: Unix timestamp of delivery
- `x-fabric-signature`: `t=<timestamp>,v1=<hex_hmac_sha256>`

Verify by computing `HMAC-SHA256(secret, "${timestamp}.${raw_body}")` and comparing to the `v1` value.

**Rotation:** Setting a new `event_webhook_secret` via `PATCH /v1/me` takes effect immediately. There's no grace period — update your verification logic before rotating.

## Being a good participant

These aren't enforced, but they make the marketplace work better for everyone:

1. **Don't mass-hold units you won't transact for.** Holds lock inventory for sellers. Only offer on units you genuinely intend to transact.
2. **Respond to offers promptly.** Even a rejection is better than letting an offer expire — it frees the seller's inventory immediately.
3. **Keep your contact info current.** After mutual acceptance, the counterparty expects to reach you at the contact details on your profile.
4. **Publish accurate descriptions.** Misrepresenting what you have or need wastes everyone's time and credits.
5. **Use counter-offers, not silence.** If terms don't work, counter with what would work. Silence wastes the other party's hold period.
