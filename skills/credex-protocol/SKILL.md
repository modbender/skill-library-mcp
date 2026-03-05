---
name: credex-protocol
description: Access unsecured credit lines for AI agents on the Arc Network using the Credex Protocol. Use for borrowing USDC against reputation, repaying debt to grow credit limits, providing liquidity as an LP, or managing cross-chain USDC via Circle Bridge. Triggers on "borrow from credex", "repay debt", "deposit to pool", "check credit status", "provide liquidity", or any credit/lending task on Arc.
---

# Credex Protocol Skill

Interact with the Credex Protocol—a decentralized credit system for AI agents on the Arc Network.

---

## Usage

**Base Directory:** `{baseDir}` (the directory containing this SKILL.md)

**Run all commands from the project root:**

```bash
cd {baseDir}
npx ts-node scripts/client.ts <command> [args]   # Borrower commands
npx ts-node scripts/lp.ts <command> [args]       # LP commands
```

**Output Format:** All scripts return **JSON** for machine readability. Parse the output to extract fields like `creditLimit`, `txHash`, `debt`, etc.

---

## Environment Variables

### Required (Must Be Set)

| Variable             | Description                                                                |
| -------------------- | -------------------------------------------------------------------------- |
| `WALLET_PRIVATE_KEY` | Private key for signing transactions. **Without this, all commands fail.** |
| `RPC_URL`            | Arc Network RPC. Default: `https://rpc.testnet.arc.network`                |

### Optional

| Variable              | Description             | Default                                      |
| --------------------- | ----------------------- | -------------------------------------------- |
| `CREDEX_POOL_ADDRESS` | Pool contract address   | `0x32239e52534c0b7e525fb37ed7b8d1912f263ad3` |
| `CREDEX_AGENT_URL`    | Credex agent server URL | `http://localhost:10003`                     |

**Pre-Flight Check:** Before running any command, verify `WALLET_PRIVATE_KEY` is set. If missing, prompt the user.

---

## Contract Addresses (Arc Testnet)

| Contract              | Address                                      |
| --------------------- | -------------------------------------------- |
| `CredexPool`          | `0x32239e52534c0b7e525fb37ed7b8d1912f263ad3` |
| `USDC` (Arc)          | `0x3600000000000000000000000000000000000000` |
| `USDC` (Base Sepolia) | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` |

---

## Client Commands (Borrower)

**Script:** `scripts/client.ts`  
**Run as:** `npx ts-node scripts/client.ts <command> [args]`

---

### `status`

Check credit status for an agent.

**Usage:**

```bash
npx ts-node scripts/client.ts status <address>
```

**Args:**

- `address` (optional): Wallet address. Defaults to `WALLET_PRIVATE_KEY` address.

**Returns:** JSON

```json
{
  "creditLimit": "100.000000",
  "principal": "5.000000",
  "interest": "0.050000",
  "debt": "5.050000",
  "availableCredit": "95.000000",
  "active": true,
  "frozen": false
}
```

**Action:** Use `availableCredit` to check if sufficient funds before calling `borrow`.

---

### `borrow`

Borrow USDC from the pool.

**Usage:**

```bash
npx ts-node scripts/client.ts borrow <amount>
```

**Args:**

- `amount` (required): USDC amount as decimal string (e.g., `"5.0"`).

**Returns:** JSON

```json
{
  "success": true,
  "txHash": "0x...",
  "borrowed": "5.000000",
  "newDebt": "5.000000",
  "availableCredit": "95.000000"
}
```

**Fails if:** `amount > availableCredit`. Check `status` first.

---

### `repay`

Repay debt to the pool.

**Usage:**

```bash
npx ts-node scripts/client.ts repay <amount|all>
```

**Args:**

- `amount`: Specific USDC amount to repay (e.g., `"5.0"`).
- `all`: Calculates total debt + 1% buffer and repays fully. The contract caps at actual debt owed.

**Returns:** JSON

```json
{
  "success": true,
  "txHash": "0x...",
  "repaid": "5.050000",
  "remainingDebt": "0.000000",
  "newCreditLimit": "110.000000"
}
```

**Note:** Repayments pay **interest first**, then **principal**. Each successful repayment increases credit limit by 10%.

---

### `bridge`

Bridge USDC between Arc Testnet and Base Sepolia.

**Usage:**

```bash
npx ts-node scripts/client.ts bridge <amount> <from> <to>
```

**Args:**

- `amount`: USDC amount (e.g., `"10.0"`).
- `from`: Source chain (`arc` or `base`).
- `to`: Destination chain (`arc` or `base`).

**Returns:** JSON

```json
{
  "success": true,
  "amount": "10.000000",
  "from": "Arc_Testnet",
  "to": "Base_Sepolia",
  "estimatedArrival": "5-10 minutes"
}
```

**Fails if:** `from === to`. Chains must be different.

---

### `balance`

Check wallet balance on both chains.

**Usage:**

```bash
npx ts-node scripts/client.ts balance
```

**Returns:** JSON

```json
{
  "arc": "50.000000",
  "base": "25.000000",
  "total": "75.000000"
}
```

---

## LP Commands (Liquidity Provider)

**Script:** `scripts/lp.ts`  
**Run as:** `npx ts-node scripts/lp.ts <command> [args]`

---

### `pool-status`

Check overall pool health and metrics.

**Usage:**

```bash
npx ts-node scripts/lp.ts pool-status
```

**Returns:** JSON

```json
{
  "totalAssets": "1000.000000",
  "totalLiquidity": "800.000000",
  "totalDebt": "200.000000",
  "totalShares": "950.000000",
  "sharePrice": "1.052631",
  "utilizationPercent": 20
}
```

---

### `deposit`

Deposit USDC to receive LP shares.

**Usage:**

```bash
npx ts-node scripts/lp.ts deposit <amount>
```

**Args:**

- `amount`: USDC to deposit (e.g., `"100.0"`).

**Returns:** JSON

```json
{
  "success": true,
  "txHash": "0x...",
  "deposited": "100.000000",
  "sharesReceived": "95.000000",
  "totalShares": "95.000000"
}
```

---

### `withdraw`

Burn LP shares to withdraw USDC.

**Usage:**

```bash
npx ts-node scripts/lp.ts withdraw <shares|all>
```

**Args:**

- `shares`: Number of shares to burn (e.g., `"50.0"`).
- `all`: Withdraw maximum possible based on available liquidity.

**Returns:** JSON

```json
{
  "success": true,
  "txHash": "0x...",
  "sharesBurned": "50.000000",
  "usdcReceived": "52.631579",
  "remainingShares": "45.000000"
}
```

**Note:** Withdrawal may be capped if liquidity is fully utilized (all USDC lent out).

---

### `lp-balance`

Check LP position for an address.

**Usage:**

```bash
npx ts-node scripts/lp.ts lp-balance [address]
```

**Returns:** JSON

```json
{
  "shares": "95.000000",
  "value": "100.000000"
}
```

---

## Protocol Mechanics

### Interest Accrual

- **Rate:** 0.1% per interval (10 basis points)
- **Interval:** 1 minute (testnet accelerated)
- **Formula:** `debt = principal + accrued_interest`

### Credit Limit Growth

After each repayment:

```
newLimit = currentLimit × 1.10
```

Maximum: 10,000 USDC.

### Available Credit

```
availableCredit = creditLimit - principal
```

Interest does NOT reduce borrowing power—only principal.

### Share Price (LP)

```
sharePrice = totalAssets / totalShares
```

Where `totalAssets = liquidity + outstandingDebt`.

---

## Workflow Examples

### Borrower Flow

```text
1. Check status     → npx ts-node scripts/client.ts status
2. Borrow           → npx ts-node scripts/client.ts borrow 5
3. Use funds        → (perform task on Arc or bridge to Base)
4. Bridge back      → npx ts-node scripts/client.ts bridge 5 base arc
5. Repay            → npx ts-node scripts/client.ts repay all
6. Verify growth    → npx ts-node scripts/client.ts status (limit increased!)
```

### LP Flow

```text
1. Check pool       → npx ts-node scripts/lp.ts pool-status
2. Deposit          → npx ts-node scripts/lp.ts deposit 100
3. Monitor          → npx ts-node scripts/lp.ts lp-balance
4. Withdraw         → npx ts-node scripts/lp.ts withdraw all
```

---

## Common Errors & Recovery

| Error                         | Cause                      | Recovery                                         |
| ----------------------------- | -------------------------- | ------------------------------------------------ |
| `WALLET_PRIVATE_KEY required` | Env var missing            | Set `WALLET_PRIVATE_KEY` before running          |
| `Exceeds credit limit`        | `amount > availableCredit` | Call `status`, borrow less                       |
| `Insufficient balance`        | Wallet has no USDC         | Bridge funds or acquire testnet USDC             |
| `Insufficient liquidity`      | Pool is fully utilized     | Wait for borrowers to repay or LPs to deposit    |
| `Nonce too low`               | Transaction conflict       | Wait 10 seconds and retry                        |
| `Bridge timeout`              | Circle Bridge delay        | Wait 5-10 minutes, check balances on both chains |
| `Same chain error`            | `from === to` in bridge    | Use different source and destination             |

---

## References

- See `references/contracts.md` for full ABIs and type definitions.
- See `scripts/client.ts` and `scripts/lp.ts` for implementation.
