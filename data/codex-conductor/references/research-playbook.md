# Research Playbook

Use during planning when `research_mode=true`.

## Goals
- Reduce architecture risk before implementation
- Provide transparent option comparison
- Tie decisions to requirements and constraints

## Research Procedure
1. Restate research questions from planning gaps.
2. Define decision criteria (cost, complexity, speed, security, scale, lock-in).
3. Generate 2-4 viable options per major decision:
   - app architecture
   - data layer
   - deployment model
   - auth model
   - testing strategy
4. For each option, record:
   - fit for requirements
   - trade-offs
   - operational burden
   - risk profile
5. Recommend one option with confidence score (low/medium/high).
6. Convert recommendation into ADR draft.

## Output Template (`docs/research-notes.md`)
- Questions
- Decision Criteria
- Options Compared
- Recommendation
- Risks and Mitigations
- Follow-up Questions

## Quality Rules
- Prefer primary docs and well-established references.
- Avoid single-source decisions for critical architecture choices.
- Mark unknowns explicitly.
- Do not present uncertain conclusions as facts.
