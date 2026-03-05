---
name: meegle-api-work-item-read-and-write
description: |
  Meegle OpenAPI for creating, reading, and updating work items.
metadata:
  openclaw: {}
---

# Meegle API — Work Item Read & Write

Create, get, and update work items in a Meegle space.

---

## Get Work Item Creation Metadata

Retrieve creation metadata (field configuration) for a specific work item type in a Meegle space. This metadata is required to correctly construct payloads for creating or updating work items.

### When to Use

- Before creating or updating work items — to get field definitions, required fields, and default values
- When building field_value_pairs for the create/update API
- When needing option IDs, compound field structure, or role assignment configuration

### API Spec: get_work_item_creation_metadata

```yaml
name: get_work_item_creation_metadata
type: api
description: >
  Retrieve creation metadata (field configuration) for a specific work item type
  in a Meegle space. This metadata is required to correctly construct payloads
  for creating or updating work items.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/meta
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space project_key or simple_name.
      project_key can be obtained by double-clicking the space name.
  work_item_type_key:
    type: string
    required: true
    description: Work item type key in the space

outputs:
  data:
    type: array
    description: >
      Field configuration list (FieldConf), including required fields,
      default values, compound fields, and role assignments.

error_mapping:
  20044: Work item type has been disabled
  30014: Work item type not found
```

### Usage notes

- **project_key, work_item_type_key**: Path parameters identifying the space and work item type.
- Call this API before **Create Work Item** to get field metadata; use the result to build `field_value_pairs` with correct option IDs and structure.

---

## Get Work Item Details

Retrieve detailed information for one or more work item instances under a specified Meegle space and work item type. Returns full detail-page data including system fields, custom fields, workflow status, and node/state info.

### When to Use

- When fetching full detail for specific work items by ID
- When needing workflow state history, current nodes, or full field list
- When building detail views or syncing work item data

### API Spec: get_work_item_details

```yaml
name: get_work_item_details
type: api
description: >
  Retrieve detailed information for one or more work item instances under a
  specified Meegle space and work item type. Returns full detail-page data
  including system fields, custom fields, workflow status, and node/state info.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/query
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space identifier. Can be the space project_key or space domain name
      (simple_name).
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type key (e.g. story, bug). Obtainable via
      "Get work item types in the space".

inputs:
  work_item_ids:
    type: array
    items: integer
    required: true
    constraints:
      max_items: 50
    description: >
      List of work item instance IDs. Maximum 50 per request.
  fields:
    type: array
    items: string
    required: false
    description: |
      Field filtering rules.
      - Specify fields: ["owner","description"]
      - Exclude fields: ["-owner","-description"]
      These two modes cannot be mixed.
  expand:
    type: object
    required: false
    description: Additional expansion parameters (reserved for extended query behavior).

outputs:
  data:
    type: array
    description: >
      Work item detail objects. Includes base attributes (id, name, status,
      timestamps), workflow state history, current nodes, and full field list.

constraints:
  - work_item_ids max 50 per request

error_mapping:
  30005: Work item not found (invalid or non-existent work_item_ids)
  20028: work_item_ids exceeds 50
  30014: Work item type not found (invalid work_item_type_key)
```

### Usage notes

- **project_key, work_item_type_key**: Path parameters for the space and work item type.
- **work_item_ids**: Required; max 50 IDs per request.
- **fields**: Use positive values to specify returned fields, or prefix with `-` to exclude; do not mix modes.

---

## Create Work Item

Create a new work item in a Meegle space. Supports multiple work item types, templates, and custom fields. Requires permission: Work Items.

### When to Use

- When creating a new task, story, bug, or other work item
- When persisting structured work into Meegle
- When initializing workflows or planning items programmatically

### API Spec: create_work_item

```yaml
name: meegle.create_work_item
description: >
  Create a new work item in a specified Meegle space.
  Supports different work item types, templates, and custom fields.
  Requires permission: Work Items.

when_to_use:
  - When creating a new task, story, bug, or other work item
  - When an AI needs to persist structured work into Meegle
  - When initializing workflows or planning items programmatically

http:
  method: POST
  path: /open_api/{project_key}/work_item/create
  auth: plugin_access_token

path_parameters:
  project_key:
    type: string
    required: true
    description: Space ID (project_key) or space domain name (simple_name)

body_parameters:
  work_item_type_key:
    type: string
    required: false
    description: Work item type key (e.g. story, task, bug)

  template_id:
    type: integer
    required: false
    description: >
      Work item process template ID.
      If omitted, the default template of the work item type is used.

  name:
    type: string
    required: false
    description: Work item name

  required_mode:
    type: integer
    required: false
    default: 0
    enum:
      - 0  # do not validate required fields
      - 1  # validate required fields and fail if missing

  field_value_pairs:
    type: list[object]
    required: false
    description: >
      Field configuration list.
      Field definitions must match metadata from
      "Get Work Item Creation Metadata".
    item_schema:
      field_key:
        type: string
        required: true
      field_value:
        type: any
        required: true
      notes:
        - For option/select fields, value must be option ID
        - Cascading fields must follow configured option hierarchy
        - role_owners must follow role + owners structure

response:
  data:
    type: integer
    description: Created work item ID
  err_code:
    type: integer
  err_msg:
    type: string

error_handling:
  - code: 30014
    meaning: Work item type not found or invalid
  - code: 50006
    meaning: Role owners parsing failed or template invalid
  - code: 20083
    meaning: Duplicate fields in request
  - code: 20038
    meaning: Required fields not set

constraints:
  - name must not also appear in field_value_pairs
  - template_id must not appear in field_value_pairs
  - option-type fields must use option ID, not label
  - role_owners default behavior depends on process role configuration

examples:
  minimal:
    project_key: doc
    body:
      work_item_type_key: story
      name: "New Story"

  full:
    project_key: doc
    body:
      work_item_type_key: story
      template_id: 123123
      name: "Example Work Item"
      field_value_pairs:
        - field_key: description
          field_value: "Example description"
        - field_key: priority
          field_value:
            value: "xxxxxx"
        - field_key: role_owners
          field_value:
            - role: rd
              owners:
                - testuser
```

### Usage notes

- **project_key**: Path parameter, required. Use space ID (project_key) or space domain (simple_name).
- **name**: Work item name; do not also send name in field_value_pairs.
- **field_value_pairs**: Send other fields (description, priority, assignees, etc.) here; use option ID for option-type fields, not display labels.
- Before creating, call "Get Work Item Creation Metadata" to get field metadata for the type and template, then build field_value_pairs accordingly.

---

## Update Work Item

Update one or more editable fields of a Meegle work item instance under a specified space and work item type. Only fields allowed by metadata and permissions can be modified. Template and calculated fields are not supported.

### When to Use

- When modifying fields (name, description, status, assignees, etc.) of an existing work item
- When updating workflow state or custom fields
- When syncing external changes into Meegle

### API Spec: update_work_item

```yaml
name: update_work_item
type: api
description: >
  Update one or more editable fields of a Meegle work item instance under a
  specified space and work item type. Only fields allowed by metadata and
  permissions can be modified. Template and calculated fields are not supported.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space identifier. Can be project_key or space domain name (simple_name).
  work_item_type_key:
    type: string
    required: true
    description: Work item type key (e.g. story, bug).
  work_item_id:
    type: string
    required: true
    description: Work item instance ID.

inputs:
  update_fields:
    type: array
    items:
      type: object
      properties:
        field_key:
          type: string
          required: true
          description: Field identifier
        field_value:
          type: any
          required: true
          description: >
            New field value. For option fields, pass option ID (value),
            not the label.
    required: true
    description: >
      List of fields to update. Each update overwrites the previous value.
      Field definitions must follow metadata from
      "Get Work Item Creation Metadata".

outputs:
  description: Update succeeded

constraints:
  - Cascading option fields must follow configured hierarchy
  - Option-type fields require option ID, not name
  - role_owners behavior depends on process role configuration
  - Template, voting, and calculated fields cannot be updated

error_mapping:
  20007: Work item has already reached terminal status; terminated items cannot be modified
  30009: Field not found (invalid field_key)
  30005: Work item not found (invalid work_item_id)
  50006: No right to edit / WorkItemValue limit exceeded
  20090: Request blocked (field cannot be updated or is calculated)
  20050: Failed to check field (field option invalid due to configuration change)
  10001: Operation not permitted (no permission)
  20014: Project and work item do not match (project_key and work item not in same space)
  1000051743: Can not find user info (invalid X-User-Key)
  10211: Token info invalid (token expired or invalid)
```

### Usage notes

- **project_key, work_item_type_key, work_item_id**: Path parameters for the target work item.
- **update_fields**: Array of `{field_key, field_value}`; use option ID for option-type fields, not labels.
- Call "Get Work Item Creation Metadata" to know editable fields and their schema.
- Terminated work items cannot be updated. Template, voting, and calculated fields are read-only.

---

## Delete Work Item

Delete a work item instance under a specified space and work item type. The operation permanently removes the work item and requires proper Work Item permissions.

### When to Use

- When permanently removing a work item that is no longer needed
- When cleaning up test or duplicate work items
- When implementing bulk delete workflows (with caution)

### API Spec: delete_work_item

```yaml
name: delete_work_item
type: api
description: >
  Delete a work item instance under a specified space and work item type.
  The operation permanently removes the work item and requires proper
  Work Item permissions.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space identifier. Can be project_key or space domain name (simple_name).
  work_item_type_key:
    type: string
    required: true
    description: Work item type key (e.g. story, bug).
  work_item_id:
    type: string
    required: true
    description: Work item instance ID.

outputs:
  description: Work item deleted successfully

constraints:
  - Requires Permission Management - Work Items permission
  - Deletion is irreversible

error_mapping:
  10001: Operation not permitted (unauthorized / no permission)
  30005: Work item not found (work_item_id incorrect or does not exist)
  20090: Request intercepted (retry later)
  20014: Project and work item do not match (project_key does not match work item)
  20003: Wrong work_item_type param (work_item_type_key incorrect)
  1000051195: ErrWorkItemNoPermission (cannot delete work items across tenants)
```

### Usage notes

- **project_key, work_item_type_key, work_item_id**: Path parameters for the target work item.
- Requires Work Items permission. Deletion is irreversible — consider soft delete or archiving if recovery may be needed.

---

## Abort or Resume Work Item

Terminate (abort) or resume a work item instance under a specified space and work item type. Used to mark work items as terminated or restore them back to active status.

### When to Use

- When terminating work items (cancel, duplicate, test, etc.)
- When resuming previously terminated work items (restart, rollback, test)
- When managing work item lifecycle (active vs terminated)

### API Spec: abort_or_resume_work_item

```yaml
name: abort_or_resume_work_item
type: api
description: >
  Terminate (abort) or resume a work item instance under a specified space
  and work item type. Used to mark work items as terminated or restore them
  back to active status.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/abort
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space identifier. Can be project_key or space domain name (simple_name).
  work_item_type_key:
    type: string
    required: true
    description: Work item type key (e.g. story, bug).
  work_item_id:
    type: string
    required: true
    description: Work item instance ID.

inputs:
  is_aborted:
    type: boolean
    required: false
    description: |
      true: terminate the work item
      false: resume the work item
  reason:
    type: string
    required: false
    description: >
      Reason for termination or recovery.
      Required when reason_option is "other".
  reason_option:
    type: string
    required: false
    description: |
      Termination reason options:
      - cancel: Cancel
      - repeat: Duplicate / merge
      - test: Test
      - other: Other
      Recovery reason options:
      - restart: Restart
      - rollback: Roll back due to misoperation
      - test: Test
      - other: Other

outputs:
  description: Operation succeeded

constraints:
  - Requires Permission Management - Work Item Instances permission
  - reason_option should match configured termination reasons in the space

error_mapping:
  20007: Work item is already aborted (already terminated)
  20008: Work item is already restored (already resumed)
  30005: Work item not found (does not exist or type does not match)
  20090: Request intercepted (request or operation was intercepted)
```

### Usage notes

- **project_key, work_item_type_key, work_item_id**: Path parameters for the target work item.
- **is_aborted**: `true` to terminate, `false` to resume.
- **reason_option**: Must match space-configured options; use `other` with **reason** when needed.

---

## Batch Update Work Item Field

Batch update a single field across multiple work item instances under a specified space and work item type. Supports APPEND, UPDATE, and REPLACE modes with field-type restrictions.

### When to Use

- When updating the same field on many work items at once (e.g. bulk status change, bulk assignee)
- When appending or replacing values in multi-select or personnel fields
- When needing async batch progress via task_id

### API Spec: batch_update_work_item_field

```yaml
name: batch_update_work_item_field
type: api
description: >
  Batch update a single field across multiple work item instances
  under a specified space and work item type. Supports APPEND, UPDATE,
  and REPLACE modes with field-type restrictions.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/batch_update
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: Meegle project space identifier (project_key).
  work_item_type_key:
    type: string
    required: true
    description: Work item type key (e.g. story, bug).
  work_item_ids:
    type: array
    items: integer
    required: true
    constraints:
      max_items: 50
    description: List of work item IDs to update. Max 50 IDs per request.
  update_mode:
    type: string
    required: true
    enum: [APPEND, UPDATE, REPLACE]
    description: |
      APPEND: Append values (supports multi-user, multi-select, multi-associated).
      UPDATE: Overwrite values (not supported for calculated or external signal fields).
      REPLACE: Replace values (supports single/multi select, cascading select,
      personnel fields, associated work item fields).
  field_key:
    type: string
    required: true
    description: >
      Field ID to be modified. Batch update supports only one field at a time.
  before_field_value:
    type: any
    required: false
    description: >
      Original field value to be replaced.
      Required only when update_mode = REPLACE.
  after_field_value:
    type: any
    required: true
    description: >
      Target field value after the operation.
      Can be empty, which means deletion of the field value.

outputs:
  data:
    type: object
    properties:
      task_id: string
    description: >
      Batch update task created successfully.
      Use task_id to query progress.

constraints:
  - QPS limit: 1
  - Requires Permission Management - Work Item Instances
  - Only one field can be updated per batch request
  - Max 50 work_item_ids per request
  - Field type support depends on update_mode

error_mapping:
  1000052062: Project key is wrong (invalid project_key)
  50006: ErrOAPIBatchUpdateOverLimit (more than 50 work_item_ids)
```

### Usage notes

- **project_key, work_item_type_key**: Identify the space and work item type.
- **work_item_ids**: Max 50 per request.
- **update_mode**: APPEND (add), UPDATE (overwrite), REPLACE (replace with before/after). Field support varies by mode.
- **before_field_value**: Required when `update_mode=REPLACE`; original value to match and replace.
- **after_field_value**: Target value; empty means delete the field value.
- Returns **task_id** — use **Get Batch Update Progress** to query batch progress asynchronously.

---

## Get Batch Update Progress

Query execution progress and results of a batch work item field update task. Used together with the Batch Update Work Item Field API.

### When to Use

- After submitting a batch update task — poll to check completion status
- When needing success/fail counts and lists (success_sub_task_list, fail_sub_task_list)
- When debugging batch failures (error_scenes)

### API Spec: get_batch_update_progress

```yaml
name: get_batch_update_progress
type: api
description: >
  Query execution progress and results of a batch work item field update task.
  Used together with the Batch Update Work Item Field API.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/task_result?task_id={{task_id}}
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  task_id:
    type: string
    required: true
    description: >
      Task ID returned by the Batch Update Work Item Field interface.
      Pass as query parameter (?task_id=...).

outputs:
  data:
    type: object
    properties:
      task_id: string
      task_status: string
      total: integer
      success_total: integer
      error_total: integer
      success_sub_task_list: array
      fail_sub_task_list: array
      error_scenes: array
    description: |
      task_status: SUCCESS | IDLE | RUNNING | FAILED | CANCELED | NOT_EXIST
      success_sub_task_list: List of successfully updated work item IDs
      fail_sub_task_list: List of failed work item IDs
      error_scenes: Failure scenarios (e.g. RelationCaseLoops, RelationCaseLevelExceeds,
        DuplicationCheckEnabledForThisField, NoPermissionToModify, WorkItemTerminated)

constraints:
  - No permission application required
  - QPS limit: 1
  - Typically polled after submitting a batch update task
```

### Usage notes

- **task_id**: Pass as query parameter; from the response of Batch Update Work Item Field.
- **task_status**: SUCCESS, IDLE, RUNNING, FAILED, CANCELED, or NOT_EXIST.
- Poll this API after a batch update to track progress and retrieve success/fail lists.

---

## Freeze or Unfreeze Work Item

Freeze or unfreeze a work item instance in a specified Meegle project space. Freezing prevents the work item from moving to the next stage; unfreezing restores normal flow.

### When to Use

- When temporarily blocking a work item from progressing to the next stage
- When restoring workflow progression for a previously frozen work item
- When managing work-in-progress hold or review gates

### API Spec: freeze_or_unfreeze_work_item

```yaml
name: freeze_or_unfreeze_work_item
type: api
description: >
  Freeze or unfreeze a work item instance in a specified Meegle project space.
  Freezing prevents the work item from moving to the next stage; unfreezing restores normal flow.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/work_item/freeze
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: >
      Unique identifier of the Meegle project space (project_key or simple_name).
  work_item_id:
    type: integer
    required: true
    description: Work item instance ID.
  is_frozen:
    type: boolean
    required: true
    description: |
      true = freeze the work item
      false = unfreeze the work item

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Requires Permission Management – Work Item Instance
  - Applies only to the specified work item instance
  - Used to temporarily block or restore workflow progression

error_mapping:
  1000052062: Project key is wrong (incorrect project_key)
```

### Usage notes

- **project_key**: Space identifier (project_key or simple_name).
- **work_item_id**: Target work item instance ID.
- **is_frozen**: `true` to freeze (block stage transition), `false` to unfreeze.

---

## Update Compound Field

Update, add, or delete a compound (composite) field group on a Meegle work item. Supports add / update / delete operations on grouped compound field data.

### When to Use

- When adding new compound field groups to a work item
- When updating existing compound field group data
- When deleting compound field groups

### API Spec: update_compound_field

```yaml
name: update_compound_field
type: api
description: >
  Update, add, or delete a compound (composite) field group on a Meegle work item.
  Supports add / update / delete operations on grouped compound field data.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/field_value/update_compound_field
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
  work_item_id:
    type: integer
    required: true
    description: Work item instance ID.
  field_key:
    type: string
    required: false
    description: >
      ID of the compound field. Cannot be empty at the same time as field_alias.
  field_alias:
    type: string
    required: false
    description: >
      Alias of the compound field. Cannot be empty at the same time as field_key.
  group_uuid:
    type: string
    required: false
    description: |
      Identifier of the compound field group.
      Required for update / delete.
      Must NOT be provided for add.
  action:
    type: string
    required: true
    enum: [add, update, delete]
    description: |
      add    = add new group(s)
      update = update existing group
      delete = delete existing group
  fields:
    type: array
    items: object
    required: false
    description: |
      Compound field data (FieldValuePair list).
      add: multiple groups
      update: single group
      delete: not required

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Requires Permission Management – Work Items
  - field_key or field_alias must be provided (one only, cannot both be empty)
  - group_uuid required for update / delete; must NOT be provided for add
  - Target field must be a compound field
  - Use Get Work Item Details with need_group_uuid_for_compound=true to obtain group_uuid

error_mapping:
  1000050244: Work item not found (does not exist or was deleted)
  1000050156: ProjectKey does not match (project_key does not match work item's space)
  1000050248: Field not found (compound field does not exist)
  1000050156: Invalid field (only compound_field supported)
```

### Usage notes

- **field_key** or **field_alias**: Provide one; used to identify the compound field.
- **group_uuid**: Required for update/delete; omit for add. Obtain via Get Work Item Details with `need_group_uuid_for_compound=true`.
- **action**: `add` (new groups), `update` (existing group), `delete` (remove group).
- **fields**: For add — multiple groups; for update — single group; for delete — omit.

---

## Get Work Item Change Log

Query operation (change) records of one or more Meegle work item instances within a specified space. Supports filtering by operator, operation type, module, time range, and pagination.

### When to Use

- When auditing or reviewing work item change history
- When tracking who changed what and when
- When filtering by operation type (create, modify, delete, terminate, restore, etc.)

### API Spec: get_work_item_change_log

```yaml
name: get_work_item_change_log
type: api
description: >
  Query operation (change) records of one or more Meegle work item instances
  within a specified space. Supports filtering by operator, operation type,
  module, time range, and pagination.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/op_record/work_item/list
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: Space ID (project_key).
  work_item_ids:
    type: array
    items: integer
    required: true
    constraints:
      max_items: 50
    description: List of work item IDs to query. Maximum 50 per request.
  start_from:
    type: string
    required: false
    description: Pagination cursor. Use the value returned by the previous request.
  operator:
    type: array
    items: string
    required: false
    description: |
      Operator identifiers.
      - user: user_key
      - auto: automation rule ID
  operator_type:
    type: array
    items: string
    required: false
    enum: [user, auto, system, calc_field, plugin, others]
    description: Operator trigger source type.
  source_type:
    type: array
    items: string
    required: false
    enum: [auto, plugin]
    description: Operation channel type.
  source:
    type: array
    items: string
    required: false
    description: |
      Operation channel identifier.
      - auto: automation rule ID
      - plugin: plugin ID
  operation_type:
    type: array
    items: string
    required: false
    enum: [modify, create, delete, terminate, restore, complete, rollback, add, remove]
    description: Operation action types.
  start:
    type: integer
    required: false
    description: Start time (milliseconds timestamp). Must be used with end. Max range: 7 days.
  end:
    type: integer
    required: false
    description: End time (milliseconds timestamp). Must be used with start. Max range: 7 days.
  op_record_module:
    type: array
    items: string
    required: false
    enum: [work_item_mod, node_mod, sub_task_mod, field_mod, role_and_user_mod, baseline_mod]
    description: Operation record module type.
  page_size:
    type: integer
    required: false
    default: 50
    constraints:
      max: 200
    description: Records per page. Max 200, default 50.

outputs:
  data:
    type: object
    properties:
      has_more: boolean
      start_from: string
      op_records: array
      total: integer
    description: |
      has_more: Whether more records exist
      start_from: Pagination cursor for next request
      op_records: Operation record list
      total: Total number of records

constraints:
  - Requires Permission Management – Work Item Instance
  - Historical records before July 2, 2024 are NOT supported
  - Pagination is cursor-based via start_from
  - work_item_ids is mandatory (max 50)
  - Time range (start, end) max 7 days

error_mapping:
  20006: Invalid param (one or more parameters invalid)
  20005: Missing param (required parameters missing)
  20013: Invalid time interval (range exceeds 7 days)
```

### Usage notes

- **work_item_ids**: Required; max 50 IDs per request.
- **start_from**: Cursor for next page; use `start_from` from previous response.
- **start / end**: Use together; 13-digit millisecond timestamps; max 7-day range.
- **operation_type**: Filter by create, modify, delete, terminate, restore, complete, rollback, add, remove.
- **op_record_module**: Filter by work_item_mod, node_mod, sub_task_mod, field_mod, role_and_user_mod, baseline_mod.

---

## Get Work Item Resource Instance Detail

Query detailed information of specified Meegle work item *resource library* instances, including field data. Only resource-library-enabled work items are supported; non-resource instances and null-value fields are not returned.

### When to Use

- When querying resource library work item instances (e.g. reusable components, templates)
- When needing full field data for resource work items
- When integrating with resource-library-enabled spaces

### API Spec: get_work_item_resource_instance_detail

```yaml
name: get_work_item_resource_instance_detail
type: api
description: >
  Query detailed information of specified Meegle work item *resource library*
  instances, including field data. Only resource-library-enabled work items
  are supported; non-resource instances and null-value fields are not returned.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/resource/query
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: Project space ID (project_key).
  work_item_ids:
    type: array
    items: integer
    required: true
    constraints:
      max_items: 50
    description: List of resource work item IDs. Maximum 50 per request.
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type key. Obtainable via "Get work item types in the space" API.
  fields:
    type: array
    items: string
    required: false
    description: >
      Specify which fields to return. If omitted, all fields are returned.
      Null-value fields are never returned.
  expand:
    type: object
    required: false
    description: Extended parameters for future expansion.

outputs:
  data:
    type: array
    description: List of resource work item instances.
    item_properties:
      id: integer
      name: string
      project_key: string
      work_item_type_key: string
      template_id: integer
      template_type: string
      simple_name: string
      created_by: string
      updated_by: string
      created_at: integer
      updated_at: integer
      fields: array

constraints:
  - Requires Permission Management – Work Item Instance
  - Only resource-library-enabled work items are supported
  - Non-resource instances will not be returned
  - Fields with null values are automatically filtered out
  - Max 50 work_item_ids per request

error_mapping:
  30005: Work item not found (one or more work items do not exist)
  20005: Invalid work_item_ids parameter
  1000050178: work_item_ids exceeds 50
```

### Usage notes

- **work_item_ids**: List of resource work item IDs; max 50. Only resource-library instances are returned.
- **work_item_type_key**: Required. Use "Get work item types in the space" to obtain.
- **fields**: Optional; omit to return all fields. Null-value fields are never included in the response.

---

## Update Work Item Resource Instance

Update fields of a specified Meegle work item **resource library instance**. Only resource fields are supported. Non-resource fields or roles are ignored. Field updates overwrite existing values (not append/merge).

### When to Use

- When updating resource library work item instances (e.g. reusable components, templates)
- When modifying resource field values
- When syncing external data into resource work items

### API Spec: update_work_item_resource_instance

```yaml
name: update_work_item_resource_instance
type: api
description: >
  Update fields of a specified Meegle work item **resource library instance**.
  Only resource fields are supported. Non-resource fields or roles are ignored.
  Field updates overwrite existing values (not append/merge).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/resource/update
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: false
    description: Project space ID (project_key).
  work_item_type_key:
    type: string
    required: false
    description: Work item type key.
  work_item_id:
    type: integer
    required: false
    description: Resource work item ID.
  update_fields:
    type: array
    items:
      type: object
      properties:
        field_key:
          type: string
          required: true
        field_value:
          type: any
          required: true
          description: >
            Field value. Must follow Meegle Field & Attribute Parsing Format.
    required: false
    description: >
      Fields to update. Values overwrite previous values entirely.

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Requires Permission Management – Work Item Instance
  - Resource library must be enabled for the work item
  - Only resource fields are processed; non-resource fields or roles ignored
  - Field updates are full overwrite, not partial append/merge
  - No duplicate field_key in update_fields

error_mapping:
  30014: Work item type key not found (incorrect project_key or work item not found)
  1000053593: NonresourceFieldsRolesUnsupported (one or more fields are not resource fields)
  1000050438: Duplication field exist (duplicate field_key in update_fields)
  1000050183: Update field invalid (update_fields format is invalid)
```

### Usage notes

- **project_key, work_item_type_key, work_item_id**: Identify the target resource work item.
- **update_fields**: Array of `{field_key, field_value}`; values overwrite (not append). Use Meegle Field & Attribute Parsing Format.
- Only resource fields are updated; non-resource fields and roles are ignored.

---

## Search Work Item Resource Instances

Search and list **work item resource library instances** in Meegle based on complex filtering conditions. Supports pagination via search_after and on-demand field selection. Only available when the resource repository is enabled for the work item type.

### When to Use

- When searching resource library work items across spaces/types
- When filtering by creation time, creator, updater, update time, resource ID
- When needing cursor-based pagination and field selection

### API Spec: search_work_item_resource_instances

```yaml
name: search_work_item_resource_instances
type: api
description: >
  Search and list **work item resource library instances** in Meegle based on
  complex filtering conditions. Supports pagination via search_after and
  on-demand field selection. Only available when the resource repository
  is enabled for the work item type.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/resource/search/params
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  data_sources:
    type: array
    items:
      type: object
      properties:
        project_key:
          type: string
          required: true
          description: Project space ID (project_key)
        work_item_type_keys:
          type: string
          required: true
          description: Work item type key
    required: true
    description: Define project space and work item type scope for resource instances.
  search_group:
    type: object
    required: true
    description: |
      Filtering conditions. Only limited fields supported:
      creation time, creator, space, resource work item ID,
      updater, update time, repository config.
    schema:
      conjunction:
        type: string
        enum: [AND, OR]
        required: true
      search_params:
        type: array
        required: false
      search_groups:
        type: array
        required: false
  field_selected:
    type: array
    items: string
    required: false
    constraints:
      max_items: 20
    description: >
      Fields to return. If omitted, only work_item_id is returned.
      Maximum 20 fields.
  pagination:
    type: object
    required: false
    properties:
      page_size: integer
      search_after: string
    description: Pagination using search_after.
  features:
    type: object
    required: false
    description: >
      Extended options. Supported keys:
      FindAborted, AllowTruncate, SkipAuthCheck.

outputs:
  data:
    type: array
    description: Resource work item instances
  pagination:
    type: object
    description: Pagination metadata

constraints:
  - Requires Permission Management – Work Item Instances
  - Resource repository must be enabled
  - Default response returns only work_item_id
  - Max 20 fields per query (field_selected)
  - Uses search_after for deep pagination
  - Only limited fields supported in search_group

error_mapping:
  20068: Search param not supported
  30014: Work item type key not found
  20069: Search param value error
  20063: Search operator error
  20072: Conjunction value only supports AND / OR
  30001: Data not found
```

### Usage notes

- **data_sources**: Array of `{project_key, work_item_type_keys}` defining scope.
- **search_group**: Same SearchGroup structure as other search APIs; only limited fields supported (creation time, creator, updater, update time, resource ID, etc.).
- **field_selected**: Max 20; omit to get only work_item_id.
- **pagination.search_after**: Cursor for deep pagination.

---

## Create Work Item Resource Repository

Create a **work item resource repository instance** under a specified project space and work item type. The work item type must have **resource library enabled** in advanced configuration.

### When to Use

- When creating new resource library work items (e.g. reusable components, templates)
- When initializing resource instances with field values
- When adding entries to a resource repository

### API Spec: create_work_item_resource_repository

```yaml
name: create_work_item_resource_repository
type: api
description: >
  Create a **work item resource repository instance** under a specified
  project space and work item type. The work item type must have
  **resource library enabled** in advanced configuration.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/resource/create_work_item
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: Feishu / Meegle project space ID (project_key).
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type key. Obtainable via "Get Work Item Types in Space".
  template_id:
    type: integer
    required: false
    description: >
      Template ID. If omitted, the first process template
      of this work item type is used.
  field_value_pairs:
    type: array
    items: object
    required: false
    description: >
      Initial field values for creating the resource instance.
      Must follow Data Structure Summary. Supported fields can be
      obtained from "Get Work Item Creation Metadata".

outputs:
  data:
    type: object
    properties:
      work_item_id: integer
    description: Newly created resource work item ID.

constraints:
  - Requires Permission Management – Work Item Instance
  - Resource library must be enabled for the work item type
  - If no template_id is provided, the default template is used

error_mapping:
  1000053507: Work item has not enabled resource library (specified type is not a resource repository)
```

### Usage notes

- **project_key, work_item_type_key**: Identify the space and work item type.
- **template_id**: Optional; omit to use the first/default process template.
- **field_value_pairs**: Same structure as Create Work Item; use Get Work Item Creation Metadata for supported fields.

---

## Create Work Item through Resources

Create work item instances using a resource library work item as the source. After enabling the Work Item Resource Library feature, use this interface to create corresponding work item instances from a resource entry.

### When to Use

- When creating work items from resource library entries (e.g. reusable component templates)
- When instantiating a resource work item as a new work item in the space
- When copying resource field values into a new work item

### API Spec: create_work_item_through_resources

```yaml
name: create_work_item_through_resources
type: api
description: >
  Create work item instances using a resource library work item as the source.
  After enabling Work Item Resource Library, use this interface to create
  corresponding work item instances from a resource entry.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/resource/{project_key}/{work_item_id}/create_instance
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
    description: >
      Resource work item instance ID. In work item details, expand ··· in the upper right, click ID.

inputs:
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtainable via "Get work item types in the space".
  name:
    type: string
    required: false
    description: >
      Work item name. When name is a resource field, this value is ignored by default.
  template_id:
    type: integer
    required: false
    description: >
      Template ID. If omitted, the first process template of this work item type is used.
      Obtain from Get Work Item Creation Metadata → template field options.
  field_value_pairs:
    type: array
    items: object
    required: false
    description: >
      Follow FieldValuePair structure. Same as Create Work Item.

outputs:
  data:
    type: object
    properties:
      work_item_id: integer
      ignore_create_info:
        field_keys: array
        role_ids: array
    description: >
      work_item_id: Created work item instance ID.
      ignore_create_info: Fields/roles that were ignored during creation.

constraints:
  - Requires Permission Management – Work Items
  - Work Item Resource Library must be enabled
  - work_item_id is the source resource work item ID

error_mapping:
  20006: Invalid param (field_value_pairs structure does not meet single-select field spec)
```

### Usage notes

- **project_key, work_item_id**: Path params. `work_item_id` is the **source resource work item** from which to create a new instance.
- **work_item_type_key**: Type of the work item to create; must match the resource type.
- **name**: Optional; ignored when name is a resource field.
- **template_id**: Optional; omit to use the first process template.
- **field_value_pairs**: Same structure as Create Work Item; follow FieldValuePair specification.
