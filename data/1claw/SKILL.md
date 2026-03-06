---
name: 1claw
version: 1.0.8
description: HSM-backed secret management for AI agents — store, retrieve, rotate, and share secrets via the 1Claw vault without exposing them in context.
homepage: https://1claw.xyz
repository: https://github.com/1clawAI/1claw
metadata:
    {
        "openclaw":
            {
                "requires":
                    {
                        "env": ["ONECLAW_AGENT_ID", "ONECLAW_AGENT_API_KEY", "ONECLAW_VAULT_ID"],
                        "bins": [],
                    },
                "primaryEnv": "ONECLAW_AGENT_ID",
                "install":
                    [
                        {
                            "id": "npm",
                            "kind": "node",
                            "package": "@1claw/mcp",
                            "bins": ["1claw-mcp"],
                            "label": "1Claw MCP Server",
                        },
                    ],
                "credentials": ["ONECLAW_AGENT_ID", "ONECLAW_AGENT_API_KEY", "ONECLAW_VAULT_ID"],
                "permissions":
                    [
                        "vault:read",
                        "vault:write",
                        "vault:delete",
                        "secret:read",
                        "secret:write",
                        "secret:delete",
                        "policy:create",
                        "share:create",
                        "tx:sign",
                        "tx:simulate",
                    ],
            },
    }
---

# 1Claw — HSM-Backed Secret Management for AI Agents

1Claw is a cloud HSM-backed secrets manager. Agents access API keys, passwords, and credentials at runtime without them ever entering the conversation context. Secrets are encrypted with keys that never leave the HSM.

**API base URL:** `https://api.1claw.xyz`
**MCP endpoint:** `https://mcp.1claw.xyz/mcp`
**Dashboard:** `https://1claw.xyz`
**Docs:** `https://docs.1claw.xyz`

## When to use this skill

- You need an API key, password, or credential to complete a task
- You want to store a newly generated credential securely
- You need to share a secret with a user or another agent
- You need to rotate a credential after regenerating it
- You want to check what secrets are available before using one
- You need to sign or simulate an EVM transaction without exposing private keys

---

## Setup

### Option 1: MCP server (recommended for AI agents)

Add to your MCP client configuration. The server auto-refreshes JWT tokens.

```json
{
    "mcpServers": {
        "1claw": {
            "command": "npx",
            "args": ["-y", "@1claw/mcp"],
            "env": {
                "ONECLAW_AGENT_ID": "<agent-uuid>",
                "ONECLAW_AGENT_API_KEY": "<agent-api-key>",
                "ONECLAW_VAULT_ID": "<vault-uuid>"
            }
        }
    }
}
```

Hosted HTTP streaming mode:

```
URL: https://mcp.1claw.xyz/mcp
Headers:
  Authorization: Bearer <agent-jwt>
  X-Vault-ID: <vault-uuid>
```

### Option 2: TypeScript SDK

```bash
npm install @1claw/sdk
```

```ts
import { createClient } from "@1claw/sdk";

const client = createClient({
    baseUrl: "https://api.1claw.xyz",
    agentId: process.env.ONECLAW_AGENT_ID,
    apiKey: process.env.ONECLAW_AGENT_API_KEY,
});
```

### Option 3: Direct REST API

Authenticate, then pass the Bearer token on every request.

```bash
# Exchange agent credentials for a JWT
TOKEN=$(curl -s -X POST https://api.1claw.xyz/v1/auth/agent-token \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"<uuid>","api_key":"<key>"}' | jq -r .access_token)

# Use the JWT
curl -H "Authorization: Bearer $TOKEN" https://api.1claw.xyz/v1/vaults
```

**Alternative:** `1ck_` API keys (personal or agent) can be used directly as Bearer tokens — no JWT exchange needed.

---

## Authentication

### Agent auth flow

1. Human registers an agent in the dashboard or via `POST /v1/agents` with an `auth_method` (`api_key` default, `mtls`, or `oidc_client_credentials`). For `api_key` agents → receives `agent_id` + `api_key` (prefix `ocv_`). For mTLS/OIDC agents → receives `agent_id` only (no API key).
2. All agents auto-receive an Ed25519 SSH keypair (public key on agent record, private key in `__agent-keys` vault).
3. API key agents exchange credentials: `POST /v1/auth/agent-token` with `{ "agent_id": "<uuid>", "api_key": "<key>" }` → returns `{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 3600 }`.
4. Agent uses `Authorization: Bearer <jwt>` on all subsequent requests.
5. JWT scopes derive from the agent's access policies (path patterns). If no policies exist, scopes are empty (zero access). The agent's `vault_ids` are also included in the JWT — requests to unlisted vaults are rejected.
6. Token TTL defaults to ~1 hour but can be set per-agent via `token_ttl_seconds`. The MCP server auto-refreshes 60s before expiry.

### API key auth

Tokens starting with `1ck_` (human personal API keys) or `ocv_` (agent API keys) can be used as Bearer tokens directly on any authenticated endpoint.

---

## MCP Tools Reference

### list_secrets

List all secrets in the vault. Returns paths, types, and versions — never values.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prefix` | string | no | Path prefix to filter (e.g. `api-keys/`) |

### get_secret

Fetch the decrypted value of a secret. Use immediately before the API call that needs it. Never store the value or include it in summaries.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Secret path (e.g. `api-keys/stripe`) |

### put_secret

Store a new secret or update an existing one. Each call creates a new version.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | yes | | Secret path |
| `value` | string | yes | | The secret value |
| `type` | string | no | `api_key` | One of: `api_key`, `password`, `private_key`, `certificate`, `file`, `note`, `ssh_key`, `env_bundle` |
| `metadata` | object | no | | Arbitrary JSON metadata |
| `expires_at` | string | no | | ISO 8601 expiry datetime |
| `max_access_count` | number | no | | Max reads before auto-expiry (0 = unlimited) |

### delete_secret

Soft-delete a secret. Reversible by an admin.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Secret path to delete |

### describe_secret

Get metadata (type, version, expiry) without fetching the value. Use to check existence.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Secret path |

### rotate_and_store

Store a new value for an existing secret, creating a new version. Use after regenerating a key.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Secret path |
| `value` | string | yes | New secret value |

### get_env_bundle

Fetch an `env_bundle` secret and parse its `KEY=VALUE` lines as JSON.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Path to an `env_bundle` secret |

### create_vault

Create a new vault for organizing secrets.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | yes | Vault name (1–255 chars) |
| `description` | string | no | Short description |

### list_vaults

List all vaults accessible to you. No parameters.

### grant_access

Grant a user or agent access to a vault path pattern.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `vault_id` | string (UUID) | yes | | Vault ID |
| `principal_type` | `user` \| `agent` | yes | | Who to grant access to |
| `principal_id` | string (UUID) | yes | | The user or agent UUID |
| `permissions` | string[] | no | `["read"]` | `["read"]`, `["write"]`, or `["read","write"]` |
| `secret_path_pattern` | string | no | `**` | Glob pattern for secret paths |

### share_secret

Share a secret via link, with your creator, or with a specific user/agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `secret_id` | string (UUID) | yes | The secret's UUID |
| `recipient_type` | `user` \| `agent` \| `anyone_with_link` \| `creator` | yes | `creator` shares with the human who registered this agent — no ID needed |
| `recipient_id` | string (UUID) | conditional | Required for `user` and `agent` types |
| `expires_at` | string | yes | ISO 8601 expiry |
| `max_access_count` | number | no (default 5) | Max reads (0 = unlimited) |

Targeted shares (creator/user/agent) require the recipient to explicitly accept before access.

### simulate_transaction

Simulate an EVM transaction via Tenderly without signing. Returns balance changes, gas estimates, success/revert status.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `to` | string | yes | | Destination address (0x-prefixed) |
| `value` | string | yes | | Value in ETH (e.g. `"0.01"`) |
| `chain` | string | yes | | Chain name or chain ID (see Supported Chains) |
| `data` | string | no | | Hex-encoded calldata |
| `signing_key_path` | string | no | `keys/{chain}-signer` | Vault path to signing key |
| `gas_limit` | number | no | 21000 | Gas limit |

### submit_transaction

Submit an EVM transaction for signing and optional broadcast. Requires `crypto_proxy_enabled`.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `to` | string | yes | | Destination address |
| `value` | string | yes | | Value in ETH |
| `chain` | string | yes | | Chain name or chain ID |
| `data` | string | no | | Hex-encoded calldata |
| `signing_key_path` | string | no | `keys/{chain}-signer` | Vault path to signing key |
| `nonce` | number | no | auto-resolved | Transaction nonce |
| `gas_price` | string | no | | Gas price in wei (legacy mode) |
| `gas_limit` | number | no | 21000 | Gas limit |
| `max_fee_per_gas` | string | no | | EIP-1559 max fee in wei (triggers Type 2) |
| `max_priority_fee_per_gas` | string | no | | EIP-1559 priority fee in wei |
| `simulate_first` | boolean | no | true | Run Tenderly simulation before signing |

---

## REST API Quick Reference

Base URL: `https://api.1claw.xyz`. All authenticated endpoints require `Authorization: Bearer <token>`.

### Auth (public — no token required)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/auth/token` | Login (email + password) → `{ access_token }` |
| `POST` | `/v1/auth/agent-token` | Agent login (agent_id + api_key) → `{ access_token }` |
| `POST` | `/v1/auth/google` | Google OAuth |
| `POST` | `/v1/auth/signup` | Create account → sends verification email |
| `POST` | `/v1/auth/verify-email` | Verify email token → creates user |
| `POST` | `/v1/auth/mfa/verify` | Verify MFA code during login |

### Auth (authenticated)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/auth/me` | Get current user profile |
| `PATCH` | `/v1/auth/me` | Update profile (`display_name`, `marketing_emails`) |
| `DELETE` | `/v1/auth/me` | Delete account (body: `{ "confirmation": "DELETE MY ACCOUNT" }`) |
| `DELETE` | `/v1/auth/token` | Revoke current token |
| `POST` | `/v1/auth/change-password` | Change password |

### Vaults

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/vaults` | Create vault (`{ name, description? }`) → `201` |
| `GET` | `/v1/vaults` | List vaults → `{ vaults: [...] }` |
| `GET` | `/v1/vaults/{id}` | Get vault details |
| `DELETE` | `/v1/vaults/{id}` | Delete vault → `204` |
| `POST` | `/v1/vaults/{id}/cmek` | Enable CMEK (`{ fingerprint }`) |
| `DELETE` | `/v1/vaults/{id}/cmek` | Disable CMEK |
| `POST` | `/v1/vaults/{id}/cmek-rotate` | Start CMEK key rotation (headers: `X-CMEK-Old-Key`, `X-CMEK-New-Key`) |
| `GET` | `/v1/vaults/{id}/cmek-rotate/{job_id}` | Get rotation job status |

### Secrets

| Method | Path | Description |
|--------|------|-------------|
| `PUT` | `/v1/vaults/{id}/secrets/{path}` | Store/update secret (`{ type, value, metadata?, expires_at?, max_access_count? }`) → `201` |
| `GET` | `/v1/vaults/{id}/secrets/{path}` | Read secret → `{ path, type, value, version, metadata }` |
| `DELETE` | `/v1/vaults/{id}/secrets/{path}` | Delete secret → `204` |
| `GET` | `/v1/vaults/{id}/secrets?prefix=...` | List secrets (metadata only, no values) |

### Agents

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/agents` | Create agent → `{ agent: {...}, api_key: "ocv_..." }` |
| `GET` | `/v1/agents` | List agents → `{ agents: [...] }` |
| `GET` | `/v1/agents/{id}` | Get agent |
| `GET` | `/v1/agents/me` | Get current agent (self) |
| `PATCH` | `/v1/agents/{id}` | Update agent (is_active, scopes, crypto_proxy_enabled, guardrails) |
| `DELETE` | `/v1/agents/{id}` | Delete agent → `204` |
| `POST` | `/v1/agents/{id}/rotate-key` | Rotate agent API key → `{ api_key: "ocv_..." }` |

### Policies (Access Control)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/vaults/{id}/policies` | Create policy (`{ principal_type, principal_id, secret_path_pattern, permissions, conditions?, expires_at? }`) |
| `GET` | `/v1/vaults/{id}/policies` | List policies for vault |
| `PUT` | `/v1/vaults/{id}/policies/{pid}` | Update policy (permissions, conditions, expires_at only) |
| `DELETE` | `/v1/vaults/{id}/policies/{pid}` | Delete policy → `204` |

### Sharing

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/secrets/{id}/share` | Create share link |
| `GET` | `/v1/shares/outbound` | List shares you created |
| `GET` | `/v1/shares/inbound` | List shares sent to you |
| `POST` | `/v1/shares/{id}/accept` | Accept an inbound share |
| `POST` | `/v1/shares/{id}/decline` | Decline an inbound share |
| `DELETE` | `/v1/share/{id}` | Revoke a share |
| `GET` | `/v1/share/{id}` | Access a share (public, may require passphrase) |

### Crypto Proxy (requires `crypto_proxy_enabled`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/agents/{id}/transactions` | Submit transaction for signing |
| `GET` | `/v1/agents/{id}/transactions` | List agent's transactions |
| `GET` | `/v1/agents/{id}/transactions/{txid}` | Get transaction details |
| `POST` | `/v1/agents/{id}/transactions/simulate` | Simulate single transaction |
| `POST` | `/v1/agents/{id}/transactions/simulate-bundle` | Simulate transaction bundle |

### Audit

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/audit/events?limit=N&action=...&from=...&to=...` | Query audit events |

### Billing

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/billing/subscription` | Subscription status, usage, credit balance |
| `GET` | `/v1/billing/credits/balance` | Credit balance + expiring credits |
| `GET` | `/v1/billing/credits/transactions` | Credit transaction ledger |
| `PATCH` | `/v1/billing/overage-method` | Set overage method (`credits` or `x402`) |
| `GET` | `/v1/billing/usage` | Usage summary (current month) |
| `GET` | `/v1/billing/history` | Usage event history |

### Chains

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/chains` | List supported chains |
| `GET` | `/v1/chains/{name_or_id}` | Get chain details |

### Other

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/health` | Health check → `{ status, service, version }` |
| `GET` | `/v1/health/hsm` | HSM health → `{ status, hsm_provider, connected }` |
| `POST/GET/DELETE` | `/v1/auth/api-keys[/{id}]` | Manage personal API keys |
| `GET/POST/DELETE` | `/v1/security/ip-rules[/{id}]` | Manage IP allowlist/blocklist |
| `GET/PATCH/DELETE` | `/v1/org/members[/{id}]` | Manage org members |

---

## SDK Method Reference

All methods return `Promise<OneclawResponse<T>>`. Access via `client.<resource>.<method>(...)`.

| Resource | Method | Description |
|----------|--------|-------------|
| `vaults` | `create({ name, description? })` | Create vault |
| `vaults` | `get(vaultId)` | Get vault |
| `vaults` | `list()` | List vaults |
| `vaults` | `delete(vaultId)` | Delete vault |
| `secrets` | `set(vaultId, key, value, { type?, metadata?, expires_at?, max_access_count? })` | Store/update secret |
| `secrets` | `get(vaultId, key)` | Read secret (decrypted) |
| `secrets` | `list(vaultId, prefix?)` | List secret metadata |
| `secrets` | `delete(vaultId, key)` | Delete secret |
| `secrets` | `rotate(vaultId, key, newValue)` | Rotate secret to new version |
| `agents` | `create({ name, description?, scopes?, expires_at?, crypto_proxy_enabled?, token_ttl_seconds?, vault_ids? })` | Create agent → returns agent + api_key |
| `agents` | `get(agentId)` | Get agent |
| `agents` | `list()` | List agents |
| `agents` | `update(agentId, { is_active?, scopes?, crypto_proxy_enabled?, tx_*? })` | Update agent |
| `agents` | `delete(agentId)` | Delete agent |
| `agents` | `rotateKey(agentId)` | Rotate agent API key |
| `agents` | `submitTransaction(agentId, { to, value, chain, ... })` | Submit EVM transaction |
| `agents` | `simulateTransaction(agentId, { to, value, chain, ... })` | Simulate transaction |
| `agents` | `simulateBundle(agentId, bundle)` | Simulate transaction bundle |
| `agents` | `getTransaction(agentId, txId)` | Get transaction |
| `agents` | `listTransactions(agentId)` | List agent transactions |
| `access` | `grantAgent(vaultId, agentId, permissions, { path?, conditions?, expires_at? })` | Grant agent access |
| `access` | `grantHuman(vaultId, userId, permissions, { path?, conditions?, expires_at? })` | Grant user access |
| `access` | `listGrants(vaultId)` | List policies |
| `access` | `update(vaultId, policyId, { permissions?, conditions?, expires_at? })` | Update policy |
| `access` | `revoke(vaultId, policyId)` | Revoke policy |
| `sharing` | `create(secretId, { recipient_type, recipient_id?, expires_at, max_access_count? })` | Create share |
| `sharing` | `access(shareId)` | Access shared secret |
| `sharing` | `listOutbound()` | Shares you created |
| `sharing` | `listInbound()` | Shares sent to you |
| `sharing` | `accept(shareId)` | Accept inbound share |
| `sharing` | `decline(shareId)` | Decline inbound share |
| `sharing` | `revoke(shareId)` | Revoke outbound share |
| `audit` | `query({ action?, actor_id?, from?, to?, limit?, offset? })` | Query audit events |
| `billing` | `usage()` | Current month usage |
| `billing` | `history(limit?)` | Usage event history |
| `auth` | `login({ email, password })` | Human login |
| `auth` | `agentToken({ agent_id, api_key })` | Agent JWT exchange |
| `auth` | `logout()` | Revoke token |
| `apiKeys` | `create({ name, scopes?, expires_at? })` | Create personal API key |
| `apiKeys` | `list()` | List API keys |
| `apiKeys` | `revoke(keyId)` | Revoke key |
| `chains` | `list()` | List supported chains |
| `chains` | `get(identifier)` | Get chain by name or ID |
| `org` | `listMembers()` | List org members |
| `org` | `updateMemberRole(userId, role)` | Update member role |
| `org` | `removeMember(userId)` | Remove member |

### OpenAPI spec for custom SDKs

The API spec is published as an npm package for generating clients in any language:

```bash
npm install @1claw/openapi-spec
```

Ships `openapi.yaml` and `openapi.json`. Use with any OpenAPI 3.1 codegen tool:

```bash
# TypeScript
npx openapi-typescript node_modules/@1claw/openapi-spec/openapi.yaml -o ./types.ts

# Python
openapi-generator generate -i node_modules/@1claw/openapi-spec/openapi.yaml -g python -o ./oneclaw-py

# Go
oapi-codegen -package oneclaw node_modules/@1claw/openapi-spec/openapi.yaml > oneclaw.go
```

SDK also re-exports generated types: `import type { ApiSchemas } from "@1claw/sdk"`.

---

## Supported Chains

Default chain registry (query `GET /v1/chains` for live list):

| Name | Chain ID | Testnet |
|------|----------|---------|
| ethereum | 1 | no |
| base | 8453 | no |
| optimism | 10 | no |
| arbitrum-one | 42161 | no |
| polygon | 137 | no |
| sepolia | 11155111 | yes |
| base-sepolia | 84532 | yes |

Use chain names (e.g. `"base"`, `"sepolia"`) or numeric chain IDs in transaction requests.

---

## Access Control Model

Agents do **not** get blanket access. A human must create a policy to grant an agent access to specific secret paths.

- **Path patterns**: Glob syntax — `api-keys/*`, `db/**`, `**` (all)
- **Permissions**: `read`, `write` (delete requires `write`)
- **Conditions**: IP allowlist, time windows (JSON)
- **Expiry**: Optional ISO 8601 date

If no policy matches → **403 Forbidden**. Vault creators always have full access (owner bypass).

### Vault binding and token scoping

Agents can be restricted beyond policies:

- **`vault_ids`**: Restrict the agent to specific vaults. If non-empty, any request to a vault not in the list returns 403.
- **`token_ttl_seconds`**: Custom JWT expiry per agent (e.g., 300 for 5-minute tokens).
- **Scopes from policies**: JWT scopes are derived from the agent's access policies. If an agent has no policies and no explicit scopes, it has zero access.

Set via dashboard, CLI (`--token-ttl`, `--vault-ids`), SDK, or API.

### Customer-Managed Encryption Keys (CMEK)

Enterprise opt-in feature (Business tier and above). A human generates a 256-bit AES key in the dashboard — the key never leaves their device. Only its SHA-256 fingerprint is stored on the server.

- Enable: `POST /v1/vaults/{id}/cmek` with `{ fingerprint }`
- Disable: `DELETE /v1/vaults/{id}/cmek`
- Rotate: `POST /v1/vaults/{id}/cmek-rotate` (server-assisted, batched in 100s)
- Secrets stored in a CMEK vault have `cmek_encrypted: true` in responses

Agents reading from a CMEK vault receive the encrypted blob. The CMEK key is required to decrypt client-side. This is designed for organizations with compliance requirements — the default HSM encryption is already strong.

### Crypto transaction proxy

When `crypto_proxy_enabled = true` (set by a human):

1. Agent **gains** transaction signing via the crypto proxy (keys stay in HSM)
2. Agent is **blocked** from reading `private_key` and `ssh_key` secrets directly (403)

Default signing key path: `keys/{chain}-signer`. Override with `signing_key_path`.

### Transaction guardrails

Human-configured, server-enforced limits on what the crypto proxy allows:

| Guardrail | Field | Effect |
|-----------|-------|--------|
| Allowed destinations | `tx_to_allowlist` | Only listed addresses permitted. Empty = unrestricted |
| Max value per tx | `tx_max_value_eth` | Single-tx cap in ETH. NULL = unlimited |
| Daily spend limit | `tx_daily_limit_eth` | Rolling 24h cumulative cap. NULL = unlimited |
| Allowed chains | `tx_allowed_chains` | Chain names. Empty = all chains |

Agents **cannot** modify their own guardrails. Violations return 403 with a descriptive error.

---

## Security Model

- **Credentials are configured by the human**, not the agent. The MCP server reads them from env vars.
- **The agent never sees its own credentials.** The MCP server authenticates on the agent's behalf.
- **Access is deny-by-default.** Even with valid credentials, only policy-allowed secrets are accessible.
- **Secret values are fetched just-in-time** and must never be stored, echoed, or included in summaries.
- **Agents cannot create email-based shares** (prevents phishing).
- **Crypto proxy is opt-in.** When enabled, raw key reads are blocked.
- **Transaction guardrails are human-controlled and server-enforced.**

---

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check request body format |
| 401 | Not authenticated | Token expired — re-authenticate |
| 402 | Quota exhausted / payment required | Inform user to top up credits or upgrade at `1claw.xyz/settings/billing` |
| 403 | No permission | Ask user to grant access via a policy. Or: guardrail violation (check error detail) |
| 403 | Resource limit reached (`type: "resource_limit_exceeded"`) | Tier limit on vaults/secrets/agents hit — ask user to upgrade at `1claw.xyz/settings/billing` |
| 404 | Not found | Check path with `list_secrets` |
| 405 | Method not allowed | Wrong HTTP verb for this endpoint |
| 409 | Conflict | Resource already exists (e.g. duplicate vault name) |
| 410 | Gone | Secret expired or max access count reached — ask user to store a new version |
| 422 | Validation error or simulation reverted | Check input. For `simulate_first`: transaction would revert |
| 429 | Rate limited | Wait and retry. Share creation: 10/min/org |

All error responses include a `detail` field with a human-readable message.

---

## Best Practices

1. **Fetch secrets just-in-time.** Call `get_secret` immediately before the API call that needs the credential.
2. **Never echo secret values.** Say "I retrieved the API key and used it" — never include raw values in responses.
3. **Use `describe_secret` first** to check existence or validity before fetching the full value.
4. **Use `list_secrets` to discover** available credentials before guessing paths.
5. **Rotate after regeneration.** If you regenerate an API key at a provider, immediately `rotate_and_store` the new value.
6. **Use `grant_access` for vault-level sharing** — creates a fine-grained policy with path patterns.
7. **Use `share_secret` for one-off sharing** — creates a time-limited, access-counted share link.
8. **Simulate before signing.** Always use `simulate_first: true` (default) or call `simulate_transaction` before `submit_transaction`.
9. **Check `list_vaults` before creating.** Avoid creating duplicate vaults.
10. **Handle 402 gracefully.** Billing/quota errors should be surfaced to the user, not retried.

---

## Billing Tiers

| Tier | Requests/mo | Vaults | Secrets | Agents | Price |
|------|-------------|--------|---------|--------|-------|
| Free | 1,000 | 3 | 50 | 2 | $0 |
| Pro | 25,000 | 25 | 500 | 10 | $29/mo |
| Business | 100,000 | 100 | 5,000 | 50 | $149/mo (+ CMEK) |
| Enterprise | Custom | Unlimited | Unlimited | Unlimited | Contact (+ CMEK + KMS delegation) |

Overage methods: **prepaid credits** (top up via Stripe, deducted per request) or **x402 micropayments** (per-query on-chain payments on Base).

Audit, org, security, chain, billing, and auth endpoints are **free and never consume quota**.

---

## Links

- Dashboard: [1claw.xyz](https://1claw.xyz)
- Docs: [docs.1claw.xyz](https://docs.1claw.xyz)
- Status: [1claw.xyz/status](https://1claw.xyz/status)
- API: `https://api.1claw.xyz`
- SDK: [@1claw/sdk on npm](https://www.npmjs.com/package/@1claw/sdk)
- OpenAPI Spec: [@1claw/openapi-spec on npm](https://www.npmjs.com/package/@1claw/openapi-spec)
- MCP Server: [@1claw/mcp on npm](https://www.npmjs.com/package/@1claw/mcp)
- CLI: [@1claw/cli on npm](https://www.npmjs.com/package/@1claw/cli)
- GitHub: [github.com/1clawAI](https://github.com/1clawAI)
- Support: [ops@1claw.xyz](mailto:ops@1claw.xyz)
