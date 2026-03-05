# openclaw-todo v0.2 Roadmap

## P1 - Must Have

### 1. Graceful file initialization (auto-create TODO.md)
**Problem:** `fs.readFileSync` in every command handler crashes if the file does not exist.
**Solution:** Add a helper that creates the file with a default header if missing. Call it at the top of every handler.
**Labels:** `bug`, `P1`

### 2. Remove hardcoded German section header
**Problem:** `addTodo()` searches for "Weitere Projektideen" - a hardcoded German string. This breaks for non-German users and couples insertion logic to a specific layout.
**Solution:** Make the section header configurable via `pluginConfig.insertSection` (default: none, append to end). Remove the German fallback entirely.
**Labels:** `enhancement`, `P1`

### 3. Add TypeScript build configuration
**Problem:** No `tsconfig.json` exists. The project relies on OpenClaw's runtime TypeScript loader with no way to type-check independently.
**Solution:** Add `tsconfig.json`, add a `build` script to `package.json`, add a `typecheck` script.
**Labels:** `infra`, `P1`

### 4. Add unit tests
**Problem:** Zero test coverage for the core parsing/mutation functions (`parseTodos`, `markDone`, `addTodo`).
**Solution:** Add a test runner (vitest or node:test) and cover the pure functions. Target: 100% branch coverage on `parseTodos`, `markDone`, `addTodo`.
**Labels:** `test`, `P1`

## P2 - Should Have

### 5. Add `/todo-edit` command
**Problem:** Users cannot edit a TODO item's text without manually editing the file.
**Solution:** Add `/todo-edit <index> <new text>` command that replaces the text of the item at the given index.
**Labels:** `enhancement`, `P2`

### 6. Add `/todo-remove` command
**Problem:** Items can only be marked done, not deleted. Over time the file accumulates stale entries.
**Solution:** Add `/todo-remove <index>` that deletes the line entirely.
**Labels:** `enhancement`, `P2`

### 7. Add tag/priority support
**Problem:** No way to categorize or prioritize items beyond ordering.
**Solution:** Parse inline tags (`#tag`) and priority markers (`!high`, `!low`) from TODO text. Expose them in `todo_status` output. Allow filtering in `/todo-list` via optional argument.
**Labels:** `enhancement`, `P2`

## P3 - Nice to Have

### 8. Add `/todo-search` command
**Problem:** With many items, finding a specific one requires reading the full list.
**Solution:** Add `/todo-search <query>` that filters items by substring match.
**Labels:** `enhancement`, `P3`

### 9. Add due date support
**Problem:** No time-based workflow support.
**Solution:** Parse `@due(YYYY-MM-DD)` from TODO text. Show overdue items first in `/todo-list`. Add optional `overdue` filter to `todo_status`.
**Labels:** `enhancement`, `P3`
