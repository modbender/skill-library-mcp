---
name: bloomfilter
description: Search, register, and manage domains via Bloomfilter x402 API - pay with USDC on Base
homepage: https://bloomfilter.xyz
metadata:
  clawdbot:
    emoji: 🌐
    requires:
      env:
        - EVM_PRIVATE_KEY
    primaryEnv: EVM_PRIVATE_KEY
---

# Bloomfilter - Domain Registration API

Base URL: `https://api.bloomfilter.xyz`

Paid endpoints use the x402 payment protocol. The API returns HTTP 402 with payment details - your x402-compatible HTTP client handles payment automatically.

EVM_PRIVATE_KEY is used locally by the agent's x402 HTTP client (@x402/axios or @x402/fetch) to sign EIP-3009 TransferWithAuthorization messages for USDC payments and to sign EIP-4361 SIWE messages for authentication. The private key never leaves the local machine and is never sent to any server. All cryptographic signing happens client-side in the agent runtime.

DNS and account endpoints require authentication via SIWE (Sign-In With Ethereum). Authenticate once, then pass the JWT as a Bearer token.

## Authentication (SIWE)

GET /auth/nonce
-> Returns { nonce, domain, uri, chainId, version, expiresIn }

POST /auth/verify
Body: { "message": "<EIP-4361 SIWE message>", "signature": "0x..." }
-> Returns { accessToken, refreshToken, walletAddress }

POST /auth/refresh
Body: { "refreshToken": "..." }
-> Returns new { accessToken, refreshToken }

POST /auth/revoke (requires Bearer token)
-> Revokes all sessions for the authenticated wallet

## Domain Search & Pricing (free, no auth)

GET /domains/search?query=example&tlds=com,io,xyz
-> Returns availability and pricing for each TLD. The tlds parameter is optional.

GET /domains/pricing
-> Returns pricing for all supported TLDs

GET /domains/pricing/:tld
-> Returns pricing for a single TLD (e.g., /domains/pricing/com)

## Domain Registration (x402 - dynamic pricing)

POST /domains/register
Body: { "domain": "example.com", "years": 1 }
years defaults to 1 if omitted.
Optional: "dns_records": [{ "type": "A", "host": "@", "value": "1.2.3.4" }]
Supported dns_records types: A, AAAA, CNAME, MX, TXT, SRV, CAA
Each record also accepts optional "ttl" (300-86400, default 3600) and "priority" (for MX/SRV)
-> First call returns 402 with exact price. Retry with x402 payment to complete.
-> Returns 201 on success, or 202 with a job ID for async provisioning.

POST /domains/renew
Body: { "domain": "example.com", "years": 1 }
years defaults to 1 if omitted.
-> Same two-phase x402 flow as registration.

## Domain Info (free, no auth)

GET /domains/:domain
-> Returns domain status, expiry, nameservers, lock/privacy state.
Note: Only works for domains registered through Bloomfilter.

## Job Status (free, no auth)

GET /domains/status/:jobId
-> Poll for async registration status. Returns 200 (done), 202 (pending), or 500 (failed).

## DNS Management (requires Bearer token)

Mutations cost $0.10 USDC each (x402). Listing is free.

IMPORTANT: Always add, update, or delete DNS records one at a time (sequentially, not in parallel). After registering a new domain, wait at least 30 seconds before adding DNS records — the DNS zone may not be ready immediately.

GET /dns/:domain
-> List all DNS records

POST /dns/:domain
Body: { "type": "A", "host": "@", "value": "1.2.3.4" }
Optional: "ttl" (300-86400, default 3600), "priority" (for MX/SRV)
Supported types: A, AAAA, CNAME, MX, TXT, NS, SRV, CAA

PUT /dns/:domain/:recordId
Body: { "host": "@", "value": "5.6.7.8" }
At least one field required. Optional: host, value, ttl, priority.

DELETE /dns/:domain/:recordId
-> Deletes the record

## Account (requires Bearer token, free)

GET /account
-> Account summary (wallet, domain count, total spent)

GET /account/domains?limit=50&offset=0
-> Paginated list of owned domains

GET /account/transactions?limit=50&offset=0
-> Paginated transaction history

## Notes

- All paid requests require an x402-compatible HTTP client with USDC on Base (chain ID 8453)
- WHOIS privacy is enabled by default on all registrations
- Docs: https://docs.bloomfilter.xyz

## External Endpoints

| URL                           | Data Sent                                   | Purpose                                     |
| ----------------------------- | ------------------------------------------- | ------------------------------------------- |
| https://api.bloomfilter.xyz/* | Domain queries, DNS records, wallet address | Domain search, registration, DNS management |

No data is sent anywhere else. All requests go to the Bloomfilter API only.

## Security & Privacy

- Your EVM_PRIVATE_KEY never leaves your local machine — it is used locally to sign x402 payment authorizations and SIWE messages
- The API receives your wallet address (derived from the key) but never the private key itself
- WHOIS privacy is enabled by default on all registrations — your identity is never exposed in public WHOIS records
- All API communication is over HTTPS

## Trust

This skill connects to `api.bloomfilter.xyz` to register ICANN domains and manage DNS records. Payments are made in USDC on Base via the x402 protocol. Your private key stays local. Install only if you trust Bloomfilter (https://bloomfilter.xyz) as a domain registration provider.
