# Youmind API Integration Plan (Live Product Validation)

Last validated: 2026-02-25

## Scope

This document records endpoints and behavior verified by running real actions in Youmind (not only static code reading), to support replacing browser-selector automation with API-first integration.

## Real Flows Executed

1. Created a new board from `https://youmind.com/boards/new`
2. Uploaded a local file into board materials
3. Added a URL to board materials via chat action command
4. Started chat to generate an image
5. Started chat to generate Slides

Boards created during validation:
- `ym-api-test-140013` (`/boards/019c9362-511c-7741-a93e-9955745ea222`)
- `AI产品策略` (`/boards/019c9368-65d5-7063-a942-38c8d1f0e7e5`)
- `AI Coding Roadmap` (`/boards/019c936a-9d01-719e-8394-412bc375eac4`)

## API Endpoints Observed

### Board discovery and lookup

- `POST /api/v1/listBoards`
- `POST /api/v1/board/getBoardDetail`
- `POST /api/v1/favorite/listFavorites`

### Board creation

- `POST /api/v1/createBoard`

Observed when sending first prompt from `/boards/new`, followed by redirect to `/boards/{boardId}`.

### Chat lifecycle

- `POST /api/v2/chatAssistant/createChat`
- `POST /api/v2/chatAssistant/sendMessage`
- `POST /api/v2/chatAssistant/listChatHistory`
- `POST /api/v2/chatAssistant/getChatDetail`
- `POST /api/v2/chatAssistant/getChatDetailByOrigin`
- `POST /api/v2/chatAssistant/markChatAsRead`

Notes:
- Initial prompt on newly created board can be submitted via `createChat` flow.
- Follow-up message on existing board triggers `sendMessage`.

### Material ingestion (file path confirmed)

- `POST /api/v1/genSignedPutUrlIfNotExist`
- `POST /api/v1/createFileRecordFromCdnUrl`
- `POST /api/v1/createTextFile`
- `POST /api/v1/snip/getSnip`
- `POST /api/v1/pick/listPicks`

Observed after actual file upload (`input[type=file]`) in Materials tab.

### Material ingestion (URL path, via chat command)

URL add command succeeded with response including:
- `资料已保存`
- `1 个资料已添加`
- `ADD_OK`

API during this operation included:
- `POST /api/v2/chatAssistant/sendMessage`
- `POST /api/v1/snip/getSnips`

Inference: link insertion can be achieved through chat tool execution even when dedicated link endpoint is not directly exposed in this capture.

### Image / Slides generation entry points

Generated from `/boards/new` quick actions:
- `创建图片`
- `创建 Slides`

Observed APIs (common orchestration path):
- `POST /api/v1/createBoard`
- `POST /api/v2/chatAssistant/createChat`
- `POST /api/v1/listCraftTemplates`
- `POST /api/v1/pick/listPicks`
- `POST /api/v2/chatAssistant/listChatHistory`

Product evidence:
- Image flow reached `图片已创建`
- Slides flow reached `创建 Slides 中 (6 张 Slides)` and rendered slide titles

## Required Capabilities -> Integration Mapping

User-required capability mapping:

1. List all boards
- Use `POST /api/v1/listBoards`

2. Find a board
- Primary: filter from `listBoards`
- Optional detail fetch: `POST /api/v1/board/getBoardDetail`

3. Create board
- Use `POST /api/v1/createBoard`

4. Add link/file to board
- File: signed upload + record creation
  - `genSignedPutUrlIfNotExist` -> upload to signed URL -> `createFileRecordFromCdnUrl`
- Link:
  - Short-term stable path: `chatAssistant/sendMessage` with strict add-link command
  - Follow-up: keep searching for dedicated link-create endpoint in JS/network traces

5. Start chat and generate image/Slides
- Chat session: `createChat` + `sendMessage`
- Read progress/result: `listChatHistory` + `getChatDetail`/`getChatDetailByOrigin`
- Mode hints (image/slides) likely flow through template/craft selection:
  - `listCraftTemplates`

## Implementation Guidance for Skill v2

1. Build `YoumindApiClient` (requests + auth session), keep UI automation as fallback only.
2. Implement these commands first:
   - `boards list`
   - `boards find`
   - `boards create`
   - `materials upload-file`
   - `materials add-link` (chat-backed fallback)
   - `chat send`
   - `chat wait` (poll history/detail until terminal state)
3. Add structured operation logs:
   - endpoint, request id, board id, chat id, elapsed time, failure reason
4. Add compatibility guard:
   - if API fails with 401/403/404/schema change, fallback to existing browser path.

## Risks / Unknowns

- These are web-app internal APIs (not guaranteed stable public API contracts).
- We captured endpoint names but not full request/response schema yet.
- Link ingestion direct endpoint was not isolated in this run; chat-driven add-link works and can be used as interim production path.

