---
name: meegle-api-setting-field-settings
description: |
  Meegle OpenAPI for field settings: get, create, update custom fields.
metadata:
  openclaw: {}
---

# Meegle API — Setting (Field Settings)

APIs under this skill: Get Field Information, Create Custom Field, Update Custom Field.

---

## Get Field Information

Obtain the basic information of all fields under the specified space or, when **work_item_type_key** is provided, under that work item type. Response follows the SimpleField structure (field_key, field_type_key, options for select, compound_fields for compound_field). Permission: Permission Management – Configuration.

### When to Use

- When building field selectors or form UIs that need field keys, types, aliases, and scopes (work_item_scopes)
- When you need option lists for select-type fields (label, value, order, is_disabled, etc.) or sub-fields for compound_field
- When resolving field_key for Update Work Item Basic Information Settings (schedule_field_key, estimate_point_field_key, actual_work_time_field_key) or for work item read/write APIs

### API Spec: get_field_information

```yaml
name: get_field_information
type: api
description: >
  Obtain all fields under the space or under a work item type. Returns SimpleField
  list: field_key, field_type_key, field_alias, field_name, is_custom_field,
  work_item_scopes, value_generate_mode, relation_id; options for select; compound_fields for compound_field.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/field/all
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

inputs:
  work_item_type_key:
    type: string
    required: false
    description: Work item type. Obtain via Get work item types in space. Omit to get all fields in space.

outputs:
  data:
    type: array
    description: >
      List of SimpleField. Each has field_key, field_type_key, field_alias, field_name,
      is_custom_field, work_item_scopes, value_generate_mode, relation_id. Select-type
      fields include options (order, color, is_visibility, is_disabled, label, value,
      work_item_type_key). compound_field type includes compound_fields (array of
      field objects with field_key, field_type_key, field_name, etc.).

constraints:
  - Permission: Permission Management – Configuration

error_mapping:
  30001: Data not found (project_key does not match work_item_type_key; no such work item type in this space)
```

### Usage notes

- **work_item_type_key**: Omit to return all fields in the space; set to a type (e.g. `story`, `chart`) to return only fields scoped to that type. If the type does not exist in the space, 30001 is returned.
- **data** items: Use **field_key** when updating work item type settings (schedule_field_key, etc.) or when sending field values in work item APIs. **field_type_key** (e.g. `multi_text`, `select`, `compound_field`) determines value shape.
- **options**: For **select** (and similar) fields; **value** is what to send in API payloads; **label** is display. **compound_fields**: For **compound_field** type; each sub-field has its own field_key and field_type_key.

---

## Create Custom Field

Create a new custom field under the specified work item type. Returns the new **field_key**. Permission: Permission Management – Work Item Instances. For feature details, see Permission Management.

### Points to note

- Work item relationship field default data visibility is fixed; conditional data range cannot be modified.
- Default values are not supported for attachment type or for external system signal / multi-value external system signal.
- Modifying field validity (default valid) is not supported.
- Updating work item type, creator, submission time, completion time, and business line fields is not supported.
- Voting fields are not supported.

### When to Use

- When adding a new custom field (text, select, date, user, number, link, etc.) to a work item type
- When reusing options from another field (value_type 1 + reference_work_item_type_key, reference_field_key) or defining custom options (field_value)
- When configuring team_option for cascading single/multi-select (tree_select, tree_multi_select); mutually exclusive with field_value

### API Spec: create_custom_field

```yaml
name: create_custom_field
type: api
description: >
  Create a custom field under the specified work item type. Returns field_key.
  Supports text, select, tree_select, date, user, number, link, multi_file, bool,
  work_item_related_select, etc. field_value and team_option are mutually exclusive.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/field/{work_item_type_key}/create
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
  field_name:
    type: string
    required: true
    description: Field name; must not duplicate other fields.
  field_alias:
    type: string
    required: false
    description: Field alias; cannot duplicate other fields of the same work item type.
  field_type_key:
    type: string
    required: true
    description: >
      Field type. See Attributes and fields. Supported: text, multi_text, select,
      multi_select, tree_select, tree_multi_select, radio, user, multi_user, date,
      schedule, link, number, multi_file, bool, signal, work_item_related_select,
      work_item_related_multi_select.
  value_type:
    type: integer
    required: false
    description: >
      Option source for select/multi_select/tree_select/tree_multi_select/radio.
      0: Custom (default); 1: Reuse. When 1, reference_work_item_type_key and reference_field_key required.
  field_value:
    type: object
    required: false
    description: >
      Option values; structure per Attributes and fields. For select, multi_select,
      tree_select, tree_multi_select, radio. Mutually exclusive with team_option.
  reference_work_item_type_key:
    type: string
    required: false
    description: Required when value_type = 1.
  reference_field_key:
    type: string
    required: false
    description: Required when value_type = 1.
  is_multi:
    type: boolean
    required: false
    description: For text: true = multi-line; false = single-line (default).
  format:
    type: boolean
    required: false
    description: For date: true = date only; false = date + time (default).
  free_add:
    type: integer
    required: false
    description: For select/tree_select etc.: 1 = allow users to add options; 2 = No (default).
  work_item_relation_uuid:
    type: string
    required: false
    description: Work item relationship ID from Get field information. Required for work_item_related_select / work_item_related_multi_select.
  default_value:
    type: object
    required: false
    description: >
      Default value; structure per field type (Attributes and fields). Not supported
      for attachment, external system signal, multi-value external system signal.
  help_description:
    type: string
    required: false
    description: Help instructions.
  authorized_roles:
    type: array
    items: string
    required: false
    description: >
      Roles or system keys that can access/operate this field. Default "Anyone".
      e.g. _master (Administrator), _owner (Creator), _role (Requirement-related person).
  team_option:
    type: object
    required: false
    description: >
      Team scope per TeamOption. Only for tree_select, tree_multi_select.
      Mutually exclusive with field_value.

outputs:
  data:
    type: string
    description: Created field key (e.g. field_73jds7).

constraints:
  - Permission: Permission Management – Work Item Instances
  - field_value and team_option cannot both be sent

error_mapping:
  1000051468: Field alias repeated (field_alias duplicate)
  1000051469: Invalid update version (field being concurrently updated)
  1000051750: Field name has been used (field_name duplicate)
  1000053603: Field name length exceeded (max characters for field name)
```

### Usage notes

- **field_type_key**: Use supported API types (e.g. **text**, **select**, **date**, **user**, **number**, **link**, **multi_file**, **bool**, **work_item_related_select**, **work_item_related_multi_select**). See **Attributes and fields** and the field type support list in the product docs.
- **field_value** vs **team_option**: Use **field_value** for custom/reused option values for select/tree_select etc.; use **team_option** only for cascading single/multi-select with team scope. Do not send both.
- **value_type 1**: Set **reference_work_item_type_key** and **reference_field_key** to reuse options from another field.
- **work_item_relation_uuid**: From Get Field Information (relation or work item relation fields). Required for **work_item_related_select** / **work_item_related_multi_select**.
- Default values are not supported for attachment, external system signal, or multi-value external system signal fields.

---

## Update Custom Field

Update the configuration of the specified custom field. Identify the field by **field_key** in the body. Permission: Permission Management – Configuration. For details, see Permission Management.

### Points to note

- Work item relationship field default data visibility is fixed; conditional data range cannot be modified.
- Default values are not supported for attachment type or for external system signal / multi-value external system signal.
- Modifying field validity (default valid) is not supported.
- Updating work item type, creator, submission time, completion time, and business line fields is not supported.
- Voting fields are not supported.
- When modifying or adding sub-options (cascading options), **parent_value** is required.

### When to Use

- When changing field name, alias, help description, default value, authorized roles, or option list (field_value with action add/modify/delete)
- When updating team scope (team_option) for cascading single/multi-select; mutually exclusive with field_value
- When updating a composite field: pass parent field_key to change only field_name, field_alias, help_description; pass child field_key to update all attributes

### API Spec: update_custom_field

```yaml
name: update_custom_field
type: api
description: >
  Update configuration of the specified custom field. field_key in body identifies
  the field. field_value supports option actions (add/modify/delete); parent_value
  required for sub-options. field_value and team_option are mutually exclusive.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/{project_key}/field/{work_item_type_key}
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
  field_key:
    type: string
    required: false
    description: >
      Unique identifier of the field from Get Field Information. For composite
      fields: parent field_key allows only field_name, field_alias, help_description;
      child field_key allows all attributes.
  field_name:
    type: string
    required: false
    description: Field name.
  field_value:
    type: array
    required: false
    description: >
      Option updates. Each item: label, value (option id), action (0 add, 1 modify, 2 delete).
      For sub-options include parent_value. Structure per Attributes and fields.
      Mutually exclusive with team_option.
  free_add:
    type: integer
    required: false
    description: 1 = allow users to add options; 2 = No (default). For select/tree_select etc.
  work_item_relation_uuid:
    type: string
    required: false
    description: Work item relationship ID from Get Field Information. For work_item_related_select / work_item_related_multi_select.
  default_value:
    type: object
    required: false
    description: Default value; structure per field type. Not supported for attachment, signal, multi-value signal.
  field_alias:
    type: string
    required: false
    description: Field alias; cannot duplicate other fields of same work item type.
  help_description:
    type: string
    required: false
    description: Help instructions.
  authorized_roles:
    type: array
    items: string
    required: false
    description: Role or system keys (e.g. _master, _owner, _role). Default "Anyone".
  team_option:
    type: object
    required: false
    description: Team scope per TeamOption. Only for tree_select, tree_multi_select. Mutually exclusive with field_value.

outputs:
  data:
    type: object
    description: Empty on success (no data in response).

constraints:
  - Permission: Permission Management – Configuration
  - field_value and team_option cannot both be sent

error_mapping:
  1000051468: Field alias repeated (replace field_alias)
  1000051750: Field name has been used (replace field_name)
  1000050746: Field type not supported
  1000053603: Field name length exceeded (max 255 characters)
  1000053604: Field description length exceeded (max 255 characters)
  1000053605: Option count exceeded (up to {Number} options)
```

### Usage notes

- **field_key**: Required to identify which field to update; from **Get Field Information**. For **compound_field**: use parent **field_key** to change only name/alias/help_description; use child **field_key** to update all attributes.
- **field_value** option actions: **action** 0 = add option, 1 = modify option, 2 = delete option. Include **parent_value** when adding or modifying sub-options (cascading).
- **field_value** vs **team_option**: Do not send both. Use **field_value** for option list changes; use **team_option** for team scope on tree_select / tree_multi_select.
- Default values are not supported for attachment, external system signal, or multi-value external system signal.
