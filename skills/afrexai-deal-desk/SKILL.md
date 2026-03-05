# Deal Desk — Structured Deal Review & Approval

Run every non-standard deal through a repeatable review process. Catch margin leaks, enforce discount guardrails, and close faster with pre-approved terms.

## When to Use
- Custom pricing requests above standard discount thresholds
- Multi-year contracts needing approval
- Bundle or package deals outside published pricing
- Enterprise deals with non-standard terms (payment, SLA, liability)
- Partner/reseller margin negotiations

## Deal Review Framework

### 1. Deal Qualification Check
Before pricing, confirm the deal is worth pursuing:

| Question | Red Flag If... |
|----------|---------------|
| Annual contract value (ACV) | Below $10K for enterprise motion |
| Decision timeline | "No urgency" or 6+ months out |
| Budget confirmed? | "We'll find budget later" |
| Champion identified? | No internal advocate |
| Technical fit validated? | Requirements don't match product |

**Kill criteria:** 2+ red flags = send back to sales for re-qualification.

### 2. Pricing Guardrails

#### Standard Discount Authority
| Discount Level | Approver | Conditions |
|---------------|----------|------------|
| 0-10% | AE (self-approve) | Standard annual contract |
| 11-20% | Sales Manager | Multi-year or 3+ seat expansion |
| 21-30% | VP Sales + Finance | Strategic account, logo value documented |
| 31-40% | CRO/CEO | Exceptional — requires written business case |
| 40%+ | Board/CEO only | Almost never. Document why. |

#### Discount Offsets (Give to Get)
Never discount without getting something back:
- **Case study rights** → worth 5-10% discount
- **Multi-year commitment** → 5% per additional year
- **Upfront annual payment** → 5-10% (cash flow value)
- **Reference calls** → worth 3-5%
- **Expanded scope** → reduce per-unit but increase total ACV
- **Shorter payment terms** → Net-15 vs Net-60 = real cash value

### 3. Deal Structure Templates

#### Template A: Standard Annual
- Payment: Annual upfront
- Term: 12 months, auto-renew
- Discount: Per guardrails above
- SLA: Standard published SLA

#### Template B: Multi-Year
- Payment: Annual upfront each year (not all upfront unless 10%+ discount warranted)
- Term: 24-36 months
- Price lock: Year 1 rate locked, 3-5% annual increase cap
- Early termination: Remaining term billed at 50%

#### Template C: Enterprise Custom
- Payment: Quarterly or monthly (premium: +10-15% vs annual)
- Term: Negotiable
- SLA: Custom with defined penalties
- Liability cap: 12 months of fees (standard), negotiate up only with legal review
- Data processing: DPA required, included in standard terms

#### Template D: Partner/Reseller
- Margin: 20-30% off list (tiered by volume)
- Deal registration: 90-day protection window
- Co-sell vs resell: Define clearly — affects margin and support responsibility
- Minimum commitment: Required for highest tier

### 4. Approval Workflow
```
AE submits deal → Deal Desk reviews (same day) →
  IF standard terms + approved discount: Auto-approve
  IF non-standard: Route to approver chain →
    Finance review (margin check) →
    Legal review (if custom terms) →
    Final approval →
AE receives approved terms + redlines
```

**SLA:** Deal Desk responds within 4 business hours. Escalation if no response in 8.

### 5. Margin Analysis

For every deal, calculate:

- **Gross margin %** = (ACV - COGS) / ACV × 100
- **Effective discount** = (List price - Deal price) / List price × 100
- **Payback period** = CAC / (Monthly revenue × Gross margin %)
- **LTV:CAC ratio** = (ACV × Expected years × Margin) / Total CAC

**Minimum thresholds:**
- Gross margin: >65% (SaaS), >40% (services)
- LTV:CAC: >3:1
- Payback: <18 months

### 6. Red Flags That Kill Deals

1. **"We need 50% off to start"** — They'll never pay full price. Walk away or repackage.
2. **Unlimited liability demand** — Legal trap. Cap at 12 months fees, firm.
3. **"Our legal will redline everything"** — Budget 4-6 weeks for legal cycle. Price it in.
4. **Payment terms beyond Net-60** — Cash flow killer. Offer early payment discount instead.
5. **Scope creep during negotiation** — New requirements = new SOW, not same price.
6. **No executive sponsor** — Deal will stall. Get sponsor or pause.
7. **Competitor benchmark bluff** — "Company X offered us 40% less." Verify. Usually inflated.

### 7. Post-Close Handoff

Deal Desk creates handoff doc:
- Agreed pricing and terms
- Custom commitments (SLAs, deliverables, timelines)
- Discount justification (for renewal team context)
- Upsell/expansion opportunities identified during negotiation
- Key contacts and decision-maker map

## Industry Deal Patterns

| Industry | Typical ACV | Common Ask | Watch For |
|----------|------------|------------|-----------|
| **Fintech** | $50K-$500K | SOC 2 + BAA | Compliance creep |
| **Healthcare** | $30K-$200K | HIPAA BAA mandatory | Slow procurement |
| **Legal** | $40K-$300K | Custom data retention | Scope inflation |
| **Construction** | $20K-$100K | Per-project pricing | Seasonal churn |
| **Ecommerce** | $25K-$150K | Revenue-share model | GMV volatility |
| **SaaS** | $30K-$250K | API/integration SLAs | Platform risk |
| **Real Estate** | $15K-$80K | Per-property pricing | Market sensitivity |
| **Recruitment** | $20K-$120K | Per-placement pricing | Volume variability |
| **Manufacturing** | $50K-$400K | On-prem/hybrid option | IT approval cycles |
| **Professional Services** | $25K-$200K | White-label rights | Margin compression |

## Resources

- **AI Revenue Leak Calculator** — quantify what deals are costing you: https://afrexai-cto.github.io/ai-revenue-calculator/
- **Industry Context Packs** ($47 each) — deep frameworks for your vertical: https://afrexai-cto.github.io/context-packs/
- **Agent Setup Wizard** — deploy deal desk automation: https://afrexai-cto.github.io/agent-setup/

### Bundle Deals
- Pick 3 packs: $97 (save $44)
- All 10 packs: $197 (save $273)
- Everything Bundle: $247
