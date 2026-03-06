# 1Claw Skill — Example Conversations

## Example 1: Fetching an API key for an external service

**User:** "Use the Stripe API to check my account balance"

**Agent thinking:** I need the Stripe API key. Let me check what's available in the vault.

```
→ list_secrets(prefix: "api-keys/")
Found 2 secret(s):
- api-keys/stripe  (type: api_key, version: 3)
- api-keys/openai  (type: api_key, version: 1)
```

```
→ get_secret(path: "api-keys/stripe")
{"path":"api-keys/stripe","type":"api_key","version":3,"value":"sk_live_..."}
```

**Agent:** "I retrieved your Stripe API key and checked your account. Your current balance is $1,234.56."

(The raw key value is never shown to the user.)

## Example 2: Storing a newly generated credential

**User:** "I just created a new Twilio account. Here's my API key: SK1234567890abcdef. Store it securely."

```
→ put_secret(path: "api-keys/twilio", value: "SK1234567890abcdef", type: "api_key", metadata: {"provider": "twilio"})
Secret stored at 'api-keys/twilio' (version 1, type: api_key).
```

**Agent:** "Done — I stored your Twilio API key securely in the vault at `api-keys/twilio`. You can access it anytime."

## Example 3: Sharing a secret with a teammate

**User:** "Share the database password with the DevOps agent"

**Agent thinking:** I need to share with a specific agent. Let me use `share_secret` with the agent's ID.

```
→ list_secrets(prefix: "passwords/")
Found 1 secret(s):
- passwords/production-db  (type: password, version: 2, id: cf592...)
```

```
→ share_secret(secret_id: "cf592...", recipient_type: "agent", recipient_id: "a1b2c3...", expires_at: "2026-04-01T00:00:00Z", max_access_count: 5)
Secret shared with agent:a1b2c3... Share ID: df703...
```

**Agent:** "I shared the production database password with the DevOps agent. The share expires April 1 and allows up to 5 accesses. The agent will need to accept the share before they can access it."

## Example 4: Granting vault-level access

**User:** "Give my CI agent read access to all API keys"

```
→ grant_access(vault_id: "...", principal_type: "agent", principal_id: "ci-agent-uuid", permissions: ["read"], secret_path_pattern: "api-keys/**")
Access granted.
  Policy ID: pol_abc123
  Granted to: agent:ci-agent-uuid
  Permissions: read
  Path pattern: api-keys/**
```

**Agent:** "Done — the CI agent now has read access to all secrets under `api-keys/` in this vault."

## Example 5: Rotating a key after regeneration

**User:** "I regenerated my OpenAI API key. The new one is sk-proj-newkey123"

```
→ rotate_and_store(path: "api-keys/openai", value: "sk-proj-newkey123")
Rotated secret at 'api-keys/openai'. New version: 2.
```

**Agent:** "Updated — the OpenAI API key in the vault is now version 2 with your new key."

## Example 6: Loading environment variables

**User:** "Set up the production environment for the deploy script"

```
→ get_env_bundle(path: "config/prod-env")
{
  "DATABASE_URL": "postgres://...",
  "REDIS_URL": "redis://...",
  "API_KEY": "sk_..."
}
```

**Agent:** "I loaded 3 environment variables from the production config. The deploy script is ready to run."

## Example 7: Simulating a transaction before signing

**User:** "Send 0.01 ETH to 0xdead...beef on Base, but check it first"

**Agent thinking:** I should simulate the transaction first to verify it will succeed and check gas costs.

```
→ simulate_transaction(to: "0x000000000000000000000000000000000000dEaD", value: "0.01", chain: "base")
Simulation SUCCESS
Gas used: 21000
Balance changes:
  0xYourAddress: -0.01 ETH
  0x000...dEaD: +0.01 ETH
Tenderly: https://dashboard.tenderly.co/...
```

**Agent:** "The simulation succeeded — it will transfer 0.01 ETH to the burn address using 21,000 gas. Shall I submit it?"

**User:** "Yes, go ahead"

```
→ submit_transaction(to: "0x000000000000000000000000000000000000dEaD", value: "0.01", chain: "base", simulate_first: true)
Transaction BROADCAST
ID: tx_abc123
Tx hash: 0x1234...
Simulation: sim_xyz (success)
```

**Agent:** "Done — the transaction was simulated, signed, and broadcast on Base. Transaction hash: `0x1234...`"

## Example 8: Agent discovers it lacks permission

**User:** "Read the SSH key at `keys/prod-server`"

```
→ get_secret(path: "keys/prod-server")
Error 403: Insufficient permissions
```

**Agent:** "I don't have access to read `keys/prod-server`. You'll need to grant my agent read access to that path. You can do this from the 1claw dashboard under Vaults → Policies, or ask me to describe what policy is needed."
