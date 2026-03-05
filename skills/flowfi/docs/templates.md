# Templates

Pre-built workflow templates. List and get are **public** (no auth); **clone** requires JWT and creates a new **draft** workflow from a template.

**List templates:** **GET** `/templates`

Query: `page`, `limit`, `sortBy`, `sortOrder`, `search`, `category`, `featured` (boolean string), `minPrice`, `maxPrice`. Returns `{ data: TemplateDisplayInfo[], meta }` — display info only (no `nodes`/`connections`/`variables`). Each item: `id`, `name`, `description`, `category`, `uses`, `steps`, `setupTime`, `price`, `featured`, `nodeCount`, `connectionCount`.

**All templates (display only):** **GET** `/templates/display`  
Returns array of template display info (no nodes/connections/variables).

**Templates by category:** **GET** `/templates/categories`  
Returns `Record<category, TemplateDisplayInfo[]>` (templates grouped by category).

**Get one template (full):** **GET** `/templates/:id`  
Returns full template including `nodes`, `connections`, `variables` (for preview or clone). No auth.

**Clone template:** **POST** `/templates/:id/clone`  
Requires JWT. Creates a new workflow in **draft** from the template, attached to the given smart account.

**Request body (JSON):**

| Field           | Type   | Required | Description                          |
|----------------|--------|----------|--------------------------------------|
| `smartAccountId` | string | yes    | Smart account to attach the new workflow to |
| `name`         | string | no       | Workflow name (default: template name + " - Copy") |
| `network`      | string | no       | Network for settings (e.g. bsc, ethereum) |

**Response:** `200` — the created workflow (draft). Template `uses` count is incremented.

**Template knowledge:** Templates follow the same workflow structure as the workflow knowledge base (settings → trigger → nodes, valid definitionIds). Use `GET /templates` or `GET /templates/categories` to discover template IDs and categories; cloning gives users a starting point they can then edit via `POST /ai/workflow/:id/prompt` or `PATCH /workflows/:id` and deploy.
