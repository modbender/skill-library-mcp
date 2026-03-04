# Crinkl Heartbeat

*Run each cycle. Find billing emails, verify DKIM signatures, submit to earn sats.*

## Step 0: Check API key

If you don't have `CRINKL_API_KEY` stored in your memory, pair with your human's wallet first.

### Pairing flow (one-time)

Generate a random 64-character hex string as your `deviceToken`. Store it — you'll need it to claim the key.

1. Call `pair-agent` with your `deviceToken`. If using AgentMail, also pass `agentmailInbox` (e.g. `crinkl-xyz@agentmail.to`) — the human will see this address when approving.
   - Returns `code` (4 characters) and `expiresAt`.

2. Tell your human:

> Open the Crinkl app and enter code: **[code]**

3. Poll `claim-api-key` every 5 seconds with your `deviceToken` and `code`:
   - **202** — human hasn't approved yet. Keep polling.
   - **200** — contains `apiKey` (starts with `crk_`). Store this as your `CRINKL_API_KEY`. Shown once.
   - **410** — code expired (10 min). Start over.

Once you have the key, store it and never run step 0 again.

## Step 1: Find billing emails

Choose the path that matches your email provider.

### Path A: Gmail (via gog)

First, fetch the vendor list: call `get-vendors`. Extract the `domain` field from each vendor. These are the only domains you will search for.

Before using any vendor domain, validate that it matches a strict domain pattern: letters, digits, hyphens, and dots only (e.g. `amazon.com`, `openai.com`). Discard any domain containing spaces, quotes, parentheses, or shell metacharacters.

Search your human's Gmail for receipts from those vendors using the Gmail API (via the gog skill's search tool or equivalent).

Build a Gmail search query string from the validated vendor domains:

```
from:(@amazon.com OR @openai.com OR @stripe.com OR @suno.com) subject:(receipt OR invoice OR order OR payment OR confirmation OR billing) newer_than:14d
```

Pass this query string to the Gmail search API. Request up to 50 results.

If no results, skip to step 4 (check earnings).

### Path B: AgentMail

Use the agentmail skill to list messages in your dedicated receipt inbox from the last 14 days. This inbox only receives vendor billing emails your human explicitly configured to send there. Submit each message for DKIM verification.

If no messages, skip to step 4 (check earnings).

## Step 2: Get the raw email

For each message from step 1, you need the **raw RFC 2822 email** — DKIM signatures are computed over the original message bytes.

### 2a. Skip already-submitted emails

Track message IDs you've already submitted in your memory. Skip any ID you've seen before.

### 2b. Download raw email

**Gmail**: Use the Gmail API to fetch the message by ID in raw format (RFC 2822).

**AgentMail**: Use the agentmail skill to get the raw message content for each email. The raw RFC 2822 bytes are required for DKIM verification.

### 2c. Encode for submission

The raw email must be submitted as **standard base64**. If the email content is returned as base64url (common in Gmail API responses), convert it:
- Replace `-` with `+`
- Replace `_` with `/`
- Pad with `=` to make length a multiple of 4

If the content is returned as plain text (raw RFC 2822), base64-encode it.

## Step 3: Submit for DKIM verification

Call `submit-receipt` with your `apiKey` and the base64-encoded `eml`.

### Handle the response

**Status 201 — DKIM verified.** Spend token minted, sats queued. Mark message ID as submitted.
```markdown
## Crinkl: verified [store] receipt — $[totalCents/100] — DKIM valid — ~[satsPerReceipt] sats
```
The response has `data.store`, `data.totalCents`, `data.date`, `data.dkimDomain`.

**Status 202 — Vendor queued.** Domain not on allowlist yet. Do NOT mark as submitted — retry next cycle. The vendor will be approved if DKIM is valid.

**Status 409 — Duplicate.** Already submitted. Mark as submitted. Skip.

**Status 422 — Validation failed.** DKIM signature invalid, email too old, or no invoice amount found. Mark as submitted (don't retry).

**Status 429 — Rate limited.** Stop. Retry next cycle.

## Step 4: Check your earnings

Call `get-agent-me` with your `apiKey`.

**Your numbers (per API key):**
- `mySubmissions` — receipts you verified via this API key
- `myEarnedSats` — sats you earned

**Wallet numbers (your human + all agents on the wallet):**
- `walletUsername` — your operator's wallet name
- `walletTotalSpends` — all receipts on the wallet
- `walletEarnedSats` — unclaimed sats on the wallet
- `walletClaimedSats` — sats already paid out via Lightning
- `satsPerReceipt` — current rate

Your submissions are tracked independently from your human's via your API key.

## Step 5: Log results

```markdown
## Crinkl: verified 2 Amazon receipts ($20.00 each) — DKIM valid — ~296 sats
```

If nothing new:
```markdown
## Crinkl: no new billing emails. 28 lifetime verified, ~4,144 sats.
```

## Step 6: Note anything unusual

- **Vendor list changed** — new vendors mean new billing emails to find
- **Sats/receipt rate changed** — reward rate adjusts with BTC price and reserve policy
- **202 response** — you discovered a vendor not yet on the allowlist
- **DKIM failure on known vendor** — their email format may have changed
