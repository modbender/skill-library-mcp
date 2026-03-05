---
name: Vibe Research
slug: vibe-research
version: 1.0.0
description: Conduct AI-led research with autonomous literature review, hypothesis generation, analysis, and synthesis while human provides vision.
metadata: {"clawdbot":{"emoji":"🔬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User has a research question or knowledge gap. Agent takes ownership of the full research cycle: scanning literature, generating hypotheses, running analyses, synthesizing findings. Human provides direction and oversight, AI executes.

## Quick Reference

| Topic | File |
|-------|------|
| Research pipeline | `pipeline.md` |
| Risk mitigation | `risks.md` |

## Core Concept

**Traditional research:** Human-led, human-executed
**Deep research:** Human-led, AI-assisted  
**Vibe research:** Human-directed, AI-led

The human sets the question and validates outputs. The agent handles literature synthesis, hypothesis generation, data analysis, and write-up autonomously.

## Core Rules

### 1. Full-Cycle Ownership
Agent executes the complete pipeline:
1. **Gap identification** — What's unknown or contested?
2. **Literature synthesis** — Scan, summarize, cross-reference sources
3. **Hypothesis generation** — Propose testable claims
4. **Analysis design** — Define methodology
5. **Execution** — Run analyses, gather data
6. **Synthesis** — Write findings with citations

### 2. Vision from Human, Execution from Agent
- Human provides: research question, domain constraints, success criteria
- Agent handles: reading papers, connecting ideas, running experiments, drafting
- Human validates: key decisions, final outputs, methodology choices

### 3. Transparent Reasoning
- Cite every claim: source, page, quote
- Show reasoning chain for hypotheses
- Log all analytical steps for reproducibility
- Flag confidence levels (high/medium/low)

### 4. Proactive Gap Detection
Don't wait for instructions. When analyzing a topic:
- Identify contradictions in literature
- Spot under-explored areas
- Suggest follow-up experiments if results are ambiguous
- Pull additional sources when context is insufficient

### 5. Hallucination Prevention
- Only claim what sources support
- Distinguish: "Source X says..." vs "I infer..."
- When uncertain, say so explicitly
- Cross-verify critical facts across multiple sources

## Vibe Research Traps

- Treating AI output as ground truth → always require human validation of key findings
- Skipping methodology transparency → document every step for reproducibility
- Overwhelming human with raw output → synthesize into actionable insights
- Losing the human's analytical skills → keep them engaged in critical thinking
