---
name: meegle-api-space
description: |
  Meegle OpenAPI for space (project) operations.
metadata:
  openclaw: {}
---

# Meegle API — Space

Space (project) related OpenAPIs. Use when you need to manage or query Meegle spaces/projects.

## Scope

This skill covers space (project) operations including:

- List spaces
- Get space details
- Create, update space
- Related space management endpoints

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
description: >
  Obtain the list of spaces that the specified user has permission to access
  and where the plugin is installed.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/projects
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  user_key:
    type: string
    required: true
    description: |
      Unique identifier of the user whose spaces to query.
      Own user_key: Double-click personal avatar in Meegle space (lower left).
      Other members: Use Get Tenant User List.
  order:
    type: array
    items: string
    required: false
    description: |
      Sort field(s). Format: prefix + field. + = ascending, - = descending; no prefix = ascending.
      Currently only last_visited is supported.
      Examples: ["last_visited"], ["+last_visited"], ["-last_visited"]

outputs:
  data:
    type: array
    items: string
    description: List of space project_keys that meet the conditions.

constraints:
  - Permission: Permission Management – Space
  - Virtual token: limited to spaces in Permission Management > Select Data Scope

error_mapping:
  30006: User not found (incorrect user_key or empty result)
  10302: User is resigned (queried user has left the company)
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
description: >
  Get detailed information of target query spaces where the plugin is installed.
  When the user is a space administrator, returns full space info including administrators.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: POST
  url: https://{domain}/open_api/projects/detail
  headers:
    Content-Type: application/json
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

inputs:
  user_key:
    type: string
    required: true
    description: >
      Query specified user. When the user is a space administrator,
      return administrator info for the space.
  project_keys:
    type: array
    items: string
    required: false
    constraints:
      max_items: 100
    description: >
      List of space project_keys to query. Either project_keys or simple_names required. Max 100.
  simple_names:
    type: array
    items: string
    required: false
    description: >
      List of space domain names (simple_name) to query.
      Either project_keys or simple_names required.

outputs:
  data:
    type: object
    additionalProperties:
      administrators: array
      name: string
      project_key: string
      simple_name: string
    description: |
      Map of project_key → Project. Key is project_key.
      Project: name, project_key, simple_name, administrators (user_key list).
      administrators visible only if querying user has space admin permission.

constraints:
  - Permission: Developer Platform – Permissions / Permission Management
  - Either project_keys or simple_names must be provided (both can be provided)
  - project_keys max 100
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
description: >
  Return a list of teams whose visibility is "in specified projects" and
  whose visible project spaces includes the requested space.

auth:
  type: plugin_access_token
  header: X-Plugin-Token
  user_header: X-User-Key

http:
  method: GET
  url: https://{domain}/open_api/{project_key}/teams/all
  headers:
    X-Plugin-Token: "{{resolved_token}}"
    X-User-Key: "{{user_key}}"

path_params:
  project_key:
    type: string
    required: true
    description: >
      Space ID (project_key) or space domain name (simple_name).

outputs:
  data:
    type: array
    items:
      team_id: integer
      team_name: string
      user_keys: array
      administrators: array
    description: |
      team_id: Team ID
      team_name: Team name
      user_keys: Member list (user_key)
      administrators: Administrator list (user_key)

constraints:
  - Permission: Developer Platform – Permissions / Permission Management
```

### Usage notes

- **project_key**: Path parameter identifying the space.
- Response: list of teams with team_id, team_name, user_keys (members), administrators.
