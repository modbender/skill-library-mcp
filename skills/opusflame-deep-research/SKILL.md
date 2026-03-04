---
name: deep-research
description: "Autonomous multi-model deep research with framework-driven reasoning. Spawns 4 parallel model agents (Gemini 2.5 Pro, o3, Opus, MiniMax), each applies best-practice frameworks to the question, then merges into a cross-validated final report. Use when: (1) user asks for in-depth research, (2) 'research X' or 'deep dive on X', (3) complex questions requiring multiple sources. NOT for: simple factual lookups."
---

# Deep Research (Multi-Model + Framework-Driven)

Autonomous research system that runs 4 AI models in parallel, each applying relevant analytical frameworks, then cross-validates and merges findings into a comprehensive cited report.

## Architecture

```
User Question
     │
     ▼
┌─ Phase 0: Framework Selection ─┐
│  Identify best-practice         │
│  framework(s) for this question │
└────────────┬────────────────────┘
             │
     ┌───────┼───────┐───────┐
     ▼       ▼       ▼       ▼
  Gemini    o3     Opus   MiniMax
  2.5 Pro         4       M2.5
  (search  (deep  (nuance (China/
  heavy)   logic) +balance)alt view)
     │       │       │       │
     └───────┼───────┘───────┘
             ▼
      Phase 5: Merge & Cross-Validate
             │
             ▼
       Final Report (PDF)
```

## Phase 0: Framework Selection (MANDATORY — before any research)

Before researching, ask: **"Is there a best-practice framework for answering this type of question?"**

### Framework Lookup Table

| Question Type | Frameworks to Apply |
|---|---|
| **Competitive strategy** | Porter's Five Forces, 7 Powers (Helmer), Schwerpunkt/High Ground (Packy), SWOT |
| **Market entry / sizing** | TAM/SAM/SOM, Blue Ocean Strategy, Jobs-to-be-Done |
| **Business model evaluation** | Business Model Canvas, Unit Economics, Ramp vs Route test (point solution vs platform?) |
| **Investment / valuation** | DCF, Comparable Analysis, Venture method, Power Law thesis |
| **Product strategy** | JTBD, Kano Model, Value Prop Canvas, Hook Model |
| **Growth / GTM** | AARRR Pirate Metrics, Bullseye Framework, STP (Segmentation-Targeting-Positioning) |
| **Technology assessment** | Gartner Hype Cycle, Wardley Maps, Build vs Buy matrix |
| **Risk analysis** | Pre-Mortem, FMEA, Scenario Planning |
| **Organizational / ops** | OKR analysis, RACI, Theory of Constraints |
| **Pricing** | Van Westendorp, Conjoint, Value-based pricing framework |
| **Industry analysis** | Value Chain Analysis, Industry Lifecycle, Winner-Takes-More thesis |
| **Person / hiring** | Track Record Analysis, Reference Triangle, Founder-Market Fit |

**If a framework applies:**
- Include it in the prompt to each model
- Structure the model's analysis around the framework's components
- The final report should explicitly reference which framework(s) were used and why

**If no standard framework applies:**
- State "No standard framework identified — using first-principles analysis"
- Each model reasons from first principles with explicit assumptions stated

## Phase 1: Decompose (30s)

Break the topic into 5-8 research sub-questions. Think like an investigative journalist:
- What are the key facts?
- What are different perspectives/sources?
- What's the timeline/history?
- What data/evidence exists?
- What are the unknowns or controversies?

## Phase 2: Spawn 4 Model Agents (Parallel)

Spawn 4 sub-agents using `sessions_spawn`, each with a different model:

```
Model 1: gemini       (google/gemini-2.5-pro)  — Search-heavy, broad coverage
Model 2: o3           (openai/o3)              — Deep logical reasoning, contrarian
Model 3: opus         (anthropic/claude-opus-4-6) — Nuanced, balanced synthesis
Model 4: minimax      (minimax/MiniMax-M2.5)   — Alternative perspectives, China/grey-area
```

### Prompt Template for Each Model

```
## Research Task
[Topic]

## Framework
You MUST structure your analysis using: [Framework Name]
Apply each component of the framework systematically to the topic.
If data is missing for a component, note it explicitly.

## Sub-Questions
[List of 5-8 sub-questions]

## Instructions
1. Use web_search extensively (minimum 10 unique searches)
2. Use web_fetch to read full articles for key sources
3. Cross-reference claims across 2+ sources
4. Structure findings around the framework components
5. Flag disagreements, unknowns, and low-confidence claims
6. Minimum 15 unique source URLs
7. Output format: markdown with inline citations [1][2]...
8. End with a Sources section listing all URLs

## Quality Rules
- Every factual claim needs a source
- Prefer primary sources (filings, official reports) over secondary
- Note source freshness — flag anything >6 months old
- Include opposing viewpoints
- State confidence level (high/medium/low) for key conclusions
```

### Model-Specific Instructions

- **Gemini**: "You are the primary search engine. Cast the widest net. Find obscure sources others would miss. Prioritize data and numbers."
- **o3**: "You are the deep reasoner. Challenge assumptions. Look for logical flaws in conventional wisdom. Apply the framework with maximum rigor. If the consensus is wrong, explain why."
- **Opus**: "You are the synthesizer. Balance multiple perspectives fairly. Identify nuance others miss. Connect dots across disciplines."
- **MiniMax**: "You are the alternative perspective agent. Consider non-Western viewpoints, grey areas, unconventional strategies. What would a Chinese entrepreneur or contrarian investor do differently?"

## Phase 3: Wait for Completion

All 4 models run in parallel via `sessions_spawn` with `mode="run"`. Do NOT poll in a loop — they auto-announce when done.

## Phase 4: Collect Individual Reports

Save each model's output:
```
memory/research/[topic]-gemini-[date].md
memory/research/[topic]-o3-[date].md
memory/research/[topic]-opus-[date].md
memory/research/[topic]-minimax-[date].md
```

## Phase 5: Cross-Validate & Merge

This is the most critical phase. The primary agent (you) must:

### 5a. Agreement Matrix
Create a matrix of key claims and which models agree/disagree:

```markdown
| Claim | Gemini | o3 | Opus | MiniMax | Confidence |
|-------|--------|----|----|---------|------------|
| [claim 1] | ✅ | ✅ | ✅ | ❌ | High (3/4) |
| [claim 2] | ✅ | ❌ | ✅ | ✅ | High (3/4) |
| [claim 3] | ✅ | ✅ | ❓ | ❓ | Medium (2/4) |
```

### 5b. Conflict Resolution
For each disagreement:
- Identify the root cause (different data? different logic? different framework interpretation?)
- Check which model has the stronger source
- If genuinely uncertain, present both sides in the final report

### 5c. Framework Synthesis
- Map findings back to the framework structure
- Ensure every framework component has been addressed
- Note which components had strong consensus vs. disagreement

### 5d. Error Catching
From experience, models commonly get wrong:
- Platform-specific limits (posting frequency, API limits)
- Pricing (especially for niche tools — often 10-30x off)
- Regulatory details
- Recency of data

**Verify any quantitative claim that only one model makes.**

## Phase 6: Final Report

```markdown
# [Topic] — Deep Research Report

**Framework Used**: [Name] — [why this framework]
**Models**: Gemini 2.5 Pro, o3, Opus 4, MiniMax M2.5
**Date**: [date]
**Total Searches**: [count across all models]

## Executive Summary
3-5 sentence overview. Note consensus level.

## Framework Analysis

### [Framework Component 1]
Analysis with model consensus noted. [1][2]

### [Framework Component 2]
...

## Key Findings (Beyond Framework)
Discoveries that don't fit neatly into the framework.

## Model Disagreements
Where models diverged and why.

## Agreement Matrix
[The table from 5a]

## Data & Evidence
Tables, numbers, comparisons.

## Risks / Unknowns
What we couldn't confirm. Low-confidence areas.

## Conclusion & Recommendations
Actionable takeaways ranked by confidence.

## Sources
[1] Title — URL
[2] ...
```

## Phase 7: Deliver

1. Save final report to `memory/research/[topic]-终极版-[date].md`
2. Generate PDF via pymupdf and save to `~/.openclaw/media/outbound/`
3. Send PDF to user via message tool

## Quality Standards

- **Minimum sources**: 15 unique URLs per model (60+ total across 4 models)
- **Source diversity**: No more than 3 citations from same domain per model
- **Freshness**: Prefer sources < 6 months old; flag older data
- **Cross-validation**: Key claims must appear in 2+ models' findings
- **Framework compliance**: Every framework component must be addressed
- **Confidence scoring**: High (3-4 models agree + strong sources), Medium (2 models or weak sources), Low (1 model or no source)
- **No hallucination**: Every factual claim must have a source

## Adaptation by Topic Type

### Financial / Stock Research
- Frameworks: DCF, Comparable Analysis, Power Law
- Check SEC/regulatory filings, earnings transcripts
- Include key metrics (revenue, margins, P/E, debt)
- See `references/financial-research.md`

### Market / Industry Research
- Frameworks: Porter's Five Forces, TAM/SAM/SOM, 7 Powers
- Competitive landscape, key players, market share
- Apply Winner-Takes-More thesis where relevant

### Strategy / Business Model
- Frameworks: Schwerpunkt/High Ground, Business Model Canvas, JTBD
- Identify the constraint, the scarce asset, expansion path
- Compare to historical precedents (Rockefeller, Ramp, etc.)

### Technical / Product Research
- Frameworks: Wardley Maps, Build vs Buy, Gartner Hype Cycle
- Architecture, benchmarks, alternatives matrix
- Community sentiment (GitHub, HN, Reddit)
