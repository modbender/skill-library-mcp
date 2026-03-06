# SiYuan Note API Reference

Complete API reference for the SiYuan Note HTTP API used by this skill.

## General

- All endpoints use **POST** method with JSON body
- Header: `Content-Type: application/json`
- Header: `Authorization: Token <api_token>`
- Response format: `{"code": 0, "msg": "", "data": {}}`
- `code = 0` means success; non-zero means error

## Notebooks

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/notebook/lsNotebooks` | None | `data.notebooks[]` with `id`, `name`, `closed` |
| `/api/notebook/createNotebook` | `{"name": "..."}` | `data.notebook` object |
| `/api/notebook/renameNotebook` | `{"notebook": "<id>", "name": "..."}` | null |
| `/api/notebook/removeNotebook` | `{"notebook": "<id>"}` | null |

## Documents

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/filetree/createDocWithMd` | `{"notebook": "<id>", "path": "/foo/bar", "markdown": "..."}` | `data` = doc ID |
| `/api/filetree/renameDocByID` | `{"id": "<doc_id>", "title": "..."}` | null |
| `/api/filetree/removeDocByID` | `{"id": "<doc_id>"}` | null |
| `/api/filetree/getHPathByID` | `{"id": "<block_id>"}` | `data` = human-readable path |
| `/api/filetree/getPathByID` | `{"id": "<block_id>"}` | `data.notebook`, `data.path` |
| `/api/filetree/getIDsByHPath` | `{"path": "/foo/bar", "notebook": "<id>"}` | `data[]` = doc IDs |

Notes:
- `path` in `createDocWithMd` starts with `/`, levels separated by `/` (corresponds to hpath)
- Repeated calls with same path will NOT overwrite existing documents

## Blocks

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/block/appendBlock` | `{"dataType": "markdown", "data": "...", "parentID": "<id>"}` | `data[0].doOperations[0].id` = new block ID |
| `/api/block/prependBlock` | `{"dataType": "markdown", "data": "...", "parentID": "<id>"}` | same as above |
| `/api/block/insertBlock` | `{"dataType": "markdown", "data": "...", "previousID": "<id>", "parentID": "<id>"}` | same as above |
| `/api/block/updateBlock` | `{"dataType": "markdown", "data": "...", "id": "<id>"}` | updated block DOM |
| `/api/block/deleteBlock` | `{"id": "<id>"}` | null |
| `/api/block/moveBlock` | `{"id": "<id>", "previousID": "<id>", "parentID": "<id>"}` | null |
| `/api/block/getBlockKramdown` | `{"id": "<id>"}` | `data.kramdown` |
| `/api/block/getChildBlocks` | `{"id": "<id>"}` | `data[]` with `id`, `type`, `subType` |

Notes:
- `dataType` can be `markdown` or `dom`
- For `insertBlock`: `previousID` > `parentID` priority; at least one required

## Attributes

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/attr/setBlockAttrs` | `{"id": "<id>", "attrs": {"custom-key": "value"}}` | null |
| `/api/attr/getBlockAttrs` | `{"id": "<id>"}` | `data` = all attributes as key-value map |

Notes:
- Custom attributes **must** be prefixed with `custom-`

## SQL

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/query/sql` | `{"stmt": "SELECT ..."}` | `data[]` = result rows |

Common tables: `blocks`, `attributes`, `spans`, `refs`

Useful queries:
- Find doc by name: `SELECT id FROM blocks WHERE type = 'd' AND content = '任务清单'`
- Find sub-docs: `SELECT * FROM blocks WHERE type = 'd' AND hpath LIKE '/任务清单/%'`
- Search content: `SELECT * FROM blocks WHERE content LIKE '%keyword%' LIMIT 20`
- Filter by attribute: `SELECT * FROM attributes WHERE name = 'custom-status' AND value = '进行中'`

## Export

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/export/exportMdContent` | `{"id": "<doc_id>"}` | `data.hPath`, `data.content` (Markdown) |

## Asset

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/asset/upload` | `multipart/form-data` with `assetsDirPath` and `file[]` | `data.succMap` = `{filename: asset_path}` |

Notes:
- Uses `multipart/form-data` content type (not JSON)
- `assetsDirPath` is typically `/assets/`
- Returned `asset_path` (e.g. `assets/screenshot-20260210-abc.png`) can be used in markdown: `![alt](asset_path)`

## Notification

| Endpoint | Params | Returns |
|----------|--------|---------|
| `/api/notification/pushMsg` | `{"msg": "...", "timeout": 7000}` | `data.id` |
| `/api/notification/pushErrMsg` | `{"msg": "...", "timeout": 7000}` | `data.id` |
