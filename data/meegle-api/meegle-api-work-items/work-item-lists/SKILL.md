---
name: meegle-api-work-item-lists
description: Meegle OpenAPI for listing, searching, querying work items (filter, full-text, associated).
metadata: { openclaw: {} }
---

# Meegle API — Work Item Lists & Search

List, filter, search, and query work items in Meegle spaces. Read-only APIs.

---

## Get Work Item List (Single Space)

Query work item list by conditions within a specified space (project_key). Excludes terminated items. Read-only API, suitable for retrieval, analysis, and aggregation.

### When to Use

- When filtering work items by name, assignees, status, type, dates, etc.
- When building dashboards, reports, or search results within a single space
- When integrating with external tools that need work item listings

### API Spec: work_item_list_single_space

```yaml
name: meegle.work_item.list.single_space
type: action
description: Query work item list by conditions in one space; excludes terminated; read-only.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/filter" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string }
inputs: { work_item_name: string, user_keys: array (max 10), work_item_ids: array, work_item_type_keys: array, created_at: object, updated_at: object, work_item_status: array, businesses: array, priorities: array, tags: array, search_id: string, page_num: number, page_size: number (max 200), expand: object }
outputs: { data: array, pagination: object }
constraints: [terminated not returned by default, time 13-digit ms, search_id exclusive, QPS 15]
error_mapping: { 20003: work_item_type_keys invalid, 20013: Invalid time range, 20004: user_keys exceeds 10, 20005: search_id invalid, 30005: Work item not exist, 30014: Type not exist or no permission }
```

### Usage notes

- **project_key**: Path parameter, required. Space ID or space domain (simple_name).
- **work_item_name**: Fuzzy match on work item name.
- **user_keys**: Max 10; used for creator, watcher, or role member filter. Obtain from double-clicking user avatar.
- **work_item_ids / work_item_type_keys**: Narrow results to specific items or types.
- **created_at / updated_at**: Use 13-digit millisecond timestamps; omit `end` for "until now".
- **search_id**: When provided, overrides all other filter parameters.
- **page_size**: Max 200; total retrievable records up to 200,000.

---

## Get Work Item List (Across Space)

Query work item list matching criteria across multiple spaces. Suitable for global search, cross-project statistics and analysis. Read-only API.

### When to Use

- When searching work items across multiple spaces/projects
- When building global dashboards or cross-project reports
- When aggregating or analyzing work items organization-wide

### API Spec: work_item_list_across_space

```yaml
name: meegle.work_item.list.across_space
type: action
description: Query work item list across spaces; global search; max 5000 results.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_items/filter_across_project" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_keys: array, simple_names: array, work_item_type_key: string, work_item_name: string, search_user: object, work_item_ids: array (max 50), created_at: object, updated_at: object, work_item_status: array, businesses: array, priorities: array, tags: array, template_ids: array, tenant_group_id: number, page_num: number, page_size: number (max 50), expand: object }
outputs: { data: array, pagination: object }
constraints: [max 5000 results, work_item_type_key required, work_item_ids max 50, QPS 15]
error_mapping: { 20094: Result exceeds 5000, 20005: search_user invalid, 20028: work_item_ids exceeds 50, 20003: work_item_type_key invalid, 20013: Time invalid, 20059: search_user.user_keys missing, 50006: Platform/user error, 50005: Internal error }
```

### Usage notes

- **project_keys / simple_names**: Limit scope to specific spaces. If both omitted, queries all spaces the user can access.
- **work_item_type_key**: Required. Single type key (unlike single-space API).
- **search_user**: Use `field_key` (owner, watchers, issue_operator, issue_reporter) with `user_keys`; `user_keys` is required.
- **work_item_ids**: Max 50 items.
- **page_size**: Max 50; total result cap 5000 (vs 200,000 for single-space).

---

## Search Work Items (Complex)

Search work items in a single Meegle space using complex combined filtering (AND / OR). Supports nested groups and up to 5000 results with pagination.

### When to Use

- When building advanced filters with AND/OR logic
- When combining multiple field conditions (e.g. status AND priority AND assignee)
- When needing field-level control over returned columns (specify or exclude fields)

### API Spec: search_work_items_complex

```yaml
name: search_work_items_complex
type: api
description: Search work items in one space with AND/OR filters; max 5000 results, pagination.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/search/params" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string }
inputs: { search_group: object (max 50, conjunction AND|OR), page_num: integer, page_size: integer (max 50), fields: array, expand: object }
outputs: { data: array, pagination: object }
constraints: [search_group max 50, conjunction AND or OR, max 5000 total]
error_mapping: { 20094: Exceeds 5000, 20069: Param value error, 20068: Param not supported, 20072: Conjunction AND/OR only, 30014: Type not found or no permission, 50006: Internal error }
```

### Usage notes

- **search_group**: Root filter object with `conjunction` (AND/OR), `search_params` (array of field conditions), and optional nested `search_groups` for complex logic.
- **search_params**: Each item has `param_key` (field key), `operator` (e.g. HAS ANY OF, =, !=, IN), and `value` (array).
- **fields**: Use positive values to specify returned fields, or prefix with `-` to exclude; do not mix modes.
- **page_size**: Max 50; total result cap 5000.

---

## Full-text Search Work Items

Perform full-text search across multiple Meegle spaces. Supports searching work items or views by title, description, and related fields. Returns top-ranked results (max 200).

### When to Use

- When searching across spaces by keyword (title, description, etc.)
- When looking for work items or views matching free-text queries
- When needing relevance-ranked results across projects

### API Spec: fulltext_search_work_items

```yaml
name: fulltext_search_work_items
type: api
description: Full-text search across spaces; work items or views; max 200 results by relevance.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/compositive_search" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_keys: array, query_type: workitem|view, query_sub_type: array, query: string (1–200 chars), page_size: integer, page_num: integer }
outputs: { data: array, pagination: object }
constraints: [max 200 results, query 1–200 chars]
error_mapping: { 20080: Query length 0 or >200, 20081: Query type not supported }
```

### Usage notes

- **project_keys**: Required. List of spaces to search within.
- **query_type**: `workitem` or `view` — search work items or views.
- **query_sub_type**: When `query_type=workitem`, restrict to specific work item type keys (e.g. story, task, bug).
- **query**: Search keyword; 1–200 characters.
- **page_size**: Default 50; max 200 results total.

---

## Get Associated Work Items (Single Space)

Retrieve work items associated with a specified work item within a single Meegle space. Used to query related items via configured association fields (relation_key).

### When to Use

- When fetching linked/related work items (e.g. sub-tasks of a story)
- When traversing association relationships (parent-child, blocks/blocked-by)
- When building dependency or hierarchy views

### API Spec: get_associated_work_items_single_space

```yaml
name: get_associated_work_items_single_space
type: api
description: Get work items associated with a work item in one space via relation_key.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/search_by_relation" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { relation_work_item_type_key: string, relation_key: string, relation_type: integer (0|1), page_size: integer (max 50), page_num: integer }
outputs: { data: array, pagination: object }
constraints: [max 5000 associated, relation_key must exist in config]
error_mapping: { 20055: Exceeds 5000, 30018: RelationKey not found, 20060: Type mismatch, 50005: Internal error }
```

### Usage notes

- **project_key, work_item_type_key, work_item_id**: Path parameters for the source work item.
- **relation_work_item_type_key**: Type of related work items to return (e.g. task, bug).
- **relation_key**: Association field key or docking identifier that defines the relationship.
- **relation_type**: 0 = use association field ID; 1 = use docking identifier.
- **page_size**: Max 50 per page; max 5000 total associated items.

---

## Get Work Items Full Search (Single Space)

Search work item instances in a specified Meegle space using full search with complex filtering and on-demand field selection. Supports cursor-based deep pagination.

### When to Use

- When needing complex filters (SearchGroup) plus explicit field selection in a single space
- When using cursor-based pagination (search_after) for large result sets
- When building views with only required fields to reduce payload size

### API Spec: get_work_items_full_search_single_space

```yaml
name: get_work_items_full_search_single_space
type: api
description: Full search in one space with SearchGroup filters and field_selected; cursor pagination.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/view_search/universal_search" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, search_group: object (max 50), pagination: object, field_selected: array (max 20) }
outputs: { datas: array, pagination: object }
constraints: [search_group max 50, field_selected max 20]
error_mapping: { 20069: Param value error, 30001: Data not found, 20063: Operator error, 30014: Type not found or no permission, 20067: Signal not supported, 20068: Param not supported }
```

### Usage notes

- **project_key, work_item_type_key**: Identify the space and work item type.
- **search_group**: Same SearchGroup structure as Search Work Items (Complex) — conjunction, search_params, nested search_groups.
- **pagination**: Use `search_after` from previous response for cursor-based deep pagination; set `page_size` as needed.
- **field_selected**: Max 20 fields to return; omit to get only `work_item_id`. Use to reduce payload when only certain fields are needed.
