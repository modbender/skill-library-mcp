# Workflows

## Common Setup (All Actions)

1. Confirm Chrome MCP works (`get_windows_and_tabs`).
2. Switch to an existing flomo tab if present; otherwise navigate to `https://v.flomoapp.com/mine`.
3. Prefer desktop layout. If viewport is narrow/mobile, try to continue but warn about reduced reliability.
4. Read the page with `chrome_read_page` and/or `chrome_get_web_content`.

## Query / Search Workflow

### Goal

Find memos by text match and return candidate metadata without modifying data.

### Default Behavior

- Matching type: contains match (case-sensitive/insensitive as appropriate to the user request)
- Scan mode: auto deep scan
- Default scan cap: 50 memos

### Steps

1. Read visible memo list content.
2. Extract visible memo candidates from memo cards and timestamp/memo links.
3. Parse `memo_id` from links matching `/mine/?memo_id=...`.
4. Build `MemoCandidate` records with timestamp + snippet + match reason.
5. If no match and scan cap not reached:
   - Scroll down to load more memos
   - Re-read page
   - Continue extraction and dedupe by `memo_id`
6. Return candidate list.

### Output Contract

For each candidate, return:
- `memo_id`
- visible timestamp
- short snippet (truncated)
- why it matched

If no match within cap, say so and mention the cap reached.

## Create / Insert Workflow

### Goal

Create a new flomo memo via the top Web editor.

### Steps

1. Run common setup.
2. Locate the top editor input region (the main compose area near the top of the memo column).
3. Fill the user-provided content (preserve line breaks).
4. Trigger submission using the visible submit button or supported keyboard path.
5. Re-read top of memo list.
6. Best-effort identify the newly created memo by timestamp recency and/or content prefix.
7. Return `ActionResult` with best-effort `memo_id`.

### Failure Handling

- If editor input ref is missing, re-read page and retry.
- If still missing, use screenshot + request element selection once (human-in-the-loop fallback).
- If submit control cannot be confirmed, stop and report failure (do not guess blindly).

### Proven Fallback (JS + Vue/Tiptap, validated 2026-02-25)

When direct typing/clicking is unreliable in flomo's Tiptap editor:

1. Target top compose `.input-box` and its Tiptap editor `.tiptap.ProseMirror`.
2. Set content with Tiptap editor API (`editor.commands.setContent(...)`).
3. Submit through the `fl-editor` Vue instance (`.input-box.__vue__.onSubmit()`).
4. Verify by checking memo counter increment and locating the newly created memo via `memo_id` link + content marker.

## Edit Workflow (Default `replace`)

### Goal

Find one memo, confirm it, open detail/edit UI, replace full content, save, and verify.

### Steps

1. Run search workflow using text query (or use `memo_id` if the user provided one explicitly).
2. If multiple candidates match, present candidates and ask user to choose.
3. Once target candidate is chosen, restate:
   - `memo_id`
   - timestamp
   - snippet
   - action (`replace`)
4. Ask for explicit confirmation before editing.
5. Open the memo detail view by clicking timestamp/memo link.
6. In detail dialog/view, first verify whether the visible `More` button is a related-memo filter menu (observed on desktop); do not assume it is edit/delete.
7. Prefer a stable edit control if present. If not, use the target detail `Memo` component fallback and enter edit mode on that memo only.
8. Replace full memo content with new text.
9. Save/submit.
10. Re-open or re-read the target memo and verify key content changed.
11. Return `ActionResult`.

### Proven Fallback (JS + Vue/Tiptap, validated 2026-02-25)

For the selected target memo in detail view:

1. Resolve the visible detail-left `Memo` Vue instance by matching the target marker/snippet (and `memo_id` if available).
2. Enter edit mode via `Memo.changeToEditMode()`.
3. In that memo subtree, resolve descendant `.input-box` (`fl-editor`) and `.tiptap.ProseMirror`.
4. Set content with Tiptap `editor.commands.setContent(...)`.
5. Submit via the descendant `fl-editor` Vue instance `onSubmit()`.
6. Verify the `Memo` component exits edit mode and rendered content changes.

### Notes

- `append` and `prepend` are optional future modes. Default is `replace`.
- If the edit control cannot be located reliably and component fallback is unavailable, stop and report what was found.

## Delete Workflow

### Goal

Find one memo, confirm the target twice, delete via UI, and verify removal.

### Steps

1. Run search workflow using text query (or use `memo_id` if provided).
2. If multiple candidates match, present candidates and ask user to choose.
3. Present final deletion preview:
   - `memo_id`
   - timestamp
   - snippet (short)
4. Ask for explicit second confirmation.
5. Open the memo detail view.
6. Prefer a stable delete control and UI confirmation dialog when reliably detectable.
7. If the UI path is unstable, use the target detail `Memo` component fallback on the exact locked memo only.
8. Re-run a focused search for the same content / `memo_id` in current scan range to verify it is gone.
9. Return `ActionResult`.

### Proven Fallback (JS + Vue, validated 2026-02-25)

1. Resolve the exact target `Memo` Vue instance in detail view (locked by `memo_id` + snippet/marker).
2. Call `Memo.removeMemo(memo)` on that instance.
3. Wait for UI update.
4. Verify counters update (memo count decreases; tag count may also decrease if a tag becomes unused).
5. Close detail sheet.
6. Verify target text is no longer visible in the memo list.

### Hard Rule

Never execute deletion without the explicit second confirmation in the same interaction context.
