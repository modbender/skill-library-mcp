---
name: meegle-api-setting-relationship-settings
description: |
  Meegle OpenAPI for work item relationship settings: list, create, update, delete.
metadata:
  openclaw: {}
---

# Meegle API — Setting (Relationship Settings)

APIs under this skill: Get the List of Work Item Relationships, Create Work Item Relationships, Update Work Item Relationships, Delete Work Item Relationships.

---

## Get the List of Work Item Relationships

Obtain the list of work item association relationships under the specified space. Response follows the WorkItemRelation structure (id, name, relation_type, work_item_type_key/name, relation_details). Permission: Permission Management – Work Item Instances.

### When to Use

- When building relationship configuration UIs or listing which work item types are linked (e.g. story → sprint)
- When you need relationship **id** or **relation_type** for Create/Update/Delete Work Item Relationships or for work_item_relation_uuid in custom fields
- When displaying **relation_details** (project_key, project_name, work_item_type_key, work_item_type_name) per relation

### API Spec: get_list_of_work_item_relationships

```yaml
name: get_list_of_work_item_relationships
type: api
description: >
  Obtain the list of work item association relationships under the space.
  Returns WorkItemRelation list: id, name, disabled, relation_type, work_item_type_key/name, relation_details.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/relation
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).

outputs:
  data:
    type: array
    description: >
      List of WorkItemRelation. Each has id, name, disabled, relation_type,
      work_item_type_key, work_item_type_name, relation_details (array of
      project_key, project_name, work_item_type_key, work_item_type_name).

constraints:
  - Permission: Permission Management – Work Item Instances

error_mapping:
  1000052062: Project key is wrong (project_key incorrect; provide correct value)
```

### Usage notes

- **data** items: Use **id** when creating/updating/deleting work item relationships or when referencing in custom field **work_item_relation_uuid**. **relation_type** and **relation_details** describe the link (source type and target project/type per detail).
- **relation_details**: Each entry gives the target space (**project_key**, **project_name**) and target work item type (**work_item_type_key**, **work_item_type_name**) for that relation.

---

## Create Work Item Relationships

Add a work item association relationship under the specified space. Returns the new relationship **relation_id** (UUID). Permission: Permission Management – Work Item Instances. For details, see Permission Management.

### When to Use

- When creating a new work item relationship (e.g. story → story in same or another space)
- When defining **relation_details** (target project_key and work_item_type_key per link)
- When you need the returned **relation_id** for custom fields (work_item_relation_uuid) or for Update/Delete Work Item Relationships

### API Spec: create_work_item_relationships

```yaml
name: create_work_item_relationships
type: api
description: >
  Add a work item association relationship under the space. Returns relation_id (UUID).
  Requires project_key, work_item_type_key (source type), name, and relation_details.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/relation/create
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params: {}

inputs:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).
  work_item_type_key:
    type: string
    required: true
    description: Work item type (source). Obtain via Get work item types in space.
  name:
    type: string
    required: true
    description: Relationship name; must not duplicate an existing relationship name.
  relation_details:
    type: array
    required: true
    description: List of relationship details. Each must have project_key and work_item_type_key.
    items:
      type: object
      properties:
        project_key: { type: string }
        work_item_type_key: { type: string }

outputs:
  data:
    type: object
    description: relation_id (UUID of the newly added work item relationship).

constraints:
  - Permission: Permission Management – Work Item Instances
  - Operating user must have space administrator privileges (else 10001)

error_mapping:
  50006: Relationship name cannot be repeated (name unavailable or duplicate)
  10001: Invalid request (operating user is not admin of the space; contact admin for permissions)
```

### Usage notes

- **relation_details**: Each element specifies a target: **project_key** (target space) and **work_item_type_key** (target work item type). Same space or cross-space links are defined by these entries.
- **name**: Must be unique among work item relationships in the space; duplicate or invalid name returns 50006.
- **data.relation_id**: Use this UUID when creating custom fields of type work_item_related_select / work_item_related_multi_select (**work_item_relation_uuid**) or when updating/deleting this relationship.
- Space administrator permission is required (10001 if user is not admin of the space).

---

## Update Work Item Relationships

Update the configuration of the specified work item relationship. This interface performs **overwrite updates** (full replace of name and relation_details). Permission: Permission Management – Work Item Instance. For details, see Permission Management.

### Points to note

- This interface is for **overwrite updates**: the provided **name** and **relation_details** replace the existing configuration for the given **relation_id**.

### When to Use

- When changing the relationship name or the list of relation_details (target project_key and work_item_type_key) for an existing relationship
- When syncing relationship configuration from external config; use **relation_id** from Get the List of Work Item Relationships

### API Spec: update_work_item_relationships

```yaml
name: update_work_item_relationships
type: api
description: >
  Update the specified work item relationship (overwrite). Requires relation_id
  from Get the List of Work Item Relationships, plus project_key, work_item_type_key,
  name, and relation_details.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/relation/update
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params: {}

inputs:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.
  name:
    type: string
    required: true
    description: Relationship name; must not duplicate another relationship name.
  relation_id:
    type: string
    required: true
    description: Work item relationship ID from Get the List of Work Item Relationships.
  relation_details:
    type: array
    required: true
    description: List of relationship details. Each must have project_key and work_item_type_key.
    items:
      type: object
      properties:
        project_key: { type: string }
        work_item_type_key: { type: string }
        project_name: { type: string }
        work_item_type_name: { type: string }

outputs:
  data:
    type: object
    description: Empty on success (no data in response).

constraints:
  - Permission: Permission Management – Work Item Instance
  - Operating user must have space administrator privileges (else 10001)

error_mapping:
  50006: Relationship name cannot be repeated (name unavailable or duplicate)
  10001: Invalid request (operating user is not admin; contact admin for permissions)
```

### Usage notes

- **relation_id**: From **Get the List of Work Item Relationships** (data[].id). Identifies which relationship to update.
- **Overwrite**: The entire relationship config is replaced; send the full **name** and full **relation_details** list you want after the update.
- **relation_details**: Same structure as Create; each entry has **project_key** and **work_item_type_key** (and optionally project_name, work_item_type_name). Duplicate or invalid **name** returns 50006.
- Space administrator permission is required (10001 if not admin).

---

## Delete Work Item Relationships

Delete the work item association relationship identified by **relation_id** under the specified space. Permission: Permission Management – Work Item Instance. For details, see Permission Management.

### When to Use

- When removing a work item relationship (e.g. story → sprint) from the space
- When **relation_id** comes from Get the List of Work Item Relationships
- When cleaning up or reconfiguring relationships (delete then recreate if needed)

### API Spec: delete_work_item_relationships

```yaml
name: delete_work_item_relationships
type: api
description: >
  Delete the work item association relationship under the space. Requires
  project_key and relation_id from Get the List of Work Item Relationships.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/work_item/relation/delete
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params: {}

inputs:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).
  relation_id:
    type: string
    required: true
    description: Work item relationship ID from Get the List of Work Item Relationships.

outputs:
  data:
    type: string
    description: Null or empty on success.

constraints:
  - Permission: Permission Management – Work Item Instance

error_mapping:
  50006: RPC call error (relationship already deleted or does not exist; confirm relation_id)
```

### Usage notes

- **relation_id**: Use the **id** from **Get the List of Work Item Relationships** (data[].id). If the relationship was already deleted or does not exist, 50006 is returned (err.msg may indicate "关系已经被删除" / relationship already deleted).
- Success response has empty or null **data**; check **err_code** 0.
