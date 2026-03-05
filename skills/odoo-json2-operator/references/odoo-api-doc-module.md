# Odoo API Doc Module Notes

## Scope
This note is extracted from `D:/odoo/odoo19e/addons/api_doc` and focuses on details needed for agent automation.

## Routes
- `GET /doc` (auth=user): API documentation UI, restricted by group `api_doc.group_allow_doc`.
- `GET /doc/index.json` (auth=user): model/method/field index.
- `GET /doc/<model>.json` (auth=user): full details for one model.
- `GET /doc-bearer/index.json` (auth=bearer): bearer-key equivalent of the index route.
- `GET /doc-bearer/<model>.json` (auth=bearer): bearer-key equivalent of model route.

## Execution Endpoint Used by Doc UI
The doc UI executes actual operations on:
- `POST /json/2/<model>/<method>`

Headers used in generated examples:
- `Authorization: Bearer <API_KEY>`
- `Content-Type: application/json`
- Optional `X-Odoo-Database: <db_name>` when the server hosts multiple databases.

## Request Body Pattern
The UI builds method payloads from method signature and defaults. Common conventions:
- Non-`@api.model` methods include `ids` and `context`.
- `@api.model` methods omit `ids`.
- CRUD examples in source include:
  - `search`: `{ "domain": [["display_name", "ilike", "a%"]] }`
  - `search_read`: domain + fields + limit
  - `read`: `{ "ids": [0, 1], "fields": ["display_name", "name"] }`
  - `create`: `{ "vals_list": [{...}] }`
  - `write`: `{ "ids": [0], "vals": {"display_name": "New Name"} }`
  - `unlink`: `{ "ids": [] }`

## Safety/Behavior Notes for Automation
- Validate target model and method through `/doc-bearer/index.json` and `/doc-bearer/<model>.json` before write operations.
- For mutating operations (`create`, `write`, `unlink`, custom write methods), run a dry-run equivalent first when possible (e.g. `search_read` + explicit confirmation).
- Keep payload minimal: only required keys and changed values.
- Treat non-2xx responses as failures and report both `message` and `debug` fields if present.
