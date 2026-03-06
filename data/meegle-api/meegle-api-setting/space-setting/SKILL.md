---
name: meegle-api-setting-space-setting
description: Meegle OpenAPI for space-level setting: work item types, business lines.
metadata: { openclaw: {} }
---

# Meegle API — Setting (Space Setting)

Get Work Item Types in Space, Get Business Line Details in Space.

## Get Work Item Types in Space

Returns all work item types and **work_item_type_key** / **api_name** for use in other APIs. Permission: Configuration Categories.

### API Spec: get_work_item_types_in_space

```yaml
name: get_work_item_types_in_space
type: api
description: All work item types in space (type_key, name, api_name, is_disable, enable_model_resource_lib).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/all-types" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true } }
outputs: { data: array }
constraints: [Permission: Configuration Categories]
error_mapping: { 10023: User not exist (X-User-Key invalid) }
```

**Usage:** type_key/api_name → work_item_type_key in other APIs. X-User-Key must be valid (10023 if not).

---

## Get Business Line Details in Space

Returns business line tree (id, name, role_owners, watchers, level_id, parent, children). Permission: Configuration.

### API Spec: get_business_line_details_in_space

```yaml
name: get_business_line_details_in_space
type: api
description: Business line tree; each node has id, name, role_owners, watchers, level_id, parent, children.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/business/all" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true } }
outputs: { data: array }
constraints: [Permission: Configuration]
error_mapping: { 1000052062: Project key wrong }
```
