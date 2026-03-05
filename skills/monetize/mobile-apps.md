# Mobile Apps: Real Monetization

## Choose Your Model

| Model | Best For | Reality Check |
|-------|----------|---------------|
| Subscription | Recurring value, habit apps | 2-5% free→paid conversion typical |
| IAP consumables | Games, AI credits | High volume needed |
| IAP unlock | One-time features | Declining, but works for pro tools |
| Paid upfront | Strong brand, niche pro | Hard to compete with free |
| Ads | Millions of users, low engagement | $0.50-10 CPM, often disappointing |

**Default to subscription** if your app provides ongoing value. But know: the "78% of App Store revenue is subscriptions" stat includes Netflix and Spotify. Indie reality is harder.

## Pricing That Makes $10K/month

The math most people get wrong:

| Price | Apple Cut | You Get | Users Needed for $10K/mo |
|-------|-----------|---------|--------------------------|
| $2.99/mo | 15% | $2.54 | 3,937 active subs |
| $4.99/mo | 15% | $4.24 | 2,358 active subs |
| $9.99/mo | 15% | $8.49 | 1,178 active subs |
| $6.99/week | 15% | $5.94 | ~420 active subs* |

*Weekly has higher churn but much higher ARPU. The "secret" of top-grossing apps.

## Weekly Pricing (The Uncomfortable Truth)

Top indie apps often use weekly:
- Impulse purchase (feels small)
- Filters to high-intent users
- Higher churn but 3-4x ARPU

**Structure that works:**
- $6.99/week (impulse buyers, ~40% of revenue)
- $9.99/month (comparison anchor)
- $59.99/year (best value, ~50% of revenue)
- $149.99 lifetime (whales, ~10% of revenue)

## Paywall Placement

| When | Conversion Rate |
|------|-----------------|
| First screen | 1-2% (too aggressive) |
| After value demo (3-5 screens) | 4-6% |
| When limit hit ("3/3 uses today") | 6-10% |

**Rule**: Show paywall AFTER the user experiences value. Not before.

## Paywall That Converts

Structure:
1. **Benefit headline** — "Unlock unlimited [thing]" not "Go Premium"
2. **3-4 outcomes** — What they GET, not feature list
3. **Social proof** — "Join 50,000+ users"
4. **Price** — Highlight annual, show per-day ("$0.27/day")
5. **CTA** — "Start Free Trial" not "Subscribe"
6. **Skip option** — Visible but subtle

Copy that works:
- ✗ "Upgrade to Premium"
- ✓ "Never miss a workout again"
- ✓ "Edit photos like a pro"

## Introductory Offers (Critical)

Set up in App Store Connect → Subscriptions → Intro Offers

| Offer Type | Best For |
|------------|----------|
| Free trial (3-7 days) | Complex apps needing time to show value |
| Pay up front ($0.99 first week) | Simple apps, filters tire-kickers |

**Optimal setup:**
- Weekly: 3 days free OR $0.99 first week
- Monthly: 7 days free OR $1.99 first month
- Annual: 7 days free OR $9.99 first year

## RevenueCat Setup (Correct)

```dart
// pubspec.yaml: purchases_flutter: ^6.0.0

// Initialize
await Purchases.configure(
  PurchasesConfiguration('appl_your_key')
);

// Get offerings for paywall
final offerings = await Purchases.getOfferings();
if (offerings.current != null) {
  // Show paywall with offerings.current.availablePackages
}

// Make purchase
try {
  await Purchases.purchasePackage(package);
} on PurchasesErrorCode catch (e) {
  // Handle: userCancelled, paymentPending, etc.
}

// Check access anywhere
final info = await Purchases.getCustomerInfo();
bool isPro = info.entitlements.all['premium']?.isActive ?? false;
```

## A/B Testing

| Test | Impact | Min Sample |
|------|--------|------------|
| Paywall timing | ±50% revenue | 1,000/variant |
| Trial length | ±30% conversion | 1,000/variant |
| Price point | ±40% revenue | 2,000/variant |
| CTA copy | ±15% | 500/variant |

**Don't bother**: Button colors, icon changes.

## Platform Differences

| | iOS | Android |
|---|-----|---------|
| Commission | 15% (<$1M), 30% | 15% (first $1M), 30% |
| Trial | 3-30 days | Min 3 days |
| Grace period | 16 days | 30 days |
| Refunds | Apple decides | User gets 48h |

**Action**: Set maximum grace period on both. Free retention.
