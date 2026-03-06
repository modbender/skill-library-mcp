---
name: odoo-json2-operator
description: Execute Odoo operations through JSON-2 API endpoints with bearer API keys. Use when the user asks to query or mutate Odoo data (search, read, create, write, unlink, or custom model methods), validate model/method signatures from the api_doc module, or automate step-by-step business actions against an Odoo instance.
---

# Odoo JSON-2 Operator

Use this skill to execute Odoo model methods safely via HTTP API.

## Use bundled resources
- Read `references/odoo-api-doc-module.md` for route map and payload conventions based on the local `api_doc` module.
- Read `references/api-doc-static-src-learning.md` for model discovery/search/method payload behavior extracted from `api_doc/static/src`.
- Read `references/analysis-playbook.md` when user asks for summary analysis, management report, trend interpretation, or decision advice.
- Use `scripts/odoo_json2_client.py` to perform deterministic discovery and API calls.

## Workflow
1. Collect required connection inputs first: `base_url`, `database`, `api_key`.
2. Parse user natural-language request into operation intent:
   - Infer target business object and map it to likely Odoo model.
   - Infer operation type (query/read/create/update/delete/custom action/data analysis).
3. Discover and validate the target method:
   - Call `/doc-bearer/index.json` to confirm the model exists.
   - Call `/doc-bearer/<model>.json` to confirm method name and parameter hints.
4. Build a minimal payload:
   - Read operations first (`search`, `search_read`, `read`) to verify scope.
   - For mutating operations, include only required and changed fields.
5. Execute API call using script:
   - Endpoint: `/json/2/<model>/<method>`
   - Method: `POST`
   - Headers: bearer token, JSON content type, `X-Odoo-Database`.
   - Store temporary payload files only under `skills/odoo-json2-operator/.tmp/`.
   - If `--payload-file` points to a `tmp_*.json` file (or any JSON under `--tmp-dir`), the client auto-deletes it after execution.
   - To keep temp payloads for debugging, pass `--keep-tmp-payload-file`.
6. Parse and report result:
   - If success, summarize key business outcome.
   - If failure, include HTTP status, `message`, and `debug` details when present.
7. If user asks for analysis/report:
   - Aggregate and compare data by period/segment.
   - Produce professional interpretation and decision recommendations in plain Chinese.

## Conversation protocol
- Persist successful connections locally as named profiles containing `base_url`, `database`, and `api_key`.
- Reuse saved profile by default in later turns; do not repeatedly ask for credentials.
- If multiple profiles exist and user does not specify a target system at session start, ask which system/profile to use before proceeding.
- Ask for `base_url`, `database`, and `api_key` only when no usable profile exists or when user wants a new/updated system.
- Accept free-form user text and convert it to `model`, `method`, and payload draft.
- Discover models and methods from `/doc-bearer/index.json` before choosing targets.
- Use normalized matching for intent mapping (lowercase + strip punctuation) and prioritize exact model/method hits.
- Validate chosen model with `/doc-bearer/<model>.json` and align payload keys to documented parameters.
- If required parameters are missing, ask in plain language and provide concrete examples.
- Explain parameters in business terms, not internal API jargon.
- Confirm assumptions when model mapping is ambiguous.

## Analysis output standard
When the task is analysis/reporting, answer with this structure:
- `结论摘要`: 1-3 lines, direct answer first.
- `关键发现`: data-backed findings with core numbers.
- `风险与机会`: what may worsen and where upside exists.
- `决策建议`: 3-5 prioritized actions with expected impact and effort.
- `下一步`: missing data to improve confidence and follow-up checks.

Use plain Chinese, avoid dense jargon, and clearly separate facts vs assumptions.

## Missing-parameter guidance style
Use short, clear prompts like:
- "我已经知道你要更新客户了，但还差客户ID。请给我一个或多个客户ID，例如 `[45]`。"
- "你要创建销售订单，还缺必填字段 `partner_id`（客户）和 `order_line`（订单行）。你可以告诉我客户是谁、商品和数量，我来帮你组装。"
- "当前只差连接信息：请发我 `base_url`、`database`、`API Key`，我就可以开始执行。"
- "要做经营分析还缺时间范围。请告诉我你要看最近7天、30天，还是本月/上月。"

## Command templates
```bash
python skills/odoo-json2-operator/scripts/odoo_json2_client.py \
  --save-profile "odoo-prod" \
  --base-url "https://odoo.example.com" \
  --database "mydb" \
  --api-key "$ODOO_API_KEY"
```

```bash
python skills/odoo-json2-operator/scripts/odoo_json2_client.py --list-profiles
```

```bash
python skills/odoo-json2-operator/scripts/odoo_json2_client.py \
  --profile "odoo-prod" \
  --discover-index
```

```bash
python skills/odoo-json2-operator/scripts/odoo_json2_client.py \
  --profile "odoo-prod" \
  --discover-model "res.partner"
```

```bash
python skills/odoo-json2-operator/scripts/odoo_json2_client.py \
  --profile "odoo-prod" \
  --model "res.partner" \
  --method "search_read" \
  --payload '{"domain": [["name", "ilike", "Acme"]], "fields": ["name", "email"], "limit": 20}'
```

```bash
python skills/odoo-json2-operator/scripts/odoo_json2_client.py \
  --profile "odoo-prod" \
  --tmp-dir "skills/odoo-json2-operator/.tmp" \
  --model "res.partner" \
  --method "search_read" \
  --payload-file "skills/odoo-json2-operator/.tmp/tmp_partner_search.json"
```

## Guardrails
- Never guess model/method names when discovery endpoints are available.
- Never run destructive mutations without first showing the matching records unless user explicitly asks to skip preview.
- Never log or persist API keys in files, command history snippets, or chat output.
- Prefer idempotent operations where possible.
