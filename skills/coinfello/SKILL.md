---
name: coinfello
description: 'Interact with CoinFello using the @coinfello/agent-cli to create MetaMask smart accounts, sign in with SIWE, manage delegations, send prompts with server-driven ERC-20 token subdelegations, and check transaction status. Use when the user wants to send crypto transactions via natural language prompts, manage smart account delegations, or check CoinFello transaction results.'
compatibility: Requires Node.js 20+ (npx is included with Node.js).
metadata:
  clawdbot:
    emoji: '👋'
    homepage: 'https://coinfello.com'
    requires:
      bins: ['node', 'npx']
      env:
        - name: COINFELLO_BASE_URL
          description: 'Base URL for the CoinFello API server'
          required: false
          default: 'https://app.coinfello.com/'
---

# CoinFello CLI Skill

Use the `npx @coinfello/agent-cli` CLI to interact with CoinFello through MetaMask Smart Accounts. The CLI handles smart account creation, SIWE authentication, delegation management, prompt-based transactions, and transaction status checks.

## Prerequisites

- Node.js 20 or later (npx is included with Node.js)

The CLI is available via `npx @coinfello/agent-cli`. No manual build step is required.

## Environment Variables

| Variable             | Required | Default                      | Description                    |
| -------------------- | -------- | ---------------------------- | ------------------------------ |
| `COINFELLO_BASE_URL` | No       | `https://app.coinfello.com/` | Base URL for the CoinFello API |

## Security Notice

This skill performs the following sensitive operations:

- **Private key generation and storage**: Running `create_account` generates a new private key and stores it **in plaintext** at `~/.clawdbot/skills/coinfello/config.json`. Protect this file accordingly.
- **Session token storage**: Running `sign_in` stores a SIWE session token in the same config file.
- **Delegation signing**: Running `send_prompt` may automatically create and sign blockchain delegations based on server-requested scopes, then submit them to the CoinFello API.

Users should ensure they trust the CoinFello API endpoint configured via `COINFELLO_BASE_URL` before running delegation flows.

## Quick Start

```bash
# 1. Create a smart account on a chain (generates a new private key automatically)
npx @coinfello/agent-cli create_account sepolia

# 2. Sign in to CoinFello with your smart account (SIWE)
npx @coinfello/agent-cli sign_in

# 3. Send a natural language prompt — the server will request a delegation if needed
npx @coinfello/agent-cli send_prompt "send 5 USDC to 0xRecipient..."

# 4. Check transaction status
npx @coinfello/agent-cli get_transaction_status <txn_id>
```

## Commands

### create_account

Creates a MetaMask Hybrid smart account with an auto-generated private key and saves it to local config.

```bash
npx @coinfello/agent-cli create_account <chain>
```

- `<chain>` — A viem chain name: `sepolia`, `mainnet`, `polygon`, `arbitrum`, `optimism`, `base`, etc.
- Generates a new private key automatically
- Saves `private_key`, `smart_account_address`, and `chain` to `~/.clawdbot/skills/coinfello/config.json`
- Must be run before `send_prompt`

### get_account

Displays the current smart account address from local config.

```bash
npx @coinfello/agent-cli get_account
```

- Prints the stored `smart_account_address`
- Exits with an error if no account has been created yet

### sign_in

Authenticates with CoinFello using Sign-In with Ethereum (SIWE) and your smart account. Saves the session token to local config.

```bash
npx @coinfello/agent-cli sign_in
```

- Signs in using the private key stored in config
- Saves the session token to `~/.clawdbot/skills/coinfello/config.json`
- The session token is loaded automatically for subsequent `send_prompt` calls
- Must be run after `create_account` and before `send_prompt` for authenticated flows

### set_delegation

Stores a signed parent delegation (JSON) in local config.

```bash
npx @coinfello/agent-cli set_delegation '<delegation-json>'
```

- `<delegation-json>` — A JSON string representing a `Delegation` object from MetaMask Smart Accounts Kit

### send_prompt

Sends a natural language prompt to CoinFello. If the server requires a delegation to execute the action, the CLI creates and signs a subdelegation automatically based on the server's requested scope and chain.

```bash
npx @coinfello/agent-cli send_prompt "<prompt>"
```

**What happens internally:**

1. Fetches available agents from `/api/v1/automation/coinfello-agents` and sends the prompt to CoinFello's conversation endpoint
2. If the server returns a read-only response (no `clientToolCalls` and no `txn_id`) → prints the response text and exits
3. If the server returns a `txn_id` directly with no tool calls → prints it and exits
4. If the server sends an `ask_for_delegation` client tool call with a `chainId` and `scope`:
   - Fetches CoinFello's delegate address
   - Rebuilds the smart account using the chain ID from the tool call
   - Parses the server-provided scope (supports ERC-20, native token, ERC-721, and function call scopes)
   - Creates and signs a subdelegation (wraps with ERC-6492 signature if the smart account is not yet deployed on-chain)
   - Sends the signed delegation back as a `clientToolCallResponse` along with the `chatId` and `callId` from the initial response
   - Returns a `txn_id` for tracking

### get_transaction_status

Checks the status of a previously submitted transaction.

```bash
npx @coinfello/agent-cli get_transaction_status <txn_id>
```

- Returns a JSON object with the current transaction status

## Common Workflows

### Basic: Send a Prompt (Server-Driven Delegation)

```bash
# Create account if not already done
npx @coinfello/agent-cli create_account sepolia

# Sign in (required for delegation flows)
npx @coinfello/agent-cli sign_in

# Send a natural language prompt — delegation is handled automatically
npx @coinfello/agent-cli send_prompt "send 5 USDC to 0xRecipient..."

# Check the result
npx @coinfello/agent-cli get_transaction_status <txn_id-from-above>
```

### Read-Only Prompt

Some prompts don't require a transaction. The CLI detects this automatically and just prints the response.

```bash
npx @coinfello/agent-cli send_prompt "what is the chain ID for Base?"
```

## Edge Cases

- **No smart account**: Run `create_account` before `send_prompt`. The CLI checks for a saved private key and address in config.
- **Not signed in**: Run `sign_in` before `send_prompt` if the server requires authentication.
- **Invalid chain name**: The CLI throws an error listing valid viem chain names.
- **Read-only response**: If the server returns a text response with no transaction, the CLI prints it and exits without creating a delegation.

## Reference

See [references/REFERENCE.md](references/REFERENCE.md) for the full config schema, supported chains, API details, scope types, and troubleshooting.

See [scripts/setup-and-send.sh](scripts/setup-and-send.sh) for an end-to-end automation script.
