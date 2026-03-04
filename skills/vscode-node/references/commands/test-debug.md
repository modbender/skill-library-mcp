# Test & Debug Commands

## Testing

### `vscode.test.list` — Check test framework

No parameters. **Returns:** `{ available: boolean, message: string }`

### `vscode.test.run` — Run tests

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ❌ | Test file path |
| `debug` | boolean | ❌ | Run in debug mode |

**Returns:** `{ ok: true, message: string }`

### `vscode.test.results` — Get latest results

No parameters. **Returns:** `{ hasResults: boolean, summary: string }`

## Debug

### `vscode.debug.launch` — Start debug session

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ❌ | Named config from launch.json |
| `config` | object | ❌ | Inline debug configuration |

Provide either `name` or `config`, not both.

### `vscode.debug.stop` — Stop debugging

No parameters.

### `vscode.debug.breakpoint` — Manage breakpoints

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | ✅ | `add`, `remove`, `list`, or `clear` |
| `path` | string | ❌ | File path (for add/remove) |
| `line` | number | ❌ | Line number (for add/remove) |
| `condition` | string | ❌ | Conditional expression (for add) |

### `vscode.debug.evaluate` — Evaluate expression

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `expression` | string | ✅ | Expression to evaluate |
| `context` | string | ❌ | `repl`, `watch`, or `hover` |

**Returns:** `{ result: string, type: string }`

Only works when stopped at a breakpoint.

### `vscode.debug.stackTrace` — Get call stack

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `levels` | number | ❌ | Max frames (default: 20) |

**Returns:** `{ frames: [{ id, name, path, line }] }`

### `vscode.debug.variables` — Inspect variables

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scope` | string | ❌ | `locals`, `globals`, or `closure` |

**Returns:** `{ variables: [{ name, value, type, variablesReference }] }`

### `vscode.debug.status` — Check debug session

No parameters. **Returns:** `{ active: boolean, sessionName?: string, sessionType?: string }`
