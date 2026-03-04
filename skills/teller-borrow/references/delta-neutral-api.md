# Teller Delta-Neutral + Lending API Cheat Sheet

Source: https://registry.scalar.com/@teller/apis/delta-neutral/latest

## Base URLs
- Production: `https://delta-neutral-api.teller.org`
- Local dev: `http://localhost:3000`

## Endpoints

### 1. `GET /perps/delta-neutral`
- Returns best delta-neutral arbitrage opportunities by `(chainId, coin)`.
- Key fields: `borrowAprPct`, `fundingAprYearlyPct`, `netAprPct`, `principalAvailableUsd`, `allPlatforms[]`.
- Cached for ~2 minutes.
- Use to decide which pool + perp venue combination yields positive net APR (borrow cost vs. negative perp funding).

### 2. `GET /borrow/general`
- Lists every Teller borrow pool.
- Filters: `chainId`, `collateral_token_address`, `borrow_token_address`, `pool_address`, `ttl`.
- Response includes enrichment: collateral ratio, principal available, marketplace fees, payment cycle.
- Cached ~30 minutes.

### 3. `GET /borrow-terms`
- Calculates how much a given wallet can borrow from a specific pool/collateral pair.
- Required params: `wallet`, `chainId`, `collateralToken`, `poolAddress`.
- Output: `maxBorrowUsd`, `ltvPct`, `principalAvailableUsd`, collateral balances, rates.

### 4. `GET /borrow-tx`
- Builds the on-chain transaction list needed to borrow (token approval, forwarder approval, commitment accept).
- Required params: `walletAddress`, `collateralTokenAddress`, `chainId`, `poolAddress`, `collateralAmount`, `principalAmount`.
- Optional `loanDuration` (seconds).
- Use results directly as calldata for sequential submission.

### 5. `GET /loans/get-all`
- Pulls the borrower’s complete loan list from the Teller subgraph.
- Params: `walletAddress`, `chainId`.
- Includes status, principal, APR, schedule, collateral info.

### 6. `GET /loans/repay-tx`
- Generates approval + repay transactions for full or partial repayment.
- Params: `bidId`, `chainId`, `walletAddress`, optional `amount`.
- Response matches `borrow-tx` structure: `transactions[]`, `summary` (repayment amount, lending token, etc.).

### Helper Notes
- All addresses should be 0x-prefixed, checksummed/lowercase; API normalizes but best to send canonical form.
- Amount fields for tx builder endpoints expect base units (wei, smallest token unit). Format as decimal strings.
- Errors typically return `{ "ok": false, "error": "message" }` with HTTP 4xx/5xx codes.
