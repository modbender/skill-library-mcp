---
name: meegle-api-users
description: Meegle user-related OpenAPIs (user groups, members). Credentials from meegle-api-credentials.
metadata: { openclaw: {} }
---

# Meegle API — Users

User-related OpenAPIs. Domain, token, context, headers from **meegle-api-credentials**.

---

## Get User Group Members

Query the members of user groups in a specified space. Supports space administrator, space member, and custom user groups.

### Points to Note

**This API only supports user access credentials (user_access_token).** Plugin access token is not supported. See **meegle-api-credentials** for how to get user_access_token.

### When to Use

- When listing members of space admin, space member, or custom user groups
- When resolving user_group_ids to user_keys in a space
- When building permission or membership checks

### API Spec: get_user_group_members

```yaml
name: get_user_group_members
type: api
description: Query user group members. user_access_token only (no plugin token).
auth: { type: user_access_token }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/user_groups/members/page" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{user_access_token}}" }
path_params: { project_key: { type: string, required: true } }
inputs: { user_group_type: { type: string, required: true, enum: [PROJECT_ADMIN, PROJECT_MEMBER, CUSTOMIZE] }, user_group_ids: { type: array, max_items: 50 }, page_num: { type: integer, default: 1 }, page_size: { type: integer, default: 50, max: 100 } }
outputs: { data: { list: array, pagination: object } }
constraints: [Permission: Users, page_size max 100]
error_mapping: { 20002: Page size limit, 1000053008: Type not supported, 1000053010: User group not found, 1000053011: Max 50 groups }
```

### Usage notes

- **user_access_token only**: Use `X-Plugin-Token: {{user_access_token}}`; plugin token will not work.
- **user_group_type**: PROJECT_ADMIN / PROJECT_MEMBER / CUSTOMIZE.
- **user_group_ids**: For CUSTOMIZE, optional; omit to get all custom user groups’ members. From URL `.../userGroup/{id}`.
- **page_size**: Max 100; default 50.

---

## Get Tenant User List

Perform a fuzzy search for users within the tenant and return their detailed information. Searches by user name or other keywords; e.g. query "user1" returns users like "user1" and "user1.1".

### When to Use

- When searching for users in the tenant by name or keyword
- When resolving user_key from partial names
- When building user pickers or member selection UIs

### API Spec: get_tenant_user_list

```yaml
name: get_tenant_user_list
type: api
description: Fuzzy search users in tenant by name; returns user details.
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: POST, url: "https://{domain}/open_api/user/search" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
inputs: { query: { type: string, required: false }, project_key: { type: string, required: false } }
outputs: { data: array }
constraints: [Permission: Users; project_key required for marketplace or when user tenant != plugin tenant]
error_mapping: { 30006: User not found, 1000052063: Project not exist }
```

### Usage notes

- **query**: Fuzzy search by user name; omit to list users in the tenant.
- **project_key**: Required for marketplace plugins; for enterprise plugins, required when the user's primary tenant differs from the plugin tenant.

---

## Get User Details

Obtain detailed information of one or more specified users by user_key, out_id (UnionId), or email.

### Points to Note

When using a **virtual token**, only collaborators of the plugin can be retrieved. To query other users, use the official (non-virtual) token.

When using **plugin_access_token** for this interface, **X-User-Key is not required**.

### When to Use

- When resolving user_key / out_id / email to full user profile
- When fetching avatar, name, email, status for display
- When batching user lookups (up to 100 per request)

### API Spec: get_user_details

```yaml
name: get_user_details
type: api
description: User details by user_keys, out_ids, or emails; X-User-Key not required.
auth: { type: plugin_access_token, header: X-Plugin-Token }
http: { method: POST, url: "https://{domain}/open_api/user/query" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{resolved_token}}" }
inputs: { user_keys: { type: array, max_items: 100 }, out_ids: { type: array, max_items: 100 }, emails: { type: array, max_items: 100 }, tenant_key: { type: string, required: false } }
outputs: { data: array }
constraints: [Permission: Users, at least one of user_keys/out_ids/emails, max 100 total]
error_mapping: { 30006: User not found, 20004: Exceeds 100 records }
```

### Usage notes

- **user_keys / out_ids / emails**: At least one must be provided; max 100 identifiers in total per request.
- **tenant_key**: When querying by email for users in a tenant other than the plugin's, pass that tenant's saas_tenant_key.
- **X-User-Key**: Not required when using plugin_access_token for this API.

---

## Get Team Member in Space

Return a list of teams whose visibility scope is searchable within the specified space and whose visible project space is the requested space. Each team includes members (user_keys) and administrators.

### When to Use

- When listing teams visible within a space
- When fetching team members and administrators
- When building team pickers or membership UIs

### API Spec: get_team_member_in_space

```yaml
name: get_team_member_in_space
type: api
description: Teams visible in space (user_keys, administrators per team).
auth: { type: plugin_access_token, header: X-Plugin-Token, user_header: X-User-Key }
http: { method: GET, url: "https://{domain}/open_api/{project_key}/teams/all" }
headers: { X-Plugin-Token: "{{resolved_token}}", X-User-Key: "{{user_key}}" }
path_params: { project_key: { type: string, required: true } }
inputs: { offset: { type: integer, required: false }, limit: { type: integer, default: 300, max: 300 } }
outputs: { data: array, has_more: boolean }
constraints: [Permission: Users, limit max 300]
error_mapping: { 30006: User not found }
```

### Usage notes

- **project_key**: Path parameter identifying the space.
- **offset / limit**: Pagination; offset 0-based; limit max 300, default 300.

---

## Create Customized User Group

Create a custom user group in a specified space. Only user members (user_key) are supported; department members cannot be added.

### Points to Note

**This API only supports user access credentials (user_access_token).** See Get Access Credentials for how to obtain user_access_token.

### When to Use

- When creating a new custom user group in a space
- When defining a group of users by user_key list
- When setting up permission or notification groups

### API Spec: create_customized_user_group

```yaml
name: create_customized_user_group
type: api
description: Create custom user group; user_access_token only; users = user_key list, max 100.
auth: { type: user_access_token }
http: { method: POST, url: "https://{domain}/open_api/{project_key}/user_group" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{user_access_token}}" }
path_params: { project_key: { type: string, required: true } }
inputs: { name: { type: string, required: true, max_length: 250 }, users: { type: array, required: true, max_items: 100 } }
outputs: { data: { id: string } }
constraints: [Permission: Users, name unique no / max 250, users max 100]
error_mapping: { 1000053001: Name exists, 1000053002: Unsupported char, 1000053003: Name length, 1000053004: User invalid, 1000053005: Users limit 100, 1000053006: Need user, 1000053007: Need name }
```

### Usage notes

- **user_access_token only**: Use `X-Plugin-Token: {{user_access_token}}`; plugin token will not work.
- **name**: Must be unique; no "/" or other unsupported characters; max 250 characters.
- **users**: List of user_key; max 100; cannot add users who have left or do not exist.

---

## Update User Group Member

Update the members of a user group. Supports add, delete, or replace members. Works with space members (PROJECT_MEMBER) or custom user groups (CUSTOMIZE).

### Points to Note

**This API only supports user access credentials (user_access_token).** See **meegle-api-credentials** for how to obtain user_access_token.

- When adding a user from non-space members, the user is automatically added to space members.
- When deleting a user from space members, the user is automatically removed from other user groups.

### When to Use

- When adding or removing members from a custom user group
- When replacing the full member list of a user group
- When updating space members (PROJECT_MEMBER) or custom groups (CUSTOMIZE)

### API Spec: update_user_group_member

```yaml
name: update_user_group_member
type: api
description: Update user group members (add/delete/replace); user_access_token only; replace_users overrides add/delete.
auth: { type: user_access_token }
http: { method: PATCH, url: "https://{domain}/open_api/{project_key}/user_group/members" }
headers: { Content-Type: application/json, X-Plugin-Token: "{{user_access_token}}" }
path_params: { project_key: { type: string, required: true } }
inputs: { user_group_type: { type: string, required: true, enum: [PROJECT_MEMBER, CUSTOMIZE] }, user_group_id: string, add_users: { type: array, max_items: 100 }, delete_users: { type: array, max_items: 100 }, replace_users: { type: array, max_items: 100 } }
outputs: { data: object }
constraints: [Permission: Users, one of add/delete/replace non-empty, user_group_id when CUSTOMIZE, max 100 per field]
error_mapping: { 1000053004: User invalid, 1000053005: Users limit 100, 1000053008: Type not supported, 1000053009: Need user group ID, 1000053006: Need user, 1000053010: User group not found }
```

### Usage notes

- **user_access_token only**: Use `X-Plugin-Token: {{user_access_token}}`; plugin token will not work.
- **user_group_id**: Required when `user_group_type=CUSTOMIZE`; from user group page URL.
- **replace_users** takes precedence: when non-empty, `add_users` and `delete_users` are ignored.
- If the same `user_key` appears in both `add_users` and `delete_users`, it is ignored.
