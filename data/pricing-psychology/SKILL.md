---
name: Pricing Psychology — Strategic Pricing Framework
description: "Design pricing that converts using cognitive biases and proven
  psychological principles. Sources: Phoenix Strategy Group, ScaleCrush,
  NetSuite research, SaaS pricing studies (2024-2026). All output..."
---

# Pricing Psychology — Strategic Pricing Framework

Design pricing that converts using cognitive biases and proven psychological principles.
Sources: Phoenix Strategy Group, ScaleCrush, NetSuite research, SaaS pricing studies (2024-2026).
All outputs go to `workspace/artifacts/`.

## Use when
- Setting prices for products, services, or subscriptions
- Designing pricing pages or tier structures
- Evaluating whether current pricing is leaving money on the table
- Preparing proposals or quotes for clients
- Choosing between pricing models (flat, tiered, usage-based, etc.)
- Repricing after market feedback or competitive analysis

## Don't use when
- Internal cost accounting or budgeting (this is about perception, not COGS)
- Commodity pricing where market sets the price (gas, raw materials)
- Regulatory/government pricing with fixed rate schedules
- Charity/nonprofit where pricing psychology feels manipulative

## Negative examples
- "Calculate my profit margins" → No. This is pricing perception, not accounting.
- "What should I charge per hour?" → Borderline. Use this to FRAME the rate, not calculate it.
- "How much does AWS cost?" → No. This is for setting YOUR prices, not understanding others'.

## Edge cases
- Freelance rate setting (Upwork, etc.) → YES. Framing and anchoring apply heavily.
- "Should I charge $29 or $30?" → YES. Charm pricing analysis directly applies.
- Negotiation prep → YES. Anchoring is the #1 negotiation tactic.
- Free tier decisions → YES. Free-to-paid conversion is a pricing psychology problem.

---

## The 9 Core Principles

### 1. Charm Pricing (Left-Digit Bias)
Prices ending in .99 or .97 feel significantly cheaper than the next round number.

**The science:** Our brains process left-to-right, anchoring on the first digit. $9.99 feels like "$9-something," not "$10."

**Impact:** Studies suggest charm prices can outperform rounded prices significantly (estimates range from 10-24% depending on context and product category). Moving from $4.99 to $5.00 typically causes a 3-6% sales drop.

**When to use:**
- Everyday products, subscriptions, impulse buys
- Price-sensitive audiences
- Competitive markets where $1 perception matters

**When NOT to use:**
- Premium/luxury positioning → use round numbers ($100, not $99.99). Round prices signal quality and confidence.
- B2B enterprise deals → round numbers feel more professional
- Very high price points (>$1,000) → the .99 looks cheap, not smart

**Application to our products:**
- ClawHub skills: $9 or $19 (not $10 or $20)
- Alfred's service: $149/mo (not $150) — charm + just below threshold

### 2. Price Anchoring
The first price a prospect sees becomes their reference point for everything after.

**The science:** Cognitive anchoring bias. A $500/mo option makes $149/mo feel like a steal, even if $149 was always the target.

**How to implement:**
- Always show your highest tier first (on pricing pages, in proposals, in conversation)
- In proposals: state the full value first, then the price. "This system typically delivers $3,000/mo in saved labor. Investment: $149/mo."
- Reference competitor pricing: "Podium charges $399/mo for similar features. We're $149."
- On pricing pages: Enterprise → Pro → Starter (left to right or top to bottom)

**Critical rule:** The anchor must be credible. An absurd anchor ($10,000 for a simple service) backfires and destroys trust.

### 3. Price Thresholds
Customers have mental boundaries. Crossing them triggers disproportionate resistance.

**Common thresholds:** $10, $25, $50, $100, $500, $1,000

**Strategy:** Price just below the threshold.
- $49 instead of $52
- $99 instead of $105
- $499 instead of $520

**The math:** A product at $49 can outsell the same product at $51 by 15-20%, even though the actual difference is $2.

**Application:** Our Reef product at $29 (below $30 threshold) — already correct.

### 4. Decoy Pricing (Asymmetric Dominance)
Add an intentionally unattractive option to make your target option look superior.

**Classic example (The Economist):**
- Digital only: $59
- Print only: $125
- Print + Digital: $125 ← everyone picks this because print-only is the decoy

**How to design a decoy:**
1. Decide which tier you want most people to buy (your "target")
2. Create a tier that's close in price to the target but much worse in value
3. The target now looks like an obvious bargain by comparison

**3-tier formula:**
| Tier | Price | Value | Purpose |
|------|-------|-------|---------|
| Basic | Low | Adequate | Entry point, captures budget buyers |
| Pro (TARGET) | Medium | High | Best value ratio — this is what you want them to buy |
| Premium | High | Highest | Anchor + decoy (close in price to Pro, makes Pro look smart) |

### 5. Bundling & Unbundling
Combining products increases perceived value. Separating them increases perceived cost.

**Bundle when:** You want to increase average order value and perceived savings.
- "Get all 5 skills for $39" (vs $15 each = $75 separately) → 48% savings messaging

**Unbundle when:** You want to show how much you're providing.
- Itemize your service in proposals: "SMS automation ($50 value) + booking system ($75 value) + review management ($50 value) = $175 value, bundled at $149/mo"

**Key insight:** Bundling works for purchases. Unbundling works for perceived value in proposals and negotiations.

### 6. Scarcity & Urgency
Limited availability increases perceived value and triggers loss aversion.

**Ethical applications:**
- "First 10 customers get founding member pricing" (real limit)
- "This rate is locked for 12 months" (real deadline)
- "3 client slots remaining this month" (real capacity constraint)

**Unethical (avoid):**
- Fake countdown timers that reset
- "Only 2 left!" when you have unlimited digital inventory
- Artificial urgency on non-scarce items

**Loss aversion multiplier:** People feel losses ~2x more intensely than equivalent gains. "Save $50/mo" is less powerful than "You're losing $50/mo without this."

### 7. Price Framing
Same price, different frame, different perception.

**Daily vs monthly:** "$3.27/day" feels cheaper than "$99/mo" feels cheaper than "$1,188/year" — even though they're identical.

**Comparison framing:** "Less than your daily coffee" (relatable anchor)

**ROI framing:** "Pays for itself in 2 weeks" (investment, not cost)

**Per-unit framing:** "$0.12 per automated message" (micro-cost feels trivial)

**Best practice:** Frame in the smallest credible unit for affordable products. Frame in ROI terms for expensive ones.

### 8. Social Proof in Pricing
What others chose influences what new buyers choose.

**Tactics:**
- "Most Popular" badge on your target tier (increases selection by 20-30%)
- "X customers chose this plan"
- Testimonials placed next to the price (reduces price objection)
- Case studies with specific ROI numbers near the CTA

**For us:** When we have ClawHub downloads, show install counts. "500+ agents use this skill."

### 9. Tiered Pricing Architecture
Multiple tiers capture different willingness-to-pay segments.

**The rule of 3:** Three tiers is optimal. Two feels like "cheap vs expensive." Four+ causes choice paralysis.

**Tier design principles:**
- Each tier should have a clear "hero feature" that justifies the jump
- Price gaps should feel logical (not 2x jumps — aim for 1.5-2x between tiers)
- The middle tier should be the obvious best value (commonly the most selected tier, though exact % varies by market — design it to be the obvious choice)
- Name tiers by outcome, not features ("Starter / Growth / Scale" beats "Basic / Pro / Enterprise")

---

## Pricing Decision Checklist

When setting any price, run through these questions:

- [ ] **Who is the buyer?** (Price-sensitive consumer vs. value-driven business)
- [ ] **What's the anchor?** (What will they compare this price to?)
- [ ] **Am I below a threshold?** ($10, $25, $50, $100, $500, $1K)
- [ ] **Charm or round?** (Everyday = charm. Premium = round.)
- [ ] **How am I framing it?** (Daily? Monthly? ROI? Comparison?)
- [ ] **Is there a decoy?** (Does my tier structure guide toward the target?)
- [ ] **Social proof near price?** (Testimonials, "most popular," customer count)
- [ ] **Scarcity real?** (Only use if the constraint is genuine)
- [ ] **Have I unbundled in proposals?** (Show itemized value, then bundled price)

---

## Quick Reference: When to Use What

| Situation | Primary Tactic | Secondary |
|-----------|---------------|-----------|
| SaaS/subscription pricing | Tiered + Decoy | Charm + Anchoring |
| Freelance rate setting | Anchoring + Framing | Bundling (package deals) |
| Product launch | Scarcity + Social Proof | Threshold pricing |
| Price increase | Framing + Bundling | Add value before raising |
| Competitive market | Threshold + Comparison | Charm pricing |
| Premium positioning | Round numbers + Anchoring | Unbundling (show value) |
| Proposal/quote | Anchor high → present price | Unbundle + ROI frame |

---

## Key Numbers
- Charm pricing outperforms round by 10-24% depending on context (multiple studies, wide range)
- 40-95% of retail prices end in 9 (industry standard)
- $4.99→$5.00 typically causes 3-6% sales drop
- Decoy pricing increases target tier selection by 10-30% (varies by implementation)
- "Most Popular" badges meaningfully increase target tier selection (test on your own pages)
- Loss aversion: losses feel ~2x stronger than equivalent gains (Kahneman & Tversky, 1979 — Prospect Theory)
- 3 tiers optimal; middle tier typically most selected when designed as best value
- Advanced pricing psychology can increase average deal size 25-60% (SaaS studies, 2026)
