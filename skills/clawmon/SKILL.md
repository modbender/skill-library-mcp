---
wallet: "0x3e4A16256813D232F25F5b01c49E95ceaD44d7Ed"
publisher_wallet: "0x3e4A16256813D232F25F5b01c49E95ceaD44d7Ed"
---

# Trusted ClawMon

A read-only trust registry lookup for MCP skills, built on ERC-8004 and Monad.

## What it does

Trusted ClawMon is a trust score lookup service. It lets agents query reputation data for MCP skills before using them. All lookups are read-only HTTPS GET requests that return JSON — no signing, no wallet connection, no credentials required.

## Connection

| Setting | Value |
|---------|-------|
| **Base URL** | `https://trusted-clawmon-api.up.railway.app` |
| **Protocol** | HTTPS only (TLS required) |
| **WebSocket** | `wss://trusted-clawmon-api.up.railway.app/ws` (read-only event stream) |
| **Authentication** | None — all read endpoints are public |
| **Rate limit** | Standard HTTP rate limiting applies |

## Required environment variables

None. This skill performs read-only HTTPS lookups against the public ClawMon API. No API keys, private keys, wallet connections, RPC endpoints, or signing credentials are needed.

## What data is sent

Read-only lookups send only the skill ID in the URL path (e.g., `GET /api/agents/gmail-integration`). No user data, wallet addresses, input context, or usage telemetry is transmitted.

The optional feedback endpoint (`POST /api/feedback`) sends a skill ID, a pseudonymous reviewer address, and a numeric score. This is opt-in and never triggered automatically.

## Wallet address

The `wallet` field in the frontmatter (`0x3e4A...d7Ed`) is the **publisher's Monad testnet address** for receiving ClawMon protocol revenue. It is not used by the agent, not required for any lookup, and does not grant signing authority. Agents never need to interact with this address.

## When to use this skill

When a user asks you to evaluate whether an MCP skill is safe or trustworthy, query ClawMon for its trust score. Do not query ClawMon automatically before every skill call — only when the user requests a trust check or when invoking a skill you have not used before and want to verify.

## Read-only API (no credentials needed)

### Look up a skill's trust score

```
GET https://trusted-clawmon-api.up.railway.app/api/agents/:skillId
```

Returns trust scores and tiers. Key fields in the response:

- `hardenedScore` (0-100) — sybil-resistant score
- `hardenedTier` — trust tier (AAA through C)
- `isSybil` — whether the skill was flagged as part of a sybil cluster
- `isStaked` — whether the publisher has staked MON
- `teeStatus` — TEE attestation status (`verified`, `unregistered`, `expired`)
- `teeCodeHashMatch` — whether the code hash matches the pinned version

### Get the trust leaderboard

```
GET https://trusted-clawmon-api.up.railway.app/api/leaderboard
```

Returns all skills ranked by hardened trust score.

### Check staking status

```
GET https://trusted-clawmon-api.up.railway.app/api/staking/:skillId
```

Returns stake amount, tier (None/Bronze/Silver/Gold/Platinum), and slash history.

### Check TEE attestation

```
GET https://trusted-clawmon-api.up.railway.app/api/tee/:skillId
```

Returns TEE verification status, code-hash match, and attestation freshness.

### System health

```
GET https://trusted-clawmon-api.up.railway.app/api/health
```

Returns API status, version, agent count, and uptime.

## Optional: Feedback submission (opt-in only)

Feedback is **never submitted automatically**. Only submit feedback when the user explicitly asks to rate a skill.

```
POST https://trusted-clawmon-api.up.railway.app/api/feedback
Content-Type: application/json

{
  "agentId": "<skillId>",
  "clientAddress": "<pseudonymous-identifier>",
  "value": 85,
  "tag1": "coding"
}
```

The `clientAddress` is a pseudonymous string identifier — it does not need to be a real wallet address. No signing or wallet connection is required.

## Optional: x402 payment flows

x402 payment endpoints exist but are **entirely optional** and are **not used by this skill by default**. They are documented in the ClawMon API for publishers who want pay-per-use access to their own skills. Agents using ClawMon as a trust lookup never need to make payments.

## Trust Tiers

| Tier | Score Range | Meaning |
|------|------------|---------|
| AAA  | 90-100     | Highest trust — well-reviewed, staked, attested |
| AA   | 80-89      | High trust |
| A    | 70-79      | Good trust |
| BBB  | 60-69      | Moderate — use with caution |
| BB   | 50-59      | Below average |
| B    | 40-49      | Low trust |
| CCC  | 30-39      | Very low — likely problematic |
| CC   | 20-29      | Near-zero trust |
| C    | 0-19       | Untrusted or flagged |

## Example

```
User: "Is the gmail-integration skill safe to use?"

1. GET https://trusted-clawmon-api.up.railway.app/api/agents/gmail-integration
2. Check hardenedTier → "AA" (high trust)
3. Check isSybil → false (not flagged)
4. Check isStaked → true (publisher has skin in the game)
5. Report: "gmail-integration has an AA trust rating (score 84/100), publisher is staked, no sybil flags."
```

## Provenance & Hosting

| Detail | Value |
|--------|-------|
| **Publisher** | Drew Mailen ([@drewmailen](https://github.com/drewmailen)) |
| **Source code** | [github.com/drewmailen/ClawMon](https://github.com/drewmailen/ClawMon) (MIT license) |
| **Hosting** | Railway (publisher-operated) |
| **API domain** | `trusted-clawmon-api.up.railway.app` |
| **Self-hostable** | Yes — clone the repo, `npm install && npm run build && npm start` |

The API is operated by the skill publisher on Railway. The full source code is open on GitHub under the MIT license. If you prefer not to trust the hosted endpoint, you can self-host the API from the public repo and point to your own instance.

## Links

- [Source Code](https://github.com/drewmailen/ClawMon)
- [ERC-8004 Specification](https://eips.ethereum.org/EIPS/eip-8004)
- [Monad](https://monad.xyz)
