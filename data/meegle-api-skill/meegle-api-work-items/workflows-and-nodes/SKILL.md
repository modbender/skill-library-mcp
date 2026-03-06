---
name: meegle-api-workflows-and-nodes
description: |
  Meegle OpenAPI for workflow and node operations.
metadata:
  openclaw: {}
---

# Meegle API — Workflows & Nodes

Workflow and node related APIs for managing work item workflows and workflow nodes.

## Scope

- Get workflow detail (node/status flow, nodes, connections, schedules, subtasks, forms)
- Get workflow details (WBS)
- Update nodes/scheduling
- Node completion/rollback
- Status flow transition
- Get required information for node or status flow
- Review management

---

## Get Workflow Detail

Obtain the workflow information of a work item instance under the specified space and work item type, including node status, assignees, estimated scores, node forms, subtasks, and connections. Supports node workflow (e.g. requirements) and status workflow (e.g. defects, versions).

### When to Use

- When building workflow UIs or reports for a work item
- When you need node-level data (schedules, owners, node_fields, sub_tasks, checker, finished_infos)
- When distinguishing node flow (flow_type 0) vs status flow (flow_type 1)

### API Spec: get_workflow_detail

```yaml
name: get_workflow_detail
type: api
description: >
  Obtain workflow information of a work item instance: nodes, connections,
  schedules, assignees, node forms, subtasks. Supports node workflow (0) and status workflow (1).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/query
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
    description: Work item type. Obtain via Get work item types in the space.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In details, expand ··· in the upper right, then click ID.

inputs:
  fields:
    type: array
    items: string
    required: false
    description: >
      Control which node form fields are returned. Default: all. Two modes (do not mix):
      Specified: e.g. ["name", "created_at"] returns only those fields.
      Excluded: fields starting with "-", e.g. ["-name", "-created_at"] returns all except those.
  flow_type:
    type: integer
    required: false
    description: >
      Workflow type. Default 0.
      0: Node workflow (e.g. requirements).
      1: Status workflow (required for defects, versions, etc.).
  expand:
    type: object
    required: false
    description: Extra options. Only need_user_detail is supported.
    properties:
      need_user_detail:
        type: boolean
        description: When true, response includes user_details for owners/assignees.

outputs:
  data:
    type: object
    description: >
      Instance workflow per NodesConnections: workflow_nodes (id, name, state_key, status,
      schedules, node_fields, finished_infos, sub_tasks, owners, checker, node_schedule,
      actual_begin_time, actual_finish_time, etc.), connections (source_state_key,
      target_state_key), user_details (when expand.need_user_detail), template_id, version.

constraints:
  - Permission: Permission Management – Work Items

error_mapping:
  30005: Work item not found (no instance for given work_item_id)
  20026: FlowType is error (flow_type in body incorrect)
  20027: FlowType is error (flow_type in body incorrect)
  10001: Operation not permitted (current user lacks permission)
  20014: Project and work item not match (project_key vs work_item_id mismatch)
  50006: Fail to read/write db (retry; escalate if repeated)
  20015: Field mix with '-' and without '-' (use either specified or excluded fields, not both)
```

### Usage notes

- **flow_type**: Use **0** for node-based workflows (e.g. story/requirement); use **1** for status-based workflows (e.g. defect, version).
- **fields**: Use only one mode—either positive list (e.g. `["name","created_at"]`) or negative list (e.g. `["-name","-created_at"]`). Mixing causes 20015.
- **expand.need_user_detail**: Set to `true` to get **user_details** (email, name_cn, name_en, user_key, username) for owners/assignees in the response.
- **data**: Follows **NodesConnections**; **workflow_nodes** contain schedules, node_fields, sub_tasks, checker, finished_infos, owner_usage_mode, etc.; **connections** define transitions between state_key values.

---

## Get Workflow Details (WBS)

Obtain the WBS (Work Breakdown Structure) workflow information of a node-flow work item instance. Available in the industry special edition. Returns WBS tree (related_sub_work_items, related_parent_work_item), deliverables, and connections.

### When to Use

- When building WBS views or hierarchy UIs for node-flow work items
- When you need integrated deliverables (need_union_deliverable) or schedule table aggregation (need_schedule_table_agg)
- When the work item is a WBS work item or WBS sub–work item

### API Spec: get_workflow_details_wbs

```yaml
name: get_workflow_details_wbs
type: api
description: >
  Obtain WBS workflow information of a node flow work item instance (industry special edition).
  Returns WBS tree, deliverables, and connections.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/wbs_view
  headers:
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
    description: Work item type. Obtain via Get work item types in the space.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In details, expand ··· in the upper right, then click ID.

inputs:
  need_union_deliverable:
    type: boolean
    required: false
    description: Whether to include integrated deliverables in the response (query).
  need_schedule_table_agg:
    type: boolean
    required: false
    description: Extended query; whether to include custom column aggregation fields for the schedule (query).
  expand:
    type: object
    required: false
    description: Optional expand options (query; structure as per product).

outputs:
  data:
    type: object
    description: >
      WBS details: template_key, related_sub_work_items (node_uuid, work_item_id, type, name,
      wbs_status_map, sub_work_item, deliverable, union_deliverable, role_owners), related_parent_work_item
      (is_top, work_item_id, name, template_key, template_version, work_item_type_key, template_id, template_name),
      connections (source_state_key, target_state_key).

constraints:
  - Permission: Permission Management – Work Item Instance
  - Work item must be a WBS work item or WBS sub–work item (node flow; industry special edition)

error_mapping:
  30005: Work item not found (work_item_id incorrect)
  20089: Current work item is not WBS or WBS children (not a WBS / sub–WBS work item)
  20014: Project and work item not match (space does not match work item)
```

### Usage notes

- **WBS**: Only applies to node-flow work items in the **industry special edition** that are WBS or WBS sub–work items; otherwise 20089.
- **Query params**: Pass **need_union_deliverable** and **need_schedule_table_agg** as query parameters (e.g. `?need_union_deliverable=true&need_schedule_table_agg=true`).
- **data.related_sub_work_items**: Tree of nodes and sub_tasks with deliverable, role_owners, wbs_status_map; **related_parent_work_item** gives parent WBS context; **connections** define state transitions.

---

## Update Nodes/Scheduling

Update specific node information in a work item: node owners, scheduling (node_schedule or differential schedules), node form fields, and role assignees. Permissions are under Developer Platform – Permissions (Permission Management).

### When to Use

- When updating node owners (node_owners or role_assignee), schedule (node_schedule or schedules), or node form fields
- When using differential scheduling (schedules array) for a task node with at least two responsible persons
- When clearing all node owners by passing an empty node_owners array

### API Spec: update_nodes_scheduling

```yaml
name: update_nodes_scheduling
type: api
description: >
  Update node information in a work item: owners, scheduling, fields, role assignees.
  Supports dynamic scheduling (node_schedule) and differential scheduling (schedules).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: PUT
  url: https://{domain}/open_api/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/{node_id}
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
    description: Work item type. Refer to Get work item types in space.
  work_item_id:
    type: string
    required: true
    description: Work item ID (API types as int64; string accepted in path).
  node_id:
    type: string
    required: true
    description: Target node ID.

inputs:
  node_owners:
    type: array
    items: string
    required: false
    description: >
      user_key array. Omit to leave unchanged; pass empty array [] to remove all owners.
  node_schedule:
    type: object
    required: false
    description: >
      Node-level schedule (dynamic calculation). Omit or null to leave unchanged.
    properties:
      estimate_start_date:
        type: integer
        description: Start timestamp (ms).
      estimate_end_date:
        type: integer
        description: End timestamp (ms).
      points:
        type: number
        description: Points.
  schedules:
    type: array
    required: false
    description: >
      Subscheduling array (differential scheduling). Omit or null to leave unchanged.
      Requires at least 2 responsible persons on the task node to take effect.
    items:
      type: object
      properties:
        estimate_start_date: { type: integer }
        estimate_end_date: { type: integer }
        points: { type: number }
        owners: { type: array, items: string }
  fields:
    type: array
    required: false
    description: Node form fields to update (FieldValuePair).
    items:
      type: object
      properties:
        field_alias: { type: string }
        field_key: { type: string }
        field_type_key: { type: string }
        field_value: {}
  role_assignee:
    type: array
    required: false
    description: >
      Role owners for the node. Use when node is bound to roles (e.g. PM, DA).
    items:
      type: object
      properties:
        role: { type: string }
        owners: { type: array, items: string }

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Developer Platform – Permissions (Permission Management)
```

### Usage notes

- **node_owners**: Omit = no change; **[]** = remove all owners. Values are **user_key** (from Meegle, e.g. double-click avatar in Developer Platform).
- **node_schedule** vs **schedules**: Use **node_schedule** for a single dynamic schedule; use **schedules** for differential scheduling per owner (task node must have at least 2 responsible persons).
- **fields**: Each item needs **field_key**, **field_type_key**, **field_value**; **field_alias** is the field identifier.
- **role_assignee**: Pass **role** and **owners** (user_key list); empty **owners** clears that role’s assignees.

---

## Node Completion/Rollback

Complete or rollback a node for a specific work item. Optionally update node owners, scheduling, fields, and role assignees in the same request. Permissions are under Developer Platform – Permissions (Permission Management).

### When to Use

- When completing a node (action **confirm**) or rolling back a node (action **rollback**)
- When submitting rollback reason (**rollback_reason** required for rollback)
- When updating node data (owners, schedule, fields, role_assignee) together with the operate action

### API Spec: node_completion_rollback

```yaml
name: node_completion_rollback
type: api
description: >
  Complete or rollback a node; optionally update node owners, scheduling, fields, and role assignees.
  Same permission and path pattern as workflow node operations.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/{node_id}/operate
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
    description: Work item type. Refer to Get work item types in space.
  work_item_id:
    type: string
    required: true
    description: Work item ID (API types as int64; string accepted in path).
  node_id:
    type: string
    required: true
    description: Target node ID; same as node state_key from Get Workflow Detail.

inputs:
  action:
    type: string
    required: true
    description: Operation type. confirm = completion; rollback = rollback.
    enum: [confirm, rollback]
  rollback_reason:
    type: string
    required: false
    description: Reason for rollback; required when action is rollback.
  node_owners:
    type: array
    items: string
    required: false
    description: >
      user_key array. Omit to leave unchanged; pass empty array [] to remove all owners.
  node_schedule:
    type: object
    required: false
    description: Node schedule (non-differentiated). Omit or empty if no update.
    properties:
      estimate_start_date: { type: integer }
      estimate_end_date: { type: integer }
      points: { type: number }
  schedules:
    type: array
    required: false
    description: Sub-scheduling array (differential scheduling). Null if no update.
    items:
      type: object
      properties:
        estimate_start_date: { type: integer }
        estimate_end_date: { type: integer }
        points: { type: number }
        owners: { type: array, items: string }
  fields:
    type: array
    required: false
    description: Node form fields to update (FieldValuePair).
    items:
      type: object
      properties:
        field_alias: { type: string }
        field_key: { type: string }
        field_type_key: { type: string }
        field_value: {}
  role_assignee:
    type: array
    required: false
    description: Role owners for the node (e.g. PM, DA).
    items:
      type: object
      properties:
        role: { type: string }
        owners: { type: array, items: string }

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Developer Platform – Permissions (Permission Management)
```

### Usage notes

- **action**: Use **confirm** to complete the node, **rollback** to roll it back. **rollback_reason** is required when **action** is **rollback**.
- **node_id**: Must match the node’s **state_key** from Get Workflow Detail (e.g. `start`, `doing`, `end`).
- Optional body fields (**node_owners**, **node_schedule**, **schedules**, **fields**, **role_assignee**) behave like Update Nodes/Scheduling: omit = no change; empty array for **node_owners** = remove all owners.

---

## Status Flow Transition

Transfer a state-flow work item instance to the specified state and optionally update status form fields and role owners. Use **transition_id** from Get Workflow Detail (connections). Permission: Permission Management – Work Item Instance.

### When to Use

- When moving a state-flow work item (e.g. defect, version) to another state
- When updating status form fields or role owners during the transition
- When driving status changes from integrations or automation

### API Spec: status_flow_transition

```yaml
name: status_flow_transition
type: api
description: >
  Transfer a state flow work item to the specified state; optionally update
  status form fields and role_owners. transition_id comes from Get Workflow Detail (connections).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/state_change
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
    description: Work item type. Obtain via Get work item types in the space.
  work_item_id:
    type: string
    required: true
    description: Work item instance ID. In details, expand ··· in the upper right, then click ID.

inputs:
  transition_id:
    type: integer
    required: false
    description: >
      ID for transitioning to the next state. Obtain from Get Workflow Detail (flow_type 1):
      connections structure, transition_id field. Must not be null or 0 for a valid transition.
  fields:
    type: array
    required: false
    description: Fields to update; only status form fields can be updated (FieldValuePair).
    items:
      type: object
      properties:
        field_alias: { type: string }
        field_key: { type: string }
        field_type_key: { type: string }
        field_value: {}
  role_owners:
    type: array
    required: false
    description: Roles and responsible persons (role, owners).
    items:
      type: object
      properties:
        role: { type: string }
        owners: { type: array, items: string }

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Work Item Instance
  - Applies to state-flow work items (flow_type 1), not node-flow

error_mapping:
  10002: Illegal operation (status transition does not match current instance status)
  20005: Missing param (transition_id cannot be null or 0)
  30005: Work item not found (no instance for given work_item_id)
  20090: Request intercepted (plugin interception rules in space)
  20038: Param missing (required status transition form field not filled; check template)
  30009: Field not found (field key not found for current work item type)
  30012: State not found in state flow (workflow template incorrect; try upgrading template)
  50006: Failed to check field (admin config changed; option values no longer exist or disabled)
```

### Usage notes

- **transition_id**: Get it from **Get Workflow Detail** with **flow_type: 1**; use the **connections** structure’s **transition_id** for the target state. Must not be null or 0 (20005).
- **fields**: Only **status form** fields are updatable; use **field_key**, **field_type_key**, **field_value** (and **field_alias** as identifier). Required fields for the transition must be filled (20038).
- **role_owners**: Same shape as **role_assignee** (role, owners); empty **owners** clears that role’s assignees.
- **10002**: Ensure the requested transition is allowed from the work item’s current state. **20090**: Check space plugin interception rules if the request is blocked.

---

## Get the Required Information for Node or Status Flow

Obtain the required information for a specified node transition or status transition of a work item instance. Single-point query only. Returns required form items, node fields, subtasks, and deliverables. Permission: Permission Management – Work Item Instance.

### When to Use

- Before performing a node or status transition, to know which form fields, node fields, subtasks, or deliverables must be completed
- When building transition UIs that show “what’s missing” (use **mode: unfinished**)
- For both node-flow (state_key = node ID) and state-flow (state_key = target state key) work items

### API Spec: get_required_info_node_or_status_flow

```yaml
name: get_required_info_node_or_status_flow
type: api
description: >
  Get required information for a node or status transition: required form items,
  node fields, subtasks, deliverables. Single-point query. state_key meaning
  depends on workflow type (node flow vs state flow).

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/transition_required_info/get
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
      project_key: Double-click space name in Meegle project space.
      simple_name: From space URL, e.g. https://meegle.com/doc/overview → doc.
  work_item_type_key:
    type: string
    required: false
    description: Work item type. Obtain via Get work item types under the space.
  work_item_id:
    type: integer
    required: true
    description: Work item instance ID. In details, expand ··· > ID in the upper right.
  state_key:
    type: string
    required: true
    description: >
      Node flow: node ID (node_key / state_key).
      State flow: target state key for the state flow transfer.
      Query specific values via Get Workflow Detail.
  mode:
    type: string
    required: false
    description: >
      Query mode. Default: all required fields.
      unfinished: Only return incomplete required information.

outputs:
  data:
    type: object
    description: >
      TransRequiredInfo: form_items (required form fields; class control/field; key; finished;
      state_info with node_fields for “node info component”; sub_field for compound/multi-member),
      tasks (task_id, finished), deliverables (deliverable_id, finished), node_fields
      (field_key, field_type_key, finished, sub_field, not_finished_owner).

constraints:
  - Permission: Permission Management – Work Item Instance
  - Single-point query only

error_mapping:
  30005: Work item not found (work_item_id incorrect)
  50006: This node no longer exists (state_key incorrect; query via Get Workflow Detail)
```

### Usage notes

- **state_key**: For **node flow**, use the node’s ID (state_key from workflow_nodes). For **state flow**, use the **target** state key for the transition. Get valid values from **Get Workflow Detail**.
- **mode**: Omit or empty for all required info; set **unfinished** to only get items that are not yet filled/completed (e.g. for “what’s missing” UI).
- **data.form_items**: Mix of **class: control** (e.g. workflow_state_info with state_info.node_fields) and **class: field** (field key, field_type_key, finished, sub_field for compound/multi-member). **finished** indicates whether the requirement is satisfied.
- **data.tasks** / **data.deliverables**: Required subtasks and deliverables for the transition; **finished** indicates completion. **data.node_fields**: Required node-level fields, with **sub_field** and **not_finished_owner** for multi-owner fields.

---

## Batch Request Review Opinion and Review Conclusion

Query review opinions and conclusions of nodes in batches. Returns summary_mode, opinion (finished_opinion_result, owners_finished_opinion_result), and conclusion (finished_conclusion_result, owners_finished_conclusion_result) per node. Permission: Permission Management – Work Item Instances.

### When to Use

- When loading review opinions and conclusions for multiple nodes of a work item in one request
- When building review/approval UIs that show per-node opinion and conclusion (up to 10 nodes per request)
- When node IDs or state_keys come from Get Workflow Detail

### API Spec: batch_request_review_opinion_and_conclusion

```yaml
name: batch_request_review_opinion_and_conclusion
type: api
description: >
  Query review opinions and conclusions of nodes in batches. Returns opinion and
  conclusion per node (summary_mode, opinion, conclusion). Max 10 node_ids per request.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/finished/batch_query
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
      Space ID (project_key). Double-click space name in Meegle project space to obtain.
  work_item_id:
    type: integer
    required: true
    description: Work item instance ID. In details, expand ··· > ID in the upper right.
  node_ids:
    type: array
    items: string
    required: true
    description: >
      List of target node IDs (node IDs or state_keys). Obtain via Get Workflow Detail.
      Number of nodes must not exceed 10.

outputs:
  data:
    type: object
    description: >
      project_key, work_item_id, finished_infos (list). Each element: node_id,
      summary_mode (calculation | independence), opinion (finished_opinion_result,
      owners_finished_opinion_result with owner user_key and finished_opinion_result),
      conclusion (finished_conclusion_result and owners_finished_conclusion_result
      with key, label, origin_label).

constraints:
  - Permission: Permission Management – Work Item Instances
  - node_ids length ≤ 10

error_mapping:
  1000051120: Workflow not found (work item instance does not exist; check work_item_id)
  1000051280: Params invalid (required parameters not filled)
```

### Usage notes

- **node_ids**: Use node IDs or **state_key** values from **Get Workflow Detail** (e.g. `start_0`, `start_1`). Maximum **10** nodes per request.
- **summary_mode**: **calculation** = summary calculation; **independence** = independent completion.
- **opinion** / **conclusion**: **finished_opinion_result** and **finished_conclusion_result** are the aggregated result; **owners_finished_opinion_result** and **owners_finished_conclusion_result** give per-owner (user_key) results. Conclusion uses **key**, **label**, **origin_label**.

---

## Update Review Opinion and Conclusion

Update the review comments and conclusion of a node, or perform a reset (empty) operation. Supports node-level review (node leader only) and owner-level personal comments. Permission: Permission Management – Work Item Instance.

### When to Use

- When updating a node’s review opinion (opinion) or conclusion (finished_conclusion_option_key)
- When clearing opinion or conclusion (pass empty string) or resetting all review info (reset: true; transfer person only)
- When operating on node review (operation_type: node) vs personal comments (operation_type: owner)

### API Spec: update_review_opinion_and_conclusion

```yaml
name: update_review_opinion_and_conclusion
type: api
description: >
  Update review opinion and conclusion for a node, or reset. Supports node-level
  (node leader) and owner-level (personal) operations.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/finished/update
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
  work_item_id:
    type: integer
    required: true
    description: Work item instance ID. In details, expand ··· > ID in the upper right.
  node_id:
    type: string
    required: false
    description: Target node ID (same as state_key). Obtain via Get Workflow Detail.
  opinion:
    type: string
    required: false
    description: Review comments. Empty string = delete; omit = no change.
  finished_conclusion_option_key:
    type: string
    required: false
    description: >
      Review conclusion label key. From Batch Request Review Opinion and Conclusion
      (conclusion key). Empty string = delete; omit = no change.
  operation_type:
    type: string
    required: false
    description: >
      node: Operate on node review info (only node leader).
      owner: Operate on personal comments. Required when reset is false for owner-level update.
    enum: [node, owner]
  reset:
    type: boolean
    required: false
    description: >
      Whether to empty current review info. Default false. Only the transfer person can reset.
      When true, opinion, finished_conclusion_option_key, and operation_type may be omitted.

outputs:
  data:
    type: object
    description: Empty object on success.

constraints:
  - Permission: Permission Management – Work Item Instance

error_mapping:
  1000051814: The node does not exist
  1000051120: Workflow not found (instance does not exist)
  20007: Work item is already aborted (cannot operate on terminated work items)
  1000053308: The review conclusion label does not exist
  1000053219: Only node owners can operate (no node owner permission)
  1000051280: Parameter invalid
```

### Usage notes

- **opinion** / **finished_conclusion_option_key**: Omit = no change; **""** = delete that value. **finished_conclusion_option_key** should match a conclusion **key** from Batch Request Review Opinion and Conclusion (or Get Conclusion Option Label).
- **operation_type**: Use **node** for node-level review (node leader only); use **owner** for personal comments. Required when **reset** is false and you are updating owner-level data.
- **reset: true**: Clears current review info; only the **transfer person** can do this. When reset is true, **opinion**, **finished_conclusion_option_key**, and **operation_type** may be left empty.

---

## Get Conclusion Option Label

Query the configured review conclusion labels for the specified nodes. Use when filling in node review conclusions (e.g. for Update Review Opinion and Conclusion). Permission: Permission Management – Work Item Instances.

### When to Use

- When building review/approval UIs that need the list of allowed conclusion options per node
- When validating or displaying conclusion options (key, label, origin_label) for **finished_conclusion_option_key**
- When node IDs or state_keys come from Get Workflow Detail (max 10 nodes per request)

### API Spec: get_conclusion_option_label

```yaml
name: get_conclusion_option_label
type: api
description: >
  Query configured review conclusion labels per node. Returns finished_conclusion_option,
  finished_owners_conclusion_option, finished_overall_conclusion_option (key, label, origin_label).
  Max 10 node_ids per request.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/work_item/finished/query_conclusion_option
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
  work_item_id:
    type: integer
    required: true
    description: Work item instance ID. In details, ··· in the upper right, then ID to copy.
  node_ids:
    type: array
    items: string
    required: true
    description: >
      List of target node IDs (node IDs or state_key). Obtain via Get Workflow Detail.
      Number of nodes must not exceed 10.

outputs:
  data:
    type: array
    description: >
      One object per node. Each has node_id, finished_conclusion_option (key, label, origin_label),
      finished_owners_conclusion_option, finished_overall_conclusion_option (same key/label/origin_label structure).

constraints:
  - Permission: Permission Management – Work Item Instances
  - node_ids length ≤ 10

error_mapping:
  1000051120: Workflow not found (instance does not exist)
```

### Usage notes

- **node_ids**: Use node IDs or **state_key** from **Get Workflow Detail** (e.g. `start_0`, `started_0`). Maximum **10** nodes per request.
- **data** items: **finished_conclusion_option** = node-level options; **finished_owners_conclusion_option** = per-owner options; **finished_overall_conclusion_option** = overall options. Use **key** as **finished_conclusion_option_key** in Update Review Opinion and Conclusion.
- Document title in product may appear as "Get Conclusion Option Lable"; API name uses "Label".
