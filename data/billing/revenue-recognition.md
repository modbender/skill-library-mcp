# Revenue Recognition (ASC 606 / IFRS 15)

## Five-Step Model

```
1. Identify contract(s) with customer
2. Identify performance obligations
3. Determine transaction price
4. Allocate price to obligations
5. Recognize revenue as obligations satisfied
```

## SaaS Revenue Recognition

### Monthly Subscription
```
Cash: $99/month
Revenue: $99/month
Simple — recognized as delivered
```

### Annual Subscription
```
Cash: $1,000 (January 1)
Revenue: $83.33/month over 12 months

Journal Entry (Jan 1):
  DR Cash              $1,000
  CR Deferred Revenue  $1,000

Journal Entry (Jan 31):
  DR Deferred Revenue  $83.33
  CR Revenue           $83.33
```

## Deferred Revenue Tracking

```typescript
interface RevenueSchedule {
  subscriptionId: string;
  totalAmount: number;
  recognizedAmount: number;
  deferredAmount: number;
  startDate: Date;
  endDate: Date;
  monthlyRecognition: number;
}

async function recognizeRevenue(schedule: RevenueSchedule) {
  const today = new Date();
  const monthsElapsed = monthsBetween(schedule.startDate, today);
  const toRecognize = Math.min(
    schedule.monthlyRecognition * monthsElapsed,
    schedule.totalAmount
  ) - schedule.recognizedAmount;
  
  if (toRecognize > 0) {
    await createJournalEntry({
      debit: { account: 'deferred_revenue', amount: toRecognize },
      credit: { account: 'revenue', amount: toRecognize }
    });
    
    schedule.recognizedAmount += toRecognize;
    schedule.deferredAmount -= toRecognize;
  }
}
```

## Multi-Element Contracts

Example: $10,000 contract includes:
- Software license
- Implementation services
- 12 months support

**Step 1:** Identify standalone selling prices (SSP)
| Element | SSP | Allocated |
|---------|-----|-----------|
| License | $6,000 | $5,455 |
| Implementation | $2,000 | $1,818 |
| Support | $4,000 | $2,727 |
| **Total** | $12,000 | $10,000 |

**Step 2:** Allocate proportionally

```typescript
function allocateRevenue(elements: Element[], totalPrice: number) {
  const totalSSP = sum(elements.map(e => e.ssp));
  
  return elements.map(e => ({
    ...e,
    allocated: (e.ssp / totalSSP) * totalPrice
  }));
}
```

## Common Mistakes

| Mistake | Correct Treatment |
|---------|-------------------|
| Recognize 100% of annual upfront | Recognize monthly over term |
| Revenue = cash collected | Revenue = when delivered |
| Ignore contract modifications | Reallocate remaining obligations |
| Bundle without allocation | Allocate to each obligation |

## Month-End Close Checklist

```markdown
## Revenue Recognition Close

### Data Gathering
- [ ] Export new subscriptions from Stripe
- [ ] Export cancellations and changes
- [ ] Reconcile subscription count to prior month

### Calculations
- [ ] Calculate new deferred revenue
- [ ] Calculate recognized revenue for period
- [ ] Calculate deferred revenue roll-forward

### Journal Entries
- [ ] Book revenue recognition entry
- [ ] Book new deferred revenue
- [ ] Book refund/credit adjustments

### Reconciliation
- [ ] Deferred revenue balance = Sum of unrecognized
- [ ] Revenue recognized = Delivered in period
- [ ] Tie out to MRR/ARR metrics
```

## Commission Capitalization (ASC 340-40)

Sales commissions on multi-year contracts must be capitalized and amortized.

```typescript
interface CommissionSchedule {
  employeeId: string;
  contractId: string;
  commissionAmount: number;
  contractTerm: number; // months
  monthlyAmortization: number;
}

// $5,000 commission on 24-month contract
// Amortize $208.33/month
```

## Reporting Metrics

| Metric | Definition | Revenue Timing |
|--------|------------|---------------|
| Bookings | Contract signed value | Point in time |
| Billings | Invoiced amount | When invoiced |
| Revenue | Recognized per GAAP | When delivered |
| ARR | Annualized recognized | Normalized |
| Deferred Revenue | Billed, not recognized | Liability |
| Unbilled AR | Recognized, not billed | Asset |

**Key insight:** Bookings ≠ Billings ≠ Revenue. Confusing them causes audit issues.
