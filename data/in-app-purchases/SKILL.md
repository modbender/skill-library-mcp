---
name: In-App Purchases
slug: in-app-purchases
version: 1.0.0
description: Implement in-app purchases and subscriptions across iOS, Android, and Flutter with RevenueCat, paywalls, receipt validation, and subscription analytics.
metadata: {"clawdbot":{"emoji":"💳","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to implement in-app purchases, subscriptions, paywalls, or monetization flows. Agent handles native APIs (StoreKit 2, Google Play Billing), cross-platform SDKs (RevenueCat, Adapty, Qonversion), paywall design, server verification, and subscription analytics.

## Quick Reference

| Topic | File |
|-------|------|
| iOS StoreKit 2 | `storekit.md` |
| Android Billing | `google-play.md` |
| Flutter packages | `flutter.md` |
| RevenueCat SDK | `revenuecat.md` |
| Platform comparison | `platforms.md` |
| Server verification | `server.md` |
| Paywall design | `paywalls.md` |
| Subscription metrics | `analytics.md` |
| Testing & sandbox | `testing.md` |

## Core Rules

### 1. Choose Your Architecture
| Approach | When to Use | Tradeoff |
|----------|-------------|----------|
| Native only | Single platform, full control | More code, no cross-platform sync |
| RevenueCat/Adapty | Cross-platform, fast launch | 1-2% fee, dependency |
| Hybrid | Native + own backend | Full control, more work |

### 2. Platform SDKs (Managed)
| Platform | Pricing | Best For |
|----------|---------|----------|
| RevenueCat | Free <$2.5k MTR, then 1% | Most apps, best docs |
| Adapty | Free <$10k MTR, then 0.6% | Cost-conscious, A/B paywalls |
| Qonversion | Free <$10k MTR, then 3% | Simple setup |
| Superwall | Paywall-focused | Paywall A/B only |
| Glassfy | Free <$10k, then 0.5% | Budget option |

### 3. Product Types
| Type | iOS | Android | Use Case |
|------|-----|---------|----------|
| Consumable | ✅ | ✅ | Credits, coins, lives |
| Non-consumable | ✅ | ✅ | Unlock feature forever |
| Auto-renewable | ✅ | ✅ | Subscriptions |
| Non-renewing | ✅ | ❌ | Season pass, time-limited |

### 4. Server Verification is Non-Negotiable
Never trust client-side validation alone:
- iOS: App Store Server API with JWS verification
- Android: Google Play Developer API
- RevenueCat: Webhooks + REST API

### 5. Handle All Transaction States
| State | Action |
|-------|--------|
| Purchased | Verify → grant → finish |
| Pending | Wait, show pending UI |
| Failed | Show error, don't grant |
| Deferred | Wait for parental approval |
| Refunded | Revoke immediately |
| Grace period | Limited access, prompt payment |
| Billing retry | Maintain access during retry |

### 6. Subscription Lifecycle Events
Must handle all of these (native or via webhooks):
- INITIAL_PURCHASE → grant access
- RENEWAL → extend access
- CANCELLATION → mark will-expire
- EXPIRATION → revoke access
- BILLING_ISSUE → prompt to update payment
- GRACE_PERIOD → limited access window
- PRICE_INCREASE → consent required (iOS)
- REFUND → revoke + flag user
- UPGRADE/DOWNGRADE → prorate

### 7. Restore Purchases Always
Required by App Store guidelines:
- Prominent restore button
- Works for logged-out users
- Handles family sharing (iOS)
- Cross-device sync

### 8. Paywall Best Practices
See `paywalls.md` for detailed patterns:
- Show value before price
- Anchor pricing (3 options, highlight middle)
- Free trial prominent
- Social proof if available
- A/B test everything

### 9. Testing Strategy
| Environment | iOS | Android |
|-------------|-----|---------|
| Dev/Debug | StoreKit Config file | License testers |
| Sandbox | Sandbox accounts | Internal testing |
| Production | Real accounts | Production |

Sandbox subscription times:
- 1 week → 3 minutes
- 1 month → 5 minutes
- 1 year → 1 hour

### 10. App Store Guidelines
- No external payment links (anti-steering)
- Must use IAP for digital goods
- Physical goods/services can use Stripe
- Reader apps have exceptions
- 15-30% commission applies

## Common Traps

- Testing with real money → use sandbox/test accounts
- Not finishing transactions → auto-refund (Android 3 days)
- Hardcoding prices → always fetch from store (regional pricing)
- Missing transaction observer → lose purchases made outside app
- No server verification → trivially bypassable
- Ignoring grace period → users churn when they could recover
- Poor paywall UX → kills conversion regardless of price
- Not tracking metrics → can't optimize what you don't measure
- Forgetting restore button → App Store rejection
- Not handling family sharing → confused users
