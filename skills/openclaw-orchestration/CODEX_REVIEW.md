# Codex Review: @openclaw/orchestration

## Summary
12 issues found (1 critical, 4 high, 5 medium, 2 low)

## Strengths
- **Solid transaction usage** in `claimTask` and `sweep` — atomic claim with dependency check prevents most race conditions
- **WAL mode + foreign keys** enabled by default — good SQLite hygiene
- **Migration system** is clean with checksums and transactional application
- **Test coverage** is good — covers race conditions, dependencies, sweep, retry lifecycle
- **`MAX(0, current_load - 1)`** prevents negative load — nice defensive SQL
- **Clean separation of concerns** — db, queue, agents, sweep, protocol, interchange are well-factored

## Issues

### 1. [CRITICAL] Race condition in `claimTask` — stale read before transaction
**File:** `src/queue.js` lines 51-54
**Problem:** `getTask()` is called *outside* the transaction, then `task.status` and `task.depends_on` are used *inside* it. Between the read and the transaction start, another process could claim the task. The `WHERE status = 'pending'` in the UPDATE catches the claim race, but `task.depends_on` is read from stale data. If dependencies are modified between the read and the transaction, the check uses outdated info. More critically, if `task.status !== 'pending'` the function returns `null` *before* entering the transaction, skipping the atomic check entirely.
**Fix:** Move the initial `getTask()` + status check inside the transaction:
```js
const doClaim = db.transaction(() => {
  const task = getTask(db, taskId);
  if (!task || task.status !== 'pending') return null;
  // ... rest of claim logic
});
```

### 2. [HIGH] `completeTask` and `failTask` are not transactional
**File:** `src/queue.js` lines 93-113, 121-134
**Problem:** These functions run multiple statements (UPDATE tasks, INSERT results, INSERT handoff_log, UPDATE agents) without a transaction. If the process crashes mid-way, the DB ends up in an inconsistent state — e.g., task marked completed but agent load not decremented, or result not recorded.
**Fix:** Wrap each in `db.transaction()`.

### 3. [HIGH] `createTask` is not transactional
**File:** `src/queue.js` lines 18-26
**Problem:** INSERT into `tasks` and INSERT into `handoff_log` are separate statements. A crash between them loses the audit trail silently.
**Fix:** Wrap in `db.transaction()`.

### 4. [HIGH] `failTask` ignores the `reason` parameter entirely
**File:** `src/queue.js` line 121
**Problem:** The `reason` parameter is accepted but never stored anywhere — not in the task, not in handoff_log, not in results. Failure context is silently discarded.
**Fix:** Either add a `reason` column to `handoff_log` or store it in `results.summary`.

### 5. [HIGH] `refreshInterchange` async close race in CLI
**File:** `src/cli.js` lines 145-150
**Problem:** The `refresh` command calls `await refreshInterchange(db)` then `closeDb()`. But Commander's `.action()` doesn't await async handlers by default in older versions. If it doesn't await, `closeDb()` runs before `refreshInterchange` finishes, causing writes to a closed database.
**Fix:** Ensure Commander v12+ is used (which awaits async actions), or wrap with `.then(() => closeDb())`.

### 6. [MEDIUM] `claimTask` doesn't enforce `max_concurrent`
**File:** `src/queue.js` lines 51-82
**Problem:** An agent can claim unlimited tasks — `max_concurrent` is tracked via `current_load` but never checked. The field exists in the schema and is displayed, creating a false sense of enforcement.
**Fix:** Inside the claim transaction, check `current_load < max_concurrent` before allowing the claim.

### 7. [MEDIUM] `backup()` calls `db.backup()` which returns a Promise but is not awaited
**File:** `src/backup.js` line 17
**Problem:** `better-sqlite3`'s `.backup()` returns a Promise. The CLI command and function treat it synchronously, so the backup may not complete before the program exits or the "Backup saved" message prints.
**Fix:** Make `backup()` async and await `db.backup(dest)`. Update CLI accordingly.

### 8. [MEDIUM] `restore()` overwrites live database without closing connections
**File:** `src/backup.js` lines 24-29
**Problem:** `fs.copyFileSync` overwrites the DB file while a connection may be open (the module-level `_db` singleton). With WAL mode this can corrupt data. The CLI `restore` command doesn't call `initDb()` first, so _db is null, but nothing prevents misuse from code.
**Fix:** Ensure `closeDb()` is called before restore. Add a guard or accept the db instance to close.

### 9. [MEDIUM] No validation on `priority` or `status` values in application layer
**File:** `src/queue.js` line 19
**Problem:** Invalid priority values (e.g., `"urgent"`) will fail with a CHECK constraint error from SQLite, producing a raw unhelpful error message. Same for any direct status manipulation.
**Fix:** Validate `priority` against `['high', 'medium', 'low']` before the INSERT and throw a descriptive error.

### 10. [MEDIUM] Stale task files accumulate in interchange
**File:** `src/interchange.js` lines 120-130
**Problem:** `generateTaskFiles` creates a `.md` file per task but never cleans up old files. If a task is deleted from the DB (not currently possible but future-proofing), its interchange file persists forever.
**Fix:** Clear the `state/tasks/` directory before regenerating, or add a cleanup step.

### 11. [LOW] UUID collision risk with 8-char truncation
**File:** `src/queue.js` line 18, `src/agents.js` line 16
**Problem:** `uuidv4().slice(0, 8)` gives 32 bits of entropy (~4 billion values). Fine for small deployments but a birthday collision is probable around 65K tasks. Not urgent but worth noting.
**Fix:** Use 12 chars for more headroom, or use `nanoid`.

### 12. [LOW] `retryTask` doesn't verify agent existence
**File:** `src/queue.js` line 145
**Problem:** Minor — `retryTask` clears `assigned_agent` but doesn't decrement the original agent's `current_load`. If a task was manually failed (not via `failTask`), the load could drift.
**Fix:** Already handled in `failTask` which is the normal path. Just document that manual DB edits can desync load counts.
