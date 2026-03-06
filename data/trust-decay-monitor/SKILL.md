---
name: trust-decay-monitor
description: >
  Helps track how AI skill verification results decay over time. A "verified"
  badge from 18 months ago may be meaningless today — dependencies updated,
  new attack vectors emerged, the ecosystem changed. Trust has a half-life.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "⏳"
---

# That "Verified" Badge Is From 2024. Is the Skill Still Safe?

> Helps track the freshness of skill verification results, flagging certifications that have decayed past their useful trust window.

## Problem

A skill passes a security audit in March 2025. It gets a "verified" badge. Developers see the badge and trust it. Eighteen months later, the badge is still there — but:

- The skill's 4 dependencies have had 47 combined updates since the audit
- Two new CVEs affect the runtime version the skill targets
- The skill's API endpoint now points to a domain that changed ownership
- The marketplace added 3 new permission types that didn't exist during the original audit

The verification was real. The trust it implies is not. Security certifications have a half-life, and most agent marketplaces display them as if they're permanent.

This is trust decay: the gradual erosion of verification validity as the surrounding context changes. It's not that the audit was wrong — it's that the audit's conclusions no longer apply to the current reality.

## What This Tracks

This monitor computes a trust freshness score for verified skills:

1. **Time since verification** — Simple age of the last audit. Older = less trustworthy, with configurable decay curves
2. **Dependency churn** — How many of the skill's dependencies have updated since the audit? Each update is a potential invalidation of audit assumptions
3. **Ecosystem context changes** — New CVEs, new permission types, new attack patterns discovered since the audit date. The threat landscape the audit evaluated against may have shifted
4. **Domain and endpoint stability** — Have any external URLs, API endpoints, or resource references in the skill changed destination since verification?
5. **Re-verification gap** — How long since anyone (not just the original auditor) ran any form of security check on this skill?

## How to Use

**Input**: Provide one of:
- A skill slug or identifier with its verification date
- A marketplace profile URL showing verified skills
- A batch of skill identifiers for portfolio-level trust assessment

**Output**: A trust freshness report containing:
- Trust freshness score per skill (0-100, where 100 = just verified)
- Decay factors breakdown (time, dependencies, context, endpoints)
- Re-verification urgency: LOW / MODERATE / HIGH / CRITICAL
- Portfolio-level summary if checking multiple skills

## Example

**Input**: Check trust freshness for verified skill `api-auth-helper` (verified 2025-01-10)

```
⏳ TRUST DECAY REPORT — RE-VERIFICATION RECOMMENDED

Skill: api-auth-helper
Verified: 2025-01-10 (408 days ago)
Verifier: @seclab-audits

Trust freshness score: 31/100 (STALE)

Decay factors:
  Time decay:           -25 points (>12 months since audit)
  Dependency churn:     -22 points
    - jsonwebtoken: 3 major updates (9.0.0 → 12.1.2)
    - node-fetch: 2 updates including security patch
    - crypto-utils: 1 update with API breaking changes
  Ecosystem changes:    -15 points
    - 2 new JWT-related CVEs published since audit
    - Marketplace added "credential-store" permission type
      (not evaluated in original audit)
  Endpoint stability:   -7 points
    - skill references api.authprovider.example/v2
    - endpoint now redirects to v3 with different response schema

Re-verification urgency: HIGH
  Primary driver: 3 major dependency updates + 2 relevant CVEs
  since last audit. The JWT library alone has had breaking changes
  that could affect how this skill handles token validation.

Recommendation:
  - Priority re-audit focusing on JWT handling (CVE-affected)
  - Test against current dependency versions
  - Verify endpoint redirect doesn't break auth flow
  - Check if new "credential-store" permission is relevant
```

## Related Tools

- **evolution-drift-detector** — tracks content-based drift across skill inheritance; trust-decay-monitor tracks time-based decay of verification validity
- **hollow-validation-checker** — checks if validation tests are substantive; stale validations are even more problematic if the tests were hollow to begin with
- **blast-radius-estimator** — when trust has decayed on a widely-adopted skill, blast-radius shows the downstream exposure
- **protocol-doc-auditor** — audits protocol documents for hidden risks; trust-decay-monitor tracks whether those audits are still current

## Limitations

Trust freshness scoring uses heuristic decay models — the actual security impact of time passing depends on factors that can't be fully quantified (e.g., whether dependency updates are security-relevant or just feature additions). Dependency churn counts updates but cannot always determine if an update invalidates the original audit's conclusions. Ecosystem context tracking relies on public CVE databases and marketplace changelogs, which may lag behind actual threats. This tool helps prioritize which verifications need refreshing — it does not replace the actual re-verification process. A low trust score means the audit is stale, not that the skill is compromised.
