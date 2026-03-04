# Websites MCP API Schema

This document defines the exact JSON-RPC request shapes for the `websites-mcp` server.

## Root cause of prior failures

`websites.run_task` expects task input under **`params.params`** (nested), not `params.input`.

From `src/server.ts`, `websites.run_task` reads:

- `siteId`
- `taskId`
- `params` (this object is passed to the task validator)

## JSON-RPC envelope

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "websites.run_task",
  "params": {
    "siteId": "prospairrow",
    "taskId": "add_prospects",
    "params": {
      "...task-specific-fields...": "..."
    }
  }
}
```

## Tool methods

- `websites.list_sites`
- `websites.bootstrap_login`
- `websites.run_task`

## Prospairrow task input schemas

### 1) `add_prospects` (WRITE)

File: `src/sites/prospairrow/tasks/add_prospects.ts`

```json
{
  "prospects": [
    {
      "company": "string (required)",
      "website": "valid URL (required)",
      "location": "string (optional)",
      "industry": "string (optional)",
      "notes": "string (optional)"
    }
  ],
  "dedupe": "boolean (optional, default true)",
  "diagnostics": "boolean (optional, default false)"
}
```

### 2) `enrich_prospects` (WRITE)

File: `src/sites/prospairrow/tasks/enrich_prospects.ts`

```json
{
  "prospectIds": ["string"],
  "prospects": [
    {
      "company": "string (required)",
      "website": "valid URL (optional)"
    }
  ],
  "mode": "standard|deep (optional, default standard)",
  "diagnostics": "boolean (optional, default false)"
}
```

Constraint: at least one of `prospectIds` or `prospects` must be provided.

### 3) `get_prospect_detail` (READ_ONLY)

File: `src/sites/prospairrow/tasks/get_prospect_detail.ts`

```json
{
  "id": "string (optional)",
  "company": "string (optional)",
  "website": "valid URL (optional)",
  "diagnostics": "boolean (optional, default false)"
}
```

Constraint: at least one of `id`, `company`, `website` must be provided.

### 4) `list_icp_qualified_companies` (READ_ONLY)

File: `src/sites/prospairrow/tasks/list_icp_qualified_companies.ts`

```json
{
  "min_company_score": "number 0..100 (optional, default 40)",
  "min_icp_score": "number 0..100 (optional)",
  "per_page": "integer 1..200 (optional, default 10)",
  "page": "integer >= 1 (optional, default 1)",
  "diagnostics": "boolean (optional, default false)"
}
```

### 5) `apollo_enrich` (WRITE)

File: `src/sites/prospairrow/tasks/apollo_enrich.ts`

```json
{
  "prospect_id": "string or positive integer (required)",
  "reveal": "boolean (optional, default true)",
  "reveal_limit": "integer 1..100 (optional, default 1)",
  "diagnostics": "boolean (optional, default false)"
}
```

### 6) `get_icp_score` (READ_ONLY)

File: `src/sites/prospairrow/tasks/get_icp_score.ts`

```json
{
  "prospect_id": "string or positive integer (required)",
  "force_rescore": "boolean (optional, default false)",
  "diagnostics": "boolean (optional, default false)"
}
```

### 7) `get_company_score` (READ_ONLY)

File: `src/sites/prospairrow/tasks/get_company_score.ts`

```json
{
  "prospect_id": "string or positive integer (required)",
  "diagnostics": "boolean (optional, default false)"
}
```

## Working examples

### List sites

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"websites.list_sites","params":{}}'
```

### Add prospects (correct nested shape)

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"add_prospects",
      "params":{
        "dedupe":true,
        "prospects":[
          {"company":"Acme Rocket Supply","website":"https://example.com"},
          {"company":"Nimbus Analytics","website":"https://www.nimbus.ai"},
          {"company":"Cedar Ridge Manufacturing","website":"https://www.cedarridgemfg.com"}
        ]
      }
    }
  }'
```

### Enrich prospects

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"enrich_prospects",
      "params":{
        "prospects":[
          {"company":"Acme Rocket Supply","website":"https://example.com"}
        ],
        "mode":"standard"
      }
    }
  }'
```

### Get prospect detail

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "id":4,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"get_prospect_detail",
      "params":{
        "company":"Acme Rocket Supply"
      }
    }
  }'
```

### List ICP-qualified companies (parameterized min_company_score)

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -d '{
    "jsonrpc":"2.0",
    "id":5,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"list_icp_qualified_companies",
      "params":{
        "min_company_score":40,
        "per_page":10
      }
    }
  }'
```

### Apollo enrich (configurable reveal_limit)

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -H 'x-api-key: sk_...' \
  -d '{
    "jsonrpc":"2.0",
    "id":6,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"apollo_enrich",
      "params":{
        "prospect_id":123,
        "reveal":true,
        "reveal_limit":2
      }
    }
  }'
```

### Get ICP score (optional force_rescore)

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -H 'x-api-key: sk_...' \
  -d '{
    "jsonrpc":"2.0",
    "id":7,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"get_icp_score",
      "params":{
        "prospect_id":185,
        "force_rescore":false
      }
    }
  }'
```

### Get company score

```bash
curl -sS http://127.0.0.1:8799 \
  -H 'content-type: application/json' \
  -H 'x-api-key: sk_...' \
  -d '{
    "jsonrpc":"2.0",
    "id":8,
    "method":"websites.run_task",
    "params":{
      "siteId":"prospairrow",
      "taskId":"get_company_score",
      "params":{
        "prospect_id":185
      }
    }
  }'
```
