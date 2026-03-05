# Workflow CLI And Definition Reference

## Quick CLI Reference

```bash
workflow create <id>                           # Scaffold workflow
workflow list                                  # List workflows
workflow show <id>                             # Print workflow source
workflow validate <id>                         # Validate definition
workflow run <id> [--input JSON]               # Execute workflow
workflow status <run-id>                       # Run status
workflow logs <run-id> [--step <step-id>]      # Run/step logs
workflow eval <run-id>                         # Evaluate run quality
workflow optimize <id> --baseline <run-id>     # Create optimization record
workflow optimize-list                         # List optimization records
workflow rollback <id> <opt-run-id>            # Restore baseline snapshot
```

## Workflow Definition (TypeScript)

Workflows live in `/workspace/.harness/workflows/` as `.ts`.
Active workflows should use the `@latest.ts` suffix convention.

```typescript
import defineWorkflow from "/workspace/tools/workflow/defineWorkflow"

export default defineWorkflow({
  version: 1,
  id: "my-workflow",
  name: "Human-readable Name",
  description: "What this workflow does",
  triggers: [{ manual: true }],
  inputs: [
    { name: "symbol", type: "string", required: true, default: "BTC" }
  ],
  output_mode: "inline", // "inline" | "sql" | "compact"
  steps: [],
  evaluation: {},
})
```

## Step Types

- `type: "ts"`: full scripting access (`callTool`, `sql`, `exec`, `fs`, `kv`)
- `type: "sql"`: SQL queries over registered tables
- `type: "host"`: direct host-tool invocation
- `type: "bash"`: shell command step
- `type: "kv"`: key-value read/write operations

## Template Syntax

Use `{{ }}` interpolation in string fields (not `${}`).

- `{{inputs.symbol}}`
- `{{steps.step_id.result}}`
- `{{steps.step_id.result.fieldName}}`
- `{{!steps.step_id.result.flag}}`

## Runtime APIs In TS Steps

- `callTool(name, input)`
- `sql(query)`
- `exec(command)`
- `fs.promises.*`
- `kv.get(key)`
- `kv.set(key, value)`
- `kv.delete(key)`
- `kv.list(prefix)` (returns `[{key, value}]`)
- `console.log(...)`
- `export default value` for step result

## Critical Runtime Limits

- `context` is not injected as a TS global.
- Python runtime is not available.
- Prefer re-querying SQL/KV/tools over assuming previous in-memory state.
