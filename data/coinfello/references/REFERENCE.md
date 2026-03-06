# CoinFello CLI Reference

## Config File

Location: `~/.clawdbot/skills/coinfello/config.json`

Created automatically by `create_account`. Schema:

```json
{
  "private_key": "0xabc123...def",
  "smart_account_address": "0x1234...abcd",
  "chain": "sepolia",
  "session_token": "...",
  "delegation": {
    "delegate": "0x...",
    "delegator": "0x...",
    "authority": "0x...",
    "caveats": [],
    "salt": "0x...",
    "signature": "0x..."
  }
}
```

| Field                   | Type     | Set by           | Description                                    |
| ----------------------- | -------- | ---------------- | ---------------------------------------------- |
| `private_key`           | `string` | `create_account` | Auto-generated hex private key                 |
| `smart_account_address` | `string` | `create_account` | Counterfactual address of the smart account    |
| `chain`                 | `string` | `create_account` | viem chain name used for account creation      |
| `session_token`         | `string` | `sign_in`        | SIWE session token for authenticated API calls |
| `delegation`            | `object` | `set_delegation` | Optional stored delegation                     |

## Command Reference

### npx @coinfello/agent-cli create_account

```
npx @coinfello/agent-cli create_account <chain>
```

| Parameter | Type     | Required | Description                 |
| --------- | -------- | -------- | --------------------------- |
| `chain`   | `string` | Yes      | viem chain name (see below) |

Generates a new private key automatically and saves it along with the smart account address and chain to config.

### npx @coinfello/agent-cli get_account

```
npx @coinfello/agent-cli get_account
```

No parameters. Prints the stored smart account address from config. Exits with an error if no account has been created.

### npx @coinfello/agent-cli sign_in

```
npx @coinfello/agent-cli sign_in [--base-url <url>]
```

| Parameter    | Type     | Required | Default                         | Description                                                                         |
| ------------ | -------- | -------- | ------------------------------- | ----------------------------------------------------------------------------------- |
| `--base-url` | `string` | No       | `${COINFELLO_BASE_URL}api/auth` | Auth server base URL. `COINFELLO_BASE_URL` defaults to `https://app.coinfello.com/` |

The default resolves using the `COINFELLO_BASE_URL` environment variable (defaults to `https://app.coinfello.com/`).

Performs a Sign-In with Ethereum (SIWE) flow using the private key from config. Saves the `session_token` to config on success. The session token is automatically injected as a cookie for subsequent API calls.

### npx @coinfello/agent-cli set_delegation

```
npx @coinfello/agent-cli set_delegation <delegation>
```

| Parameter    | Type     | Required | Description                                                     |
| ------------ | -------- | -------- | --------------------------------------------------------------- |
| `delegation` | `string` | Yes      | JSON-encoded Delegation object from MetaMask Smart Accounts Kit |

### npx @coinfello/agent-cli send_prompt

```
npx @coinfello/agent-cli send_prompt <prompt>
```

| Parameter | Type     | Required | Default | Description                                  |
| --------- | -------- | -------- | ------- | -------------------------------------------- |
| `prompt`  | `string` | Yes      | —       | Natural language prompt to send to CoinFello |

The server determines whether a delegation is needed and, if so, what scope and chain to use. The client creates and signs the subdelegation based on the server's `ask_for_delegation` client tool call response. Each subdelegation is created with a unique random salt to ensure delegation uniqueness.

**ERC-6492 signature wrapping**: If the smart account has not yet been deployed on-chain, the CLI wraps the delegation signature using ERC-6492 (`serializeErc6492Signature`) with the account's factory address and factory data. This allows the delegation to be verified even before the account contract exists.

### npx @coinfello/agent-cli get_transaction_status

```
npx @coinfello/agent-cli get_transaction_status <txn_id>
```

| Parameter | Type     | Required | Description                     |
| --------- | -------- | -------- | ------------------------------- |
| `txn_id`  | `string` | Yes      | Transaction ID from send_prompt |

## Supported Chains

Any chain exported by `viem/chains`. Common examples:

| Chain Name  | Chain ID | Network                  |
| ----------- | -------- | ------------------------ |
| `mainnet`   | 1        | Ethereum mainnet         |
| `sepolia`   | 11155111 | Ethereum Sepolia testnet |
| `polygon`   | 137      | Polygon PoS              |
| `arbitrum`  | 42161    | Arbitrum One             |
| `optimism`  | 10       | OP Mainnet               |
| `base`      | 8453     | Base                     |
| `avalanche` | 43114    | Avalanche C-Chain        |
| `bsc`       | 56       | BNB Smart Chain          |

## API Endpoints

Base URL: Configured via the `COINFELLO_BASE_URL` environment variable (defaults to `https://app.coinfello.com/`).

| Endpoint                                 | Method | Description                                          |
| ---------------------------------------- | ------ | ---------------------------------------------------- |
| `/api/v1/automation/coinfello-address`   | GET    | Returns CoinFello's delegate address                 |
| `/api/v1/automation/coinfello-agents`    | GET    | Returns available CoinFello agents (id, name)        |
| `/api/conversation`                      | POST   | Submits prompt (and optionally client tool response) |
| `/api/v1/transaction_status?txn_id=<id>` | GET    | Returns transaction status                           |

### GET /api/v1/automation/coinfello-agents response

```json
{
  "availableAgents": [{ "id": 1, "name": "CoinFello Agent" }]
}
```

The `send_prompt` command fetches this list and uses the first agent's `id` as `agentId` in conversation requests.

### POST /api/conversation body

Initial request (prompt only):

```json
{
  "inputMessage": "send 5 USDC to 0xRecipient...",
  "agentId": 1,
  "stream": false
}
```

`agentId` is dynamically resolved from the `/api/v1/automation/coinfello-agents` endpoint (not hardcoded).

The follow-up request (sending the signed delegation back) is handled internally by `send_prompt` — no manual construction is needed.

### POST /api/conversation response

Read-only response:

```json
{
  "responseText": "The chain ID for Base is 8453."
}
```

Delegation request (server asks client to sign):

```json
{
  "clientToolCalls": [
    {
      "type": "function_call",
      "name": "ask_for_delegation",
      "callId": "call_abc123...",
      "arguments": "{\"chainId\": 8453, \"scope\": {\"type\": \"erc20TransferAmount\", \"tokenAddress\": \"0x...\", \"maxAmount\": \"5000000\"}}"
    }
  ],
  "chatId": "chat_abc123..."
}
```

Final response (after delegation submitted):

```json
{
  "txn_id": "abc123..."
}
```

| Field             | Type      | Description                                                    |
| ----------------- | --------- | -------------------------------------------------------------- |
| `responseText`    | `string?` | Text response for read-only prompts                            |
| `txn_id`          | `string?` | Transaction ID when a transaction has been submitted           |
| `clientToolCalls` | `array?`  | Server-requested client tool calls (e.g. `ask_for_delegation`) |
| `chatId`          | `string?` | Chat session ID, sent back in follow-up requests               |

## Delegation Scope Types

The server may request any of the following scope types via `ask_for_delegation`. The CLI parses and creates the appropriate delegation caveat automatically.

| Scope Type                  | Fields                                                                       |
| --------------------------- | ---------------------------------------------------------------------------- |
| `erc20TransferAmount`       | `tokenAddress`, `maxAmount`                                                  |
| `erc20PeriodTransfer`       | `tokenAddress`, `periodAmount`, `periodDuration`, `startDate`                |
| `erc20Streaming`            | `tokenAddress`, `initialAmount`, `maxAmount`, `amountPerSecond`, `startTime` |
| `nativeTokenTransferAmount` | `maxAmount`                                                                  |
| `nativeTokenPeriodTransfer` | `periodAmount`, `periodDuration`, `startDate`                                |
| `nativeTokenStreaming`      | `initialAmount`, `maxAmount`, `amountPerSecond`, `startTime`                 |
| `erc721Transfer`            | `tokenAddress`, `tokenId`                                                    |
| `functionCall`              | `targets`, `selectors`                                                       |

All `amount` fields are in the token's smallest unit (e.g. `5000000` for 5 USDC with 6 decimals).

## Common Token Decimals

| Token | Decimals | Note                          |
| ----- | -------- | ----------------------------- |
| USDC  | 6        | amounts use 6 decimal places  |
| USDT  | 6        | amounts use 6 decimal places  |
| DAI   | 18       | amounts use 18 decimal places |
| WETH  | 18       | amounts use 18 decimal places |

## Environment Variables

| Variable             | Required | Default                      | Description                    |
| -------------------- | -------- | ---------------------------- | ------------------------------ |
| `COINFELLO_BASE_URL` | No       | `https://app.coinfello.com/` | Base URL for the CoinFello API |

## Security Considerations

- **Private key storage**: `create_account` generates and stores a private key in plaintext at `~/.clawdbot/skills/coinfello/config.json`. Restrict file permissions (e.g. `chmod 600`) and do not share or commit this file.
- **Session token storage**: `sign_in` stores a SIWE session token in the same config file.
- **Automatic delegation signing**: `send_prompt` may create and sign delegations based on scopes requested by the server, then submit them to the CoinFello API endpoint. Ensure the `COINFELLO_BASE_URL` points to a trusted endpoint before running delegation flows.

## Error Messages

| Error                                                         | Cause                               | Fix                                                   |
| ------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------- |
| `Unknown chain "<name>"`                                      | Invalid chain name                  | Use a valid viem chain name                           |
| `No private key found in config. Run 'create_account' first.` | Missing private key in config       | Run `npx @coinfello/agent-cli create_account <chain>` |
| `No smart account found. Run 'create_account' first.`         | Missing smart account in config     | Run `npx @coinfello/agent-cli create_account <chain>` |
| `No chain found in config. Run 'create_account' first.`       | Missing chain in config             | Run `npx @coinfello/agent-cli create_account <chain>` |
| `No delegation request received from the server.`             | Server returned unexpected response | Check the full response JSON printed                  |
