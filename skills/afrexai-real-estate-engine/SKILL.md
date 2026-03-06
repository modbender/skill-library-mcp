---
name: Real Estate Investment & Operations Engine
description: "Score each market (0-100):"
---

# Real Estate Investment & Operations Engine

> Complete real estate system — from deal sourcing through portfolio management. Covers buying, selling, investing, landlording, and development with actionable frameworks, calculators, and templates.

---

## Phase 1: Investment Strategy & Criteria

### Strategy Selection Matrix

| Strategy | Capital Needed | Time Commitment | Risk | Cash Flow | Appreciation |
|----------|---------------|-----------------|------|-----------|-------------|
| Buy & Hold (rental) | Medium | Medium | Low-Med | ✅ Strong | ✅ Long-term |
| BRRRR | Medium-High | High | Medium | ✅ Recycled | ✅ Forced |
| Fix & Flip | High | Very High | High | ❌ Lump sum | N/A |
| House Hack | Low | Low | Low | ✅ Offset | ✅ Yes |
| Wholesale | Very Low | High | Low | ❌ Fee-based | N/A |
| Short-Term Rental (STR) | Medium | High | Med-High | ✅✅ Higher | ✅ Yes |
| Commercial | Very High | Medium | Medium | ✅ Strong | ✅ Yes |
| Land Banking | Low-Med | Very Low | Med-High | ❌ None | ✅✅ Speculative |
| REIT/Syndication | Any | Very Low | Varies | ✅ Passive | ✅ Diversified |

### Investment Criteria YAML

```yaml
investment_criteria:
  strategy: "buy_and_hold"  # buy_and_hold | brrrr | flip | house_hack | str | commercial
  markets:
    primary: ""        # City/metro you know best
    secondary: []      # Expansion markets
  property_types: []   # SFR, duplex, triplex, fourplex, MFH, commercial
  price_range:
    min: 0
    max: 0
  target_metrics:
    min_cash_on_cash: 8       # % annual
    min_cap_rate: 6           # %
    max_price_per_unit: 0     # For multi-family
    min_monthly_cashflow: 200 # Per unit, after all expenses
    max_rehab_budget: 0       # For value-add
  financing:
    available_cash: 0
    max_leverage: 80          # % LTV
    preferred_loan: "conventional"  # conventional | FHA | VA | DSCR | hard_money | seller_finance
  deal_breakers:              # Auto-reject
    - "flood_zone"
    - "foundation_issues"
    - "environmental_contamination"
    - "declining_population"
  nice_to_haves:
    - "below_median_price"
    - "near_employment_centers"
    - "growing_population"
    - "landlord_friendly_state"
```

### Market Analysis Framework

Score each market (0-100):

| Dimension | Weight | Metrics |
|-----------|--------|---------|
| Population Growth | 20% | 5yr trend, net migration, age demographics |
| Job Market | 20% | Unemployment rate, employer diversity, wage growth |
| Rent-to-Price Ratio | 15% | Gross rent / purchase price (>0.7% = good) |
| Landlord Friendliness | 15% | Eviction timeline, rent control, regulations |
| Supply/Demand | 15% | Vacancy rates, permits issued, absorption |
| Affordability | 10% | Median income vs median home price |
| Infrastructure | 5% | Transportation, schools, development plans |

**Market grades:**
- 80-100: Aggressively acquire
- 60-79: Selectively acquire (cherry-pick deals)
- 40-59: Hold existing, don't acquire
- Below 40: Consider exit

---

## Phase 2: Deal Sourcing

### 8 Deal Channels (Ranked by Quality)

1. **Direct Mail** — Targeted lists (absentee owners, tax delinquent, estate/probate). Response rate: 1-3%. Cost: $0.50-$2/piece
2. **Driving for Dollars** — Physical scouting for distressed properties. Free but time-intensive. Use DealMachine or similar to track
3. **Wholesaler Network** — Pre-negotiated deals at markup. Verify ARV independently. Quality varies wildly
4. **MLS (Agent)** — Listed properties. Most competitive. Look for: days on market >30, price reductions, motivated keywords
5. **Auction** — Foreclosure, tax lien, estate. Due diligence limited. Cash required. Discount: 20-40% typical
6. **FSBO** — For Sale By Owner. Direct negotiation, no agent commission baked in
7. **Networking** — REI meetups, BiggerPockets, local REIA chapters. Long-game relationship building
8. **Online Marketplaces** — Zillow, Redfin, Realtor.com, Roofstock, Auction.com

### Deal Screening Checklist (5-Minute Filter)

```
□ Meets price range criteria
□ Rent-to-price ratio > 0.7% (or flip ARV margin > 30%)
□ No deal-breaker conditions
□ Neighborhood grade C+ or better
□ Verified comparable sales within 6 months
□ No major structural red flags from photos
□ Zoning allows intended use
□ Insurance obtainable (not in exclusion zone)
```

If ALL checked → proceed to full analysis. If ANY unchecked → pass or investigate.

---

## Phase 3: Deal Analysis

### Rental Property Calculator

```
MONTHLY INCOME
  Gross Rent:                    $______
  + Other Income (laundry, parking, storage):  $______
  = Gross Monthly Income:        $______

MONTHLY EXPENSES
  Mortgage (P&I):                $______
  Property Tax:                  $______ (annual / 12)
  Insurance:                     $______ (annual / 12)
  Vacancy Reserve:               $______ (8-10% of gross rent)
  Maintenance Reserve:           $______ (8-10% of gross rent)
  CapEx Reserve:                 $______ (5-8% of gross rent)
  Property Management:           $______ (8-12% of gross rent)
  HOA/Condo Fees:               $______
  Utilities (if landlord-paid):  $______
  = Total Monthly Expenses:      $______

MONTHLY CASH FLOW = Gross Income - Total Expenses
ANNUAL CASH FLOW = Monthly × 12

KEY METRICS
  Cash-on-Cash Return = Annual Cash Flow / Total Cash Invested × 100
  Cap Rate = NOI / Purchase Price × 100
  NOI = Annual Income - Annual Operating Expenses (excluding mortgage)
  GRM = Purchase Price / Annual Gross Rent
  DSCR = NOI / Annual Debt Service (lenders want > 1.25)
  50% Rule (screening): Expenses ≈ 50% of gross rent (excluding mortgage)
```

### Fix & Flip Calculator

```
ACQUISITION
  Purchase Price:       $______
  Closing Costs (buy):  $______ (2-4%)
  = Total Acquisition:  $______

REHAB
  Renovation Budget:    $______
  + Contingency (15%):  $______
  = Total Rehab:        $______

HOLDING COSTS (Monthly × Hold Time)
  Loan Payments:        $______ /mo × ____ months
  Insurance:            $______ /mo × ____ months
  Taxes:               $______ /mo × ____ months
  Utilities:           $______ /mo × ____ months
  = Total Holding:      $______

SELLING COSTS
  Agent Commission:     $______ (5-6% of ARV)
  Closing Costs:       $______ (1-2% of ARV)
  Staging:             $______
  = Total Selling:     $______

TOTAL INVESTMENT = Acquisition + Rehab + Holding + Selling

PROFIT = ARV - Total Investment
ROI = Profit / Cash Invested × 100

RULES:
  70% Rule: Max Offer = ARV × 0.70 - Repair Costs
  Minimum profit target: $25,000 or 15% of ARV
```

### BRRRR Analysis

```
BUY:     Purchase price + closing costs
REHAB:   Renovation budget + contingency
RENT:    Market rent verification (3+ comps)
REFINANCE:
  After Repair Value (ARV):     $______
  Refinance LTV (75%):          $______
  New Loan Amount:              $______
  Cash Recovered:               New Loan - Original Loan Payoff
  Cash Left In Deal:            Total Invested - Cash Recovered
REPEAT:
  Cash-on-Cash = Annual Cash Flow / Cash Left In Deal
  Target: Infinite return (recover 100%+ of cash invested)
```

### Stress Test (MANDATORY Before Buying)

Run every deal through these scenarios:

| Scenario | Test | Pass Threshold |
|----------|------|----------------|
| Vacancy Spike | What if vacancy hits 20%? | Still cash-flow positive |
| Rate Increase | What if rates rise 2%? (ARM/refi) | Still cash-flow positive |
| Rent Decline | What if rents drop 10%? | Still covers mortgage + reserves |
| Major Repair | $10K-$20K unexpected expense | Can cover without selling |
| Market Crash | What if value drops 20%? | Not underwater on loan |
| Eviction | 3 months no rent + legal costs | Reserves cover it |

**If ANY scenario = financial distress → don't buy or renegotiate terms.**

---

## Phase 4: Due Diligence

### Property Inspection Checklist

```
STRUCTURE (Deal-Breakers First)
□ Foundation — cracks, settling, water intrusion
□ Roof — age, condition, remaining life (replace: $8K-$15K+)
□ Electrical — panel age, amperage (100A minimum), knob-and-tube?
□ Plumbing — material (copper/PEX good, polybutylene/galvanized bad), water pressure
□ HVAC — age, type, efficiency (replace: $5K-$12K)
□ Water heater — age, capacity, type
□ Windows — single/double pane, condition, drafts

INTERIOR
□ Flooring — type, condition, repair vs replace
□ Walls/ceilings — water stains (= active leak?), cracks
□ Kitchen — cabinets, counters, appliances, layout
□ Bathrooms — fixtures, tile, ventilation, water damage
□ Doors — operation, locks, weather sealing

EXTERIOR
□ Siding — material, condition, paint
□ Drainage — grading away from foundation, gutters
□ Driveway/walkways — condition
□ Landscaping — trees near foundation, overgrowth
□ Fencing — condition, property line verification

ENVIRONMENTAL
□ Lead paint (pre-1978 homes)
□ Asbestos (insulation, tiles, siding)
□ Radon testing
□ Mold inspection
□ Termite/pest inspection
□ Flood zone check (FEMA maps)

TITLE & LEGAL
□ Title search — liens, encumbrances, easements
□ Survey — boundaries match deed
□ Zoning verification — conforming use
□ HOA review — rules, reserves, assessments, litigation
□ Permit history — all work permitted and closed
□ Property tax verification — pending reassessment?
```

### Comparable Sales Analysis (CMA)

```yaml
subject_property:
  address: ""
  beds: 0
  baths: 0
  sqft: 0
  lot_size: 0
  year_built: 0
  condition: ""  # poor | fair | average | good | excellent
  features: []   # garage, pool, basement, updated kitchen

comparables:  # Need 3-5, sold within 6 months, within 1 mile
  - address: ""
    sold_price: 0
    sold_date: ""
    beds: 0
    baths: 0
    sqft: 0
    adjustments:
      sqft_diff: 0       # +/- $50-$150 per sqft
      bed_diff: 0        # +/- $5K-$15K per bedroom
      bath_diff: 0       # +/- $5K-$10K per bathroom
      condition_diff: 0  # +/- $5K-$30K
      garage_diff: 0     # +/- $5K-$15K
      age_diff: 0        # +/- $1K-$5K per decade
    adjusted_price: 0

estimated_value:
  low: 0    # Lowest adjusted comp
  mid: 0    # Average of adjusted comps
  high: 0   # Highest adjusted comp
  confidence: ""  # high (tight range) | medium | low (wide spread)
```

---

## Phase 5: Financing

### Loan Type Decision Matrix

| Loan Type | Down Payment | Rate | Best For | Watch Out |
|-----------|-------------|------|----------|-----------|
| Conventional | 20-25% | Lowest | Strong credit, primary or investment | DTI limits |
| FHA | 3.5% | Low | First-time buyers, house hack | Owner-occupy required, MIP |
| VA | 0% | Very Low | Veterans, house hack | Eligibility, funding fee |
| DSCR | 20-25% | Higher | Investors, no income verification | Higher rates, prepay penalty |
| Hard Money | 10-30% | Highest (10-15%) | Flips, bridge loans | Short term (6-18mo), points |
| Seller Finance | Negotiable | Negotiable | Creative deals, no bank qualifying | Balloon risk, due-on-sale |
| HELOC | N/A | Variable | Rehab funding, down payment | Variable rate, cross-collateral |
| Commercial | 25-35% | Medium-High | 5+ units, mixed-use | Shorter amort, balloon |

### Creative Financing Strategies

1. **Subject-To** — Take over existing mortgage payments without formally assuming. Risk: due-on-sale clause
2. **Seller Carryback** — Seller acts as lender for portion. Combine with bank loan for lower down
3. **Lease Option** — Control property with option to buy. Lock price now, close later
4. **Self-Directed IRA/401K** — Use retirement funds for real estate. Complex rules, need custodian
5. **Partnership/JV** — One brings capital, other brings time/expertise. Define roles in operating agreement
6. **Private Money** — Borrow from individuals at agreed terms. More flexible than hard money

### Refinance Decision Framework

Refinance when ALL true:
- New rate saves >0.5% AND payback period < 3 years
- OR cash-out refinance recovers capital for next deal
- Sufficient equity (>25% after refi)
- Plan to hold property >3 more years
- No prepayment penalty or penalty < savings

---

## Phase 6: Property Management

### Tenant Screening System

```yaml
screening_criteria:
  income:
    minimum_ratio: 3.0  # Monthly income / monthly rent
    verification: ["pay_stubs_2mo", "tax_returns", "bank_statements", "employment_letter"]
  credit:
    minimum_score: 620  # Adjust for market
    red_flags:
      - "active_collections_over_500"
      - "prior_eviction"
      - "bankruptcy_under_2yrs"
      - "multiple_late_payments"
  background:
    check: ["criminal", "eviction_history", "sex_offender"]
    disqualify:
      - "violent_felony"
      - "drug_manufacturing"
      - "prior_eviction_last_5yrs"
    # NOTE: Follow Fair Housing laws — no blanket bans
  rental_history:
    minimum_years: 2
    verify: ["landlord_references_x2", "payment_history"]
    red_flags:
      - "no_references_available"
      - "lease_violations"
      - "unauthorized_occupants"
  
  scoring:  # Weight and score for borderline cases
    income: 30
    credit: 25
    rental_history: 25
    employment_stability: 10
    completeness: 10
    # Accept: >70/100 | Review: 50-70 | Decline: <50
```

### Lease Essentials Checklist

```
MUST INCLUDE (All Jurisdictions)
□ Parties (full legal names of all adults)
□ Property address and description
□ Lease term (start/end dates)
□ Rent amount, due date, payment methods
□ Security deposit amount and return conditions
□ Late fee policy (amount, grace period)
□ Maintenance responsibilities (landlord vs tenant)
□ Entry/access notice requirements
□ Termination/renewal procedures
□ Pet policy (if applicable — breed, size, deposit)
□ Occupancy limits
□ Utilities responsibility
□ Insurance requirements (renter's insurance)

JURISDICTION-SPECIFIC (Verify Locally)
□ Rent increase notice requirements
□ Security deposit limits and interest
□ Lead paint disclosure (pre-1978)
□ Mold disclosure
□ Bed bug policy
□ Smoke/CO detector compliance
□ Habitability standards
□ Domestic violence provisions
```

### Rent Setting Framework

```
MARKET RENT DETERMINATION
1. Search 5+ comparable rentals within 1 mile (same beds/baths/sqft range)
2. Adjust for: condition, amenities, parking, laundry, updates
3. Check trend: rising, flat, or declining market
4. Set at or slightly below market for fast occupancy (2-4 weeks target)

RENT INCREASE DECISION
  Current market rent: $______
  Current tenant rent:  $______
  Gap: $______
  Tenant tenure: ____ years
  Payment history: excellent / good / fair / poor

  IF gap < 3%: Skip increase (retention > marginal revenue)
  IF gap 3-10%: Increase to close 50% of gap
  IF gap > 10%: Increase to close 75% of gap
  IF tenant is problematic: Increase to full market (or non-renew)

  TURNOVER COST CHECK:
  Vacancy (1 month): $______
  Make-ready repairs: $______
  Listing/screening: $______
  Total turnover cost: $______
  Months to recoup with increase: Total / Monthly Increase
  IF > 12 months to recoup: Consider smaller increase
```

### Maintenance Priority System

| Priority | Response Time | Examples |
|----------|-------------|---------|
| P0 — Emergency | Immediate (1-4 hrs) | Water leak, no heat (winter), gas leak, fire damage, lockout |
| P1 — Urgent | 24 hours | Broken AC (summer), no hot water, toilet not working (only one), appliance failure |
| P2 — Standard | 3-7 days | Minor plumbing, non-critical appliance, pest issue |
| P3 — Low | 2-4 weeks | Cosmetic issues, landscaping, minor repairs |
| P4 — Scheduled | Next turnover | Paint, carpet, upgrades |

---

## Phase 7: Tax Strategy

### Real Estate Tax Benefits

1. **Depreciation** — Deduct property value (not land) over 27.5 years (residential) or 39 years (commercial)
   - Cost segregation study: accelerate depreciation on components (5, 7, 15 year)
   - Bonus depreciation: 40% in 2026 (declining annually)
2. **Mortgage Interest** — Fully deductible on investment properties
3. **Operating Expenses** — Property management, insurance, repairs, travel, education
4. **1031 Exchange** — Defer capital gains by reinvesting in like-kind property
   - 45-day identification period, 180-day closing deadline
   - Must be equal or greater value and debt
5. **Real Estate Professional Status** — If qualified (750+ hrs, material participation), deduct losses against active income
6. **Opportunity Zones** — Tax benefits for investing in designated areas
7. **Pass-Through Deduction (199A)** — Up to 20% QBI deduction

### Annual Tax Checklist

```
□ Track all income by property
□ Track all expenses by property (receipts!)
□ Calculate depreciation (include improvements)
□ Document mileage for property visits
□ Review 1031 exchange eligibility for any sales
□ Evaluate cost segregation for new purchases
□ Review RE Professional status hours log
□ Consult CPA before Dec 31 for year-end planning
```

---

## Phase 8: Portfolio Management

### Portfolio Health Dashboard

```yaml
portfolio_snapshot:
  date: ""
  total_units: 0
  total_value: 0        # Current market value
  total_debt: 0         # Outstanding mortgages
  total_equity: 0       # Value - Debt
  ltv_ratio: 0          # Debt / Value (target: <70%)
  monthly_gross_income: 0
  monthly_expenses: 0
  monthly_net_cashflow: 0
  annual_cash_on_cash: 0 # %
  portfolio_cap_rate: 0  # %
  average_vacancy: 0     # % (target: <8%)
  
properties:
  - address: ""
    type: ""             # SFR, duplex, etc.
    units: 1
    purchase_price: 0
    purchase_date: ""
    current_value: 0
    mortgage_balance: 0
    equity: 0
    monthly_rent: 0
    monthly_expenses: 0
    monthly_cashflow: 0
    cash_on_cash: 0
    cap_rate: 0
    occupancy: 0         # %
    condition: ""        # A, B, C, D
    next_action: ""      # hold, refinance, sell, improve
```

### Hold vs Sell Decision Framework

**Sell when 2+ are true:**
- Cash-on-cash return < 5% AND no appreciation play
- Property requires >$20K deferred maintenance
- Market at cyclical peak (price-to-rent ratio stretched)
- Better use of equity elsewhere (opportunity cost)
- Management headaches disproportionate to returns
- Neighborhood in sustained decline
- 1031 exchange into superior asset available

**Hold when:**
- Cash flow positive with growing rents
- Below-market mortgage locked in
- Significant depreciation remaining
- Appreciation trend intact
- Low management burden
- Strong tenant in place

### Scaling Strategy

| Portfolio Size | Focus | Key Challenge |
|---------------|-------|---------------|
| 1-4 units | Learn fundamentals, systems | Analysis paralysis |
| 5-10 units | Hire PM, systematize | Cash flow vs growth |
| 11-25 units | Team building, commercial loans | Financing complexity |
| 26-50 units | Asset management, syndication | Operational complexity |
| 50+ units | Institutional standards, raise capital | Compliance, investor relations |

---

## Phase 9: Short-Term Rental (STR) Operations

### STR Feasibility Analysis

```
REVENUE ESTIMATION
  Average Daily Rate (ADR): $______ (AirDNA, PriceLabs, comp search)
  Occupancy Rate: ______% (conservative: 65%, good: 75%, great: 85%)
  Monthly Revenue = ADR × 30 × Occupancy Rate

ADDITIONAL STR COSTS (vs long-term rental)
  Furnishing (one-time): $5K-$25K depending on size
  Cleaning (per turnover): $75-$200
  Supplies/amenities (monthly): $100-$300
  Channel management software: $50-$200/mo
  Dynamic pricing tool: $20-$100/mo
  Professional photos: $200-$500 (one-time)
  Higher insurance: +$500-$2K/year
  Higher utilities: +$200-$500/mo (you pay all)
  Licensing/permits: $0-$5K/year
  Occupancy/tourism tax: varies (8-15% of revenue)

NET = Revenue - All LTR Expenses - Additional STR Costs
Compare: STR Net vs LTR Net. Need >30% premium to justify extra work.
```

### STR Listing Optimization

```
TITLE FORMULA: [Unique Feature] + [Location/View] + [Key Amenity]
  Example: "Lakefront Cabin w/ Hot Tub | 5 Min to Slopes | Sleeps 8"

PHOTOS (20+ required):
  1. Hero shot (best exterior or view)
  2. Living room (wide angle, lights on)
  3. Kitchen (clean, staged)
  4. Master bedroom
  5. Master bathroom
  6. Each additional bedroom
  7. Outdoor space / patio
  8. Amenities (hot tub, pool, game room)
  9. Neighborhood / attraction proximity
  10. Welcome touches (basket, guidebook)

DESCRIPTION STRUCTURE:
  Para 1: The experience (emotional, what makes it special)
  Para 2: The space (factual, beds/baths/capacity)
  Para 3: The location (distance to attractions, restaurants)
  Para 4: The amenities (bullet list)
  Para 5: Guest expectations (house rules, check-in)

PRICING STRATEGY:
  - Use dynamic pricing (PriceLabs, Beyond, Wheelhouse)
  - New listing: 20% below market for first 5 bookings (reviews)
  - Weekend premium: +20-40%
  - Event/seasonal premium: +50-200%
  - Last-minute discount: -15% within 3 days
  - Length-of-stay discount: 10% weekly, 20% monthly
```

---

## Phase 10: Advanced Strategies

### Value-Add Playbook

| Strategy | Cost | Rent Increase | ROI |
|----------|------|---------------|-----|
| Kitchen update (counters, paint, hardware) | $3K-$8K | $75-$200/mo | 12-30 months |
| Bathroom refresh (vanity, fixtures, paint) | $1.5K-$4K | $50-$100/mo | 15-40 months |
| Flooring (LVP throughout) | $2K-$6K | $50-$150/mo | 20-40 months |
| Washer/dryer (in-unit) | $1K-$2K | $50-$100/mo | 10-20 months |
| Smart home (thermostat, locks, lights) | $500-$1.5K | $25-$50/mo | 10-30 months |
| Add bedroom (convert den/office) | $2K-$10K | $100-$300/mo | 7-33 months |
| ADU / garage conversion | $30K-$100K | $800-$2000/mo | 15-50 months |
| Utility bill-back (RUBS) | $500 | $50-$150/mo | 3-10 months |
| Laundry (coin-op) | $3K-$8K | $50-$100/unit/mo | 3-13 months |

### 1031 Exchange Checklist

```
BEFORE SELLING
□ Identify qualified intermediary (QI) BEFORE closing
□ Document investment intent (not personal use)
□ Calculate basis and estimated gain
□ Identify potential replacement properties

TIMELINE (Strict — No Extensions)
  Day 0: Close sale of relinquished property
  Day 45: Identify up to 3 replacement properties (or 200% rule)
  Day 180: Close on replacement property
  
RULES
□ Like-kind (any real property → any real property)
□ Equal or greater value
□ Equal or greater debt
□ All equity reinvested (boot = taxable)
□ Same taxpayer on both transactions
□ Not personal residence (unless converted)
□ QI holds funds (never touch the money)
```

### Syndication Basics (Raising Capital)

```
STRUCTURE
  - GP (General Partner): You — finds deals, manages, earns fees + promote
  - LP (Limited Partners): Investors — passive, earn preferred return + split
  
TYPICAL TERMS
  Preferred Return: 6-8% (LP gets paid first)
  Profit Split: 70/30 or 80/20 (LP/GP after preferred)
  Acquisition Fee: 1-3% of purchase price (to GP)
  Asset Management Fee: 1-2% of revenue (to GP)
  Hold Period: 3-7 years
  
REQUIREMENTS
  - Securities attorney (506(b) or 506(c) exemption)
  - CPA experienced in syndication
  - Track record (start with JV, then syndicate)
  - PPM, operating agreement, subscription agreement
  - Investor relations system
```

---

## Phase 11: Market Cycles & Timing

### Real Estate Cycle Phases

```
EXPANSION → HYPER-SUPPLY → RECESSION → RECOVERY → EXPANSION...

EXPANSION (BUY)
  Signals: Rising rents, falling vacancy, new construction starting
  Strategy: Acquire aggressively, lock long-term financing

HYPER-SUPPLY (CAUTION)  
  Signals: Overbuilding, rising vacancy, rent growth slowing
  Strategy: Stop acquiring, focus on operations, build reserves

RECESSION (PREPARE)
  Signals: Rising vacancy, falling rents, distress sales emerging
  Strategy: Hold cash, hunt distressed deals, negotiate hard

RECOVERY (AGGRESSIVE BUY)
  Signals: Vacancy stabilizing, construction stopped, prices bottoming
  Strategy: Maximum acquisition mode — best deals of the cycle
```

### Interest Rate Impact Rules

- Rate ↑ 1% = ~10% reduction in purchasing power
- Rate ↑ → prices soften (buying opportunity if cash flow still works)
- Rate ↓ → prices rise (refinance existing, sell flips)
- Always underwrite at current rates + 1% buffer
- ARMs: only if plan to sell/refi within fixed period

---

## Quality Scoring (0-100)

| Dimension | Weight | Score |
|-----------|--------|-------|
| Financial Analysis Rigor | 20% | Numbers verified, stress-tested, conservative assumptions |
| Due Diligence Completeness | 15% | All inspection items checked, title clear |
| Market Research Depth | 15% | Multiple data sources, trends analyzed |
| Risk Assessment | 15% | Downside scenarios modeled, mitigations planned |
| Legal/Tax Compliance | 10% | Jurisdiction-specific, professional consultation noted |
| Operational Planning | 10% | PM, maintenance, tenant systems in place |
| Exit Strategy Clarity | 10% | Hold period, triggers, 1031 optionality |
| Documentation Quality | 5% | Organized, retrievable, complete records |

---

## Edge Cases

### First-Time Buyer
- Start with house hack (FHA 3.5% down, live in one unit)
- Build reserves before buying investment property
- Get pre-approved, then find deals (not reverse)

### Remote Investing
- Visit market first (fly once, walk neighborhoods)
- Build team BEFORE buying: agent, PM, contractor, inspector
- Never rely solely on photos — video walkthroughs minimum

### Inherited Property
- Get appraisal immediately (stepped-up basis = date of death value)
- Evaluate: sell, rent, or 1031 exchange
- Clear title issues ASAP (probate timeline varies)

### Rising Rate Environment
- Focus on cash flow over appreciation
- Seller financing and assumable mortgages = gold
- Negotiate price reductions (fewer buyers = leverage)
- Avoid ARMs unless very short hold period

### Tenant Disputes
- Document everything in writing
- Follow local eviction procedures EXACTLY
- Offer cash-for-keys before formal eviction (often cheaper)
- Never self-help evict (illegal everywhere)

### Natural Disaster / Insurance
- Get proper coverage BEFORE closing (flood, earthquake, wind separate)
- Document property condition with photos/video
- Keep separate reserve for insurance deductibles
- Review policy annually — don't be underinsured

---

## Commands

```
"Analyze this deal"     → Full rental/flip/BRRRR calculator
"Screen this property"  → 5-minute screening checklist
"Compare these comps"   → CMA analysis with adjustments
"Set rent for [addr]"   → Market rent analysis with comp research
"Screen this tenant"    → Scoring template with criteria
"Review my portfolio"   → Portfolio health dashboard
"Should I sell [addr]"  → Hold vs sell framework
"STR feasibility"       → Short-term rental analysis
"1031 exchange plan"    → Timeline and checklist
"Market analysis [city]" → Full market scoring
"Value-add options"     → Renovation ROI analysis
"Tax strategy review"   → Annual tax optimization checklist
```

---

## ⚠️ Disclaimer

This skill provides educational frameworks and analysis templates. **It is not legal, tax, or investment advice.** Always consult qualified professionals (attorney, CPA, licensed agent) for jurisdiction-specific guidance. Laws vary dramatically by location. Never make investment decisions based solely on AI analysis.
