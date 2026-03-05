# Query Library

Pre-built AQL queries for common reporting needs. Each query is shown as an inline one-liner and a reusable module file.

## 1. Spending by category (current month)

Total spent per category for a given month.

```bash
fscl query --inline "q('transactions').filter({date:{$gte:'2026-02-01',$lte:'2026-02-28'},amount:{$lt:0}}).select(['category.name',{total:{$sum:'$amount'}}]).groupBy('category.name').orderBy({total:'asc'})"
```

```javascript
// spending-by-category.mjs
export default (q) =>
  q('transactions')
    .filter({
      date: { $gte: '2026-02-01', $lte: '2026-02-28' },
      amount: { $lt: 0 },
    })
    .select(['category.name', { total: { $sum: '$amount' } }])
    .groupBy('category.name')
    .orderBy({ total: 'asc' });
```

## 2. Income vs expenses

Total income and total spending for a period.

```bash
fscl query --inline "q('transactions').filter({date:{$gte:'2026-01-01',$lte:'2026-12-31'}}).select([{income:{$sum:{$case:[{$gt:['$amount',0]},'$amount',0]}}},{expenses:{$sum:{$case:[{$lt:['$amount',0]},'$amount',0]}}}])"
```

```javascript
// income-vs-expenses.mjs
export default (q) =>
  q('transactions')
    .filter({
      date: { $gte: '2026-01-01', $lte: '2026-12-31' },
    })
    .select([
      { income: { $sum: { $case: [{ $gt: ['$amount', 0] }, '$amount', 0] } } },
      { expenses: { $sum: { $case: [{ $lt: ['$amount', 0] }, '$amount', 0] } } },
    ]);
```

## 3. Top payees by spending

Top N payees ranked by total outflow.

```bash
fscl query --inline "q('transactions').filter({date:{$gte:'2026-01-01',$lte:'2026-12-31'},amount:{$lt:0}}).select(['payee.name',{total:{$sum:'$amount'}}]).groupBy('payee.name').orderBy({total:'asc'}).limit(20)"
```

```javascript
// top-payees.mjs
export default (q) =>
  q('transactions')
    .filter({
      date: { $gte: '2026-01-01', $lte: '2026-12-31' },
      amount: { $lt: 0 },
    })
    .select(['payee.name', { total: { $sum: '$amount' } }])
    .groupBy('payee.name')
    .orderBy({ total: 'asc' })
    .limit(20);
```

## 4. Monthly spending trend

Total spending per month for the past 12 months.

```bash
fscl query --inline "q('transactions').filter({date:{$gte:'2025-03-01',$lte:'2026-02-28'},amount:{$lt:0}}).select([{month:{$month:'$date'}},{total:{$sum:'$amount'}}]).groupBy({month:{$month:'$date'}}).orderBy({month:'asc'})"
```

```javascript
// monthly-trend.mjs
export default (q) =>
  q('transactions')
    .filter({
      date: { $gte: '2025-03-01', $lte: '2026-02-28' },
      amount: { $lt: 0 },
    })
    .select([
      { month: { $month: '$date' } },
      { total: { $sum: '$amount' } },
    ])
    .groupBy({ month: { $month: '$date' } })
    .orderBy({ month: 'asc' });
```

## 5. Large transactions

Transactions above a threshold amount (e.g. $100 expenses).

```bash
fscl query --inline "q('transactions').filter({date:{$gte:'2026-02-01'},amount:{$lt:-10000}}).select(['date','payee.name','category.name','amount','notes']).orderBy({amount:'asc'})"
```

```javascript
// large-transactions.mjs
export default (q) =>
  q('transactions')
    .filter({
      date: { $gte: '2026-02-01' },
      amount: { $lt: -10000 }, // -$100.00 in minor units
    })
    .select(['date', 'payee.name', 'category.name', 'amount', 'notes'])
    .orderBy({ amount: 'asc' });
```

## 6. Net worth snapshot

Sum of all account balances (current).

```bash
fscl query --inline "q('transactions').select([{net_worth:{$sum:'$amount'}}])"
```

```javascript
// net-worth.mjs
export default (q) =>
  q('transactions')
    .select([{ net_worth: { $sum: '$amount' } }]);
```

## Usage notes

- All amounts in AQL are integer minor units: `-4599` = -$45.99
- Date filters use ISO format: `YYYY-MM-DD`
- `$month` extracts the month from a date for grouping
- Run with `fscl query --module ./file.mjs` or `fscl query --inline "..."`
- Adjust date ranges and thresholds to match your needs

## Workflow: advanced queries

```bash
# Inline query: total spending by category this month
fscl query --inline "q('transactions').filter({date:{$gte:'2026-02-01'}}).select(['category.name','amount']).groupBy('category.name')"

# Module query: save reusable queries as files
fscl query --module ./top-payees.mjs
```
