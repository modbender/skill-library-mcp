---
name: meegle-api-setting-relationship-settings
description: Meegle OpenAPI for work item relationship settings: list, create, update, delete.
metadata: { openclaw: {} }
---

# Meegle API — Setting (Relationship Settings)

Get List of Work Item Relationships, Create, Update, Delete Work Item Relationships.

## Get the List of Work Item Relationships

List work item association relationships (WorkItemRelation: id, name, relation_type, work_item_type_key/name, relation_details). Permission: Work Item Instances.

```yaml
name: get_list_of_work_item_relationships
type: api
description: List work item relationships (id, name, relation_type, relation_details).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/relation" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true } }
outputs: { data: array }
constraints: [Permission: Work Item Instances]
error_mapping: { 1000052062: Project key wrong }
```

**Usage:** id → Create/Update/Delete or work_item_relation_uuid in custom fields.

---

## Create Work Item Relationships

Add relationship. Returns relation_id (UUID). Body: project_key, work_item_type_key, name, relation_details (array of project_key, work_item_type_key). Permission: Work Item Instances; space admin (10001).

```yaml
name: create_work_item_relationships
type: api
description: Add relationship; returns relation_id. Inputs project_key, work_item_type_key, name, relation_details.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/relation/create" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, name: string, relation_details: array }
outputs: { data: { relation_id: string } }
constraints: [Permission: Work Item Instances, space admin]
error_mapping: { 50006: Name repeated, 10001: Not admin }
```

---

## Update Work Item Relationships

Overwrite name and relation_details for relation_id. Permission: Work Item Instance; space admin.

```yaml
name: update_work_item_relationships
type: api
description: Overwrite relationship; relation_id + project_key, work_item_type_key, name, relation_details.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/relation/update" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, name: string, relation_id: string, relation_details: array }
outputs: { data: object }
constraints: [Permission: Work Item Instance, space admin]
error_mapping: { 50006: Name repeated, 10001: Not admin }
```

---

## Delete Work Item Relationships

Delete by relation_id. Permission: Work Item Instance.

```yaml
name: delete_work_item_relationships
type: api
description: Delete relationship by project_key and relation_id.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: DELETE, url: "https://{domain}/open_api/work_item/relation/delete" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, relation_id: string }
outputs: { data: null }
constraints: [Permission: Work Item Instance]
error_mapping: { 50006: Already deleted or not exist }
```
