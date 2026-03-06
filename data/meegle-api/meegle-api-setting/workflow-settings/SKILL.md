---
name: meegle-api-setting-workflow-settings
description: Meegle OpenAPI for workflow/process template settings: list, get detail, create, update, delete.
metadata: { openclaw: {} }
---

# Meegle API — Setting (Workflow Settings)

Get Workflow Templates, Get Detailed Settings of Workflow Templates, Create Workflow Templates, Update Workflow Template, Delete Workflow Templates.

## Get Workflow Templates

List process templates under work item type (TemplateConf: version, unique_key, is_disabled, template_id, template_key, template_name). Permission: Configuration.

```yaml
name: get_workflow_templates
type: api
description: List process templates for work item type.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/template_list/{work_item_type_key}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, work_item_type_key: { type: string, required: true } }
outputs: { data: array }
constraints: [Permission: Configuration]
```

---

## Get Detailed Settings of Workflow Templates

Template detail: workflow_confs (nodes), connections. Node event config not supported. Permission: Process Type.

```yaml
name: get_detailed_settings_of_workflow_templates
type: api
description: Template detail (workflow_confs, connections); node event not supported.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/template_detail/{template_id}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, template_id: { type: string, required: true } }
outputs: { data: object }
constraints: [Permission: Process Type]
error_mapping: { 50006: Template not found, 30001: Data not found }
```

---

## Create Workflow Templates

Create process template; optional copy_template_id. Returns template ID. Permission: Configuration; space admin (10005).

```yaml
name: create_workflow_templates
type: api
description: Create template; optional copy_template_id; returns template ID.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/template/v2/create_template" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, template_name: string, copy_template_id: integer }
outputs: { data: integer }
constraints: [Permission: Configuration, space admin]
error_mapping: { 10005: No project admin, 50006: Template name duplicate }
```

---

## Update Workflow Template

Update template: workflow_confs (node flow, action 1 add, 2 delete, 3 modify), state_flow_confs (state flow). Permission: Settings; space admin.

```yaml
name: update_workflow_template
type: api
description: Update template; workflow_confs (action 1/2/3), state_flow_confs.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/template/v2/update_template" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, template_id: integer, workflow_confs: array, state_flow_confs: array }
outputs: { data: object }
constraints: [Permission: Settings, space admin]
error_mapping: { 10005: No project admin, 50006: Template not found }
```

---

## Delete Workflow Templates

Delete template by project_key and template_id. Permission: Settings.

```yaml
name: delete_workflow_templates
type: api
description: Delete template; path project_key, template_id.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: DELETE, url: "https://{domain}/open_api/template/v2/delete_template/{project_key}/{template_id}" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true }, template_id: { type: string, required: true } }
outputs: { data: object }
constraints: [Permission: Settings]
error_mapping: { 9999: template_id invalid }
```
