---
name: meegle-api-views-measurement
description: |
  Meegle OpenAPI for views, kanban, Gantt, and measurement/charts.
metadata:
  openclaw: {}
---

# Meegle API — Views & Measurement

Views, boards, and measurement related OpenAPIs (e.g. get view detail, list views, metrics, charts). Use when you need to query or manage views or measurement data.

---

## Get the List of Views and Settings

Search for the list of views that meet the request parameters and related configuration in the specified space. Response follows FixView format (view_id, name, view_type, auth, collaborators, created_at, created_by, quick_filters, system_view, view_url, etc.). Permission: Permission Management – Views. For details, see Permission Management.

### When to Use

- When listing or searching views by work item type (e.g. story, issue) with optional filters (view_name, view_ids, created_by, created_at)
- When you need **view_id**, **view_url**, or **quick_filters** for Get the List of Work Items in Views or for view management UIs
- When paginating view results (**page_size** max 10, **page_num**); set **is_query_quick_filter** true to include quick filter conditions in the response

### API Spec: get_list_of_views_and_settings

```yaml
name: get_list_of_views_and_settings
type: api
description: >
  Search for the list of views meeting the request parameters and related
  configuration in the space. Returns list per FixView with pagination.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/view_conf/list
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
    required: true
    description: >
      Work item type. Obtain via Get work item types in space. Sub_task is not supported.
  view_name:
    type: string
    required: false
    description: View name, fuzzy search. Ignored when view_ids is specified.
  view_ids:
    type: array
    items: string
    required: false
    description: List of view IDs to query. When specified, other filters are ignored.
  created_by:
    type: string
    required: false
    description: Creator ID; filter views created by this user (AND with view_name/view_ids).
  created_at:
    type: object
    required: false
    description: Creation time range. Supports start and optional end (omit end for up to now).
    properties:
      start: { type: integer }
      end: { type: integer }
  page_size:
    type: integer
    required: false
    description: Page size, max 10, default 10.
  page_num:
    type: integer
    required: false
    description: Page number, default 1.
  is_query_quick_filter:
    type: boolean
    required: false
    description: Whether to return quick filter conditions in view info; default false.

outputs:
  data:
    type: array
    description: List of view info per FixView (auth, collaborators, created_at, created_by, quick_filters, name, system_view, view_id, view_type, view_url, etc.).
  pagination:
    type: object
    description: page_num, page_size, total.

constraints:
  - Permission: Permission Management – Views

error_mapping:
  30004: View not exist
  30014: WorkItem Type Not Found (work item type does not exist or no permission)
  50006: Miss params (view id or stage missing)
```

### Usage notes

- **work_item_type_key**: Required; get from Get work item types in space. **sub_task** is not supported.
- **view_ids** vs **view_name**: If **view_ids** is set, only those views are returned and **view_name** is ignored. **created_by** applies in AND with view_name/view_ids.
- **created_at**: Time range; omit **end** for "up to now". Timestamps in milliseconds.
- **data** items: Use **view_id** for Get the List of Work Items in Views or update/delete view APIs. **quick_filters** is populated when **is_query_quick_filter** is true.
- **pagination**: total, page_num, page_size for paging.

---

## Get the List of Work Items in Views

Obtain the list of all work item instances in the specified (fixed) view. Response includes view metadata (name, view_id, editable, created_at, created_by, modified_by) and **work_item_id_list**. Permission: Permission Management – View. For details, see Permission Management.

### When to Use

- When listing work items displayed in a fixed view by **view_id** (from Get the List of Views and Settings or from the view page URL)
- When paginating work item IDs (**page_size** max 200, **page_num**); use **quick_filter_id** to filter by a quick filter from the view list interface
- Panorama (multi-project) view is not supported; use Get the List of Work Items in Views (Panorama View) for that case

### API Spec: get_list_of_work_items_in_views

```yaml
name: get_list_of_work_items_in_views
type: api
description: >
  Obtain the list of all work item instances in the specified fixed view.
  Returns view info and work_item_id_list with pagination.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/fix_view/{view_id}
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
  view_id:
    type: string
    required: true
    description: >
      View ID. From view page URL (e.g. .../storyView/RHCFGTzDa then view_id is RHCFGTzDa),
      or from Get the List of Views and Settings (data[].view_id).

inputs:
  page_size:
    type: integer
    required: false
    description: Data per page, max 200.
  page_num:
    type: integer
    required: false
    description: Page number, starting from 1, default 1.
  quick_filter_id:
    type: string
    required: false
    description: Quick filter ID to filter data in the view list. From Get the List of Views and Settings (data[].quick_filters[].quick_filter_id).

outputs:
  data:
    type: object
    description: View info: name, view_id, editable, created_at, created_by, modified_by, work_item_id_list (list of work item IDs in the view).
  pagination:
    type: object
    description: total, page_num, page_size.

constraints:
  - Permission: Permission Management – View
  - Panorama (multi-project) view not supported; use Panorama View API instead

error_mapping:
  30004: View not exist
  50006: Es searching too many docs (query exceeds 200,000; add filters to reduce)
  20012: View Is Not In The Input Project (view's space does not match project_key)
  30014: Work item not found (work item type key does not exist)
  50006: Can not handle multiProjectView (panorama view not supported; use Panorama View API)
```

### Usage notes

- **view_id**: From the view page URL (e.g. `.../storyView/RHCFGTzDa` → view_id `RHCFGTzDa`) or from **Get the List of Views and Settings** (data[].view_id).
- **work_item_id_list**: List of work item IDs shown in this view; use these IDs with work item APIs to get full details.
- **quick_filter_id**: Optional; from **Get the List of Views and Settings** with **is_query_quick_filter** true (data[].quick_filters[].quick_filter_id).
- Query result cap: if the view would return more than 200,000 docs, 50006 is returned; narrow with **quick_filter_id** or other filters.
- **20012**: The view belongs to a different space than **project_key**; use the correct space.
- Panorama view: this interface returns 50006 for multi-project view; use **Get the List of Work Items in Views (Panorama View)** for that scenario.

---

## Get the List of Work Items in Views (Panorama View)

Obtain the list and detailed information of all work item instances in the specified panoramic (multi-project) view. Response follows WorkItemInfo (id, name, work_item_type_key, project_key, simple_name, template_id, template, pattern, sub_stage, work_item_status, current_nodes, state_times, created_by, updated_by, created_at, updated_at, fields). Permission: Permission Management – Views. For details, see Permission Management.

### When to Use

- When listing work items in a **panorama view** (multi-project view); use this API instead of Get the List of Work Items in Views (which returns 50006 for panorama view)
- When you need full work item detail per item (WorkItemInfo with fields, current_nodes, state_times) rather than only IDs
- When paginating with **page_size** max 50 and optional **quick_filter_id** from the view list interface

### API Spec: get_list_of_work_items_in_views_panorama

```yaml
name: get_list_of_work_items_in_views_panorama
type: api
description: >
  Obtain the list and detailed information of all work item instances in the
  specified panoramic view. Returns list per WorkItemInfo with pagination.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/view/{view_id}
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
  view_id:
    type: string
    required: true
    description: >
      View ID. From view page URL (e.g. .../storyView/RHCFGTzDa then view_id is RHCFGTzDa),
      or from Get the List of Views and Settings (data[].view_id).

inputs:
  page_size:
    type: integer
    required: false
    description: Data per page, max 50.
  page_num:
    type: integer
    required: false
    description: Page number, starting from 1, default 1.
  quick_filter_id:
    type: string
    required: false
    description: Quick filter ID. From Get the List of Views and Settings (data[].quick_filters[].quick_filter_id).

outputs:
  data:
    type: array
    description: >
      List of work item info per WorkItemInfo: id, name, work_item_type_key,
      project_key, simple_name, template_id, template, pattern, sub_stage,
      work_item_status, current_nodes, state_times, created_by, updated_by,
      created_at, updated_at, fields.
  pagination:
    type: object
    description: Pagination information.

constraints:
  - Permission: Permission Management – Views
  - For panorama (multi-project) views only; use Get the List of Work Items in Views for fixed single-space views

error_mapping:
  30004: View not exist (current view_id does not exist)
  20003: Wrong WorkItemType Param (work_item_type_key not filled in when required for specified work item list)
```

### Usage notes

- **view_id**: From the view page URL or from **Get the List of Views and Settings** (data[].view_id). Must be a panorama view; for fixed views use Get the List of Work Items in Views.
- **data**: Each element is full **WorkItemInfo** (id, name, work_item_type_key, project_key, simple_name, template, pattern, sub_stage, current_nodes, state_times, fields, etc.) — no need to call work item detail API per ID for basic display.
- **page_size**: Max 50 (smaller than the fixed-view API’s 200).
- **quick_filter_id**: Optional; from **Get the List of Views and Settings** with **is_query_quick_filter** true.
- **20003**: When the API requires a work item type filter for the specified list, ensure the required parameter (e.g. work_item_type_key) is provided per product behavior.

---

## Create a Fixed View

Add a fixed view under the specified space and work item type. Request supplies **work_item_id_list** (max 200), **name**, and optional collaboration settings. Returns the newly created view (FixView: view_id, name, work_item_id_list, editable, created_by, created_at, modified_by) and pagination. Permission: Permission Management – Views & Metrics. For details, see Permission Management.

### When to Use

- When creating a new fixed view for a work item type (e.g. story) with a chosen list of work item IDs
- When setting **cooperation_mode** (1: specified users/teams, 2: all space admins, 3: all space members) and optionally **cooperation_user_keys** / **cooperation_team_ids**
- When you need the returned **view_id** for Get the List of Work Items in Views or Update/Delete Views

### API Spec: create_fixed_view

```yaml
name: create_fixed_view
type: api
description: >
  Add a fixed view under the specified space and work item type. Requires
  work_item_id_list (max 200) and name. Returns new view (FixView) and pagination.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/{work_item_type_key}/fix_view
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
  work_item_id_list:
    type: array
    items: integer
    required: true
    description: List of work item IDs to show in the view; max 200 items.
  name:
    type: string
    required: true
    description: View name.
  cooperation_mode:
    type: integer
    required: false
    description: >
      Collaboration scope. Default 1. 1: Specified personnel or teams;
      2: All space administrators; 3: All space members.
  cooperation_user_keys:
    type: array
    items: string
    required: false
    description: user_key list; applies when cooperation_mode is 1. From avatar in Feishu/Meegle or Search user list within tenant.
  cooperation_team_ids:
    type: array
    items: integer
    required: false
    description: team_id list; applies when cooperation_mode is 1. From Get team members in the space.

outputs:
  data:
    type: object
    description: Newly created view per FixView (view_id, name, work_item_id_list, editable, created_by, created_at, modified_by).
  pagination:
    type: object
    description: total, page_num, page_size for work items in the view.

constraints:
  - Permission: Permission Management – Views & Metrics

error_mapping:
  30005: WorkItem Not Found (fill in correct and valid work_item_id_list)
  1000053645: Workitem Ids Limit 200 For Fix View (work_item_id_list max 200)
  50006: Invalid params (work_item_id_list missing)
  20010: WorkItemType Is Not Same (work item types in list do not match work_item_type_key)
  30004: View Not Found (fixed view creation error / view does not exist)
```

### Usage notes

- **work_item_id_list**: Must be valid work item IDs under the space; max **200** items. All must match **work_item_type_key** (20010 otherwise). Invalid IDs return 30005.
- **cooperation_mode** **1**: Provide **cooperation_user_keys** and/or **cooperation_team_ids**; user_key from double-click avatar in space or Search user list within tenant; team_id from Get team members in the space.
- **data.view_id**: Use for Get the List of Work Items in Views, Update a Fixed View, or Delete Views.
- **50006**: Request is invalid when **work_item_id_list** is missing.

---

## Update a Fixed View

Add or remove work item instances in a specified fixed view. Send either **add_work_item_ids** or **remove_work_item_ids** (not both, not both empty); each list has a maximum of 200 items. On success, **data** is null. Permission: Permission Management – Views & Metrics. For details, see Permission Management.

### When to Use

- When adding work items to an existing fixed view (**add_work_item_ids**) or removing them (**remove_work_item_ids**)
- When **view_id** comes from Get the List of Views and Settings or Create a Fixed View
- One operation per request: either add or remove, not both; at least one of the two lists must be non-empty

### API Spec: update_fixed_view

```yaml
name: update_fixed_view
type: api
description: >
  Add or remove work item instances in a fixed view. Pass either add_work_item_ids
  or remove_work_item_ids (not both; not both empty). Max 200 per list.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/{work_item_type_key}/fix_view/{view_id}
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
  view_id:
    type: string
    required: true
    description: View ID. From view page URL or Get the List of Views and Settings / Create a Fixed View.

inputs:
  add_work_item_ids:
    type: array
    items: integer
    required: false
    description: Work item IDs to add to the view; max 200. Cannot be used together with remove_work_item_ids; one of add/remove must be non-empty.
  remove_work_item_ids:
    type: array
    items: integer
    required: false
    description: Work item IDs to remove from the view; max 200. Cannot be used together with add_work_item_ids; one of add/remove must be non-empty.

outputs:
  data:
    type: object
    description: Null on success; no return value on failure.

constraints:
  - Permission: Permission Management – Views & Metrics
  - Exactly one of add_work_item_ids or remove_work_item_ids must be provided and non-empty (not both, not both empty)

error_mapping:
  30004: View not exist (view_id in path does not exist)
  20005: Missing Param (work_item_id in add_work_item_ids does not exist — has no workitems)
  1000053645: Workitem Ids Limit 200 For Fix View (add or remove list exceeds 200)
  10001: Invalid req (No Permission — no operation permission for this view)
  20005: Missing Param (can't both add and remove workitems — pass only one of add_work_item_ids or remove_work_item_ids, and it must be non-empty)
```

### Usage notes

- **view_id**: From the view page URL or from **Get the List of Views and Settings** / **Create a Fixed View** (data.view_id).
- **add_work_item_ids** vs **remove_work_item_ids**: Pass **only one** of them per request, and it must be **non-empty**. Passing both or both empty returns 20005.
- Each list: max **200** IDs per request (1000053645 if exceeded). IDs in **add_work_item_ids** must exist (20005 “has no workitems” otherwise).
- **10001**: Caller does not have permission to modify this view.

---

## Create a Conditional View

Add a new conditional view under the specified space and work item type. Request includes **search_group** (filter conditions: conjunction, search_params with param_key, value, operator). Returns **view_id**. Permission: Permission Management – Views. For details, see Permission Management.

### When to Use

- When creating a conditional view (filter-based) for a work item type with **search_group** (AND/OR and search_params)
- When setting **cooperation_mode** (1: specified users/teams, 2: all space admins, 3: all space members) and optionally **cooperation_user_keys** / **cooperation_team_ids**
- When you need the returned **view_id** for Get the List of Work Items in Views or Update/Delete Views

### API Spec: create_conditional_view

```yaml
name: create_conditional_view
type: api
description: >
  Add a new conditional view under the specified space and work item type.
  Requires project_key, work_item_type_key, name, and search_group. Returns view_id.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/view/v1/create_condition_view
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
      Space ID (project_key). Double-click space name in Meegle to obtain.
      Note: Space domain names (simple_name) are not supported for this API.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.
  name:
    type: string
    required: true
    description: View name.
  search_group:
    type: object
    required: true
    description: >
      Filter conditions for combined conditional search. conjunction (e.g. AND)
      and search_params (array of param_key, value, operator e.g. "=").
      For date/date+time fields use UTC format (e.g. 2024-09-01T00:00:00+07:00);
      hour/minute/second-level filtering not supported, day-level only.
    properties:
      conjunction: { type: string }
      search_params:
        type: array
        items:
          type: object
          properties:
            param_key: { type: string }
            value: {}
            operator: { type: string }
  cooperation_mode:
    type: integer
    required: false
    description: >
      Collaboration scope. Default 1. 1: Specified personnel or teams;
      2: All space administrators; 3: All space members.
  cooperation_user_keys:
    type: array
    items: string
    required: false
    description: user_key list; applies when cooperation_mode is 1.
  cooperation_team_ids:
    type: array
    items: integer
    required: false
    description: team_id list; applies when cooperation_mode is 1. From Get team members in the space.

outputs:
  data:
    type: object
    description: view_id (string) of the newly created conditional view.

constraints:
  - Permission: Permission Management – Views
  - project_key must be space ID; simple_name (domain name) not supported

error_mapping:
  20029: Unsupported Field Type (search param key is invalid; unsupported field keys may be returned in msg)
  50006: Invalid params (e.g. field not found; check request parameters)
```

### Usage notes

- **project_key**: Must be the space **project_key** (double-click space name); **simple_name** (space domain name) is **not** supported for this API.
- **search_group**: **conjunction** (e.g. `"AND"`) and **search_params** (each with **param_key**, **value**, **operator** such as `"="`). **param_key** must be a supported field (20029 if invalid). For date/date+time fields use **UTC** format (e.g. `2024-09-01T00:00:00+07:00`); filtering is at **day** level only (hour/minute/second not supported).
- **data.view_id**: Use for Get the List of Work Items in Views, Update a Conditional View, or Delete Views.
- **cooperation_mode** **1**: Provide **cooperation_user_keys** and/or **cooperation_team_ids** as for Create a Fixed View.

---

## Update a Conditional View

Update the filtering conditions and collaborator information of a specified conditional view. Request includes **view_id**, **search_group** (required), and optional **name**, **cooperation_mode**, **cooperation_user_keys**, **cooperation_team_ids**. On success, no data body is returned (err_code 0). Permission: Permission Management – Views. For details, see Permission Management.

### When to Use

- When changing filter conditions (**search_group**) or collaboration settings of an existing conditional view
- When **view_id** is from the conditional view (e.g. from Create a Conditional View or from browser URL suffix such as .../multiProjectView/view_text → view_id "view_text")
- When renaming the view (**name**) or updating who can collaborate (**cooperation_mode**, **cooperation_user_keys**, **cooperation_team_ids**)

### API Spec: update_conditional_view

```yaml
name: update_conditional_view
type: api
description: >
  Update filtering conditions and collaborator information of a conditional view.
  Requires project_key, work_item_type_key, view_id, and search_group.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/view/v1/update_condition_view
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
      Space ID (project_key). Double-click space name in Meegle to obtain.
      Note: Space domain names (simple_name) are not supported for this API.
  work_item_type_key:
    type: string
    required: true
    description: Work item type. Obtain via Get work item types in space.
  view_id:
    type: string
    required: true
    description: >
      Conditional view ID. Currently only obtainable from the browser URL suffix
      (e.g. .../multiProjectView/view_text then view_id is "view_text").
  search_group:
    type: object
    required: true
    description: >
      Filter conditions. conjunction (e.g. AND) and search_params (param_key, value, operator).
      For date/date+time fields use UTC format; day-level filtering only.
    properties:
      conjunction: { type: string }
      search_params:
        type: array
        items:
          type: object
          properties:
            param_key: { type: string }
            value: {}
            operator: { type: string }
  name:
    type: string
    required: false
    description: View name.
  cooperation_mode:
    type: integer
    required: false
    description: >
      1: Specified persons or teams; 2: All space administrators; 3: All space members. Default 1.
  cooperation_user_keys:
    type: array
    items: string
    required: false
    description: user_key list; applies when cooperation_mode is 1.
  cooperation_team_ids:
    type: array
    items: integer
    required: false
    description: team_id list; applies when cooperation_mode is 1.

outputs:
  data:
    type: object
    description: No data returned on success; check err_code 0.

constraints:
  - Permission: Permission Management – Views
  - project_key must be space ID; simple_name not supported
  - view_id currently only from browser URL suffix (e.g. multiProjectView path)

error_mapping:
  20029: Unsupported Field Type (field types that do not support updates; field key may be in msg)
  50006: Invalid params (check request input parameters)
  30004: View not exist (pass correct view_id; currently only from browser URL suffix, e.g. .../multiProjectView/view_text)
```

### Usage notes

- **view_id**: For this API, **view_id** is currently only obtainable from the **browser URL suffix** (e.g. URL `.../multiProjectView/view_text` → view_id `"view_text"`). Use the correct view_id or 30004 is returned.
- **project_key**: Must be space **project_key**; **simple_name** is not supported.
- **search_group**: Same structure as Create a Conditional View (conjunction, search_params); date fields in UTC, day-level only. Unsupported field types return 20029.
- Success: no **data** in response; **err_code** 0 indicates success.

---

## Delete Views

Delete a view from the specified space. Supports **conditional**, **fixed**, and **panoramic** views. Request is DELETE with **project_key** and **view_id** in path. On success, no data body is returned (err_code 0). Permission: Permission Management – Views & Metrics. For details, see Permission Management.

### When to Use

- When removing a view (fixed, conditional, or panorama) from the space
- When **view_id** comes from Get the List of Views and Settings, Create a Fixed View, Create a Conditional View, or the view page URL

### API Spec: delete_views

```yaml
name: delete_views
type: api
description: >
  Delete a view from the specified space. Supports conditional, fixed, and
  panoramic views. Path params project_key and view_id.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: DELETE
  url: https://{domain}/open_api/{project_key}/fix_view/{view_id}
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
  view_id:
    type: string
    required: true
    description: View ID. From view page URL (e.g. .../storyView/RHCFGTzDa) or Get the List of Views and Settings / Create a Fixed View / Create a Conditional View.

outputs:
  data:
    type: object
    description: No data returned on success; check err_code 0.

constraints:
  - Permission: Permission Management – Views & Metrics

error_mapping:
  30004: View Not Found (current view_id does not exist)
```

### Usage notes

- **view_id**: From the view page URL (e.g. `.../storyView/RHCFGTzDa` → view_id `RHCFGTzDa`) or from **Get the List of Views and Settings** (data[].view_id), **Create a Fixed View** (data.view_id), or **Create a Conditional View** (data.view_id).
- **project_key**: May be space **project_key** or **simple_name** (unlike Create/Update Conditional View).
- Applies to all view types: fixed view, conditional view, and panoramic view.
- Success: no **data** in response; **err_code** 0 indicates success.

---

## Get Detailed Data from Charts

Retrieve the detailed data of a specified metric chart. Request is GET with **project_key** and **chart_id** in path. Response returns chart data (name, chart_id, chart_data_list with dim/value/is_zero_spec, dim_titles, quota_titles). Permission: Permission Management – Metrics & Views. For details, see Permission Management.

### Instructions

- **chart_id**: Obtain from the **browser URL** of the chart page.
- **Timeout**: Some metric charts are complex and require long computation; set **HTTP timeout to more than 60 seconds**.
- **Concurrency**: Metric rate limiting applies. **Control concurrency to 1** — use single-threaded serial calls on a single machine; otherwise you may be rate-limited.

### When to Use

- When fetching chart data for a specific metric chart by **chart_id** (from browser URL or Query all charts by view ID)
- When building dashboards or reporting that display chart dimensions and quota values

### API Spec: get_detailed_data_from_charts

```yaml
name: get_detailed_data_from_charts
type: api
description: >
  Retrieve the detailed data of a specified metric chart. Path params project_key
  and chart_id. Chart ID from browser URL.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/measure/{chart_id}
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
  chart_id:
    type: string
    required: true
    description: Unique identifier for the chart. Obtain from the browser URL of the chart page.

outputs:
  data:
    type: object
    description: >
      Chart data: name, chart_id, chart_data_list (array of dim, value, is_zero_spec),
      dim_titles, quota_titles.

constraints:
  - Permission: Permission Management – Metrics & Views
  - HTTP timeout recommended > 60 seconds for complex charts
  - Concurrency 1 (serial calls) to avoid rate limiting

error_mapping:
  50006: ErrMeasureCommonBizError / 1000051872 business error (exception in chart configuration; check for red-marked config and fix)
  500006: ErrNilChartCfg / 1000050535 chartCfg is nil (chart_id incorrect or chart deleted; verify chart_id and chart existence)
```

### Usage notes

- **chart_id**: From the **browser URL** when viewing the chart, or from **Query all charts by view ID**.
- **data.chart_data_list**: Array of data points; each has **dim** (dimension key-value), **value** (quota key-value), **is_zero_spec**. **dim_titles** and **quota_titles** describe axis labels.
- **50006 / 1000051872**: Chart configuration has an exception; check for configurations marked in red in the product and adjust.
- **500006 / 1000050535**: **chart_id** is invalid or the chart was deleted; confirm chart_id and that the chart exists.

---

## Query all charts by view ID

Query all metric charts under a space view. Request is POST with **project_key** and **view_id** in body; optional **page_num** (default 1) and **page_size** (max 200, default 50). Response returns **chart_list** (chart_id, chart_name per chart) and **chart_page** (total, page_num, page_size). Permission: Permission Management – Views & analytics. For details, see Permission Management.

### When to Use

- When listing all metric charts under a view by **view_id** (from Get the List of Views and Settings or the view page URL)
- When you need **chart_id** and **chart_name** for each chart (e.g. to call Get Detailed Data from Charts)
- When paginating chart results (**page_size** max 200)

### API Spec: query_all_charts_by_view_id

```yaml
name: query_all_charts_by_view_id
type: api
description: >
  Query all metric charts under the space view. Body: project_key, view_id,
  optional page_num/page_size. Returns chart_list and chart_page.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/measure/charts
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
  view_id:
    type: string
    required: true
    description: View ID. From view page URL (e.g. .../storyView/RHCFGTzDa) or Get the List of Views and Settings.
  page_num:
    type: integer
    required: false
    description: Page number, starting from 1; default 1.
  page_size:
    type: integer
    required: false
    description: Data per page, max 200; default 50.

outputs:
  data:
    type: object
    description: >
      chart_list (array of chart_id, chart_name per chart),
      chart_page (total, page_num, page_size).

constraints:
  - Permission: Permission Management – Views & analytics

error_mapping:
  1000051401: ErrnoInvalidParameter / Invalid parameter (unreasonable parameters in input; check request)
```

### Usage notes

- **view_id**: From the view page URL (e.g. `.../storyView/RHCFGTzDa`) or from **Get the List of Views and Settings** (data[].view_id).
- **data.chart_list**: Each item has **chart_id** and **chart_name**; use **chart_id** with **Get Detailed Data from Charts** to fetch chart detail.
- **data.chart_page**: **total** (total pages or total count per product), **page_num**, **page_size** for pagination.
- **1000051401**: Invalid or unreasonable input parameters; verify project_key and view_id.
