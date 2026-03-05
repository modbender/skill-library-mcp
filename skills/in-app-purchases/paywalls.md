# Paywall Design — Conversion Patterns

## Paywall Anatomy

```
┌─────────────────────────────────┐
│         [Close Button]     X    │
│                                 │
│          🎯 HEADLINE           │
│     Value proposition           │
│                                 │
│    ┌─────────────────────┐     │
│    │  Feature bullets     │     │
│    │  ✓ Benefit 1        │     │
│    │  ✓ Benefit 2        │     │
│    │  ✓ Benefit 3        │     │
│    └─────────────────────┘     │
│                                 │
│    ┌─────────────────────┐     │
│    │  $4.99/month        │     │
│    └─────────────────────┘     │
│    ┌─────────────────────┐     │
│    │  $29.99/year ✨     │ ← Best value
│    │  SAVE 50%           │     │
│    └─────────────────────┘     │
│                                 │
│    [ Start Free Trial ]         │
│                                 │
│    Restore · Terms · Privacy    │
└─────────────────────────────────┘
```

## High-Converting Patterns

### 1. Anchoring (3-Tier Pricing)
Show 3 options, highlight the middle one:

```
Weekly $2.99     ← Decoy (expensive per month)
Monthly $4.99    ← Target (highlighted, "Best Value")
Annual $29.99    ← Anchor (shows big savings)
```

Why it works: Weekly makes monthly seem reasonable. Annual shows commitment.

### 2. Trial First, Price Second
```
✅ "Start your 7-day free trial"
   After trial: $4.99/month

❌ "$4.99/month with 7-day free trial"
```

Lead with free. Price is secondary.

### 3. Social Proof
```
⭐⭐⭐⭐⭐ "Life-changing app!" - @user
"Used by 500,000+ people"
"Featured in App Store"
```

Numbers + testimonials + authority.

### 4. Loss Aversion
```
"Don't lose your progress"
"Keep your streak alive"
"Unlock what you've already built"
```

Works after user has invested time.

### 5. Scarcity/Urgency (Use Carefully)
```
"50% off - Today only"
"Limited time offer"
```

⚠️ Don't fake scarcity. Apple/Google can reject.

## Layout Patterns

### Soft Paywall
User can dismiss, shown periodically:
- After X free uses
- After completing onboarding
- After hitting a limit

```swift
// RevenueCat
PaywallView(displayCloseButton: true)
```

### Hard Paywall
Blocks feature until purchase:
- Premium features
- Content behind wall
- Usage limits exceeded

```swift
PaywallView(displayCloseButton: false)
```

### Hybrid (Freemium)
Free tier with paid upgrades:
- Free: 5 items
- Premium: Unlimited
- Show upgrade inline, not blocking

## Copy That Converts

### Headlines
```
✅ "Unlock your full potential"     ← Aspirational
✅ "Never lose a workout again"     ← Problem-solving
✅ "Join 1M+ members"               ← Social proof

❌ "Subscribe to Premium"           ← Boring
❌ "Pay for more features"          ← Transactional
```

### Feature Lists
Benefits over features:
```
✅ "Save 10 hours per week"         ← Outcome
❌ "Unlimited exports"              ← Feature

✅ "Access anywhere, anytime"       ← Freedom
❌ "Cloud sync enabled"             ← Technical
```

### CTA Buttons
```
✅ "Start Free Trial"
✅ "Try Premium Free"
✅ "Continue" (if trial is default)

❌ "Subscribe"
❌ "Buy Now"
❌ "Pay $4.99"
```

## A/B Testing

Test these elements (in order of impact):
1. **Price points** - $4.99 vs $5.99 vs $3.99
2. **Trial length** - 3 days vs 7 days vs 14 days
3. **Number of options** - 2 vs 3 packages
4. **Headline copy** - Benefit vs feature-focused
5. **CTA copy** - "Start Free" vs "Try Premium"
6. **Layout** - Features above/below pricing
7. **Social proof** - With/without testimonials

### RevenueCat Experiments
```swift
// Set up in dashboard, SDK handles rest
let offerings = try await Purchases.shared.offerings()
// Returns experiment variant automatically
```

### Adapty A/B
```swift
// Visual paywall builder with built-in A/B
let paywall = try await Adapty.getPaywall(placementId: "onboarding")
// paywall.variationId tells you which variant
```

## Platform-Specific Guidelines

### iOS
- Must have restore button
- Can't mention competing platforms
- Price must be clear before purchase
- Terms/Privacy links required
- No "free" if it auto-renews

### Android
- Must show subscription terms
- Cancellation info required
- Play Store handles price display
- Grace period handling expected

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Showing paywall too early | Wait until user sees value |
| Price as main focus | Lead with benefits |
| Single price option | Use 3-tier anchoring |
| Boring CTA | Action-oriented copy |
| No trial | Always offer trial |
| Hidden restore | Prominent restore button |
| Wall of text | Scannable bullet points |
| No social proof | Add ratings, testimonials |
| Same paywall everywhere | Context-aware paywalls |
| Not testing | A/B test continuously |

## Paywall Triggers

When to show:
```
GOOD TRIGGERS:
- After onboarding completion
- After first value moment
- When hitting free limit
- When requesting premium feature
- After X days of use

BAD TRIGGERS:
- Immediately on first open
- Mid-task interruption
- Multiple times per session
- Before user sees any value
```

## Metrics to Track

| Metric | Formula | Target |
|--------|---------|--------|
| Paywall view rate | Views / DAU | >20% |
| Trial start rate | Trials / Views | >30% |
| Trial conversion | Paid / Trials | >50% |
| Overall conversion | Paid / Views | >5% |

## Code: Custom Paywall (SwiftUI)

```swift
struct PaywallView: View {
    @State private var packages: [Package] = []
    @State private var selectedPackage: Package?
    
    var body: some View {
        VStack(spacing: 20) {
            // Headline
            Text("Unlock Premium")
                .font(.largeTitle.bold())
            
            // Features
            FeatureList()
            
            // Packages
            ForEach(packages, id: \.identifier) { package in
                PackageButton(
                    package: package,
                    isSelected: selectedPackage?.identifier == package.identifier
                ) {
                    selectedPackage = package
                }
            }
            
            // CTA
            Button("Start Free Trial") {
                purchase(selectedPackage)
            }
            .buttonStyle(.prominent)
            
            // Footer
            HStack {
                Button("Restore") { restore() }
                Link("Terms", destination: termsURL)
                Link("Privacy", destination: privacyURL)
            }
            .font(.caption)
        }
        .task {
            packages = await loadPackages()
            selectedPackage = packages.first { $0.identifier == "annual" }
        }
    }
}
```
