---
name: meegle-api-space-association
description: Meegle OpenAPI for space association operations.
metadata: { openclaw: {} }
---

# Meegle API — Space Association

Space association related APIs for linking work items to spaces and managing associations.

## Scope

- Associate work items with spaces
- List or manage space associations
- Related association endpoints

---

## Get the List of Rules for Space Association

Obtain the list of space association rules configured under the specified space. Optionally filter by associated spaces (remote_projects).

### When to Use

- When listing space association rules for a project
- When checking which rules link the current space to remote spaces
- When building UI or automation for space association management

### API Spec: get_space_association_rules

```yaml
name: get_space_association_rules
type: api
description: List space association rules; optional filter by remote_projects.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/relation/rules" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string }
inputs: { remote_projects: array }
outputs: { data: array }
constraints: [Permission: Space Association]
error_mapping: { 1000052062: Project key wrong, 1000052063: Not found simple name }
```

### Usage notes

- **remote_projects**: Optional; when provided, limits returned rules to those involving the listed associated spaces.
- **data**: Array of rule groups per remote project; each has a **rules** array with rule details (relation, work item types, chat_group_merge, etc.).

---

## Get the List of Work Items under Space Association

Obtain the list of work item instances that are spatially associated with the specified work item instance. Use body parameters to filter by rule, remote space, or related work item.

### When to Use

- When listing work items linked to the current work item via space association
- When filtering by relation rule, remote project, or work item type
- When building cross-space association UIs or reports

### API Spec: get_work_items_under_space_association

```yaml
name: get_work_items_under_space_association
type: api
description: List work items spatially associated with given work item; optional filters (rule, project, type).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/relation/{work_item_type_key}/{work_item_id}/work_item_list" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { relation_rule_id: string, relation_work_item_id: integer, relation_work_item_type_key: string, relation_project_key: string }
outputs: { data: array }
constraints: [Permission: Work Item Instance]
error_mapping: { 10001: Not permitted, 30005: Work item not found, 50006: Too many records }
```

### Usage notes

- **relation_rule_id**: Optional filter; from Get the List of Rules for Space Association (rules[].id).
- **relation_project_key**, **relation_work_item_type_key**, **relation_work_item_id**: Optional filters to narrow results.
- **data**: Array of RelationInstance objects (remote project, work item id/name/type, rule id/name).

---

## Apply Space Association Rules to Work Items

Establish a spatial association binding between the specified work item instance and a list of work item instances. Optionally specify a relation rule and pass instances (project_key, work_item_id, work_item_type_key, chat_group_merge).

### When to Use

- When binding multiple work items to the current work item via space association
- When applying a specific relation rule to new bindings
- When automating cross-space association from integrations or scripts

### API Spec: apply_space_association_rules_to_work_items

```yaml
name: apply_space_association_rules_to_work_items
type: api
description: Bind work items via space association; optional relation_rule_id, instances (project_key, work_item_id, work_item_type_key, chat_group_merge).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/relation/{work_item_type_key}/{work_item_id}/batch_bind" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { relation_rule_id: string, instances: array }
outputs: { data: object }
constraints: [Permission: Work Item Instances]
error_mapping: { 1000051617: Bind duplicate, 30005: Work item not found, 30015: Record not found }
```

### Usage notes

- **relation_rule_id**: Optional; from Get the List of Rules for Space Association.
- **instances**: Each element has **project_key**, **work_item_id**, **work_item_type_key**, **chat_group_merge**; omit or use empty strings where the API allows.
- Success response has empty **data**; check **err_code** 0 and empty **err** / **err_msg**.

---

## Remove Work Items under Space Association

Unbind the space association between the specified work item instance and another work item instance. Optionally specify the relation rule and the work item to unbind.

### When to Use

- When removing a single space-association link from the current work item
- When clearing cross-space bindings by rule or by related work item
- When syncing association state from external systems (e.g. unlink on delete)

### API Spec: remove_work_items_under_space_association

```yaml
name: remove_work_items_under_space_association
type: api
description: Unbind space association; optional relation_rule_id, relation_work_item_id.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: DELETE, url: "https://{domain}/open_api/{project_key}/relation/{work_item_type_key}/{work_item_id}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { relation_rule_id: string, relation_work_item_id: integer }
outputs: { data: object }
constraints: [Permission: Work Item Instances]
error_mapping: { 20006: Invalid param }
```

### Usage notes

- **relation_rule_id** and **relation_work_item_id**: Optional; use to identify which binding to remove. If omitted, behavior may unbind by other rules (refer to product docs).
- Request example shows **relation_work_item_id** as string; API doc type is int64—both typically accepted.
- Success response has empty **data**; check **err_code** 0 and empty **err** / **err_msg**.
