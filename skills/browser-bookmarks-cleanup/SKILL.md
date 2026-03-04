---
name: browser-bookmarks-cleanup
description: Analyze, organize, and clean browser bookmarks on macOS using on-disk bookmark and history files. Detects duplicates, stale bookmarks, tracking parameters, and folder issues. All writes are opt-in with backup and rollback.
---

# Browser Bookmark Cleanup

Analyze first, organize, then clean up. All writes are opt-in and reversible.

> **Supported browsers:** Chrome and Firefox out of the box. Other Chromium-based browsers (Edge, Brave, Arc, etc.) can be handled by pointing to their profile directories, which use the same Bookmarks JSON format as Chrome.

## Workflow

1. Discover browser profiles.
2. Run read-only analysis and share findings.
3. Propose cleanup plan with preview.
4. Get explicit user approval before any writes.
5. Dry-run first, then write with automatic backup.
6. Report changes and how to roll back.

## Hard Safety Rule

Never send network requests to bookmark URLs. Analysis uses only local files.

## Commands

Discover profiles:

```bash
python3 scripts/browser_bookmarks.py discover [--browser chrome|firefox]
```

Analyze bookmarks:

```bash
python3 scripts/browser_bookmarks.py analyze --bookmarks "<PATH>" --output /tmp/bookmark-analysis.json
```

Apply plan (dry-run by default, `--write` to commit):

```bash
python3 scripts/browser_bookmarks.py apply-plan --bookmarks "<PATH>" --plan /tmp/bookmark-plan.json [--write]
```

## Analysis Categories

1. Exact and semantic duplicate URLs
2. Tracking-parameter variants (`utm_*`, `gclid`, `fbclid`, etc.)
3. Subdomain and domain concentration
4. HTTP links that should be HTTPS
5. Empty, singleton, deep, and oversized folders
6. Weak bookmark names
7. Old bookmarks by age
8. Never-visited and stale bookmarks (from browser history)

## Approval Gate

Before any write: show plan preview, get explicit approval, ask user to close the browser.

## Plan Format

See `references/plan-schema.md` for the JSON plan structure.

## Rollback

Restore the timestamped backup file created before any write.
