---
name: hle-benchmark-evolver
description: Runs HLE-oriented benchmark reward ingestion and curriculum generation for capability-evolver. Use when the user asks to optimize Humanity's Last Exam score, ingest question-level benchmark results, prioritize easy-first queues, or request an immediate benchmark progress result.
tags: [benchmark, hle, evolution, reward, curriculum]
---

# HLE Benchmark Evolver

This skill operationalizes HLE score-driven evolution for OpenClaw.

## When to Use

- User asks to improve HLE score (for example target >= 60%).
- User provides question-level benchmark output and wants it converted to reward.
- User wants easy-first curriculum queue and next-focus questions.
- User asks for an immediate benchmark result snapshot.

## Inputs

- Benchmark report JSON path (`--report=/abs/path/report.json`)
- Optional benchmark id (`cais/hle` default)

## Workflow

1. Validate the report JSON exists and is parseable.
2. Ingest report into `capability-evolver` benchmark reward state.
3. Generate curriculum signals:
   - `benchmark_*`
   - `curriculum_stage:*`
   - `focus_subject:*`
   - `focus_modality:*`
   - `question_focus:*`
4. Return a compact result summary for this run.

## Run

```bash
node skills/hle-benchmark-evolver/run_result.js --report=/absolute/path/hle_report.json
```

Full automatic loop (starts evolution cycle):

```bash
node skills/hle-benchmark-evolver/run_pipeline.js --report=/absolute/path/hle_report.json --cycles=1
```

If your evaluator can be called from shell, let pipeline generate the report each cycle:

```bash
node skills/hle-benchmark-evolver/run_pipeline.js \
  --report=/absolute/path/hle_report.json \
  --eval_cmd="python /path/to/eval_hle.py --out {{report}}" \
  --cycles=3 --interval_ms=2000
```

If no `--report` is provided, it defaults to:

`skills/capability-evolver/assets/gep/hle_report.template.json`

## Output Contract

Always print JSON with these fields:

- `benchmark_id`
- `run_id`
- `accuracy`
- `reward`
- `trend`
- `curriculum_stage`
- `queue_size`
- `focus_subjects`
- `focus_modalities`
- `next_questions`

## Notes

- This skill handles reward/curriculum ingestion. It does not directly solve HLE questions.
- `run_pipeline.js` links ingestion, evolve, and solidify into one executable loop.
