---
name: meegle-api-work-item-read-and-write
description: Meegle OpenAPI for creating, reading, and updating work items.
metadata: { openclaw: {} }
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
description: Creation metadata (field config) for a work item type; required to build create/update payloads.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/meta" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string }
outputs: { data: array }
error_mapping: { 20044: Work item type disabled, 30014: Work item type not found }
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
description: Detailed info for one or more work items; full detail including fields, workflow, nodes.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/query" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string }
inputs: { work_item_ids: array (max 50), fields: array (specify or exclude, do not mix), expand: object }
outputs: { data: array }
constraints: [work_item_ids max 50 per request]
error_mapping: { 30005: Work item not found, 20028: work_item_ids exceeds 50, 30014: Work item type not found }
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
type: api
description: Create a new work item in a Meegle space; supports types, templates, custom fields. Requires Work Items permission.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/create" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string }
inputs: { work_item_type_key: string, template_id: integer, name: string, required_mode: integer (0|1), field_value_pairs: list[object] }
outputs: { data: integer }
constraints: [name not in field_value_pairs, template_id not in field_value_pairs, option fields use option ID, role_owners per process config]
error_mapping: { 30014: Work item type not found, 50006: Role owners/template invalid, 20083: Duplicate fields, 20038: Required fields not set }
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
description: Update one or more editable fields of a work item; metadata/permissions apply; template/calculated read-only.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { update_fields: array of { field_key, field_value } }
outputs: success
constraints: [cascading options follow hierarchy, option ID not label, role_owners per config, no template/voting/calculated]
error_mapping: { 20007: Terminated cannot modify, 30009: Field not found, 30005: Work item not found, 50006: No right/limit, 20090: Field blocked, 20050: Option invalid, 10001: No permission, 20014: Project mismatch, 1000051743: User not found, 10211: Token invalid }
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
description: Permanently delete a work item instance; requires Work Items permission.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: DELETE, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
outputs: success
constraints: [Work Items permission, deletion irreversible]
error_mapping: { 10001: No permission, 30005: Work item not found, 20090: Request intercepted, 20014: Project mismatch, 20003: Wrong work_item_type, 1000051195: No cross-tenant delete }
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
description: Terminate (abort) or resume a work item; mark terminated or restore to active.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/abort" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { is_aborted: boolean, reason: string, reason_option: string (cancel|repeat|test|other; restart|rollback|test|other) }
outputs: success
constraints: [Work Item Instances permission, reason_option must match space config]
error_mapping: { 20007: Already aborted, 20008: Already restored, 30005: Work item not found, 20090: Request intercepted }
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
description: Batch update one field across multiple work items; APPEND/UPDATE/REPLACE modes.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/batch_update" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, work_item_ids: array (max 50), update_mode: APPEND|UPDATE|REPLACE, field_key: string, before_field_value: any, after_field_value: any }
outputs: { data: { task_id: string } }
constraints: [QPS 1, Work Item Instances permission, one field per batch, max 50 work_item_ids]
error_mapping: { 1000052062: Invalid project_key, 50006: Over 50 work_item_ids }
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
description: Query progress and results of a batch work item field update task.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/task_result?task_id={{task_id}}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { task_id: string }
outputs: { data: { task_id, task_status, total, success_total, error_total, success_sub_task_list, fail_sub_task_list, error_scenes } }
constraints: [QPS 1, poll after batch update]
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
description: Freeze or unfreeze a work item; freeze blocks next stage, unfreeze restores flow.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/work_item/freeze" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_id: integer, is_frozen: boolean }
outputs: { data: object }
constraints: [Work Item Instance permission]
error_mapping: { 1000052062: Invalid project_key }
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
description: Add, update, or delete a compound field group on a work item.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/field_value/update_compound_field" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_id: integer, field_key: string, field_alias: string, group_uuid: string, action: add|update|delete, fields: array }
outputs: { data: object }
constraints: [Work Items permission, field_key or field_alias one required, group_uuid for update/delete only, compound field only]
error_mapping: { 1000050244: Work item not found, 1000050156: ProjectKey mismatch or invalid field, 1000050248: Field not found }
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
description: Query change records for work items; filter by operator, type, module, time; cursor pagination.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/op_record/work_item/list" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_ids: array (max 50), start_from: string, operator: array, operator_type: array, source_type: array, source: array, operation_type: array, start: integer, end: integer, op_record_module: array, page_size: integer (max 200) }
outputs: { data: { has_more, start_from, op_records, total } }
constraints: [Work Item Instance permission, work_item_ids max 50, start/end max 7 days, no records before Jul 2 2024]
error_mapping: { 20006: Invalid param, 20005: Missing param, 20013: Time range exceeds 7 days }
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
description: Query resource library work item instances; only resource-enabled; null fields omitted.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/resource/query" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_ids: array (max 50), work_item_type_key: string, fields: array, expand: object }
outputs: { data: array }
constraints: [Work Item Instance permission, resource-library only, max 50 work_item_ids]
error_mapping: { 30005: Work item not found, 20005: Invalid work_item_ids, 1000050178: work_item_ids exceeds 50 }
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
description: Update resource library instance fields; resource fields only; overwrite not append.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/resource/update" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, work_item_id: integer, update_fields: array of { field_key, field_value } }
outputs: { data: object }
constraints: [Work Item Instance permission, resource library enabled, no duplicate field_key]
error_mapping: { 30014: Work item type not found, 1000053593: Non-resource fields/roles, 1000050438: Duplicate field, 1000050183: Invalid update_fields }
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
description: Search resource library instances with filters; search_after pagination; field_selected max 20.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/resource/search/params" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { data_sources: array, search_group: object, field_selected: array (max 20), pagination: object, features: object }
outputs: { data: array, pagination: object }
constraints: [Work Item Instances permission, resource repo enabled, field_selected max 20]
error_mapping: { 20068: Search param not supported, 30014: Work item type not found, 20069: Param value error, 20063: Operator error, 20072: Conjunction AND/OR only, 30001: Data not found }
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
description: Create a resource repository instance; work item type must have resource library enabled.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/resource/create_work_item" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, template_id: integer, field_value_pairs: array }
outputs: { data: { work_item_id: integer } }
constraints: [Work Item Instance permission, resource library enabled]
error_mapping: { 1000053507: Type not resource repository }
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
description: Create work item instances from a resource library entry; source is path work_item_id.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/resource/{project_key}/{work_item_id}/create_instance" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_id: string }
inputs: { work_item_type_key: string, name: string, template_id: integer, field_value_pairs: array }
outputs: { data: { work_item_id: integer, ignore_create_info: { field_keys, role_ids } } }
constraints: [Work Items permission, Resource Library enabled]
error_mapping: { 20006: Invalid field_value_pairs }
```

### Usage notes

- **project_key, work_item_id**: Path params. `work_item_id` is the **source resource work item** from which to create a new instance.
- **work_item_type_key**: Type of the work item to create; must match the resource type.
- **name**: Optional; ignored when name is a resource field.
- **template_id**: Optional; omit to use the first process template.
- **field_value_pairs**: Same structure as Create Work Item; follow FieldValuePair specification.
