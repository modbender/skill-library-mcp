# Summarization Techniques

## Zero-Shot Direct

Use the model's general knowledge without examples. Fast but less precise.

**When:** Quick overviews, straightforward content, time pressure.

**Pattern:**
```
Summarize [content] in [format/length], focusing on [aspect].
```

**Example:**
```
Summarize this article in one paragraph, focusing on the main conclusion and supporting evidence.
```

**Limitation:** May miss nuance or produce generic output on specialized content.

---

## Few-Shot with Examples

Provide 1-3 examples of source→summary pairs before the target content.

**When:** Need consistent style, specialized domain, specific tone.

**Pattern:**
```
Example 1:
Source: [text]
Summary: [summary]

Example 2:
Source: [text]
Summary: [summary]

Now summarize: [target text]
```

**Tip:** Examples should match target content type and desired output style.

---

## Chain-of-Thought

Walk through reasoning before final summary. Best for complex material.

**When:** Academic papers, technical docs, legal content, anything requiring careful analysis.

**Pattern:**
```
Step 1: Identify the main argument
Step 2: List supporting evidence
Step 3: Note methodology or approach
Step 4: Extract conclusions
Final: Synthesize into [length] summary
```

**Example:**
```
First, identify the research question and hypothesis. Then outline the methodology. Next, summarize key findings with data. Finally, state conclusions in 2-3 sentences.
```

---

## Role-Based

Assign a perspective to adjust vocabulary, focus, and depth.

**When:** Audience-specific summaries, professional contexts.

**Patterns:**
```
As a [role], summarize for [audience]:
- As a teacher → simplify for students
- As a consultant → focus on business implications
- As a researcher → emphasize methodology and gaps
- As a journalist → lead with news angle
```

**Example:**
```
As a business analyst, summarize this report for executives. Focus on ROI, risks, and recommended actions. Keep under 150 words.
```

---

## Instruction-Heavy

Explicit, detailed requirements when precision matters.

**When:** Strict length limits, specific elements required, compliance contexts.

**Pattern:**
```
Summarize following these rules:
- Exactly [N] words/sentences
- Must include: [element 1], [element 2]
- Must exclude: [element]
- Format: [bullet/paragraph/structured]
- Tone: [formal/casual]
```

**Example:**
```
Summarize in exactly 50 words. Include: main finding, sample size, statistical significance. Exclude: methodology details. Format: single paragraph. Tone: academic.
```

---

## Multi-Pass Refinement

Multiple passes for complex or lengthy content.

**When:** Book chapters, long reports, content requiring different summary levels.

**Pattern:**
```
Pass 1: Broad overview (what is this about?)
Pass 2: Key details (what are the main points?)
Pass 3: Synthesis (what does it mean?)
Pass 4: Compression (distill to final length)
```

**Use case:** Creating both executive summary and detailed breakdown from same source.

---

## Technique Selection Matrix

| Scenario | Primary Technique | Backup |
|----------|-------------------|--------|
| Quick email summary | Zero-shot | — |
| Academic paper for students | Role-based | Chain-of-thought |
| Legal contract highlights | Chain-of-thought | Instruction-heavy |
| Consistent newsletter format | Few-shot | Instruction-heavy |
| Meeting notes for exec | Role-based | Zero-shot |
| Technical doc for non-tech | Role-based | Multi-pass |
| Compliance requirement | Instruction-heavy | — |
