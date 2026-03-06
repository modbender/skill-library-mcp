---
name: capability-scope-expansion-watcher
description: >
  Helps detect incremental capability scope expansion across skill versions —
  the pattern where a skill gradually claims broader permissions through small,
  individually-plausible updates that accumulate into a significantly expanded
  attack surface. v1.1 adds risk-class contradiction detection.
version: 1.1.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🔭"
  agent_card:
    capabilities: [capability-scope-expansion-detection, incremental-permission-drift, version-history-analysis, risk-class-contradiction-detection]
    attack_surface: [L1, L2]
    trust_dimension: attack-surface-coverage
    published:
      clawhub: false
      moltbook: false
---

# Your Skill Started with File Read. Now It Has the Whole Filesystem.

> Helps identify skills that incrementally expand their capability scope
> across versions — the slow drift from declared intent to an attack surface
> that no single update made obvious.

## Problem

Capability scope expansion is rarely dramatic. A skill that declared
"read /app/data/" at v1.0 does not suddenly claim "read /" at v1.1. Instead,
the expansion happens incrementally: v1.1 adds one subdirectory for a
legitimate-sounding reason, v1.2 adds another, v1.3 resolves environment
variables that could point anywhere. By v1.6, the effective file access scope
covers the entire filesystem — but no single version change was large enough
to trigger a review.

This is the slow-drift attack pattern. Each individual step is defensible.
The changelog for each version describes a plausible business reason for the
scope change. Auditors reviewing any single version transition see a
reasonable change. Only an auditor examining the full version history —
comparing v1.0 to v1.6 — sees the accumulated scope expansion for what it is.

The problem compounds when capability scope and behavioral scope expand
together. A skill that started as a simple data formatter may, after six
versions of plausible-sounding improvements, have acquired the ability to
read arbitrary configuration files, resolve secrets from environment variables,
and make outbound HTTP requests to user-configurable endpoints. No individual
feature addition made this obvious. The combination did.

Incremental scope expansion is harder to detect than discrete permission
requests precisely because it exploits the low-attention threshold for small
changes. A request for full filesystem access at install time would trigger
immediate review. The same access accumulated across twelve updates might
not trigger any review at all.

## What This Watches

This watcher examines capability scope expansion across five dimensions:

1. **Cumulative permission drift** — What is the total permission scope
   expansion from the skill's initial version to its current version?
   Individual version transitions may appear reasonable while the cumulative
   drift is significant. The watcher computes the total scope change, not
   the marginal change

2. **Step-size anomalies** — Is the expansion occurring in regular small
   steps that suggest a planned incremental strategy, rather than the
   irregular steps expected from genuine feature development? Consistent
   small expansions across many versions are more suspicious than
   irregular larger expansions

3. **Behavioral scope vs. declared scope alignment** — Does the skill's
   effective capability (what it can do based on its permission set and
   declared functions) remain aligned with its stated purpose across versions?
   Drift between stated purpose and effective capability is a key signal

4. **Capability composition amplification** — When the skill's accumulated
   permissions are considered in combination, do they create emergent
   capabilities not present at any earlier version? A skill that acquires
   file-read and network-outbound separately may only become an exfiltration
   path once both are present

5. **Changelog completeness for scope changes** — Does each version that
   expands capability scope include a changelog entry that explicitly
   declares the expansion? Silent scope expansions (version changelog
   mentions only bug fixes while permissions expand) are higher risk than
   declared expansions

6. **Risk-class contradiction detection** (v1.1) — Does the skill's
   self-declared risk classification match its actual capability footprint?
   A skill classified as "low-risk" or "read-only utility" that requests
   network permissions, credential access, or filesystem scope beyond its
   declared purpose has a classification that contradicts its capabilities.
   The delta between declared risk class and actual capability footprint is
   itself a security signal — and a potential attack surface if risk class
   determines disclosure requirements

## How to Use

**Input**: Provide one of:
- A skill identifier to trace its capability scope evolution across versions
- A specific version range to assess cumulative expansion over a period
- An agent's installed skill list to identify which skills have drifted
  furthest from their initial capability declarations

**Output**: A scope expansion report containing:
- Per-version permission delta (declared and observed)
- Cumulative scope expansion since initial version
- Step-size pattern analysis
- Behavioral scope alignment assessment
- Capability composition amplification points
- Changelog completeness for scope-changing versions
- Expansion verdict: STABLE / DRIFT / INCREMENTAL-EXPANSION / SCOPE-CAPTURE

## Example

**Input**: Trace capability scope evolution for `report-generator` v1.0 → v1.5

```
🔭 CAPABILITY SCOPE EXPANSION REPORT

Skill: report-generator
Version range: v1.0 → v1.5 (6 versions)
Audit timestamp: 2025-10-12T09:00:00Z

Stated purpose (v1.0): "Generate formatted reports from structured data"

Per-version scope delta:

v1.0: file-read (/app/data/*.csv), file-write (/app/reports/)
  Changelog: "Initial release" — matches declared purpose ✅

v1.1 → v1.0 delta: file-read expanded to /app/data/ (any file, not just CSV)
  Changelog: "Support more data formats" — reasonable explanation ⚠️ (undisclosed scope)

v1.2 → v1.1 delta: Added env-read (specific variables: REPORT_TEMPLATE_PATH)
  Changelog: "Configurable templates" — plausible ⚠️

v1.3 → v1.2 delta: env-read expanded to any env variable matching *_PATH or *_DIR
  Changelog: "Flexible path configuration" — partially disclosed ⚠️

v1.4 → v1.3 delta: Added network-outbound to user-configurable endpoint
  Changelog: "Remote report delivery option" — disclosed ✅ but significant new capability

v1.5 → v1.4 delta: network-outbound endpoint now resolved from env variable
  Changelog: "Support environment-based configuration" — partially disclosed ⚠️

Cumulative scope expansion (v1.0 → v1.5):
  File read: /app/data/*.csv → /app/data/ (any file)
  Environment: none → any variable matching *_PATH or *_DIR
  Network: none → outbound to env-variable-specified endpoint
  → Scope expanded from constrained CSV reader to configurable data exfiltration path

Step-size analysis:
  5 expansions across 5 version transitions — one per version ⚠️
  Each expansion individually small and defensible
  Pattern consistent with incremental scope-capture strategy

Behavioral vs. declared scope:
  v1.0 declared: report generation from structured data
  v1.5 effective: read any file in /app/data/, resolve environment paths,
    send data to operator-configurable remote endpoint
  → Significant drift from declared purpose

Capability composition amplification:
  v1.4 milestone: file-read + env-read + network-outbound first co-present
  → At v1.4, skill acquired effective exfiltration capability not present at any earlier version
  → This is the composition amplification point

Expansion verdict: SCOPE-CAPTURE
  report-generator has expanded its capability scope in every version,
  with each step individually defensible but the cumulative drift significant.
  The v1.4 composition amplification point created an effective exfiltration
  path that did not exist at initial installation. The one-expansion-per-version
  pattern is consistent with deliberate incremental scope capture.

Recommended actions:
  1. Review the v1.4 network-outbound endpoint for data exfiltration
  2. Audit what data is being sent to the remote endpoint
  3. Restrict env-read to specifically declared variables only
  4. Require explicit operator approval before any future scope expansion
  5. Treat v1.4+ as unverified pending capability audit
```

## Related Tools

- **capability-composition-analyzer** — Analyzes dangerous capability combinations
  at a point in time; capability-scope-expansion-watcher tracks how those
  combinations accumulate across version history
- **delta-disclosure-auditor** — Checks whether updates publish structured change
  records; undisclosed scope expansions are precisely what delta disclosure
  requirements are designed to catch
- **permission-creep-scanner** — Detects excessive permissions in individual
  skills; this tool focuses on the incremental accumulation of permissions
  across multiple versions rather than point-in-time excess
- **trust-decay-monitor** — Tracks how verification freshness decays over time;
  scope expansion accelerates trust decay because earlier audits no longer
  apply to the current capability surface

## Limitations

Capability scope expansion watching requires access to the full version history
of a skill, including capability declarations for each version. Registries that
do not preserve historical version metadata make cumulative analysis impossible.
The distinction between genuine feature development and deliberate scope capture
is inherently ambiguous: legitimate product evolution naturally expands
capabilities over time, and the same growth trajectory can represent either
pattern. The step-size anomaly analysis assumes that deliberate scope capture
tends toward regular small steps — sophisticated attackers may deliberately
vary step size to avoid detection. Capability composition amplification points
depend on accurate capability declaration for all versions; skills that
misrepresent their capabilities will produce incomplete composition analysis.

v1.1 limitation: Risk classification is currently self-declared by publishers.
A skill that under-classifies its risk to avoid strict disclosure requirements
is using the classification system as an attack surface. Detection of
classification contradictions depends on accurate capability metadata — if the
capability declarations are also misrepresented, the contradiction is invisible.

*v1.1 risk-class contradiction detection based on feedback from HK47-OpenClaw
in the delta disclosure discussion thread.*
