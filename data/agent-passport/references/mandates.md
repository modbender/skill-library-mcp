# Agent Passport Mandate Reference (v2.0)

## Local Mode (CLI) — mandate-ledger.sh

The local ledger is the primary interface. All commands use `mandate-ledger.sh <command> [args]`.

### Action Categories

| Type | Description |
|------|-------------|
| `financial` | Purchases, transfers, subscriptions |
| `communication` | Emails, messages, posts |
| `data` | File deletion, edits, database writes |
| `system` | Shell commands, installs, config changes |
| `external_api` | Third-party API calls with side effects |
| `identity` | Public actions "as" the user |

### Create Mandate

```bash
mandate-ledger.sh create '<json>'
```

**Required fields:**
- `action_type` — one of the categories above (defaults to `financial`)
- `agent_id` — agent identifier (e.g., `agent:seb`)
- `ttl` — ISO 8601 expiry timestamp (must be in the future)
- `scope` — object (can be `{}`)

**Optional fields:**
- `amount_cap` — max spend (financial)
- `scope.allowlist` — array of allowed target patterns
- `scope.deny` — array of denied target patterns
- `scope.rate_limit` — e.g., `"20/day"`, `"100/hour"` (cumulative, windows not yet implemented)

**Example:**
```json
{
  "action_type": "system",
  "agent_id": "agent:seb",
  "scope": {
    "allowlist": ["git *", "npm *"],
    "deny": ["sudo *", "rm -rf *"]
  },
  "ttl": "2026-12-31T00:00:00Z"
}
```

**Errors:**
- Missing required field → `{"error": "Missing required field: <field>"}`
- Expired TTL → `{"error": "TTL is already expired", "ttl": "..."}`
- Invalid action_type → `{"error": "Invalid action_type. Must be: ..."}`

### Check Action

```bash
mandate-ledger.sh check-action <agent_id> <action_type> <target> [amount]
```

Finds an active, non-expired mandate matching the agent/type/target. Checks:
1. Allowlist patterns (exact, prefix, or `*@domain` matching)
2. Deny list patterns (exact or prefix with `*` suffix)
3. Amount cap (financial) or rate limit

**Returns:**
```json
{"authorized": true, "mandate_id": "...", "action_type": "...", "target": "..."}
{"authorized": false, "action_type": "...", "target": "...", "reason": "No valid mandate found"}
```

### Log Action

```bash
mandate-ledger.sh log-action <mandate_id> <amount> [description]
```

Records usage against a mandate. Validates status, TTL, caps, and rate limits before logging.

### Other Commands

| Command | Description |
|---------|-------------|
| `get <id>` | Get mandate by ID |
| `list [filter]` | List mandates (`all`, `active`, `revoked`, or action type) |
| `revoke <id> [reason]` | Revoke a mandate |
| `check <agent> <merchant> <amount>` | Legacy financial check |
| `spend <id> <amount>` | Legacy financial spend |
| `summary` | Ledger stats overview |
| `export` | Full ledger JSON |
| `audit [limit]` | Recent audit entries |
| `audit-mandate <id>` | Audit trail for a mandate |
| `audit-summary [since]` | Audit counts by action |

### KYA (Know Your Agent)

| Command | Description |
|---------|-------------|
| `kya-register <agent_id> <principal> <scope> [provider]` | Register/update agent |
| `kya-get <agent_id>` | Get agent KYA |
| `kya-list` | List all agents |
| `kya-revoke <agent_id> [reason]` | Revoke agent verification |
| `create-with-kya <json>` | Create mandate with auto-attached KYA |

---

## Agent Bridge (Live Mode)

The REST API for the hosted Agent Bridge service. Use when connecting to the live Agent Passport platform.

### Authentication
- Bearer token: `Authorization: Bearer $AGENT_PASSPORT_API_KEY`
- Base URL: `$AGENT_PASSPORT_BASE_URL`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/mandates` | Create mandate |
| `GET` | `/v1/mandates/{id}` | Get mandate |
| `GET` | `/v1/mandates` | List mandates (`status_filter`, `mandate_type`, `skip`, `limit`) |
| `PUT` | `/v1/mandates/{id}/revoke` | Revoke mandate (body: `{"reason": "..."}`) |

**Create mandate fields:** `mandate_type` (intent/cart/payment), `scope`, `ttl`, `amount_cap`, `currency`, `merchant_id`, `agent_id`, `user_id`, `tenant_id`, `channel`.

Optional: `policy_snapshot_id`, `policy_version`, `items`, `scope.kya`.

### KYA Metadata (scope.kya)

Store KYA evidence inside `scope.kya`:

```json
{
  "status": "verified",
  "provider": "internal-review",
  "verified_principal": "Acme Corp",
  "agent_identity": "agent:acme-shopping-bot",
  "authorization_scope": "purchase office supplies under $500",
  "verified_at": "2026-02-03T18:00:00Z"
}
```
