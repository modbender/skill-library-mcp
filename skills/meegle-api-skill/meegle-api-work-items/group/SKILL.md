---
name: meegle-api-work-item-group
description: |
  Meegle OpenAPI for work item group operations.
metadata:
  openclaw: {}
---

# Meegle API — Group

Work item group related APIs for organizing and managing work item groups.

## Scope

- Create, list, update work item groups
- Group membership and hierarchy
- Related group endpoints

---

## Invite BOTs into Groups

Add the specified Feishu robot to the group associated with the work item. The group must already exist and be bound to the work item.

### Points to Note

- **The Feishu Project bot must already be in the corresponding Feishu group** before using this interface.
- This interface **only supports adding the bot to the group associated with the work item** (not arbitrary groups).

### When to Use

- When inviting a Feishu/Lark bot into the work item’s associated group chat
- When automating group notifications or workflows for a work item’s group
- When the work item has an associated group and the bot needs to join it

### API Spec: invite_bots_into_groups

```yaml
name: invite_bots_into_groups
type: api
description: >
  Add the specified Feishu robot to the group associated with the work item.
  The Feishu Project bot must already be in the corresponding Feishu group.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_id}/bot_join_chat
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
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.

inputs:
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  app_ids:
    type: array
    items: string
    required: true
    description: >
      App ID(s) of the Feishu Open Platform application (bot).
      For acquisition, refer to Feishu Documentation.

outputs:
  data:
    type: object
    properties:
      chat_id: string
      failed_members: array
      success_members: array
    description: |
      chat_id: Associated group chat ID.
      failed_members: List of app_id that failed to join.
      success_members: List of app_id that successfully joined the chat.

constraints:
  - Permission: Permission Management – Work Item Instance
  - Feishu Project bot must already be in the Feishu group
  - Only adds bot to the group associated with the work item
  - app_ids cannot be empty

error_mapping:
  50006: Lark OpenAPI error (e.g. robot not in group; operator cannot be out of chat; bot invisible to user; no permission to invite; work item ID changed)
  30005: Work item not found
  20021: Chat ID not belong to work item (group not bound to this work item)
  20020: Bot app_ids empty
  20014: Project and work item not match (work item does not belong to this space)
```

### Usage notes

- **work_item_id**: Path parameter; the work item must have an associated group.
- **work_item_type_key**: Must match the type of the work item.
- **app_ids**: Feishu Open Platform App ID(s) of the bot(s) to invite; cannot be empty.
- Ensure the Feishu Project bot is already in the Feishu group before calling this API.
