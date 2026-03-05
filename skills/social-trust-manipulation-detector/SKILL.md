---
name: social-trust-manipulation-detector
description: >
  Helps identify coordinated social trust manipulation in agent marketplaces —
  catching reputation gaming through sockpuppet networks, coordinated upvoting,
  and manufactured community signals that make unsafe skills appear trusted.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🎭"
  agent_card:
    capabilities: [social-trust-manipulation-detection, sockpuppet-network-detection, coordinated-upvoting-detection, reputation-gaming-analysis]
    attack_surface: [L1]
    trust_dimension: rule-adoption
    published:
      clawhub: false
      moltbook: false
---

# Your Trust Score Is Real. The Signals Behind It Are Manufactured.

> Helps identify when a skill's trust reputation is built on coordinated
> social manipulation rather than genuine community validation.

## Problem

Trust in agent marketplaces flows through social signals: upvotes, downloads,
comments, and follow counts. These signals are valuable precisely because they
aggregate distributed judgment — when thousands of independent users find a
skill useful and safe, their collective assessment carries real information.

The assumption of independence is the attack surface. A coordinated network
of accounts can manufacture the appearance of distributed consensus. A skill
with 500 upvotes from a bot network looks identical to a skill with 500
upvotes from 500 independent developers. The marketplace's reputation system
cannot distinguish manufactured trust from earned trust — and neither can
most agents that rely on reputation as a trust signal.

Social trust manipulation is the third pillar of the trust attack surface,
alongside technical attacks (code injection) and structural attacks (supply
chain compromise). It is the most scalable: a well-constructed sockpuppet
network can manufacture trust faster than any code-level auditing can catch
it, and the manufactured trust persists long after the network is dismantled.

Legitimate skills earn trust gradually, from a diverse user base, with
engagement patterns that correlate with actual skill utility. Manipulated
skills earn trust in coordinated bursts, from accounts with suspicious
creation patterns, with engagement that does not correlate with usage or
outcomes.

## What This Detects

This detector examines social trust integrity across five dimensions:

1. **Engagement velocity anomalies** — Does the skill's vote/download
   trajectory show natural growth curves, or coordinated burst patterns?
   Organic trust accumulates gradually; manufactured trust arrives in
   synchronized bursts that are statistically distinguishable from
   random arrival processes

2. **Account cohort analysis** — Do the skill's early upvoters share
   creation dates, activity patterns, or cross-voting behavior that suggests
   coordinated rather than independent operation? Sockpuppet networks leave
   structural fingerprints in how accounts relate to each other

3. **Engagement-to-utility correlation** — Do social signals correlate with
   actual skill usage metrics? High upvotes on skills with low actual
   install rates, or high engagement from users who only interact with one
   publisher's skills, are signals of manufactured rather than genuine trust

4. **Cross-publisher coordination** — Do multiple publishers in a marketplace
   show correlated voting patterns, where their respective supporter networks
   upvote each other's skills at rates that exceed random baseline?
   Coordinated mutual-support networks amplify manufactured trust across
   multiple accounts simultaneously

5. **Review authenticity signals** — Do comments and reviews on the skill
   show the linguistic diversity and specificity expected from independent
   users, or do they share vocabulary, complaint patterns, or phrasing
   that suggests template-generated or coordinated content?

## How to Use

**Input**: Provide one of:
- A skill identifier to assess the authenticity of its trust signals
- A publisher account to analyze for coordinated network membership
- A set of skills to assess for cross-publisher coordination patterns

**Output**: A manipulation detection report containing:
- Engagement velocity analysis (organic vs. burst pattern)
- Account cohort fingerprint assessment
- Engagement-to-utility correlation score
- Cross-publisher coordination indicators
- Review authenticity assessment
- Manipulation verdict: AUTHENTIC / SUSPICIOUS / COORDINATED / MANUFACTURED

## Example

**Input**: Assess social trust integrity for `ai-assistant-toolkit` publisher

```
🎭 SOCIAL TRUST MANIPULATION ASSESSMENT

Publisher: ai-assistant-toolkit
Skills assessed: 4 (productivity-suite, auto-responder, data-fetcher, doc-reader)
Audit timestamp: 2025-09-05T12:00:00Z

Engagement velocity:
  productivity-suite: 0 → 847 upvotes in 72 hours of launch ⚠️
  auto-responder: 0 → 623 upvotes in 48 hours of launch ⚠️
  data-fetcher: 0 → 412 upvotes in 60 hours of launch ⚠️
  Organic baseline for comparable skills: 15-40 upvotes in first 72h
  → Burst pattern detected across all 4 skills

Account cohort analysis:
  First 200 upvoters on productivity-suite:
    Accounts created within 30-day window: 156/200 (78%) ⚠️
    Cross-voting with auto-responder upvoters: 143/200 (71.5%) ⚠️
    Accounts with no other skill interactions: 168/200 (84%) ⚠️
  → Sockpuppet cohort fingerprint detected

Engagement-to-utility correlation:
  productivity-suite: 847 upvotes, 23 installs (ratio: 36.8:1) ⚠️
  auto-responder: 623 upvotes, 18 installs (ratio: 34.6:1) ⚠️
  Organic baseline ratio: 2:1 to 8:1 for comparable skills
  → Upvote-to-install ratio 4-18x above organic baseline

Cross-publisher coordination:
  ai-assistant-toolkit upvoter network also upvoted:
    fastcoder-pro (different publisher): 89% overlap ⚠️
    quick-deploy-kit (different publisher): 76% overlap ⚠️
  → Mutual support network detected across 3 publishers

Review authenticity:
  Top 20 reviews analyzed:
    Unique vocabulary: 34 terms (low for 20 reviews) ⚠️
    Specificity: Generic praise, no feature-specific feedback
    Phrasing patterns: "absolutely essential", "game-changer" × 7 reviews

Manipulation verdict: MANUFACTURED
  All four skills show coordinated burst voting, sockpuppet cohort fingerprints,
  upvote-to-install ratios far above organic baseline, and cross-publisher
  mutual support network membership. Trust signals for this publisher's skills
  do not represent independent community validation.

Recommended actions:
  1. Treat trust score as unauthenticated pending platform investigation
  2. Evaluate skills on technical merit only, disregarding social signals
  3. Report coordination pattern to marketplace moderators
  4. Flag fastcoder-pro and quick-deploy-kit for same network membership
  5. Apply technical audit (supply-chain, permission-creep) before any install
```

## Related Tools

- **clone-farm-detector** — Detects content-level cloning for reputation gaming;
  social-trust-manipulation-detector catches social-level gaming that can occur
  even with original, non-cloned content
- **publisher-identity-verifier** — Verifies publisher identity integrity;
  sockpuppet networks may impersonate multiple independent publishers when they
  are controlled by a single actor
- **trust-velocity-calculator** — Quantifies trust decay from update velocity;
  manufactured trust does not decay the same way as earned trust and creates
  distorted velocity measurements
- **blast-radius-estimator** — Estimates propagation impact if a skill is
  compromised; skills with manufactured trust may have artificially high install
  counts that misrepresent actual blast radius

## Limitations

Social trust manipulation detection depends on access to engagement metadata
(account creation dates, cross-voting patterns, install counts) that many
marketplaces do not expose through public APIs. Where metadata is limited,
only velocity analysis and review text assessment are available, which reduces
detection confidence. Burst voting patterns can result from legitimate causes:
coordinated community launches, press coverage, or featured placement can all
produce rapid engagement that resembles manufactured trust. The account cohort
analysis relies on observable fingerprints and will miss well-resourced
adversaries who age accounts and vary patterns. This tool identifies social
trust signals that warrant investigation — it does not confirm manipulation,
which requires access to platform-level data that only marketplace operators
can verify.
