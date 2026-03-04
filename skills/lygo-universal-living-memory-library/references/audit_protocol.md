# Audit Protocol (Living Memory)

## Goal
Detect drift, missing anchors, fragile items, and unreadable files.

## Steps
1) Load `core_files_index.json`.
2) Enforce `maxItems`.
3) For each item:
   - verify it exists (file/folder)
   - collect: mtime, size, sha256 (files only)
   - if tag includes FRAGILE -> flag it
4) Output:
   - PASS/FAIL summary
   - fragile review list
   - recommended next action

## Drift practice
- Drift is expected; the point is to *measure* it.
- If drift is acceptable: compress → mint → anchor.
- If drift is suspicious: isolate changes, request receipts.
