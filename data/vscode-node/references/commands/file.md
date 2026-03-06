# File & Directory Commands

## `vscode.file.read` — Read file content

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Relative path from workspace root |
| `offset` | number | ❌ | Start line (0-indexed) |
| `limit` | number | ❌ | Max lines to read |

**Returns:** `{ content: string, totalLines: number, language: string }`

## `vscode.file.write` — Create or overwrite a file

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Relative path from workspace root |
| `content` | string | ✅ | Full file content |

**Returns:** `{ ok: true, created: boolean }`

Respects `readOnly` and `confirmWrites` extension settings.

## `vscode.file.edit` — Precise text replacement

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Relative path from workspace root |
| `oldText` | string | ✅ | Exact text to find (must match exactly, including whitespace) |
| `newText` | string | ✅ | Replacement text |

**Returns:** `{ ok: true, replacements: number }`

If no match found, returns `replacements: 0`. Ensure `oldText` matches exactly.

## `vscode.file.delete` — Delete a file

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | Relative path from workspace root |
| `useTrash` | boolean | ❌ | Move to trash (default: true) |

**Returns:** `{ ok: true }`

## `vscode.dir.list` — List directory contents

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ❌ | Directory path (default: workspace root) |
| `pattern` | string | ❌ | Glob pattern (e.g., `**/*.ts`) |
| `recursive` | boolean | ❌ | Include subdirectories (default: false) |

**Returns:** `{ entries: [{ name, type, size }] }`
