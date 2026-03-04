---
name: virtual-reading-group
description: Orchestrate a multi-agent virtual academic reading group. Use when reading multiple papers, generating expert discussion notes, cross-examining positions across papers, and synthesizing integrated summaries with full citations. Triggers on requests to analyze academic literature, run paper discussions, create reading group sessions, or synthesize research across multiple sources. Supports 1-50 papers with configurable expert personas (1-4 papers work but produce simpler single-expert output).
---

# Virtual Reading Group

Orchestrate parallel expert agents to read papers, discuss findings, challenge each other's interpretations, and synthesize an integrated discussion document with traceable citations.

## Quick Start

Minimum inputs required:
1. **Research question** — the lens through which papers are analyzed
2. **Paper list** — paths to PDFs/text files, or paper descriptions for web lookup
3. **Output directory** — where all outputs are written

Optional inputs:
- Custom expert personas (default: see `references/default-personas.md`)
- Custom junior researcher persona
- Language preference (default: English)
- Number of experts (default: auto-calculated from paper count)

## Workflow Overview

The skill runs 4 sequential phases. Each phase must complete before the next begins.

| Phase | Agents | Input | Output |
|-------|--------|-------|--------|
| 1. Paper Reading | N experts (parallel) | Papers + research question | `{AuthorYear}_notes.md`, `{Expert}_session_summary.md` |
| 2. Junior Discussion | 1 junior researcher | All Phase 1 outputs | `{Junior}_discussion.md` |
| 3. Expert Responses | N experts (parallel) | Phase 2 output + other experts' summaries | `{Expert}_response_to_{Junior}.md` |
| 4. Synthesis | 1 synthesizer | All previous outputs | `Integrated_Discussion_Summary.md` |

**For detailed prompts and phase specifications**: Read `references/workflow.md`.

## Orchestration Procedure

> ⚠️ **Important:** The prompts below are **abbreviated summaries**. For full prompt templates that produce quality output, use `references/workflow.md`. The pseudocode blocks show orchestration structure — adapt to your actual sub-agent spawning mechanism.

### 1. Validate Inputs

```
- Confirm research question is specified
- Confirm paper list is non-empty
- Confirm output directory exists or create it
- Load personas from user input or references/default-personas.md
```

### 2. Calculate Expert Assignment

Determine number of experts and paper batches:

```
if paper_count <= 4:
    num_experts = 1
elif paper_count <= 10:
    num_experts = 2
elif paper_count <= 20:
    num_experts = min(4, ceil(paper_count / 5))
else:
    num_experts = min(8, ceil(paper_count / 5))

Distribute papers evenly across experts (max 5 per expert).

# ⚠️ Context contamination warning: assigning >5 papers per expert degrades
# note quality — later papers in the batch get shallower treatment as context
# fills up. Prefer 3-5 papers per agent for best results.
```

### 3. Execute Phase 1 — Paper Reading (Parallel)

For each expert, spawn a sub-agent with:
- **Label:** `expert-reader-{expert_name}`
- **Model:** opus (or sonnet for budget)
- **Core instructions:**
  - Read assigned papers through research question lens
  - Write notes using `references/paper-notes-template.md`
  - Save as `{output_dir}/{AuthorYear}_notes.md`
  - Write session summary with cross-cutting themes
  - **Critical:** Quote specific passages with section labels — all claims must be traceable

📄 **Full prompt template:** See `references/workflow.md` → Phase 1

**Wait for all Phase 1 agents to complete before proceeding.**

### 4. Execute Phase 2 — Junior Discussion (Single Agent)

Spawn single agent with:
- **Label:** `junior-discussion`
- **Model:** opus (required — needs strong reasoning)
- **Core instructions:**
  - Read all Phase 1 outputs (notes + summaries)
  - For each paper: summarize claims, pose challenging questions to each expert
  - Generate Grand Questions: 3 unsolved problems, 2 testable hypotheses, 2 methodological gaps
  - Reference specific passages — be intellectually provocative

📄 **Full prompt template:** See `references/workflow.md` → Phase 2

**Wait for Phase 2 to complete before proceeding.**

### 5. Execute Phase 3 — Expert Responses (Parallel)

For each expert, spawn a sub-agent with:
- **Label:** `expert-response-{expert_name}`
- **Model:** opus (recommended)
- **Core instructions:**
  - Read junior's discussion + other experts' summaries + own notes
  - Respond to each question directed at them (150-300 words per response)
  - Reference specific paper passages, engage with other expert's perspective
  - Respond to Grand Questions from their domain expertise
  - Be collegial but intellectually rigorous — disagree where warranted

📄 **Full prompt template:** See `references/workflow.md` → Phase 3

**Wait for all Phase 3 agents to complete before proceeding.**

### 6. Execute Phase 4 — Synthesis (Single Agent)

Spawn single agent with:
- **Label:** `synthesis`
- **Model:** opus (required — complex reasoning)
- **Core instructions:**
  - Read ALL files from Phases 1-3
  - Follow `assets/synthesis-template.md` structure
  - Organize by THEME, not by paper or speaker
  - Every claim attributed: `[Expert_A]`/`[Expert_B]`/`[Junior]` + `(PaperCode, §Section)`
  - Include: Points of Consensus, Points of Disagreement, Open Questions
  - **Synthesize, don't summarize** — find the intellectual threads

📄 **Full prompt template:** See `references/workflow.md` → Phase 4

### 7. Report Completion

List all generated files and provide a brief summary of the discussion themes.

## Iteration and Follow-up

### Deeper Discussion

If user wants experts to expand on specific points:
1. Spawn new expert response agent(s) with targeted follow-up questions
2. Re-run Phase 4 synthesis including the additional responses

### Second Round

For a full second round (new questions, new responses):
1. Rename Phase 2-4 outputs with round suffix (e.g., `Chen_discussion_r1.md`)
2. Re-run Phase 2 with instruction to build on previous round
3. Continue through Phases 3-4

### Recovery from Partial Run

If a phase fails:
1. Check error handling in `references/workflow.md`
2. Retry failed agent(s) individually  
3. Continue from last successful phase (outputs are saved incrementally)

## File Naming Conventions

| File Type | Pattern | Example |
|-----------|---------|---------|
| Paper notes | `{FirstAuthorLastName}{Year}_notes.md` | `Chen2024_notes.md` |
| Expert summary | `{ExpertLastName}_session_summary.md` | `Lin_session_summary.md` |
| Junior discussion | `{JuniorLastName}_discussion.md` | `Chen_discussion.md` |
| Expert response | `{ExpertLastName}_response_to_{JuniorLastName}.md` | `Lin_response_to_Chen.md` |
| Synthesis | `Integrated_Discussion_Summary.md` | — |

## Citation Requirements

**Enforce in all agent prompts:**

1. Every factual claim must reference a paper
2. Use format: `(AuthorYear, §Section)` or `(AuthorYear, p.X)`
3. Direct quotes must include section/page
4. Discussion claims must attribute speaker: `[Expert_A]`, `[Expert_B]`, `[Junior]`

### ⚠️ Anti-Fabrication Rule (Critical)

**Never fabricate citations.** If an agent cannot find the exact passage in the source text:
- Leave the field blank or write `<!-- source not found -->`
- Do NOT paraphrase and present it as a quote
- Do NOT infer what the paper "probably says"

Fabricated citations are worse than missing citations — they corrupt the knowledge base silently. **Accuracy > Coverage.**

### No Source = No Notes

If a paper has no PDF or markdown source available:
- Write a placeholder note with status `📭 未讀`
- Leave all content sections blank
- Do NOT attempt to write notes from memory or web search results

Only write substantive notes when the actual source document is accessible.

## Scaling Guidelines

| Papers | Experts | Batches | Estimated Time |
|--------|---------|---------|----------------|
| 1-6 | 1 | 1 | 15-20 min |
| 7-12 | 2 | 2 | 20-30 min |
| 13-24 | 3-4 | 3-4 | 30-45 min |
| 25-50 | 4-8 | 5-8 | 45-90 min |

## Customization

### Custom Personas

Replace default personas by providing:

```markdown
Expert A: Dr. [Name], [Role]. Background in [X]. 
Emphasizes [methodology/perspective]. Skeptical of [Y].
Tone: [collegial/rigorous/provocative].

Expert B: Dr. [Name], [Role]. Background in [X].
...
```

See `references/default-personas.md` for complete templates.

### Language

Pass the `language` parameter when invoking the orchestration:
- All agent prompts include `Language: {language}` instruction
- Agents read papers and write outputs in the specified language  
- Default: English

Example: "Run the reading group in Japanese" → adds `Language: Japanese` to all phase prompts.

### Model Selection

Model choice significantly impacts output quality and cost:

| Configuration | Phases | Quality | Cost | Use When |
|--------------|--------|---------|------|----------|
| **Full opus** | All phases use opus | Highest | $$$ | Publication-quality analysis, complex papers |
| **Mixed** | Phase 1: sonnet, Phases 2-4: opus | High | $$ | Good balance — reading is less reasoning-intensive |
| **Budget** | All phases use sonnet | Medium | $ | Quick exploration, simpler papers |

**Recommendations:**
- **Phase 2 (Junior Discussion)** benefits most from opus — requires synthesizing multiple papers and generating non-obvious questions
- **Phase 4 (Synthesis)** also benefits from opus — thematic organization requires complex reasoning
- **Phase 1 (Reading)** can use sonnet if papers aren't highly technical
- **Phase 3 (Responses)** can use sonnet if questions are straightforward

## Integration

This skill is standalone but works well with paper collection workflows:
- **literature-manager** or similar skills: Use to gather and organize papers first, then pass the collection to virtual-reading-group
- **PDF extraction tools**: Pre-extract text from PDFs if agents have trouble reading them directly

## References

- `references/workflow.md` — Detailed phase specifications and full prompt templates
- `references/default-personas.md` — Ready-to-use expert and junior researcher personas
- `references/paper-notes-template.md` — Template for individual paper notes

## Assets

- `assets/synthesis-template.md` — Structure for the final integrated discussion summary
