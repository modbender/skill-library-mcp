# Language Intelligence Commands

These commands leverage the IDE's language server (TypeScript, ESLint, etc.).

## `vscode.lang.definition` — Go to definition

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `line` | number | ✅ | Line number (0-indexed) |
| `character` | number | ✅ | Column number (0-indexed) |

**Returns:** `{ locations: [{ path, line, character }] }`

## `vscode.lang.references` — Find all references

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `line` | number | ✅ | Line (0-indexed) |
| `character` | number | ✅ | Column (0-indexed) |
| `includeDeclaration` | boolean | ❌ | Include declaration (default: true) |

**Returns:** `{ locations: [{ path, line, character }] }`

## `vscode.lang.hover` — Get type/documentation info

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `line` | number | ✅ | Line (0-indexed) |
| `character` | number | ✅ | Column (0-indexed) |

**Returns:** `{ contents: [string] }` — Markdown-formatted type info

## `vscode.lang.symbols` — Search symbols

**Document symbols** (provide `path`):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |

**Workspace search** (provide `query`):

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | ✅ | Search query |

**Returns:** `{ symbols: [{ name, kind, path, line, endLine }] }`

Paginates at 200 symbols per response.

## `vscode.lang.rename` — Safe cross-file rename

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `line` | number | ✅ | Line (0-indexed) |
| `character` | number | ✅ | Column (0-indexed) |
| `newName` | string | ✅ | New symbol name |

**Returns:** `{ ok: true, filesChanged: number, editsApplied: number }`

Uses the language server for semantic safety.

## `vscode.lang.codeActions` — List available quick fixes

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `line` | number | ✅ | Line number |
| `kind` | string | ❌ | Filter: `quickfix`, `refactor`, `source` |

**Returns:** `{ actions: [{ title, kind, isPreferred, index }] }`

## `vscode.lang.applyCodeAction` — Apply a code action

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `line` | number | ✅ | Line number |
| `kind` | string | ❌ | Filter kind |
| `index` | number | ✅ | Index from `codeActions` result |

**Returns:** `{ ok: true, title: string }`

## `vscode.code.format` — Format document

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |

**Returns:** `{ ok: true, editsApplied: number }`
