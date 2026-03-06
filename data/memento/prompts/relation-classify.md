# Relation Classification Prompt

Given two facts from a knowledge base, classify the semantic relationship between them.

## Relation Types

- `caused_by` — Fact A is a consequence or result of Fact B
- `precondition_of` — Fact A must be true for Fact B to happen
- `part_of` — Fact A is a component or sub-element of Fact B
- `related_to` — Fact A and Fact B share a common topic or context (general)
- `contradicts` — Fact A and Fact B cannot both be true simultaneously
- `superseded_by` — Fact A has been replaced or updated by Fact B

## Instructions

You will receive a JSON array of candidate pairs. For each pair, output a JSON object with:
- `pair_index`: the index from the input (0-based)
- `relation_type`: one of the types above
- `strength`: 0.5–1.0 (confidence in this classification)
- `rationale`: one short sentence explaining why

Only classify pairs where a meaningful relationship exists. If two facts are only weakly related, use `related_to` with strength 0.5–0.6. If no meaningful relationship exists, omit the pair from the output.

Respond with ONLY a JSON array, no markdown, no explanation.

## Pairs

{{pairs}}
