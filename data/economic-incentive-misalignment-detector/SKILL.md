---
name: economic-incentive-misalignment-detector
description: >
  Helps identify when marketplace economic incentives systematically favor
  quantity over quality — creating structural pressure toward publishing
  unsafe skills that individual technical audits cannot detect because the
  problem is incentive design, not code content.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "💰"
  agent_card:
    capabilities: [economic-incentive-analysis, marketplace-structure-auditing, quality-vs-quantity-bias-detection]
    attack_surface: [L2]
    trust_dimension: rule-adoption
    published:
      clawhub: false
      moltbook: false
---

# The Marketplace Is Not Broken. The Incentives Are.

> Helps identify when marketplace economic structures create systematic bias
> toward publishing volume over safety quality — the root cause that technical
> audits cannot fix because the problem predates the code.

## Problem

Technical audits catch bad code. They do not catch bad incentives. An agent
marketplace where publishers are rewarded primarily for download counts and
upvotes creates structural pressure toward a specific failure mode: optimize
for initial impressions rather than long-term safety, publish early and often
rather than thoroughly audit, prioritize visible features over invisible
security properties.

This pressure operates even when every publisher intends to be responsible.
A publisher competing in a marketplace where competitors publish ten skills
per week faces a choice between competitive disadvantage and cutting corners
on security review. The individual publisher's incentives point toward
lower-quality publishing even when the publisher values quality. The
incentive misalignment is systemic, not individual.

The economic dimensions of this problem interact with the technical ones in
ways that compound risk. Marketplaces that charge per-download create
pressure to maximize installs, which favors misleading capability descriptions
that attract more installs. Marketplaces that reward upvotes create pressure
toward social manipulation. Marketplaces that take revenue from publishers
have conflicts of interest in aggressive safety enforcement that might reduce
their publisher base.

These structural problems produce predictable patterns in marketplace data:
concentrated publishing from a small number of high-volume publishers, rapid
update cycles that exceed any reasonable review capacity, reputation inflation
through social gaming, and systematic underfunding of safety infrastructure
relative to growth infrastructure.

## What This Analyzes

This analyzer examines economic incentive alignment across five dimensions:

1. **Publisher concentration risk** — Is marketplace activity concentrated
   in a small number of high-volume publishers who face the strongest
   incentive pressure? High concentration means a small number of publishers
   facing misaligned incentives can disproportionately affect marketplace
   safety quality

2. **Publication velocity vs. review capacity** — Does the rate of new skill
   publications exceed any plausible human review capacity? Marketplaces
   where publication velocity outpaces review capacity structurally cannot
   maintain quality standards regardless of individual publisher intent

3. **Revenue model conflict of interest** — Does the marketplace's revenue
   model create conflicts of interest in safety enforcement? Payment models
   tied to publisher count or download volume create financial incentives
   to tolerate lower safety standards

4. **Safety investment vs. growth investment ratio** — Does the marketplace
   invest comparably in safety infrastructure (audit tools, reviewer capacity,
   enforcement mechanisms) and growth infrastructure (discovery algorithms,
   publisher tools, marketing)? Systematic underinvestment in safety relative
   to growth is a structural signal

5. **Enforcement asymmetry** — Does the marketplace apply consistent
   enforcement standards regardless of publisher size and revenue contribution?
   Asymmetric enforcement that protects high-revenue publishers from the same
   standards applied to small publishers is a structural misalignment signal

## How to Use

**Input**: Provide one of:
- A marketplace to assess for structural incentive misalignment
- A publisher's output metrics to assess for incentive-driven quality degradation
- A marketplace policy document to analyze for structural conflict of interest

**Output**: An incentive alignment report containing:
- Publisher concentration analysis
- Publication velocity vs. review capacity assessment
- Revenue model conflict of interest evaluation
- Safety vs. growth investment indicators
- Enforcement consistency assessment
- Alignment verdict: ALIGNED / PARTIAL / MISALIGNED / STRUCTURALLY-COMPROMISED

## Example

**Input**: Assess incentive alignment for `AgentMarket` marketplace

```
💰 ECONOMIC INCENTIVE ALIGNMENT ASSESSMENT

Marketplace: AgentMarket
Assessment timestamp: 2025-11-01T14:00:00Z

Publisher concentration:
  Total active publishers: 847
  Top 10 publishers by output: 68% of all skills published
  Top publisher output: 47 skills in 30 days (1.6 skills/day)
  → High concentration: 1.2% of publishers produce 68% of content ⚠️
  → Top publishers face strongest incentive pressure

Publication velocity vs. review capacity:
  New skills published (last 30 days): 2,847
  Marketplace review team size: 12 (estimated from job postings)
  Skills per reviewer per day: 7.9
  Industry standard thorough review time: 45-90 minutes per skill
  Maximum review capacity at 8h/day: 5.3 skills/reviewer/day
  → Publication rate exceeds review capacity by ~50% ⚠️
  → Thorough manual review of all publications is structurally impossible

Revenue model:
  Publisher fees: Per-download revenue share (publisher earns per download)
  Marketplace revenue: Transaction cut + premium placement fees
  Conflict assessment: Per-download model creates incentive for misleading
    capability descriptions that maximize installs over actual fit ⚠️
  Premium placement fees create incentive to favor high-paying publishers
    in discovery algorithms regardless of quality ⚠️

Safety vs. growth investment:
  Safety team: 12 reviewers (estimated)
  Growth/product team: 84 (estimated from LinkedIn)
  Safety-to-growth ratio: 1:7 ⚠️
  Industry comparable for financial infrastructure: 1:2 to 1:3
  → Systematic underinvestment in safety relative to growth

Enforcement consistency:
  Top 5 publishers by revenue: 3 have had policy violations in 90 days
    with no public enforcement action found
  Small publishers with similar violations: enforcement found in 2/3 cases
  → Enforcement asymmetry detected ⚠️

Alignment verdict: STRUCTURALLY-COMPROMISED
  AgentMarket shows four of five misalignment indicators. The per-download
  revenue model creates direct incentive to maximize installs over quality.
  Publication velocity structurally exceeds review capacity. Safety investment
  is systematically lower than growth investment. Enforcement is asymmetric
  by publisher revenue tier. Individual publisher behavior is influenced by
  these structural incentives regardless of individual intent.

Recommended actions:
  1. Apply higher scrutiny standards when evaluating skills from this marketplace
  2. Do not rely on download count or upvotes as quality proxies in this context
  3. Prefer skills from publishers who preemptively publish audit artifacts
  4. Advocate for marketplace structural reforms: fixed-fee rather than
     per-download revenue, mandatory safety review before publishing
  5. Support alternative marketplaces with different incentive structures
```

## Related Tools

- **clone-farm-detector** — Detects content-level cloning for reputation gaming;
  economic incentive misalignment creates structural pressure that explains why
  clone farming emerges even without individual malicious intent
- **social-trust-manipulation-detector** — Identifies coordinated social trust
  manipulation; economic incentives to maximize perceived trust create demand
  for the manipulation techniques this tool detects
- **blast-radius-estimator** — Estimates propagation impact if a skill is
  compromised; markets with misaligned incentives will systematically produce
  more compromised skills, amplifying blast radius across the ecosystem
- **publisher-identity-verifier** — Verifies publisher identity integrity;
  economic pressure toward high-volume publishing creates conditions where
  identity shortcuts (account selling, takeover) become economically rational

## Limitations

Economic incentive analysis requires marketplace-level data that may not be
publicly accessible: publisher revenue figures, enforcement actions, review
team size, and internal investment allocations are often proprietary.
Where data is limited, the assessment is based on publicly observable proxies
(publication rates, team size estimates from job postings, enforcement actions
visible in public records) that may not accurately reflect actual operations.
Publisher concentration analysis depends on accurate publisher attribution,
which may be obscured when publishers operate through multiple accounts.
The assessment identifies structural incentive problems that create risk
conditions — it does not assess the intentions of individual marketplace
operators, who may be working within genuine constraints while still producing
structurally problematic outcomes.
