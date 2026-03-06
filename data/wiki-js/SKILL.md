---
name: Wiki.js
description: Deploy and manage Wiki.js documentation sites avoiding common configuration traps.
metadata: {"clawdbot":{"emoji":"📖","os":["linux","darwin","win32"]}}
---

## Critical Initial Config
- Site URL must be correct from first setup — changing later breaks all internal links, no easy fix
- PostgreSQL over SQLite for any multi-user setup — SQLite locks under concurrent writes
- HTTPS terminates at reverse proxy — Wiki.js runs HTTP internally, don't configure SSL in Wiki.js

## Editor Traps
- Visual Editor uses HTML underneath — switching from Markdown loses formatting, can't switch back cleanly
- Markdown editor is the safe default — WYSIWYG has rendering quirks and sync issues
- Internal links require locale prefix — `[Link](/en/path/to/page)` not just `/path/to/page`

## Permission Pitfalls
- Deny rules take precedence over allow — overlapping patterns cause unexpected lockouts
- Page rules use path patterns — `/engineering/*` covers subpages, `/engineering` is exact match only
- Default "Users" group applies to all new accounts — configure before inviting users

## Storage and Sync
- Git sync is one-way by default — Wiki.js to Git only, external edits don't sync back
- Asset storage in database bloats backups — use S3/GCS for images on larger wikis
- Database backup IS the complete backup — all content, users, permissions stored there

## Search Behavior
- Search respects permissions — users don't find pages they can't access (can cause confusion)
- Search index rebuilds automatically — large imports need patience, no manual trigger helps
- Elasticsearch optional — built-in DB search works but lacks relevance ranking

## Troubleshooting Specifics
- Login redirect loops — almost always HTTPS/HTTP mismatch in Site URL config
- Assets not loading — Site URL doesn't match actual access URL
- Page shows 404 after creation — special characters in path, use lowercase alphanumeric
- Slow after import — search reindexing in progress, wait or check Admin > Utilities
