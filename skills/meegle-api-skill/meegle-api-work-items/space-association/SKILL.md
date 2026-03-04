---
name: meegle-api-space-association
description: |
  Meegle OpenAPI for space association operations.
metadata:
  openclaw: {}
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
description: >
  Obtain the list of space association rules configured under the specified space.
  Response follows ProjectRelationRules structure.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/relation/rules
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
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.

inputs:
  remote_projects:
    type: array
    items: string
    required: false
    description: >
      List of project_key for associated (remote) spaces.
      Used to filter rules for specific spaces.

outputs:
  data:
    type: array
    description: >
      List of ProjectRelationRules. Each item includes remote_project_key,
      remote_project_name, and rules array (id, name, disabled,
      work_item_relation_id, work_item_relation_name, current_work_item_type_key,
      remote_work_item_type_key, chat_group_merge, etc.).

constraints:
  - Permission: Permission Management – Space Association

error_mapping:
  1000052062: Project key is wrong (project_key incorrect)
  1000052063: Not found simple name (project_key incorrect)
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
description: >
  Obtain the list of work item instances that are spatially associated with
  the specified work item instance. Optional filters by rule, project, or related work item.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/relation/{work_item_type_key}/{work_item_id}/work_item_list
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
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtainable via "Get work item types in the space". Must match work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In work item details, click ··· in the upper right, then ID to copy.

inputs:
  relation_rule_id:
    type: string
    required: false
    description: Space association rule ID. Obtain via Get the List of Rules for Space Association.
  relation_work_item_id:
    type: integer
    required: false
    description: ID of the associated work item; used to filter by a specific related work item.
  relation_work_item_type_key:
    type: string
    required: false
    description: Work item type key of the associated work items.
  relation_project_key:
    type: string
    required: false
    description: project_key of the associated (remote) space.

outputs:
  data:
    type: array
    description: >
      List of associated work items (RelationInstance). Each item includes
      relation_project_name, relation_work_item_id, relation_work_item_name,
      relation_work_item_type_key/name, project_relation_rule_id/name, relation_project_key.

constraints:
  - Permission: Permission Management – Work Item Instance

error_mapping:
  10001: Operation not permitted (insufficient permissions)
  30005: Work item not found (work_item_id incorrect or does not match work_item_type_key)
  50006: Too many records (exceed system limit; reduce or batch)
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
description: >
  Establish spatial association binding between the specified work item instance
  and the incoming list of work item instances. Optional relation_rule_id and instances list.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/relation/{work_item_type_key}/{work_item_id}/batch_bind
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
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types under the space. Must match work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In details, expand ··· > ID in the upper right to obtain.

inputs:
  relation_rule_id:
    type: string
    required: false
    description: Space association rule ID. Obtain via Get the List of Rules for Space Association.
  instances:
    type: array
    required: false
    description: List of work item instances to bind.
    items:
      type: object
      properties:
        project_key:
          type: string
          description: project_key of the associated space (can be empty in some cases).
        work_item_id:
          type: string
          description: Work item instance ID to associate.
        work_item_type_key:
          type: string
          description: Work item type key of the instance (can be empty in some cases).
        chat_group_merge:
          type: integer
          description: Chat group merge option (e.g. 1).

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Work Item Instances

error_mapping:
  1000051617: Project relation instance bind duplicate (binding already exists)
  30005: Work item not found (path work item does not exist)
  30015: Record not found (associated work item does not exist)
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
description: >
  Unbind the space association relationship between the specified work item instance
  and the incoming work item instance. Optional relation_rule_id and relation_work_item_id.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/{project_key}/relation/{work_item_type_key}/{work_item_id}
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
      project_key: Double-click space name in Meegle.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types under the space. Must match work_item_id.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In details, expand ··· > ID in the upper right to obtain.

inputs:
  relation_rule_id:
    type: string
    required: false
    description: Space association rule ID. Obtain via Get the List of Rules for Space Association.
  relation_work_item_id:
    type: integer
    required: false
    description: >
      Work item instance ID to unbind. In work item details, expand ··· > ID in the upper right to obtain.
      API types this as int64; string IDs in request body are accepted (e.g. "301228xxxx").

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Work Item Instances

error_mapping:
  20006: Invalid param (work_item or relation_rule_id not found; relation_work_item_id or relation_rule_id incorrect)
```

### Usage notes

- **relation_rule_id** and **relation_work_item_id**: Optional; use to identify which binding to remove. If omitted, behavior may unbind by other rules (refer to product docs).
- Request example shows **relation_work_item_id** as string; API doc type is int64—both typically accepted.
- Success response has empty **data**; check **err_code** 0 and empty **err** / **err_msg**.
