# nova CLI

`nova` is a CLI wallet for managing balances, sending funds, and
withdrawing stablecoins across supported blockchains.

It requires **Node.js 24+** as a prerequisite.

If `nova` is not installed, you can install it via:

``` bash
npm install -g @mynthai/nova
```

Or run without installing via npx (replace all `nova` usage with
`npx @mynthai/nova`).

It supports:

- Email-based login wallets
- Automatically generated private-key wallets (default if not logged in)
- Multiple blockchains (e.g., base, solana, sui, etc.)
- Human-readable, JSON, and TOON output formats

## Core Concepts

### Wallet Types

1.  **Email Wallet**

    - Created via the `nova login` flow (email + verification code)
    - Linked to user email
    - Suitable for interactive human users

2.  **Private-Key Wallet (Default)**

    - Automatically created if no login is performed

    - Must be backed up manually

    - Users should be advised to:

      - `nova export key`
      - or `nova export phrase`

⚠️ If user is using a private key wallet, always suggest backing up the
private key or mnemonic.

## Output Modes

| Mode           | Flag      | Use Case                            |
|----------------|-----------|-------------------------------------|
| Human-readable | (default) | Interactive CLI usage               |
| JSON           | `-j`      | Automation / programmatic parsing   |
| TOON           | `-t`      | Structured terminal-friendly output |

Agents should prefer `-j` or `-t` for deterministic parsing.

## Exit Codes

`nova` uses only two exit codes:

| Exit Code | Meaning |
|-----------|---------|
| `0`       | Success |
| `1`       | Error   |

Agent guidance:

- Treat exit code `0` as successful execution (still parse `status`).

- Treat exit code `1` as failure and inspect `error.message`.

- Never assume success without checking both:

  - Process exit code
  - `status` field in structured output (`-j` or `-t`)

## Command Reference

### Authentication

#### Login (Email Wallet)

`nova login` is a **non-interactive 2-step flow**:

1.  Request a code to be sent to the email address
2.  Confirm the code to complete login

##### Step 1 — Request Code

``` bash
nova login request <email>
```

Options:

- `-j, --json` Output results as JSON
- `-t, --toon` Output results as TOON
- `-f, --force` Overwrite existing private key if it exists

Use when:

- User wants account linked to email
- Shared access or recovery needed

##### Step 2 — Confirm Code

``` bash
nova login confirm <code>
```

Options:

- `-j, --json` Output results as JSON
- `-t, --toon` Output results as TOON

Use when:

- User received the 6-character authentication code and wants to finish
  login

Agent guidance:

- Prefer `-j` or `-t` to reliably detect success/failure.
- Do not ask users to paste sensitive information beyond the 6-character
  code.
- If `--force` is used, clearly warn it can overwrite an existing
  private-key wallet.

### Account Information

#### Get Address

``` bash
nova address [blockchain]
```

- Default blockchain: `mynth`
- Supported: `base`, `cardano`, `hyperliquid`, `mynth`, `plasma`,
  `solana`, `stable`, `sui`, `tron`

Use when:

- User needs deposit address
- Withdrawing from external service
- Sharing a wallet address for direct wallet-to-wallet transfers

#### Get Balance

``` bash
nova balance
```

Returns:

- `balance`
- `currency` (always USD)

Example (TOON):

``` bash
nova -t balance
```

### Currency Model

- `balance` is denominated in USD equivalent
- Withdrawals require specifying stablecoin
- Network does not change denomination

### Network Configuration

`nova` operates on either `mainnet` or `testnet`.

- **Default on fresh install:** `testnet`
- **Setting persists across sessions**
- **Funds are isolated per network**
- Addresses and balances are different between networks

#### Get Current Network

``` bash
nova config get network
```

Always check before sending or withdrawing funds.

#### Set Network

``` bash
nova config set network <mainnet|testnet>
```

Examples:

``` bash
nova config set network mainnet
nova config set network testnet
```

Before any financial action (`send`, `withdraw`) agents should:

1.  Check current network.
2.  Confirm intended network with user.
3.  Default to `mainnet` unless user is explicitly testing.

### Sending Funds

#### Send to Email or Wallet Address

``` bash
nova send <amount> [destination]
```

`destination` can be:

- An **email address** (e.g., `user@email.com`)
- A **nova wallet address** (e.g.,
  `pcr6cdcvwjf9297vv6jmy8284xwlscspj2g0fw`)

Behavior:

- If destination omitted → creates claim link
- If destination is an email → sends to that email-linked nova wallet
- If destination is a wallet address → sends directly to that wallet

Email-based sends:

- If the email is already registered with `nova`, funds are delivered
  directly to that wallet.
- If the email is not yet registered, funds are reserved and can be
  claimed once the recipient completes email login.
- No blockchain address is required when sending to email.

Wallet-address sends:

- Must be a valid `nova` wallet address for the current network.
- Always validate format before execution.

⚠️ Non-Interactive Execution Warning. `nova send` executes immediately
and does **not** prompt for confirmation.

- There is **no interactive confirmation step**
- Sends are **not idempotent** (re-running the same command will send
  funds again)
- Use `--dry-run` (`-d`) to validate inputs and preview the transaction
  **without** submitting it

Options:

- `-j, --json` Output results as JSON
- `-t, --toon` Output results as TOON
- `-d, --dry-run` Validate and preview without submitting

Agents must:

- Explicitly confirm amount, destination (email or wallet address), and
  network **before** executing
- Avoid retrying failed sends without verifying transaction status
- Treat every `nova send` call as a final financial action
- Always parse `status` and confirm `sent: true` before assuming success
- If uncertain about execution outcome, call `nova -t balance` to verify

A successful send (TOON example):

``` bash
status: ok
result:
  sent: true
  amount: "1"
  to: pcr6cdcvwjf9297vv6jmy8284xwlscspj2g0fw
```

✅ `nova send` returns a transaction id (`txId`). If a claim link is
created (destination omitted), it also returns `claimUrl`.

Example (TOON):

``` bash
➜ nova -t send 1
status: ok
result:
  sent: true
  amount: "1"
  txId: d32c966fd4302673455eb790b66e3efc331ef7aace412c73b8917ba0bb37ace8
  claimUrl: "https://preview.mynth.ai/c/mto3M1JEa6Hr0UFRCBGjOg"
```

Balance updates immediately after a successful `nova send`, and can be
checked safely using:

``` bash
nova -t balance
```

### Claim Links

When `nova send <amount>` is executed without a destination:

- A **claim link** is generated
- Funds leave the wallet immediately
- The full specified amount is locked for the recipient
- Claim links are **one-time use**
- Claim links **do not expire**

Revocation:

- To revoke a claim link, the creator must claim it themselves (i.e.,
  redeem it back into their own wallet)

Security Considerations:

- Claim URLs grant access to funds
- Treat them as sensitive credentials
- Never log claim URLs in shared or persistent logs

Examples:

Create claim link:

``` bash
nova send 10
```

Send to email:

``` bash
nova send 10 friend@email.com
```

Send to wallet address:

``` bash
nova send 10 pcr6cdcvwjf9297vv6jmy8284xwlscspj2g0fw
```

Dry-run (preview without submitting):

``` bash
nova -j send --dry-run 10 friend@email.com
```

Example dry-run output (JSON):

``` bash
{"result":{"amount":"10","dryRun":true,"to":"friend@email.com"},"status":"ok"}
```

Best Practices for Agents:

- Confirm amount before sending
- Validate destination format (email vs wallet address)
- Prefer structured output (`-j` or `-t`)
- Display claim URL clearly if generated
- Treat `claimUrl` like a secret (don’t paste it into shared channels,
  tickets, or logs)

### Withdraw to External Blockchain

``` bash
nova withdraw <amount> <stablecoin> <address> <blockchain>
```

Options:

- `-j, --json` Output results as JSON
- `-t, --toon` Output results as TOON
- `-d, --dry-run` Validate and preview without submitting

Example:

``` bash
nova withdraw 10 USDC 0x7600eFB256ae7519e73C14a55152B0806b5cfF28 base
```

Dry-run (preview without submitting):

``` bash
nova -j withdraw --dry-run 10 USDC 0x7600eFB256ae7519e73C14a55152B0806b5cfF28 base
```

Example dry-run output (JSON):

``` bash
{"result":{"amount":"10","blockchain":"base","dryRun":true,"stablecoin":"USDC","to":"0x7600eFB256ae7519e73C14a55152B0806b5cfF28"},"status":"ok"}
```

Parameters:

- `amount` — numeric string
- `stablecoin` — e.g., USDC
- `address` — blockchain wallet address
- `blockchain` — required if not inferable

Agent Checklist:

- Verify sufficient balance
- Validate blockchain compatibility
- Confirm stablecoin support
- Confirm network (mainnet/testnet)

✅ `nova withdraw` returns a transaction id (`txId`) in structured
output (TOON/JSON). Agents should capture and surface `txId` to the user
for verification/support workflows.

Balance updates immediately after a successful `nova withdraw`, and can
be verified with:

``` bash
nova -t balance
```

#### Supported Stablecoins

##### Mainnet

| Network     | USDC | USDT | USDA | USDM |
|-------------|:----:|:----:|:----:|:----:|
| Base        |  ✅  |  ❌  |  ❌  |  ❌  |
| Cardano     |  ✅  |  ❌  |  ✅  |  ✅  |
| Hyperliquid |  ✅  |  ❌  |  ❌  |  ❌  |
| Solana      |  ✅  |  ✅  |  ❌  |  ❌  |
| Stable      |  ❌  |  ✅  |  ❌  |  ❌  |
| Sui         |  ✅  |  ❌  |  ❌  |  ❌  |
| Tron        |  ❌  |  ✅  |  ❌  |  ❌  |

##### Testnet

| Network     | USDC | USDT | USDA | USDM |
|-------------|:----:|:----:|:----:|:----:|
| Base        |  ✅  |  ❌  |  ❌  |  ❌  |
| Cardano     |  ✅  |  ❌  |  ✅  |  ✅  |
| Hyperliquid |  ✅  |  ❌  |  ❌  |  ❌  |
| Solana      |  ✅  |  ❌  |  ❌  |  ❌  |
| Stable      |  ❌  |  ✅  |  ❌  |  ❌  |
| Sui         |  ❌  |  ✅  |  ❌  |  ❌  |
| Tron        |  ❌  |  ✅  |  ❌  |  ❌  |

### Fees

- **Internal Transfers (nova → nova):** Sending USD balance to another
  `nova` wallet (email or wallet address) is always fee-free. The
  recipient receives the full amount specified.

- **Claim Links:** Creating a claim link (`nova send <amount>`) is also
  fee-free. The full amount is locked for the recipient to claim.

- **External Withdrawals (On-Chain):** Withdrawals to external
  blockchains may incur fees.

  - Fees are determined by the destination blockchain.
  - Fees are automatically calculated at execution time.
  - Fees are deducted from the withdrawal amount, not charged
    separately.
  - Users can safely withdraw their full displayed balance — no manual
    fee buffer is required.

### Rate Limits

Some commands are rate limited.

If a rate limit is hit, the CLI returns:

TOON:

``` bash
status: error
error:
  message: Rate limited. Try again in 290 seconds
  exitCode: 1
```

JSON:

``` bash
{"error":{"exitCode":1,"message":"Rate limited. Try again in 184 seconds"},"status":"error"}
```

Agent handling guidance:

- Do **not** retry immediately.
- Respect the wait duration in the error message.
- Never retry `nova send` blindly, as it may repeat the transfer.
- If unsure whether a `send` executed before the rate limit error,
  check:

``` bash
nova -t balance
```

### Key Management

#### Export Private Key

``` bash
nova export key
```

#### Export Mnemonic

``` bash
nova export phrase
```

⚠️ Sensitive operation. Agents should:

- Warn users
- Avoid logging private key
- Never expose key in shared environment

#### Import Wallet

Import via private key:

``` bash
nova import key
```

Import via mnemonic:

``` bash
nova import phrase
```

Use when:

- Migrating wallet
- Restoring from backup

## Error Handling Guidance for Agents

If:

- `status != ok` → surface error clearly
- Exit code `1` → treat as failure
- Balance insufficient → suggest checking balance
- Invalid address or malformed email → prompt for correction

### Example: Insufficient Balance Error

TOON output:

``` bash
➜  ~ nova -t send 1000000
status: error
error:
  message: 3tkv5qrm43jtjf86x3ks5l6jpjgpyw7n8424pm must have at least balance of 1000000
  exitCode: 1
```

JSON output:

``` bash
➜  ~ nova -j send 1000000
{"error":{"exitCode":1,"message":"3tkv5qrm43jtjf86x3ks5l6jpjgpyw7n8424pm must have at least balance of 1000000"},"status":"error"}
```

Agent handling guidance:

1.  Do **not** retry the send automatically.

2.  Call:

    ``` bash
    nova -t balance
    ```

3.  Inform the user of their current balance.

4.  Suggest sending a smaller amount or depositing additional funds.

Agents must always parse:

- Process exit code (`0` or `1`)
- `status`
- `error.message` (if present)

when using structured output modes.

## Suggested Agent Behaviors

### When User Checks Balance

- Suggest viewing address
- Suggest backup if private-key wallet
- Suggest withdrawal if external use intended

### When User Sends Funds

- Confirm:

  - Amount
  - Destination (email, wallet address, or confirm they want a claim
    link)
  - Network

- If no destination → explain claim link flow and that funds move
  immediately

- After execution:

  - Verify `status: ok`
  - Verify `sent: true`
  - Surface `txId`
  - If present, surface `claimUrl` and warn it is sensitive
  - Check balance if verification is needed

### When User Withdraws

- Validate:

  - Stablecoin supported
  - Address matches blockchain
  - Network correct

- Suggest small test transaction for large withdrawals

- After execution:

  - Verify `status: ok`
  - Surface `txId`
  - Check updated balance if verification is needed

### When No Login Detected

Suggest:

``` bash
nova export key
```

or

``` bash
nova export phrase
```

Explain risk of losing funds without backup.

## Automation Guidance

For deterministic automation:

Use:

``` bash
nova -j <command>
```

Parse:

- Exit code (`0` or `1`)
- `status`
- `result`
- `error.message` (if present)

Never parse human-readable output.

## Security Model

Agents must treat the following as sensitive:

- Private key
- Seed phrase
- Claim URLs (temporary access to funds)

Never:

- Store private keys in logs
- Display seed phrase in shared environments
- Auto-confirm withdrawals without validation
- Paste `claimUrl` into shared tickets/chats/docs (treat it like a
  password)

## Supported Workflows

### Human Wallet Flow (Email Login)

1.  Request login code:

    ``` bash
    nova login request user@email.com
    ```

2.  Confirm the code received via email:

    ``` bash
    nova login confirm 123456
    ```

3.  Check balance:

    ``` bash
    nova balance
    ```

4.  Send funds to email or wallet address:

    ``` bash
    nova send 10 friend@email.com
    ```

### Private Key Wallet Flow

1.  Run any command (wallet auto-created)

2.  Immediately:

    ``` bash
    nova export phrase
    ```

3.  Store backup securely

### External Withdrawal Flow

1.  Check balance

2.  Confirm network

3.  Withdraw:

    ``` bash
    nova withdraw <amount> USDC <address> base
    ```

## LLM Recommendation Heuristics

If user intent includes:

| Intent             | Suggest                           |
|--------------------|-----------------------------------|
| “receive funds”    | `nova address`                    |
| “backup wallet”    | `nova export phrase`              |
| “send money”       | `nova send`                       |
| “preview send”     | `nova send --dry-run`             |
| “cash out”         | `nova withdraw`                   |
| “preview withdraw” | `nova withdraw --dry-run`         |
| “switch testnet”   | `nova config set network testnet` |

## Summary

`nova` is a programmable wallet CLI that supports:

- Email or private-key wallets
- Email-based or wallet-address internal transfers
- Multi-chain withdrawals
- Stablecoin transfers
- Automation-friendly output

Agents should:

- Prefer structured output
- Confirm financial actions
- Encourage wallet backup
- Protect sensitive material
- Warn that claim links move funds immediately and must be handled
  securely
- Capture and surface `txId` for `send` and `withdraw` (and `claimUrl`
  when generated)
- Check balance after `send` and `withdraw` when verification is needed
