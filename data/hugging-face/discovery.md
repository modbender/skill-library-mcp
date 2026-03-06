# Discovery Workflow - Hugging Face

## Objective

Build a candidate shortlist that is technically compatible before any inference run.

## Model Discovery

1. Define task and constraints:
- Task family
- Max latency
- Max cost
- Required license type

2. Query model catalog:
```bash
curl -s "https://huggingface.co/api/models?search=<term>&limit=20" | jq '.[].id'
```

3. For each candidate, capture:
- `model_id`
- Task compatibility
- License
- Gated or public status
- Approximate size and framework

4. Keep at least three finalists with different tradeoffs:
- High quality
- Fastest
- Lowest cost

## Dataset Discovery

Use dataset catalog when the task requires domain data or benchmark sources:

```bash
curl -s "https://huggingface.co/api/datasets?search=<term>&limit=20" | jq '.[].id'
```

Record:
- Dataset license
- Update cadence
- Split availability
- Domain relevance

## Space Discovery

Use Spaces to validate runnable demos or workflows quickly:

```bash
curl -s "https://huggingface.co/api/spaces?search=<term>&limit=20" | jq '.[].id'
```

Record:
- Public availability
- Hardware assumptions
- Input and output format

## Exit Criteria

Do not move to inference until each finalist has:
- Known license
- Known access status
- Clear runtime compatibility
- Stated reason for inclusion
