---
name: attestation-root-diversity-analyzer
description: >
  Helps measure the concentration of trust roots in a skill's attestation
  graph — identifying monoculture risk where a single compromised root
  invalidates an entire chain that appears to have multiple validators.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🌐"
---

# The Attestation Chain Has Seven Links. They All Trace Back to One Root.

> Helps identify when a skill's trust chain is structurally fragile — not because individual links are weak, but because all paths converge on a single root that one compromise can invalidate.

## Problem

A skill with five attestation badges looks more trustworthy than a skill with one. But if four of those five badges trace back through the same root attestor, the effective trust diversity is closer to two than to five. The appearance of multiple independent validators is real; the independence is not.

This is a topology problem, not a cryptography problem. A trust graph where all paths converge on a single root is not a distributed trust system — it's a hub-and-spoke system wearing the visual appearance of a mesh. A hub-and-spoke system has all the failure properties of centralized trust: compromise the hub, and every spoke-rooted badge becomes invalid simultaneously.

The risk is not hypothetical. Self-attesting roots — where the publisher is also the root attestor, or where multiple attestation badges trace back to a single organization — are common in ecosystems where attestation is new and infrastructure is thin. A skill from a well-known publisher that has also reviewed its own dependencies through affiliated validators presents structural fragility even if every individual attestation is cryptographically correct.

Measuring this requires looking at the full trust graph, not just the badges at the leaves.

## What This Analyzes

This analyzer examines attestation root diversity across five dimensions:

1. **Root concentration index** — What fraction of the attestation graph's trust paths converge on each distinct root? A Herfindahl-style concentration measure identifies whether trust is effectively distributed or structurally centralized
2. **Self-attestation detection** — Does the skill's publisher appear anywhere in its own trust chain? Self-attestation is not inherently invalid, but it must be disclosed and weighted appropriately
3. **Organizational diversity** — Are the distinct roots associated with independent organizations, or do multiple roots trace back to the same controlling entity through different organizational names?
4. **Effective validator count** — After accounting for convergence, how many truly independent validators contribute to the skill's trust score? A skill with 12 badges from 3 organizations has an effective count of 3, not 12
5. **Structural fragility score** — If the highest-concentration root were compromised, what percentage of the skill's attestation graph would be invalidated?

## How to Use

**Input**: Provide one of:
- A skill identifier with its attestation metadata
- A trust graph (validator chain, root identifiers) to analyze
- Two skills to compare relative root concentration

**Output**: A root diversity report containing:
- Root concentration index (0 = fully distributed, 1 = single root)
- Attestation graph visualization (text-based)
- Self-attestation flags
- Organizational diversity assessment
- Effective validator count
- Structural fragility score
- Diversity verdict: DISTRIBUTED / CONCENTRATED / MONOCULTURE / SELF-ATTESTING

## Example

**Input**: Analyze attestation root diversity for `workflow-automator` skill

```
🌐 ATTESTATION ROOT DIVERSITY ANALYSIS

Skill: workflow-automator
Attestation badges: 7
Audit timestamp: 2025-04-20T14:00:00Z

Trust graph structure:
  Badge A → Validator-1 → Root-Alpha (publisher-org)
  Badge B → Validator-2 → Root-Alpha (publisher-org)
  Badge C → Validator-3 → Root-Alpha (publisher-org)
  Badge D → Validator-4 → Root-Beta (third-party)
  Badge E → Validator-5 → Root-Beta (third-party)
  Badge F → Validator-6 → Root-Alpha (publisher-org)  ← affiliate
  Badge G → Validator-7 → Root-Gamma (community)

Root concentration analysis:
  Root-Alpha (publisher-org): 4/7 paths (57%) → publisher + 3 affiliated validators
  Root-Beta (third-party): 2/7 paths (29%)
  Root-Gamma (community): 1/7 paths (14%)

Herfindahl index: 0.57² + 0.29² + 0.14² = 0.42
  (0 = perfect distribution, 1 = single root)
  Classification: CONCENTRATED (threshold: >0.33 = concentrated)

Self-attestation: ⚠️ DETECTED
  Root-Alpha is publisher-org — publisher attests to its own skill
  3 of 7 badges trace directly to publisher-controlled validators

Organizational diversity:
  Distinct organizations: 3 (publisher-org, third-party, community)
  Effective independent: 2 (publisher-org counts as 1 despite 4 paths)
  Effective validator count: 2.4 (weighted by independence)

Structural fragility:
  If Root-Alpha were compromised: 4/7 badges (57%) invalidated
  Residual trust: Root-Beta (29%) + Root-Gamma (14%) = 43%

Diversity verdict: CONCENTRATED
  7 badges with 3 roots, but effective independence is 2.4 validators.
  Root-Alpha concentration exceeds recommended threshold for high-impact
  skills. Self-attestation by publisher reduces independence further.

Recommended actions:
  1. Require minimum 2 non-publisher roots for full DISTRIBUTED status
  2. Disclose self-attestation presence in badge display
  3. Weight Root-Alpha badges at 0.5× for concentration-aware scoring
  4. Target Root-Gamma growth to reduce Alpha concentration below 0.33
```

## Related Tools

- **attestation-chain-auditor** — Validates chain integrity and completeness; root diversity analyzer measures whether that chain's roots are structurally independent
- **transparency-log-auditor** — Checks whether signing events are independently auditable; diverse roots are more valuable when each root's behavior is logged
- **publisher-identity-verifier** — Verifies publisher identity; publisher as self-attesting root is a specific concentration risk to flag
- **trust-velocity-calculator** — Quantifies trust decay rate; concentrated attestation graphs decay faster when a root is compromised

## Limitations

Root diversity analysis requires access to the full attestation graph, including the organizational relationships between validators — data that many current marketplaces do not expose. Where only the leaf badges are visible and root relationships must be inferred, the analysis is necessarily approximate. Organizational independence is difficult to verify programmatically: two organizations with different names may share effective control. The Herfindahl-based concentration measure is a useful heuristic, not a definitive security assessment — the appropriate threshold depends on the risk profile of the capability being attested. A concentrated attestation graph is a structural concern, not a confirmation of compromise; it means the trust infrastructure is more fragile, not that it has already failed.
