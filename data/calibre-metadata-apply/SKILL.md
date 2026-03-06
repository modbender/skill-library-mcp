---
name: calibre-metadata-apply
description: Apply metadata updates to existing Calibre books via calibredb over a Content server. Use for controlled metadata edits after target IDs are confirmed by a read-only lookup.
metadata: {"openclaw":{"requires":{"bins":["node","calibredb"],"env":["CALIBRE_PASSWORD"]},"optionalBins":["pdffonts"],"optionalEnv":["CALIBRE_USERNAME"],"primaryEnv":"CALIBRE_PASSWORD","dependsOnSkills":["subagent-spawn-command-builder"],"localWrites":["skills/calibre-metadata-apply/state/runs.json","~/.config/calibre-metadata-apply/auth.json","~/.config/calibre-metadata-apply/config.json"],"modifiesRemoteData":["calibre:metadata"]}}
---

# calibre-metadata-apply

A skill for updating metadata of existing Calibre books.

## Requirements

- `calibredb` must be available on PATH in the runtime environment
- `subagent-spawn-command-builder` installed (for spawn payload generation)
- `pdffonts` is optional/recommended for PDF evidence checks
- Reachable Calibre Content server URL
  - `http://HOST:PORT/#LIBRARY_ID`
- If authentication is enabled, prefer `/home/altair/.openclaw/.env`:
  - `CALIBRE_USERNAME=<user>`
  - `CALIBRE_PASSWORD=<password>`
- Pass `--password-env CALIBRE_PASSWORD` (username auto-loads from env)
- You can still override explicitly with `--username <user>`.
- Optional auth cache: `--save-auth` (default file: `~/.config/calibre-metadata-apply/auth.json`)

## Supported fields

### Direct fields (`set_metadata --field`)
- `title`
- `title_sort`
- `authors` (string with `&` or array)
- `author_sort`
- `series`
- `series_index`
- `tags` (string or array)
- `publisher`
- `pubdate` (`YYYY-MM-DD`)
- `languages`
- `comments`

### Helper fields
- `comments_html` (OC marker block upsert)
- `analysis` (auto-generates analysis HTML for comments)
- `analysis_tags` (adds tags)
- `tags_merge` (default `true`)
- `tags_remove` (remove specific tags after merge)

## Required execution flow

### A. Target confirmation (mandatory)
1. Run read-only lookup to narrow candidates
2. Show `id,title,authors,series,series_index`
3. Get user confirmation for final target IDs
4. Build JSONL using only confirmed IDs

### B. Proposal synthesis (when metadata is missing)
1. Collect evidence from file extraction + web sources
2. Show one merged proposal table with:
   - `candidate`, `source`, `confidence (high|medium|low)`
   - `title_sort_candidate`, `author_sort_candidate`
3. Get user decision:
   - `approve all`
   - `approve only: <fields>`
   - `reject: <fields>`
   - `edit: <field>=<value>`
4. Apply only approved/finalized fields
5. If confidence is low or sources conflict, keep fields empty

### C. Apply
1. Run dry-run first (mandatory)
2. Run `--apply` only after explicit user approval
3. Re-read and report final values

## Analysis worker policy

- Use `subagent-spawn-command-builder` to generate `sessions_spawn` payload for heavy candidate generation
  - `task` is required.
  - Profile should include model/thinking/timeout/cleanup for this workflow.
- Use lightweight subagent model for analysis (avoid main heavy model)
- Keep final decisions + dry-run/apply in main

## Data flow disclosure

- Local execution:
  - Build `calibredb set_metadata` commands from JSONL.
  - Read/write local state files (`state/runs.json`) and optional auth/config files under `~/.config/calibre-metadata-apply/`.
- Subagent execution (optional for heavy candidate generation):
  - Uses `sessions_spawn` via `subagent-spawn-command-builder`.
  - Text/metadata sent to subagent can reach model endpoints configured by runtime profile.
- Remote write:
  - `calibredb set_metadata` updates metadata on the target Calibre Content server.

Security rules:
- Do not use `--save-plain-password` unless explicitly instructed by the user.
- Prefer env-based password (`--password-env CALIBRE_PASSWORD`) over inline `--password`.
- If user does not want external model/subagent processing, keep flow local and skip subagent orchestration.

## Long-run turn-split policy (library-wide)

For library-wide heavy processing, always use turn-split execution.

## Unknown-document recovery flow (M3)

Batch sizing rule:
- Keep each unknown-document batch small enough to show full row-by-row results in chat (no representative sampling).
- If unresolved items remain, stop and wait for explicit user instruction to start the next batch.

### User intervention checkpoints (fixed)

1. **Light pass (metadata-only)**
   - Always run this stage by default (no extra user instruction required)
   - Analyze existing metadata only (no file content read)
   - Present a table to user:
     - current file/title
     - recommended title/metadata
     - confidence/evidence summary
   - Stop and wait for user instruction before any deeper stage

2. **On user request: page-1 pass**
   - Read only the first page and refine proposals
   - Report delta from light pass

3. **If still uncertain: deep pass**
   - Read first 5 pages + last 5 pages
   - Add web evidence search
   - Produce finalized proposal with confidence + rationale

4. **Approval gate**
   - Show detailed findings and request explicit approval before apply

### Pending and unsupported handling

- Use `pending-review` tag for unresolved/hold items.
- If document is unresolved in current flow, do not force metadata guesses.
  - Tag with `pending-review` and keep for follow-up investigation.

### Diff report format (for unknown batch runs)

Return full results (not samples):
- execution summary (target/changed/pending/skipped/error)
- full changed list with `id` + key before/after fields
- full pending list with `id` + reason
- full error list with `id` + error summary
- confidence must be expressed as `high|medium|low`

### Runtime artifact policy

- Keep run-state and temporary artifacts only while a run is active.
- On successful completion, remove per-run state/artifacts.
- On failure, keep minimal artifacts only for retry/debug, then clean up after resolution.

### Internal orchestration (recommended)

- Use lightweight subagent for all analysis stages
- Keep apply decisions in main session
- Persist run state for each stage in `state/runs.json`

### Turn 1 (start)
1. Main defines scope
2. Main generates spawn payload via `subagent-spawn-command-builder` (profile example: `calibre-meta`), then calls `sessions_spawn`
3. Save `run_id/session_key/task` via `scripts/run_state.mjs upsert`
4. Immediately tell the user this is a subagent job and state the execution model used for analysis
5. Reply with "analysis started" and keep normal chat responsive

### Turn 2 (completion)
1. Receive subagent completion notice
2. Save result JSON
3. Complete state handling via `scripts/handle_completion.mjs --run-id ... --result-json ...`
4. Return summarized proposal (apply only when needed)

Run state file:
- `state/runs.json`

## PDF extraction policy

1. Try `ebook-convert` first
2. If empty/failed, fallback to `pdftotext`
3. If both fail, switch to web-evidence-first mode

## Sort reading policy

- Use user-configured `reading_script` for Japanese/non-Latin sort fields
  - `katakana` / `hiragana` / `latin`
- Ask once on first use, then persist and reuse
- Default policy is full reading (no truncation)
- Config path: `~/.config/calibre-metadata-apply/config.json`
  - key: `reading_script`

## Usage

Dry-run:

```bash
cat changes.jsonl | node skills/calibre-metadata-apply/scripts/calibredb_apply.mjs \
  --with-library "http://127.0.0.1:8080/#MyLibrary" \
  --password-env CALIBRE_PASSWORD \
  --lang ja
```

Apply:

```bash
cat changes.jsonl | node skills/calibre-metadata-apply/scripts/calibredb_apply.mjs \
  --with-library "http://127.0.0.1:8080/#MyLibrary" \
  --password-env CALIBRE_PASSWORD \
  --apply
```

## Do not

- Do not run direct `--apply` using ambiguous title matches only
- Do not include unconfirmed IDs in apply payload
- Do not auto-fill low-confidence candidates without explicit confirmation
