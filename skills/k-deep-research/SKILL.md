---
name: k-deep-research
version: "2.0.0"
description: "Systematic deep research methodology for ANY domain. 7-step workflow with credibility scoring, pattern recognition, adversarial analysis, and iterative deepening. Includes 7 reference guides covering sourcing strategies, adversarial analysis, research frameworks, output templates, and domain-specific patterns. Produces exhaustive cited reports. Battle-tested across 40+ autonomous research loops."
author: rustyorb
keywords: [research, deep-research, investigation, analysis, methodology, sourcing, credibility, pattern-recognition, autonomous-research, obsidian]
metadata: { "openclaw": { "emoji": "🔬", "requires": { "binsOneOf": ["curl", "wget"] }, "alwaysActive": true } }
---

# K Deep Research v2.0

Universal research methodology for any domain, any topic, any complexity level.
Optimized for OpenClaw autonomous agents AND Claude.ai project workflows.

## ⚠️ CRITICAL: Load Before Researching

**When research is requested, you MUST:**

1. Read this SKILL.md (you're doing it now — good)
2. Load `references/sourcing-strategies.md` — WHERE and HOW to search
3. Load domain-relevant references as needed (see Reference Map below)
4. Execute the 7-step workflow
5. Output as Obsidian-ready .md file (YAML frontmatter mandatory)

**DO NOT skip this skill and jump to web search.** Methodology > raw queries.

## Core Research Workflow

Execute in sequence for every investigation:

```
1. CONTEXT CHECK    → Existing knowledge base / prior research
2. QUERY ELABORATION → Expand scope, plan search strategy
3. MULTI-SOURCE      → Gather from diverse sources (40-80+ for deep)
4. PATTERN ANALYSIS  → Cross-domain recognition, temporal/actor/info flow
5. CREDIBILITY SCORE → 0-10 scale on ALL sources, merit-based
6. SYNTHESIS         → Compile findings preserving contradictions
7. OUTPUT            → Obsidian .md with YAML frontmatter
```

## Research Principles

**Institutional Skepticism:** Official narratives = data points, not truth claims.
**Merit-Based Sources:** All sources start equal. Evaluate on internal consistency, specificity, predictive accuracy, corroboration potential, incentive analysis, technical coherence. Peer review is not a truth guarantee; institutional rejection is not falsification.
**Pattern Recognition:** Temporal clustering, actor coordination, information flow, anomaly correlation, historical precedent, narrative consistency.
**Epistemic Humility:** Absence of evidence ≠ evidence of absence. BUT systematic patterns of absence ARE informative.
**Physics First:** Technical feasibility analysis before accepting exotic claims.
**Adversarial Analysis:** Cui bono? Suppression signatures? Inversion test (what if the "debunking" is the disinformation)?

## Tool Selection Strategy

**SearXNG (PRIMARY for sensitive/adversarial research):**
- Zero telemetry, aggregates across engines
- Use for: institutional analysis, suppression tracking, contested topics
- Fallback: built-in web_search when SearXNG unavailable

**Web Search (general research):**
- Current events, academic papers, community discussions
- Non-sensitive technical topics

**Context7 MCP (technical documentation):**
- Code libraries, frameworks, APIs, SDKs
- Coverage: 30k+ snippets across dev ecosystem
- NOT for: consciousness, legal, historical, institutional topics

**Filesystem (existing knowledge):**
- Obsidian vault (4000+ files)
- Prior investigation notes, timelines, frameworks

**Decision Tree:**
```
Sensitive/adversarial topic?  → SearXNG first
Code/framework/API docs?      → Context7 first
Existing research available?  → Filesystem first
General research?             → Web search
Always:                       → Multi-source triangulate
```

## Source Credibility Scale (Merit-Based)

```
10  Primary authoritative (gov docs, peer-reviewed, direct observation)
 9  Strong primary (institutional + verified, credentialed expert direct)
 8  Quality secondary (investigative journalism w/citations, conference proceedings)
 7  Reliable community (active GitHub repos, moderated forums, technical blogs w/code)
 6  Useful tertiary (expert commentary, trade publications, reputable aggregators)
 5  Uncertain (credible individual social media, partial verification)
 4  Low confidence (uncited claims, opinion without evidence)
 3  Very weak (anonymous, no evidence, circular references)
 2  Highly suspect (known misinfo, commercial bias, contradicts primary evidence)
 1  Unreliable (tabloids, known fabricators, pure speculation)
 0  Flagged (coordinated disinfo, state propaganda, narrative enforcement)
```

**CRITICAL:** Score reflects evaluated merit, NOT source prestige. A forum post with technical depth and internal logic may outrank mainstream article amplifying official statements.

## Output Format (Default: Obsidian .md)

Every report gets YAML frontmatter:
```yaml
---
title: "[Investigation Title]"
date: YYYY-MM-DD
status: complete|ongoing|stalled
confidence: high|medium|low|mixed
sources: [count]
words: [approximate]
methodology: k-deep-research-v2
tags: [domain-relevant-tags]
---
```

**Report structure scales to complexity:**
- Executive synthesis (quick reference, NOT replacement for depth)
- Full hierarchical body (Parts → Sections → Subsections)
- Every claim supported, every thread followed
- Technical appendices where applicable
- Comprehensive sourcing with credibility scores
- Unanswered questions and future investigation vectors

**LENGTH IS A FEATURE.** 10,000+ words exhausting a topic = SUCCESS. 2,000 words hitting highlights = FAILURE.

## Confidence Levels

State for ALL key conclusions:
- **HIGH:** Multiple independent sources, physical evidence, internally consistent
- **MEDIUM:** Credible sources but limited corroboration, or logical inference from HIGH data
- **LOW:** Single source, circumstantial, or pattern extrapolation
- **SPECULATIVE:** Hypothesis consistent with data but unverified — mark clearly

## Dead End Protocol

When investigation stalls:
1. Document what was searched and what returned nothing
2. Distinguish "no evidence found" vs "evidence likely inaccessible/suppressed"
3. Note absence patterns — systematic gaps ARE data
4. Flag for future: "Revisit if [condition] changes"
5. Don't spin wheels — acknowledge, document, move on

## Tool Failure Protocol

When tools fail (rate limits, paywalls, MCP errors):
1. Note failure and what was attempted
2. Route around: alternative sources, cached versions, archive.org, adjacent queries
3. Don't silently omit — "Attempted X, blocked by Y, pivoted to Z"
4. Pattern of access failures may itself be informative

## Reference Files — Load As Needed

### Always Load First
- **`references/sourcing-strategies.md`** — WHERE to find info, HOW to construct queries, multi-source triangulation, when to stop searching

### Load By Domain
- **`references/research-frameworks.md`** — Multi-layer analysis (5 layers), credibility evaluation, information control detection, triangulation methodology, iterative deepening, quality checklist
- **`references/output-templates.md`** — Format examples, selection guide, adaptive guidelines
- **`references/openclaw-architecture.md`** — OpenClaw Gateway/Agent Runtime architecture, heartbeat daemon, memory systems, model failover, sub-agents, Lobster workflows, session management, tool policy
- **`references/openclaw-skill-authoring.md`** — SKILL.md format, YAML frontmatter spec, three-tier loading, reference file patterns, ClawHub registry, security model, testing, publishing
- **`references/autonomy-patterns.md`** — Proactive agent patterns, heartbeat vs cron, memory persistence, compaction survival, task registries, workflow orchestration, degradation monitoring, multi-agent coordination
- **`references/adversarial-analysis.md`** — Suppression detection, institutional behavior, narrative flow analysis, information archaeology, inversion testing, incentive mapping

### Loading Strategy
```
Research request arrives →
  1. ALWAYS: sourcing-strategies.md
  2. IF complex multi-domain: research-frameworks.md
  3. IF OpenClaw/agent topic: openclaw-architecture.md + autonomy-patterns.md
  4. IF building skills: openclaw-skill-authoring.md
  5. IF institutional/suppression angle: adversarial-analysis.md
  6. IF custom output needed: output-templates.md
```

## OpenClaw Autonomy Integration

When this skill runs inside OpenClaw:
- **Heartbeat context:** Can be triggered by heartbeat to check research queues
- **Cron scheduling:** Schedule recurring research sweeps on monitored topics
- **Memory persistence:** Write research state to MEMORY.md / memory plugin
- **Sub-agent delegation:** Spawn focused sub-agents for parallel source gathering
- **Task registry:** Read TASKS.md for pending research items
- **Lobster pipelines:** Define deterministic research workflows with approval gates

## Quality Checklist (Before Completing)

- [ ] Loaded sourcing-strategies.md before searching
- [ ] Used appropriate tools for domain (SearXNG/Context7/web/filesystem)
- [ ] Scored ALL sources for credibility (0-10)
- [ ] Documented contradictions explicitly
- [ ] Checked for information control patterns (if applicable)
- [ ] Applied cross-domain pattern recognition
- [ ] Preserved uncertainty where warranted
- [ ] YAML frontmatter present with all fields
- [ ] Listed next investigation priorities
- [ ] Complete source bibliography with scores
- [ ] No forced conclusions — evidence speaks

## Remember

This methodology is universal. What changes: domain-specific sources and authorities. What stays constant: credibility scoring, pattern recognition, triangulation, epistemic humility.

**When K asks a question, the answer is a complete investigation, not a response.**
