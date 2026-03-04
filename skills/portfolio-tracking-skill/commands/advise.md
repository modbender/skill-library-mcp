# /advise — AI Investment Advice

Analyze the current portfolio and provide personalized investment advice using Claude's built-in capabilities. No external API key needed.

## Behavior

1. Run `npx tsx <skill-path>/scripts/data-store.ts load` to get portfolio data
2. Run `npx tsx <skill-path>/scripts/data-store.ts load-config` to get user profile
3. If no user profile configured, ask the user for:
   - Age
   - Risk tolerance: Conservative, Moderate, Aggressive, or Growth
   - Monthly investable cash flow (USD)
   - Investment goal (e.g., "Retirement in 20 years", "Wealth preservation")
   - Maximum acceptable drawdown percentage
4. Prepare the portfolio summary from current data
5. Use the following analysis framework:

## Analysis Framework

Using the portfolio data and user profile, provide:

### 1. Portfolio Analysis
- Current allocation breakdown by asset type (CRYPTO, USSTOCK, HKSTOCK, ASHARE, CASH)
- Concentration risk (any single asset > 20% of portfolio?)
- Currency exposure breakdown
- Comparison against the user's stated risk tolerance
- Total portfolio value in display currency

### 2. Target Asset Allocation
Based on the user's profile, suggest target percentages:
- For **Conservative**: Heavy bonds/cash (60%+), limited equity (30%), minimal crypto (0-5%)
- For **Moderate**: Balanced equity (50-60%), some bonds (20-30%), moderate crypto (5-10%), cash reserve (10%)
- For **Aggressive**: Heavy equity (60-70%), meaningful crypto (10-20%), minimal bonds/cash (10-20%)
- For **Growth**: Maximum equity/crypto (80%+), minimal cash buffer (5-10%)

Present as a table:
```
| Category   | Current | Target | Action   |
|------------|---------|--------|----------|
| US Stock   | 25%     | 40%    | Increase |
| Crypto     | 45%     | 15%    | Decrease |
| Cash       | 30%     | 10%    | Deploy   |
```

### 3. Rebalancing Plan
Specific, actionable steps:
- What to sell (and approximate amounts)
- What to buy (specific tickers if possible)
- Order of operations (sell first, then buy)
- Consider tax implications (suggest tax-loss harvesting if applicable)
- Monthly DCA suggestions based on cash flow

## Prompt Template

```
Role: You are an expert financial advisor using modern portfolio theory.

Client Profile:
- Age: {age}
- Risk Tolerance: {riskTolerance}
- Monthly Cash Flow: ${monthlyCashFlow}
- Goal: {investmentGoal}
- Max Acceptable Drawdown: {maxDrawdown}%

Current Portfolio (Total Value approx: {totalValue} {displayCurrency}):
{portfolioSummary}

-- portfolioSummary format per asset:
-- "- {symbol} ({type}): Quantity {quantity}, Value {value} {currency}"

Task:
1. Analyze the current portfolio structure against the client's profile.
2. Suggest a Target Asset Allocation (percentages by category).
3. Create a Rebalancing Plan with specific actionable steps.
```

## Notes

- This command uses Claude's own reasoning — no external AI API needed
- If prices are stale (lastPriceRefresh > 24 hours), suggest running `/prices` first
- Always include a disclaimer: "This is not financial advice. Please consult a licensed financial advisor."
- Convert all values to `displayCurrency` for consistent comparison
- If user profile is missing, collect it interactively and save to config for future use
