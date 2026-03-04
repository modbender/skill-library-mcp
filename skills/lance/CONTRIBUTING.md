# Contributing to Lance

Contributions are welcome if they improve signal quality and reduce triage rejection risk.

## Contribution Priorities

1. Better exploitability validation logic
2. Better economic feasibility checks
3. Better false-positive elimination
4. Better platform-ready report quality
5. Better benchmark realism and coverage

## Ground Rules

- Do not add speculative vulnerability logic without rejection criteria.
- Do not add style/lint-only findings to core playbooks.
- Do not weaken evidence requirements for `Confirmed` findings.
- Keep instructions concrete and operational.
- Keep ASCII unless a file already requires non-ASCII.

## Pull Request Checklist

- Explain what changed and why.
- Include examples of before/after behavior.
- Update relevant reference files if workflow changes.
- Update benchmark cases when detection/triage behavior changes.
- Keep changelog entries short and factual.

## Benchmarks

If your change affects scoring or triage:
- add or update cases in `assets/benchmarks/`
- run:
  - `python scripts/benchmark_harness.py assets/benchmarks/sample_benchmark.json`
- document expected metric impact in your PR

## Script Quality

For any script change:
- ensure CLI help remains clear
- keep input/output JSON contracts stable
- avoid hardcoding local machine paths

## Documentation Quality

- prefer short, direct wording
- avoid hype language
- every new playbook section should include:
  - exploit checks
  - reject conditions
  - evidence requirements

## Versioning

- patch updates: typo/docs/internal fixes
- minor updates: new references/playbooks/scripts that preserve compatibility
- major updates: breaking workflow or schema changes

## Security and Scope

Lance is for authorized security testing only. Do not contribute workflows that encourage out-of-scope or unethical testing.
