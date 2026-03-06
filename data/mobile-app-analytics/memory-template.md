# Memory Template — Mobile App Analytics

Create `~/mobile-app-analytics/memory.md` with this structure:

```markdown
# Mobile App Analytics Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Apps Tracked
<!-- List each app you're helping analyze -->
<!-- app: AppName | platforms: iOS, Android | stack: Firebase, Mixpanel -->

## Current Focus
<!-- What metrics or goals are they working on right now -->

## Alert Preferences
<!-- What anomalies should trigger proactive alerts -->
<!-- e.g., D1 retention < 30%, crash rate > 1% -->

## Notes
<!-- Observations, patterns noticed, things to remember -->

---
*Updated: YYYY-MM-DD*
```

## Per-App Template

Create `~/mobile-app-analytics/apps/{app-name}.md` for each app:

```markdown
# {App Name} Analytics

## Overview
platforms: iOS | Android | both
store_ids: 
  ios: 123456789
  android: com.company.app
analytics_stack: Firebase, Mixpanel, Amplitude

## Key Events
<!-- Custom events being tracked -->
| Event | Description | Params |
|-------|-------------|--------|
| complete_onboarding | User finishes onboarding | step_count |
| start_subscription | User begins sub flow | plan_type |
| complete_purchase | Successful purchase | revenue, plan |

## Funnel Stages
<!-- Main conversion funnel -->
1. Install
2. Registration
3. Onboarding complete
4. First value moment
5. Subscription start
6. Paid conversion

## Target KPIs
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| D1 retention | 35% | 40% | 🟡 |
| D7 retention | 18% | 25% | 🔴 |
| Trial-to-paid | 8% | 12% | 🟡 |

## Recent Insights
<!-- Notable findings, trends, experiments -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their stack | Gather context opportunistically |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Key Principles

- **No config keys visible** — use natural language, not technical jargon
- **Learn from behavior** — notice what metrics they ask about most
- **Store IDs are optional** — don't push for them, add when naturally shared
- Update `last` on each use
