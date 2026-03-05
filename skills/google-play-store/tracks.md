# Release Tracks — Google Play Store

## Track Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│  INTERNAL          100 users max, instant, QA builds       │
├─────────────────────────────────────────────────────────────┤
│  CLOSED            Email list, 2-6h review, beta testers   │
├─────────────────────────────────────────────────────────────┤
│  OPEN              Anyone joins, 2-6h review, public beta  │
├─────────────────────────────────────────────────────────────┤
│  PRODUCTION        Everyone, 2-24h review, full release    │
└─────────────────────────────────────────────────────────────┘
```

## New App Requirements (Critical)

Google enforces before FIRST production release:

| Requirement | Details |
|-------------|---------|
| Closed testers | Minimum 20 must OPT IN (invited ≠ opted in) |
| Testing period | 14 consecutive days of testing activity |
| Data safety | Form must be 100% complete |
| Content rating | Questionnaire completed |

**Check status:** Console → Release → Closed testing → Testers

### Timeline Planning

```
Day 1:   Upload to internal, QA
Day 2:   Fix critical bugs
Day 3:   Upload to closed, invite 25+ testers
Day 4-7: Testers install and use
Day 7:   Check 20+ have opted in
Day 8-16: Continue closed testing
Day 17:  Requirements met, promote to production
Day 18+: Production review (2-24h)
```

**Start closed testing immediately when app is usable.**

## Staged Rollouts

### Production Rollout Stages

| Percentage | Duration | What to Watch |
|------------|----------|---------------|
| 1% | 24-48 hours | Crashes, critical bugs |
| 5% | 48-72 hours | ANRs, performance |
| 20% | 72-96 hours | User feedback, ratings |
| 50% | 96-120 hours | Stability at scale |
| 100% | — | Full release |

### Rollout Controls

**Increase rollout:**
Console → Release → Production → Manage release → Edit rollout percentage

**Halt rollout:**
Console → Release → Production → Halt rollout
- Users who updated keep the update
- New users get previous stable version
- Can resume or upload new release

**Rollback:**
Upload previous version with NEW versionCode, rollout to 100%

### Halt Triggers

Stop rollout immediately if:
- Crash rate > 1% (vs previous version)
- ANR rate > 0.5%
- Sudden spike in 1-star reviews
- Critical functionality broken
- Security vulnerability discovered

## Track-Specific APKs

Different tracks CAN have different APKs:

| Track | Example Config |
|-------|----------------|
| Internal | debuggable, verbose logging, test endpoints |
| Closed | release build, analytics verbose, staging API |
| Production | release build, production API, optimized |

**Requirements:**
- Each APK needs unique versionCode
- Can't promote APK to track with lower versionCode already there
- Production APK should match what was tested

## Country Targeting

### Per-Track Availability

| Track | Typical Countries |
|-------|-------------------|
| Internal | Worldwide (dev team) |
| Closed | Home country + test markets |
| Open | Target launch markets |
| Production | Final market list |

### Staged Geographic Rollout

1. Launch in 1-3 countries first
2. Monitor metrics for 2 weeks
3. Expand to similar markets
4. Go global

**Why:** Catch localization issues, server scaling problems, regional policy issues.

## Track Management Commands

### Using bundletool

```bash
# Build AAB
./gradlew bundleRelease

# Upload to internal track
# (Use Play Console or Fastlane - API requires service account)
```

### Using Fastlane

```bash
# Upload to internal
fastlane supply --aab app.aab --track internal

# Promote internal to beta
fastlane supply --track_promote_to beta --track internal

# Production with staged rollout
fastlane supply --aab app.aab --track production --rollout 0.01
```

## Common Track Mistakes

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Skip closed testing | Cannot promote to production | Start testing day 1 |
| Promote before 14 days | Blocked | Calendar reminder |
| Same APK to multiple tracks | Confusing version state | Unique versionCodes |
| 100% rollout on day 1 | Bad update hits everyone | Always stage |
