# RLM Controller Flows

## Manual Flow
1) Store input:
```
python3 scripts/rlm_ctx.py store --infile /path/to/input.txt --ctx-dir <workspace>/scratch/rlm_prototype/ctx
```
2) Init run log:
```
python3 scripts/rlm_runner.py init --ctx <ctx_path> --goal "<goal>" --log <log_path>
```
3) Plan slices:
```
python3 scripts/rlm_auto.py --ctx <ctx_path> --goal "<goal>" --outdir <run_dir>
```
4) Spawn subcalls (manual or via async flow)
5) Aggregate and finalize

## Async Flow
1) Build async plan:
```
python3 scripts/rlm_async_plan.py --plan <run_dir>/plan.json --batch-size 4 > <run_dir>/async_plan.json
```
2) Build spawn manifest:
```
python3 scripts/rlm_async_spawn.py --async-plan <run_dir>/async_plan.json --out <run_dir>/spawn.jsonl
```
3) Emit toolcalls:
```
python3 scripts/rlm_emit_toolcalls.py --spawn <run_dir>/spawn.jsonl --subcall-system prompts/subcall_system.txt > <run_dir>/toolcalls.json
```
4) Execute batches in root controller (sub-agents cannot spawn sub-agents)

## Aggregation Guidance
- Keep a structured list of subcall outputs
- Map outputs to slice ranges
- Summarize in FINAL_ANSWER with citations to slice ranges

## Cleanup Notes
Use the cleanup script after runs if desired:
```
CLEAN_RETENTION=0 scripts/cleanup.sh   # delete all
CLEAN_RETENTION=5 scripts/cleanup.sh   # keep last 5 files per dir
```
Ignore rules live in `docs/cleanup_ignore.txt` (substring match).
