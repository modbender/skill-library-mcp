# Mobile App Paywalls

## iOS vs Android Differences

| Aspect | iOS | Android |
|--------|-----|---------|
| Pricing flexibility | Limited (manual per-country) | Better (bulk updates) |
| Introductory offers | One active at a time | More flexible |
| Review process | Strict, watches for dark patterns | Faster, less strict |
| User spending | Higher average | Lower, more price sensitive |
| Trial management | Store-managed | Store-managed |

## iOS-Specific Rules

### App Store Guidelines
- No fake urgency ("Offer expires in 5 minutes" with fake timer)
- Clear pricing before purchase
- Easy cancellation path
- No hiding subscription terms
- Restore purchases button required

### Introductory Offers
Only ONE can be active per subscription group:
- Free trial (7 days, 14 days, 1 month common)
- Pay-up-front discount
- Pay-as-you-go discount

**Can't combine:** Free trial AND discount simultaneously on iOS.

### Pricing Tools
- App Store Connect is tedious for multi-country pricing
- Use Pricetag or similar API tools for bulk management
- Test prices in smaller markets first

---

## Android-Specific Rules

### Play Store Advantages
- Bulk pricing updates across countries
- More flexible offer combinations
- Faster review process
- Better promotional code system

### Play Store Constraints
- Pattern Day Trading-style rules coming
- Increasing transparency requirements
- Must show price before any interaction

---

## Native vs Web-Based Paywalls

| Native | Web-Based (WebView) |
|--------|---------------------|
| Faster loading | Slower initial load |
| Platform-specific UI | Cross-platform consistent |
| Harder to update | Update without app release |
| Better UX | Can feel less native |

**Recommendation:** Use native for production, web-based for rapid A/B testing.

### Third-Party Tools
- **RevenueCat** — Native paywalls, strong analytics
- **Superwall** — Web-based, fast iteration
- **Purchasely** — Native, no-code builder
- **Adapty** — Native + A/B testing

---

## Mobile Paywall Patterns

### Full-Screen Takeover
Most common. Blocks content until dismissed or purchased.
- Use during onboarding
- Ensure clear dismiss option (Apple requires this)

### Bottom Sheet
Slides up from bottom. Less aggressive.
- Good for contextual triggers
- Feels less intrusive

### Card Modal
Centered card with slight background dim.
- Premium feel
- Good for limited-time offers

### Inline Upgrade
Embedded in content feed or feature list.
- Non-blocking
- Good for "upgrade to unlock" features

---

## Mobile-Specific UI Elements

### Product Badges
Guide users to preferred plan:
- "Best Value" on annual
- "Most Popular" (social proof)
- "Save X%" with calculation

### Plan Cards
Horizontal layout common on mobile:
```
[Weekly] [Monthly ★] [Yearly]
  $9.99    $4.99/mo    $29.99
           BEST VALUE
```

### Benefit Carousels
Swipeable cards showing features:
- 3-5 slides max
- Include screenshots or illustrations
- Auto-advance optional (test it)

### Social Proof
- App Store rating badge
- User count ("Join 2M+ users")
- Testimonial cards (real names, photos)

---

## Restore Purchases

**Required on iOS.** Users who reinstall need to restore.

Placement options:
- Small link at bottom of paywall
- Settings screen
- Both (recommended)

Text: "Restore Purchases" or "Already subscribed?"

---

## Trial Best Practices

### Trial Length
| App Type | Recommended |
|----------|-------------|
| Utility/Productivity | 7 days |
| Content/Media | 7-14 days |
| Fitness/Health | 14 days |
| Education | 7 days |

### Trial Conversion Tactics
- Remind users before trial ends (push/email)
- Show value during trial ("You've used X 15 times")
- Extend trial for engaged non-converters

### No Trial Alternative
Some apps skip trials entirely:
- Lower CAC (no trial-hoppers)
- Attracts committed users
- Test both approaches
