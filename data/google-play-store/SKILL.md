---
name: Google Play Store
slug: google-play-store
version: 1.0.0
homepage: https://clawic.com/skills/google-play-store
description: Publish, optimize, and scale Android apps on Google Play with release automation, ASO, policy compliance, and rejection recovery.
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs to publish, manage, or optimize Android apps on Google Play. Agent handles release workflows, store optimization, policy compliance, review processes, and rejection troubleshooting.

## Architecture

Memory lives in `~/google-play-store/`. See `memory-template.md` for structure.

```
~/google-play-store/
├── memory.md         # Account, apps, preferences
├── apps/             # Per-app tracking
│   └── {package}/    # Package-specific notes
└── checklists/       # Saved submission checklists
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Release tracks and rollouts | `tracks.md` |
| App Store Optimization | `aso.md` |
| Policy compliance | `policies.md` |
| Rejection recovery | `rejections.md` |
| Automation with Fastlane | `fastlane.md` |

## Core Rules

### 1. Release Track Progression

| Track | Purpose | Review | Users |
|-------|---------|--------|-------|
| Internal | Daily builds, QA | None | 100 max |
| Closed | Beta testers | 2-6h | Email list |
| Open | Public beta | 2-6h | Anyone joins |
| Production | Full release | 2-24h | Everyone |

**Mandatory progression for new apps:**
```
Internal → Closed (20+ testers, 14+ days) → Production
```

Skip this = instant rejection. Start closed testing on day one.

### 2. Pre-Submission Checklist

Run before EVERY submission:

```
CONTENT
[ ] Privacy policy URL live and HTTPS
[ ] Data safety form 100% complete
[ ] Content rating questionnaire done
[ ] All screenshots show real app (no placeholders)
[ ] Feature graphic 1024x500 uploaded

TECHNICAL
[ ] Target SDK ≥ 34 (Android 14)
[ ] versionCode higher than ALL previous uploads
[ ] Signed with correct key
[ ] No hardcoded API keys in code
[ ] ProGuard/R8 not breaking functionality

TESTING (new apps only)
[ ] 20+ testers opted in (not just invited)
[ ] 14+ consecutive days completed
[ ] Crash-free rate > 99%
```

### 3. Version Code Strategy

```
versionCode must ALWAYS increase. Cannot reuse. Ever.

Pattern: YYYYMMDDHH
Example: 2025022514 (Feb 25, 2025, 2pm)

Why: Rejected uploads "burn" the versionCode.
     Multiple builds per day need unique codes.
```

### 4. App Signing Models

| Model | Control | Recovery | Best For |
|-------|---------|----------|----------|
| Google-managed | Google holds key | Easy | New apps |
| Upload key | You sign, Google re-signs | Medium | Most apps |
| Self-managed | Full control | Hard | Enterprise |

**Recommendation:** Google-managed for new apps. Upload key for updates.

**Critical:** Export and backup your upload key immediately after creating it.

### 5. Staged Rollout Protocol

| Stage | % | Duration | Gate |
|-------|---|----------|------|
| Canary | 1% | 24-48h | Crashes < 0.1% |
| Early | 5% | 48-72h | ANRs < 0.5% |
| Mid | 20% | 72-96h | Ratings stable |
| Late | 50% | 96-120h | No regressions |
| Full | 100% | — | All clear |

**Halt triggers:** Crash spike, ANR spike, 1-star surge, critical bug reports.

### 6. ASO Essentials

| Element | Limit | Impact |
|---------|-------|--------|
| Title | 30 chars | Highest |
| Short description | 80 chars | High |
| Full description | 4000 chars | Medium |
| Screenshots | 8 per type | High |
| Feature graphic | 1024x500 | Medium |

**Keyword strategy:**
- Title: Primary keyword + brand
- Short desc: Top 3 keywords naturally
- Full desc: Long-tail throughout
- Update quarterly based on Search Console

### 7. Response Time SLAs

| Action | Google Response | Your Deadline |
|--------|-----------------|---------------|
| Policy email | 7 days to fix | Respond in 3 |
| Appeal | 3-7 days | Submit in 24h |
| Data request | 30 days | Complete in 14 |
| Critical issue | 24h suspension | Immediate |

**Rule:** Never ignore policy emails. Silence = admission.

## Common Traps

### Publishing Traps
- **Skipped closed testing** → Cannot release to production. 20 testers + 14 days mandatory for new apps.
- **Data safety incomplete** → Instant rejection. Fill EVERY field even if "no data collected."
- **Screenshots with mockups** → Rejection for misleading. Use real app screenshots only.
- **Privacy policy 404** → Rejection. Verify URL works before every submission.

### Technical Traps
- **versionCode not incremented** → Upload rejected. Even rejected uploads burn codes.
- **Target SDK too old** → Rejection. Check current requirement before building.
- **Forgot upload key password** → Cannot update app. Store password in password manager.
- **ProGuard broke app** → Crashes after release. Always test release build.

### Policy Traps
- **Undeclared permissions** → Policy violation. Justify EVERY sensitive permission.
- **Background location without need** → Rejection + strike. Remove or justify with video.
- **Kids content undeclared** → Policy violation. If ANY appeal to children, declare it.
- **Deceptive ads** → Suspension risk. Follow interstitial timing and close button rules.

### Business Traps
- **No staged rollout** → Bad update hits everyone. Always start at 1%.
- **Ignored policy email** → Escalation to strike. Respond within 3 days.
- **Multiple accounts to evade** → Termination. One violation becomes account death.

## Security & Privacy

**Data that stays local:**
- Package names and app status in ~/google-play-store/
- Submission checklists and workflow notes
- Release history and lessons learned

**This skill stores ONLY non-sensitive metadata:**
- App names and package identifiers
- Track status (internal/closed/production)
- Workflow preferences (manual vs CI/CD tool names)
- Checklist progress

**This skill does NOT store and will refuse:**
- API keys, service account JSON content
- Keystore files or passwords
- OAuth tokens or Play Console credentials
- Any secret or credential material

**This skill does NOT:**
- Upload apps or make network requests
- Access signing keys or certificates
- Execute Fastlane commands directly

User manages all credentials in their CI/CD system and runs commands themselves. The Fastlane examples are documentation only.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `android` — Android development
- `app-store` — iOS and Android publishing
- `mobile` — Cross-platform mobile

## Feedback

- If useful: `clawhub star google-play-store`
- Stay updated: `clawhub sync`
