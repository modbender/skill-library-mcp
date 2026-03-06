# Cursor Agent CLI Commands

Only available when the IDE is **Cursor** (not VS Code).

## `vscode.agent.status` — Check CLI availability

No parameters. **Returns:** `{ available: boolean, version?: string, authenticated?: boolean }`

## `vscode.agent.run` — Run Cursor Agent

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ | Task description or question |
| `mode` | string | ❌ | `agent` (default), `plan`, or `ask` |
| `model` | string | ❌ | Model name |
| `cwd` | string | ❌ | Working directory |
| `timeoutMs` | number | ❌ | Timeout (default: 300000) |

### Modes

| Mode | Access | Use Case |
|------|--------|----------|
| **agent** | Read + write files | Execute changes, implement features |
| **plan** | Read only, proposes changes | Review before executing |
| **ask** | Read only Q&A | Understand codebase, ask questions |

**Returns:** `{ output: string, exitCode: number }`

### Best Practice

1. Use `plan` mode first to review proposed changes
2. Review the output
3. Use `agent` mode to execute if the plan looks good

### Timeout

Agent tasks can be long-running. Use:
- `plan`/`ask`: `invokeTimeoutMs: 180000`, `timeoutMs: 185000`
- `agent`: `invokeTimeoutMs: 300000`, `timeoutMs: 305000`

## `vscode.agent.setup` — Open setup wizard

No parameters. Opens the extension's setup wizard in the IDE.
