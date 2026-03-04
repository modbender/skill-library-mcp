# Workflow Specification

Detailed specifications for each phase of the virtual reading group.

## Table of Contents

1. [Phase 1: Paper Reading](#phase-1-paper-reading)
2. [Phase 2: Junior Discussion](#phase-2-junior-discussion)
3. [Phase 3: Expert Responses](#phase-3-expert-responses)
4. [Phase 4: Synthesis](#phase-4-synthesis)
5. [Phase Coordination](#phase-coordination)
6. [Error Handling](#error-handling)

---

## Phase 1: Paper Reading

### Purpose

Each expert reads their assigned batch of papers and produces:
1. Individual paper notes (one file per paper)
2. A session summary covering all papers in their batch

### Agent Configuration

```yaml
role: expert-reader
model: opus (recommended) or sonnet
parallel: true (all experts run simultaneously)
timeout: 30 minutes per expert
```

### Input Files

- Paper files (PDF, text, or markdown)
- Research question (string)
- Expert persona description
- Paper notes template (from `references/paper-notes-template.md`)

### Full Prompt Template

```markdown
# Expert Reading Session

You are {expert_persona_full}.

## Your Task

Read and analyze the following papers through the lens of this research question:

**Research Question:** {research_question}

## Your Assigned Papers

{paper_list_with_paths}

## Instructions

### For Each Paper

1. **Read thoroughly** — understand the core argument, methods, and findings
2. **Take structured notes** following this template:

---
# {Paper Title}

## Metadata
- **Authors:** 
- **Year:** 
- **Venue:** 
- **DOI/Link:** 

## Core Argument
[1-2 paragraphs: What is the paper's main thesis?]

## Key Findings
[Bullet points with section references]
- Finding 1 (§Section, p.X)
- Finding 2 (§Section, p.X)

## Methods
[Brief description of methodology]

## Notable Passages
> "Direct quote" (§Section, p.X)

[Why this passage matters]

## Relevance to Research Question
[How does this paper address: {research_question}?]

## Questions Raised
- Question 1
- Question 2
---

3. **Save** as `{output_dir}/{FirstAuthorLastName}{Year}_notes.md`

### After All Papers

Write your session summary:

```markdown
# {Your Name} — Session Summary

## Paper Summaries

### {Paper 1 Title} ({AuthorYear})
[1 paragraph: key contribution + relevance to research question]

### {Paper 2 Title} ({AuthorYear})
[...]

## Cross-Cutting Themes

### Theme 1: {Theme Name}
[Which papers address this? How do they relate?]

### Theme 2: {Theme Name}
[...]

## Preliminary Observations
[Your initial synthesis — what patterns emerge? What tensions exist?]
```

Save as `{output_dir}/{YourLastName}_session_summary.md`

## Critical Requirements

- **Citation granularity:** Every claim must reference a specific section or page
- **Direct quotes:** Include at least 2-3 notable passages per paper
- **Research question focus:** Evaluate each paper's relevance to the research question
- **Intellectual honesty:** Note limitations, gaps, or weaknesses you observe
```

### Output Files

| File | Content |
|------|---------|
| `{AuthorYear}_notes.md` | Individual paper notes (one per paper) |
| `{ExpertLastName}_session_summary.md` | Expert's synthesis of their batch |

---

## Phase 2: Junior Discussion

### Purpose

A junior researcher reads all expert outputs and generates challenging questions that probe disagreements, assumptions, and gaps.

### Agent Configuration

```yaml
role: junior-discussant
model: opus (required — needs strong reasoning)
parallel: false (single agent)
timeout: 20 minutes
```

### Input Files

- All `{AuthorYear}_notes.md` files from Phase 1
- All `{ExpertLastName}_session_summary.md` files from Phase 1
- Research question
- Junior persona description

### Full Prompt Template

```markdown
# Junior Researcher Discussion

You are {junior_persona_full}.

## Context

You have just attended a reading group where senior researchers presented papers. Now it's your turn to synthesize, challenge, and probe their analyses.

**Research Question:** {research_question}

## Your Reading

Read all files in `{output_dir}`:
- Paper notes: {list_of_note_files}
- Expert summaries: {list_of_summary_files}

## Your Task

Write a discussion document that challenges the experts and identifies deeper questions.

### Document Structure

```markdown
# Discussion Document — {Your Name}

## Overview
[1 paragraph: What are the key themes and tensions you see across all papers?]

---

## Paper-by-Paper Discussion

### {Paper 1 Title} ({AuthorYear})

**Summary of Expert Interpretations:**
[What did the experts say about this paper?]

**→ Question to {Expert_A}:**
[A challenging question that probes their interpretation, asks for clarification, or points out a potential gap. Be specific — reference their exact claims.]

**→ Question to {Expert_B}:**
[A different angle — perhaps methodological, theoretical, or about connections to other papers.]

---

[Repeat for each paper]

---

## Grand Questions

### Major Unsolved Problems
1. [Problem that emerges from reading all papers]
2. [Another unresolved issue]
3. [A third problem]

### Testable Hypotheses
1. [A hypothesis that could resolve a disagreement between papers or experts]
2. [Another testable claim]

### Methodological Gaps
1. [What methods are missing from this literature?]
2. [What data would we need?]
```

Save as `{output_dir}/{YourLastName}_discussion.md`

## Guidelines

- **Be intellectually provocative** — your questions should make experts think
- **Reference specific passages** — cite paper notes and expert summaries
- **Find tensions** — where do papers or experts disagree?
- **Think across papers** — what emerges from reading them together?
- **Stay humble but curious** — you're learning, but you see things fresh eyes see

## Question Quality Criteria

Good questions:
- Challenge assumptions
- Point out contradictions
- Ask "why not X?"
- Connect disparate findings
- Probe methodological choices

Avoid:
- Questions answerable by re-reading
- Pure clarification requests
- Softball questions
```

### Output Files

| File | Content |
|------|---------|
| `{JuniorLastName}_discussion.md` | Cross-paper discussion with targeted questions |

---

## Phase 3: Expert Responses

### Purpose

Each expert responds to the junior researcher's questions, engaging with both the questions and the other expert's perspective.

### Agent Configuration

```yaml
role: expert-responder
model: opus (recommended)
parallel: true (all experts run simultaneously)
timeout: 20 minutes per expert
```

### Input Files

- `{JuniorLastName}_discussion.md` from Phase 2
- Other experts' `{ExpertLastName}_session_summary.md` files
- Their own paper notes from Phase 1
- Expert persona description

### Full Prompt Template

```markdown
# Expert Response Session

You are {expert_persona_full}.

## Context

A junior researcher has posed challenging questions about the papers you and your colleagues presented. Time to respond.

**Research Question:** {research_question}

## Your Reading

1. Junior discussion: `{output_dir}/{JuniorLastName}_discussion.md`
2. Other expert's summary: `{output_dir}/{OtherExpertLastName}_session_summary.md`
3. Your own notes from the reading session

## Your Task

Write thoughtful responses to each question directed at you.

### Document Structure

```markdown
# {Your Name} — Response to {Junior Name}

## Paper-Specific Responses

### {Paper 1 Title} ({AuthorYear})

**{Junior Name} asked:**
> [Quote the exact question from the discussion document]

**Response:**
[REQUIRED: 150-300 words per response. Be substantive:
- Directly address the question
- Reference specific paper passages
- Acknowledge valid critiques
- Offer your expert perspective
- Engage with what the other expert said if relevant]

---

[Repeat for each question directed at you]

---

## Grand Question Responses

### On: {Quote the grand question}

**Response:**
[Your perspective as {your domain} expert. How does your expertise inform this question?]

[Repeat for relevant grand questions]

---

## Additional Thoughts

[Optional: Any cross-cutting observations that emerged from engaging with these questions? Points of agreement/disagreement with the other expert?]
```

Save as `{output_dir}/{YourLastName}_response_to_{JuniorLastName}.md`

## Response Requirements

- **Each question response:** 150-300 words minimum (not shorter)
- **Each Grand Question response:** 100-200 words
- **Total document:** Must be substantive, not brief

## Guidelines

- **Be collegial but rigorous** — disagree respectfully where warranted
- **Engage substantively** — no hand-waving or deferrals
- **Reference evidence** — cite specific papers and passages
- **Acknowledge uncertainty** — where you don't know, say so
- **Build on others** — reference and respond to the other expert's views
```

### Output Files

| File | Content |
|------|---------|
| `{ExpertLastName}_response_to_{JuniorLastName}.md` | Expert's responses to junior's questions |

---

## Phase 4: Synthesis

### Purpose

Create an integrated discussion summary organized by theme, with full attribution and citations.

### Agent Configuration

```yaml
role: synthesizer
model: opus (required — complex reasoning)
parallel: false (single agent)
timeout: 30 minutes
```

### Input Files

- All files from Phases 1-3
- Synthesis template from `assets/synthesis-template.md`

### Full Prompt Template

```markdown
# Synthesis Agent

You are creating the final integrated discussion summary for this reading group.

**Research Question:** {research_question}

## Your Reading

Read ALL files in `{output_dir}`:
- Paper notes: {list_of_note_files}
- Expert summaries: {list_of_summary_files}
- Junior discussion: {junior_discussion_file}
- Expert responses: {list_of_response_files}

## Your Task

Synthesize everything into a thematic discussion document.

### Critical Rules

1. **Organize by THEME, not by paper or speaker**
2. **Every claim must be attributed:**
   - Speaker: `[Lin]`, `[Webb]`, `[Chen]`
   - Paper: `(AuthorYear, §Section)`
3. **Synthesize, don't summarize** — find the intellectual threads
4. **Preserve disagreements** — don't flatten productive tensions

### Document Structure

Follow `assets/synthesis-template.md` exactly.

### Output

Save as `{output_dir}/Integrated_Discussion_Summary.md`
```

### Output Files

| File | Content |
|------|---------|
| `Integrated_Discussion_Summary.md` | Final thematic synthesis with full attribution |

---

## Phase Coordination

### Dependency Graph

```
Phase 1 (parallel)
    │
    ▼
Phase 2 (sequential)
    │
    ▼
Phase 3 (parallel)
    │
    ▼
Phase 4 (sequential)
```

### Coordination Implementation

```python
# Illustrative pseudocode — adapt to your orchestration framework
# Functions like sessions_spawn() and wait_for_completion() are conceptual

# Phase 1
phase1_agents = []
for expert, papers in expert_assignments.items():
    agent = sessions_spawn(
        label=f"expert-reader-{expert}",
        prompt=phase1_prompt(expert, papers)
    )
    phase1_agents.append(agent)

# Wait for all Phase 1 agents
for agent in phase1_agents:
    wait_for_completion(agent)

# Phase 2
phase2_agent = sessions_spawn(
    label="junior-discussion",
    prompt=phase2_prompt(junior, all_phase1_outputs)
)
wait_for_completion(phase2_agent)

# Phase 3
phase3_agents = []
for expert in experts:
    agent = sessions_spawn(
        label=f"expert-response-{expert}",
        prompt=phase3_prompt(expert, phase2_output, other_expert_summaries)
    )
    phase3_agents.append(agent)

for agent in phase3_agents:
    wait_for_completion(agent)

# Phase 4
phase4_agent = sessions_spawn(
    label="synthesis",
    prompt=phase4_prompt(all_outputs)
)
wait_for_completion(phase4_agent)
```

---

## Error Handling

### Common Issues

| Issue | Detection | Resolution |
|-------|-----------|------------|
| Agent timeout | No response within timeout | Retry with extended timeout |
| Missing citations | Synthesis agent reports | Ask expert to revise |
| Paper unreadable | File read error | Report to user, skip or provide alternative |
| Persona mismatch | User provides invalid persona | Use default + warn |

### Recovery Strategy

If a phase fails:
1. Log the failure with context
2. Attempt retry (max 2 retries)
3. If persistent, report to user with partial outputs
4. Allow user to continue from last successful phase
