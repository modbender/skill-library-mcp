# Workflow REST API

Instructions for FlowFi REST endpoints. Base URL is the backend API root (e.g. `https://api.seimoney.link`). Workflow and smart-account endpoints require **JWT** (see [Authorization](authorization.md)).

## How to generate a workflow with AI

1. **Get a smart account ID** — Call `GET /smart-accounts` (with JWT). Pick an account `id` to attach the workflow to.
2. **Generate from a natural-language prompt** — Call `POST /ai/generate-workflow` with JSON body:
   - `prompt` (required): user description, e.g. "When ETH price goes above 3500, send me a Telegram message"
   - `smartAccountId` (required): the smart account ID from step 1
3. **Response** — Returns the new workflow object with `id`, `name`, `nodes`, `connections`. The workflow is created in **draft** status.

**Example request:**

```json
POST /ai/generate-workflow
{
  "prompt": "When ETH price drops below 2000, send a Telegram notification",
  "smartAccountId": "0x..."
}
```

---

## What to do next (workflow lifecycle)

| Goal | Action |
|------|--------|
| **Run the workflow** | Deploy it: `POST /workflows/:id/deploy`. Workflow becomes **active** and runs on its triggers/schedule. |
| **Change the workflow** | If it's **active** or **paused**, call `POST /workflows/:id/undeploy` first. Then use `POST /ai/workflow/:id/prompt` (or `PATCH /workflows/:id`) to edit. |
| **Get AI edit ideas** | `GET /ai/workflow/:id/suggestions` returns short suggestions (e.g. "Add a delay", "Add a notification"). |
| **Apply an edit with AI** | `POST /ai/workflow/:id/prompt` with a prompt like "Add a 10 second delay after the price check". Workflow must be **draft** (undeploy first if deployed). |
| **Temporarily stop running** | `POST /workflows/:id/pause` (active → paused). Resume with `POST /workflows/:id/resume`. |
| **Stop and make editable again** | `POST /workflows/:id/undeploy` (active/paused/ended → draft). |
| **End the workflow** | `POST /workflows/:id/stop` (sets status to **ended**; no more runs). Can deploy again later. |
| **Remove the workflow permanently** | `DELETE /workflows/:id`. Safe for any status (backend stops scheduler if needed). |

---

## Capabilities (quick reference)

- **List smart accounts** — `GET /smart-accounts`; use an `id` as `smartAccountId` when generating workflows.
- **Generate workflow with AI** — `POST /ai/generate-workflow` with `prompt` and `smartAccountId`; creates a **draft**.
- **Get edit suggestions** — `GET /ai/workflow/:id/suggestions` for short AI edit ideas.
- **Edit by prompt** — `POST /ai/workflow/:id/prompt`; workflow must be **draft** (undeploy first if deployed).
- **Deploy** — `POST /workflows/:id/deploy` → draft/ended becomes **active** and runnable.
- **Undeploy** — `POST /workflows/:id/undeploy` → back to **draft** so you can edit.
- **Pause / Resume** — `POST /workflows/:id/pause`, `POST /workflows/:id/resume` (active ↔ paused).
- **Stop** — `POST /workflows/:id/stop` → **ended** (no more runs; can deploy again later).
- **Delete** — `DELETE /workflows/:id` removes the workflow permanently (any status).
- **List workflows** — `GET /workflows` with optional `?status=draft`, `?smartAccountId=...`, pagination.
- **Price** — `GET /price?symbol=BNB` (one token USD price, no auth); `GET /price/prices` (BNB + ETH, no auth).
- **Templates** — `GET /templates` (list, no auth), `GET /templates/display`, `GET /templates/categories`, `GET /templates/:id` (full); `POST /templates/:id/clone` (JWT) creates a draft workflow.

## Example prompts

**Generate workflow** (`POST /ai/generate-workflow` body `prompt`):

- "When ETH price goes above 3500, send me a Telegram message"
- "Every day at 9am, check Uniswap for WETH/USDC and post the price to Discord"
- "If gas is below 20 gwei, run a swap on Uniswap and notify me on Telegram"

**Edit workflow** (`POST /ai/workflow/:id/prompt` body `prompt`):

- "Add a 10 second delay after the price check"
- "Change the threshold to 4000"
- "Add an email notification when the workflow runs"

---

## Deploy workflow

**POST** `/workflows/:id/deploy`

Deploys a workflow so it can run (schedule/triggers). Workflow must be **draft** or **ended**; must have a smart account assigned.

**Path:** `id` = workflow ID.

**Response:** `200` — updated workflow (e.g. `status: 'active'`).

**Errors:** `400` if already deployed or missing smart account.

---

## Undeploy workflow

**POST** `/workflows/:id/undeploy`

Stops a deployed workflow and sets status back to **draft**. Required before editing a deployed workflow.

**Path:** `id` = workflow ID.

**Response:** `200` — updated workflow (`status: 'draft'`).

**Errors:** `400` if workflow is not deployed (e.g. already draft or archived).

---

## Delete workflow

**DELETE** `/workflows/:id`

Permanently removes a workflow. Safe for any status: if the workflow is **active**, **paused**, or **ended**, the backend stops the scheduler first, then deletes the workflow and its variables.

**Path:** `id` = workflow ID (owner must match authenticated user).

**Response:** `200` with no body on success.

---

## Pause workflow

**POST** `/workflows/:id/pause`

Temporarily stops a running workflow (active → paused). Triggers/schedule will not run until resumed.

**Path:** `id` = workflow ID.

**Response:** `200` — updated workflow (`status: 'paused'`).

**Errors:** `400` if workflow is not active.

---

## Resume workflow

**POST** `/workflows/:id/resume`

Resumes a paused workflow (paused → active).

**Path:** `id` = workflow ID.

**Response:** `200` — updated workflow (`status: 'active'`).

**Errors:** `400` if workflow is not paused.

---

## Stop workflow

**POST** `/workflows/:id/stop`

Stops the workflow and sets status to **ended**. No more runs; scheduler is stopped. You can deploy again later to reactivate.

**Path:** `id` = workflow ID.

**Response:** `200` — updated workflow (`status: 'ended'`).

**Errors:** `400` if workflow is draft or archived (not running).

---

## List workflows

**GET** `/workflows`

Returns workflows for the authenticated user. Supports query params: `status` (e.g. `draft`, `active`), `smartAccountId`, `page`, `limit`, `sortBy`, `sortOrder`, `search`.

---

## Draft workflows

- **Creating a draft:** `POST /ai/generate-workflow` and `POST /workflows` both create workflows with status **draft**.
- **Listing drafts:** `GET /workflows?status=draft` (optional query).
- **Editing:** Only draft (or ended) workflows can be edited. Use `POST /ai/workflow/:id/prompt` or `PATCH /workflows/:id` for draft workflows.
- **Deploy:** When ready, call `POST /workflows/:id/deploy` to move from draft to active.
