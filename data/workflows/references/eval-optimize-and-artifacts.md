# Eval, Optimize, And Artifacts

## Run Artifacts

Each `workflow run` produces artifacts in `/workspace/.harness/runs/run_xxx/`:

```text
run_xxx/
  run.json
  eval.json
  audit.jsonl
  outputs/final.md
  steps/
    {step}.meta.json
    {step}.result.json
    {step}.context.json
    {step}.stdout
    {step}.stderr
```

Note: `{step}.context.json` is diagnostic output, not a runtime global variable.

## Eval -> Optimize Loop

1. Run baseline:
   ```bash
   workflow run prediction-scanner
   ```
2. Evaluate baseline:
   ```bash
   workflow eval run_abc123
   ```
3. Start optimization record:
   ```bash
   workflow optimize prediction-scanner --baseline run_abc123
   ```
4. Apply code changes manually, then rerun and reevaluate.
5. Compare metrics and rollback if degraded:
   ```bash
   workflow rollback prediction-scanner opt_xxx
   ```

## Default Evaluation Metrics

- `total_duration_ms` (target max)
- `step_count`
- `success_rate` (target min 100%)
- `error_rate` (target max 0%)
- `output_size_bytes` (target max 1MB)
