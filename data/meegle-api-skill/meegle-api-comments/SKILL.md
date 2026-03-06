---
name: meegle-api-comments
description: |
  Meegle OpenAPI for comments on work items or other entities.
metadata:
  openclaw: {}
---

# Meegle API — Comments

Comment-related OpenAPIs (e.g. add, list, update comments on work items). Use when you need to create or query comments.

## Scope

This skill covers comment operations including:

- Create comment on work items or other entities
- List comments
- Update and delete comments
- Related comment endpoints

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
description: >
  Add a comment under the specified work item. The comment appears on the
  Comments/Notes tab and is marked as added by the plugin.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comment/create
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtainable via "Get work item types in the space".
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, expand ··· in the upper right, click ID.

inputs:
  content:
    type: string
    required: false
    description: >
      Plain text comment content. Either content or rich_text required; both cannot be empty.
      When both have values, rich_text takes precedence.
  rich_text:
    type: object
    required: false
    description: >
      Rich text format. Either content or rich_text required; rich_text takes precedence when both present.
      Refer to Rich Text Format. Direct Markdown is not supported.

outputs:
  data:
    type: integer
    description: ID of the newly created comment.

constraints:
  - Permission: Permission Management – Comment
  - Either content or rich_text must be provided (both cannot be empty)
  - When both provided, rich_text takes precedence

error_mapping:
  10211: Token info invalid (user_key is empty)
  30001: Data not found (project_key error)
  50001: Create fail (no permission to comment)
  1000051280: Params invalid (rich text format incorrect; refer to Rich Text Format)
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
description: >
  Obtain all comment information under the specified work item.
  Results returned in ascending order of creation time.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comments
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtainable via "Get work item types in the space".
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, expand ··· in the upper right, click ID.

inputs:
  page_size:
    type: integer
    required: false
    constraints:
      max: 200
    description: Items per page. Max 200.
  page_num:
    type: integer
    required: false
    default: 1
    description: Page number, 1-based. Default 1.

outputs:
  data:
    type: array
    items:
      id: integer
      work_item_id: integer
      work_item_type_key: string
      created_at: integer
      operator: string
      content: string
    description: |
      Comment list. id: comment ID; operator: user_key; created_at: millisecond timestamp.
  pagination:
    type: object
    properties:
      total: integer
      page_num: integer
      page_size: integer
    description: Pagination info (total, page_num, page_size).

constraints:
  - Permission: Permission Management – Comments
  - page_size max 200

error_mapping:
  1000051135: Work item not found (work item does not exist)
  1000051280: Params invalid (user_key, work_item_id, or work_item_type_key is empty)
  1000051256: No permission (no permission to query comments)
  20002: Page size limit (page size exceeds 200)
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
description: >
  Update the content of a specified comment. The updated comment is marked
  as added by the plugin. Only the creator can update.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comment/{comment_id}
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtainable via "Get work item types in the space".
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, expand ··· in the upper right, click ID.
  comment_id:
    type: string
    required: true
    description: Comment ID. Obtainable via Search Comments.

inputs:
  content:
    type: string
    required: false
    description: >
      Plain text comment content. Either content or rich_text required; both cannot be empty.
      When both have values, rich_text takes precedence.
  rich_text:
    type: object
    required: false
    description: >
      Rich text format. Either content or rich_text required; rich_text takes precedence when both present.
      Refer to Rich Text Format. Direct Markdown is not supported.

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Comment
  - Only the creator of the comment can update it
  - Either content or rich_text must be provided (both cannot be empty)

error_mapping:
  10211: Token info invalid (access authorization expired; re-obtain access)
  1000051280: Params invalid (rich text format error)
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
description: >
  Delete a specified comment under the work item.
  Only the creator can delete; deletion is API-only.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/comment/{comment_id}
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtainable via "Get work item types in the space".
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, expand ··· in the upper right, click ID.
  comment_id:
    type: string
    required: true
    description: Comment ID. Obtainable via Search Comments.

outputs:
  description: Success returns err_code 0.

constraints:
  - Permission: Permission Management – Comments
  - Only the creator of the comment can delete it

error_mapping:
  1000050052: Db record not found (comment_id incorrect)
  20014: Project and work item not match (project_key does not match work item)
  10211: Token info invalid (token expired)
  10001: No permission (only creator can delete)
```

### Usage notes

- **comment_id**: Path parameter; obtain via Search Comments.
- Deletion is API-only; cannot delete comments through the Meegle UI.
