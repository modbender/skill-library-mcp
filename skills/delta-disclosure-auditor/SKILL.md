---
name: delta-disclosure-auditor
description: >
  Helps verify that skill updates publish an auditable record of what changed —
  catching the gap between "the registry shows the new version" and "anyone can
  see what the new version changed relative to the old one." v1.1 adds risk-class
  binding, chain-of-custody verification, and update eligibility assessment.
version: 1.1.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "📝"
  agent_card:
    capabilities: [delta-disclosure-auditing, change-record-verification, update-transparency-checking, risk-class-binding, chain-of-custody-verification, update-eligibility-assessment]
    attack_surface: [L1]
    trust_dimension: rule-adoption
    published:
      clawhub: false
      moltbook: false
---

# The Skill Updated. Nobody Published What Changed.

> Helps identify when skill updates lack auditable change records — the
> transparency gap that makes continuous monitoring impossible without
> re-executing the full skill on every version.

## Problem

A skill that re-audits on every update is more trustworthy than one audited
once at install time. But re-auditing requires knowing what changed. If a skill
can update its capability declarations, dependency set, and validation commands
without publishing a machine-readable delta, continuous monitoring reduces to
full re-execution on every version — expensive, often impractical, and
frequently skipped.

The gap is structural. Most current skill registries record that a new version
was published. They do not require publishers to disclose what changed between
versions. An auditor comparing v1.1 to v1.2 must either execute both versions
and compare behavior, or accept the new version at face value. Neither option
supports continuous security monitoring at scale.

Delta disclosure changes this. If every update is required to publish a diff of
what changed — in capability declarations, dependency sets, validation commands,
and behavioral scope — then continuous monitoring becomes tractable. External
auditors can watch for specific types of changes (new outbound endpoints, expanded
file access, dropped validation commands) without re-executing everything. The
monitoring cost scales with what changed, not with the full skill surface.

The absence of delta disclosure is not evidence of malicious intent. It is
evidence that continuous monitoring is harder than it needs to be.

v1.1 adds three dimensions from community feedback. First, risk-class binding:
the same undisclosed change carries different weight depending on the skill's
risk classification. A formatting helper adding a dependency is different from
a credential handler adding one. Disclosure requirements should scale with risk.
Second, chain-of-custody verification: deltas should be cryptographically signed
and hash-chained to prior versions, converting changelogs from suggestions to
commitments. Third, update eligibility: skills without adequate disclosure should
not qualify for auto-update — disclosure becomes a prerequisite for frictionless
updates, not an optional best practice.

## What This Audits

This auditor examines delta disclosure completeness across five dimensions:

1. **Capability declaration delta** — Does each version update publish a diff
   of what capabilities changed? Added capabilities, removed capabilities, and
   scope changes should each be explicitly declared, not inferred by comparison

2. **Dependency delta** — Does each update disclose which dependencies were
   added, removed, or version-bumped? Dependency changes are a primary vector
   for supply chain attacks and should be immediately visible without full
   diff inspection

3. **Validation command delta** — Does each update disclose changes to the
   validation suite? Dropped tests, weakened assertions, and removed coverage
   are security-relevant changes that should require explicit disclosure

4. **Behavioral scope change declaration** — Does each update explicitly
   declare whether its behavioral scope changed? "This update adds a new
   outbound endpoint" is a different security posture from "this update fixes
   a typo" and should be declared, not inferred

5. **Delta completeness verification** — Where deltas are published, are they
   complete and accurate? A delta that omits material changes is equivalent
   to no delta at all — and potentially worse, as it creates false assurance
   that monitoring is occurring

6. **Risk-class binding** (v1.1) — Does the skill's risk classification match
   its actual capability footprint? A skill classified as low-risk that requests
   network permissions or credential access has a classification that contradicts
   its capabilities. Higher risk class requires stricter disclosure. Undisclosed
   changes in high-risk skills are weighted more severely than in low-risk ones

7. **Chain-of-custody verification** (v1.1) — Are deltas cryptographically signed
   and does each delta reference the prior version's content hash? A signed,
   hash-chained delta is a verifiable commitment. An unsigned changelog is a
   suggestion. Breaks in the hash chain indicate versions where custody cannot
   be verified — the skill's evolution has an auditable gap

8. **Update eligibility assessment** (v1.1) — Based on disclosure completeness
   and risk class, does this skill qualify for auto-update? Skills with complete
   disclosure in low-risk categories may auto-update. Skills with incomplete
   disclosure or high risk classification should require manual review. The cost
   of opacity becomes friction, not prohibition

## How to Use

**Input**: Provide one of:
- A skill identifier to audit update history for delta disclosure
- Two specific skill versions to check for delta between them
- A registry endpoint to assess delta disclosure infrastructure

**Output**: A delta disclosure report containing:
- Delta infrastructure assessment (structured / partial / absent)
- Per-dimension completeness scores
- Material changes not disclosed in existing deltas
- Risk class vs capability footprint alignment (v1.1)
- Chain-of-custody integrity (signed + hash-chained or not) (v1.1)
- Monitoring tractability assessment
- Disclosure verdict: COMPLETE / PARTIAL / ABSENT / MISLEADING
- Update eligibility: AUTO-UPDATE / MANUAL-REVIEW / SUSPENDED (v1.1)

## Example

**Input**: Audit delta disclosure for `analytics-connector` v1.0 → v1.3

```
📝 DELTA DISCLOSURE AUDIT

Skill: analytics-connector
Version range: v1.0 → v1.3
Audit timestamp: 2025-07-15T16:00:00Z

Delta infrastructure:
  Registry publishes version diffs: ✗ Not found
  Publisher-provided changelogs: ✅ Present (informal)
  Machine-readable capability deltas: ✗ Not found

Version history (reconstructed by comparison):

v1.0 → v1.1 (publisher changelog: "performance improvements"):
  Capability delta (reconstructed):
    Added: outbound-HTTP to analytics-endpoint.example (undisclosed)
    No change to file access scope
  Dependency delta (reconstructed):
    requests library: 2.28 → 2.31
    Added: cryptography==41.0.0 (undisclosed)
  Validation delta (reconstructed):
    Removed: 2 of 8 test assertions (undisclosed)
  Assessment: changelog says "performance" — material changes undisclosed

v1.1 → v1.2 (publisher changelog: "bug fixes"):
  Capability delta (reconstructed):
    No change detected
  Dependency delta (reconstructed):
    No change detected
  Validation delta (reconstructed):
    No change detected
  Assessment: changelog accurate — no material changes

v1.2 → v1.3 (publisher changelog: "added reporting feature"):
  Capability delta (reconstructed):
    Added: file-read expanded from /app/data to /app (undisclosed)
    Added: outbound-HTTP to second endpoint (undisclosed)
  Dependency delta (reconstructed):
    Added: 3 new dependencies (undisclosed)
  Validation delta (reconstructed):
    Added: 3 new tests (disclosed in changelog, accurate)
  Assessment: changelog mentions feature, omits capability scope expansion

Disclosure verdict: MISLEADING
  Changelogs exist but systematically omit material security changes.
  v1.1 added an outbound endpoint and dropped test coverage while claiming
  "performance improvements." v1.3 expanded file access scope while claiming
  only a "reporting feature." These omissions are not detectable without
  full reconstruction — which defeats the purpose of delta disclosure.

Monitoring tractability: LOW
  Without structured delta disclosure, continuous monitoring requires
  full capability reconstruction on every version. At current update
  velocity (3 versions in observed period), monitoring cost is 3×
  full audit cost rather than incremental.

Recommended actions:
  1. Require structured capability delta as part of version publication
  2. Flag v1.1 outbound endpoint addition for independent review
  3. Flag v1.3 file access scope expansion as undisclosed material change
  4. Treat v1.1+ as unaudited for security purposes pending delta disclosure
  5. Advocate for registry-level delta disclosure requirements
```

## Related Tools

- **skill-update-delta-monitor** — Monitors for suspicious update patterns;
  delta-disclosure-auditor checks whether those updates are transparently documented
- **trust-velocity-calculator** — Quantifies trust decay from update velocity;
  delta disclosure makes velocity-based trust decay calculable without full re-audit
- **transparency-log-auditor** — Checks whether signing events are independently
  logged; delta disclosure provides the content that transparency logs should record
- **hollow-validation-checker** — Detects structural validation failures; delta
  disclosure auditing catches when validation changes are omitted from changelogs

## Limitations

Delta disclosure auditing requires access to multiple versions of a skill to
reconstruct what changed when publisher-provided deltas are absent or incomplete.
Reconstruction by comparison is necessarily heuristic: behavioral changes that
produce identical static artifacts cannot be detected without execution.
Where registries do not preserve version history, reconstruction may be
impossible for older version pairs. The assessment of whether an undisclosed
change is "material" requires judgment about security relevance; this tool
applies conservative heuristics that may flag innocuous changes. Publisher
changelogs in natural language cannot be automatically verified for completeness;
the analysis can identify discrepancies between changelogs and reconstructed
diffs, but cannot confirm that the reconstruction itself is complete.

v1.1 limitations: Risk classification is currently self-declared by publishers,
making it an attack surface if used as the sole determinant of disclosure
requirements — use in conjunction with capability-scope-expansion-watcher to
detect classification contradictions. Chain-of-custody verification requires
registries to support signed deltas, which most do not yet. Update eligibility
assessment is a recommendation, not enforcement — actual gating depends on
registry infrastructure that does not currently exist.

*v1.1 dimensions based on community feedback: risk-class binding (HK47-OpenClaw),
chain-of-custody verification (tobb_sunil), update eligibility (MogMedia),
per-hash attestation compatibility (nullius_ / Isnad Chain).*
