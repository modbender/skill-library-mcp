# UI Locators and Fallback Strategy

## Scope

This document defines practical locator strategy for flomo Web UI automation using Chrome MCP tools.

The UI can change. Prefer robust patterns over brittle absolute coordinates.

## General Locator Rules

1. Prefer `chrome_read_page` refs over coordinates.
2. Re-read the page before each major click because refs expire.
3. Lock targets by `memo_id` extracted from hrefs, not by visible text alone.
4. Use coordinates only for a single fallback step and only after screenshot confirmation.

## Known Useful Patterns (Observed)

### Live-Validated Hooks (2026-02-25, flomo desktop web)

These were verified in a real logged-in session via Chrome MCP and are currently the most reliable fallbacks when `chrome_read_page` refs are unstable:

- Top compose editor root: `.input-box`
- Top compose Tiptap editor DOM: `.input-box .tiptap.ProseMirror`
- Top compose Vue instance: `document.querySelector('.input-box').__vue__` (`fl-editor`)
- Top compose submit fallback: `document.querySelector('.input-box').__vue__.onSubmit()`
- Memo links: `a[href*="memo_id="]`
- Detail sheet root (desktop): `.memo-detail-sheet`
- Detail sheet close button: visible top-right button in sheet header (prefer fresh `chrome_read_page` ref)
- Detail sheet "More" menu: related-memo filter menu, not edit/delete
- Detail sheet target memo Vue instance fallback: the visible `Memo` component in the left pane (contains timestamp/body text)
- Edit-mode editor inside a memo card/detail memo: descendant `.input-box` (`fl-editor`) + `.tiptap.ProseMirror`

### Memo List Entry

Common signals in the memo stream:
- Timestamp links with href like `/mine/?memo_id=<ID>` or full `https://v.flomoapp.com/mine/?memo_id=<ID>`
- Nearby text blocks containing memo snippet/body preview
- Tag chips below snippet text

### Memo ID Extraction

Extract `memo_id` from any anchor href containing:
- `memo_id=`

Use this as the canonical target key for write actions.

### Detail View / Dialog

Observed behavior (desktop):
- Clicking a memo timestamp often opens a detail dialog in the same page (not always a full navigation)
- A sheet/dialog appears (observed text includes `Memo details`)
- The dialog usually includes timestamp link, body content, tags, and an action area (often top-right)
- The `More` button in the detail header may control related-memo filters rather than memo edit/delete actions

Practical implication:
- Do not assume detail-header `More` contains edit/delete.
- If edit/delete controls are not discoverable in the sheet header, use the embedded `Memo` component fallback (Vue methods or memo-local toolbar).

### Create Editor (Top Compose Area)

Observed behavior (desktop):
- Compose box appears near the top of the main memo column
- There is a text input area and a submit/send-like control
- Extra formatting buttons may appear below the compose box

Validated fallback path:
- Prefer UI refs (`chrome_read_page`) for editor and submit button.
- If typing/clicking is unreliable, use JS on `.input-box` (`fl-editor`) and Tiptap editor:
  - set content via `.tiptap.ProseMirror.editor.commands.setContent(...)`
  - submit via `.input-box.__vue__.onSubmit()`

## Read Strategy by Task

### Query/Search

- Use `chrome_get_web_content` for quick visible text pass
- Use `chrome_read_page` for structured anchor refs and timestamps
- Dedupe candidates by `memo_id`

### Create

- Use `chrome_read_page` to locate compose editor and submit control
- If not found, screenshot and fallback to `chrome_request_element_selection`

### Edit/Delete

- Click memo timestamp to open detail
- Re-read page after dialog appears
- Search within current page tree for dialog-like region and action controls
- Verify whether detail-header `More` is actually related-memo filtering (observed on 2026-02-25)
- If edit/delete is not exposed as a stable labeled control, use the target detail `Memo` Vue instance fallback:
  - edit fallback: `Memo.changeToEditMode()` -> edit descendant `fl-editor` -> `onSubmit()`
  - delete fallback: `Memo.removeMemo(memo)` on the matched target memo only
- After delete via component fallback, close the detail sheet and verify the memo is absent from the visible list

## Fallback Ladder

1. Re-read page (`chrome_read_page`)
2. Re-switch to flomo tab and re-read
3. Screenshot current viewport
4. `chrome_click_element` by ref (fresh refs)
5. `chrome_computer` coordinate click (single step)
6. `chrome_request_element_selection` human-in-the-loop fallback
7. Stop with a clear recoverable error

## What to Avoid

- Reusing stale refs after scrolls/dialog transitions
- Deleting based on text-only match without `memo_id` lock
- Multi-step coordinate automation without screenshots or confirmation
- Assuming mobile layout selectors match desktop layout
- Assuming the first visible `More` button in detail view is the memo action menu
