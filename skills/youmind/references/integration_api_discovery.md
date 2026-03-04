# Youmind API Integration Notes (Verified by Real Product Runs)

Last verified: 2026-02-25

This document records API-related findings from real in-product operations (not only static docs):
- created new boards
- uploaded files into a board
- added a URL into a board via chat action
- started chat flows for image and slides generation

## Scope

Target capabilities for the skill rewrite:
1. list all boards
2. find/search a board
3. create a board
4. add link/file into a board
5. start conversations (including image/slides generation workflows)

## Verified Flows and Endpoints

### 1) List all boards

Observed endpoint:
- `POST /api/v1/listBoards`

Related endpoints typically loaded together:
- `POST /api/v1/favorite/listFavorites`
- `POST /api/v1/board/getBoardDetail`

Integration note:
- `listBoards` should be the primary source for board library sync.

### 2) Find/search a board

No explicit `searchBoards` endpoint was directly observed in this run.

Practical approach:
- pull board list via `POST /api/v1/listBoards`
- perform client-side fuzzy search/filter by name/id/metadata

Related endpoint:
- `POST /api/v1/board/getBoardDetail`

### 3) Create board

Observed during `/boards/new` submission:
- `POST /api/v1/createBoard`
- `POST /api/v2/chatAssistant/createChat`

Validated payload for `createBoard`:
```json
{
  "name": "新建项目",
  "description": "",
  "icon": {"name": "Game", "color": "--function-red"},
  "prompt": "..."
}
```

Validation note:
- If no `prompt`, `name` + `icon.name` + `icon.color` are required.

Observed result:
- URL redirected to `/boards/{boardId}`
- board title generated from prompt context

Integration note:
- For "create board and start first task", combine `createBoard` + `chatAssistant/createChat` workflow.

### 4) Add link/file into a board

#### 4.1 Upload file (verified)

Observed endpoints:
- `POST /api/v1/genSignedPutUrlIfNotExist`
- `POST /api/v1/createFileRecordFromCdnUrl`
- `POST /api/v1/createTextFile`
- `POST /api/v1/snip/getSnip`

Observed behavior:
- file appeared in board materials with upload success state.

Integration note:
- file upload is a multi-step flow (sign URL -> upload/CDN record -> create material record).

Validated request shapes:

1) `genSignedPutUrlIfNotExist`
```json
{"hash":"<sha256>"}
```

2) upload bytes to returned signed URL via `PUT`

3) `createFileRecordFromCdnUrl`
```json
{"cdnUrl":"https://youmind-user-files-private...","name":"file.ext"}
```

4) attach to board with `createTextFile`
```json
{
  "file":{"name":"file.ext","hash":"<sha256>"},
  "board_id":"<board-id>"
}
```

#### 4.2 Add URL/link (direct API confirmed)

Direct endpoint (confirmed):
- `POST /api/v1/tryCreateSnipByUrl`

Observed payload shape:
```json
{
  "url": "https://example.com/...",
  "board_id": "019c9362-511c-7741-a93e-9955745ea222"
}
```

Important headers seen in real call:
- `x-client-type: web`
- `x-time-zone: Asia/Shanghai` (or local timezone)

Recommended integration:
- use `tryCreateSnipByUrl` as primary URL ingestion API
- then poll/fetch snip detail/list to confirm material readiness

Related material listing API:
- `POST /api/v1/snip/getSnips`

Observed payload example:
```json
{
  "ids": ["019c9375-eff0-7751-9a4b-b99be742ff66"]
}
```

Note:
- `getSnips` is id-based fetch (by snip ids), useful for detail retrieval/verification after creation.

Fallback operation previously verified:
- sent chat instruction to save `https://example.com` into current board
- UI response contained: `资料已保存` and `ADD_OK`

Observed endpoint during this operation:
- `POST /api/v2/chatAssistant/sendMessage`
- `POST /api/v1/snip/getSnips`

Important:
- dedicated add-link endpoint is now known: `tryCreateSnipByUrl`.
- chat-driven save can remain as emergency fallback during migration.

Recommended strategy:
- use `tryCreateSnipByUrl` directly for link ingestion
- use `snip/getSnips` for post-create verification and metadata fetch

### 5) Start chat and generate image/slides

#### 5.1 Normal/command chat

Observed endpoints:
- `POST /api/v2/chatAssistant/createChat`
- `POST /api/v2/chatAssistant/sendMessage`
- `POST /api/v2/chatAssistant/listChatHistory`
- `POST /api/v2/chatAssistant/getChatDetail`
- `POST /api/v2/chatAssistant/getChatDetailByOrigin`
- `POST /api/v2/chatAssistant/markChatAsRead`

Validated payloads:

`createChat`
```json
{
  "origin":{"type":"board","id":"<board-id>"},
  "board_id":"<board-id>",
  "message":"...",
  "message_mode":"agent",
  "max_mode":false
}
```

`sendMessage`
```json
{
  "chat_id":"<chat-id>",
  "message":"...",
  "board_id":"<board-id>",
  "message_mode":"agent",
  "origin":{"type":"board","id":"<board-id>"},
  "max_mode":false
}
```

#### 5.2 Image generation flow (verified)

Action:
- clicked `创建图片` and sent prompt

Observed behavior:
- board responded with `创建图片中` -> `图片已创建`

Observed endpoints in this run:
- `POST /api/v1/createBoard`
- `POST /api/v2/chatAssistant/createChat`
- `POST /api/v2/chatAssistant/getChatDetail`
- plus standard board/chat list endpoints

#### 5.3 Slides generation flow (verified)

Action:
- clicked `创建 Slides` and sent prompt

Observed behavior:
- board responded with `创建 Slides 中(6 张 Slides)` and generated slide outline/pages

Observed endpoints in this run:
- `POST /api/v1/createBoard`
- `POST /api/v2/chatAssistant/createChat`
- plus standard board/chat list endpoints

Note:
- no dedicated slide/image generation endpoint was isolated from fetch/xhr in this pass; generation may be abstracted behind chat service internals.

## API Surface Proposal for Skill v2

Define a stable internal client interface independent from current UI scripts. Runtime calls are API-only.

- `boards.list()` -> uses `POST /api/v1/listBoards`
- `boards.get(boardId)` -> uses `POST /api/v1/board/getBoardDetail`
- `boards.create(payload)` -> uses `POST /api/v1/createBoard`
- `materials.uploadFile(boardId, file)` -> signed upload flow endpoints
- `materials.addLink(boardId, url)` -> `POST /api/v1/tryCreateSnipByUrl`
- `materials.getByIds(ids[])` -> `POST /api/v1/snip/getSnips`
- `chat.create(boardId, firstMessage?)` -> `POST /api/v2/chatAssistant/createChat`
- `chat.send(chatId/origin, message)` -> `POST /api/v2/chatAssistant/sendMessage`
- `chat.history(boardId/origin)` -> `POST /api/v2/chatAssistant/listChatHistory`

## Priority and Migration Plan

P0:
- board list/get/create
- chat create/send/history
- file upload via API

P1:
- expand material read APIs around snips/picks for richer list/filter operations
- image/slides "typed task" wrappers around chat flow

P2:
- favorites/skills/connectors/subscription/credit exposure as optional admin APIs

## Stability Notes

These appear to be web private APIs (not a publicly versioned SDK contract). Keep safeguards:
- centralize endpoint constants
- strict error classification and retries
- use browser only for token bootstrap/refresh, not for business actions
- add contract tests that run against a real authenticated session
