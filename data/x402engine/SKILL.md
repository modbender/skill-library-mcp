---
name: x402engine
description: Pay-per-call API gateway skill — calls 63 APIs (LLMs, image/video gen, flights, hotels, crypto, web search) via x402 micropayments. Each call costs $0.001-$0.60 in USDC/USDm, enforced by a local policy engine with spend caps.
version: 1.3.2
metadata:
  openclaw:
    requires:
      env:
        - EVM_PRIVATE_KEY
      bins:
        - node
    primaryEnv: EVM_PRIVATE_KEY
    emoji: "⚡"
    homepage: https://x402engine.app
    install:
      - kind: node
        package: "@x402/fetch"
        bins: []
      - kind: node
        package: "@x402/evm"
        bins: []
      - kind: node
        package: "viem"
        bins: []
---

# x402engine

Call 63 paid APIs via x402 micropayments. Each API call costs between $0.001 and $0.60, paid with USDC on Base/Solana or USDm on MegaETH.

## What this skill does

This skill signs and submits stablecoin micropayments to call remote APIs on the user's behalf. It uses the EVM_PRIVATE_KEY environment variable to sign on-chain payment transactions. Each call deducts a small amount from the wallet.

**Cost transparency:** When presenting results, include the cost of the call (e.g. "Bitcoin is $97,500 (cost: $0.001)"). If the user asks about spending, show full budget breakdown.

## Triggers
- "what's the price of bitcoin"
- "ethereum price"
- "show me trending crypto"
- "generate an image of a sunset"
- "run this python code"
- "transcribe this audio"
- "wallet activity of vitalik.eth"
- "ask gpt to explain x402"
- "scrape this url"
- "pin this to ipfs"
- "resolve vitalik.eth"
- "flights from JFK to LAX"
- "search hotels in Paris"
- "find cheap flights to Tokyo"
- "how much budget is left"
- "list available services"

## How it works
1. Fetch cached service catalog from discovery endpoint (default: https://x402engine.app/.well-known/x402.json).
2. Score query against 63 service descriptions to find best match.
3. Run policy preflight — check per-tx caps, daily caps, and recipient allowlist before signing.
4. Call service via @x402/fetch — handles 402 payment flow automatically.
5. Return structured data to the agent for natural-language presentation.

## Rules
- Present results naturally. Include the cost of each call so the user knows what was spent.
- If a payment fails due to insufficient funds, tell the user: "I need funds to access this service. Add USDC to your wallet to continue."
- If no matching service is found, say so plainly — don't expose internal routing details.
- Policy limits are authoritative — do not bypass spend caps or recipient allowlists.
- Keep all decisions explainable with reason codes internally.

## Security

### Required credential
- **EVM_PRIVATE_KEY** (required) — signs payment transactions. Use a dedicated wallet with limited funds — never your primary wallet. If not set, an ephemeral key is generated (no real funds, no payments possible).

### Optional configuration
These environment variables are NOT required. They provide additional controls:
- **EVM_PRIVATE_KEY_FILE** — alternative to EVM_PRIVATE_KEY; reads the key from a file instead of an env var. Use one or the other, not both.
- **X402_POLICY_PATH** — path to a JSON policy file. Defines per-transaction caps, daily spending limits, and a recipient allowlist. Without this, no spending limits are enforced beyond the wallet's on-chain balance. When configured, the engine is fail-closed: if the file is missing or invalid, all payments are denied.
- **X402_STATE_PATH** — path to a JSON file tracking daily spend and rate-limit state. Defaults to `.x402engine-state.json`.
- **X402_DISCOVERY_URL** — override the service catalog URL (default: `https://x402engine.app/.well-known/x402.json`). Use a self-hosted catalog if you don't trust the default.
- **X402_AUTOPREFLIGHT** — set to `false` to skip policy preflight checks. Enabled by default.
- **X402_DISCOVERY_REFRESH_MS** — cache TTL for the service catalog in milliseconds.

### How payments work
All payments go to the `payTo` address declared in the service catalog. The catalog is fetched from the discovery URL above. If you want to restrict which addresses can receive payments, configure a policy file with a recipient allowlist.

## Budget check
When the user asks "how much budget is left" or similar:
- Load policy and state files.
- Show daily cap remaining per chain/asset if caps are enabled.
- Show rate limit status.
- Show wallet balance.

## Dependencies
This skill requires Node.js and the following npm packages (declared in package.json):
- `@x402/fetch` — x402 payment-aware fetch wrapper
- `@x402/evm` — EVM payment scheme (Permit2 signatures)
- `viem` — Ethereum client library

Install with: `cd skills/x402engine && npm install`

## Reason Codes
- `POLICY_MISSING`, `POLICY_INVALID`
- `CHAIN_DENIED`, `ASSET_DENIED`, `RECIPIENT_DENIED`
- `PER_TX_EXCEEDED`, `DAILY_CAP_EXCEEDED`, `RATE_LIMITED`
- `ACTION_DENIED`
- `SERVICE_NOT_FOUND`
- `WALLET_UNDERFUNDED`
