# RLM Controller Examples

This directory contains example inputs and workflows demonstrating RLM Controller capabilities.

## Basic Usage

### Example 1: Simple Text Analysis

```bash
# Store a long document
python3 scripts/rlm_ctx.py store \
  --infile examples/sample_log.txt \
  --ctx-dir ./ctx

# Generate execution plan
python3 scripts/rlm_auto.py \
  --ctx ./ctx/<ctx_id>.txt \
  --goal "find all ERROR entries and summarize root causes" \
  --outdir ./run_example1
```

### Example 2: Code Repository Analysis

```bash
# Concatenate multiple files into one context
cat src/**/*.py > /tmp/codebase.txt

# Store and analyze
python3 scripts/rlm_ctx.py store \
  --infile /tmp/codebase.txt \
  --ctx-dir ./ctx

python3 scripts/rlm_auto.py \
  --ctx ./ctx/<ctx_id>.txt \
  --goal "identify security vulnerabilities in authentication code" \
  --outdir ./run_security_audit \
  --max-subcalls 16 \
  --slice-max 12000
```

### Example 3: Async Batch Processing

```bash
# Full pipeline from context to async execution plan
python3 scripts/rlm_ctx.py store \
  --infile large_dataset.csv \
  --ctx-dir ./ctx

python3 scripts/rlm_auto.py \
  --ctx ./ctx/<ctx_id>.txt \
  --goal "extract all customer complaints and categorize by theme" \
  --outdir ./run_async

python3 scripts/rlm_async_plan.py \
  --plan ./run_async/plan.json \
  --batch-size 8 > ./run_async/async_plan.json

python3 scripts/rlm_async_spawn.py \
  --async-plan ./run_async/async_plan.json \
  --out ./run_async/spawn.jsonl

# View the execution plan
python3 scripts/rlm_batch_runner.py \
  --toolcalls <(python3 scripts/rlm_emit_toolcalls.py \
    --spawn ./run_async/spawn.jsonl \
    --subcall-system <path_to_subcall_prompt>)
```

## Sample Data

Create example inputs:

```bash
# Generate a sample log file
for i in {1..1000}; do
  echo "$(date) [INFO] Processing record $i"
  if [ $((i % 10)) -eq 0 ]; then
    echo "$(date) [ERROR] Failed to process record $i: Connection timeout"
  fi
done > examples/sample_log.txt

# Generate sample documentation
cat > examples/sample_docs.txt <<'EOF'
# API Documentation

## Authentication Endpoints

### POST /api/auth/login
Authenticates a user and returns a session token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

... (continue with more documentation)
EOF
```

## Tips

- **Start small**: Test with ~10k char inputs before scaling to 100k+
- **Tune slice size**: Adjust `--slice-max` based on subcall complexity
- **Monitor logs**: Use `rlm_trace_summary.py` to review execution
- **Cleanup**: Run `scripts/cleanup.sh` after each run to purge artifacts

## Integration with OpenClaw

For OpenClaw agent integration, see [../docs/flows.md](../docs/flows.md) for complete workflows using `sessions_spawn`.
