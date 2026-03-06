---
name: meegle-api-work-item-tasks
description: Meegle OpenAPI for work item task operations.
metadata: { openclaw: {} }
---

# Meegle API — Tasks

Task related APIs for managing work item tasks in Meegle spaces.

## Scope

- Task creation, retrieval, update
- Task lifecycle and status
- Task-related endpoints

---

## Get a List of Specified Tasks (Across Space)

Search for subtasks that meet the input conditions across spaces. Only spaces where the plugin is installed are queried. Max 5000 results; use filters to stay within limit.

### When to Use

- When listing subtasks across one or more spaces
- When filtering by name, owner (user_keys), status, or creation time
- When building task dashboards or reports across projects

### API Spec: get_task_list_across_space

```yaml
name: get_task_list_across_space
type: api
description: Search subtasks across spaces; plugin-installed spaces only; max 5000 results.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/subtask/search" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_keys: array, simple_names: array, page_size: integer, page_num: integer, name: string, user_keys: array, status: integer (0|1), created_at: object }
outputs: { data: array, pagination: object }
constraints: [Subtasks permission, project_keys+simple_names union max 10, max 5000 results, created_at 13-digit ms]
error_mapping: { 20094: Exceeds 5000, 20013: Invalid time interval, 20057: project_keys+simple_names exceeds 10, 50006: Operate fail }
```

### Usage notes

- **project_keys** or **simple_names**: Optional; omit to query all accessible spaces where the plugin is installed. Combined count max 10.
- **status**: 0 = In progress, 1 = Completed.
- **created_at**: Use 13-digit millisecond timestamps; omit end for “until now”.

---

## Get Task Details

Obtain the detailed information of subtasks on the specified work item instance. Returns nodes and their associated subtask data. The work item must be a workflow (node-flow) type.

### When to Use

- When fetching all subtasks for a work item, optionally filtered by node
- When building task lists or progress views for a single work item
- When syncing or auditing subtask data

### API Spec: get_task_details

```yaml
name: get_task_details
type: api
description: Subtask details for a work item; nodes and sub_tasks; workflow (node-flow) only.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/task" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { node_id: string }
outputs: { data: array }
constraints: [Work Item Instance permission, node-flow only]
error_mapping: { 20018: Node ID not exist, 50006: Not workflow mode, 30005: Work item not found, 10001: No permission }
```

### Usage notes

- **node_id**: Optional query parameter; use to limit results to one node’s subtasks. Same as node state_key; obtain from task list response.
- **data**: List of nodes; each node has sub_tasks array with full task details (id, name, owners, schedules, passed, etc.).

---

## Create Tasks

Create a subtask on a specified node of a work item instance. The work item must be a workflow (node-flow) type. Requires `name` and `node_id`.

### When to Use

- When adding a new subtask to a workflow node
- When creating tasks with assignees, schedule, or custom fields
- When automating task creation from external systems

### API Spec: create_tasks

```yaml
name: create_tasks
type: api
description: Create subtask on a node; workflow mode; name and node_id required.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/task" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { node_id: string, name: string, alias_key: string, assignee: array, role_assignee: array, schedule: object, note: string, field_value_pairs: array }
outputs: { data: integer }
constraints: [Work Item Instance permission, node-flow, name+node_id required, not both assignee and role_assignee]
error_mapping: { 20018: Node ID not exist, 20007: Work item aborted, 20005: Missing param, 30005: Work item not found, 20090: Request intercepted, 20047: assignee and role_assignee both set, 30015: Record not found }
```

### Usage notes

- **node_id**, **name**: Required. Get node_id (state_key) from Get Workflow Details or Get Task Details.
- **assignee** vs **role_assignee**: Use one only, depending on whether the node’s owner assignment is "linked with roles" (use role_assignee) or not (use assignee).
- **schedule**: Follow the Schedule structure used in task list/details responses.

---

## Update Tasks

Update the detailed information of a subtask on the specified node of a work item instance. For updating custom fields of subtasks, you can also use Update Work Item with `work_item_type_key=sub_task`.

### When to Use

- When editing a subtask’s name, assignees, schedule, note, deliverables, or custom fields
- When syncing task updates from external systems
- When changing role_assignee or assignee (use one only)

### API Spec: update_tasks

```yaml
name: update_tasks
type: api
description: Update subtask on a node; custom fields also via Update Work Item work_item_type_key=sub_task.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/{node_id}/task/{task_id}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string, node_id: string, task_id: string }
inputs: { name: string, assignee: array, role_assignee: array, schedule: object, note: string, deliverable: array, update_fields: array }
outputs: err_code 0
constraints: [Work Item Instance permission, not both assignee and role_assignee]
error_mapping: { 20007: Work item aborted, 30005: Work item not found, 20046: Task ID not exist, 20018: Node ID not exist, 20090: Request intercepted, 20050: Field option wrong, 50006: No right to edit, 20047: assignee and role_assignee both set, 30009: Field not found }
```

### Usage notes

- **task_id**: Path parameter; from Create Tasks response or Get Task Details (sub_task.id).
- **assignee** vs **role_assignee**: Use one only; same rule as Create Tasks.
- **update_fields**: FieldValuePair list; values overwrite previous. For more custom fields, consider Update Work Item with work_item_type_key=sub_task.

---

## Complete/Rollback Tasks

Complete or roll back a subtask on a specified node of a work item instance. Optionally update assignee, role_assignee, schedules, deliverable, or note during the operation.

### When to Use

- When marking a subtask as complete (confirm) or rolling it back (rollback)
- When updating deliverable, schedule, or note while completing/rolling back
- When syncing task status from external systems

### API Spec: complete_or_rollback_tasks

```yaml
name: complete_or_rollback_tasks
type: api
description: Complete (confirm) or roll back a subtask; optionally update assignee, schedules, deliverable, note.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/subtask/modify" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { node_id: string, task_id: integer, action: confirm|rollback, assignee: array, role_assignee: array, schedules: array, deliverable: array, note: string }
outputs: err_code 0
constraints: [Work Item Instance permission, action confirm or rollback]
error_mapping: { 50006: Already confirmed or deliverable error, 30005: Work item not found, 20090: Request intercepted, 20082: Action not supported, 20046: Task ID not exist, 20005: Missing param, 20018: Node ID not exist, 20007: Work item aborted }
```

### Usage notes

- **action**: `confirm` to complete, `rollback` to roll back.
- **task_id**: From task list (across space) or Get Task Details (sub_task.id).
- Optional **assignee**, **role_assignee**, **schedules**, **deliverable**, **note** update subtask fields during the operation; complete may require deliverable to be set.

---

## Delete Tasks

Delete a subtask in the specified work item instance. No request body; identify the subtask by path parameters.

### When to Use

- When removing a subtask from a work item
- When cleaning up or reorganizing workflow tasks
- When syncing deletions from external systems

### API Spec: delete_tasks

```yaml
name: delete_tasks
type: api
description: Delete subtask; no body; identify by path (project_key, work_item_type_key, work_item_id, task_id).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: DELETE, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/task/{task_id}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string, task_id: string }
outputs: {}
constraints: [Permission: Work Item Instance]
error_mapping: { 20007: Work item aborted, 20090: Request intercepted, 30005: Work item not found }
```

### Usage notes

- **task_id**: Path parameter; from task list (across space) or Get Task Details (sub_task.id).
- No request body; use DELETE with path only.
