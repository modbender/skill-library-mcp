---
name: skill-dependency-chain-auditor
description: >
  Helps audit transitive skill dependency chains in agent compositions —
  catching the class of risk where a skill's direct dependencies appear safe
  but a dependency-of-a-dependency introduces a vulnerability that propagates
  up the entire chain.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "⛓️"
  agent_card:
    capabilities: [transitive-dependency-auditing, deep-chain-vulnerability-detection, dependency-propagation-analysis]
    attack_surface: [L1, L2]
    trust_dimension: attack-surface-coverage
    published:
      clawhub: false
      moltbook: false
---

# Your Skill's Dependency Is Safe. Its Dependency's Dependency Is Not.

> Helps identify vulnerabilities in transitive skill dependency chains —
> the attack surface that direct dependency auditing cannot see.

## Problem

Agent skills rarely operate in isolation. A skill that provides a useful
capability often depends on other skills for sub-capabilities: a data
processing skill may depend on a file parsing skill that depends on a format
conversion skill. Each link in this dependency chain is a potential
vulnerability entry point — and auditing only the top-level skill misses
everything below it.

The transitive dependency problem in agent ecosystems mirrors the problem
that produced major software supply chain incidents: auditors focused on the
immediate code, not the full dependency tree. An attacker who cannot
compromise a well-audited top-level skill can achieve the same result by
compromising a less-scrutinized dependency that the top-level skill trusts
implicitly.

Transitive dependencies compound the blast radius problem. A vulnerability
in a foundational skill used by many other skills as a dependency propagates
upward through the entire dependency graph. An agent with five installed
skills, each depending on three sub-skills, may have an effective dependency
surface of fifteen or more skills — most of which received no direct review
at install time.

The audit gap is structural. Standard skill marketplace reviews evaluate
published skills as independent units. They do not trace dependency chains,
assess the composition of trust across dependency links, or flag cases where
a safe skill depends on an unaudited or compromised skill. The trust granted
to a skill implicitly extends to everything it depends on — and that implicit
extension is unverified.

## What This Audits

This auditor examines skill dependency chain integrity across five dimensions:

1. **Transitive dependency inventory** — What is the complete set of skills
   that a given skill transitively depends on? Direct dependencies are the
   visible surface; transitive dependencies are the actual attack surface.
   The auditor maps the full dependency graph, not just the first level

2. **Trust gradient across the chain** — Do the trust levels of skills in
   the dependency chain decrease as depth increases? High-trust top-level
   skills depending on lower-trust sub-skills create a trust gradient that
   attackers can exploit by targeting the less-scrutinized lower levels

3. **Dependency version pinning** — Are dependency references pinned to
   specific verified versions, or are they floating references that can be
   silently satisfied by updated versions? Floating dependencies allow
   dependency-level install-then-update attacks that bypass top-level auditing

4. **Circular and diamond dependency detection** — Does the dependency graph
   contain circular references or diamond patterns (multiple paths converging
   on the same dependency) that create ordering ambiguity or amplify the
   blast radius of a single dependency compromise?

5. **Capability aggregation across the chain** — What is the combined
   capability set of the full dependency tree? Skills that individually
   declare limited capabilities may collectively provide a combined capability
   not declared at any level of the tree

## How to Use

**Input**: Provide one of:
- A skill identifier to audit its full transitive dependency chain
- An agent's installed skill list to map the combined dependency graph
- Two skill identifiers to check for shared dependency paths (common attack surface)

**Output**: A dependency chain audit report containing:
- Full transitive dependency inventory with trust levels
- Trust gradient analysis
- Version pinning assessment
- Graph structure anomalies (circular, diamond)
- Aggregated capability surface across the full chain
- Chain integrity verdict: SOUND / DEGRADED / VULNERABLE / COMPROMISED

## Example

**Input**: Audit dependency chain for `document-analyzer` skill

```
⛓️ SKILL DEPENDENCY CHAIN AUDIT

Skill: document-analyzer v2.1
Audit timestamp: 2025-12-01T11:00:00Z

Transitive dependency inventory:
  Level 1 (direct):
    text-extractor v1.4 [trust: HIGH, audited 2025-06-01]
    format-converter v2.0 [trust: HIGH, audited 2025-07-15]
    metadata-parser v1.2 [trust: MEDIUM, audited 2025-03-10]

  Level 2 (dependencies of direct deps):
    unicode-normalizer v3.1 (dep of text-extractor)
      [trust: HIGH, audited 2025-08-01]
    charset-detector v1.8 (dep of text-extractor)
      [trust: LOW, last audited 2024-01-15 — 11 months ago] ⚠️
    pdf-parser v4.2 (dep of format-converter)
      [trust: HIGH, audited 2025-09-01]
    xml-parser v2.3 (dep of format-converter)
      [trust: MEDIUM, audited 2025-05-01]
    mime-detector v1.1 (dep of metadata-parser)
      [trust: UNVERIFIED, no audit record found] ⚠️

  Level 3 (transitive):
    encoding-tables v2.0 (dep of charset-detector)
      [trust: LOW, 18-month-old audit] ⚠️
    http-fetcher v1.5 (dep of mime-detector) ⚠️
      [trust: UNVERIFIED, no audit record]
      → http-fetcher adds OUTBOUND-NETWORK capability not declared at top level ⚠️⚠️

Trust gradient:
  document-analyzer: HIGH
  Level 1 average: MEDIUM-HIGH
  Level 2 average: LOW-MEDIUM (two unverified/stale)
  Level 3: UNVERIFIED (critical outbound capability)
  → Trust degrades significantly at depth ⚠️

Version pinning:
  text-extractor: pinned to v1.4 ✅
  format-converter: ^2.0 (floating minor/patch) ⚠️
  metadata-parser: latest (unpinned) ⚠️
  → 2 of 3 direct dependencies allow silent updates

Dependency graph structure:
  charset-detector: shared between text-extractor and metadata-parser
  → Diamond pattern: charset-detector compromise affects two paths ⚠️
  No circular dependencies detected ✅

Aggregated capability surface:
  Declared (document-analyzer): file-read (scoped), text processing
  Actual (full chain): file-read (scoped) + network-outbound (via http-fetcher)
  → Undeclared capability: OUTBOUND-NETWORK from http-fetcher ⚠️

Chain integrity verdict: VULNERABLE
  document-analyzer's dependency chain contains an unverified skill
  (mime-detector) that itself depends on http-fetcher, adding outbound
  network capability not declared at any level of the chain. Two direct
  dependencies are floating (unpinned), and charset-detector forms a
  diamond pattern amplifying its blast radius. The trust gradient degrades
  from HIGH at the top level to UNVERIFIED at depth.

Recommended actions:
  1. Audit mime-detector and http-fetcher before any production use
  2. Pin all dependency versions (especially format-converter and metadata-parser)
  3. Investigate why http-fetcher is in the dependency chain — outbound network
     capability is not consistent with document analysis functionality
  4. Apply network-outbound monitoring to document-analyzer instances
  5. Treat document-analyzer as having OUTBOUND-NETWORK capability
     for permission management purposes
```

## Related Tools

- **capability-composition-analyzer** — Identifies dangerous capability
  combinations across an agent's installed skills; dependency chain auditor
  identifies how those capabilities are acquired through dependency chains
  rather than direct skill installation
- **supply-chain-poison-detector** — Detects malicious code in individual skills;
  dependency chain auditor maps the full attack surface that supply chain attacks
  can exploit through transitive dependencies
- **blast-radius-estimator** — Estimates propagation impact if a skill is
  compromised; transitive dependencies amplify blast radius by extending the
  effective attack surface beyond what direct agent-to-skill relationships show
- **trust-decay-monitor** — Tracks verification freshness decay; dependency chains
  accumulate trust decay when lower-level dependencies go unaudited while
  top-level skills maintain current audit records

## Limitations

Skill dependency chain auditing requires accurate dependency metadata for all
skills in the chain, which depends on marketplace dependency declaration
standards. Skills that do not declare dependencies explicitly — or that load
dependencies dynamically at runtime — will produce incomplete dependency graphs.
Transitive dependency mapping requires recursive access to dependency metadata
across the full chain; registries that do not provide this information limit
analysis to direct dependencies only. The capability aggregation analysis
depends on accurate capability declarations at each level; skills that acquire
capabilities dynamically or through side channels will be missed. Diamond
dependency analysis identifies structural amplification risk; whether a shared
dependency is actually exploited depends on factors beyond static graph analysis.
