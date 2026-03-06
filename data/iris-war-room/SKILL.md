---
name: war-room
description: "Run adversarial multi-agent war-room evaluations for any strategic decision. Spawns 5 parallel subagents (Analyst, Guardian, Treasurer, Builder, Strategist) to challenge a proposal from different angles, then synthesizes a GO/NO-GO/REWORK ruling. Use when: (1) evaluating proposals that need multi-perspective stress-testing, (2) making go/no-go decisions on investments, products, hires, or architecture, (3) any decision where adversarial challenge improves quality. Supports finance, product, engineering, and hiring domains. NOT for: simple questions, routine tasks, or decisions that do not need formal evaluation."
---

# War Room

Structured adversarial evaluation of any strategic proposal using 5 parallel subagents.

## Roles

| Role | Focus | Must Answer |
|------|-------|-------------|
| **Analyst** | Data, math, quantitative modeling | "Show the numbers and formulas." |
| **Guardian** | Risk, failure modes, worst cases | "If [X] fails, what is the maximum loss?" |
| **Treasurer** | Resource efficiency, ROI, costs | "Per $1 invested, what is the expected return?" |
| **Builder** | Execution feasibility, timeline, tooling | "What is the time/cost/risk to implement?" |
| **Strategist** | Strategic fit, alternatives, long-term vision | "How does this fit the long-term strategy?" |

## 4-Phase Flow

### Phase 1: Stance

State the proposal, key assumptions, and GO/NO-GO criteria.

### Phase 2: Spawn Subagents

Spawn all 5 in parallel with `sessions_spawn`, `mode: "run"`.

**Token optimization** (recommended for large proposals):
1. Write proposal data to a temp file: `/tmp/rt_{topic}.md`
2. Keep task prompts small (~500 tokens): role definition + deliverables + "Read /tmp/rt_{topic}.md for full context"
3. Subagents use the `read` tool to load the file themselves

This cuts input tokens by ~95% vs inlining all data in each prompt.

**If the proposal is short** (under 1500 words), inline it directly in the task prompt.

Label pattern: `{role}_{topic}_{YYYYMMDD}`

### Phase 3: Collect and Critique

Wait for all 5 (auto-announced). Then apply the Critic lens:
- Consensus (4/5+ agree)
- Disputes and contradictions
- Stress-test: "If [X] fails, the entire logic collapses."
- Blind spots no agent raised

### Phase 4: Ruling

Output document must include ALL sections:

1. Participants table (role, label, runtime, key contribution)
2. Per-agent summaries with numbers
3. Consensus points
4. Disputes with explicit rulings and rationale
5. Final plan with concrete numbers
6. Scenario projections (bull/base/bear with probabilities)
7. Retained doubts (mandatory: intellectual honesty)
8. Ruling: GO / NO-GO / REWORK + conditions
9. Task list: P0/P1/P2 with owners and deadlines

Audit ID format: `RT{N}-{TOPIC}-{YYYYMMDD}`

## Domain Adaptation

The 5 roles adapt to any domain. See [references/domains.md](references/domains.md) for domain-specific mandatory questions and prompt guidance for: Finance, Product, Engineering, Hiring.

## Role Details and Prompt Templates

See [references/roles.md](references/roles.md) for full role definitions.
See [references/prompts.md](references/prompts.md) for spawn patterns and ruling templates.

## Post-Ruling Checklist

1. Write ruling to a file and commit
2. Store key decisions to long-term memory with audit ID
3. Update daily log
