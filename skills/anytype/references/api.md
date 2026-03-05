# Anytype API Reference

Base URL: `http://127.0.0.1:31012`
Version: `2025-11-08`
Auth: `Authorization: Bearer <ANYTYPE_API_KEY>`
Full OpenAPI spec: https://raw.githubusercontent.com/anyproto/anytype-api/main/docs/reference/openapi-2025-11-08.yaml

## Table of Contents
1. [Auth](#auth)
2. [Spaces](#spaces)
3. [Objects](#objects)
4. [Search](#search)
5. [Lists](#lists)
6. [Members](#members)
7. [Types](#types)
8. [Properties](#properties)
9. [Tags](#tags)
10. [Templates](#templates)

---

## Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/auth/challenge` | Create a challenge (for desktop-app code flow) |
| POST | `/v1/auth/api_key` | Exchange challenge + code for API key |

```json
// POST /v1/auth/challenge
{"app_name": "tippy-bot"}
// → {"challenge_id": "67647f5e..."}

// POST /v1/auth/api_key
{"challenge_id": "67647f5e...", "code": "1234"}
// → {"api_key": "zhSG/..."}
```

---

## Spaces

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces` | List all spaces the bot has access to |
| POST | `/v1/spaces` | Create a new space |
| GET | `/v1/spaces/{space_id}` | Get a space |
| PATCH | `/v1/spaces/{space_id}` | Update space name/description |
| DELETE | `/v1/spaces/{space_id}` | Delete a space |

```json
// POST /v1/spaces
{"name": "My Space", "description": "Optional description"}
```

---

## Objects

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces/{space_id}/objects` | List objects (`?limit=50&offset=0`) |
| POST | `/v1/spaces/{space_id}/objects` | Create an object |
| GET | `/v1/spaces/{space_id}/objects/{object_id}` | Get an object |
| PATCH | `/v1/spaces/{space_id}/objects/{object_id}` | Update an object |
| DELETE | `/v1/spaces/{space_id}/objects/{object_id}` | Delete an object |

```json
// POST /v1/spaces/{space_id}/objects
{
  "type_key": "page",          // required — use "page", "task", or custom type key
  "name": "My Page",
  "body": "Markdown body here",  // CREATE uses "body"
  "icon": {"format": "emoji", "emoji": "📄"},
  "properties": [
    {"key": "done", "checkbox": false}
  ]
}

// PATCH /v1/spaces/{space_id}/objects/{object_id}
// ⚠️ UPDATE uses "markdown" (not "body") for the content field!
{
  "name": "Updated name",
  "markdown": "Updated markdown body"  // UPDATE uses "markdown", not "body"
}
```

Object response includes: `id`, `name`, `type`, `body`, `properties[]`, `icon`, `created_date`, `last_modified_date`

---

## Search

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/search` | Global search across all spaces |
| POST | `/v1/spaces/{space_id}/search` | Search within a specific space |

```json
// POST /v1/search  or  POST /v1/spaces/{space_id}/search
{
  "query": "meeting notes",
  "limit": 20,
  "offset": 0,
  "types": ["page"],           // optional: filter by type keys
  "filter": {                  // optional: property filters
    "operator": "and",
    "conditions": [
      {"property_key": "done", "condition": "eq", "checkbox": false}
    ]
  },
  "sort": {
    "property_key": "last_modified_date",
    "direction": "desc"
  }
}
```

Filter conditions: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `ncontains`, `in`, `nin`, `all`, `empty`, `nempty`

---

## Lists

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/spaces/{space_id}/lists/{list_id}/objects` | Add objects to a list |
| GET | `/v1/spaces/{space_id}/lists/{list_id}/objects` | Get objects in a list |
| PATCH | `/v1/spaces/{space_id}/lists/{list_id}/objects` | Reorder objects in a list |
| DELETE | `/v1/spaces/{space_id}/lists/{list_id}/objects` | Remove objects from a list |

---

## Members

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces/{space_id}/members` | List space members |
| PATCH | `/v1/spaces/{space_id}/members/{member_id}` | Update member role |

---

## Types

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces/{space_id}/types` | List types in a space |
| POST | `/v1/spaces/{space_id}/types` | Create a custom type |
| GET | `/v1/spaces/{space_id}/types/{type_key}` | Get a type (includes linked properties) |
| PATCH | `/v1/spaces/{space_id}/types/{type_key}` | Update a type |
| DELETE | `/v1/spaces/{space_id}/types/{type_key}` | Delete a type |

Built-in type keys: `page`, `task`, `note`, `bookmark`, `set`, `collection`

---

## Properties

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces/{space_id}/properties` | List properties |
| POST | `/v1/spaces/{space_id}/properties` | Create a property |
| GET | `/v1/spaces/{space_id}/properties/{property_key}` | Get a property |
| PATCH | `/v1/spaces/{space_id}/properties/{property_key}` | Update a property |
| DELETE | `/v1/spaces/{space_id}/properties/{property_key}` | Delete a property |

Property formats: `text`, `number`, `select`, `multi_select`, `date`, `checkbox`, `url`, `email`, `phone`, `files`, `objects`

---

## Tags

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces/{space_id}/types/{type_key}/tags` | List tags for a select/multi_select property |
| POST | `/v1/spaces/{space_id}/types/{type_key}/tags` | Create a tag |
| GET | `/v1/spaces/{space_id}/types/{type_key}/tags/{tag_id}` | Get a tag |
| PATCH | `/v1/spaces/{space_id}/types/{type_key}/tags/{tag_id}` | Update a tag |
| DELETE | `/v1/spaces/{space_id}/types/{type_key}/tags/{tag_id}` | Delete a tag |

Tag colors: `grey`, `yellow`, `orange`, `red`, `pink`, `purple`, `blue`, `ice`, `teal`, `lime`

---

## Templates

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/spaces/{space_id}/types/{type_key}/templates` | List templates |
| GET | `/v1/spaces/{space_id}/types/{type_key}/templates/{template_id}` | Get a template |
