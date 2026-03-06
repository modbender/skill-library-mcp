## Delegation Contract

This skill enforces a non-negotiable authority boundary.

- The agent must never reason.
- The agent must never write or modify code.
- The agent must never post-process output.
- All cognition is performed by KIMMY.

Violating this contract breaks the skill by definition.

## Design Rationale

Using Transformers directly guarantees:
- No hidden orchestration logic
- Full control over generation parameters
- Explicit delegation enforcement

The agent is reduced to I/O plumbing.

## Operational Notes

- Prompt stripping prevents scaffold leakage
- Deterministic low-temperature sampling minimizes variance
- No fallback logic is permitted
