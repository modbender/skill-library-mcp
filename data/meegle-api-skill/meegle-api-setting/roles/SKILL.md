---
name: meegle-api-setting-roles
description: |
  Meegle OpenAPI for workflow roles: create, get, update, delete.
metadata:
  openclaw: {}
---

# Meegle API — Setting (Roles)

APIs under this skill: Create Workflow Role, Get Detailed Role Settings, Update Workflow Role Settings, Delete Workflow Role Configuration.

---

## Create Workflow Role

Add a role under the specified work item type. Returns the new **Role ID**. Permission: Permission Management – Configuration.

### When to Use

- When creating a workflow role (e.g. Task, PM, DA) for a work item type
- When configuring **member_assign_mode** (manual / assign to specified person / assign to creator), **is_owner**, **auto_enter_group**, or **members** (user_key list)
- When you need the returned role ID for Get/Update/Delete Workflow Role or for node/field role bindings

### API Spec: create_workflow_role

```yaml
name: create_workflow_role
type: api
description: >
  Add a role under the specified work item type. Returns role ID. role object
  includes name, is_owner, auto_enter_group, member_assign_mode, members, is_member_multi, role_alias, lock_scope.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}/create_role
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
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.

inputs:
  role:
    type: object
    required: true
    description: Role configuration.
    properties:
      id:
        type: string
        description: Role ID. Optional; if not provided, auto-generated and returned on create.
      name:
        type: string
        description: Role name.
      is_owner:
        type: boolean
        description: Whether this role is the manager for the task.
      auto_enter_group:
        type: boolean
        description: Whether members are automatically added to the group.
      member_assign_mode:
        type: integer
        description: >
          1: Add manually; 2: Assign to a specified person by default; 3: Assign to the creator by default.
          When 2, members (user_key array) is used.
      members:
        type: array
        items: string
        description: Assigned members (user_key). Used when member_assign_mode is 2.
      is_member_multi:
        type: boolean
        description: Restrict to single-person configuration (false) or allow multiple.
      role_alias:
        type: string
        description: Role identifier/alias.
      lock_scope:
        type: array
        description: Lock scope (structure per product).

outputs:
  data:
    type: string
    description: Role ID (e.g. 5727769).

constraints:
  - Permission: Permission Management – Configuration

error_mapping:
  20006: Invalid param (role id already exists; change the id)
```

### Usage notes

- **role.id**: Optional; omit to let the server generate and return the role ID. If provided and already exists, 20006 is returned.
- **member_assign_mode**: **1** = manual add; **2** = assign to specified person (set **members** with user_key list); **3** = assign to creator by default.
- **members**: Only meaningful when **member_assign_mode** is **2**; values are **user_key** (from Meegle, e.g. double-click avatar in Developer Platform).
- **data**: Use the returned role ID when calling Get Detailed Role Settings, Update Workflow Role Settings, or Delete Workflow Role Configuration, or when binding roles to nodes/fields.

---

## Get Detailed Role Settings

Obtain the configuration of all roles and personnel under the specified work item type. Response follows the RelationDetail structure (id, name, is_owner, role_appear_mode, deletable, auto_enter_group, member_assign_mode, members, is_member_multi). Permission: Permission Management – Process Roles.

### When to Use

- When listing all workflow roles (e.g. PM, DA) for a work item type and their settings
- When you need role **id**, **member_assign_mode**, **members** (user_key list), or **deletable** for Update/Delete Workflow Role or for UI display
- When building role management UIs or syncing role configuration

### API Spec: get_detailed_role_settings

```yaml
name: get_detailed_role_settings
type: api
description: >
  Obtain all roles and personnel configuration under the specified work item type.
  Returns list per RelationDetail: id, name, is_owner, role_appear_mode, deletable,
  auto_enter_group, member_assign_mode, members, is_member_multi.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}
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
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.

outputs:
  data:
    type: array
    description: >
      List of RelationDetail. Each has id, name, is_owner, role_appear_mode,
      deletable, auto_enter_group, member_assign_mode, members (user_key array),
      is_member_multi.

constraints:
  - Permission: Permission Management – Process Roles

error_mapping:
  1000052062: Project key is wrong (project_key incorrect)
```

### Usage notes

- **data** items: Use **id** when updating or deleting a role (Update Workflow Role Settings, Delete Workflow Role Configuration). **deletable** indicates whether the role can be deleted.
- **member_assign_mode** and **members**: Same semantics as Create Workflow Role (1 manual, 2 specified members, 3 creator). **role_appear_mode**: Display/visibility mode per product.

---

## Update Workflow Role Settings

Update a role under the specified work item type. Identify the role by **role_id** or **role_alias** (one required; **role_id** takes precedence if both are sent). Permission: Permission Management – Process Roles.

### When to Use

- When changing role name, is_owner, auto_enter_group, member_assign_mode, members, is_member_multi, role_alias, or lock_scope
- When **role_id** or **role_alias** comes from Get Detailed Role Settings
- When member_assign_mode is 2, **members** must be provided (non-empty)

### API Spec: update_workflow_role_settings

```yaml
name: update_workflow_role_settings
type: api
description: >
  Update a role under the specified work item type. One of role_id or role_alias
  required (role_id preferred). role object contains updated config.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}/update_role
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
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.

inputs:
  role_id:
    type: string
    required: false
    description: Process role ID from Get Detailed Role Settings. One of role_id or role_alias required; role_id preferred if both sent.
  role_alias:
    type: string
    required: false
    description: Role docking identifier from Get Detailed Role Settings. One of role_id or role_alias required.
  role:
    type: object
    required: true
    description: Updated role configuration.
    properties:
      name: { type: string }
      is_owner: { type: boolean }
      auto_enter_group: { type: boolean }
      member_assign_mode: { type: integer }
      members: { type: array, items: string }
      is_member_multi: { type: boolean }
      role_alias: { type: string }
      lock_scope: { type: array }

outputs:
  data:
    type: object
    description: Empty on success.

constraints:
  - Permission: Permission Management – Process Roles
  - One of role_id or role_alias must be provided
  - When member_assign_mode is 2, members must be non-empty

error_mapping:
  20006: Invalid param (members should not be empty when member_assign_mode is 2)
  20006: Invalid param (role_id does not exist; obtain via Get Detailed Role Settings)
```

### Usage notes

- **role_id** or **role_alias**: Provide one to identify the role to update; get from **Get Detailed Role Settings** (data[].id or role_alias). If both are sent, **role_id** is used.
- **role**: Same shape as Create Workflow Role (name, is_owner, auto_enter_group, member_assign_mode, members, is_member_multi, role_alias, lock_scope). When **member_assign_mode** is **2**, **members** must be a non-empty user_key array (20006 otherwise).

---

## Delete Workflow Role Configuration

Delete a role under the specified work item type. Identify the role by **role_id** or **role_alias** (one required; **role_id** takes precedence if both are sent). Permission: Permission Management – Configuration.

### When to Use

- When removing a workflow role (e.g. PM, DA) from a work item type
- When **role_id** or **role_alias** comes from Get Detailed Role Settings
- Role must not be in use in process template nodes (else 20093)

### API Spec: delete_workflow_role_configuration

```yaml
name: delete_workflow_role_configuration
type: api
description: >
  Delete a role under the specified work item type. One of role_id or role_alias
  required (role_id preferred). Role cannot be referenced in template nodes.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}/delete_role
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
      project_key: Double-click space name in Meegle. simple_name: from space URL (e.g. doc).
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.

inputs:
  role_id:
    type: string
    required: false
    description: Process role ID from Get Detailed Role Settings. One of role_id or role_alias required; role_id preferred if both sent.
  role_alias:
    type: string
    required: false
    description: Role docking identifier from Get Detailed Role Settings. One of role_id or role_alias required.

outputs:
  data:
    type: object
    description: Empty on success.

constraints:
  - Permission: Permission Management – Configuration
  - One of role_id or role_alias must be provided
  - Role must not be referenced in process template nodes (else 20093)

error_mapping:
  20093: Role in use (cannot delete; role is referenced in template nodes)
  20006: Invalid param (role_id does not exist or has been deleted; obtain via Get Detailed Role Settings)
```

### Usage notes

- **role_id** or **role_alias**: Provide one to identify the role to delete; get from **Get Detailed Role Settings**. If both are sent, **role_id** is used.
- **20093**: The role is referenced in workflow template nodes and cannot be deleted until those references are removed.
- **20006**: The given role_id does not exist or was already deleted; confirm via Get Detailed Role Settings.
