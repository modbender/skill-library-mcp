---
name: meegle-api-work-item-tasks
description: |
  Meegle OpenAPI for work item task operations.
metadata:
  openclaw: {}
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
description: >
  Search for subtasks that meet input conditions across spaces.
  Only spaces where the plugin is installed. Max 5000 results.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/subtask/search
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_keys:
    type: array
    items: string
    required: false
    description: >
      Space IDs to query. Obtain by double-clicking space name in Meegle.
      If neither project_keys nor simple_names is provided, defaults to spaces
      where the plugin is installed and user_key in header can access.
      Union of project_keys and simple_names cannot exceed 10.
  simple_names:
    type: array
    items: string
    required: false
    description: >
      Space simple_name list. From space URL, e.g. https://project.feishu.cn/doc/overview → doc.
      Same default and limit as project_keys; union with project_keys max 10.
  page_size:
    type: integer
    required: false
    default: 50
    description: Page size. Default 50. Total results cap 5000.
  page_num:
    type: integer
    required: false
    default: 1
    description: Page number. Default 1.
  name:
    type: string
    required: false
    description: Subtask name, fuzzy match.
  user_keys:
    type: array
    items: string
    required: false
    description: >
      Subtask owner user_keys. Own: double-click avatar in Meegle; others: Get Tenant User List.
  status:
    type: integer
    required: false
    enum: [0, 1]
    description: |
      0: In progress
      1: Completed
  created_at:
    type: object
    required: false
    properties:
      start: integer
      end: integer
    description: >
      Creation time interval (millisecond timestamps, 13-digit).
      If end is omitted, current time is used as default.

outputs:
  data:
    type: array
    description: >
      Subtask list. Max 5000 total. Each item includes work_item_id, work_item_name,
      node_id, sub_task (id, name, owners, assignee, schedules, passed, actual_begin_time, etc.).
  pagination:
    type: object
    properties:
      page_num: integer
      page_size: integer
      total: integer

constraints:
  - Permission: Permission Management – Subtasks
  - Union of project_keys and simple_names max 10
  - Total results max 5000; refine filters if exceeded
  - created_at must be 13-digit millisecond timestamps

error_mapping:
  20094: Search result exceeds 5000 (refine search params)
  20013: Invalid time interval (not millisecond timestamps)
  20057: project_keys and simple_names union exceeds 10
  50006: Operate fail (contact platform)
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
description: >
  Obtain detailed information of subtasks on the specified work item instance.
  Returns nodes and their sub_tasks. Work item must be workflow (node-flow) mode.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/task
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
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.

inputs:
  node_id:
    type: string
    required: false
    description: >
      state_key of the target node; query subtasks of that node only.
      Obtain from Get a List of Specified Tasks (Across Space) (node_id / state_key).
      If omitted, returns subtasks of all nodes.

outputs:
  data:
    type: array
    description: >
      Array of nodes, each with id, state_key, node_name, template_id, version, sub_tasks.
      sub_tasks: array of task objects (id, name, owners, assignee, schedules, fields,
      passed, actual_begin_time, actual_finish_time, role_assignee, etc.).

constraints:
  - Permission: Permission Management – Work Item Instance
  - Work item must be workflow (node-flow) mode

error_mapping:
  20018: Node ID not exist in workflow (node_id incorrect)
  50006: Work item is not workflow mode
  30005: Work item not found (check project_key, work_item_type_key, work_item_id)
  10001: Operation not permitted (no permission)
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
description: >
  Create a subtask on a specified node of a work item instance.
  Work item must be workflow mode. name and node_id are required.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/task
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
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID to which the new subtask belongs.

inputs:
  node_id:
    type: string
    required: true
    description: >
      Target node ID (equivalent to node state_key). Obtain via Get Workflow Details.
  name:
    type: string
    required: true
    description: Name of the subtask.
  alias_key:
    type: string
    required: false
    description: Docking identifier of the target node for external system reference.
  assignee:
    type: array
    items: string
    required: false
    description: >
      List of user_key for subtask owners. Use only when node owner assignment is NOT "linked with roles".
      Cannot be set together with role_assignee.
  role_assignee:
    type: array
    items: object
    required: false
    description: >
      List of role owners (RoleOwner structure: role ID + owners user_key array).
      Use only when node owner assignment is "linked with roles".
      Cannot be set together with assignee.
  schedule:
    type: object
    required: false
    description: Scheduling information. Follow Schedule structure.
  note:
    type: string
    required: false
    description: Remarks for the subtask.
  field_value_pairs:
    type: array
    items: object
    required: false
    description: Custom fields and values. Follow FieldValuePair structure.

outputs:
  data:
    type: integer
    description: ID of the successfully created subtask.

constraints:
  - Permission: Permission Management – Work Item Instance
  - Work item must be workflow (node-flow) mode
  - name and node_id are required
  - Do not set both assignee and role_assignee

error_mapping:
  20018: Node ID not exist in workflow (node_id incorrect)
  20007: Work item is already aborted (cannot operate on terminated work items)
  20005: Missing param (name required, or node_id required)
  30005: Work item not found
  20090: Request intercepted
  20047: role_assignee and assignee cannot be set together
  30015: Record not found (workflow err)
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
description: >
  Update detailed information of a subtask on the specified node of a work item instance.
  For subtask custom fields, Update Work Item with work_item_type_key=sub_task is also supported.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/{node_id}/task/{task_id}
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
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.
  node_id:
    type: string
    required: true
    description: Target node ID (equivalent to node state_key). Obtain via Get Workflow Details.
  task_id:
    type: string
    required: true
    description: Subtask ID. Returned by Create Tasks or from Get Task Details (sub_task.id).

inputs:
  name:
    type: string
    required: false
    description: Subtask name.
  assignee:
    type: array
    items: string
    required: false
    description: >
      List of user_key for subtask owners. Use when node owner type is not role-based.
      Cannot be set together with role_assignee.
  role_assignee:
    type: array
    items: object
    required: false
    description: >
      List of role owners (RoleOwner: role + owners). Use when node owner type is role assignee.
      Cannot be set together with assignee.
  schedule:
    type: object
    required: false
    description: Scheduling information. Follow Schedule structure.
  note:
    type: string
    required: false
    description: Remarks for the subtask.
  deliverable:
    type: array
    items: object
    required: false
    description: Deliverables. Follow FieldValuePair structure.
  update_fields:
    type: array
    items: object
    required: false
    description: >
      Fields to update. Follow FieldValuePair structure. Updated values overwrite previous ones.

outputs:
  description: Success returns err_code 0.

constraints:
  - Permission: Permission Management – Work Item Instance
  - Do not set both assignee and role_assignee

error_mapping:
  20007: Work item is already aborted (terminated)
  30005: Work item not found
  20046: Task ID not exist in workflow
  20018: Node ID not exist in workflow
  20090: Request intercepted
  20050: Field option value wrong (config updated)
  50006: No right to edit (no permission to edit this subtask)
  20047: role_assignee and assignee cannot be set together
  30009: Field not found
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
description: >
  Complete or roll back a subtask on a specified node of a work item instance.
  Optionally update assignee, schedules, deliverable, or note during the operation.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/subtask/modify
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
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.

inputs:
  node_id:
    type: string
    required: true
    description: Target node ID (equivalent to state_key). Obtain via Get Workflow Details.
  task_id:
    type: integer
    required: true
    description: Subtask ID. Obtain via Get a List of Specified Tasks (Across Space) or Get Task Details.
  action:
    type: string
    required: true
    enum: [confirm, rollback]
    description: |
      confirm: Complete the subtask
      rollback: Roll back the subtask
  assignee:
    type: array
    items: string
    required: false
    description: List of user_key for subtask leaders. Use when node leader type is non-role.
  role_assignee:
    type: array
    items: object
    required: false
    description: >
      Role owners (RoleOwner structure). Use when node responsible person type is role assignee.
      Can update subtask fields while completing/rolling back.
  schedules:
    type: array
    items: object
    required: false
    description: Schedule structure. Can update subtask schedule during complete/rollback.
  deliverable:
    type: array
    items: object
    required: false
    description: Deliverables. Follow FieldValuePair structure.
  note:
    type: string
    required: false
    description: Remarks. Can update note during complete/rollback.

outputs:
  description: Success returns err_code 0.

constraints:
  - Permission: Permission Management – Work Item Instance
  - action must be confirm or rollback

error_mapping:
  50006: Subtask already confirmed (refresh and try again) or task deliverable error (required deliverable not entered)
  30005: Work item not found
  20090: Request intercepted
  20082: Action not supported (use confirm or rollback)
  20046: Task ID not exist in workflow
  20005: Missing param (node_id, task_id, or action required)
  20018: Node ID not exist in workflow
  20007: Work item is already aborted (terminated)
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
description: >
  Delete a subtask in the specified work item instance.
  No body; subtask identified by path parameters.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/task/{task_id}
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
    description: >
      Work item type. Obtainable via "Get work item types in the space".
      Must match the work item instance identified by work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.
  task_id:
    type: string
    required: true
    description: Subtask ID. Obtain via Get a List of Specified Tasks (Across Space) or Get Task Details (sub_task.id).

outputs:
  description: Success returns err_code 0.

constraints:
  - Permission: Permission Management – Work Item Instance

error_mapping:
  20007: Work item is already aborted (terminated)
  20090: Request intercepted
  30005: Work item not found
```

### Usage notes

- **task_id**: Path parameter; from task list (across space) or Get Task Details (sub_task.id).
- No request body; use DELETE with path only.
