---
name: cavos-cli
description: Interact with the Cavos CLI for Starknet wallet operations. Use for transfers, approvals, contract calls, session management, and transaction monitoring.
metadata: { "openclaw": { "requires": { "bins": ["npx"] } } }
---

# Cavos CLI Skill

This skill allows you to interact with the Cavos CLI (`@cavos/cli`) to manage Starknet wallets, perform transfers, and execute contract calls.

## Core Commands

Always use the `--json` flag when possible to get structured output.

### 1. Identity & Session
- **Who Am I**: Check current session and wallet address.
  ```bash
  npx @cavos/cli whoami --json
  ```
- **Session Status**: Check if the session is active/expired.
  ```bash
  npx @cavos/cli session-status --json
  ```
- **Import Session**: Import a session token provisioned from the [Dashboard](https://agent.cavos.xyz/).
  ```bash
  npx @cavos/cli session import <token>
  ```

### 2. Assets & Transfers
- **Check Balance**:
  ```bash
  npx @cavos/cli balance --token <STRK|ETH|address> --json
  ```
- **Transfer Tokens**:
  ```bash
  npx @cavos/cli transfer --to <address> --amount <amount> --token <token> --json
  ```

### 3. Contract Interactions
- **Approve Spending**:
  ```bash
  npx @cavos/cli approve --spender <address> --amount <amount> --token <token> --json
  ```
- **Execute Call**:
  ```bash
  npx @cavos/cli execute --contract <address> --entrypoint <method> --calldata <comma_separated_vals> --json
  ```
- **Read Call**:
  ```bash
  npx @cavos/cli call --contract <address> --entrypoint <method> --calldata <vals> --json
  ```

### 4. Advanced Operations
- **Multicall**: Batch multiple calls.
  ```bash
  npx @cavos/cli multicall --calls '<json_array>' --json
  ```
- **Simulate/Estimate**: Check tx before sending.
  ```bash
  npx @cavos/cli simulate --contract <addr> --entrypoint <method> --calldata <vals> --json
  ```
- **Transaction Status**:
  ```bash
  npx @cavos/cli tx status <hash> --json
  ```

## Best Practices
1. **Verify Balance**: Always run `balance` before a `transfer`.
2. **Check Session**: Run `whoami` or `session-status` at the start of a workflow to ensure authentication.
3. **Use JSON**: Parsing JSON output is safer than regexing stdout.
4. **Calldata**: Calldata for `execute` and `call` should be comma-separated strings (e.g., `0x1,100`).
