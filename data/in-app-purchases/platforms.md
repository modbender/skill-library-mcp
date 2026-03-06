# Platform Comparison — IAP Services

## Overview

| Platform | Pricing | Best For |
|----------|---------|----------|
| RevenueCat | Free <$2.5k MTR, 1% after | Most apps, best ecosystem |
| Adapty | Free <$10k MTR, 0.6% after | A/B paywalls, cost-conscious |
| Qonversion | Free <$10k MTR, 3% after | Simple needs |
| Superwall | Custom pricing | Paywall-only optimization |
| Glassfy | Free <$10k MTR, 0.5% after | Budget apps |
| Native only | Free | Full control, single platform |

MTR = Monthly Tracked Revenue

## RevenueCat

**Pros:**
- Best documentation in the industry
- Largest community, most Stack Overflow answers
- Native paywall UI components
- Experiments (A/B testing)
- Customer Center for subscription management
- Integrations: Amplitude, Mixpanel, Segment, etc.

**Cons:**
- 1% fee adds up at scale ($10k MTR = $100/month)
- Paywall customization limited without custom UI

**Best for:** Most apps. Start here unless you have specific needs.

```swift
// Setup - 3 lines
Purchases.configure(withAPIKey: "appl_xxx")
let offerings = try await Purchases.shared.offerings()
let customerInfo = try await Purchases.shared.purchase(package: package)
```

## Adapty

**Pros:**
- Lower fees (0.6% vs RevenueCat's 1%)
- Powerful paywall builder (visual editor)
- Built-in A/B testing for paywalls
- Remote paywall configuration (no app update needed)
- Higher free tier ($10k vs $2.5k)

**Cons:**
- Smaller community
- Documentation not as polished
- Fewer integrations

**Best for:** Apps focused on paywall optimization, cost-sensitive.

```swift
// Setup
Adapty.activate("public_sdk_key")

// Fetch paywall
let paywall = try await Adapty.getPaywall(placementId: "onboarding")

// Native UI
let config = try await Adapty.getViewConfiguration(forPaywall: paywall)
let paywallController = try AdaptyUI.paywallController(for: paywall, viewConfiguration: config)
present(paywallController, animated: true)
```

## Qonversion

**Pros:**
- Simple API
- Free tier up to $10k MTR
- Automation rules (win-back campaigns)

**Cons:**
- Highest percentage fee (3%)
- Less feature-rich
- Smaller ecosystem

**Best for:** Simple subscription apps that won't scale past $10k MTR.

```swift
// Setup
Qonversion.initWithConfig(.init(projectKey: "xxx", launchMode: .subscriptionManagement))

// Purchase
let permissions = try await Qonversion.shared().purchaseProduct(product)
```

## Superwall

**Pros:**
- Best-in-class paywall builder
- Advanced A/B testing
- Analytics focused on conversion
- Works alongside other SDKs

**Cons:**
- Paywall-only (not full IAP management)
- Need separate receipt validation
- Custom pricing

**Best for:** Apps with existing IAP that want better paywalls.

```swift
// Setup (works with RevenueCat or native)
Superwall.configure(apiKey: "xxx")

// Trigger paywall
Superwall.shared.register(event: "campaign_trigger") {
  // Paywall was shown
}
```

## Glassfy

**Pros:**
- Lowest fees (0.5%)
- Generous free tier
- Server-side subscription management

**Cons:**
- Smallest community
- Fewer features than RevenueCat
- Limited paywall tools

**Best for:** Budget-conscious apps, indie developers.

## Native Only

**Pros:**
- No fees
- Full control
- No vendor lock-in

**Cons:**
- More code to write
- Handle receipt validation yourself
- No cross-platform sync
- Build own analytics

**Best for:** Single platform apps with engineering resources.

## Decision Framework

```
Start here:
│
├─ Do you need cross-platform sync?
│  ├─ YES → RevenueCat or Adapty
│  └─ NO → Native or any
│
├─ Is paywall optimization critical?
│  ├─ YES → Adapty or Superwall
│  └─ NO → RevenueCat
│
├─ Will you exceed $10k MTR?
│  ├─ YES → RevenueCat (better ecosystem at scale)
│  └─ NO → Adapty or Glassfy (lower costs)
│
└─ Do you have engineering resources?
   ├─ YES → Native possible
   └─ NO → RevenueCat (best docs)
```

## Migration Between Platforms

All platforms support import from others:

```
RevenueCat → Export subscriber list
↓
Adapty → Import via CSV or API
```

Key considerations:
- Transaction history transfers
- Entitlement mapping
- User ID linking
- Grace period during transition

## Feature Comparison

| Feature | RevenueCat | Adapty | Qonversion | Superwall |
|---------|------------|--------|------------|-----------|
| iOS SDK | ✅ | ✅ | ✅ | ✅ |
| Android SDK | ✅ | ✅ | ✅ | ✅ |
| Flutter SDK | ✅ | ✅ | ✅ | ✅ |
| React Native | ✅ | ✅ | ✅ | ✅ |
| Web SDK | ✅ | ✅ | ❌ | ❌ |
| Receipt validation | ✅ | ✅ | ✅ | ❌ |
| Webhooks | ✅ | ✅ | ✅ | ✅ |
| REST API | ✅ | ✅ | ✅ | ✅ |
| Native paywalls | ✅ | ✅ | ❌ | ✅ |
| Visual paywall builder | ⚠️ Basic | ✅ | ❌ | ✅ |
| A/B experiments | ✅ | ✅ | ✅ | ✅ |
| Promo codes | ✅ | ✅ | ✅ | ❌ |
| Integrations | 30+ | 15+ | 10+ | 10+ |
| Customer Center | ✅ | ❌ | ❌ | ❌ |

## Pricing Calculator

At different MTR levels:

| MTR | RevenueCat | Adapty | Qonversion | Glassfy |
|-----|------------|--------|------------|---------|
| $5k | Free | Free | Free | Free |
| $10k | $75 | Free | Free | Free |
| $25k | $225 | $90 | $450 | $75 |
| $50k | $475 | $240 | $1,200 | $200 |
| $100k | $975 | $540 | $2,700 | $450 |

*RevenueCat: 1% over $2.5k. Adapty: 0.6% over $10k. Qonversion: 3% over $10k. Glassfy: 0.5% over $10k.*
