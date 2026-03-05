---
name: meegle-api-workflows-and-nodes
description: Meegle OpenAPI for workflow and node operations.
metadata: { openclaw: {} }
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
description: Workflow info for a work item: nodes, connections, schedules, assignees, subtasks; flow_type 0 node / 1 status.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/workflow/query" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { fields: array, flow_type: integer (0|1), expand: object }
outputs: { data: object }
constraints: [Permission Management – Work Items]
error_mapping: { 30005: Work item not found, 20026: FlowType error, 20027: FlowType error, 10001: No permission, 20014: Project mismatch, 50006: DB error, 20015: Field mix specified/excluded }
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
description: WBS workflow for node-flow work item (industry edition); tree, deliverables, connections.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/wbs_view" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { need_union_deliverable: boolean, need_schedule_table_agg: boolean, expand: object }
outputs: { data: object }
constraints: [Work Item Instance permission, WBS or WBS sub work item only]
error_mapping: { 30005: Work item not found, 20089: Not WBS/WBS children, 20014: Project mismatch }
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
description: Update node: owners, node_schedule or schedules, fields, role_assignee.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: PUT, url: "https://{domain}/open_api/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/{node_id}" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string, node_id: string }
inputs: { node_owners: array, node_schedule: object, schedules: array, fields: array, role_assignee: array }
outputs: { data: object }
constraints: [Permission Management]
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
description: Complete (confirm) or rollback a node; optionally update owners, schedule, fields, role_assignee.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/{node_id}/operate" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string, node_id: string }
inputs: { action: confirm|rollback, rollback_reason: string, node_owners: array, node_schedule: object, schedules: array, fields: array, role_assignee: array }
outputs: { data: object }
constraints: [Permission Management]
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
description: Transfer state-flow work item to target state; optional fields and role_owners; transition_id from Get Workflow Detail.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/workflow/{work_item_type_key}/{work_item_id}/node/state_change" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: string, work_item_type_key: string, work_item_id: string }
inputs: { transition_id: integer, fields: array, role_owners: array }
outputs: { data: object }
constraints: [Work Item Instance permission, state-flow only]
error_mapping: { 10002: Illegal transition, 20005: transition_id missing, 30005: Work item not found, 20090: Request intercepted, 20038: Param missing, 30009: Field not found, 30012: State not found, 50006: Field check failed }
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
description: Required info for node/status transition (form_items, node fields, tasks, deliverables); state_key = node or target state; mode optional (unfinished).

auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/transition_required_info/get" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_type_key: string, work_item_id: integer, state_key: string, mode: string }
outputs: { data: object }

constraints: [Permission: Work Item Instance, single-point query]
error_mapping: { 30005: Work item not found, 50006: Node no longer exists }
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
description: Batch query review opinions and conclusions per node; max 10 node_ids.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/finished/batch_query" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_id: integer, node_ids: array (max 10) }
outputs: { data: object }
constraints: [Work Item Instances permission, node_ids ≤ 10]
error_mapping: { 1000051120: Workflow not found, 1000051280: Params invalid }
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
description: Update or reset review opinion and conclusion; node-level or owner-level (operation_type).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/finished/update" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_id: integer, node_id: string, opinion: string, finished_conclusion_option_key: string, operation_type: node|owner, reset: boolean }
outputs: { data: object }
constraints: [Work Item Instance permission]
error_mapping: { 1000051814: Node not exist, 1000051120: Workflow not found, 20007: Work item aborted, 1000053308: Conclusion label not exist, 1000053219: Only node owners, 1000051280: Parameter invalid }
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
description: Query conclusion labels per node (key, label, origin_label); max 10 node_ids.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/work_item/finished/query_conclusion_option" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { project_key: string, work_item_id: integer, node_ids: array (max 10) }
outputs: { data: array }
constraints: [Work Item Instances permission, node_ids ≤ 10]
error_mapping: { 1000051120: Workflow not found }
```

### Usage notes

- **node_ids**: Use node IDs or **state_key** from **Get Workflow Detail** (e.g. `start_0`, `started_0`). Maximum **10** nodes per request.
- **data** items: **finished_conclusion_option** = node-level options; **finished_owners_conclusion_option** = per-owner options; **finished_overall_conclusion_option** = overall options. Use **key** as **finished_conclusion_option_key** in Update Review Opinion and Conclusion.
- Document title in product may appear as "Get Conclusion Option Lable"; API name uses "Label".
