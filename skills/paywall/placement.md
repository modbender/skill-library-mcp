# Paywall Placement Strategy

## The Four Placement Types

### 1. Onboarding Paywall

**When:** After install, during initial setup flow
**Why it works:** Motivation is highest right after download

```
Install → Onboarding slides → Paywall → App
```

**Conversion share:** 40-60% of all trial starts
**Best practices:**
- Show after 2-3 value-demonstrating screens
- Offer free trial (removes friction)
- Include skip/dismiss option (required by app stores)

**Timing variants to test:**
- Before any app usage (aggressive)
- After completing profile/setup
- After first value moment (e.g., first photo edited)

---

### 2. Contextual Paywall

**When:** User attempts to use a premium feature
**Why it works:** User demonstrated intent

**Trigger examples:**
- Export in high resolution
- Use premium filter/effect
- Access gated content
- Exceed free tier limits

**Best practices:**
- Explain what they're trying to access
- Show preview of premium result if possible
- Offer alternative (watch ad, invite friend)

**Conversion share:** 20-30%

---

### 3. Persistent Upgrade Button

**When:** Always visible in UI
**Why it works:** Ready-to-convert users have a path

**Placement options:**
- Profile/settings screen
- Navigation menu
- Feature toolbar
- Dashboard header

**Best practices:**
- Subtle but findable
- Use "Pro" badge or crown icon
- Don't clutter core experience

**Conversion share:** 10-20%

**Case study:** Adding an upgrade button increased revenue 10-20% at Avast.

---

### 4. Campaign Paywall

**When:** Triggered by marketing campaigns or events
**Why it works:** Creates urgency and reaches lapsed users

**Trigger mechanisms:**
- Push notification
- Email deeplink
- In-app event (app open after X days)
- Special occasion (Black Friday)

**Best practices:**
- Time-limited offers create urgency
- Personalize based on user segment
- Don't over-trigger (fatigue)

**Conversion share:** 5-15%

**Tools:** Superwall, OneSignal, Braze

---

## Placement Decision Matrix

| User State | Best Placement |
|------------|----------------|
| Just installed | Onboarding paywall |
| Engaged free user | Contextual trigger |
| Hit feature limit | Contextual paywall |
| Lapsed user (7+ days) | Campaign paywall |
| Active but free | Upgrade button + campaign |

---

## Timing Optimization

### Onboarding Timing Tests

| Timing | Pros | Cons |
|--------|------|------|
| Before app use | Highest reach | No value shown yet |
| After profile setup | Invested user | May feel early |
| After first action | Value demonstrated | Lower reach |
| After 3 actions | Strong engagement signal | Much lower reach |

**Recommendation:** Test timing. For most apps, "after 2-3 onboarding screens" wins.

---

### Contextual Trigger Timing

**Show paywall when:**
- Feature is attempted (not on feature discovery)
- Limit is hit (not approaching)
- Value is clear (they know what they're missing)

**Don't show when:**
- User is mid-task (frustrating)
- User just dismissed a paywall (<24h)
- User is in first session (unless onboarding)

---

### Campaign Trigger Rules

**Good triggers:**
- App open after 3+ days inactive
- Specific achievement unlocked
- Content consumed milestone
- End of content/level

**Bad triggers:**
- Every app open (fatigue)
- Mid-content consumption
- During user's first week

---

## Frequency Capping

Never show paywall more than:
- 1x per session (unless different trigger)
- 1x per 24h (campaign paywalls)
- 3x per week total

**Store respect:** App stores watch for aggressive paywalls. Keep dismiss option clear.

---

## Soft vs Hard Paywalls

### Hard Paywall
- Blocks all access until purchase/trial
- Higher conversion per impression
- Lower free user retention
- Common in: Newspapers, premium content apps

### Soft Paywall
- Limits access (X free articles, Y free exports)
- Builds engagement first
- Higher reach, lower conversion rate
- Common in: Productivity, utilities, freemium games

### Metered Paywall
- X free uses per day/week/month
- User decides when to convert
- Good for showing value repeatedly
- Common in: News, AI tools, creative apps

---

## A/B Testing Placement

Test these placement variations:
1. **Onboarding position:** Slide 3 vs slide 5 vs post-setup
2. **Contextual trigger:** Feature attempt vs limit reached
3. **Campaign timing:** App open vs achievement vs day 7
4. **Frequency:** 1x/day vs 1x/3 days vs 1x/week
