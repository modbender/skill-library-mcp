---
name: safe-merge-update
description: "Safely merge upstream OpenClaw updates without destroying plugin/skill injections, custom UI tabs, or workspace features. Uses the configured agent model for conflict resolution."
metadata:
  openclaw:
    emoji: "🔄"
    requires:
      anyBins: ["git", "pnpm"]
      env:
        - REPO_DIR
---

# Safe Merge Update

Merges upstream OpenClaw changes into your fork while preserving all custom code:
plugin registrations, custom UI tabs, workspace skills, controllers, and state extensions.

## How It Works

1. **Pre-flight**: Fetch upstream, compute divergence, detect conflicts
2. **AI Merge**: The agent resolves each conflict using the merge manifest as intent context
3. **Validate**: Build check, tab verification, protected pattern scan
4. **Report**: Announce results back to the requesting session

## Security & Privacy

### Model Usage
This skill uses your **currently configured OpenClaw agent model** for conflict resolution. No external API calls are made beyond what your agent already uses. The model sees conflict diffs (ours/base/theirs) for files that have merge conflicts — this is the same model that already has access to your codebase via the agent's file tools.

To use a specific model, set `SAFE_MERGE_MODEL` environment variable (e.g., `anthropic/claude-opus-4-6`).

### Secret Redaction
Before any file content is sent to the model for conflict resolution, it passes through `scripts/redact-secrets.sh` which detects and replaces:
- API keys (OpenAI `sk-`, GitHub `ghp_`, Slack `xoxb-`, AWS `AKIA`, etc.)
- Bearer/Basic auth tokens
- Private keys (RSA, EC, OPENSSH)
- Connection strings with embedded passwords
- Config values for `password`, `secret`, `token`, `apiKey` fields

Detected secrets are replaced with `[REDACTED_N]` placeholders. The redaction map is written **exclusively to fd 3** — if fd 3 is not open, the script **aborts with an error** rather than falling back to stderr. This is a hard guarantee: the map never touches stderr, stdout, or disk.

**Caller protocol (agent must follow this):**
```bash
# Open a temp file on fd 3 to hold the map in memory
TMPMAP=$(mktemp)
exec 3>"$TMPMAP"
redacted=$(scripts/redact-secrets.sh "$file")   # map → fd 3 / $TMPMAP
exec 3>&-                                        # close fd 3

# ... send $redacted to model, resolve conflict ...

# Restore secrets from map
echo "$resolved" | scripts/redact-secrets.sh --restore --map-file "$TMPMAP"
rm -f "$TMPMAP"  # wipe map immediately after use
```

Backups in `/tmp/safe-merge/backups/` contain only **redacted content** — they are created after redaction and never contain plaintext secrets.

### What Gets Sent to the Model
- Only **conflicting file diffs** are sent (not the entire repository)
- All secrets are **redacted before transmission** (see above)
- The merge manifest describes file intents and protected patterns
- `.env` files are never included in merge prompts

### Build Execution
The validation phase runs `pnpm install --ignore-scripts`, `pnpm build`, and `pnpm ui:build` to verify the merge compiles.

**`pnpm install` will download packages from the npm registry.** This is network activity. `--ignore-scripts` is always passed to suppress `preinstall`/`postinstall` lifecycle hooks from running untrusted code.

**Before proceeding past pre-flight:**
- Review upstream `package.json` diffs in the pre-flight report
- Check for new dependencies you don't recognize before running install
- For maximum safety, run the full merge in an isolated environment (container, VM, or disposable clone)

**SKILL.md says "No Network Installs" — this refers to the skill package itself (no curl/wget/npm install in the skill's own setup). It does NOT mean the merge workflow avoids network; `git fetch upstream` and `pnpm install` both require network access.**

### Backups (Non-Negotiable)
Before ANY file edits, the skill creates a full backup of every conflicting file at `/tmp/safe-merge/backups/` preserving directory structure. **Backups are created after secret redaction** — they never contain plaintext secrets. If the merge goes wrong, restore from backups and re-run secret restoration.

### No Network Installs
This skill contains no install scripts that download from external URLs. All files are local to the skill package. The only network activity is `git fetch upstream` and your normal model API calls.

## Invocation

### Via UI
Click the **↑ Update** button in the topbar (right of Health pill).

### Via Chat
```
/update — or ask: "run a safe merge update"
```

## Architecture Note

This skill is **instruction-driven**: there is no single automated merge script that runs start-to-finish. Instead:
- `preflight.sh` — read-only analysis, produces a JSON report
- `validate.sh` — post-merge build + pattern checks
- `merge-agent-prompt.md` — prompt template that the **agent** follows to resolve each conflicting file interactively

The AI merge step (Phase 2) is executed by the agent itself, file by file, guided by `merge-agent-prompt.md` and `MERGE_MANIFEST.json`. This is intentional — it allows the agent to apply judgment, ask clarifying questions, and adapt to unexpected conflicts that a script couldn't handle.

## Phases

### Phase 1: Pre-flight (`scripts/preflight.sh`)

Run automatically when invoked. Produces a report at `/tmp/safe-merge/preflight-report.json`.

**What it does:**
- Fetches upstream (`git fetch upstream`)
- Computes commit divergence (ahead/behind counts)
- Lists conflicting files via `git merge-tree`
- Checks each conflict against the merge manifest for protection status
- Creates a temporary worktree for dry-run merge (avoids touching your working tree)

**Pre-flight report includes:**
- Divergence stats
- List of conflicting files with protection status
- Recommended strategy per file (keep-ours, ai-merge, accept-upstream)

**Environment variables:**
- `REPO_DIR` — Path to your OpenClaw repo (must be set explicitly)
- `UPSTREAM_REMOTE` — Upstream remote name (default: `upstream`)
- `UPSTREAM_BRANCH` — Upstream branch (default: `main`)

### Phase 2: Merge & Conflict Resolution

The agent performs the actual merge and resolves conflicts:

1. **Create merge branch** — `git checkout -b safe-merge-YYYY-MM-DD`
2. **Examine conflicts before merging** — read both our version and upstream's version of each conflicting file to understand what each side changed
3. **Run the merge** — `git merge upstream/main --no-commit --no-ff`
4. **For each conflicting file:**
   a. Read the conflict markers to understand the exact diff
   b. Check `MERGE_MANIFEST.json` for intent and strategy (`keep-ours`, `accept-upstream`, `ai-merge`)
   c. Resolve: write the clean merged file preserving our customizations + upstream improvements
   d. `git add` the resolved file
5. **Verify auto-merged protected files** — even files that auto-merge need checking: grep for `mustPreserve` patterns to confirm our custom code survived
6. **Secret redaction** (for complex conflicts requiring prompt-based resolution):
   - `scripts/redact-secrets.sh` replaces secrets with `[REDACTED_N]` placeholders
   - Redaction map held in memory via fd 3 (never touches disk)
   - After resolution, restore secrets from map

**Key principle:** Always examine both sides of a conflict BEFORE attempting resolution. Understanding what upstream changed and what we customized is essential for correct merges.

### Phase 3: Validation (`scripts/validate.sh`)

After all conflicts are resolved:
- `pnpm install --ignore-scripts` — install any new dependencies (lifecycle scripts suppressed)
- `pnpm build` — compile the gateway
- `pnpm ui:build` — compile the Control UI
- Protected pattern scan — verify `mustPreserve` patterns from the manifest still exist
- Tab verification — check that custom UI tabs are still registered

### Phase 4: Commit & Report

- Commits on the merge branch (`safe-merge-YYYY-MM-DD`) — never directly on `main`
- Commit message includes: upstream version, commit count, conflict resolution summary, file counts
- Reports to user: files resolved, strategies used, build status, any warnings
- User decides whether to merge the branch into `main` and push:
  ```bash
  git checkout main
  git merge safe-merge-YYYY-MM-DD
  git push origin main
  ```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REPO_DIR` | *(required, declared in metadata)* | Path to your OpenClaw repository |
| `SAFE_MERGE_MODEL` | *(agent's current model)* | Model override for conflict resolution |
| `UPSTREAM_REMOTE` | `upstream` | Git remote name for upstream |
| `UPSTREAM_BRANCH` | `main` | Upstream branch to merge from |

### Merge Model Selection

The model used for AI conflict resolution can be configured in two ways:

1. **Via the UI modal** — The update modal includes a "Merge Model" dropdown that lists all available models (same catalog as Agents → Model Selection). The selection is persisted in `localStorage` under the key `openclaw-merge-model` and survives page reloads. When a model is selected and "Run Safe Merge" is clicked, the merge prompt includes `SAFE_MERGE_MODEL=<selected-model>`.

2. **Via environment variable** — Set `SAFE_MERGE_MODEL` before invoking the skill (e.g., in the agent's env config or inline).

If neither is set, the skill uses the agent's currently configured primary model.

The dropdown appears on both the initial "Check for Updates" screen and the results screen, so you can change it at any point before starting the merge.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — skill instructions |
| `MERGE_MANIFEST.json` | Protected files, intents, `mustPreserve` patterns |
| `scripts/preflight.sh` | Pre-flight analysis (read-only, no modifications) |
| `scripts/validate.sh` | Post-merge build and pattern validation |
| `scripts/merge-agent-prompt.md` | Prompt template for per-file conflict resolution |
| `scripts/redact-secrets.sh` | Secret detection and redaction before model transmission |
| `update-modal.ts` | Reference copy of the UI update modal component (source of truth: `ui/src/ui/views/update-modal.ts`) |

## UI Update Modal

Clicking the topbar update button (in **any** state) opens an update modal with a guided flow:

1. **Check for Updates** — asks the user to confirm, then calls `update.checkUpstream` RPC with `force: true` (bypasses cache)
2. **Status Result** — shows upstream divergence: commits behind, commits ahead, or "Up to date"
3. **Action Buttons** — "⚡ Run Safe Merge" (if behind) or "🔄 Run Merge Anyway" (if up to date) — both send the merge prompt to the chat session

The modal is rendered by `ui/src/ui/views/update-modal.ts` and uses state properties `updateModalState` (closed/confirm/checking/result), `upstreamDivergence`, and `mergeModel` on the app component. A reference copy of the modal source is kept at `skills/safe-merge-update/update-modal.ts`.

### Button States

- **N Updates** (accent-colored): Git upstream has N newer commits
- **Updates Available** (accent-colored): npm registry has a newer version (non-fork workflows)
- **✓ Up to Date** (muted pill, clickable): Up to date — click still opens the modal to re-check
- **Merging…** (spinner, disabled): Merge in progress

### How Update Detection Works

The gateway runs two parallel checks:

1. **npm registry** (`update-startup.ts`): Compares `VERSION` against npm latest. Used for standard installs.
2. **Git upstream** (`update.checkUpstream` RPC): Runs `git fetch upstream && git rev-list --count HEAD..upstream/main`. Used for fork workflows. Result is cached for 5 minutes.

For forks, the git check is authoritative — your local `package.json` version will often be ahead of npm (since you're building from source), so the npm check would incorrectly say "up to date."

## Post-Merge Checklist

After a successful merge, always:
1. Run `pnpm ui:build` — the Control UI is served from `dist/control-ui/`
2. **Update systemd service version** — the UI header reads `OPENCLAW_SERVICE_VERSION` from the service unit:
   ```bash
   NEW_VERSION=$(node -e "console.log(require('./package.json').version)")
   sed -i "s/OPENCLAW_SERVICE_VERSION=.*/OPENCLAW_SERVICE_VERSION=$NEW_VERSION/" ~/.config/systemd/user/openclaw-gateway.service
   systemctl --user daemon-reload
   ```
3. Run `openclaw gateway restart` — pick up the new build
4. Check config schema compatibility — upstream may add `.strict()` to schemas
5. Clean up backups: `rm -rf /tmp/safe-merge/` — while backups are redacted, remove them when no longer needed

## Known Issues / Lessons Learned

### Discord Voice Schema (2026-02-27)
Upstream added `.strict()` to `DiscordVoiceSchema`, rejecting keys our fork previously supported. Fix: remove unsupported keys from config, or add them back to the schema.

### Control UI Assets Missing (2026-02-27)
`pnpm build` builds the gateway but NOT the Control UI. UI needs separate `pnpm ui:build`. The validate script now includes this.

### Duplicate Schema Properties (2026-02-27)
Git auto-merge kept both our extracted const AND upstream's inline block. Fix: manual dedup during AI conflict resolution.

### CSP connect-src Extensions (2026-03-01)
Our fork adds `http://localhost:*` (Jarvis voice agent) and `https://api.openai.com` (Realtime API) to the CSP `connect-src` directive in `control-ui-csp.ts`. Upstream only has `ws: wss:`. On merge, always keep our extensions — they're required for voice features.

### Branch Naming Convention (2026-03-01)
Merge branches should be date-stamped: `safe-merge-YYYY-MM-DD`. This makes it easy to identify merge attempts and clean up old branches.

### Auto-Merged Protected Files Need Verification (2026-03-01)
Even files that auto-merge without conflicts can lose custom code if upstream refactors the surrounding context. After merge, always verify `mustPreserve` patterns exist in auto-merged protected files — don't just trust git's auto-merge.

### pnpm install May Add Packages (2026-03-01)
Upstream may add new dependencies. When 162 commits are merged, `pnpm install` downloaded 51 new packages. This is expected but worth noting in the merge report.

## Safety Summary

- ✅ **Backups before any edits** — `/tmp/safe-merge/backups/`
- ✅ **New branch** — never merges directly into current branch
- ✅ **Validation must pass** before committing
- ✅ **No external downloads in skill setup** — skill files are all local; merge workflow does use network for `git fetch` and `pnpm install`
- ✅ **No credential requirements** — uses your existing agent model
- ✅ **Secrets redacted before model transmission** — API keys, tokens, passwords, private keys
- ✅ **Only conflict diffs sent to model** — not the entire repo
- ✅ **User controls merge** — agent reports results, user decides to push
- ✅ **Dry-run in worktree** — pre-flight uses a temp worktree, not your working tree
- ✅ **Stops on failure** — if validation fails, reports and stops rather than pushing broken code
