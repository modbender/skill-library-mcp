---
name: meegle-api-setting-workflow-settings
description: |
  Meegle OpenAPI for workflow/process template settings: list, get detail, create, update, delete.
metadata:
  openclaw: {}
---

# Meegle API — Setting (Workflow Settings)

APIs under this skill: Get Workflow Templates, Get Detailed Settings of Workflow Templates, Create Workflow Templates, Update Workflow Template, Delete Workflow Templates.

---

## Get Workflow Templates

Obtain the list of all process templates under the specified work item type. Response follows the TemplateConf structure (version, unique_key, is_disabled, template_id, template_key, template_name). Permission: Permission Management – Configuration.

### When to Use

- When listing workflow/process templates for a work item type (e.g. story, issue)
- When you need **template_id**, **unique_key**, or **template_name** for Get Detailed Settings of Workflow Templates, Update Workflow Template, or Delete Workflow Templates
- When building template selection UIs or checking **is_disabled** / **version** per template

### API Spec: get_workflow_templates

```yaml
name: get_workflow_templates
type: api
description: >
  Obtain the list of all process templates under the specified work item type.
  Returns list per TemplateConf: version, unique_key, is_disabled, template_id, template_key, template_name.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/template_list/{work_item_type_key}
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
      List of TemplateConf. Each has version, unique_key, is_disabled, template_id,
      template_key, template_name.

constraints:
  - Permission: Permission Management – Configuration
```

### Usage notes

- **data** items: Use **template_id** or **unique_key** when calling Get Detailed Settings of Workflow Templates, Update Workflow Template, or Delete Workflow Templates. **is_disabled** indicates whether the template is disabled (value meaning per product).
- For common error codes and server-side call analysis, refer to **Open API Error Codes** in the product docs.

---

## Get Detailed Settings of Workflow Templates

Obtain the detailed configuration of the specified process template, including node information and node transfer configuration. Node event configuration is not supported. Response follows the TemplateDetail structure (template_id, template_name, version, work_item_type_key, workflow_confs, connections). Permission: Permission Management – Process Type.

### When to Use

- When editing or displaying a workflow template's nodes, fields, sub_tasks, sub_work_items, and transitions (connections)
- When **template_id** comes from Get Workflow Templates, Get metadata for creating work items, or Get field information (template field options)
- When building template editors or syncing workflow config; omit template_id to use the first process template of the work item type (per product behavior)

### API Spec: get_detailed_settings_of_workflow_templates

```yaml
name: get_detailed_settings_of_workflow_templates
type: api
description: >
  Obtain detailed configuration of the specified process template: node info and
  node transfer config. TemplateDetail includes workflow_confs (nodes) and connections.
  Node event configuration not supported.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/template_detail/{template_id}
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
  template_id:
    type: string
    required: true
    description: >
      Process template ID. Obtain from Get Workflow Templates, or from template
      field options in Get metadata for creating work items / Get field information.
      When not passed, first process template of the work item type may be used (product-dependent).

outputs:
  data:
    type: object
    description: >
      TemplateDetail: template_id, template_name, version, is_disabled,
      work_item_type_key, workflow_confs (nodes with name, state_key, owner_usage_mode,
      fields, sub_tasks, sub_work_items, done_operation_role, connections, etc.),
      connections (source_state_key, target_state_key).

constraints:
  - Permission: Permission Management – Process Type
  - Node event configuration not supported

error_mapping:
  50006: Template not found (check template_id)
  30001: Data not found (template_id not found in project_key space)
```

### Usage notes

- **template_id**: From **Get Workflow Templates** (data[].template_id), or from the template field options in **Get metadata for creating work items** / **Get field information**. Must belong to the space identified by **project_key** (30001 otherwise).
- **data.workflow_confs**: Array of node configs; each has **state_key**, **name**, **fields**, **sub_tasks**, **sub_work_items**, **done_operation_role**, **connections**, and related flags. **data.connections**: Transitions between state_key values.
- Node event configuration is not supported in this interface.

---

## Create Workflow Templates

Create a new process template under the specified work item type. Optionally copy from an existing template via **copy_template_id**. Returns the new **template ID**. Permission: Permission Management – Configuration.

### When to Use

- When creating a new process template for a work item type (e.g. story, issue)
- When copying an existing template: set **copy_template_id** from Get Workflow Templates (list of process templates under the work item type)
- When you need the returned template ID for Get Detailed Settings, Update, or Delete Workflow Template

### API Spec: create_workflow_templates

```yaml
name: create_workflow_templates
type: api
description: >
  Create a new process template under the specified work item type. Optional
  copy_template_id to reuse an existing template. Returns new template ID (int64).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/template/v2/create_template
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params: {}

inputs:
  project_key:
    type: string
    required: true
    description: Space ID (project_key). Double-click space name in Meegle project space.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.
  template_name:
    type: string
    required: true
    description: Process template name; must not duplicate an existing template name.
  copy_template_id:
    type: integer
    required: false
    description: >
      ID of template to copy from. Obtain via Get Workflow Templates (list of process
      templates under the work item type). Omit to create an empty new template.

outputs:
  data:
    type: integer
    description: Template ID of the newly created process template (int64).

constraints:
  - Permission: Permission Management – Configuration
  - Current user must have space configuration permission (else 10005)

error_mapping:
  10005: No project admin permission (no permission to configure the space)
  50006: Template name duplicate (template name already exists; change the name)
```

### Usage notes

- **template_name**: Must be unique among process templates for the work item type in the space; duplicate returns 50006.
- **copy_template_id**: From **Get Workflow Templates** (data[].template_id). When provided, the new template is created by copying this template; when omitted, a new empty template is created.
- **data**: Use the returned template ID when calling Get Detailed Settings of Workflow Templates, Update Workflow Template, or Delete Workflow Templates.
- Space configuration (admin) permission is required (10005 if not allowed).

---

## Update Workflow Template

Update the configuration of the specified process template. Supports node flow (**workflow_confs**, WorkflowConf) and state flow (**state_flow_confs**, StateFlowConf). Permission: Permission Management – Settings.

### When to Use

- When changing node configuration (add/delete/modify nodes via **action** in workflow_confs or state_flow_confs)
- When **template_id** comes from Get Workflow Templates, Get metadata for creating work items, or Get field information
- When updating owner_usage_mode, owner_roles, owners, need_schedule, pass_mode, done_operation_role, task_confs, etc.

### API Spec: update_workflow_template

```yaml
name: update_workflow_template
type: api
description: >
  Update the specified process template. workflow_confs for node flow (WorkflowConf),
  state_flow_confs for state flow (StateFlowConf). Node action: 1 Add, 2 Delete (state_key only), 3 Modify.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/template/v2/update_template
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
  template_id:
    type: integer
    required: true
    description: >
      Process template ID. From Get Workflow Templates, or template field options in
      Get metadata for creating work items / Get field information.
  workflow_confs:
    type: array
    required: false
    description: Node flow configuration per WorkflowConf. Each can have action (1 add, 2 delete, 3 modify), state_key, name, tags, pre_node_state_key, owner_usage_mode, owner_roles, owners, need_schedule, different_schedule, deletable, deletable_operation_role, pass_mode, done_operation_role, done_schedule, done_allocate_owner, task_confs, etc. For action 2 (delete), only state_key required.
  state_flow_confs:
    type: array
    required: false
    description: State flow configuration per StateFlowConf structure.

outputs:
  data:
    type: object
    description: Empty on success (no data in response).

constraints:
  - Permission: Permission Management – Settings
  - Current user must have space configuration permission (else 10005)

error_mapping:
  10005: No project admin permission (operator cannot configure the space)
  1000052062: Project key is wrong (project_key incorrect)
  20006: Invalid param (state_key illegal for node flow work item)
  50006: Template not found (template_id incorrect)
```

### Usage notes

- **template_id**: From **Get Workflow Templates**, or from template field options in **Get metadata for creating work items** / **Get field information**. Must be correct for the space (50006 if not found).
- **workflow_confs** (node flow): **action** 1 = add node, 2 = delete node (only **state_key** needed), 3 = modify node. Structure follows WorkflowConf (state_key, name, tags, owner_usage_mode, owner_roles, owners, need_schedule, different_schedule, pass_mode, done_operation_role, task_confs, etc.).
- **state_flow_confs**: State flow config per StateFlowConf; use for state-flow work item types.
- Space configuration (admin) permission is required (10005 if not allowed).

---

## Delete Workflow Templates

Delete the specified process template. Permission: Permission Management – Settings.

### When to Use

- When removing a process template for a work item type
- When **template_id** comes from Get Workflow Templates, Get metadata for creating work items, or Get field information (template field options)

### API Spec: delete_workflow_templates

```yaml
name: delete_workflow_templates
type: api
description: >
  Delete the specified process template. Path parameters project_key and template_id.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/template/v2/delete_template/{project_key}/{template_id}
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
  template_id:
    type: string
    required: true
    description: >
      Process template ID. From Get Workflow Templates, or template field options in
      Get metadata for creating work items / Get field information.

outputs:
  data:
    type: object
    description: Empty on success (no data in response).

constraints:
  - Permission: Permission Management – Settings

error_mapping:
  9999: Invalid param (key template_id value invalid; template_id incorrect)
```

### Usage notes

- **template_id**: From **Get Workflow Templates** (data[].template_id), or from template field options in **Get metadata for creating work items** / **Get field information**. Invalid or non-existent template_id returns 9999.
- Success response has no **data**; check **err_code** 0.
