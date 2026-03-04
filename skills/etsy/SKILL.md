---
name: Etsy
slug: etsy
version: 1.0.0
homepage: https://clawic.com/skills/etsy
description: Improve Etsy listings with buyer-intent keywords, margin-safe pricing checks, and structured experiments that raise qualified traffic and conversion.
changelog: Initial release with listing audits, keyword clustering, pricing safeguards, and experiment tracking for steady Etsy shop growth.
metadata: {"clawdbot":{"emoji":"ET","requires":{"bins":[],"config":["~/etsy/"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.
Ask permission before saving persistent shop context, then continue with the user's current Etsy task immediately.

## When to Use

User needs Etsy growth support for listing quality, search visibility, pricing sanity checks, shop positioning, or conversion improvements.
Use this skill for repeatable execution, not generic brainstorming.

## Architecture

Memory lives in `~/etsy/`. See `memory-template.md` for setup.

```text
~/etsy/
|- memory.md                  # Stable shop context and operating preferences
|- listing-experiments.md     # Experiment log and outcomes
`- launch-checklists.md       # Reusable pre-launch and post-launch checks
```

## Quick Reference

Load only the file needed for the current bottleneck to keep the workflow focused.

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Listing diagnostics workflow | `listing-audit-playbook.md` |

## Core Rules

### 1. Lock Context Before Recommendations
Confirm the listing category, target buyer, shipping region, production model, and current goal before proposing changes.
Without scope, Etsy advice becomes vague and low impact.

### 2. Build Keyword Clusters, Not Isolated Tags
Create one primary intent cluster and two supporting clusters.
Map those terms across title opening words, tags, and first description lines without repeating identical phrasing.

### 3. Optimize the Full Listing Stack Together
Treat title, images, offer clarity, description opening, and shipping promise as one system.
Do not optimize tags alone while weak photos or unclear value proposition remain unresolved.

### 4. Protect Unit Economics Before Growth Tactics
Estimate a conservative contribution margin including Etsy fees, payment fees, packaging, shipping, and ad spend.
Never recommend discount campaigns or paid traffic if the post-fee margin is unclear.

### 5. Run Controlled Experiments With Traceable Metrics
Change one variable per cycle and measure views, favorites, add-to-cart signals, and conversion rate.
Keep each experiment window long enough to avoid false conclusions from short-term noise.

### 6. Enforce Policy and Trust Constraints
Avoid trademarked terms, unverifiable claims, and misleading delivery promises.
When compliance risk exists, state it explicitly and provide a safer alternative.

## Etsy Growth Traps

- Chasing high-volume keywords without buyer fit -> more impressions but weaker conversion.
- Rewriting titles every day -> unstable learning and no reliable baseline.
- Pricing from competitor screenshots alone -> hidden fee structure and margin collapse.
- Ignoring listing photos while tweaking tags -> search traffic may improve but sales stay flat.
- Scaling ads before listing fundamentals -> expensive traffic with low purchase intent.

## Security & Privacy

**Data that leaves your machine:**
- None by default from this skill itself

**Data that stays local:**
- Shop context and workflow preferences in `~/etsy/`

**This skill does NOT:**
- Ask for marketplace passwords or payment credentials
- Post, edit, or publish listings automatically
- Make undeclared network requests

## Scope

This skill ONLY:
- Structures Etsy listing and shop growth workflows
- Audits conversion blockers and search relevance gaps
- Recommends measurable experiments with clear success criteria

This skill NEVER:
- Guarantees ranking position
- Invents performance metrics not provided by the user
- Executes irreversible marketplace actions without confirmation

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ecommerce` - End-to-end online store operations and conversion foundations.
- `seo` - Search intent and content optimization principles transferable to listings.
- `pricing` - Pricing strategy and tradeoff frameworks for margin and demand.
- `market-research` - Competitive positioning and demand validation workflows.
- `content-marketing` - Messaging frameworks that improve listing clarity and value communication.

## Feedback

- If useful: `clawhub star etsy`
- Stay updated: `clawhub sync`
