# Editor, Diagnostics & Workspace Commands

## `vscode.editor.active` — Get active file info

No parameters. **Returns:** `{ path, language, selections: [{ line, character }] }`

## `vscode.editor.openFiles` — List all open tabs

No parameters. **Returns:** `{ files: [{ path, language, isDirty }] }`

## `vscode.editor.selections` — Get selected text

No parameters. **Returns:** `{ path, selections: [{ startLine, endLine, text }] }`

## `vscode.diagnostics.get` — Get errors and warnings

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ❌ | Filter to specific file |
| `severity` | string | ❌ | `error`, `warning`, `info`, `hint` |

**Returns:** `{ diagnostics: [{ path, line, severity, message, source }] }`

## `vscode.workspace.info` — Workspace information

No parameters. **Returns:** `{ name: string, rootPath: string, folders: string[] }`
