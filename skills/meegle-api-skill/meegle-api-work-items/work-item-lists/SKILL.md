---
name: meegle-api-work-item-lists
description: |
  Meegle OpenAPI for listing, searching, and querying work items.
  Includes single-space filter, cross-space filter, complex search, full-text search,
  associated items, and full search.
metadata:
  openclaw: {}
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
description: |
  Query work item list by conditions within a specified space (project_key).
  Excludes terminated items. Read-only API, suitable for retrieval / analysis / aggregation.

context:
  project_key:
    type: string
    required: true
    description: |
      Space unique identifier.
      How to obtain:
      1. Double-click the Meegle space name
      2. simple_name in the space URL

auth:
  operation_type: read
  token_strategy:
    - plugin_access_token + X-User-Key
    - user_access_token (optional, if already available)

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/filter
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  work_item_name:
    type: string
    required: false
    description: Work item name (fuzzy match)

  user_keys:
    type: array
    items: string
    required: false
    constraints:
      max_items: 10
    description: |
      List of user user_keys.
      Used to match creator / watcher / role member.
      How to obtain: Double-click user avatar

  work_item_ids:
    type: array
    items: number
    required: false
    description: |
      List of work item IDs.
      How to obtain: Work item top-right ··· → ID

  work_item_type_keys:
    type: array
    items: string
    required: false
    description: |
      Work item type keys.
      How to obtain: Get Work Item Types in Space

  created_at:
    type: object
    required: false
    schema:
      start: number
      end: number
    description: |
      Created-at time range (millisecond timestamp).
      end can be omitted to mean "until now"

  updated_at:
    type: object
    required: false
    schema:
      start: number
      end: number
    description: |
      Updated-at time range (millisecond timestamp)

  work_item_status:
    type: array
    required: false
    description: |
      Status filter (WorkItemStatus structure).
      How to obtain: Get field information → work_item_status.options

  businesses:
    type: array
    items: string
    required: false
    description: Business line list

  priorities:
    type: array
    items: string
    required: false
    description: |
      Priorities.
      Source: priority field options

  tags:
    type: array
    items: string
    required: false
    description: |
      Tags.
      Source: tags field options

  search_id:
    type: string
    required: false
    exclusive: true
    description: |
      Exact search ID.
      ⚠️ If provided, all other parameters are ignored

  page_num:
    type: number
    required: false
    default: 1
    description: Page number (1-based)

  page_size:
    type: number
    required: false
    default: 20
    constraints:
      max: 200
    description: |
      Items per page.
      Max 200; up to 200,000 records can be retrieved

  expand:
    type: object
    required: false
    description: |
      Extended parameters (e.g. need_workflow).
      ⚠️ Workflow work items do not allow need_workflow=true

outputs:
  data:
    type: array
    description: |
      Work item list.
      Each element includes:
      - id
      - name
      - work_item_type_key
      - project_key
      - work_item_status
      - current_nodes
      - fields
      - created_at / updated_at

  pagination:
    type: object
    description: |
      Pagination info:
      - page_num
      - page_size
      - total

constraints:
  - Terminated work items are not returned by default
  - Terminated status must be queried separately and merged
  - Custom sorting not supported (uses platform default order)
  - Time fields must be 13-digit millisecond timestamps
  - search_id is mutually exclusive with other parameters
  - QPS limit: 15 / token

error_mapping:
  20003: work_item_type_keys missing or invalid
  20013: Invalid time range (not milliseconds)
  20004: user_keys exceeds 10
  20005: search_id invalid
  30005: Work item does not exist
  30014: Work item type does not exist or no permission
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
description: |
  Query work item list matching criteria across multiple spaces.
  Suitable for global search, cross-project statistics and analysis. Read-only.

auth:
  operation_type: read
  token_strategy:
    - plugin_access_token + X-User-Key
    - user_access_token

http:
  method: POST
  url: https://{domain}/open_api/work_items/filter_across_project
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_keys:
    type: array
    items: string
    required: false
    description: |
      List of space project_keys.
      How to obtain: Double-click space name.
      If omitted, queries all spaces where the plugin is installed and user has permission

  simple_names:
    type: array
    items: string
    required: false
    description: |
      List of space simple_names.
      Source: Space URL, e.g. https://project.feishu.cn/doc/overview → doc

  work_item_type_key:
    type: string
    required: true
    description: |
      Work item type key.
      How to obtain: Get Work Item Types in Space

  work_item_name:
    type: string
    required: false
    description: Work item name (fuzzy search)

  search_user:
    type: object
    required: false
    description: |
      User-related search conditions.
      field_key only supports:
      - owner
      - watchers
      - issue_operator
      - issue_reporter
      ⚠️ user_keys must be present
    schema:
      field_key: string
      user_keys:
        type: array
        items: string
      role: string

  work_item_ids:
    type: array
    items: number
    required: false
    constraints:
      max_items: 50
    description: |
      List of work item IDs.
      How to obtain: Work item detail page ··· → ID

  created_at:
    type: object
    required: false
    schema:
      start: number
      end: number
    description: |
      Created-at time range (millisecond timestamp)

  updated_at:
    type: object
    required: false
    schema:
      start: number
      end: number
    description: |
      Updated-at time range (millisecond timestamp)

  work_item_status:
    type: array
    required: false
    description: |
      Work item status list.
      Source: Get field information → work_item_status.options

  businesses:
    type: array
    items: string
    required: false
    description: |
      Business line list.
      Source: Get business list in space

  priorities:
    type: array
    items: string
    required: false
    description: |
      Priorities.
      Source: priority field options

  tags:
    type: array
    items: string
    required: false
    description: |
      Tags.
      Source: tags field options

  template_ids:
    type: array
    items: number
    required: false
    description: |
      Template ID list.
      Source: template field options

  tenant_group_id:
    type: number
    required: false
    description: |
      Tenant group ID (required only for tenant users)

  page_num:
    type: number
    required: false
    default: 1
    description: Page number (1-based)

  page_size:
    type: number
    required: false
    default: 20
    constraints:
      max: 50
    description: |
      Items per page, max 50

  expand:
    type: object
    required: false
    description: |
      Extended parameters (e.g. need_workflow).
      ⚠️ Workflow work items do not allow need_workflow=true

outputs:
  data:
    type: array
    description: |
      Work item list (WorkItemInfo).
      Each element includes:
      - id
      - name
      - work_item_type_key
      - project_key
      - simple_name
      - work_item_status
      - current_nodes
      - fields
      - created_at / updated_at

  pagination:
    type: object
    description: |
      Pagination info:
      - page_num
      - page_size
      - total

constraints:
  - Max 5000 results returned; use filters to narrow scope
  - Time parameters must be 13-digit millisecond timestamps
  - work_item_type_key is required
  - user_keys in search_user must be present
  - work_item_ids max 50
  - QPS limit: 15 / token

error_mapping:
  20094: Query result exceeds 5000
  20005: search_user parameter invalid
  20028: work_item_ids exceeds 50
  20003: work_item_type_key missing or invalid
  20013: Time parameter invalid
  20059: search_user.user_keys missing
  50006: Platform error or user does not exist
  50005: Internal service error
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
description: >
  Search work items in a single Meegle space using complex combined
  filtering conditions (AND / OR). Supports up to 5000 results with pagination.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/search/params
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain (simple_name).
  work_item_type_key:
    type: string
    required: true
    description: >
      Work item type key, e.g. story / task / bug.

inputs:
  search_group:
    type: object
    required: true
    description: >
      Combined filter conditions (max 50). Supports nested AND / OR.
    schema:
      conjunction:
        type: string
        enum: [AND, OR]
        required: true
      search_params:
        type: array
        required: true
        items:
          type: object
          properties:
            param_key:
              type: string
              required: true
              description: Field key to filter on
            operator:
              type: string
              required: true
              description: >
                Operator, e.g. HAS ANY OF / = / != / IN
            value:
              type: array
              required: true
              description: Value list for the filter
      search_groups:
        type: array
        required: false
        description: Nested search_group conditions

  page_num:
    type: integer
    required: false
    default: 1
    description: Page number (start from 1)

  page_size:
    type: integer
    required: false
    default: 10
    constraints:
      max: 50
    description: Items per page (max 50)

  fields:
    type: array
    items: string
    required: false
    description: |
      Returned fields.
      - Specify mode: ["name","created_at"]
      - Exclude mode: ["-name","-created_at"]
      (modes cannot be mixed)

  expand:
    type: object
    required: false
    description: Additional expand parameters

outputs:
  data:
    type: array
    description: Work item list (max 5000 total)
  pagination:
    type: object
    properties:
      page_num: integer
      page_size: integer
      total: integer

constraints:
  - Max 50 search conditions in search_group
  - conjunction only supports AND or OR
  - Max 5000 total results; refine filters if exceeded

error_mapping:
  20094: Search result exceeds 5000, refine filters
  20069: Search param value error
  20068: Search param not supported
  20072: Conjunction only supports AND / OR
  30014: Work item type not found or no permission
  50006: Internal service error
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
description: >
  Perform full-text search across multiple Meegle spaces.
  Supports searching work items or views by title, description, and related fields.
  Returns top-ranked results (max 200).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/compositive_search
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_keys:
    type: array
    items: string
    required: true
    description: List of space project_keys to search in

  query_type:
    type: string
    required: true
    enum: [workitem, view]
    description: Search target type

  query_sub_type:
    type: array
    items: string
    required: false
    description: >
      Work item type keys (effective only when query_type = workitem)

  query:
    type: string
    required: true
    constraints:
      min_length: 1
      max_length: 200
    description: >
      Full-text search keyword (1–200 characters)

  page_size:
    type: integer
    required: false
    default: 50
    description: Page size

  page_num:
    type: integer
    required: false
    default: 1
    description: Page number (start from 1)

outputs:
  data:
    type: array
    description: >
      Search result list (max 200 items, sorted by relevance)
  pagination:
    type: object
    properties:
      page_num: integer
      page_size: integer
      total: integer

constraints:
  - Max 200 total results (top-ranked by relevance)
  - query length 1–200 characters

error_mapping:
  20080: Query length must be larger than 0 and <= 200
  20081: Query type is not supported
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
description: >
  Retrieve work items associated with a specified work item within a single Meegle space.
  Used to query related items via configured association fields (relation_key).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/search_by_relation
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: Space project_key or simple_name
  work_item_type_key:
    type: string
    required: true
    description: Source work item type key
  work_item_id:
    type: string
    required: true
    description: Source work item ID

inputs:
  relation_work_item_type_key:
    type: string
    required: true
    description: Related work item type key

  relation_key:
    type: string
    required: true
    description: Association field key or docking identifier

  relation_type:
    type: integer
    required: false
    default: 0
    enum: [0, 1]
    description: |
      Relation identification method
      0 = association field ID
      1 = docking identifier

  page_size:
    type: integer
    required: false
    default: 50
    constraints:
      max: 50
    description: Max 50 per page

  page_num:
    type: integer
    required: false
    default: 1
    description: Page number (start from 1)

outputs:
  data:
    type: array
    description: Associated work item list (WorkItemInfo)
  pagination:
    type: object
    properties:
      page_num: integer
      page_size: integer
      total: integer

constraints:
  - Max 5000 associated items; use pagination
  - relation_key must exist in association field configuration

error_mapping:
  20055: Search result exceeds 5000
  30018: RelationKey not found in configuration
  20060: Work item type mismatch in relation field configuration
  50005: Internal server error
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
description: >
  Search work item instances in a specified Meegle space using full search with
  complex filtering and on-demand field selection.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/view_search/universal_search
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  project_key:
    type: string
    required: true
    description: Space project_key (double-click space name to obtain)

  work_item_type_key:
    type: string
    required: true
    description: Work item type key in the space

  search_group:
    type: object
    required: true
    description: >
      Combined filter conditions (max 50). Conforms to SearchGroup structure.

  pagination:
    type: object
    required: false
    properties:
      page_size:
        type: integer
        description: Page size
      search_after:
        type: string
        description: Cursor for deep pagination

  field_selected:
    type: array
    items: string
    required: false
    constraints:
      max_items: 20
    description: >
      Fields to return. If omitted, only work_item_id is returned by default.

outputs:
  datas:
    type: array
    description: Work item detail list (new model)
  pagination:
    type: object
    properties:
      page_size: integer
      total: integer
      search_after: string

constraints:
  - search_group max 50 conditions; conforms to SearchGroup structure
  - field_selected max 20 fields; omit for work_item_id only

error_mapping:
  20069: Search parameter value error
  30001: Data not found
  20063: Search operator error
  30014: Work item type not found or no permission
  20067: Search signal value not supported
  20068: Search parameter not supported
```

### Usage notes

- **project_key, work_item_type_key**: Identify the space and work item type.
- **search_group**: Same SearchGroup structure as Search Work Items (Complex) — conjunction, search_params, nested search_groups.
- **pagination**: Use `search_after` from previous response for cursor-based deep pagination; set `page_size` as needed.
- **field_selected**: Max 20 fields to return; omit to get only `work_item_id`. Use to reduce payload when only certain fields are needed.
