# Ghost Catalog Header Templates

## Python / Shell / YAML / Ruby

```python
# ==============================================================================
# file_id: SOM-XXX-NNNN-vX.X.X
# name: filename.py
# description: Brief description of what this file does
# project_id: PROJECT-NAME
# category: script
# tags: [tag1, tag2, tag3]
# created: YYYY-MM-DD
# modified: YYYY-MM-DD
# version: X.X.X
# agent_id: AGENT-DROID-001
# ==============================================================================
```

## JavaScript / TypeScript

```typescript
// =============================================================================
// file_id: SOM-XXX-NNNN-vX.X.X
// name: filename.ts
// description: Brief description of what this file does
// project_id: PROJECT-NAME
// category: library
// tags: [tag1, tag2, tag3]
// created: YYYY-MM-DD
// modified: YYYY-MM-DD
// version: X.X.X
// agent_id: AGENT-DROID-001
// =============================================================================
```

## CSS / SCSS

```css
/* =============================================================================
 * file_id: SOM-XXX-NNNN-vX.X.X
 * name: filename.css
 * description: Brief description of what this file does
 * project_id: PROJECT-NAME
 * category: style
 * tags: [tag1, tag2, tag3]
 * created: YYYY-MM-DD
 * modified: YYYY-MM-DD
 * version: X.X.X
 * agent_id: AGENT-DROID-001
 * ============================================================================= */
```

## Markdown

```markdown
<!--
file_id: SOM-XXX-NNNN-vX.X.X
name: filename.md
description: Brief description of what this file does
project_id: PROJECT-NAME
category: doc
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
modified: YYYY-MM-DD
version: X.X.X
agent_id: AGENT-DROID-001
-->
```

## SQL

```sql
-- =============================================================================
-- file_id: SOM-XXX-NNNN-vX.X.X
-- name: filename.sql
-- description: Brief description of what this file does
-- project_id: PROJECT-NAME
-- category: schema
-- tags: [tag1, tag2, tag3]
-- created: YYYY-MM-DD
-- modified: YYYY-MM-DD
-- version: X.X.X
-- agent_id: AGENT-DROID-001
-- =============================================================================
```

## HTML / XML

```html
<!--
  file_id: SOM-XXX-NNNN-vX.X.X
  name: filename.html
  description: Brief description of what this file does
  project_id: PROJECT-NAME
  category: component
  tags: [tag1, tag2, tag3]
  created: YYYY-MM-DD
  modified: YYYY-MM-DD
  version: X.X.X
  agent_id: AGENT-DROID-001
-->
```

## JSON (as top-level `_catalog` key)

JSON does not support comments. For JSON files that support arbitrary keys,
add a `_catalog` object at the top level:

```json
{
  "_catalog": {
    "file_id": "SOM-CFG-NNNN-vX.X.X",
    "name": "config.json",
    "description": "Application configuration",
    "project_id": "PROJECT-NAME",
    "category": "config",
    "tags": ["config", "settings"],
    "created": "YYYY-MM-DD",
    "modified": "YYYY-MM-DD",
    "version": "X.X.X",
    "agent_id": "AGENT-DROID-001"
  }
}
```

For JSON files where adding keys would break the schema (e.g., `package.json`, `tsconfig.json`),
skip the header and register the file in the catalog DB only (no inline header).
