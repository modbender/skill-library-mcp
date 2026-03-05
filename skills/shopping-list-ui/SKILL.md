---
name: shopping-list-ui
version: 1.0.0
description: >
  Web UI for the shopping-list skill. Adds a /shopping page to Second Brain
  with full CRUD — view, add, edit, check off, and delete items. Requires
  the shopping-list skill to be installed (shares the same data files).
---

# Shopping List UI

Web interface for managing the shopping list. Adds a `/shopping` page to the
Second Brain portal with categorized list view and inline editing.

## Prerequisites

- Second Brain portal running (Next.js)
- `shopping-list` skill installed (`clawhub install shopping-list`)

## Files

This skill adds the following files to the Second Brain app:

| File | Purpose |
|------|---------|
| `second-brain/src/lib/shopping.ts` | Data layer — reads/writes shopping-list skill JSON files |
| `second-brain/src/app/api/shopping/route.ts` | GET list + POST add item |
| `second-brain/src/app/api/shopping/[id]/route.ts` | PUT edit, DELETE remove, PATCH check-off |
| `second-brain/src/app/shopping/page.tsx` | Shopping list page with CRUD UI |

Also modifies:
- `second-brain/src/components/Sidebar.tsx` — adds Shopping nav entry
- `second-brain/src/components/SFIcon.tsx` — adds cart.fill icon

## Data

Reads and writes `skills/shopping-list/data/active.json` — the same file used
by the conversational shopping-list CLI skill. Changes made in the web UI are
immediately visible in chat, and vice versa.

User identity for `addedBy` is read from `skills/shopping-list/data/config.json`.
If not set, defaults to "web".
