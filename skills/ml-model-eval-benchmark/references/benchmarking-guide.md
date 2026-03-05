# Benchmarking Guide

## Inputs

- `weights`: metric -> weight
- `models`: list of model candidate rows with `name` and `metrics`

## Recommended Practices

- Normalize metric scales before weighted scoring.
- Keep metric names identical across candidates.
- Use explicit tie-break rules (for example: higher precision after equal score).
- Log all assumptions in the benchmark artifact.

## Output Fields

- Weighted leaderboard
- Recommended model
- Applied metric weights
