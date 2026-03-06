---
name: App Store
description: Publish and manage iOS and Android apps with account setup, submission workflows, review compliance, and rejection handling.
---

## Scope

App Store Connect (iOS) and Google Play Console (Android). Covers the full publishing lifecycle from account creation to updates. For keyword optimization, see `app-store-optimization` skill.

---

## Account Setup

| Platform | Cost | Time | Key Steps |
|----------|------|------|-----------|
| Apple Developer Program | $99/year | 1-7 days | Enroll → D-U-N-S (orgs) → Payment → Agreements |
| Google Play Console | $25 once | Minutes-48h | Register → Identity verification → Payment profile |

**Apple gotchas:**
- D-U-N-S number required for organizations (free, takes 1-2 weeks)
- Legal entity name must match D-U-N-S exactly
- Agreements (Paid Apps, Apple Pay) must be accepted before features work

**Google gotchas:**
- Identity verification can take 48h+ for new accounts
- Closed testing track required before production (20+ testers, 14+ days for new apps since 2023)

---

## iOS Signing (The Hard Part)

| Asset | What It Is | Where Created | Expires |
|-------|------------|---------------|---------|
| Distribution Certificate | Your signing identity | Keychain → App Store Connect | 1 year |
| Provisioning Profile | Links cert + app ID + devices | App Store Connect | 1 year |
| App ID | Unique identifier (bundle ID) | App Store Connect | Never |

**When Xcode says "No signing identity":**
1. Check certificate exists in Keychain Access (login keychain)
2. Check provisioning profile includes that certificate
3. Check bundle ID in Xcode matches App ID exactly
4. Revoke and recreate if nothing else works

**Automatic vs Manual Signing:**
- Automatic: Xcode manages everything (fine for solo devs)
- Manual: Required for CI/CD, teams, or multiple apps
- Never mix — pick one approach per project

---

## Submission Checklist

Pre-submit verification (both platforms):

- [ ] Privacy policy URL live and accessible
- [ ] All required permissions have usage descriptions
- [ ] App works without network (or handles offline gracefully)
- [ ] No placeholder content, "lorem ipsum", or test data
- [ ] Screenshots match actual app UI (no misleading marketing)
- [ ] Contact support email valid and monitored

**iOS-specific:**
- [ ] Export Compliance (ITSAppUsesNonExemptEncryption in Info.plist)
- [ ] App Tracking Transparency if using IDFA
- [ ] Privacy manifest (PrivacyInfo.xcprivacy) for required APIs

**Android-specific:**
- [ ] Target SDK meets current requirement (currently API 34)
- [ ] Data safety form completed
- [ ] Content rating questionnaire filled
- [ ] 20+ testers on closed track for 14+ days (new apps)

---

## Common Rejections

| Code | Meaning | Fix |
|------|---------|-----|
| **4.2** (iOS) | Minimum functionality | Add features, or argue value proposition in appeal |
| **4.3** (iOS) | Spam/duplicate | Differentiate significantly from your other apps |
| **5.1.1** (iOS) | Data collection | Implement App Tracking Transparency, update privacy manifest |
| **2.1** (iOS) | Crashes/bugs | Test on real devices, check Crashlytics |
| Deceptive behavior (Android) | Misleading metadata | Match screenshots to real functionality |
| Broken functionality (Android) | App doesn't work as described | Full QA on production build |

**Appeal strategy:**
1. Read rejection reason carefully (don't assume)
2. If misunderstanding: Explain with screenshots, video if needed
3. If valid: Fix issue, note what changed in resolution notes
4. Never resubmit identical binary hoping for different reviewer

---

## Review Timeline

| Platform | Typical | Expedited | Slower Periods |
|----------|---------|-----------|----------------|
| Apple | 24-48h | Request via App Review form | New iOS launches, holidays |
| Google | 2-6h | N/A | Initial submissions, policy violations |

**Apple expedited review:** Only for critical bugs, time-sensitive events. Overuse = ignored.

---

## Monetization Setup

**In-app purchases (IAP):**
1. Create products in App Store Connect / Play Console
2. Implement StoreKit (iOS) / BillingClient (Android)
3. Set up server-side receipt validation (don't trust client)
4. Handle sandbox vs production environments

**Subscriptions:**
- Configure introductory offers, free trials, grace periods
- Implement subscription lifecycle: renewal, cancellation, billing retry
- Server notifications endpoint for real-time status updates
- Test with sandbox accounts (both platforms have quirks)

**Revenue splits:** Apple/Google take 15-30% (15% for Small Business Program or after year 1 of subscription).

---

## Multi-App Management

**Organization structure:**
- Apple: One enrollment, multiple apps, team roles per app
- Google: One developer account, multiple apps, user permissions

**Team roles (critical):**
- Separate "submit builds" from "release to production"
- Marketing should access metadata only
- Finance sees revenue, not code

**Cross-platform releases:**
- Submit iOS first (longer review)
- Hold Android release until iOS approved
- Use phased rollout to catch issues early

---

## When to Load More

| Situation | Reference |
|-----------|-----------|
| Keyword optimization, A/B testing | `app-store-optimization` skill |
| Generating release notes from git | `app-store-changelog` skill |
| TestFlight/internal testing setup | `testing.md` |
| CI/CD automation (fastlane, APIs) | `automation.md` |
