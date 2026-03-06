---
name: Google Play Store
slug: play-store
version: 1.0.0
description: Publish and optimize Android apps on Google Play with listing optimization, ASO keywords, and policy compliance.
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to prepare, publish, or optimize an Android app for Google Play. Agent handles listing content, screenshots specs, ASO strategy, policy checks, and release planning.

## Quick Reference

| Topic | File |
|-------|------|
| Listing requirements | `listing.md` |
| ASO strategy | `aso.md` |
| Policy compliance | `policies.md` |

## Core Rules

### 1. Listing Content Essentials
| Field | Limits | Tips |
|-------|--------|------|
| Title | 30 chars | Primary keyword + brand |
| Short description | 80 chars | Hook + main value prop |
| Full description | 4000 chars | Keywords natural, features, social proof |
| Screenshots | 2-8 per device | First 2 visible in search, make them count |
| Feature graphic | 1024x500 px | Required, no text smaller than 24pt |

### 2. Screenshot Specifications
| Device | Min dimensions | Aspect ratio |
|--------|----------------|--------------|
| Phone | 320-3840 px | 16:9 or 9:16 |
| Tablet 7" | 320-3840 px | 16:9 |
| Tablet 10" | 1080-7680 px | 16:9 |
| Wear | 384-3840 px | 1:1 |
| TV | 1920x1080 | 16:9 |

Max 8 screenshots per device type. First 2 are hero shots.

### 3. ASO Keyword Strategy
- **Title:** Most weight, 1-2 primary keywords
- **Short description:** Supporting keywords, action-oriented
- **Full description:** Long-tail variations, 3-5 natural mentions
- **Never:** Keyword stuffing, competitor names, misleading claims
- **Track:** Organic installs, search visibility, keyword rankings

### 4. Policy Red Flags
Avoid these or face rejection/removal:
- Misleading functionality claims
- Sexual content or nudity
- Violence beyond ESRB T equivalent
- User data collection without privacy policy
- Deceptive install tactics
- Impersonation of other apps/brands
- Gambling without proper licensing

### 5. Release Strategy
| Release type | When to use |
|--------------|-------------|
| Internal testing | Team only, immediate |
| Closed testing | Invited testers, 12hr review |
| Open testing | Public beta, indexed in store |
| Production | Full release, staged rollout recommended |

**Staged rollout:** Start 5-10%, monitor crashes/ANRs, expand gradually.

### 6. Content Ratings
- Fill IARC questionnaire honestly
- Ratings affect visibility in some regions
- Under-rating = policy violation
- Re-submit if content changes significantly

### 7. Pre-Launch Checklist
Before any release:
- [ ] All store listing fields complete
- [ ] Privacy policy URL valid and accessible
- [ ] Content rating applied
- [ ] Target API level meets current requirements (API 33+)
- [ ] 64-bit support included
- [ ] App bundle format (.aab), not APK
- [ ] Deobfuscation files uploaded

## Common Traps

- **Generic screenshots** → Low conversion. Show actual UI with value props overlaid.
- **Ignoring tablet screenshots** → Missed visibility on tablets and Chromebooks.
- **Keyword in developer name** → Policy violation, can get suspended.
- **Missing privacy policy** → Instant rejection if app requests any permissions.
- **Low target API** → Apps must target API 33+ for new submissions.
- **APK instead of AAB** → Required since 2021, AAB enables dynamic delivery.
- **Ignoring ANR rate** → >0.47% ANR rate triggers bad quality warnings.
- **Changelog copy-paste** → Users notice, hurts trust. Be specific about changes.
