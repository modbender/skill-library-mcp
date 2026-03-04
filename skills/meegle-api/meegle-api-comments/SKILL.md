---
name: meegle-api-comments
description: Meegle OpenAPI for comments on work items.
metadata: { openclaw: {} }
---

# Meegle API — Comments

Add, list, update, delete comments on work items.

---

## Add Comments

Add a comment under the specified work item. The comment appears on the Comments/Notes tab of the work item details page and is marked as added by the plugin.

### When to Use

- When adding a plain text or rich text comment to a work item
- When logging notes or feedback on work items via the plugin
- When syncing external comments into Meegle

### API Spec: add_comments

```yaml
name: add_comments
type: api
description: Add comment under work item; content or rich_text required (rich_text precedence).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comment/create" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { content: string, rich_text: object }
outputs: { data: integer }
constraints: [Permission: Comment, content or rich_text required]
error_mapping: { 10211: Token invalid, 30001: Data not found, 50001: No permission, 1000051280: Rich text invalid }
```

### Usage notes

- **content**: Plain text only; use for simple comments.
- **rich_text**: Use for formatted comments; follow Rich Text Format; Markdown not supported.

---

## Search Comments

Obtain all comment information under the specified work item. Results are returned in ascending order of creation time.

### When to Use

- When listing comments on a work item
- When building comment threads or activity feeds
- When syncing or auditing work item comments

### API Spec: search_comments

```yaml
name: search_comments
type: api
description: List comments under work item; ascending by creation time.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comments" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { page_size: { type: integer, max: 200 }, page_num: { type: integer, default: 1 } }
outputs: { data: array, pagination: object }
constraints: [Permission: Comments, page_size max 200]
error_mapping: { 1000051135: Work item not found, 1000051280: Params invalid, 1000051256: No permission, 20002: Page size limit }
```

### Usage notes

- **project_key, work_item_type_key, work_item_id**: Path parameters identifying the work item.
- **page_num / page_size**: Optional pagination; page_size max 200.

---

## Update Comments

Update the content of a specified comment. The updated comment is marked as added by the plugin.

### Tip

**Only the creator of the comment can update it.**

### When to Use

- When editing a comment created by the plugin
- When correcting or revising comment content
- When syncing updated content from external systems

### API Spec: update_comments

```yaml
name: update_comments
type: api
description: Update comment; only creator can update; content or rich_text required.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comment/{comment_id}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string, comment_id: string }
inputs: { content: string, rich_text: object }
outputs: { data: object }
constraints: [Permission: Comment, only creator, content or rich_text required]
error_mapping: { 10211: Token invalid, 1000051280: Params invalid }
```

### Usage notes

- **comment_id**: Path parameter; obtain via Search Comments.
- **content** or **rich_text**: At least one required; when both present, rich_text takes precedence.

---

## Delete Comments

Delete a specified comment under the work item.

### Tip

**Only the creator of the comment can delete it.** Deletion can only be done through API operations (not via the UI).

### When to Use

- When removing a comment created by the plugin
- When cleaning up obsolete or incorrect comments
- When syncing deletions from external systems

### API Spec: delete_comments

```yaml
name: delete_comments
type: api
description: Delete comment; only creator can delete; API-only.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: DELETE, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comment/{comment_id}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string, comment_id: string }
outputs: {}
constraints: [Permission: Comments, only creator]
error_mapping: { 1000050052: Comment not found, 20014: Project/work item mismatch, 10211: Token invalid, 10001: No permission }
```

### Usage notes

- **comment_id**: Path parameter; obtain via Search Comments.
- Deletion is API-only; cannot delete comments through the Meegle UI.
