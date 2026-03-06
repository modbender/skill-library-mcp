# Property Analysis — Real Estate Agent

## Valuation Framework

### Comparable Sales Analysis (Comps)

The foundation of property valuation. Find 3-5 similar properties that sold recently.

**Selection criteria:**
- Same neighborhood (ideally same street or block)
- Similar size (within 15% of square meters)
- Similar type (apartment vs house vs townhouse)
- Sold within last 6 months (3 months preferred)
- Similar condition/age

**Adjustment factors:**

| Factor | Adjustment per Unit |
|--------|-------------------|
| Size | +/- €X per sqm based on local rate |
| Bedrooms | +/- 3-5% per bedroom |
| Bathrooms | +/- 2-3% per bathroom |
| Parking | +5-15% for garage vs none |
| Floor (apartments) | +1-2% per floor (varies) |
| Condition | +/- 5-20% for renovation state |
| Outdoor space | +5-10% for balcony/garden |
| View | +5-15% for premium views |

**Comp analysis template:**

```markdown
## Comparable Sales Analysis

Target: [Address], [Size] sqm, [Beds] bed, [Baths] bath

### Comp 1: [Address]
- Sold: €XXX,XXX on YYYY-MM-DD
- Size: XXX sqm (+/- X sqm vs target)
- Details: X bed, X bath, [features]
- Adjustments: +€X (size), -€Y (no parking)
- Adjusted value: €XXX,XXX

### Comp 2: [Address]
[Same structure]

### Comp 3: [Address]
[Same structure]

### Valuation Range
- Low: €XXX,XXX (based on comp X)
- Mid: €XXX,XXX (average of adjusted comps)
- High: €XXX,XXX (based on comp Y)

**Recommended price:** €XXX,XXX (+/- €XX,XXX)
```

### Price Per Square Meter

Quick sanity check using area averages.

**Calculation:**
```
Price per sqm = Sale Price / Usable Square Meters
```

**Interpretation:**
- Below area average: Potential opportunity or hidden problems
- At area average: Fair market value
- Above area average: Premium features or overpriced

**Watch out for:**
- Including terrace/balcony at full sqm (usually 25-50% of interior value)
- "Built" vs "usable" square meters (can differ 10-20%)
- Common areas included in some markets

### Investment Analysis

For investors evaluating rental properties.

**Key metrics:**

| Metric | Formula | Target |
|--------|---------|--------|
| Gross Yield | Annual Rent / Purchase Price | 5-8% |
| Net Yield | (Rent - Expenses) / Total Cost | 4-6% |
| Cap Rate | NOI / Property Value | 4-8% |
| Cash-on-Cash | Annual Cash Flow / Cash Invested | 8-12% |
| GRM | Price / Annual Gross Rent | 10-15 |

**Expense estimation (typical):**
- Property tax: 0.5-2% of value annually
- Insurance: 0.3-0.5% of value
- Maintenance: 1-2% of value
- Vacancy: 5-10% of gross rent
- Management: 8-12% of gross rent (if not self-managing)
- HOA/Community fees: varies by property

**Investment analysis template:**

```markdown
## Investment Analysis

Property: [Address]
Purchase Price: €XXX,XXX
Total Acquisition Cost: €XXX,XXX (including fees, taxes, renovation)

### Income
Monthly Rent: €X,XXX
Annual Gross Rent: €XX,XXX
Vacancy Allowance (X%): -€X,XXX
Effective Gross Income: €XX,XXX

### Expenses
Property Tax: €X,XXX
Insurance: €XXX
HOA Fees: €X,XXX
Maintenance Reserve: €X,XXX
Management (if applicable): €X,XXX
Total Expenses: €XX,XXX

### Returns
Net Operating Income (NOI): €XX,XXX
Gross Yield: X.X%
Net Yield: X.X%
Cap Rate: X.X%

### Financing (if applicable)
Down Payment: €XX,XXX
Mortgage: €XXX,XXX at X.X% for XX years
Monthly Payment: €X,XXX
Annual Debt Service: €XX,XXX
Cash Flow After Debt: €X,XXX
Cash-on-Cash Return: X.X%
```

## Market Analysis

### Days on Market (DOM)

Critical indicator of pricing and market conditions.

| DOM | Interpretation |
|-----|----------------|
| 0-14 days | Hot market or underpriced |
| 15-45 days | Normal market |
| 45-90 days | Slow market or overpriced |
| 90+ days | Significant issue (price, condition, or market) |

**What to tell clients:**
- "This property has been on market X days vs Y average for the area"
- "Properties like this typically sell in X days"
- "Long DOM could mean negotiating room"

### Seasonal Patterns

Real estate is seasonal in most markets:

| Season | Market Activity | Strategy |
|--------|-----------------|----------|
| Spring | Peak buying season | List early to catch buyers, expect competition |
| Summer | Active, families moving | Good for family homes, vacation markets quiet |
| Fall | Second peak | Last chance before holidays, motivated buyers |
| Winter | Slowest | Serious buyers only, less competition, negotiate harder |

### Price Trend Indicators

**Rising market signs:**
- DOM decreasing
- Multiple offers common
- Properties selling above asking
- Low inventory

**Falling market signs:**
- DOM increasing
- Price reductions common
- Properties sitting
- Rising inventory

## Report Templates

### Buyer Report

```markdown
# Property Report: [Address]

## Summary
**Recommendation:** [Consider | Pass | Strong Consider]
**Value Assessment:** [Below Market | At Market | Above Market]
**Action Required By:** [Date if urgent]

## Property Overview
- Address: 
- Price: €XXX,XXX
- Size: XXX sqm
- Type: 
- Condition: 

## Market Position
- Price per sqm: €X,XXX (vs area avg €X,XXX)
- Days on Market: X (area avg: Y)
- Price History: [Original €X, reduced to €Y on date]

## Comparable Sales
[3-5 comps with adjusted values]

## Valuation
- Comp-based range: €XXX,XXX - €XXX,XXX
- Current asking: €XXX,XXX
- **Suggested offer range:** €XXX,XXX - €XXX,XXX

## Concerns
- [Issue 1]
- [Issue 2]

## Opportunities
- [Upside 1]
- [Upside 2]

## Next Steps
1. [Action item]
2. [Action item]
```

### Seller Report

```markdown
# Listing Strategy: [Address]

## Property Summary
- Address:
- Size: XXX sqm
- Features:
- Condition:

## Market Analysis
- Area average price/sqm: €X,XXX
- Recent comparable sales: [summary]
- Current inventory: X similar properties
- Average DOM in area: X days

## Pricing Strategy
- Conservative (quick sale): €XXX,XXX
- Market value: €XXX,XXX
- Optimistic (may take longer): €XXX,XXX
- **Recommended list price:** €XXX,XXX

## Listing Optimization
- Photos needed: [specific shots]
- Description focus: [key selling points]
- Suggested improvements: [if any]

## Timeline Expectations
- Expected DOM: X-Y days
- Offer range expectation: €XXX,XXX - €XXX,XXX
```
