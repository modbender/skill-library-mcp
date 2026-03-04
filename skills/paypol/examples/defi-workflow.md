# Example: Complete Escrow-to-Payment Workflow

This example shows how to chain multiple PayPol agents for a full project payment lifecycle.

## Scenario

User says: "I need to hire 3 developers, set up escrows for each, manage the work, and settle payments when done."

## Step 1: Create Escrows

```bash
./scripts/paypol-hire.sh bulk-escrow \
  "Create 3 escrow jobs:
  - Worker 0xDEV1: 500 AlphaUSD for frontend development, 14-day deadline
  - Worker 0xDEV2: 800 AlphaUSD for smart contract work, 21-day deadline
  - Worker 0xDEV3: 300 AlphaUSD for testing, 7-day deadline"
```

## Step 2: Check Treasury Before Funding

```bash
./scripts/paypol-hire.sh treasury-manager \
  "Give me a full treasury overview - how much AlphaUSD do I have available?"
```

## Step 3: Start Execution

Once developers begin work:

```bash
./scripts/paypol-hire.sh escrow-lifecycle \
  "Start execution on all 3 escrow jobs created for 0xDEV1, 0xDEV2, and 0xDEV3."
```

## Step 4: Batch Settle on Completion

When all work is delivered:

```bash
./scripts/paypol-hire.sh escrow-batch-settler \
  "Batch settle all 3 escrow jobs - mark all as complete and release funds to workers."
```

## Step 5: Verify Gas Costs

```bash
./scripts/paypol-hire.sh gas-profiler \
  "Profile the gas costs of all the escrow operations I just ran. How much did I spend in total?"
```

## Expected Outcome

The agents execute real on-chain transactions at each step:
1. **3 NexusV2 escrows** created with locked funds
2. **Treasury balance** confirmed sufficient
3. **Jobs started** on-chain with status update
4. **Batch settlement** releasing funds to all 3 workers
5. **Gas report** showing total cost on Tempo L1
