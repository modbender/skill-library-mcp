---
name: meegle-api-setting-space-setting
description: |
  Meegle OpenAPI for space-level setting: work item types, business lines.
metadata:
  openclaw: {}
---

# Meegle API — Setting (Space Setting)

APIs under this skill: Get Work Item Types in Space, Get Business Line Details in Space.

---

## Get Work Item Types in Space

Obtain the list of all work item types in the space and their docking identifiers (**work_item_type_key** / **api_name**) for use in subsequent APIs. Permission: Permission Management > Configuration Categories.

### When to Use

- When you need **work_item_type_key** or **api_name** for other interfaces (work item CRUD, workflow, lists, etc.)
- When building space configuration UIs or listing available work item types (story, issue, version, sprint, chart, sub_task, etc.)
- When checking **is_disable** or **enable_model_resource_lib** per type

### API Spec: get_work_item_types_in_space

```yaml
name: get_work_item_types_in_space
type: api
description: >
  Obtain all work item types in the space (WorkItemKeyType). Returns type_key, name,
  api_name, is_disable, enable_model_resource_lib for each type.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/all-types
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space unique identifier (project_key). Double-click space name in Meegle project space to obtain.

outputs:
  data:
    type: array
    description: >
      List of work item types per WorkItemKeyType: type_key, name, is_disable,
      api_name, enable_model_resource_lib. type_key / api_name are used as work_item_type_key in other APIs.

constraints:
  - Permission: Permission Management – Configuration Categories

error_mapping:
  10023: User not exist (X-User-Key in header incorrect or user not found)
```

### Usage notes

- **type_key** and **api_name**: Use as **work_item_type_key** in work item, workflow, list, and other APIs (e.g. `story`, `issue`, `version`, `sub_task`).
- **is_disable**: Indicates whether the type is disabled (value meaning per product; typically 2 = enabled).
- **enable_model_resource_lib**: Whether the type supports model resource library.
- **X-User-Key**: Must be a valid user key; invalid or missing key returns 10023.

---

## Get Business Line Details in Space

Obtain the business line information of the space. Response follows the Business structure (tree with id, name, role_owners, watchers, level_id, parent, children, etc.). For the platform feature, see Business Line Configuration. Permission: Permission Management – Configuration.

### When to Use

- When building business-line UIs or selectors that need the full business line tree for the space
- When you need role_owners, watchers, super_masters, or hierarchy (parent, children, level_id) per business line
- When validating or displaying business line IDs (id) for work items or filters

### API Spec: get_business_line_details_in_space

```yaml
name: get_business_line_details_in_space
type: api
description: >
  Obtain business line information of the space. Returns list of Business objects
  (tree: id, name, role_owners, watchers, level_id, parent, children, disabled, labels, order, project, super_masters).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/business/all
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space unique identifier (project_key). Double-click space name in Meegle project space to obtain.

outputs:
  data:
    type: array
    description: >
      List of Business objects. Each has id, name, role_owners (role, owners, name),
      watchers, level_id, parent, disabled, labels, order, project, super_masters,
      children (nested Business objects with same structure).

constraints:
  - Permission: Permission Management – Configuration

error_mapping:
  1000052062: Project key is wrong (not found simple name; project_key incorrect)
```

### Usage notes

- **data**: Root-level array may represent top-level business lines; each item can have **children** forming a tree. **parent** links to parent id; **level_id** indicates depth.
- **role_owners**: Can be array of `{ role, owners }` or object keyed by role (e.g. `role_test: { name, owners, role }`); **owners** are user_key lists.
- **watchers** / **super_masters**: user_key arrays. **project** is the space/project identifier.
- For business line configuration in the product, refer to **Business Line Configuration** in the platform docs.
