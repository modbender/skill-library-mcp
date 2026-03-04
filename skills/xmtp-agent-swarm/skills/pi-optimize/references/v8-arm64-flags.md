# V8 Flags for ARM64 Constrained Environments

Populate after first audit. Track which flags are tested, their impact, and whether they're worth recommending upstream.

## Memory Reduction

| Flag | Description | Tested | Impact |
|------|-------------|--------|--------|
| `--max-old-space-size=512` | Cap old generation heap | no | -- |
| `--optimize-for-size` | Optimize for memory over speed | no | -- |
| `--gc-interval=100` | More frequent GC | no | -- |
| `--max-semi-space-size=2` | Limit young generation | no | -- |
| `--lite-mode` | Reduced tier compilation | no | -- |

## ARM64 Specific

| Flag | Description | Tested | Impact |
|------|-------------|--------|--------|
| `--no-turbo-inlining` | Reduce compiled code size | no | -- |

## Notes

- Baseline memory usage and startup time should be recorded in `pi-benchmarks.md` before testing flags
- Test each flag independently, then in combination
- Record results with `process.memoryUsage()` and `time` measurements
