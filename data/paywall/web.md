# Web/SaaS Pricing Pages

## Pricing Page vs In-App Paywall

| Pricing Page | In-App Upgrade |
|--------------|----------------|
| Pre-signup decision | Post-signup upsell |
| Compare all plans | Highlight upgrade path |
| SEO-indexed | Authenticated only |
| Longer consideration | Quick decision |

---

## Pricing Page Structure

```
Hero (headline + subheadline)
↓
Plan cards (2-4 tiers)
↓
Feature comparison table (expandable)
↓
FAQ
↓
Social proof
↓
Final CTA
```

---

## Plan Card Anatomy

Each plan card should include:

1. **Plan name** — Free, Pro, Business, Enterprise
2. **Price** — Monthly/annual toggle above cards
3. **Billing period** — "/month" or "/user/month"
4. **Primary CTA** — "Start free trial", "Get started"
5. **Feature list** — 5-8 key features
6. **Highlight** — "Most popular" badge on recommended plan

### Plan Card Layout
```
┌─────────────────┐
│     PRO         │
│   MOST POPULAR  │
├─────────────────┤
│    $29/mo       │
│  billed annually│
├─────────────────┤
│ ✓ Feature 1     │
│ ✓ Feature 2     │
│ ✓ Feature 3     │
│ ✓ Feature 4     │
│ ✓ Feature 5     │
├─────────────────┤
│ [Start trial]   │
└─────────────────┘
```

---

## How Many Plans?

| # Plans | When |
|---------|------|
| 2 | Simple product, clear free/paid split |
| 3 | Most common. Free → Pro → Business |
| 4 | Enterprise segment + self-serve |
| 5+ | Usually too many. Confuses users. |

**Decoy effect:** The middle plan often converts best when framed between budget and premium options.

---

## Monthly vs Annual Toggle

### Display Options
- Toggle switch (most common)
- Tabs
- Radio buttons

### Annual Discount
Standard: 15-20% off monthly equivalent
Aggressive: 30-50% (often called "2 months free")

### Default Selection
**Always default to annual.** Higher LTV, lower churn.

Show monthly equivalent: "$29/mo billed annually" not just "$348/year"

---

## Feature Comparison Table

### Rules
- Lead with features that differentiate paid plans
- Use checkmarks and X marks (not "unlimited" vs "limited")
- Group features into categories
- Make it scannable
- Collapsible on mobile

### Table Structure
```
| Feature          | Free | Pro | Business |
|------------------|------|-----|----------|
| Projects         | 3    | ∞   | ∞        |
| Team members     | 1    | 5   | ∞        |
| Storage          | 1GB  | 50GB| 500GB    |
| Priority support | ✗    | ✓   | ✓        |
| Custom domain    | ✗    | ✗   | ✓        |
```

---

## Enterprise Tier

### When to Include
- B2B product
- Deals over $10K/year expected
- Custom requirements common

### Enterprise Card Content
- "Contact sales" or "Book a demo" CTA
- "Everything in Business, plus:"
- SSO, SLA, dedicated support, custom contracts
- No public price (negotiate)

---

## FAQ Section

### Must-Answer Questions
- Can I change plans later?
- What happens when trial ends?
- Do you offer refunds?
- Is there a free tier?
- What payment methods do you accept?

### Format
Accordion/collapsible. 5-8 questions max.

---

## Trust Elements

### Near Pricing
- "Cancel anytime"
- "No credit card required" (if true for trial)
- "30-day money-back guarantee"
- Security badges (SOC 2, GDPR)

### Social Proof
- Customer logos
- "Trusted by X,000 teams"
- G2/Capterra ratings

---

## In-App Upgrade Prompts

### Contextual Triggers
- User hits feature limit
- User tries premium feature
- Usage milestone ("You've created 100 projects!")
- Trial ending soon

### Upgrade Modal Content
1. What they're missing (feature they just hit)
2. What they get with upgrade
3. Price + CTA
4. "Maybe later" option

### Banner Prompts
Persistent but dismissible upgrade banners:
- Top of dashboard
- Feature sidebar
- Settings page

---

## Checkout Flow

### Reduce Friction
- Pre-fill known info (email, name)
- Minimal form fields
- Show order summary
- Apply discount codes
- Multiple payment methods

### Post-Checkout
- Confirmation page with next steps
- Welcome email with onboarding
- In-app celebration/confetti (tastefully)
