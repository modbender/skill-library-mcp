---
name: meegle-api-work-item-group
description: Meegle OpenAPI for work item group operations.
metadata: { openclaw: {} }
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
description: Add Feishu bot to work item's associated group; bot must already be in Feishu group.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_id}/bot_join_chat" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_id: string }
inputs: { work_item_type_key: string, app_ids: { type: array, required: true } }
outputs: { data: { chat_id: string, failed_members: array, success_members: array } }
constraints: [Permission: Work Item Instance, bot in group, app_ids non-empty]
error_mapping: { 50006: Lark OpenAPI error, 30005: Work item not found, 20021: Chat not belong to work item, 20020: app_ids empty, 20014: Project/work item mismatch }
```

### Usage notes

- **work_item_id**: Path parameter; the work item must have an associated group.
- **work_item_type_key**: Must match the type of the work item.
- **app_ids**: Feishu Open Platform App ID(s) of the bot(s) to invite; cannot be empty.
- Ensure the Feishu Project bot is already in the Feishu group before calling this API.
