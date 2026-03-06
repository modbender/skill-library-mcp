---
name: Vincent - A wallet for agents
description: |
  The agent's wallet for EVM chain transactions and raw signing. Use this skill when users want to
  create a wallet, transfer tokens, swap on DEXs, interact with smart contracts, or sign messages.
  Triggers on "wallet", "create wallet", "transfer ETH", "swap tokens", "send transaction",
  "check balance", "EVM wallet", "raw signer", "sign message".
allowed-tools: Read, Write, Bash(npx:@vincentai/cli*)
version: 1.0.0
author: HeyVincent <contact@heyvincent.ai>
license: MIT
homepage: https://heyvincent.ai
source: https://github.com/HeyVincent-ai/Vincent
metadata:
  clawdbot:
    homepage: https://heyvincent.ai
    requires:
      config:
        - ${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/agentwallet
        - ./agentwallet
---

# Vincent - A wallet for agents

Use this skill to safely create a wallet the agent can use for transfers, swaps, and any EVM chain transaction without ever exposing private keys to the agent. Create a wallet, set spending policies, and your agent can transfer tokens, do swaps, and interact with smart contracts within the boundaries you define.

**The agent never sees the private key.** All transactions are executed server-side through a ZeroDev smart account. The agent receives a scoped API key that can only perform actions permitted by the wallet owner's policies. The private key never leaves the Vincent server.

All commands use the `@vincentai/cli` package. API keys are stored and resolved automatically — you never handle raw keys or file paths.

## Security Model

This skill is designed for **autonomous agent operation with human oversight via server-side controls**. Understanding this model is important:

**No environment variables are required** because this skill uses agent-first onboarding: the agent creates its own wallet at runtime by calling the Vincent API, which returns a scoped API key. There is no pre-existing credential to configure. The CLI stores the returned API key automatically during wallet creation. The config paths where the key is persisted (`${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/agentwallet/` or `./agentwallet/`) are declared in this skill's metadata.

**The agent's API key is not a private key.** It is a scoped Bearer token that can only execute transactions within the policies set by the wallet owner. The Vincent server enforces all policies server-side — the agent cannot bypass them regardless of what it sends. If a transaction violates a policy, the server rejects it. If a transaction requires approval, the server holds it and notifies the wallet owner via Telegram for out-of-band human approval.

**Model invocation is intentionally enabled.** The purpose of this skill is to give AI agents autonomous wallet capabilities. The agent is expected to invoke wallet actions (transfers, swaps, contract calls) on its own, within the boundaries the human operator defines. The human controls what the agent can do through policies (spending limits, address allowlists, token allowlists, function allowlists, approval thresholds) — not by gating individual invocations. The stored key is scoped and policy-constrained — even if another process reads it, it can only perform actions the wallet owner's policies allow, and the owner can revoke it instantly.

**All API calls go exclusively to `heyvincent.ai`** over HTTPS/TLS. No other endpoints, services, or external hosts are contacted. The agent does not read, collect, or transmit any data beyond what is needed for wallet operations.

**Vincent is open source and audited.** The server-side code that enforces policies, manages private keys, and executes transactions is publicly auditable at [github.com/HeyVincent-ai/Vincent](https://github.com/HeyVincent-ai/Vincent). The Vincent backend undergoes continuous security audits covering key management, policy enforcement, transaction signing, and API authentication. You can verify how policy enforcement works, how private keys are stored, how the scoped API key is validated, and how revocation is handled — nothing is opaque. If you want to self-host Vincent rather than trust the hosted service, the repository includes deployment instructions.

**Key lifecycle:**

- **Creation**: The agent runs `secret create` — the CLI stores the API key automatically and returns a `keyId` and `claimUrl`.
- **Claim**: The human operator uses the claim URL to take ownership and configure policies.
- **Revocation**: The wallet owner can revoke the agent's API key at any time from `https://heyvincent.ai`. Revoked keys are rejected immediately by the server.
- **Re-linking**: If the agent loses its API key, the wallet owner generates a one-time re-link token and the agent exchanges it for a new key via `secret relink`.
- **Rotation**: The wallet owner can revoke the current key and issue a re-link token to rotate credentials at any time.

## Which Secret Type to Use

| Type         | Use Case                                  | Network                 | Gas              |
| ------------ | ----------------------------------------- | ----------------------- | ---------------- |
| `EVM_WALLET` | Transfers, swaps, DeFi, contract calls    | Any EVM chain           | Sponsored (free) |
| `RAW_SIGNER` | Raw message signing for special protocols | Any (Ethereum + Solana) | You pay          |

**Choose `EVM_WALLET`** (default) for:

- Sending ETH or tokens
- Swapping tokens on DEXs
- Interacting with smart contracts
- Any standard EVM transaction

**Choose `RAW_SIGNER`** only when you need:

- Raw ECDSA/Ed25519 signatures for protocols that don't work with smart accounts
- To sign transaction hashes you'll broadcast yourself
- Solana signatures

## Quick Start

### 1. Check for Existing Keys

Before creating a new wallet, check if one already exists:

```bash
npx @vincentai/cli@latest secret list --type EVM_WALLET
```

If a key is returned, use its `id` as the `--key-id` for all subsequent commands. If no keys exist, create a new wallet.

### 2. Create a Wallet

```bash
npx @vincentai/cli@latest secret create --type EVM_WALLET --memo "My agent wallet" --chain-id 84532
```

Returns `keyId` (use for all future commands), `claimUrl` (share with the user), and `address`.

After creating, tell the user:

> "Here is your wallet claim URL: `<claimUrl>`. Use this to claim ownership, set spending policies, and monitor your agent's wallet activity at https://heyvincent.ai."

### 3. Get Wallet Address

```bash
npx @vincentai/cli@latest wallet address --key-id <KEY_ID>
```

### 4. Check Balances

```bash
# All balances across all supported chains
npx @vincentai/cli@latest wallet balances --key-id <KEY_ID>

# Filter to specific chains
npx @vincentai/cli@latest wallet balances --key-id <KEY_ID> --chain-ids 1,137,42161
```

Returns all ERC-20 tokens and native balances with symbols, decimals, logos, and USD values.

### 5. Transfer ETH or Tokens

```bash
# Transfer native ETH
npx @vincentai/cli@latest wallet transfer --key-id <KEY_ID> --to 0xRecipient --amount 0.01

# Transfer ERC-20 token
npx @vincentai/cli@latest wallet transfer --key-id <KEY_ID> --to 0xRecipient --amount 100 --token 0xTokenAddress
```

If the transaction violates a policy, the server returns an error explaining which policy was triggered. If the transaction requires human approval (based on the approval threshold policy), the server returns `status: "pending_approval"` and the wallet owner receives a Telegram notification to approve or deny.

### 6. Swap Tokens

Swap one token for another using DEX liquidity (powered by 0x).

```bash
# Preview a swap (no execution, just pricing)
npx @vincentai/cli@latest wallet swap preview --key-id <KEY_ID> \
  --sell-token 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE \
  --buy-token 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  --sell-amount 0.1 --chain-id 1

# Execute a swap
npx @vincentai/cli@latest wallet swap execute --key-id <KEY_ID> \
  --sell-token 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE \
  --buy-token 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  --sell-amount 0.1 --chain-id 1 --slippage 100
```

- Use `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE` for native ETH.
- `--sell-amount`: Human-readable amount (e.g. `0.1` for 0.1 ETH).
- `--chain-id`: 1 = Ethereum, 137 = Polygon, 42161 = Arbitrum, 10 = Optimism, 8453 = Base, etc.
- `--slippage`: Slippage tolerance in basis points (100 = 1%). Defaults to 100. Execute only.

The preview returns expected buy amount, route info, and fees without executing. Execute performs the actual swap, handling ERC20 approvals automatically.

### 7. Send Arbitrary Transaction

Interact with any smart contract by sending custom calldata.

```bash
npx @vincentai/cli@latest wallet send-tx --key-id <KEY_ID> --to 0xContract --data 0xCalldata --value 0
```

### 8. Transfer Between Your Secrets

Transfer funds between Vincent secrets you own (e.g., from one EVM wallet to another, or to a Polymarket wallet). Vincent verifies you own both secrets and handles any token conversion or cross-chain bridging automatically.

```bash
# Preview (get quote without executing)
npx @vincentai/cli@latest wallet transfer-between preview --key-id <KEY_ID> \
  --to-secret-id <DEST_SECRET_ID> --from-chain 8453 --to-chain 8453 \
  --token-in ETH --amount 0.1 --token-out ETH

# Execute
npx @vincentai/cli@latest wallet transfer-between execute --key-id <KEY_ID> \
  --to-secret-id <DEST_SECRET_ID> --from-chain 8453 --to-chain 8453 \
  --token-in ETH --amount 0.1 --token-out ETH --slippage 100

# Check cross-chain transfer status
npx @vincentai/cli@latest wallet transfer-between status --key-id <KEY_ID> --relay-id <RELAY_REQUEST_ID>
```

**Behavior:**

- **Same token + same chain**: Executes as a direct transfer (gas sponsored).
- **Different token or chain**: Uses a relay service for atomic swap + bridge.
- The destination secret can be an `EVM_WALLET` or `POLYMARKET_WALLET`.
- The server verifies you own both the source and destination secrets — transfers to secrets you don't own are rejected.
- Transfers are subject to the same server-side policies as regular transfers (spending limits, approval thresholds, etc.).

## Output Format

CLI commands return JSON to stdout. Successful responses include the relevant data:

```json
{
  "address": "0x...",
  "balances": [
    {
      "token": "ETH",
      "balance": "0.5",
      "usdValue": "1250.00"
    }
  ]
}
```

Transaction commands return:

```json
{
  "transactionHash": "0x...",
  "status": "confirmed"
}
```

For transactions requiring human approval:

```json
{
  "status": "pending_approval",
  "message": "Transaction requires owner approval via Telegram"
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Check that the key-id is correct; re-link if needed |
| `403 Policy Violation` | Transaction blocked by server-side policy | User must adjust policies at heyvincent.ai |
| `400 Insufficient Balance` | Not enough tokens for the transfer | Check balances before transferring |
| `429 Rate Limited` | Too many requests | Wait and retry with backoff |
| `pending_approval` | Transaction exceeds approval threshold | User will receive Telegram notification to approve/deny |
| `Key not found` | API key was revoked or never created | Re-link with a new token from the wallet owner |

If a transaction is rejected, inform the user to check their policy settings at `https://heyvincent.ai`.

## Policies (Server-Side Enforcement)

The wallet owner controls what the agent can do by setting policies via the claim URL at `https://heyvincent.ai`. All policies are enforced server-side by the Vincent API — the agent cannot bypass or modify them. If a transaction violates a policy, the API rejects it. If a transaction triggers an approval threshold, the API holds it and sends the wallet owner a Telegram notification for out-of-band human approval. The policy enforcement logic is open source and auditable at [github.com/HeyVincent-ai/Vincent](https://github.com/HeyVincent-ai/Vincent).

| Policy                      | What it does                                                        |
| --------------------------- | ------------------------------------------------------------------- |
| **Address allowlist**       | Only allow transfers/calls to specific addresses                    |
| **Token allowlist**         | Only allow transfers of specific ERC-20 tokens                      |
| **Function allowlist**      | Only allow calling specific contract functions (by 4-byte selector) |
| **Spending limit (per tx)** | Max USD value per transaction                                       |
| **Spending limit (daily)**  | Max USD value per rolling 24 hours                                  |
| **Spending limit (weekly)** | Max USD value per rolling 7 days                                    |
| **Require approval**        | Every transaction needs human approval via Telegram                 |
| **Approval threshold**      | Transactions above a USD amount need human approval via Telegram    |

Before the wallet is claimed, the agent can operate without policy restrictions. This is by design: agent-first onboarding allows the agent to begin accumulating and managing funds immediately. Once the human operator claims the wallet via the claim URL, they can add any combination of policies to constrain the agent's behavior. The wallet owner can also revoke the agent's API key entirely at any time.

## Re-linking (Recovering API Access)

If the agent loses its API key, the wallet owner can generate a **re-link token** from the frontend. The agent then exchanges this token for a new API key.

**How it works:**

1. The user generates a re-link token from the wallet detail page at `https://heyvincent.ai`
2. The user gives the token to the agent (e.g. by pasting it in chat)
3. The agent runs the relink command:

```bash
npx @vincentai/cli@latest secret relink --token <TOKEN_FROM_USER>
```

The CLI exchanges the token for a new API key, stores it automatically, and returns the new `keyId`. Use this `keyId` for all subsequent commands.

**Important:** Re-link tokens are one-time use and expire after 10 minutes.

## Important Notes

- **No gas needed.** A paymaster is fully set up — all transaction gas fees are sponsored automatically. The wallet does not need ETH for gas.
- **Never try to access raw secret values.** The private key stays server-side — that's the whole point.
- Always share the claim URL with the user after creating a wallet.
- If a transaction is rejected, it may be blocked by a server-side policy. Tell the user to check their policy settings at `https://heyvincent.ai`.
- If a transaction requires approval, it will return `status: "pending_approval"`. The wallet owner will receive a Telegram notification to approve or deny.

---

## Raw Signer (Advanced)

For raw ECDSA/Ed25519 signing when smart accounts won't work.

### Create a Raw Signer

```bash
npx @vincentai/cli@latest secret create --type RAW_SIGNER --memo "My raw signer"
```

Response includes both Ethereum (secp256k1) and Solana (ed25519) addresses derived from the same seed.

### Get Addresses

```bash
npx @vincentai/cli@latest raw-signer addresses --key-id <KEY_ID>
```

Returns `ethAddress` and `solanaAddress`.

### Sign a Message

```bash
npx @vincentai/cli@latest raw-signer sign --key-id <KEY_ID> --message 0x<hex-encoded-bytes> --curve ethereum
```

- `--message`: Hex-encoded bytes to sign (must start with `0x`)
- `--curve`: `ethereum` for secp256k1 ECDSA, `solana` for ed25519

Returns a hex-encoded signature. For Ethereum, this is `r || s || v` (65 bytes). For Solana, it's a 64-byte ed25519 signature.
