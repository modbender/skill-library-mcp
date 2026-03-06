# 1Claw Skill — Configuration Reference

## Environment variables

### MCP server (stdio mode — recommended: auto-refreshing credentials)

| Variable                | Required | Description                                                |
| ----------------------- | -------- | ---------------------------------------------------------- |
| `ONECLAW_AGENT_ID`      | Yes\*    | Agent UUID                                                 |
| `ONECLAW_AGENT_API_KEY` | Yes\*    | Agent API key (`ocv_...`). Auto-refreshes JWT.             |
| `ONECLAW_VAULT_ID`      | Yes      | UUID of the vault to operate on                            |
| `ONECLAW_BASE_URL`      | No       | API URL (default: `https://api.1claw.xyz`)                 |

\*Or use `ONECLAW_AGENT_TOKEN` (static JWT, expires ~1h) instead of agent ID + API key.

### MCP server (stdio mode — legacy: static JWT)

| Variable              | Required | Description                                  |
| --------------------- | -------- | -------------------------------------------- |
| `ONECLAW_AGENT_TOKEN` | Yes      | Agent JWT (from `POST /v1/auth/agent-token`) |
| `ONECLAW_VAULT_ID`    | Yes      | UUID of the vault to operate on              |
| `ONECLAW_BASE_URL`    | No       | API URL (default: `https://api.1claw.xyz`)   |

### MCP server (HTTP streaming mode)

| Variable           | Required | Description                                |
| ------------------ | -------- | ------------------------------------------ |
| `MCP_TRANSPORT`    | Yes      | Set to `httpStream`                        |
| `PORT`             | No       | HTTP port (default: `8080`)                |
| `ONECLAW_BASE_URL` | No       | API URL (default: `https://api.1claw.xyz`) |

Per-request authentication via headers:

- `Authorization: Bearer <agent-jwt>`
- `X-Vault-ID: <vault-uuid>`

### TypeScript SDK

| Variable                | Required | Description                                |
| ----------------------- | -------- | ------------------------------------------ |
| `ONECLAW_API_KEY`       | Yes\*    | Personal API key (`1ck_...`)               |
| `ONECLAW_BASE_URL`      | No       | API URL (default: `https://api.1claw.xyz`) |
| `ONECLAW_AGENT_ID`      | Yes\*    | Agent UUID (alternative to API key)        |
| `ONECLAW_AGENT_API_KEY` | Yes\*    | Agent API key (`ocv_...`)                  |

\*Use either a personal API key or agent credentials, not both.

## Getting your credentials

1. Go to [1claw.xyz](https://1claw.xyz) and sign in.
2. Create a vault (or use an existing one).
3. Register an agent under **Agents**.
4. Copy the agent ID and API key.
5. Create a policy granting the agent `read` (and optionally `write`) on the vault.
6. Exchange the agent credentials for a JWT:

```bash
curl -X POST https://api.1claw.xyz/v1/auth/agent-token \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"<uuid>","api_key":"ocv_..."}'
```

Use the returned `access_token` as `ONECLAW_AGENT_TOKEN`.

## Secret types

| Type          | Use for                                  |
| ------------- | ---------------------------------------- |
| `api_key`     | API keys, tokens, bearer credentials     |
| `password`    | Passwords, passphrases                   |
| `private_key` | SSH keys, signing keys                   |
| `certificate` | TLS/SSL certificates                     |
| `ssh_key`     | SSH key pairs                            |
| `env_bundle`  | Multi-line KEY=VALUE environment configs |
| `note`        | Free-form text notes                     |
| `file`        | Raw file contents                        |

## Rate limits and billing

- **Free tier:** 1,000 API requests/month, 3 vaults, 50 secrets, 2 agents per organization.
- **Subscription tiers:** Pro ($29/mo), Business ($149/mo), Enterprise (custom). Higher quotas and discounted overage rates.
- **Overage methods (org chooses one):**
    - **Prepaid credits** — Top up $5–$1,000 via Stripe. Credits deducted at tier-discounted rates. Expire 12 months from purchase.
    - **x402 micropayments** — Per-query on-chain payments on Base. No credit card needed.
- Share creation is rate-limited to 10 per minute per organization.
- Agents cannot create email-based share invites (only human users can).
- Share recipients must explicitly accept shares before accessing secrets.
- Manage billing and upgrade at [1claw.xyz/settings/billing](https://1claw.xyz/settings/billing) or [1claw.xyz/pricing](https://1claw.xyz/pricing).
