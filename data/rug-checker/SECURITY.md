# Security Model — Rug Checker

## Overview

Rug Checker is a **read-only analysis tool**. It queries public APIs and renders risk reports. It has no capability to interact with wallets, sign transactions, or modify any on-chain state.

## Threat Model

### What This Tool CAN Do

- Read publicly available on-chain data from Solana mainnet
- Query public REST APIs (Rugcheck.xyz, DexScreener)
- Format and display data as text reports
- Write temporary files to the system's temp directory (for HTTP responses)

### What This Tool CANNOT Do

- ❌ Access, create, or import any wallet
- ❌ Sign or submit any transaction
- ❌ Request or process private keys or seed phrases
- ❌ Send tokens, SOL, or any value
- ❌ Interact with smart contracts in any write capacity
- ❌ Store or transmit API keys (none are used)
- ❌ Access user files outside the skill directory
- ❌ Phone home or transmit telemetry

## API Data Sources

### Rugcheck.xyz (`api.rugcheck.xyz`)

| Aspect | Detail |
|--------|--------|
| Auth | None (public API) |
| Data accessed | Token risk reports, holder analysis, LP lock data |
| HTTPS | Yes (TLS) |
| Rate limits | Undocumented; no rate-limit headers observed |
| Privacy | No user data transmitted; only token mint addresses in URL path |

### DexScreener (`api.dexscreener.com`)

| Aspect | Detail |
|--------|--------|
| Auth | None (public API) |
| Data accessed | Token market data, pricing, liquidity, search |
| HTTPS | Yes (TLS) |
| Rate limits | 300 req/min (documented) |
| Privacy | Search queries and token addresses in URL; no user data |

### Solana RPC (`api.mainnet-beta.solana.com`)

| Aspect | Detail |
|--------|--------|
| Auth | None (public endpoint) |
| Data accessed | Mint account info (authorities, supply) |
| HTTPS | Yes (TLS) |
| Rate limits | Aggressive on some methods (429 responses handled) |
| Privacy | Only token addresses transmitted in JSON-RPC requests |

## Known Trust Boundaries

### SOLANA_RPC_URL Override

The `SOLANA_RPC` endpoint defaults to the public Solana mainnet-beta RPC (`https://api.mainnet-beta.solana.com`) but can be overridden via the `SOLANA_RPC_URL` environment variable. A malicious value could point to a server that returns fake mint authority data (e.g., claiming mint authority is revoked when it isn't).

**Mitigation:** The tool cross-references Rugcheck.xyz data with on-chain RPC data. For an RPC spoofing attack to succeed, Rugcheck would also need to be compromised or return consistent false data. Users who override `SOLANA_RPC_URL` should only point to trusted RPC endpoints (e.g., their own node, Helius, QuickNode, etc.).

## Local State

The skill writes a small rate-limiting state file to:
```
${XDG_STATE_HOME:-$HOME/.local/state}/cacheforge/rate_limits
```

This file contains only timestamps and API domain names (e.g., `dexscreener|1739584200`). No token data, user data, or API responses are persisted.

## Network Security

- All API calls use HTTPS (TLS)
- No custom certificates or certificate pinning
- User-Agent header: `CacheForge-DeFi-Stack/0.1.2`
- No cookies or session tokens

## Supply Chain

The skill has zero runtime dependencies beyond standard Unix tools:
- `bash` (system shell)
- `curl` (HTTP client)
- `jq` (JSON processor)
- `bc` (calculator)

No npm packages, no pip packages, no compiled binaries, no third-party scripts.

## ⚠️ NOT Financial Advice

This tool provides **informational risk signals only**. It does NOT:

- Recommend buying or selling any token
- Guarantee that any token is safe or unsafe
- Replace professional financial advice
- Account for off-chain risks (team reputation, legal, regulatory)
- Detect all possible scam vectors (novel attack patterns may not be covered)

Risk scores are algorithmic estimates based on on-chain data available at the time of analysis. On-chain conditions can change at any time.

**Always Do Your Own Research (DYOR).**

CacheForge is not responsible for any financial losses incurred based on information provided by this tool.
