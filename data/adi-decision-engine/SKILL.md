---
name: adi-decision-engine
description: Structured multi-criteria decision analysis for ranking options with weights, constraints, confidence, tradeoff reasoning, sensitivity analysis, and explainable recommendations. Use when the user asks for decision support, MCDA, weighted scoring, prioritization, vendor selection, route planning, hiring shortlist ranking, tool comparison, procurement decisions, or auditable agent decision logic.
homepage: https://github.com/dimgouso/adi-decision-engine_skill_openclaw
metadata: {"openclaw":{"emoji":"⚖️","requires":{"bins":["python3"],"env":[],"config":[]},"os":["darwin","linux","win32"]}}
---

# ADI Decision Engine

## Core promise

Turn a messy tradeoff problem into a structured, auditable multi-criteria decision and return a ranked recommendation with confidence and explanation.

## When to use this skill

Use this skill when the user needs structured decision support rather than open-ended brainstorming. Typical triggers include:

- multi-criteria decision analysis
- weighted scoring or option ranking
- vendor selection or procurement
- route planning with explicit tradeoffs
- hiring shortlist ranking
- tool or platform comparison
- policy-driven or auditable agent decisions

## Input modes

This skill supports exactly two input modes.

### 1. Structured mode

The user already has a decision request with:

- `options`
- `criteria`
- optional `constraints`
- optional `policy_name`
- optional evidence, confidence, or context

Use [scripts/validate_request.py](scripts/validate_request.py) first if request quality is uncertain, then [scripts/run_adi.py](scripts/run_adi.py) to execute it.

### 2. Freeform mode

The user provides a natural-language tradeoff problem.

First use [scripts/normalize_problem.py](scripts/normalize_problem.py) to produce a request skeleton. Do not pretend the request is complete if important fields are missing. If the skeleton is not ready, ask for the missing inputs instead of inventing scores or constraints.

## Output contract

If ADI runs successfully, the final answer must contain:

- `best_option`
- a short rationale for why it won
- top-ranked alternatives
- confidence summary
- constraint impact summary
- sensitivity or stability summary when available
- explicit assumptions

If the request is not complete enough to run, return a request-completion prompt rather than a fabricated ranking.

## Workflow

1. Determine whether the user input is structured or freeform.
2. For freeform input, normalize it into a request skeleton using [scripts/normalize_problem.py](scripts/normalize_problem.py).
3. Validate candidate requests with [scripts/validate_request.py](scripts/validate_request.py).
4. Run complete requests with [scripts/run_adi.py](scripts/run_adi.py).
5. Present the ADI result in clear decision-support language:
   - recommendation first
   - strongest tradeoff second
   - caveats and sensitivity after that

## Decision hygiene rules

- Never rank options without explicit criteria.
- Never silently invent hard constraints.
- If criterion direction is ambiguous, stop and clarify.
- Normalize vague goals into named criteria before scoring.
- Prefer a small, explicit criteria set over many overlapping criteria.
- Keep the policy choice visible: `balanced`, `risk_averse`, or `exploratory`.

## Output quality rules

- Show the top recommendation first.
- Explain why it won.
- Mention the strongest tradeoff.
- Call out eliminated or constraint-violating options.
- Include confidence caveats when evidence is weak.
- Use a compact comparison table or structured bullet list when comparing several options.

## Safety and honesty rules

- No hidden math.
- No fake scores.
- No fabricated evidence.
- Do not claim ADI ran if the runtime dependency is missing.
- Do not request API keys.
- Do not require network access for the core workflow.
- Do not tell the user to trust the ranking if the request is under-specified.

## Runtime requirements

- `python3`
- either an importable `adi-decision` package or the `adi` CLI on `PATH`

If the ADI runtime is unavailable, stop with a clear error and explain that the dependency must be installed locally.

## References

- Request schema: [references/request_schema.md](references/request_schema.md)
- Result interpretation: [references/result_interpretation.md](references/result_interpretation.md)
- Policy guide: [references/policy_guide.md](references/policy_guide.md)
- Use cases: [references/use_cases.md](references/use_cases.md)

## Examples

- [examples/vendor_selection.json](examples/vendor_selection.json)
- [examples/route_planning.json](examples/route_planning.json)
- [examples/hiring_shortlist.json](examples/hiring_shortlist.json)
- [examples/research_methods.json](examples/research_methods.json)
- [examples/tool_selection.json](examples/tool_selection.json)
