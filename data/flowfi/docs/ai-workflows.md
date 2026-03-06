# AI workflows

## Generate workflow

**POST** `/ai/generate-workflow`

Creates a new workflow from a natural-language prompt using AI. The workflow is created in the database with status **draft**.

**Request body (JSON):**

| Field           | Type   | Required | Description                          |
|----------------|--------|----------|--------------------------------------|
| `prompt`       | string | yes      | User description of the workflow     |
| `smartAccountId` | string | yes    | Smart account ID to attach           |

**Example:**

```json
{
  "prompt": "When ETH price drops below 2000, send a Telegram notification",
  "smartAccountId": "0x..."
}
```

**Response:** `200` — workflow object with `id`, `name`, `nodes`, `connections`.

---

## Get workflow suggestions

**GET** `/ai/workflow/:id/suggestions`

Returns AI-generated edit suggestions for a workflow (e.g. four short actionable edit ideas). Used by "Edit workflow with AI" UI.

**Path:** `id` = workflow ID (owner must match authenticated user).

**Response:** `200` — `{ "suggestions": string[] }` (e.g. 4 suggestion strings).

---

## Edit workflow by prompt

**POST** `/ai/workflow/:id/prompt`

Edits an existing workflow using a natural-language prompt. Updates name, nodes, connections, and variables. Workflow must be **draft** (undeploy first if deployed).

**Path:** `id` = workflow ID.

**Request body (JSON):**

| Field   | Type   | Required | Description                    |
|--------|--------|----------|--------------------------------|
| `prompt` | string | yes     | Edit instruction (e.g. "Add a 5s delay") |

**Response:** `200` — `{ "message": string, "workflow": Workflow }`.
