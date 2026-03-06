---
name: volcengine-compute-function
description: Build and operate Volcengine Function Compute workloads. Use when users need function deployment, event triggers, runtime configuration, or serverless troubleshooting.
---

# volcengine-compute-function

Deploy and troubleshoot serverless functions with predictable packaging and runtime checks.

## Execution Checklist

1. Confirm runtime, trigger type, and region.
2. Build package and validate environment variables.
3. Deploy function and verify latest revision.
4. Invoke test event and return logs/latency summary.

## Reliability Rules

- Keep deployment artifacts versioned.
- Separate config from code.
- Include rollback target in outputs.

## References

- `references/sources.md`
