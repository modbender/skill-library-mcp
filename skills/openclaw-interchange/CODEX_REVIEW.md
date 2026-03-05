# Code Review: @openclaw/interchange

**Reviewer:** Codex subagent  
**Date:** 2026-02-19  
**Scope:** Full library review — all src/, test/, package.json, README.md  
**Verdict:** Solid foundation with several issues that need attention before this is truly bulletproof.

---

## CRITICAL

### 1. Lock is not actually exclusive under race conditions (lock.js)

The `O_CREAT | O_EXCL` open is atomic on POSIX, so the initial acquire is safe. **However**, the stale-lock cleanup path has a TOCTOU race:

```js
const lockPid = parseInt(fs.readFileSync(lockPath, 'utf8').trim(), 10);
if (lockPid && !isProcessAlive(lockPid)) {
  try { fs.unlinkSync(lockPath); } catch {}
  continue; // Two processes can both unlink + re-create
}
```

Two waiters can both read the stale PID, both confirm it's dead, both unlink, and both succeed on the next `O_EXCL` open — one gets the lock, then the other immediately overwrites the lock file on its next iteration. This breaks mutual exclusion.

**Fix:** After unlinking, don't `continue` — fall through to the normal `O_EXCL` open attempt which will naturally resolve the race (only one wins). The current code already does this structurally, but the `continue` bypasses the timeout check, creating an infinite-loop risk if unlink keeps failing silently. Wrap the whole stale-detection in a single atomic rename-and-recreate instead.

### 2. Lock fd is never closed on the happy path before unlink (lock.js)

`releaseLock` calls `closeSync` then `unlinkSync`. But the fd was opened with `O_EXCL` and written to — it's held open for the entire lock duration. The file descriptor is **not used for flock()** — it's just a marker file. This means:

- Another process could unlink the lock file while the holder still has it open (stale detection does exactly this)
- The holder wouldn't know its lock was stolen

This is an **advisory** lock by convention only. It works for single-process sequential use but is not robust for true multi-process concurrency. Document this limitation explicitly or switch to `flock()` via a native addon.

### 3. `writeMd` doesn't pass caller's frontmatter fields through validation (io.js)

`writeMd` never calls `validateFrontmatter`. A caller can write a file with `{ skill: 'test' }` and no `type`, `layer`, `version`, `generator`, or `tags` — producing an invalid interchange file that will fail validation when read by other skills. The "CRITICAL" fields (per validate.js) are silently omitted.

**Fix:** Either validate in `writeMd` and throw on invalid meta, or document that callers must validate themselves. The current API is a footgun.

---

## HIGH

### 4. readMd regex fails on edge cases (io.js)

```js
const match = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
```

- **Windows line endings (`\r\n`):** Regex won't match, returning `{ meta: {}, content: raw }` silently. Any file edited on Windows or by a tool that uses CRLF breaks the parser with zero error.
- **Empty frontmatter (`---\n\n---\n`):** The `\n` between `---` markers requires at least one char in the capture group due to `*?` being non-greedy — actually `[\s\S]*?` matches empty string, so this works. But `\n---` requires a newline before the closing `---`, so `---\n---\n` (no content between) fails.
- **Trailing whitespace after `---`:** `---  \n` won't match.

**Fix:** Normalize `\r\n` → `\n` before matching. Make the regex more lenient: `/^---[ \t]*\n([\s\S]*?)\n---[ \t]*\n?([\s\S]*)$/`.

### 5. `atomicWrite` rename is NOT atomic across filesystems (io.js)

`fs.renameSync` fails with `EXDEV` if tmp and target are on different filesystems. Since `tmp` is in the same directory as `filePath`, this is fine in practice. But if someone mounts `INTERCHANGE_ROOT` on a different filesystem from `/tmp`, and a future refactor puts temps in `/tmp`, it would silently break. Add a comment documenting this assumption.

### 6. indexer.js doesn't use locking (indexer.js)

`updateIndex` and `rebuildIndex` call `atomicWrite` directly without `acquireLock`. If two skills rebuild their index simultaneously, the master index write could race. The atomic write prevents corruption but you could lose one update (last-writer-wins with stale data).

**Fix:** Use `writeMd` or at least `acquireLock` around the master index write.

### 7. `isProcessAlive` false positives (lock.js)

`process.kill(pid, 0)` returns true if the PID exists but belongs to a **different process** (PID reuse). On macOS/Linux, PIDs can be reused quickly under high process churn. The lock would appear held by a live process when the original holder is long dead.

**Fix:** Also store and check process start time, or accept this as a known limitation with documentation.

---

## MEDIUM

### 8. Date serialization non-determinism (serialize.js)

`js-yaml` serializes `Date` objects using their native `toISOString()`. If a field contains a Date object, `sortObject` skips it (`instanceof Date` check), so js-yaml handles it — but the output depends on the Date's milliseconds. If `updated` is set to `new Date().toISOString()` (a string), this is fine. But if someone passes a `Date` object, js-yaml may format it differently than the string representation. The `sortObject` Date check prevents deep-sorting, but doesn't ensure deterministic serialization.

**Fix:** Coerce all Date values to ISO strings in `serializeFrontmatter` before passing to `yaml.dump`.

### 9. `serializeTable` doesn't escape pipe characters (serialize.js)

If any cell value contains `|`, the table structure breaks. This is a markdown table — pipes in content need to be escaped as `\|`.

**Fix:** `const pad = (s, w) => String(s).replace(/\|/g, '\\|').padEnd(w);` (but then width calculation needs to account for escaped length).

### 10. CircuitBreaker `lastResult` memory leak (circuit-breaker.js)

`lastResult` holds a reference to the last successful result forever. If results are large objects (e.g., API responses), this prevents GC. No way to clear it.

**Fix:** Add a `reset()` method and/or allow configuring whether to cache stale results.

### 11. CircuitBreaker HALF_OPEN allows unlimited concurrent probes (circuit-breaker.js)

When transitioning from OPEN → HALF_OPEN, every concurrent caller gets through to the actual function. Standard circuit breaker pattern allows only ONE probe request in HALF_OPEN.

**Fix:** Add a flag like `this._probing = true` to gate HALF_OPEN to a single caller.

### 12. `backoffMs` is unused internally (circuit-breaker.js)

The `backoffMs` method exists but `call()` never uses it. There's no retry logic in the breaker — callers must implement their own. This is either a missing feature or a misleading API.

**Fix:** Either integrate retry logic into `call()` or document that `backoffMs` is a helper for callers to use externally.

### 13. No path traversal protection (io.js, indexer.js)

`writeMd`, `atomicWrite`, `readMd` accept arbitrary paths. A skill could write to `../../etc/passwd` or any location. While skills are trusted code, defense-in-depth would restrict writes to within `INTERCHANGE_ROOT`.

**Fix:** Add an optional `assertWithinRoot(filePath)` guard to `writeMd`.

### 14. `reconcileDbToInterchange` doesn't check `updated` timestamps (reconcile.js)

The function compares hashes but ignores `updated` field from the file objects, even though the type signature includes it. If the DB and file have the same hash but different timestamps, it's reported as "unchanged" — but the metadata is actually drifted.

---

## LOW

### 15. `relativeTime` says "0 seconds ago" for just-now times (helpers.js)

When `seconds < 60` and `seconds === 0`, output is "0 seconds ago". Consider returning "just now".

### 16. `slugify` strips non-ASCII entirely (helpers.js)

`/[^a-z0-9]+/g` removes all non-Latin characters. A CRM contact named "José García" becomes "jos-garc-a". Consider using a transliteration library or at least documenting this limitation.

### 17. `nextGenerationId` is unused by writeMd (generation.js)

`writeMd` implements its own generation logic inline. `nextGenerationId` exists as a public API but is redundant — it reads the file a second time without locking. If someone calls `nextGenerationId` then `writeMd`, they'd get a stale generation number.

**Fix:** Either remove `nextGenerationId` from public API or document it as read-only/informational.

### 18. No `engines` field in package.json

The code uses `??`, optional chaining, and other modern syntax. Should specify `"engines": { "node": ">=18" }`.

### 19. `formatTable` re-export creates a confusing dual export (helpers.js / index.js)

`formatTable` is exported from both `helpers.js` (as re-export of `serializeTable`) and from `index.js` directly as `serializeTable`. Users might import both, not realizing they're the same function. Pick one name.

### 20. Test coverage gaps

Missing tests for:
- `readMd` with no frontmatter (plain markdown)
- `readMd` with malformed YAML (should it throw or return empty meta?)
- `writeMd` with `force: true` 
- `updateIndex` / `rebuildIndex` / `listInterchange` — zero test coverage
- `validateLayer` with Windows-style paths
- `nextGenerationId` on missing file
- `slugify` with empty string, unicode, special characters
- `relativeTime` with future dates
- `isStale` with missing `ttl` field (returns false — is this correct?)
- Concurrent lock contention with stale lock cleanup
- `atomicWrite` cleanup on write failure

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 3     |
| HIGH     | 4     |
| MEDIUM   | 7     |
| LOW      | 6     |

**Bottom line:** The core design is sound — atomic write protocol, deterministic serialization, and the idempotency contract are well-conceived. The main risks are: (1) the lock mechanism has race conditions in stale cleanup that could break mutual exclusion, (2) `writeMd` doesn't enforce its own validation schema, and (3) the regex parser is fragile with CRLF. Fix the 3 CRITICALs and the indexer locking gap before any skill goes to production.
