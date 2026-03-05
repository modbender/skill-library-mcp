---
name: meegle-api-setting-work-item-settings
description: |
  Meegle OpenAPI for work item type basic settings (get/update).
metadata:
  openclaw: {}
---

# Meegle API — Setting (Work Item Settings)

APIs under this skill: Get Basic Work Item Settings, Update Work Item Basic Information Settings.

---

## Get Basic Work Item Settings

Obtain the basic information configuration of the specified work item type (type_key, name, flow_mode, schedule/estimate/actual-work-time fields, belong_roles, resource library settings, etc.). Permission: Permission Management – Work Item Instance. For details, see Permission Management.

### When to Use

- When building work item type configuration UIs or displaying current settings before editing (pair with Update Work Item Basic Information Settings)
- When you need flow_mode (workflow vs stateflow), enable_schedule, field keys/names, belong_roles, or resource_lib_setting
- When checking actual_work_time_switch or enable_model_resource_lib for a type

### API Spec: get_basic_work_item_settings

```yaml
name: get_basic_work_item_settings
type: api
description: >
  Obtain basic information configuration of the specified work item type:
  type_key, name, flow_mode, api_name, description, is_disabled, is_pinned,
  enable_schedule, schedule/estimate/actual_work_time field keys and names,
  belong_roles, actual_work_time_switch, enable_model_resource_lib, resource_lib_setting.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/type/{work_item_type_key}
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
    description: Work item type. Obtain via Get work item types in space; must match the type to query.

outputs:
  data:
    type: object
    description: >
      type_key, name, flow_mode (workflow | stateflow), api_name, description,
      is_disabled, is_pinned, enable_schedule, schedule_field_key/name,
      estimate_point_field_key/name, actual_work_time_field_key/name,
      belong_roles (id, name, key), actual_work_time_switch, enable_model_resource_lib,
      resource_lib_setting (enable_roles, enable_fields with field_alias, field_key, field_name, field_type_key).

constraints:
  - Permission: Permission Management – Work Item Instance

error_mapping:
  30014: Work item type not found (no type for given work_item_type_key)
```

### Usage notes

- **flow_mode**: **workflow** = node flow; **stateflow** = state flow. **enable_schedule** applies to overall scheduling; when true, schedule/estimate/actual field settings take effect; when false, only supported for state-flow work items.
- **belong_roles**: Array of `{ id, name, key }` for roles associated with scheduling and score estimation. **resource_lib_setting**: **enable_roles** and **enable_fields** describe resource library configuration when **enable_model_resource_lib** is true.
- **actual_work_time_switch**: true = work item time managed via Open API; false = via platform standard functions.

---

## Update Work Item Basic Information Settings

Update the basic information configuration of the specified work item type (description, disabled/pinned, schedule and estimate fields, role keys, actual work time switch). Permission: Permission Management – Work Items. For permission details, see Permission Management.

### When to Use

- When changing work item type settings: description, is_disabled, is_pinned, schedule/estimate/actual-work-time fields, belong roles, or actual_work_time_switch
- When configuring which fields are used for scheduling, estimate points, and actual work time
- When enabling or disabling the API for registering work-item working hours

### API Spec: update_work_item_basic_information_settings

```yaml
name: update_work_item_basic_information_settings
type: api
description: >
  Update basic information configuration of the specified work item type:
  description, is_disabled, is_pinned, enable_schedule, field keys, belong_role_keys, actual_work_time_switch.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/{project_key}/work_item/type/{work_item_type_key}
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
    description: Work item type. Obtain via Get work item types in space; must match the type to update.

inputs:
  description:
    type: string
    required: false
    description: Work item type description.
  is_disabled:
    type: boolean
    required: false
    description: true = disable this work item type; false = enabled.
  is_pinned:
    type: boolean
    required: false
    description: true = show as entry in navigation bar; false = do not show.
  enable_schedule:
    type: boolean
    required: false
    description: true = work item supports overall scheduling; false = does not.
  schedule_field_key:
    type: string
    required: false
    description: Field key for scheduling; use a date-range type field.
  estimate_point_field_key:
    type: string
    required: false
    description: Field key for estimated score; use a numeric field.
  actual_work_time_field_key:
    type: string
    required: false
    description: Field key for actual working hours; use a numeric field.
  belong_role_keys:
    type: array
    items: string
    required: false
    description: >
      Keys of associated roles for scheduling and score estimation (score split among roles).
      Roles must already exist in process role configuration.
  actual_work_time_switch:
    type: boolean
    required: false
    description: Whether to enable the API for registering work-item working hours.

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Work Items
  - Current user must have space admin permission (else 10005)

error_mapping:
  10005: No project admin permission (current user is not space administrator)
  30014: Work item not found (work_item_type_key incorrect)
```

### Usage notes

- **work_item_type_key**: From **Get Work Item Types in Space** (e.g. `story`, `issue`). Wrong or non-existent type returns 30014.
- **belong_role_keys**: Parameter name in API is **belong_role_keys** (some examples may show **belong_roles_keys**). Roles must exist in process role configuration.
- **schedule_field_key** / **estimate_point_field_key** / **actual_work_time_field_key**: Use field keys from field configuration (e.g. Get Field Information). Date-range for schedule; numeric for estimate and actual work time.
- Space administrator permission is required (10005 if not admin).
