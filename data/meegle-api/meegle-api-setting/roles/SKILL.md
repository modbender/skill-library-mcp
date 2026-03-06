---
name: meegle-api-setting-roles
description: Meegle OpenAPI for workflow roles: create, get, update, delete.
metadata: { openclaw: {} }
---

# Meegle API — Setting (Roles)

Create Workflow Role, Get Detailed Role Settings, Update Workflow Role Settings, Delete Workflow Role Configuration.

## Create Workflow Role

Add role under work item type. Returns role ID. role: name, is_owner, auto_enter_group, member_assign_mode (1 manual, 2 specified members, 3 creator), members (user_key), is_member_multi, role_alias, lock_scope. Permission: Configuration.

```yaml
name: create_workflow_role
type: api
description: Add role; returns role ID. member_assign_mode 1|2|3; members when 2.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}/create_role" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
inputs: { role: object }
outputs: { data: string }
constraints: [Permission: Configuration]
error_mapping: { 20006: Role id already exists }
```

---

## Get Detailed Role Settings

All roles under work item type (RelationDetail: id, name, is_owner, member_assign_mode, members, deletable, etc.). Permission: Process Roles.

```yaml
name: get_detailed_role_settings
type: api
description: All roles and personnel for work item type.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
outputs: { data: array }
constraints: [Permission: Process Roles]
error_mapping: { 1000052062: Project key wrong }
```

---

## Update Workflow Role Settings

Update role; one of role_id or role_alias required. When member_assign_mode 2, members must be non-empty. Permission: Process Roles.

```yaml
name: update_workflow_role_settings
type: api
description: Update role by role_id or role_alias; role object with updated config.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}/update_role" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
inputs: { role_id: string, role_alias: string, role: object }
outputs: { data: object }
constraints: [Permission: Process Roles, one of role_id/role_alias, members non-empty when mode 2]
error_mapping: { 20006: members empty when mode 2, or role_id not exist }
```

---

## Delete Workflow Role Configuration

Delete role; one of role_id or role_alias required. Role must not be in use in template nodes (20093). Permission: Configuration.

```yaml
name: delete_workflow_role_configuration
type: api
description: Delete role by role_id or role_alias; role not in template nodes.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/flow_roles/{work_item_type_key}/delete_role" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
inputs: { role_id: string, role_alias: string }
outputs: { data: object }
constraints: [Permission: Configuration, one of role_id/role_alias]
error_mapping: { 20093: Role in use, 20006: role_id not exist }
```
