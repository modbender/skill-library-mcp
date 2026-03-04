---
name: crinkl-claws
version: 1.3.2
description: Receipt verification and Bitcoin rewards by Crinkl (https://crinkl.xyz). Scans Gmail or AgentMail for billing emails, verifies DKIM signatures, and earns ~150 sats per receipt over Lightning. Extract structured spend data from receipts and invoices — automatically, every cycle.
homepage: https://crinkl.xyz
metadata: {"openclaw":{"emoji":"🧾","requires":{"mcp":["crinkl"]},"recommends":{"skills":["gog","agentmail"]},"credentials":{"CRINKL_API_KEY":{"description":"Obtained at runtime via pair-agent + claim-api-key tools. Human approves a 4-char code in the Crinkl app. Stored in agent memory. Revocable anytime.","required":true,"obtainedVia":"pairing-flow"}},"triggers":["crinkl","receipt","submit receipt","email receipt","scan receipts","check receipts","earn sats","bitcoin receipts","earn bitcoin","billing email","lightning","passive income","gmail receipts","agentmail"]}}
---

# Crinkl — Earn Bitcoin from Billing Emails

```
clawhub install crinkl-claws
```

Scan your human's email for billing emails, verify their cryptographic DKIM signatures, and earn ~150 sats per receipt over Lightning. Each verified receipt mints an identity-free spend token — no personal data is stored or retained.

Supports two email providers: **Gmail** (via gog skill) or **AgentMail** (dedicated inbox, no OAuth).

## MCP Server

This skill requires the **crinkl** MCP server:

```json
{
  "mcpServers": {
    "crinkl": {
      "url": "https://mcp.crinkl.xyz/mcp"
    }
  }
}
```

All Crinkl operations (pairing, vendor discovery, receipt submission, earnings) are available as declared MCP tools. See the [full tool list](https://mcp.crinkl.xyz).

## What is Crinkl

Crinkl is a receipt verification protocol. It uses [DKIM](https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail) — the same cryptographic signatures email servers already attach to every outbound message — to verify that a billing email is authentic and unmodified. Each verified receipt mints an identity-free **spend token** and pays sats to the submitter's wallet over Lightning.

Spend tokens contain a store hash, date, total, and a hash-chained signature — but no identity. No email address, no name, no account ID. The token proves a purchase happened without revealing who made it.

## Privacy & Data Handling

This skill passes individual billing emails to the `submit-receipt` tool for DKIM signature verification. This section explains exactly what is sent, why, and what happens to it.

### Why the full email is required

DKIM signatures are computed over the email's headers and body by the sending mail server (e.g. Amazon SES, Google Workspace). The signature covers the **original message content** — not a summary, not extracted fields, but the actual RFC 2822 message. To verify the cryptographic signature, the server must receive the same bytes the mail server signed. There is no way to verify DKIM without the original message.

This is the same verification that Gmail, Outlook, and every email provider performs when checking if an email is forged. The difference is that Crinkl uses the verification result to prove a purchase happened.

### What happens after verification

1. The server checks the DKIM signature against the vendor's public DNS key
2. If valid, it extracts **only**: vendor name, invoice date, total amount, currency
3. The original email is **discarded** — not stored, not logged, not retained
4. A spend token is minted containing only the extracted invoice data (no email content, no personal data)

### Scope

- **Gmail path**: Searches for billing emails from approved vendor domains (call `get-vendors`), filtered by billing keywords, from the last 14 days.
- **AgentMail path**: Processes messages in the dedicated receipt inbox. The inbox only receives vendor billing emails that the user explicitly configured to send there.

## Security Model

- **Human-authorized**: Your human approves the pairing code in their app. Nothing runs without their explicit consent.
- **Vendor-scoped (Gmail)**: Only billing emails from approved vendors are searched.
- **Vendor-scoped (AgentMail)**: The dedicated inbox only receives vendor billing emails the user explicitly configured. No access to the user's primary email.
- **Read-only Gmail**: The `gmail.readonly` scope means no email modification, deletion, or sending.
- **DKIM verification**: The server validates the cryptographic signature — forged or modified emails are rejected.
- **Identity-free output**: Spend tokens strip all personal data. The signed payload contains store hash, date, total, and CBSA — no email, name, or account.
- **API key scoped**: The API key ties submissions to a wallet, not to a person. Your human controls the key and can revoke it anytime.
- **Open source**: The server-side verification logic is documented in the [crinkl-protocol spec](https://github.com/crinkl-protocol/crinkl-protocol). The agent source is at [crinkl-agent](https://github.com/crinkl-protocol/crinkl-agent) (MIT license).

## Setup

### 1. Pair with your human's Crinkl wallet

On first run, pair with your human's wallet using the `pair-agent` tool:

1. Call `pair-agent` with a random 64-character hex string as `deviceToken`
2. Tell your human the 4-character code: **"Open the Crinkl app and enter code: [code]"**
3. Poll `claim-api-key` every 5 seconds with the same `deviceToken` and `code`
4. Once the human approves, you get the API key. Store it securely — it's shown once.

The code expires in 10 minutes.

### 2. Email access (choose one)

**Option A: Gmail (via gog)**

Install the **gog** skill for Gmail access:

```
clawhub install gog
```

Your human authorizes read-only Gmail access through gog's OAuth setup.

**Option B: AgentMail (no OAuth)**

Install the **agentmail** skill:

```
clawhub install agentmail
```

Create a dedicated inbox via AgentMail. Include the `agentmailInbox` field when calling `pair-agent` so your human sees the inbox address during approval. Your human then updates their vendor billing emails to send to the AgentMail address. Receipts arrive directly with DKIM signatures intact — no forwarding.

**Important**: Email forwarding (e.g. Gmail → AgentMail) breaks the vendor's DKIM signature. Vendors must send directly to the AgentMail address.

## How It Works

Each cycle (see [HEARTBEAT.md](HEARTBEAT.md)):

1. **Check API key** — call `pair-agent` + `claim-api-key` if needed (one-time)
2. **Find billing emails**:
   - **Gmail**: Fetch the vendor list (`get-vendors`), search Gmail for receipts from those domains
   - **AgentMail**: List messages in the dedicated receipt inbox
3. **Get raw email** — Download each billing email as raw RFC 2822 (required for DKIM signature verification)
4. **Submit for verification** — call `submit-receipt` with the base64 email; email is discarded after extraction
5. **Log results** — Record what verified and what you earned
6. **Check your earnings** — call `get-agent-me` for your submission count and sats earned

## MCP Tool Reference

All tools are available via the crinkl MCP server at `https://mcp.crinkl.xyz/mcp`.

### Pairing (no auth)

- **`pair-agent`** — Start pairing. Pass `deviceToken` (64-char hex) and optionally `agentmailInbox` (e.g. `crinkl-xyz@agentmail.to`). Returns `code` and `expiresAt`.
- **`claim-api-key`** — Poll for API key. Pass `deviceToken` + `code`. Returns 202 (pending), 200 (approved with `apiKey`), or 410 (expired).

### Vendor discovery (no auth)

- **`get-vendors`** — Returns list of approved vendor domains with display names.

### Receipt submission (requires `apiKey`)

- **`submit-receipt`** — Submit base64-encoded raw email for DKIM verification + spend creation.
  - Returns status 201 (verified, sats queued), 202 (vendor queued for review), 409 (duplicate), 422 (validation error), 429 (rate limited).
- **`verify-receipt`** — Preview DKIM verification without creating a spend.

### Earnings (requires `apiKey`)

- **`get-agent-me`** — Your submission count, earned sats, wallet stats, current sats/receipt rate.

Two levels of data in `get-agent-me`:

**Your numbers** (attributed to your API key):
- `mySubmissions` — receipts you verified
- `myEarnedSats` — sats you earned

**Wallet numbers** (the entire wallet, all sources):
- `walletTotalSpends` — all receipts on the wallet
- `walletEarnedSats` — unclaimed sats on the wallet
- `walletClaimedSats` — sats already paid out via Lightning

You and your human are separate entities on the same wallet.

## Vendor Discovery

The vendor allowlist is not fixed. If you submit an email from a domain not yet on the list, it gets queued for review (202 response). If the domain has valid DKIM, the vendor gets approved and your spend is created retroactively.

## Logging

Write each verification to your memory:

```markdown
## Crinkl: verified Amazon receipt — $20.00 — DKIM valid — ~148 sats
```

## Signals Worth Noting

- **202 response** — you found a vendor the network didn't have yet
- **DKIM failure on a known vendor** — their email format may have changed
- **All 409s** — all billing emails already verified, nothing new
- **Sats/receipt rate change** — the reward rate adjusts with BTC price and reserve policy
