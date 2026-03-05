# Research Output Templates

Flexible templates for any research domain. ALL outputs are Obsidian-ready .md files
with YAML frontmatter unless explicitly overridden by K.

## Table of Contents
1. Format Selection Guide
2. Standard Research Report (Default)
3. Technical Architecture Analysis
4. OpenClaw Skill Specification
5. Timeline Format
6. Comparative Analysis
7. Synchronicity Documentation
8. Quick Brief
9. YAML Frontmatter Reference
10. Adaptive Guidelines

---

## 1. Format Selection Guide

| Research Type | Format | When |
|--------------|--------|------|
| General investigation | Standard Report | Most research tasks |
| Technical system analysis | Architecture Analysis | OpenClaw, frameworks, systems |
| Building/evaluating skills | Skill Specification | Authoring OpenClaw skills |
| Sequential events | Timeline | Tracking developments over time |
| Side-by-side evaluation | Comparative Analysis | Comparing tools, approaches, claims |
| Meaningful coincidences | Synchronicity Doc | Objective + subjective significance |
| Quick synthesis | Quick Brief | Time-constrained, simple queries |
| Unique requirements | Custom | Build what the research needs |

**Default: Standard Research Report.** Scale up to Architecture Analysis for technical depth.

## 2. Standard Research Report (Default)

```markdown
---
title: "[Topic] Research Analysis"
date: YYYY-MM-DD
status: complete|ongoing|stalled
confidence: high|medium|low|mixed
sources: [count]
words: [approximate]
methodology: k-deep-research-v2
tags: [domain, subtopic, methodology-used]
---

# [Topic] Research Analysis

## Executive Synthesis
[2-3 paragraphs: Key findings, pattern detection, credibility assessment, open questions.
This is for quick reference — NOT a replacement for the depth below.]

## Part I: [Major Theme]

### [Section 1.1]
[Findings with inline source citations and credibility scores]
[Source: description (credibility X/10)]

### [Section 1.2]
[Cross-domain connections, anomalies, contradictions]

## Part II: [Major Theme]
[Scale sections to complexity — add Parts/Sections/Subsections as needed]

## Pattern Analysis
### Temporal Patterns
[Coordinated timing, cycles, sequences detected]

### Actor Patterns
[Coordination, messaging alignment, institutional behavior]

### Information Flow
[What's amplified vs. suppressed, by whom, through what channels]

### Anomalies
[Unexplained observations, systematic gaps, missing evidence]

## Source Analysis
### High Credibility (8-10)
- [Source] — [description] — [score/10]

### Medium Credibility (5-7)
- [Source] — [description] — [score/10]

### Low Credibility (1-4)
- [Source] — [description] — [score/10]

### Flagged (0)
- [If applicable: coordinated narrative, active suppression indicators]

## Open Questions
[What remains unresolved — these become future investigation vectors]
1. [Question + what would answer it]
2. [Question + where to look]

## Future Investigation Vectors
[Specific next steps, not vague "more research needed"]

## Complete Source Bibliography
[All sources organized by credibility tier, with URLs where available]
```

## 3. Technical Architecture Analysis

For OpenClaw, frameworks, systems, and technical deep dives:

```markdown
---
title: "[System] Architecture Analysis"
date: YYYY-MM-DD
status: complete|ongoing
confidence: high|medium|low|mixed
sources: [count]
words: [approximate]
methodology: k-deep-research-v2
tags: [system-name, architecture, specific-components]
---

# [System] Architecture Analysis

## Executive Synthesis
[Key architectural findings, critical decisions, failure modes]

## Architecture Overview
### Component Map
[High-level system diagram in text/mermaid]

### Data Flow
[How information moves through the system]

### Control Flow
[How decisions/actions propagate]

## Component Deep Dives

### [Component 1]
**Purpose:** [What it does]
**Implementation:** [How it works]
**Configuration:** [Key settings]
**Failure Modes:** [What can go wrong]
**Community Experience:** [Real-world deployment patterns]

### [Component 2]
[...]

## Integration Patterns
[How components interact, API surfaces, event flows]

## Known Issues & Edge Cases
| Issue | Impact | Workaround | Status |
|-------|--------|------------|--------|
| [Issue] | [Severity] | [Mitigation] | [Open/Fixed] |

## Production Deployment Pattern
[Recommended configuration for production use]

## Capability Matrix
| Capability | Status | Configuration | Notes |
|-----------|--------|---------------|-------|
| [Feature] | ✅/⚠️/❌ | [How to enable] | [Caveats] |

## Security Considerations
[Attack surfaces, mitigation strategies, unsolved problems]

## Open Questions & Future Vectors
[Specific technical questions that need resolution]

## Source Bibliography
[Credibility-scored sources]
```

## 4. OpenClaw Skill Specification

For designing and documenting new OpenClaw skills:

```markdown
---
title: "[Skill Name] — OpenClaw Skill Specification"
date: YYYY-MM-DD
status: draft|tested|production
skill-version: "1.0.0"
tags: [openclaw, skill, domain-tags]
---

# [Skill Name] Specification

## Purpose
[What this skill teaches the agent to do]

## Trigger Description
[The description field — how users ask for this task]

## YAML Frontmatter
```yaml
---
name: skill-name
description: "[trigger phrase matching user language]"
version: "1.0.0"
metadata: { "openclaw": { "emoji": "🔬", "requires": { "bins": [], "env": [], "config": [] } } }
---
```

## Body Structure (Tier 2)
[Outline of SKILL.md body — what goes in, what points to references]

## Reference Files (Tier 3)
| File | Purpose | When Loaded |
|------|---------|-------------|
| `references/[file].md` | [Content description] | [Trigger condition] |

## Operations
### [Operation Category]
- [What the agent does]
- [Parameters needed]
- [Expected output]

## Guardrails
- [What NOT to do]
- [Error handling]
- [When to ask human]

## Testing Plan
- [ ] Description triggers on expected queries
- [ ] Simple task works from body alone
- [ ] References load correctly
- [ ] Sandbox compatibility verified
- [ ] Dependencies documented accurately

## Deployment
- [ ] Target: workspace | managed | ClawHub
- [ ] Security review complete
- [ ] Multi-agent sharing plan (if applicable)
```

## 5. Timeline Format

```markdown
---
title: "[Topic] Timeline"
date: YYYY-MM-DD
status: complete|ongoing
confidence: high|medium|low|mixed
sources: [count]
tags: [timeline, domain-tags]
---

# [Topic] Timeline

## Summary
[Brief overview of timeline scope and significance]

## [Date/Period]: [Event Name]
**What happened:** [Primary source description]
**Significance:** [Why this matters]
**Pattern connections:** [Links to other events]
**Source:** [Source with credibility score]

## [Date/Period]: [Event Name]
[...]

## Pattern Analysis
[Temporal patterns, coordination indicators, gaps]

## Sources
[Credibility-scored bibliography]
```

## 6. Comparative Analysis

```markdown
---
title: "[Subject A] vs [Subject B] — Comparative Analysis"
date: YYYY-MM-DD
status: complete
confidence: high|medium|low|mixed
sources: [count]
tags: [comparison, subjects]
---

# [Subject A] vs [Subject B]

## Executive Summary
[Key differentiators and recommendation if applicable]

## Comparison Matrix

| Dimension | Subject A | Subject B | Assessment |
|-----------|-----------|-----------|------------|
| [Dimension] | [Finding] | [Finding] | [Winner/Trade-off] |

## Detailed Analysis

### [Dimension 1]
**Subject A:** [Detailed findings with sources]
**Subject B:** [Detailed findings with sources]
**Assessment:** [Analysis with credibility weighting]

### [Dimension 2]
[...]

## Use Case Mapping
| Use Case | Recommended | Why |
|----------|-------------|-----|
| [Use case] | [A or B] | [Reasoning] |

## Sources
[Credibility-scored bibliography]
```

## 7. Synchronicity Documentation

```markdown
---
title: "Pattern: [Name]"
date: YYYY-MM-DD
status: documented
confidence: mixed
tags: [synchronicity, pattern-type]
---

# Pattern: [Name]

## Observable Elements (OBJECTIVE)
**Temporal:** [Dates, cycles, anniversaries]
**Symbolic:** [Recurring themes, archetypal patterns]
**Contextual:** [Circumstances, environment]
**Evidence:** [What can be verified]

## Personal Significance (SUBJECTIVE)
[Why this matters to K specifically]
[What it reveals about ongoing patterns]

## Pattern Analysis
[Connections WITHOUT forced interpretation]
[Multiple possible meanings acknowledged]
[Epistemological stance: document without concluding]

## Cross-References
[Links to other documented patterns]
[Adjacent domain connections]

## Further Investigation
[What would strengthen or weaken this pattern]
```

## 8. Quick Brief

```markdown
# [Topic] — Quick Brief

**Key Findings:**
1. [Finding] — [source credibility X/10]
2. [Finding] — [source credibility Y/10]
3. [Finding] — [source credibility Z/10]

**Confidence Assessment:**
- High confidence: [What we know reliably]
- Medium confidence: [What seems likely]
- Low/Speculative: [What's uncertain]

**Pattern Detection:** [If patterns detected, note briefly]

**Next Steps:**
1. [Immediate priority]
2. [Follow-up investigation]

**Top Sources:** [3-5 with scores]
```

## 9. YAML Frontmatter Reference

**Required fields for ALL reports:**
```yaml
---
title: "string"
date: YYYY-MM-DD
status: complete|ongoing|stalled
confidence: high|medium|low|mixed
sources: integer
tags: [list, of, tags]
---
```

**Optional fields (add when relevant):**
```yaml
words: integer (approximate)
methodology: k-deep-research-v2
skill-version: "2.0.0"
related: [[other-note-title]]
supersedes: [[previous-investigation]]
monitoring: true|false
next-review: YYYY-MM-DD
```

**Tag Conventions:**
- Domain tags: `openclaw`, `consciousness`, `uap`, `institutional`, `technical`
- Method tags: `timeline`, `comparison`, `architecture`, `adversarial`
- Status tags: `monitoring`, `stalled`, `needs-depth`
- Priority: concepts first, then domains, then methods

## 10. Adaptive Guidelines

- Templates are starting points, NOT straightjackets
- Adapt structure to what the research reveals
- Credibility scoring is MANDATORY (always)
- Preserve uncertainty and contradictions
- Format serves the investigation, not vice versa
- If research needs unique structure, BUILD IT
- LENGTH IS A FEATURE — exhaust the topic
- Every claim supported, every thread followed
- "Let me know if you want more detail" = FAILURE
- Give ALL the detail upfront

**The methodology matters more than the template.**
