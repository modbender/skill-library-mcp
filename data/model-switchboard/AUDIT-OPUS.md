# Model Switchboard v2.0 — Security & Code Audit

**Auditor:** Claude Opus 4.6 (subagent)
**Date:** 2026-02-25
**Scope:** All source files (switchboard.sh, validate.py, redundancy.py, model-registry.json, task-routing.json, ui/index.html, SKILL.md, README.md)
**Verdict:** **CONDITIONAL PASS** — No critical vulnerabilities found. Several medium/low issues to address before ClawHub publish.

---

## Summary

The codebase is well-architected with strong safety fundamentals: fail-closed validation, atomic writes, automatic backups, and no direct config editing. The code quality is above average for a skill of this scope. However, there are real issues that should be fixed.

**Findings by severity:**
- CRITICAL: 0
- HIGH: 2
- MEDIUM: 5
- LOW: 6

---

## HIGH Findings

### H-1: XSS via innerHTML in UI allowlist and Telegram user rendering
**Files:** `ui/index.html` lines ~610, ~840-860
**Severity:** HIGH

The `renderAllowlist()` function uses innerHTML with model names:
```js
t.innerHTML = `${esc(m)} <button class="xbtn" ... onclick="removeAllow('${esc(m).replace(/'/g, "\\'")}')">x</button>`;
```

Similarly `renderTelegramUsers()`:
```js
tag.innerHTML = `${esc(u)} <button class="xbtn" ... onclick="removeTelegramUser('${esc(u).replace(/'/g, "\\'")}')">x</button>`;
```

The `esc()` function only does `String()` — it does NOT HTML-encode. A model name like `<img onerror=alert(1) src=x>` would execute. While model names are validated server-side via regex (`^[a-zA-Z0-9][a-zA-Z0-9._/-]*$`), the UI receives data from an API and shouldn't trust it.

**Fix:** Replace `esc()` with proper HTML escaping:
```js
function esc(v) {
  const s = String(v == null ? '' : v);
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}
```
Or switch to `textContent` + `createElement` pattern (as used in `renderRoles()`).

### H-2: Shell injection possible via model names in inline Python
**Files:** `switchboard.sh` lines ~620-640 (import_config function)
**Severity:** HIGH

In `import_config()`, the `$input` variable is interpolated directly into a Python string as a fallback:
```bash
imp_primary=$(python3 -c "
import json, os
with open(os.environ.get('SWITCHBOARD_IMPORT_FILE', '$input')) as f:
```

If `$input` contains a single quote, this breaks the Python string and allows code injection. While the file path comes from a CLI argument (not untrusted user input in most cases), this is still a bad pattern.

**Fix:** Always use the env var, never the shell interpolation fallback:
```bash
SWITCHBOARD_IMPORT_FILE="$input" python3 -c "
import json, os
with open(os.environ['SWITCHBOARD_IMPORT_FILE']) as f:
```
(This pattern IS correctly used in the atomic-write Python block in the same function — just not in the extraction blocks.)

---

## MEDIUM Findings

### M-1: No cron job model validation against allowlist
**Severity:** MEDIUM

**There is no code anywhere** that validates cron job model assignments against the model registry or allowlist. The `task-routing.json` defines a `cron` routing to `google/gemini-2.5-flash`, but nothing validates that cron jobs spawned by OpenClaw use only allowed/safe models. A cron job could theoretically be configured to use a blocked or unsafe model.

**Fix:** Add a `validate_cron_models()` function to validate.py that checks:
1. All cron job model references against the registry
2. That cron models have minimum required capabilities for their task type
3. Add a `cron-validate` command to switchboard.sh

### M-2: Stale model reference in task-routing.json
**File:** `task-routing.json` line 13
**Severity:** MEDIUM

`google/gemini-2.5-flash` is listed as the cron and heartbeat model. While this model IS in the registry, the registry marks it as "Gemini 2.5 Flash" — an older generation model. The registry has `google/gemini-3-flash-preview` available. This isn't a bug (the model still works), but for a production ClawHub skill, the default task routing should reference current-generation models.

**Fix:** Update task-routing.json:
```json
"cron": { "model": "google/gemini-3-flash-preview", ... },
"heartbeat": { "model": "google/gemini-3-flash-preview", ... }
```

### M-3: Race condition on backup pruning
**File:** `switchboard.sh` lines ~130-140
**Severity:** MEDIUM

The backup pruning logic uses `ls -t | tail | xargs rm -f`. If two switchboard commands run concurrently (e.g., two agents, or rapid CLI calls), both could backup and prune simultaneously, potentially deleting each other's backups or counting wrong.

**Fix:** Use a lockfile for backup operations:
```bash
LOCKFILE="$BACKUP_DIR/.switchboard.lock"
(
  flock -n 9 || { log_warn "Backup lock held — skipping prune"; return; }
  # ... prune logic ...
) 9>"$LOCKFILE"
```

### M-4: redundancy.py fails open when registry can't load
**File:** `redundancy.py` lines 21-26
**Severity:** MEDIUM

`load_registry()` in redundancy.py returns `{"models": {}, "providers": {}, "roles": {}}` on failure (no strict mode option). This means `generate_redundant_config()` will produce an empty config with no models, which then gets applied via `redundancy-apply`. The error path returns `{"error": ...}` only when no providers are detected, not when registry fails.

The shell wrapper does check for empty output and error keys, so this is partially mitigated. But the Python function itself should be more defensive.

**Fix:** Add an explicit registry validation check at the top of `generate_redundant_config()`:
```python
registry = load_registry()
if not registry.get("models"):
    return {"error": "Model registry is empty or corrupt. Cannot generate redundancy config."}
```

### M-5: Atomic write in import_config validates after write, not before
**File:** `switchboard.sh` lines ~680-695
**Severity:** MEDIUM

The inline Python for import does:
```python
json.dump(cfg, f, indent=2)  # Write to temp
json.load(open(tmp))          # Re-read to validate
os.rename(tmp, config_path)   # Move into place
```

The re-read validation only checks JSON parse validity, not schema validity. A structurally valid JSON that is semantically wrong (e.g., model set to an integer) would pass this check. The validate.py engine IS called for individual model refs before this point, but the final merged config isn't schema-validated.

**Fix:** After the atomic write, call `validate_config_schema()` on the merged config before renaming:
```python
issues = validate_config_schema(cfg)
errors = [i for i in issues if i['level'] == 'error']
if errors:
    os.unlink(tmp)
    print('VALIDATION_FAILED')
    sys.exit(1)
```

---

## LOW Findings

### L-1: Version string mismatch
**Files:** SKILL.md says "v2.0", README.md says "v2.0", switchboard.sh header says "v2.0", but ui/index.html title says "v2". The task referenced "v3".
**Fix:** Decide on the canonical version and update all files.

### L-2: Dead code — `setup.sh` referenced but not audited
**File:** `switchboard.sh` line ~960: `bash "$SKILL_DIR/scripts/setup.sh"`
The setup command delegates to `scripts/setup.sh` which was not provided for audit. If it doesn't exist, the command silently fails.
**Fix:** Verify setup.sh exists or add a guard: `[ -f "$SKILL_DIR/scripts/setup.sh" ] || { log_error "setup.sh not found"; exit 1; }`

### L-3: stderr suppression masks real errors
**File:** `switchboard.sh` — many `2>/dev/null` on python3 calls (lines ~60, 70, 80, etc.)
Python errors (import failures, syntax errors, crashes) are silently swallowed. The fail-closed design mitigates this (empty output = reject), but debugging becomes harder.
**Fix:** Log stderr to a temp file or the backup directory for diagnostics.

### L-4: Backup permissions — umask not set
**File:** `switchboard.sh` line ~125
`chmod 600 "$backup_file"` is good, but the `mkdir -p "$BACKUP_DIR"` doesn't set directory permissions. On a multi-user system, the backup directory could be world-readable.
**Fix:** Add `chmod 700 "$BACKUP_DIR"` after mkdir.

### L-5: model-registry.json — `openai/dall-e-3` has empty safeRoles
**File:** `model-registry.json` ~line 240
DALL-E 3 has `"safeRoles": []` AND `"blocked": true`. The blocked flag is sufficient, but the empty safeRoles is redundant. Not a bug, just noise.

### L-6: UI uses `innerHTML` in several render functions with `esc()`
**File:** `ui/index.html` — `renderRoles()`, `renderPipeline()`, `renderProviders()`, etc.
Similar to H-1 but these use `esc()` on values that come from the model registry (controlled data). Lower risk than H-1 because the data source is a local JSON file, not user input. Still best practice to use textContent.

---

## Positive Findings (What's Done Well)

1. **Fail-closed validation** — validate.py correctly blocks on registry load failure in strict mode (line ~30). The shell wrapper treats empty/error responses as rejections. This is textbook correct.

2. **Atomic writes** — Config changes use temp file → validate → rename pattern. This prevents corruption on crash/power loss.

3. **Operation-specific rollback** — Each change tracks its own backup file with PID in timestamp. Rollback restores the exact pre-operation state, not just "latest."

4. **No direct JSON editing** — All config changes go through `openclaw models set` CLI. The skill never does raw JSON manipulation of model fields (except import, which validates first).

5. **Model format regex** — `validate_model_ref()` uses strict regex that blocks shell metacharacters, path traversal (`../`), and null bytes. A malicious model name like `anthropic/../../etc/passwd` is rejected by the regex.

6. **Provider diversity enforcement** — redundancy.py correctly ensures fallback chains don't stack the same provider.

7. **Registry completeness** — 50+ models across 20+ providers with capability/role metadata. Well-maintained.

---

## Recommendations for ClawHub Publish

1. **Fix H-1 and H-2** before publishing — these are real injection vectors even if exploitation requires unusual conditions.
2. **Add M-1** (cron validation) — this is a feature gap that users will expect.
3. **Update M-2** (stale model refs) — easy win for credibility.
4. **Add integration tests** — no test suite was found. At minimum, test validate.py functions with edge cases (empty strings, special chars, corrupt JSON).
5. **Add a CHANGELOG.md** — version history for ClawHub users.

---

*Audit complete. No showstoppers for a private deployment, but H-1 and H-2 should be fixed before public ClawHub publishing.*
