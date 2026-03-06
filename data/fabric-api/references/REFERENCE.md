# Fabric API skill reference

This file is extra detail for the `fabric-api` skill. Read it when you need the exact schema expectations or you’re debugging validation errors.

## Endpoint map (from `fabric-api.yaml`)

Creation:

- Notepads (“notes”): `POST /v2/notepads`
- Folders: `POST /v2/folders`
- Bookmarks: `POST /v2/bookmarks`
- Files: `POST /v2/files` (requires `/v2/upload` first)
- Tags: `POST /v2/tags`

Read / browse:

- Who am I: `GET /v2/user/me`
- Resource roots: `GET /v2/resource-roots`
- Get resource by ID: `GET /v2/resources/{resourceId}`
- List resources: `POST /v2/resources/filter`
- Search: `POST /v2/search`
- List tags: `GET /v2/tags`

Dangerous / destructive:

- Delete: `POST /v2/resource/delete`
- Recover: `POST /v2/resource/recover`

## “Notes” vs “notepads”

The Fabric HTTP API models a note-like item as a **resource of kind `notepad`** and exposes a dedicated create endpoint:

- Create: `POST /v2/notepads`

If you previously tried `POST /v2/notes` and got a 404, that matches the OpenAPI spec: there is no `/v2/notes` path defined.

## `parentId`: valid values and when aliases work

For create endpoints (`/v2/notepads`, `/v2/folders`, `/v2/bookmarks`, `/v2/files`), `parentId` is:

- a UUID (folder resource id), **or**
- one of the RootAlias enum values:
  - `@alias::inbox`
  - `@alias::bin`

This alias resolution happens “during request handling” (server-side). It’s a convenience for creates.

For *filtering/listing* (`POST /v2/resources/filter`), `parentId` is defined as a UUID pattern and **does not accept aliases**. Use a UUID there.

### How to resolve Inbox/Bin IDs

Call:

- `GET /v2/resource-roots`

Find the root with `type: SYSTEM` and `subtype: inbox` or `subtype: bin`, then use `folder.id` as the UUID.

## Tags: exact schema (and the common failure modes)

Many create endpoints share the same `tags` schema:

```json
"tags": [
  { "name": "ideas" },
  { "id": "550e8400-e29b-41d4-a716-446655440000" }
]
```

Key rules:

- `tags` is an array.
- Each item must be an object.
- Each object must be either:
  - `{ "name": "<string up to 255>" }` (create or reuse tag by name), or
  - `{ "id": "<uuid>" }` (attach an existing tag by id)
- Don’t send:
  - `["tag1","tag2"]` (strings are invalid)
  - `[["tag1"],["tag2"]]` (nested arrays are invalid)
  - `{ "tags": { ... } }` (wrong shape)
  - `{ "name": ["ideas"] }` (wrong type)

If you’re unsure, omit `tags` for the initial create request. Then:

1) List tags (`GET /v2/tags?name=...`) or create tag (`POST /v2/tags`)  
2) Use tag IDs or names in a follow-up create/attach flow (Fabric currently supports tags on create; attaching after create may require an endpoint not in this spec).

## Notepad creation schema in plain English

`POST /v2/notepads` body is roughly:

- Required:
  - `parentId`
  - and either:
    - `text` (markdown string) **OR**
    - `ydoc` (structured)
- Optional:
  - `name` (nullable, 1-255 chars)
  - `tags` (array, shape above)
  - `comment` (object with `content`)

Minimal valid example:

```json
{
  "parentId": "@alias::inbox",
  "text": "Hello"
}
```

Recommended example:

```json
{
  "name": "My note title",
  "parentId": "@alias::inbox",
  "text": "# Heading\n\nSome text\n"
}
```

### `name` vs `title`

The schema uses `name`. If you have a “title” value (from a UI or user phrasing), map it to `name` in the payload.

## File upload (3-step flow)

Creating a file is a two-endpoint flow:

1) `GET /v2/upload?filename=...&size=...` → returns presigned `url` and required `headers`
2) `PUT` the file bytes to the presigned URL (no API key)
3) `POST /v2/files` with:
   - `attachment.path`: the path part of the presigned URL (strip host + query string)
   - `attachment.filename`: original filename
   - `parentId`: uuid or alias
   - `mimeType`

See the examples in `SKILL.md` and consult `fabric-api.yaml` for the exact `FileCreation` schema.

## Keep the OpenAPI close

When debugging, open `{baseDir}/fabric-api.yaml` and search for the exact endpoint:

- `paths: /v2/notepads`
- `paths: /v2/resources/filter`
- `components: schemas: RootAlias`, `FileCreation`, etc.

That spec is the source of truth for field names and required properties.
