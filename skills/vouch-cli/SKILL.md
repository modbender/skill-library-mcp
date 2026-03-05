---
name: vouch-cli
description: >-
  Signs, verifies, and manages cryptographic identity for AI agents using the
  Vouch CLI on Base. Use when an agent needs to: set up identity and register
  an account; link social identities via X, GitHub, or DNS; cryptographically
  sign outbound messages with EIP-712 envelopes; verify inbound signed messages
  against onchain identity records; send verified messages to other agents;
  receive and process incoming verified messages; scaffold, test, and deploy
  OpenAI-powered agents; look up agents by identity or capability; manage
  runtime key delegations and trust allowlists; manage account usage, API keys,
  and billing; or publish agent endpoints to the onchain directory.
compatibility: Requires the vouch binary on PATH and jq for JSON processing
allowed-tools: Bash(vouch:*) Bash(jq:*)
metadata:
  author: vouch
  version: "1.0.0"
---

# Vouch CLI

Vouch provides verifiable identity for AI agents on Base. Agents create an identity wallet, connect a social account (X or GitHub) to create their API account, optionally link additional identities (including DNS), and delegate short-lived runtime keys. Messages are signed as EIP-712 envelopes and verified against the VouchHub smart contract via direct RPC reads.

```
Account (OAuth + API key) ──manages──> Wallet (identity)
                                            │
       ┌────────────────────────────────────┤
       ▼                                    ▼
  Linked Identities                  Runtime Key (delegated, scoped)
  (X, GitHub, DNS)                         │
                                           └──sign──> Envelope (EIP-712)
                                                           │
                              Recipient ──verify──> VouchHub (RPC)
                                                           │
                                                    ✓ signer → wallet → linked identities
```

## Install

```bash
curl -fsSL https://vouch.directory/install.sh | bash
```

Verify: `vouch --version`

## Global flags

- `--json` — JSON output (auto-enabled when piped)
- `--config <path>` — Config file (default `~/.vouch/config.toml`)
- `--network <base-sepolia|base>` — Network override

## Onboarding

### Full setup wizard

`vouch init` walks through complete onboarding: generate a wallet, connect a social account (X or GitHub) which creates your API account and links your identity, then delegate a runtime key.

```bash
vouch init
```

The init flow:
1. **Generate wallet** — creates a new identity keypair stored locally at `~/.vouch/keys/`
2. **Save config** — writes `~/.vouch/config.toml` with network defaults
3. **Connect account** — opens browser for X or GitHub OAuth, which creates your API account (provides API key) and links your identity on-chain
4. **Delegate runtime key** — creates a 24-hour signing key for your agent

Re-initialize an existing setup:

```bash
vouch init --force
```

This is the recommended first command. It handles everything needed to start signing and verifying messages.

### Log in on a new machine

Set an existing API key:

```bash
vouch login --api-key vk_...
```

**Flags:** `--api-key <vk_...>` (required). Validates against the API before saving.

## Link identities

Vouch supports three identity providers. Each links a social account or domain to your onchain wallet.

### Link X (Twitter)

Interactive mode opens the browser for OAuth:

```bash
vouch link-x
```

Pipe mode for scripting:

```bash
vouch --json link-x --wallet-key 0xKEY --attestation '{"provider":1,...}'
```

**Flags:** `--wallet-key <hex>`, `--attestation <json>`

### Link GitHub

```bash
vouch link-github
```

Pipe mode:

```bash
vouch --json link-github --wallet-key 0xKEY --attestation '{"provider":2,...}'
```

**Flags:** `--wallet-key <hex>`, `--attestation <json>`

### Link a domain via DNS

Link a domain to your wallet. Requires an existing API account (created via `vouch init`), since DNS alone cannot verify user identity for account creation.

Interactive mode requests a DNS challenge, shows the TXT record to add, then verifies:

```bash
vouch link-dns
```

Pipe mode:

```bash
vouch --json link-dns --wallet-key 0xKEY --domain example.com
```

**Flags:** `--wallet-key <hex>`, `--domain <domain>`

### Revoke a linked identity

```bash
vouch --json revoke-link --wallet-key 0xKEY --provider x
```

**Flags:** `--wallet-key <hex>` (required), `--provider <x|github|dns>` (required)

## Sign outbound messages

Wrap any JSON payload in a signed EIP-712 envelope:

```bash
vouch --json sign --payload '{"msg":"hello from agent"}'
```

Pipe payload via stdin:

```bash
echo '{"task":"summarize","doc_id":"abc"}' | vouch --json sign
```

With explicit runtime key and custom expiry:

```bash
vouch --json sign --key 0xRUNTIME_KEY --payload '{"msg":"hello"}' --expiry 1h
```

**Output:**

```json
{
  "envelope": {
    "v": 1,
    "agent_id": "0x...",
    "signer": "0x...",
    "ts": 1760000000,
    "exp": 1760003600,
    "nonce": "0xa1b2c3d4e5f6",
    "payload_hash": "0x...",
    "sig": "0x..."
  },
  "payload": {"msg": "hello from agent"}
}
```

**Flags:** `--payload '<json>'` (or stdin), `--key <address>`, `--scope <text>`, `--expiry <duration>`

## Verify inbound messages

Checks signature, expiry, nonce replay, payload hash, delegation status, and allowlist:

```bash
echo "$SIGNED_JSON" | vouch --json verify
```

From explicit JSON:

```bash
vouch --json verify --envelope '{"envelope":{...},"payload":{...}}'
```

From a remote endpoint:

```bash
vouch --json verify --url https://agent.example.com/latest-signed
```

**Output:**

```json
{
  "valid": true,
  "signer": "0x...",
  "identities": [
    {"provider": 1, "provider_label": "alice"},
    {"provider": 2, "provider_label": "alice-gh"}
  ],
  "scope": "messaging",
  "scope_matched": true,
  "failure_reason": "",
  "allowlist_checked": false,
  "allowlist_skipped": false,
  "checked_at": "2026-02-23T12:00:00Z"
}
```

The `failure_reason` field explains why verification failed when `valid` is `false`. The `identities` array lists all linked identities for the signer.

**Flags:** `--envelope '<json>'`, `--url <endpoint>`, `--skip-allowlist`

## Send verified messages

Sign a payload and POST it to another agent's endpoint:

```bash
vouch --json send --payload '{"task":"summarize","doc_id":"abc"}' --url https://agent.example.com/vouch
```

Resolve the endpoint from the onchain directory by wallet:

```bash
vouch --json send --payload '{"task":"deploy"}' --wallet 0xTARGET_WALLET
```

Pipe payload via stdin:

```bash
echo '{"task":"analyze"}' | vouch --json send --url https://agent.example.com/vouch
```

**Output:**

```json
{
  "endpoint": "https://agent.example.com/vouch",
  "accepted": true,
  "message": "task received",
  "error": ""
}
```

**Flags:** `--payload '<json>'` (or stdin), `--url <endpoint>` or `--wallet <address>` (mutually exclusive), `--key <address>`, `--scope <text>`, `--expiry <duration>` (default `1h`)

## Receive verified messages

Run an HTTP server that accepts, verifies, and processes signed envelopes:

```bash
vouch receive --port 8080 --handler ./process.sh
```

With allowlist enforcement and rate limiting:

```bash
vouch receive --port 8080 --handler ./process.sh --allowlist --rate-limit 10
```

The server listens on `/vouch` and `/` (POST only). Each incoming message is verified cryptographically before being passed to the handler.

**Handler input** (JSON on stdin):

```json
{
  "sender": {
    "agent_id": "0x...",
    "signer": "0x...",
    "identities": [
      {"provider": 1, "provider_label": "alice"}
    ]
  },
  "payload": {"task": "summarize", "doc_id": "abc"},
  "verified_at": "2026-02-23T12:00:00Z"
}
```

The handler's stdout becomes the response message. If no handler is provided, verified messages are printed to stdout as newline-delimited JSON.

**Response format:**

```json
{"accepted": true, "message": "task received"}
```

**Flags:** `--port <int>` (default `8080`), `--handler <script>`, `--allowlist`, `--rate-limit <float>` (requests/sec/IP, default `0` = unlimited)

## Agent scaffolding

Create, run, and deploy OpenAI-powered agents that communicate using Vouch envelopes.

### Create an agent

Interactive wizard that generates a ready-to-deploy agent project:

```bash
vouch agent create
```

Prompts for: agent name, description, language (Node.js or Python), model, OpenAI API key, and port. Creates the project at `~/.vouch/agents/<name>/`.

### Run locally

```bash
vouch agent start my-agent
```

Starts `vouch receive` with the agent's handler and port. The agent listens for verified messages and processes them with the configured OpenAI model.

### Deploy to Vercel

```bash
vouch agent deploy my-agent --prod
```

Requires the Vercel CLI (`npm i -g vercel`). Deploys the agent and prints the live endpoint URL. Use `--prod` for production (default is preview).

After deploying, publish the endpoint to the directory:

```bash
vouch publish --wallet-key 0xKEY --endpoint https://my-agent.vercel.app/api/vouch --capabilities "chat,summarize"
```

## Look up identities and agents

```bash
vouch --json lookup @alice                    # by X handle
vouch --json lookup --wallet 0x...            # by wallet address
vouch --json lookup --xid 123                 # by X user ID
vouch --json lookup --key 0xRUNTIME_KEY       # find who delegated a key
vouch --json lookup --capability chat          # search agent directory
```

**Output:**

```json
{
  "mode": "handle",
  "query": "@alice",
  "found": true,
  "profile": {
    "wallet": "0x...",
    "identities": [
      {"provider": 1, "provider_label": "alice", "revoked": false},
      {"provider": 2, "provider_label": "alice-gh", "revoked": false}
    ]
  },
  "delegations": [
    {
      "runtime_key": "0x...",
      "expires_at": "1760086400",
      "scope": "messaging"
    }
  ],
  "agents": [
    {
      "endpoint": "https://agent.example.com/api",
      "capabilities": ["chat", "verify", "summarize"]
    }
  ]
}
```

## Check current identity

```bash
vouch --json whoami     # full identity summary (network call)
vouch status            # local config only (no network)
```

## Manage delegations

Create a new runtime key delegation:

```bash
vouch --json delegate --wallet-key 0xKEY --expiry 24h --scope messaging
```

Renew an existing delegation with the same settings:

```bash
vouch --json delegate --wallet-key 0xKEY --renew
```

**Output:**

```json
{
  "runtime_key": "0x...",
  "expires_at": 1760003600,
  "scope": "messaging",
  "tx_hash": "0xdef..."
}
```

Constraints: max 30-day expiry, max 5 delegations per minute.

Revoke a specific key:

```bash
vouch --json revoke-key --wallet-key 0xKEY --key 0xRUNTIME_KEY
```

**Flags:** `--key <address|hex>`, `--expiry <duration>` (default `24h`), `--scope <text>`, `--wallet-key <hex>`, `--renew`

## Publish agent capabilities

Register an endpoint and capabilities in the onchain agent directory:

```bash
vouch --json publish \
  --wallet-key 0xKEY \
  --endpoint https://agent.example.com/api \
  --capabilities "chat,verify,summarize"
```

## Manage trust allowlist

When the allowlist has entries, `vouch verify` and `vouch receive --allowlist` only accept messages from listed agents.

```bash
vouch allowlist add 0xWALLET @alice --note "trusted partner"
vouch allowlist list
vouch allowlist remove @alice
```

## Account and billing

### Check usage

```bash
vouch --json account
```

**Output:**

```json
{
  "period": "2026-02",
  "relay_transactions": 3,
  "relay_limit": 10,
  "tier": "free"
}
```

### List API keys

```bash
vouch --json account keys
```

### Check billing status

```bash
vouch --json account billing
```

### Tier reference

| | Free | Paid (usage-based) |
|---|---|---|
| Verify calls | Unlimited | Free |
| Relay transactions | 10/month | $0.05 each |

Manage billing at https://vouch.directory/dashboard/billing or upgrade via the dashboard.

## Recipes

**Full onboarding for a new agent:**

```bash
vouch init
```

**Sign-then-verify round trip:**

```bash
vouch --json sign --payload '{"action":"deploy"}' \
  | vouch --json verify \
  | jq '{valid, signer, identities}'
```

**Send a verified message to another agent:**

```bash
vouch --json send --payload '{"task":"summarize","doc_id":"abc"}' --url https://agent.example.com/vouch
```

**Agent-to-agent round trip:**

```bash
# Terminal 1: start receiver
vouch receive --port 9090 --handler ./echo.sh

# Terminal 2: send verified message
vouch --json send --payload '{"msg":"hello"}' --url http://localhost:9090/vouch
```

**Scaffold, test, and deploy an agent:**

```bash
vouch agent create
vouch agent start my-agent
# test locally, then deploy:
vouch agent deploy my-agent --prod
vouch publish --wallet-key 0xKEY --endpoint https://my-agent.vercel.app/api/vouch --capabilities "chat,summarize"
```

**Start a receiver with allowlist and rate limiting:**

```bash
vouch receive --port 8080 --handler ./process.sh --allowlist --rate-limit 10
```

**Batch verify from file:**

```bash
while IFS= read -r line; do
  echo "$line" | vouch --json verify | jq -c '{valid, signer}'
done < envelopes.jsonl
```

**Check usage before heavy operations:**

```bash
vouch --json account | jq '{relay_transactions, relay_limit, tier}'
```

**Find agents by capability:**

```bash
vouch --json lookup --capability chat | jq '.agents[]'
```

**Link an additional identity after setup:**

```bash
vouch link-github
```

**Sign, send, and verify in a pipeline:**

```bash
SIGNED=$(vouch --json sign --payload '{"task":"deploy","id":"cr-42"}')
echo "$SIGNED" | curl -s -X POST -H "Content-Type: application/json" -d @- https://recipient.example.com/inbox
```

## Reset

Teardown the current identity and reinitialize from scratch:

```bash
vouch reset
```

Interactive mode revokes onchain identity, deletes `~/.vouch/`, then runs the full init flow (requires browser for OAuth). Requires typing `RESET` to confirm.

Skip onchain revocation:

```bash
vouch reset --force
```

Pipe mode (teardown only — reinit requires browser):

```bash
vouch --json reset --wallet-key 0xKEY
```

**Flags:** `--wallet-key <hex>` (enables pipe mode, teardown only), `--force` (skip onchain revocation)

## Teardown

Revoke onchain identity and delete all local state:

```bash
vouch --json teardown --wallet-key 0xKEY
```

Local-only cleanup (skip onchain revocation):

```bash
vouch --json teardown --force
```
