# Evaluation Rubric - Hugging Face

## Goal

Select the best candidate for the user objective using a comparable and repeatable scoring method.

## Benchmark Set

Use the same mini-suite for every candidate:
- Typical case: primary user request
- Edge case: unusual formatting or long input
- Failure-prone case: ambiguity or low-context prompt

Keep prompts fixed during one evaluation round.

## Scoring Grid

| Dimension | Weight | What to check |
|-----------|--------|---------------|
| Output quality | 40% | Correctness, completeness, clarity |
| Reliability | 20% | Stable behavior across reruns |
| Latency | 20% | Time to first useful result |
| Cost efficiency | 10% | Expected compute or endpoint cost |
| Integration fit | 10% | Schema and tooling compatibility |

Use 1-10 scoring per dimension and compute weighted total.

## Decision Rules

- Recommend only candidates with no unresolved license or access risks.
- If top scores are within 0.5 points, prefer lower operational risk.
- If no candidate reaches acceptable quality, return "no-go" and propose alternatives.

## Output Template

Record each run as:

```text
date:
objective:
candidate:
benchmark_set:
scores:
decision:
notes:
```

## Anti-Patterns

- Changing prompts between candidates.
- Mixing hosted and local runs without labeling.
- Ignoring latency because one output looked slightly better.
- Recommending a gated model without access confirmation.
