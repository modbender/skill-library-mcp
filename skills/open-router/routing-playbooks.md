# Routing Playbooks — Open Router

## Workload Classes

Define routing by workload first, then select models.

| Workload | Primary Objective | Suggested Routing Strategy |
|----------|-------------------|----------------------------|
| Short coding tasks | Fast turnaround | Lower-latency model with code reliability baseline |
| Deep analysis | Reasoning quality | Higher-capability model with fallback for rate limits |
| Long-context synthesis | Context capacity | Long-context model plus fallback with similar context window |
| Extraction and formatting | Deterministic output | Stable, lower-cost model with strict prompt templates |
| Brainstorming | Creative breadth | Mid-tier model with cheaper fallback for iterative cycles |

## Decision Sequence

1. Identify workload class and acceptable latency.
2. Choose primary model for that class.
3. Assign fallback from a different family when possible.
4. Define trigger: timeout, rate limit, or quality threshold.
5. Validate with a small prompt set before rollout.

## Verification Prompt Set

Use 3-5 representative prompts per workload class:

- One typical case
- One edge case with long or noisy input
- One strict-format output case

Track success rate, latency, and output consistency before finalizing policy.

## Anti-Pattern

Using one "best model" for every workflow causes avoidable cost spikes and weak reliability when task shapes change.
