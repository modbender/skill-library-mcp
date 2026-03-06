# Cleanup Plan JSON Schema

```json
{
  "name": "Conservative bookmark cleanup",
  "operations": [
    { "action": "delete", "selector": { "guid": "..." } },
    { "action": "create_folder", "parent": { "root": "bookmark_bar" }, "name": "Research" },
    { "action": "move", "selector": { "guid": "..." }, "target": { "path": "/bookmark_bar/Research" } },
    { "action": "rename", "selector": { "path": "/bookmark_bar/Old Folder" }, "new_name": "Archive" },
    { "action": "update_url", "selector": { "guid": "..." }, "new_url": "https://example.com/" }
  ]
}
```

## Actions

- `delete` — Remove a bookmark or folder.
- `create_folder` — Create a folder under a parent.
- `move` — Move a bookmark/folder to a target folder.
- `rename` — Rename a bookmark or folder.
- `update_url` — Change a bookmark's URL.

## Selectors

One form per selector:

- `{ "guid": "..." }` or `{ "id": "..." }` or `{ "key": "guid:..." }`
- `{ "path": "/bookmark_bar/Folder/Name" }`
- `{ "url": "https://..." }` (must match exactly one bookmark)
- `{ "root": "bookmark_bar" }` (for `parent`/`target` only)
