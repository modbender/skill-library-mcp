---
name: holded-skill
description: Operate Holded ERP through holdedcli to read and update data safely. Use when the user asks to read, search, create, update, or delete Holded entities (contacts, invoices, products, CRM, projects, team, accounting) or run Holded API endpoints from the terminal.
metadata: {"openclaw":{"homepage":"https://github.com/jaumecornado/holded-skill","requires":{"bins":["holded"]},"primaryEnv":"HOLDED_API_KEY","install":[{"id":"brew","kind":"brew","formula":"jaumecornado/tap/holded","bins":["holded"],"label":"Install holdedcli (brew)"}]}}
---

# holded-skill

Use `holdedcli` to read and modify Holded data with a safe, repeatable workflow.

## Operational Flow

1. Confirm technical prerequisites.
2. Discover available actions with `holded actions list`.
3. Inspect the selected action with `holded actions describe <action> --json`.
4. Classify the action as read or write.
5. If it is a write operation, ask for explicit confirmation before execution.
6. Run with `--json` and summarize IDs, HTTP status, and applied changes.

## Prerequisites

- Verify that the binary exists: `holded help`
- Verify credentials: `holded auth status` or `HOLDED_API_KEY`
- Prefer structured output whenever possible: `--json`

## Safety Rules

- **ALWAYS check deductibility rules BEFORE creating any document.** See "Accounting Rules for Spain" section below.
- Treat any `POST`, `PUT`, `PATCH`, or `DELETE` action as **write**.
- Treat any `GET` action (or `HEAD` when present) as **read**.
- Before any operation, always run `holded actions describe <action> --json` (after `holded actions list`) to validate accepted parameters.
- For purchase receipts, always enforce `docType=purchase` and include `"isReceipt": true` in the JSON body. Since holdedcli validates against Holded's schema (which doesn't include `isReceipt`), you **must** use `--skip-validation` flag.
- Ask for explicit user confirmation **every time** before any write action.
- Do not execute writes on ambiguous replies (`ok`, `go ahead`, `continue`) without clarification.
- Repeat the exact command before confirmation to avoid unintended changes.
- If the user does not confirm, stop and offer payload adjustments.

## Mandatory Confirmation Protocol

Before any write action, show:

1. Holded action (`action_id` or `operation_id`).
2. Method and endpoint.
3. `--path`, `--query`, and body parameters (`--body` or `--body-file`).
4. The exact command to run.

Use this format:

```text
This operation will modify data in Holded.
Action: <action_id> (<METHOD> <endpoint>)
Changes: <short summary>
Command: holded actions run ... --json
Do you confirm that I should run exactly this command? (reply with "yes" or "confirm")
```

Execute only after an explicit affirmative response.

## Execution Pattern

### Read Operations

1. Locate the action with `holded actions list --json` (use `--filter`).
2. Verify accepted path/query/body parameters with `holded actions describe <action> --json`.
3. Run `holded actions run <action> ... --json`.
4. Return a clear summary and relevant IDs for follow-up steps.

### Write Operations

1. Locate and validate the action.
2. Run `holded actions describe <action> --json` to verify required/optional parameters.
3. Prepare the final payload.
4. If creating a purchase receipt/ticket, verify `docType=purchase` and `"isReceipt": true`, and use `--skip-validation` flag.
5. Request mandatory confirmation.
6. Run the command after confirmation.
7. Report result (`status_code`, affected ID, API response).

## Base Commands

```bash
holded auth set --api-key "$HOLDED_API_KEY"
holded auth status
holded ping --json
holded actions list --json
holded actions list --filter contacts --json
holded actions describe invoice.get-contact --json
holded actions run invoice.get-contact --path contactId=<id> --json
```

For long payloads, prefer `--body-file`:

```bash
holded actions run invoice.update-contact \
  --path contactId=<id> \
  --body-file payload.json \
  --json
```

Purchase receipt rule (mandatory for purchase tickets):

```bash
holded actions describe invoice.create-document --json
holded actions run invoice.create-document \
  --path docType=purchase \
  --body '{"isReceipt": true, "date": 1770764400, "contactId": "<contactId>", "items": [{"name": "Description", "units": 1, "subtotal": 29.4, "tax": 0}]}' \
  --skip-validation \
  --json
```

**Important notes:**
- Use `--skip-validation` flag because holdedcli validates against Holded's schema which doesn't include `isReceipt`.
- Use `subtotal` in items (not `price`) - this is the field name Holded's API expects.
- Timestamps must be in seconds (Unix epoch) and in **Europe/Madrid timezone**.

**Timestamp calculation (Python):**
```python
from datetime import datetime, timezone, timedelta
# For 11/02/2026 00:00 in Madrid:
dt = datetime(2026, 2, 11, 0, 0, 0, tzinfo=timezone(timedelta(hours=1)))
print(int(dt.timestamp()))  # 1770764400
```

## Accounting Rules for Spain

**⚠️ ALWAYS check these rules BEFORE creating any expense document:**

| Expense Type | IVA Deductible | Expense Deductible | Account |
|--------------|----------------|---------------------|---------|
| Restaurants/Meals | ❌ No | ✅ Yes (with justification) | 629 |
| Displacement | ❌ No | ✅ Yes | 629 |
| Fuel | ⚠️ Mixed | ✅ Yes | 625/622 |
| Office supplies | ✅ Yes | ✅ Yes | 600/602 |
| Insurance | ⚠️ Mixed | ✅ Yes | 625 |

**Before creating any document, ALWAYS verify:**
1. Is the expense tax deductible?
2. Is the IVA deductible? (usually NO for restaurants, displacement)
3. If in doubt, ASK before creating the document.

**Common mistake to avoid:** Never set `tax: 10` or `tax: 21` for restaurant expenses - IVA is NOT deductible for meals unless it's a business event with proper justification.

## Error Handling

- If `MISSING_API_KEY` appears, configure API key through `--api-key`, `HOLDED_API_KEY`, or `holded auth set`.
- If `ACTION_NOT_FOUND` appears, list the catalog and search with `--filter`.
- If `INVALID_BODY` appears, validate JSON before execution.
- If `API_ERROR` appears, report `status_code` and the API snippet.

## References

- Read `{baseDir}/references/holdedcli-reference.md` for quick commands and criteria.
- Use dynamic action discovery and parameter inspection via:
  - `holded actions list --json`
  - `holded actions describe <action> --json`
