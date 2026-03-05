# Bookkeeper Comparison: Heath Ledger vs Professional Bookkeeper

*Documented 2026-02-22 after comparing OnSched (entity 1) books against professional bookkeeper output.*

## What We Learned

### Things We Got Right
- **Transaction categorization accuracy**: After iterative corrections, ~95% match rate with professional bookkeeper
- **P&L structure**: Chart of accounts aligned well with standard startup accounting
- **Stripe revenue recognition**: Gross-up calculation (using 2.3% + $0.30) produced numbers close to actuals

### Things the Bookkeeper Did Differently

#### 1. Stripe Net vs Gross
- **Bookkeeper**: Used Stripe API data for exact gross revenue and exact fees
- **Us (without Stripe API)**: Estimated gross from net using fee rate formula
- **Delta**: ~1-3% variance on revenue line depending on month
- **Fix**: Added optional Stripe API integration; without it, the estimate is documented as approximate

#### 2. Gusto = Payroll, Not Tax
- **Bookkeeper**: Categorized Gusto as "Wages & Salaries" (net payroll)
- **Us initially**: Had it under "Business Licensing, Fees & Tax" → "Net Payroll"
- **Fix**: Updated seed rules to map Gusto → "Wages & Salaries" → "Payroll"

#### 3. Deel Fee Splitting
- **Bookkeeper**: Split Deel transactions into platform fees vs actual payroll
- **Pattern discovered**: Small fixed amounts ($2-5) = platform fee, larger variable = payroll
- **Fix**: Documented pattern; system learns from corrections

#### 4. Wise = Bank Fees, Not Transfers
- **Bookkeeper**: Wise fees → "Bank Service Charges" (the fee component)
- **Us**: Were categorizing some Wise as "Transfers Between Accounts"
- **Nuance**: Wise can be both — the fee is an expense, the transfer is a balance sheet movement
- **Fix**: Small Wise amounts → Bank Service Charges; large round amounts → likely transfers

#### 5. Amortization
- **Bookkeeper**: Included monthly amortization entries for acquired software assets
- **Us**: Added `amortization_monthly` entity setting + `synthetic_entries` table
- **Fix**: System now generates synthetic amortization entries during book generation

#### 6. Month Offset / Fiscal Year
- **Bookkeeper**: Used calendar year (Jan-Dec)
- **Us**: Made configurable via `month_offset` setting (default: 1 = calendar year)

### Accuracy Summary (OnSched, Full Year 2025)
- **Revenue**: Within 2% (Stripe gross-up estimation vs actual)
- **Total Expenses**: Within 1% after categorization corrections
- **Net Income**: Within 3% — mainly driven by Stripe fee estimation delta
- **Category-level accuracy**: 95%+ match after 3 rounds of corrections

## Key Takeaways

1. **Stripe API is important** — the single biggest accuracy gap comes from net vs gross Stripe deposits
2. **Payroll providers need careful mapping** — Gusto, Deel, Rippling all have nuances (fees vs actual payroll)
3. **The learning system works** — each correction makes future runs more accurate
4. **80/20 rule applies** — 20 vendor rules cover 80% of transactions for a typical SaaS company
5. **Synthetic entries matter** — amortization, Stripe fee splits, and accruals need to be generated, not just categorized
