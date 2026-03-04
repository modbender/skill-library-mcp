# Prompt Templates

This file contains canonical prompt templates for each round in the multi-model critique pipeline.

## Usage notes
- Keep all models on the same task statement and constraints.
- Keep output structure identical across models for easier comparison.
- Keep language aligned to user preference (default here: Korean unless overridden).

## A. Initial draft prompt (per model)

Use this for each model independently in Round 1.

```text
You are model {MODEL_NAME}. Solve the task with this exact internal sequence:
1) Plan
2) Execute
3) Review
4) Improve

Rules:
- Be concrete and evidence-aware.
- State assumptions.
- Flag uncertainty explicitly.
- Keep output in Korean unless user asked otherwise.

User question:
{QUESTION}

Constraints:
{CONSTRAINTS}

Output format:
## Plan
...
## Execute
...
## Review
...
## Improve
...
## Draft Answer
...
```

## B. Cross-critique prompt (per model)

Use this in Round 2 after collecting all draft answers.

```text
You are model {MODEL_NAME}. Critique peer drafts.

Your own draft (for reference):
{SELF_DRAFT}

Peer drafts:
{PEER_DRAFTS}

Evaluate each peer draft on:
1) Strengths
2) Weaknesses
3) Missing assumptions/data
4) Hallucination/confidence risks
5) Concrete fixes

Score each peer draft (1-5) on:
- Accuracy (weight 0.40)
- Coverage (weight 0.25)
- Evidence quality (weight 0.20)
- Actionability (weight 0.15)

Then rank peer drafts (best to worst) with reasons and weighted score.

Output format:
## Critique of Peer A
...
## Critique of Peer B
...
## Ranking
1) ...
2) ...
## Highest-impact fixes to apply globally
...
```

## C. Revision prompt (per model)

Use this in Round 3, feeding each model the critiques that target its own draft.

```text
You are model {MODEL_NAME}. Revise your answer using received critiques.

Original draft:
{SELF_DRAFT}

Critiques received:
{CRITIQUES_FOR_SELF}

Run this sequence exactly:
1) Plan
2) Execute
3) Review
4) Improve

Output format:
## Plan
...
## Execute
...
## Review
...
## Improve
...
## Changes from Critique
- ...
## Revised Answer
...
```

## D. Final synthesis prompt

Use this in Round 4 to produce the final user-facing response.

```text
Synthesize one final response from revised answers.

Revised answers:
{REVISED_ANSWERS}

Requirements:
- Provide a single best final answer.
- Explain key improvements gained from cross-critique.
- List uncertainties/open questions.
- Suggest next actions if helpful.

Output format:
## Final Answer
...
## Key Improvements from Critique
...
## Uncertainties
...
## Next Steps
...
```
