---
name: meegle-api-setting-field-settings
description: Meegle OpenAPI for field settings: get, create, update custom fields.
metadata: { openclaw: {} }
---

# Meegle API — Setting (Field Settings)

Get Field Information, Create Custom Field, Update Custom Field.

## Get Field Information

All fields under space or under a work item type (SimpleField: field_key, field_type_key, options, compound_fields). Permission: Configuration.

```yaml
name: get_field_information
type: api
description: All fields in space or under work item type (field_key, field_type_key, options, compound_fields).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/field/all" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true } }
inputs: { work_item_type_key: { type: string, required: false } }
outputs: { data: array }
constraints: [Permission: Configuration]
error_mapping: { 30001: Data not found }
```

**Usage:** Omit work_item_type_key for all space fields; set for type-scoped fields. field_key → schedule_field_key etc. in work item type settings.

---

## Create Custom Field

Create custom field under work item type. Returns field_key. field_value and team_option mutually exclusive. Permission: Work Item Instances.

```yaml
name: create_custom_field
type: api
description: Create custom field; returns field_key. field_value vs team_option (tree_select) mutually exclusive.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/field/{work_item_type_key}/create" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
inputs: { field_name: string, field_alias: string, field_type_key: string, value_type: integer, field_value: object, reference_work_item_type_key: string, reference_field_key: string, is_multi: boolean, format: boolean, free_add: integer, work_item_relation_uuid: string, default_value: object, help_description: string, authorized_roles: array, team_option: object }
outputs: { data: string }
constraints: [Permission: Work Item Instances, field_value and team_option not both]
error_mapping: { 1000051468: Field alias repeated, 1000051750: Field name used, 1000053603: Field name length }
```

**Usage:** field_type_key e.g. text, select, date, user, number, link. value_type 1 → set reference_work_item_type_key + reference_field_key. work_item_relation_uuid from Get Field Information for work_item_related_select.

---

## Update Custom Field

Update custom field by field_key. field_value (option actions add/modify/delete), parent_value for sub-options. field_value and team_option mutually exclusive. Permission: Configuration.

```yaml
name: update_custom_field
type: api
description: Update field by field_key; field_value actions add/modify/delete; parent_value for sub-options.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/{project_key}/field/{work_item_type_key}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
inputs: { field_key: string, field_name: string, field_value: array, free_add: integer, work_item_relation_uuid: string, default_value: object, field_alias: string, help_description: string, authorized_roles: array, team_option: object }
outputs: { data: object }
constraints: [Permission: Configuration, field_value and team_option not both]
error_mapping: { 1000051468: Alias repeated, 1000051750: Name used, 1000050746: Field type not supported }
```

**Usage:** field_key from Get Field Information. compound_field: parent field_key → name/alias/help only; child field_key → all attributes.
