---
name: meegle-api-setting-work-item-settings
description: Meegle OpenAPI for work item type basic settings (get/update).
metadata: { openclaw: {} }
---

# Meegle API — Setting (Work Item Settings)

Get Basic Work Item Settings, Update Work Item Basic Information Settings.

## Get Basic Work Item Settings

Basic config of a work item type (type_key, name, flow_mode, schedule/estimate/actual field keys, belong_roles, resource_lib_setting). Permission: Work Item Instance.

### API Spec: get_basic_work_item_settings

```yaml
name: get_basic_work_item_settings
type: api
description: Basic info config for work item type (flow_mode, field keys, belong_roles, resource_lib_setting).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/type/{work_item_type_key}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
outputs: { data: object }
constraints: [Permission: Work Item Instance]
error_mapping: { 30014: Work item type not found }
```

**Usage:** flow_mode = workflow | stateflow. belong_roles = roles for scheduling/estimate. Get work_item_type_key from Get Work Item Types in Space.

---

## Update Work Item Basic Information Settings

Update description, is_disabled, is_pinned, schedule/estimate/actual field keys, belong_role_keys, actual_work_time_switch. Permission: Work Items; space admin required (10005).

### API Spec: update_work_item_basic_information_settings

```yaml
name: update_work_item_basic_information_settings
type: api
description: Update basic config of work item type (description, fields, belong_role_keys, actual_work_time_switch).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/{project_key}/work_item/type/{work_item_type_key}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
inputs: { description: string, is_disabled: boolean, is_pinned: boolean, enable_schedule: boolean, schedule_field_key: string, estimate_point_field_key: string, actual_work_time_field_key: string, belong_role_keys: array, actual_work_time_switch: boolean }
outputs: { data: object }
constraints: [Permission: Work Items, space admin]
error_mapping: { 10005: No project admin, 30014: Work item type not found }
```

**Usage:** work_item_type_key from Get Work Item Types in Space. belong_role_keys = role keys from process roles. Field keys from Get Field Information.
