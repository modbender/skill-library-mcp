# Example: Token Deployment with Security

## Scenario

User says: "Deploy a new token and set up proper allowances before distributing to my team."

## Step 1: Deploy the Token

```bash
./scripts/paypol-hire.sh token-deployer \
  "Deploy a new ERC-20 token called ProjectCoin (PROJ) with 1,000,000 initial supply on Tempo L1."
```

## Expected Result

The agent returns deployment details:
- **Contract address**: Deployed token address on Tempo L1
- **Tx hash**: On-chain transaction hash
- **Token details**: Name, symbol, decimals, total supply
- **Verification**: Sourcify verification status

## Step 2: Set Up Allowances

After deployment, approve the MultisendVault to distribute tokens:

```bash
./scripts/paypol-hire.sh allowance-manager \
  "Approve MultisendVaultV2 to spend 500,000 PROJ tokens for batch distribution."
```

## Step 3: Batch Distribute to Team

```bash
./scripts/paypol-hire.sh multisend-batch \
  "Send PROJ tokens to team: 0xAAA 50000, 0xBBB 50000, 0xCCC 30000, 0xDDD 20000."
```

## Step 4: Verify Everything

```bash
./scripts/paypol-hire.sh balance-scanner \
  "Scan all token balances for my wallet and verify the PROJ distribution went through."
```
