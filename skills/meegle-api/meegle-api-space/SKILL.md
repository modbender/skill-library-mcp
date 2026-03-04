---
name: meegle-api-space
description: Meegle OpenAPI for space (project) operations.
metadata: { openclaw: {} }
---

# Meegle API — Space

Space (project) OpenAPIs: list spaces, get details, get team members.

---

## Get Space List

Obtain the list of spaces that the specified user has permission to access and where the plugin is installed.

### Points to Note

When using a **virtual token**, only spaces in Permission Management > Select Data Scope can be queried. To query other spaces, use the official (non-virtual) token.

### When to Use

- When listing spaces accessible to a user
- When building space pickers or navigation
- When checking which spaces the plugin is installed in

### API Spec: get_space_list

```yaml
name: get_space_list
type: api
description: List spaces user can access where plugin is installed.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/projects" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { user_key: { type: string, required: true }, order: { type: array, required: false } }
outputs: { data: array }
constraints: [Permission: Space; virtual token limited to Select Data Scope]
error_mapping: { 30006: User not found, 10302: User resigned }
```

### Usage notes

- **user_key**: Required; identifies whose spaces to list.
- **order**: Optional; use `["-last_visited"]` for most recently visited first.

---

## Get Space Details

Get detailed information of target query spaces where the plugin is installed. When the user specified in the request is a space administrator of the query space, it returns all space information including administrators.

### When to Use

- When fetching space metadata (name, project_key, simple_name)
- When resolving project_key or simple_name to full space info
- When checking space administrators (visible only if querying user has space admin permission)

### API Spec: get_space_details

```yaml
name: get_space_details
type: api
description: Space details; if user is space admin, includes administrators.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/projects/detail" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { user_key: { type: string, required: true }, project_keys: { type: array, max_items: 100 }, simple_names: { type: array } }
outputs: { data: object }
constraints: [Permission: Permissions, project_keys or simple_names required, max 100]
```

### Usage notes

- **user_key**: Required; when user is space admin, response includes administrators.
- **project_keys** or **simple_names**: At least one required; max 100 project_keys.
- **data**: Map of project_key → { name, project_key, simple_name, administrators }.

---

## Get Team Members in Space

Return a list of teams whose visibility is set to "in specified projects" and whose "visible project spaces" is set as the requested space. Each team includes members (user_keys) and administrators.

### When to Use

- When listing teams visible within a space
- When fetching team members and administrators for a space
- When building team pickers or membership UIs

### API Spec: get_team_members_in_space

```yaml
name: get_team_members_in_space
type: api
description: Teams visible in the space (user_keys, administrators).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/teams/all" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true } }
outputs: { data: array }
constraints: [Permission: Permissions]
```

### Usage notes

- **project_key**: Path parameter identifying the space.
- Response: list of teams with team_id, team_name, user_keys (members), administrators.
