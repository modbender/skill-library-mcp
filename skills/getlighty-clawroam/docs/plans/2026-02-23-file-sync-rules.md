# Per-Profile File Sync Rules — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Let users select which files sync per machine — default all-shared, opt-out by unchecking files in the dashboard.

**Architecture:** Exclusion list stored in a new D1 `sync_rules` table. Dashboard reads/writes rules via two new Worker endpoints. `cloud.sh` fetches the list before staging and passes each path as an `--exclude` to rsync.

**Tech Stack:** Cloudflare Workers (Hono, D1), vanilla JS (dashboard.html), Bash (cloud.sh)

---

### Task 1: Add `sync_rules` table to D1

**Files:**
- Modify: `cloud-api-worker/schema.sql`

**Step 1: Add table + index to schema.sql**

Append after the last `CREATE INDEX` line:

```sql

CREATE TABLE IF NOT EXISTS sync_rules (
  id           TEXT PRIMARY KEY,
  vault_id     TEXT NOT NULL REFERENCES vaults(id),
  profile_name TEXT NOT NULL,
  path         TEXT NOT NULL,
  created_at   TEXT DEFAULT (datetime('now')),
  UNIQUE(vault_id, profile_name, path)
);
CREATE INDEX IF NOT EXISTS idx_sync_rules_profile ON sync_rules(vault_id, profile_name);
```

**Step 2: Apply migration to live D1**

```bash
cd cloud-api-worker
npx wrangler d1 execute clawroam --file=schema.sql --remote
```

Expected output contains: `"Total queries executed": 8` (6 original + 2 new) and `success: true`.

**Step 3: Verify table exists**

```bash
npx wrangler d1 execute clawroam \
  --command="SELECT name FROM sqlite_master WHERE type='table'" \
  --remote
```

Expected: `sync_rules` appears in results.

**Step 4: Commit**

```bash
git add cloud-api-worker/schema.sql
git commit -m "feat: add sync_rules table to D1 schema"
```

---

### Task 2: Worker — GET sync-rules endpoint

**Files:**
- Modify: `cloud-api-worker/src/index.ts` (before `export default app;`)

**Step 1: Verify endpoint doesn't exist yet**

```bash
curl -s https://clawroam-api.ovisoftblue.workers.dev/v1/vaults/test/profiles/test/sync-rules
```

Expected: `404 Not Found`

**Step 2: Add GET route**

Insert before `export default app;`:

```typescript
// ─── Sync rules — get ────────────────────────────────────────

app.get("/v1/vaults/:id/profiles/:profile/sync-rules", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const ts = c.req.header("X-ClawRoam-Timestamp") || String(Math.floor(Date.now() / 1000));
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `sync-rules:${vaultId}:${profileName}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const rows = await c.env.DB.prepare(
    "SELECT path FROM sync_rules WHERE vault_id = ? AND profile_name = ? ORDER BY path"
  ).bind(vaultId, profileName).all<{ path: string }>();
  return c.json({ excluded: rows.results.map(r => r.path) });
});
```

**Step 3: Deploy**

```bash
cd cloud-api-worker
npx wrangler deploy
```

Expected: `Deployed clawroam-api triggers` with the worker URL.

**Step 4: Test with real JWT (get token first)**

```bash
TOKEN=$(curl -s -X POST https://clawroam-api.ovisoftblue.workers.dev/v1/dashboard/auth \
  -H "Content-Type: application/json" \
  -d '{"vault_id":"cccd796a-d618-43c7-9009-6c39ea796e83","email":"ovisoftblue@yahoo.com"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -s https://clawroam-api.ovisoftblue.workers.dev/v1/vaults/cccd796a-d618-43c7-9009-6c39ea796e83/profiles/192/sync-rules \
  -H "Authorization: Bearer $TOKEN"
```

Expected: `{"excluded":[]}`

**Step 5: Commit**

```bash
git add cloud-api-worker/src/index.ts
git commit -m "feat: add GET /sync-rules endpoint"
```

---

### Task 3: Worker — PUT sync-rules endpoint

**Files:**
- Modify: `cloud-api-worker/src/index.ts`

**Step 1: Add PUT route** (insert after the GET route from Task 2):

```typescript
// ─── Sync rules — update ─────────────────────────────────────

app.put("/v1/vaults/:id/profiles/:profile/sync-rules", async (c) => {
  const vaultId = c.req.param("id");
  const profileName = c.req.param("profile");
  const ts = c.req.header("X-ClawRoam-Timestamp") || String(Math.floor(Date.now() / 1000));
  const a = await auth(c.env.DB, c.env.JWT_SECRET, vaultId, c.req, `sync-rules:${vaultId}:${profileName}:${ts}`);
  if (!a.ok) return c.json({ error: a.error }, 401);
  const body = await c.req.json<{ excluded: string[] }>();
  if (!Array.isArray(body.excluded)) return c.json({ error: "excluded must be an array" }, 400);
  // Sanitize: strip empty strings, limit path length
  const paths = body.excluded.filter(p => typeof p === "string" && p.length > 0 && p.length < 512);
  // Atomic replace: delete existing, insert new
  await c.env.DB.prepare(
    "DELETE FROM sync_rules WHERE vault_id = ? AND profile_name = ?"
  ).bind(vaultId, profileName).run();
  for (const path of paths) {
    await c.env.DB.prepare(
      "INSERT OR IGNORE INTO sync_rules (id, vault_id, profile_name, path) VALUES (?, ?, ?, ?)"
    ).bind(crypto.randomUUID(), vaultId, profileName, path).run();
  }
  return c.json({ status: "ok", excluded_count: paths.length });
});
```

**Step 2: Deploy**

```bash
npx wrangler deploy
```

**Step 3: Test round-trip**

```bash
# Get token (same as Task 2 Step 4)
TOKEN=$(curl -s -X POST https://clawroam-api.ovisoftblue.workers.dev/v1/dashboard/auth \
  -H "Content-Type: application/json" \
  -d '{"vault_id":"cccd796a-d618-43c7-9009-6c39ea796e83","email":"ovisoftblue@yahoo.com"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

VAULT="cccd796a-d618-43c7-9009-6c39ea796e83"
BASE="https://clawroam-api.ovisoftblue.workers.dev/v1"

# Set exclusions
curl -s -X PUT "$BASE/vaults/$VAULT/profiles/192/sync-rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"excluded":["knowledge/private-notes.md","config/secrets.yaml"]}'
# Expected: {"status":"ok","excluded_count":2}

# Read back
curl -s "$BASE/vaults/$VAULT/profiles/192/sync-rules" \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"excluded":["config/secrets.yaml","knowledge/private-notes.md"]}

# Clear
curl -s -X PUT "$BASE/vaults/$VAULT/profiles/192/sync-rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"excluded":[]}'
# Expected: {"status":"ok","excluded_count":0}
```

**Step 4: Commit**

```bash
git add cloud-api-worker/src/index.ts
git commit -m "feat: add PUT /sync-rules endpoint"
```

---

### Task 4: Dashboard — checkbox UI and sync-rules state

**Files:**
- Modify: `web/dashboard.html`

This task is pure frontend — test by opening the dashboard in a browser.

**Step 1: Add CSS for checkbox + excluded file state**

Find the `/* ── File row ── */` block and add after `.file-row .file-size { ... }`:

```css
  /* ── Sync rule checkbox ── */
  .file-checkbox {
    width: 15px; height: 15px; flex-shrink: 0;
    accent-color: var(--amber); cursor: pointer;
    margin-right: 0.1rem;
  }
  .file-row.excluded {
    opacity: 0.38;
  }
  .file-row.excluded .file-name {
    text-decoration: line-through;
    text-decoration-color: rgba(255,255,255,0.25);
  }

  /* ── Excluded badge in profile header ── */
  .excluded-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem; color: var(--text-dim);
    padding: 1px 6px; border: 1px solid var(--border);
    border-radius: 3px; margin-left: 0.5rem;
  }
  .excluded-badge.has-exclusions {
    color: var(--amber); border-color: rgba(217,119,6,0.3);
  }
```

**Step 2: Add sync-rules state to the global `state` object**

Find `var state = {` and add `syncRules: {}` — a map of `profileName → Set<path>`:

```javascript
var state = {
  token: localStorage.getItem('cs_token') || null,
  vaultId: localStorage.getItem('cs_vault_id') || null,
  email: localStorage.getItem('cs_email') || null,
  profiles: [],
  syncRules: {}   // profileName → Set of excluded paths
};
```

**Step 3: Add sync-rules API helpers**

After the `api()` function, add:

```javascript
// ═══════════════════════════════════════════════
// SYNC RULES
// ═══════════════════════════════════════════════
var syncRulesDebounce = {};

function loadSyncRules(profileName, callback) {
  api('GET', '/vaults/' + state.vaultId + '/profiles/' + encodeURIComponent(profileName) + '/sync-rules')
    .then(function(data) {
      state.syncRules[profileName] = new Set(data.excluded || []);
      if (callback) callback();
    })
    .catch(function() {
      state.syncRules[profileName] = new Set();
      if (callback) callback();
    });
}

function saveSyncRules(profileName, columnEl) {
  clearTimeout(syncRulesDebounce[profileName]);
  syncRulesDebounce[profileName] = setTimeout(function() {
    var excluded = Array.from(state.syncRules[profileName] || []);
    api('PUT', '/vaults/' + state.vaultId + '/profiles/' + encodeURIComponent(profileName) + '/sync-rules',
      { excluded: excluded })
      .then(function() {
        showToast('Sync rules saved', 'success');
        updateExcludedBadge(profileName, columnEl);
      })
      .catch(function(err) {
        showToast('Failed to save rules: ' + err.message, 'error');
      });
  }, 500);
}

function updateExcludedBadge(profileName, columnEl) {
  var badge = columnEl.querySelector('.excluded-badge');
  if (!badge) return;
  var count = (state.syncRules[profileName] || new Set()).size;
  badge.textContent = count > 0 ? count + ' excluded' : '';
  badge.className = 'excluded-badge' + (count > 0 ? ' has-exclusions' : '');
}
```

**Step 4: Add excluded-badge to profile header**

In `createProfileColumn`, find where `profile-meta` is built and add the badge:

```javascript
  var badge = el('span', { className: 'excluded-badge' });

  var header = el('div', { className: 'profile-header' }, [
    el('div', { className: 'profile-name' }, [
      el('span', { className: 'dot' }),
      document.createTextNode(profile.name),
      badge
    ]),
    el('div', { className: 'profile-meta' }, [
      el('span', { textContent: formatTime(profile.last_push) }),
      el('span', { textContent: formatSizeMB(profile.size_mb) })
    ])
  ]);
```

**Step 5: Load sync-rules before rendering files**

In `loadProfileFiles`, wrap the existing `api('GET', .../files)` call so sync-rules are fetched first:

```javascript
function loadProfileFiles(profileName, columnEl) {
  var filesContainer = columnEl.querySelector('.profile-files');

  // Load sync rules first, then files
  if (!state.syncRules[profileName]) {
    loadSyncRules(profileName, function() {
      fetchAndRenderFiles(profileName, columnEl, filesContainer);
    });
  } else {
    fetchAndRenderFiles(profileName, columnEl, filesContainer);
  }
}

function fetchAndRenderFiles(profileName, columnEl, filesContainer) {
  api('GET', '/vaults/' + state.vaultId + '/profiles/' + encodeURIComponent(profileName) + '/files')
    .then(function(data) {
      // ... existing render logic, moved here verbatim ...
    })
    .catch(function(err) {
      // ... existing error handling, moved here verbatim ...
    });
}
```

**Step 6: Add checkbox to each file row**

In `createFileRow`, replace the function body with:

```javascript
function createFileRow(file, profileName, columnEl) {
  var catInfo = getCategoryInfo(file.category);
  var fileName = file.path.split('/').pop();
  var isExcluded = (state.syncRules[profileName] || new Set()).has(file.path);

  var checkbox = el('input', {
    'type': 'checkbox',
    className: 'file-checkbox',
    title: isExcluded ? 'Excluded from sync' : 'Synced'
  });
  checkbox.checked = !isExcluded;

  var row = el('div', {
    className: 'file-row' + (isExcluded ? ' excluded' : ''),
    draggable: true,
    title: file.path
  }, [
    checkbox,
    el('span', { className: 'file-icon', textContent: isExcluded ? '\uD83D\uDEAB' : catInfo.icon }),
    el('span', { className: 'file-name', textContent: fileName }),
    el('span', { className: 'file-size', textContent: formatFileSize(file.size) })
  ]);

  row.setAttribute('data-profile', profileName);
  row.setAttribute('data-filepath', file.path);
  row.setAttribute('data-category', file.category || 'other');

  // Checkbox toggle
  checkbox.addEventListener('change', function(e) {
    e.stopPropagation();
    var rules = state.syncRules[profileName] || new Set();
    if (checkbox.checked) {
      rules.delete(file.path);
      row.classList.remove('excluded');
      row.querySelector('.file-icon').textContent = catInfo.icon;
    } else {
      rules.add(file.path);
      row.classList.add('excluded');
      row.querySelector('.file-icon').textContent = '\uD83D\uDEAB';
    }
    state.syncRules[profileName] = rules;
    saveSyncRules(profileName, columnEl);
  });

  // Click to preview (only if not dragging, not on checkbox)
  var wasDragged = false;
  row.addEventListener('mousedown', function() { wasDragged = false; });
  row.addEventListener('mousemove', function() { wasDragged = true; });
  row.addEventListener('click', function(e) {
    if (e.defaultPrevented || wasDragged || e.target === checkbox) return;
    openFileModal(profileName, file);
  });

  row.addEventListener('dragstart', function(e) { wasDragged = true; handleDragStart(e); });
  row.addEventListener('dragend', handleDragEnd);

  return row;
}
```

**Step 7: Update all `createFileRow` call sites** to pass `columnEl`:

In `fetchAndRenderFiles` (Task 4 Step 5), the call becomes:
```javascript
filesList.appendChild(createFileRow(file, profileName, columnEl));
```

**Step 8: Test in browser**

1. Open `web/dashboard.html` in a browser
2. Log in with `ovisoftblue@yahoo.com` + vault ID `cccd796a-d618-43c7-9009-6c39ea796e83`
3. Verify checkboxes appear on all file rows, all checked by default
4. Uncheck a file — row dims + strikethrough, toast "Sync rules saved" appears
5. Reload page — unchecked file is still unchecked (rules persisted to server)
6. Check it again — row returns to normal, badge disappears

**Step 9: Commit**

```bash
git add web/dashboard.html
git commit -m "feat: per-profile file sync rules UI in dashboard"
```

---

### Task 5: Bash client — fetch rules before push

**Files:**
- Modify: `providers/cloud.sh` (inside `cmd_push()`, before the rsync staging block)

**Step 1: Add `fetch_sync_rules` helper function**

Find the `sign_request()` function and add after it:

```bash
fetch_sync_rules() {
  local vault_id="$1"
  local profile_name="$2"
  local ts
  ts=$(date +%s)
  local sig
  sig=$(sign_request "sync-rules:${vault_id}:${profile_name}:${ts}" 2>/dev/null || echo "unsigned")
  $CURL -sf \
    -H "X-ClawRoam-Signature: $sig" \
    -H "X-ClawRoam-Timestamp: $ts" \
    "$API_BASE/vaults/$vault_id/profiles/$profile_name/sync-rules" 2>/dev/null \
    | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for p in data.get('excluded', []):
        print(p)
except:
    pass
" 2>/dev/null || true
}
```

**Step 2: Apply exclusions in `cmd_push()`**

In `cmd_push()`, find the `# Stage files for upload` comment and replace the rsync block with:

```bash
  # Fetch per-profile sync exclusions from server
  local excluded_paths=()
  local rule
  while IFS= read -r rule; do
    [[ -n "$rule" ]] && excluded_paths+=("$rule")
  done < <(fetch_sync_rules "$vault_id" "$(get_profile_name)" 2>/dev/null || true)

  if [[ ${#excluded_paths[@]} -gt 0 ]]; then
    log "Applying ${#excluded_paths[@]} sync exclusion(s)..."
  fi

  # Stage files for upload (exclude local-only files + user exclusions)
  mkdir -p "$sync_dir"
  local rsync_excludes=(
    '--exclude' 'local/'
    '--exclude' 'keys/'
    '--exclude' '.cloud-provider.json'
    '--exclude' '.sync-staging/'
    '--exclude' '.sync-archive.tar.gz'
    '--exclude' '.heartbeat.pid'
    '--exclude' '.git-local/'
  )
  for rule in "${excluded_paths[@]}"; do
    rsync_excludes+=('--exclude' "$rule")
  done
  rsync -a --delete "${rsync_excludes[@]}" "$VAULT_DIR/" "$sync_dir/"
```

**Step 3: Test exclusion works end-to-end**

First, set an exclusion via API (replace with your actual vault ID and token):

```bash
TOKEN=$(curl -s -X POST https://clawroam-api.ovisoftblue.workers.dev/v1/dashboard/auth \
  -H "Content-Type: application/json" \
  -d '{"vault_id":"cccd796a-d618-43c7-9009-6c39ea796e83","email":"ovisoftblue@yahoo.com"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -s -X PUT \
  "https://clawroam-api.ovisoftblue.workers.dev/v1/vaults/cccd796a-d618-43c7-9009-6c39ea796e83/profiles/192/sync-rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"excluded":["requirements.yaml"]}'
```

Then push and verify the log:

```bash
bash /Users/ovidiusandru/Downloads/clawVault/clawroam.sh sync push
```

Expected log line: `Applying 1 sync exclusion(s)...` before the push size line.

Then clear the exclusion:

```bash
curl -s -X PUT \
  "https://clawroam-api.ovisoftblue.workers.dev/v1/vaults/cccd796a-d618-43c7-9009-6c39ea796e83/profiles/192/sync-rules" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"excluded":[]}'
```

Push again — log line should not appear.

**Step 4: Commit**

```bash
git add providers/cloud.sh
git commit -m "feat: fetch and apply sync rules before push"
```

---

### Task 6: Deploy, update both machines, push to GitHub

**Step 1: Deploy final Worker**

```bash
cd cloud-api-worker
npx wrangler deploy
```

**Step 2: Update skill on jasper**

```bash
rsync -av --delete \
  --exclude='.git' --exclude='node_modules' --exclude='.claude' \
  --exclude='.github' --exclude='cloud-api' --exclude='cloud-api-worker' \
  --exclude='web' \
  /Users/ovidiusandru/Downloads/clawVault/ \
  jasper@192.168.0.112:~/.openclaw/skills/getlighty-clawroam/
```

**Step 3: Smoke test on jasper**

```bash
ssh jasper@192.168.0.112 \
  "bash ~/.openclaw/skills/getlighty-clawroam/clawroam.sh sync push"
```

Expected: normal push with no errors.

**Step 4: Push to GitHub**

```bash
git push origin main
```

**Step 5: Publish to ClawHub**

Update version in `SKILL.md` from `2.0.0` to `2.1.0`, then:

```bash
clawhub publish . --slug clawroam --name "ClawRoam" --version "2.1.0"
```
