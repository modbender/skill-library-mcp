# Git Commands

## `vscode.git.status` — Working tree status

No parameters. **Returns:** `{ branch, staged: [], modified: [], untracked: [], ahead, behind }`

## `vscode.git.diff` — View diffs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ❌ | Specific file (default: all) |
| `staged` | boolean | ❌ | Show staged diff |
| `ref` | string | ❌ | Compare against ref (e.g., `HEAD~1`) |

**Returns:** `{ diff: string }`

## `vscode.git.log` — Commit history

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | number | ❌ | Max commits (default: 10) |
| `oneline` | boolean | ❌ | One-line format |
| `path` | string | ❌ | Filter by file |

**Returns:** `{ log: string }`

## `vscode.git.blame` — Line-level blame

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | ✅ | File path |
| `startLine` | number | ❌ | Start line |
| `endLine` | number | ❌ | End line |

**Returns:** `{ blame: string }` (porcelain format)

## `vscode.git.stage` — Stage files

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paths` | string[] | ✅ | File paths to stage |

**Returns:** `{ ok: true }`

## `vscode.git.unstage` — Unstage files

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `paths` | string[] | ✅ | File paths to unstage |

**Returns:** `{ ok: true }`

## `vscode.git.commit` — Commit staged changes

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | ✅ | Commit message |
| `amend` | boolean | ❌ | Amend last commit |

**Returns:** `{ ok: true, output: string }`

## `vscode.git.stash` — Stash operations

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | ✅ | `push`, `pop`, `list`, or `drop` |
| `message` | string | ❌ | Stash message (for push) |

**Returns:** `{ ok: true, output: string }`
