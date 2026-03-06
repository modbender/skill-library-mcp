# Heath Ledger Reconciliation System

## Overview

This document explains how Heath Ledger reconciles Mercury bank data with professional bookkeeper output.

## Key Concepts

### Data Source Limitations

**Mercury** only shows:
- NET Stripe payouts (after Stripe deducts fees)
- Posted transaction dates (1-2 days after actual transaction)
- Aggregated payouts (multiple customer transactions per payout)

**Professional Bookkeepers** typically have:
- Direct Stripe API access → actual GROSS sales and itemized fees
- Customer invoices → revenue recognized by billing date (accrual)
- Full chart of accounts with adjusting entries

### Reconciliation Strategies

#### 1. Stripe Gross-Up (Automatic)

When `stripe_fee_rate` is configured, the system:
1. Identifies Stripe payouts (credits from "STRIPE")
2. Calculates: `gross = net / (1 - fee_rate)`
3. Adds `Stripe Fees` as COGS = `gross - net`
4. Grosses up `Sales/Service Revenue` by the same amount

**Limitation**: This is an approximation. Actual Stripe fees are per-transaction (2.9% + $0.30 each), which we can't calculate without knowing transaction counts.

**Better approach**: Import actual Stripe data via API integration.

#### 2. Month Offset (Accrual Basis)

When `month_offset` is set:
- Mercury posts transactions 1-2 days after actual date
- A December 31 charge posts as January 2 in Mercury
- Setting `month_offset = 1` shifts transactions back by 1 month

This aligns with bookkeepers who use accrual basis (revenue/expenses recognized when earned/incurred, not when cash moves).

#### 3. Synthetic Entries (Amortization)

When `amortization_monthly` is set:
- Adds a synthetic Amortization expense each month
- Used for goodwill amortization, prepaid expenses, etc.
- These don't appear in bank transactions

### Entity Settings

```sql
entity_settings:
  stripe_fee_rate      -- Default: 0.029 (2.9%)
  stripe_fee_fixed     -- Default: 0.30 (per-transaction, for future use)
  month_offset         -- Default: 0 (months to shift for accrual)
  accounting_basis     -- 'cash' or 'accrual'
  amortization_monthly -- Monthly amortization amount
```

Configure via:
```bash
node scripts/entity-settings.mjs set-accrual <entity_id> \
  --month-offset=1 \
  --amortization=5833.50 \
  --stripe-rate=2.3
```

### Categorization Rules

#### Global Rules (entity_id = NULL)
Apply across all entities. Seeded with common vendors:
- Twilio, GitHub, Slack → Software expenses
- Google Ads → Advertising
- AWS, Heroku → Servers & Hosting
- Stripe (credits) → Sales/Service Revenue

#### Entity Rules
Override global rules for specific business needs.

#### Confidence Scoring
- Confirmed rules increase confidence (+0.01)
- Overridden rules decrease confidence (-0.05)
- Rules with high override rates flagged for review

#### Rule Promotion
When 3+ entities categorize a vendor the same way, the rule is promoted to global.

### Known Reconciliation Gaps

1. **Sales Revenue**: Mercury NET vs Bookkeeper GROSS
   - Fix: Integrate Stripe API for actual gross data
   - Workaround: Configure `stripe_fee_rate` for estimation

2. **Stripe Fees**: Estimated vs Actual
   - Fix: Integrate Stripe API
   - Current: Uses `gross - net` approximation

3. **Deferred Revenue**: Bookkeepers may recognize revenue differently
   - Some income recognized over time (SaaS subscriptions)
   - Mercury shows cash receipt, not revenue recognition

4. **Adjusting Entries**: Journal entries not in bank
   - Accruals, deferrals, corrections
   - Must be added as synthetic entries

## Usage

### Generate P&L with Adjustments
```javascript
import { buildPnl } from './lib/pnl.js';

const pnl = buildPnl(db, entityId, startDate, endDate, {
  includeStripeGrossUp: true,  // Apply Stripe fee gross-up
  includeAmortization: true,   // Include synthetic amortization
  useMonthOffset: true,        // Use entity's month offset setting
});
```

### Compare with Bookkeeper
```bash
node scripts/compare-with-bookkeeper.mjs <entity_id> <bookkeeper_excel_dir>
```

### Seed Global Rules
```javascript
import { seedGlobalRules } from './lib/categorization.js';
seedGlobalRules(db);
```

## Future Improvements

1. **Stripe API Integration**: Import actual gross sales, fees, and transaction details
2. **Invoice Import**: Match revenue to invoices for proper accrual
3. **Deferred Revenue Tracking**: Manage subscription revenue recognition
4. **Multi-Source Reconciliation**: Cross-check Stripe, Mercury, and accounting software
