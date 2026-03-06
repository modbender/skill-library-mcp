---
name: guardrail-smart-accounts
description: Create and manage ERC-4337 smart accounts, policies, permissions, and enforcement for AI agents with on-chain spending guardrails.
version: 1.0.8
metadata:
  openclaw:
    requires:
      env:
        - GUARDRAIL_CHAIN_ID
        - GUARDRAIL_RPC_URL
        - GUARDRAIL_SIGNING_MODE
    optionalSecrets:
      - name: GUARDRAIL_SIGNER_ENDPOINT
        when: GUARDRAIL_SIGNING_MODE is external_signer
        sensitive: true
        description: External signer service URL
      - name: GUARDRAIL_SIGNER_AUTH_TOKEN
        when: GUARDRAIL_SIGNING_MODE is external_signer
        sensitive: true
        description: Scoped, revocable auth token for the external signer
      - name: GUARDRAIL_DASHBOARD_API_KEY
        when: Using dashboard API only
        sensitive: true
        description: Dashboard API key for management UI interaction
    primaryEnv: GUARDRAIL_RPC_URL
    emoji: "\U0001F6E1"
    homepage: https://agentguardrail.xyz
---

# Guardrail Smart Accounts Skill

> Create and manage ERC-4337 smart accounts, policies, permissions, and enforcement for AI agents with on-chain spending guardrails.

## Overview

The Guardrail Smart Accounts Skill enables agents and humans to create dedicated ERC-4337 smart accounts with built-in spending limits enforced on-chain. Every account is bound to a Guardrail policy at creation.

Guardrail never takes custody of funds — all enforcement occurs on-chain via deployed contracts.

This skill supports both:

- Programmatic agent execution
- Human-in-the-loop wallet workflows

It is designed as infrastructure: contract-level fees, policy-bound accounts, and non-custodial enforcement.

## Security & Credential Model (Required)

This skill performs on-chain operations that require:

- JSON-RPC access
- Transaction signing

**Private keys must never be provided in chat and must never be stored in unconstrained agent memory.**

The skill supports the following secure signing models:

### 1. External Signer (Recommended)

- The agent prepares a transaction.
- The runtime forwards it to a secure signer service (HSM, MPC, hosted signer).
- The signer enforces scope, rate limits, and allowlists.
- The agent never sees raw private keys.

### 2. Wallet Connector / User-Approved Signing

- Transactions are prepared by the agent.
- A user wallet (browser, hardware wallet) prompts for approval.
- Keys remain in the wallet.

### 3. Scoped Session Keys (Advanced)

- Session keys must be policy-restricted.
- Keys must have strict limits (value caps, allowlists).
- Keys must be short-lived and rotated frequently.
- Never expose a long-lived owner EOA private key.

### The Skill Must NOT

- Ask the user to paste private keys or seed phrases.
- Store private keys in memory, logs, or prompts.
- Access unrelated environment variables or local files.
- Request cloud credentials or system-level secrets.
- Persist secrets beyond runtime execution.

If secure signing is not configured, use this skill in **read-only mode** until proper signing is established.

## Required Runtime Configuration

These values must be provided via secure secret storage (not chat):

- `GUARDRAIL_CHAIN_ID` — Target chain identifier
- `GUARDRAIL_RPC_URL` — JSON-RPC endpoint for the target chain (treat as sensitive — hosted RPC URLs often contain API keys)
- `GUARDRAIL_SIGNING_MODE` — one of: `external_signer`, `wallet_connector`, `session_key`

### Conditional Secrets (declared in manifest as optionalSecrets)

These are only required when using specific signing modes:

- `GUARDRAIL_SIGNER_ENDPOINT` — External signer service URL. Only required when `GUARDRAIL_SIGNING_MODE` is `external_signer`. Not needed for `wallet_connector` or `session_key` modes.
- `GUARDRAIL_SIGNER_AUTH_TOKEN` — Scoped, revocable authentication token for the external signer. Only required when `GUARDRAIL_SIGNING_MODE` is `external_signer`. Must be stored in secure secret storage, never in chat or logs.
- `GUARDRAIL_DASHBOARD_API_KEY` — API key for dashboard management UI interaction. Not required for direct contract usage.

### Signer Token Rotation and Revocation

When using `external_signer` mode:

- `GUARDRAIL_SIGNER_AUTH_TOKEN` should be scoped to the minimum required permissions (allowlists, rate limits, spend caps).
- Tokens should be short-lived and rotated on a regular schedule.
- The external signer provider must support immediate token revocation.
- If a token is compromised, revoke it at the signer provider and rotate to a new token in secure secret storage.
- Never use long-lived owner EOA private keys as signer tokens.

### Dashboard API Key Usage

`GUARDRAIL_DASHBOARD_API_KEY` provides access to the management dashboard API for registering agents, managing policies, and viewing audit logs. It does not grant signing or fund-transfer capability. Store it in secure secret storage and rotate periodically.

The runtime must validate the chain ID and reject unsupported networks by default.

## Core Capabilities

### 1. Create Smart Account

Deploy a new smart account via the Guardrail factory. The account is bound to a PermissionEnforcer and controlled by a signer (EOA or generated keypair).

- Deterministic deployment via CREATE2 (salt-based)
- Owner recorded on-chain
- One-time creation fee: $10 USD equivalent in ETH
- Policy-bound by default

**Factory Contract:** `AgentAccountFactory`
**Function:** `createAccount(address owner, bytes32 agentId, bytes32 salt) payable returns (address)`

```solidity
// Get required creation fee
uint256 fee = factory.getCreationFee();

// Deploy account (send fee as msg.value)
address account = factory.createAccount{value: fee}(ownerAddress, agentId, salt);
```

### 2. Fund Smart Account (Inbound Transfer)

Send ETH to the smart account address.

Inbound transfers are free.

```javascript
// NOTE: walletClient must be backed by a secure signer integration.
// Do NOT provide raw private keys to the agent.

await walletClient.sendTransaction({
  to: smartAccountAddress,
  value: parseEther("1.0"),
});
```

### 3. Withdraw from Smart Account (Outbound Transfer)

Execute a transfer from the smart account.

Outbound transfers are charged a 10 bps (0.10%) fee, capped at $100 USD equivalent per transaction.

**Function:** `execute(address target, uint256 value, bytes data)`

```javascript
const data = encodeFunctionData({
  abi: agentSmartAccountABI,
  functionName: "execute",
  args: [destinationAddress, parseEther("1.0"), "0x"],
});

await walletClient.sendTransaction({
  to: smartAccountAddress,
  data,
});
```

Fee enforcement occurs inside GuardrailFeeManager.

### 4. Read State (Safe / Read-Only)

These functions do not require signing.

```javascript
// Get account owner
const owner = await publicClient.readContract({
  address: smartAccountAddress,
  abi: agentSmartAccountABI,
  functionName: "owner",
});

// Get creation fee
const fee = await publicClient.readContract({
  address: factoryAddress,
  abi: agentAccountFactoryABI,
  functionName: "getCreationFee",
});

// Calculate transfer fee
const transferFee = await publicClient.readContract({
  address: feeManagerAddress,
  abi: guardrailFeeManagerABI,
  functionName: "calculateTransferFee",
  args: [parseEther("10.0")],
});
```

`publicClient` must be a read-only RPC client.

### 5. Policy Management

Create and manage policies that define what actions agents can perform, with constraints on value, volume, and scope.

**Create Policy** — `POST /api/v1/policies`

```javascript
const response = await fetch(`${API_BASE_URL}/api/v1/policies`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    name: "DeFi Trading Policy",
    description: "Allow swaps and transfers with daily limits",
    definition: {
      actions: ["swap", "transfer"],
      assets: {
        tokens: ["0xA0b8...eB48", "0xdAC1...1eC7"],
        protocols: ["*"],
        chains: [1, 8453],
      },
      constraints: {
        maxValuePerTx: "1000000000000000000",
        maxDailyVolume: "10000000000000000000",
        maxWeeklyVolume: "50000000000000000000",
        maxTxCount: 100,
        requireApproval: false,
      },
      duration: {
        validFrom: "2025-01-01T00:00:00Z",
        validUntil: "2025-12-31T23:59:59Z",
      },
      conditions: [
        { field: "amount", operator: "lte", value: "5000000000000000000" },
      ],
    },
  }),
});
const policy = await response.json();
```

**PolicyDefinition structure:**

| Field | Type | Description |
|-------|------|-------------|
| `actions` | `string[]` | Allowed action types: `swap`, `transfer`, `approve`, `stake`, `unstake`, `deposit`, `withdraw`, `mint`, `burn`, `bridge`, `claim`, `vote`, `delegate`, `lp_add`, `lp_remove`, `borrow`, `repay`, `liquidate`, `*` (wildcard) |
| `assets.tokens` | `string[]` | Token contract addresses, or `["*"]` for all |
| `assets.protocols` | `string[]` | Protocol contract addresses, or `["*"]` for all |
| `assets.chains` | `number[]` | Allowed chain IDs |
| `constraints.maxValuePerTx` | `string` | Maximum value per transaction (wei) |
| `constraints.maxDailyVolume` | `string` | Maximum daily volume (wei) |
| `constraints.maxWeeklyVolume` | `string` | Maximum weekly volume (wei) |
| `constraints.maxTxCount` | `number` | Maximum transaction count within the duration |
| `constraints.requireApproval` | `boolean` | Whether transactions require manual approval |
| `duration.validFrom` | `string` | ISO 8601 start time |
| `duration.validUntil` | `string` | ISO 8601 end time |
| `conditions` | `array` | Advanced rules with `field`, `operator` (`eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `contains`, `regex`), and `value` |

**Activate Policy** — `POST /api/v1/policies/{id}/activate`

Registers the policy on-chain via PolicyRegistry. Required before granting permissions.

```javascript
await fetch(`${API_BASE_URL}/api/v1/policies/${policyId}/activate`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});
```

**Update Policy** — `PUT /api/v1/policies/{id}`

Draft policies update directly. Active policies create a new version.

```javascript
await fetch(`${API_BASE_URL}/api/v1/policies/${policyId}`, {
  method: "PUT",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    name: "Updated Policy Name",
    definition: {
      actions: ["swap", "transfer", "approve"],
      constraints: { maxValuePerTx: "2000000000000000000" },
    },
  }),
});
```

**Revoke Policy** — `POST /api/v1/policies/{id}/revoke`

Deactivates the policy on-chain. Active permissions using this policy will no longer validate.

**Reactivate Policy** — `POST /api/v1/policies/{id}/reactivate`

Re-registers a previously revoked policy on-chain.

**List Policies** — `GET /api/v1/policies`

**Get Policy** — `GET /api/v1/policies/{id}`

**Delete Policy** — `DELETE /api/v1/policies/{id}`

Only draft policies can be deleted. Active or revoked policies must be revoked first.

### 6. Permission Management

Permissions link an agent to a policy, authorizing specific actions for a defined period.

**Grant Permission** — `POST /api/v1/permissions`

The agent must be active and the policy must be activated before granting a permission.

```javascript
const response = await fetch(`${API_BASE_URL}/api/v1/permissions`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    agent_id: "agent-uuid",
    policy_id: "policy-uuid",
    valid_from: "2025-01-01T00:00:00Z",
    valid_until: "2025-12-31T23:59:59Z",
  }),
});
const permission = await response.json();
```

**Mint Permission** — `POST /api/v1/permissions/{id}/mint`

Registers the permission on-chain via `PolicyRegistry.grantPermission()`. For smart account agents, syncs constraints to PermissionEnforcer. Returns `onchain_token_id`.

```javascript
const minted = await fetch(
  `${API_BASE_URL}/api/v1/permissions/${permissionId}/mint`,
  {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  }
).then((r) => r.json());
// minted.onchain_token_id — on-chain token ID
```

**Revoke Permission** — `DELETE /api/v1/permissions/{id}`

Revokes the permission. Calls `PolicyRegistry.revokePermission()` on-chain if the permission was minted.

**List Permissions** — `GET /api/v1/permissions`

Supports query parameters: `agent_id`, `policy_id`.

```javascript
const response = await fetch(
  `${API_BASE_URL}/api/v1/permissions?agent_id=${agentId}`,
  { headers: { Authorization: `Bearer ${token}` } }
);
const permissions = await response.json();
```

**Get Permission** — `GET /api/v1/permissions/{id}`

### 7. Action Validation

Validate whether an agent is permitted to perform an action. Runs for both advisory (EOA) and enforced (smart account) agents.

**Validate Action** — `POST /api/v1/validate`

```javascript
const result = await fetch(`${API_BASE_URL}/api/v1/validate`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    agent_id: "agent-uuid",
    action: {
      type: "swap",
      token: "0xA0b8...eB48",
      protocol: "0x7a25...3e6F",
      amount: "500000000000000000",
      chain: 8453,
      to: "0xDef1...C0de",
    },
  }),
}).then((r) => r.json());
// result.allowed — boolean
// result.reason — explanation if denied
// result.permission_id — matching permission
// result.policy_id — matching policy
// result.constraints — active constraints
// result.request_id — audit trail reference
```

For enforced (smart account) agents, validation acts as a pre-flight check before on-chain execution. The on-chain `PermissionEnforcer` performs the final enforcement in `validateUserOp`.

**Simulate Action** — `POST /api/v1/validate/simulate`

Same input as validate, but returns current usage and remaining quota without recording a validation request.

```javascript
const sim = await fetch(`${API_BASE_URL}/api/v1/validate/simulate`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    agent_id: "agent-uuid",
    action: { type: "transfer", amount: "1000000000000000000", chain: 1 },
  }),
}).then((r) => r.json());
// sim.would_allow — boolean
// sim.reason — explanation
// sim.matching_policy — policy ID if matched
// sim.current_usage — current period usage
// sim.remaining_quota — remaining allowance
// sim.recommendations — suggested adjustments
```

**Batch Validate** — `POST /api/v1/validate/batch`

Validate multiple actions in a single request.

### 8. Audit & Monitoring

Query the immutable audit trail for policy, permission, and validation events.

**List Audit Logs** — `GET /api/v1/audit`

Supports query parameters: `event_type`, `agent_id`, `policy_id`, `start_date`, `end_date`, `limit`, `offset`.

```javascript
const logs = await fetch(
  `${API_BASE_URL}/api/v1/audit?event_type=policy.activated&start_date=2025-01-01T00:00:00Z`,
  { headers: { Authorization: `Bearer ${token}` } }
).then((r) => r.json());
```

Event types: `policy.created`, `policy.activated`, `policy.revoked`, `permission.created`, `permission.minted`, `permission.revoked`, `validation.request`.

**Export Audit Logs** — `GET /api/v1/audit/export`

Supports `format=json` or `format=csv`, plus `start_date` and `end_date` parameters.

```javascript
const exportUrl = `${API_BASE_URL}/api/v1/audit/export?format=csv&start_date=2025-01-01`;
// Download or redirect to this URL
```

## Enforcement Model

The system supports two enforcement tiers based on agent wallet type:

### Advisory (EOA Agents)

- Off-chain validation via `/api/v1/validate` logs actions and returns allow/deny decisions.
- The backend **cannot prevent** on-chain execution for EOA wallets.
- Use validation results for dashboards, alerts, and compliance monitoring.
- Violations are recorded in audit logs for review.

### Enforced (Smart Account Agents)

- `AgentSmartAccount.validateUserOp()` calls `PermissionEnforcer` on-chain.
- Transactions that violate policy constraints **revert before execution**.
- The agent cannot bypass enforcement — it is built into the account's validation logic.
- Off-chain validation still runs for dashboards, simulation, and pre-flight checks.

### Which Tier Applies?

| Agent Type | Enforcement | On-Chain Prevention | Off-Chain Validation |
|------------|-------------|--------------------|--------------------|
| EOA | Advisory | No | Yes |
| Smart Account | Enforced | Yes | Yes |

Upgrading from EOA to smart account is one-way via `POST /api/v1/agents/{id}/upgrade-to-smart-account`.

## Fee Structure

### Account Creation Fee

- **Amount:** $10 USD equivalent in ETH
- **When:** One-time, at smart account deployment
- **Enforced in:** AgentAccountFactory contract
- **Paid to:** Fee collector address via GuardrailFeeManager

### Transfer Fee (Outbound Only)

- **Rate:** 10 basis points (0.10%)
- **Cap:** $100 USD equivalent per transaction
- **When:** On every `execute()` or `executeBatch()` call with `value > 0`
- **Not charged on:**
  - Inbound deposits
  - Zero-value calls
  - ERC-20 transfers encoded in calldata

| Transfer Amount | Fee | Notes |
|----------------|-----|-------|
| $1,000 | $1 | |
| $10,000 | $10 | |
| $100,000 | $100 | Cap reached |
| $2,000,000 | $100 | Cap applies |

## Smart Contract Addresses

### Base Mainnet (Chain ID 8453)

| Contract | Address |
|----------|---------|
| IdentityRegistry | `0xc1fa477f991C74Cc665E605fC74f0e2B795b5104` |
| PolicyRegistry | `0x92cd41e6a4aA13072CeBCda8830d48f269F058c4` |
| PermissionEnforcer | `0xbF63Fa97cfBba99647B410f205730d63d831061c` |
| PriceOracle | `0xf3c8c6BDc54C60EDaE6AE84Ef05B123597C355B3` |
| GuardrailFeeManager | `0xD1B7Bd65F2aB60ff84CdDF48f306a599b01d293A` |
| AgentAccountFactory | `0xCE621A324A8cb40FD424EB0D41286A97f6a6c91C` |
| EntryPoint (v0.6) | `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` |

### Sepolia (Chain ID 11155111)

| Contract | Address |
|----------|---------|
| IdentityRegistry | `0xc1fa477f991C74Cc665E605fC74f0e2B795b5104` |
| PolicyRegistry | `0x92cd41e6a4aA13072CeBCda8830d48f269F058c4` |
| PermissionEnforcer | `0x94991827135fbd0E681B3db51699e4988a7752f1` |
| PriceOracle | `0x052cDddba3C55A63F5e48F9e5bC6b70604Db93b8` |
| GuardrailFeeManager | `0x0f77fdD1AFCe0597339dD340E738CE3dC9A5CC12` |
| AgentAccountFactory | `0xA831229B58C05d5bA9ac109f3B29e268A0e5F41E` |
| EntryPoint (v0.6) | `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789` |

## Dashboard

All API operations documented above are also available via the web dashboard at **https://agentguardrail.xyz/**, which provides a visual interface for managing agents, policies, permissions, and audit logs.

If using dashboard-generated signer keypairs or API keys:

- Store them in secure secret storage
- Never paste them into chat
- Prefer external signer or hardware-backed signing

## Autonomy & Safety Guidance

Because this skill can move funds on-chain:

1. Start on Sepolia testnet.
2. Fund accounts with small amounts initially.
3. Use strict Guardrail policies.
4. Enable autonomous execution only with secure signing configured.
5. Apply rate limits and allowlists at the signer layer.

## Privacy and Data Handling

- This skill does not store, log, or transmit private keys, seed phrases, or signer tokens.
- `GUARDRAIL_RPC_URL` may contain an embedded API key (common with hosted RPC providers). Treat it as sensitive.
- `GUARDRAIL_SIGNER_AUTH_TOKEN` grants signing capability when combined with the signer endpoint. It must be stored in secure secret storage and never exposed in logs, prompts, or chat.
- On-chain transactions are public by nature. The skill does not add any off-chain data collection beyond what the blockchain records.
- The skill does not access local files, browser storage, or environment variables beyond those declared in the manifest metadata.

## Design Principles

1. **Policy-Bound by Default** — Every account is bound to a Guardrail policy at creation.
2. **Agent and Human Neutral** — Authority derives from ownership and policy, not caller identity.
3. **Non-Custodial** — Guardrail never holds funds.
4. **Infrastructure First** — Fees are enforced at the contract layer. The API cannot bypass protocol economics.
5. **Least Privilege** — Signing must use scoped, secure integrations.
