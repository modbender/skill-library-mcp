# Marketplace Builder Guide

## Cold Start Playbooks

**Supply-first approach:**
- Recruit suppliers before demand exists
- Offer fee-free period / guaranteed minimum payouts
- Curate aggressively—quality over quantity

**Demand-first approach:**
- Build waitlist, then onboard supply to match
- Works for scarce/premium supply

**Managed marketplace:**
- Platform handles transactions manually at first
- Validates unit economics before automation
- Higher cost but proves model works

**Geographic constraint:**
- Launch in single city/region
- Achieve density before expansion
- Local network effects compound

## Liquidity Thresholds

- **Below 30% search success rate** = buyers churn
- Model this BEFORE scoping launch geography
- Better to be dense in one area than sparse everywhere

## Commission Structures

| Model | When to Use |
|-------|-------------|
| Transaction fee (5-20%) | Standard; aligns with GMV |
| Subscription | Predictable revenue; works for high-volume sellers |
| Freemium | Low barrier entry; monetize power users |
| Lead gen fee | Services marketplaces; charge per lead vs transaction |
| Featured listings | Additional revenue; don't make it pay-to-play |

**Take rate ceiling:**
- Sellers compare alternatives
- Exceed their margin tolerance = price inflation or exit
- 15-20% is common ceiling for most categories

## Trust System Design

**Verification tiers:**
- Identity verification (real name, phone)
- Payment method verification
- Background checks (services)
- Portfolio/credential review

**Rating systems:**
- Two-sided ratings prevent retaliation
- Don't show ratings until both parties submit
- Weight recent ratings higher

**Dispute resolution:**
- Clear escalation path
- Time-limited response windows
- Platform arbitration as final step

## Payment Integration Complexity

**NOT "just Stripe Connect":**
- Escrow timing varies by category
- Services: release after delivery window
- Goods: release after delivery confirmation
- Rentals: security deposits and damage claims

**International payouts:**
- Currency conversion fees
- Local payment method preferences
- Tax withholding requirements

**Merchant of Record implications:**
- MoR = you handle VAT/sales tax collection
- MoR = you're liable for chargebacks
- MoR = PCI compliance scope expands

## Regulatory Landmines

- **Services marketplaces:** Gig worker classification risk
- **Rentals:** Insurance requirements, liability for injuries
- **B2B:** Invoicing, net-30/60 terms, credit checks
- **Consumer goods:** Warranty obligations vary by jurisdiction
- **EU:** 14-day cooling-off period mandatory
