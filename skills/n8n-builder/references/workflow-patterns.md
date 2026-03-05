# n8n Workflow Patterns

## Pattern 1: Webhook → Process → Respond

Receive HTTP request, process data, return response.

```json
{
  "name": "Webhook Processor",
  "nodes": [
    {
      "id": "webhook1",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "my-endpoint",
        "httpMethod": "POST",
        "responseMode": "responseNode"
      }
    },
    {
      "id": "code1",
      "name": "Process",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [450, 300],
      "parameters": {
        "jsCode": "for (const item of $input.all()) {\n  item.json.processed = true;\n}\nreturn $input.all();"
      }
    },
    {
      "id": "respond1",
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [650, 300],
      "parameters": {
        "respondWith": "allIncomingItems"
      }
    }
  ],
  "connections": {
    "Webhook": { "main": [[ { "node": "Process", "type": "main", "index": 0 } ]] },
    "Process": { "main": [[ { "node": "Respond", "type": "main", "index": 0 } ]] }
  },
  "settings": { "executionOrder": "v1" }
}
```

## Pattern 2: Schedule → Fetch → Conditional → Action

Periodic check with branching logic.

```json
{
  "name": "Scheduled Check",
  "nodes": [
    {
      "id": "schedule1",
      "name": "Every Hour",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [250, 300],
      "parameters": {
        "rule": { "interval": [{ "field": "hours", "hoursInterval": 1 }] }
      }
    },
    {
      "id": "http1",
      "name": "Fetch Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [450, 300],
      "parameters": {
        "url": "https://api.example.com/data",
        "method": "GET"
      }
    },
    {
      "id": "if1",
      "name": "Has Results?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 300],
      "parameters": {
        "conditions": {
          "options": { "caseSensitive": true, "leftValue": "", "typeValidation": "strict" },
          "conditions": [
            { "leftValue": "={{ $json.results.length }}", "rightValue": "0", "operator": { "type": "number", "operation": "gt" } }
          ],
          "combinator": "and"
        }
      }
    },
    {
      "id": "slack1",
      "name": "Notify Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.2,
      "position": [850, 200],
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": "#alerts",
        "text": "={{ $json.results.length }} new results found"
      }
    },
    {
      "id": "noop1",
      "name": "No Results",
      "type": "n8n-nodes-base.noOp",
      "typeVersion": 1,
      "position": [850, 400],
      "parameters": {}
    }
  ],
  "connections": {
    "Every Hour": { "main": [[ { "node": "Fetch Data", "type": "main", "index": 0 } ]] },
    "Fetch Data": { "main": [[ { "node": "Has Results?", "type": "main", "index": 0 } ]] },
    "Has Results?": {
      "main": [
        [ { "node": "Notify Slack", "type": "main", "index": 0 } ],
        [ { "node": "No Results", "type": "main", "index": 0 } ]
      ]
    }
  },
  "settings": { "executionOrder": "v1" }
}
```

## Pattern 3: AI Agent with Tools

LangChain AI agent that can call sub-workflows as tools.

```json
{
  "name": "AI Agent",
  "nodes": [
    {
      "id": "webhook1",
      "name": "Chat Input",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "position": [250, 300],
      "parameters": {
        "path": "chat",
        "httpMethod": "POST",
        "responseMode": "responseNode"
      }
    },
    {
      "id": "agent1",
      "name": "AI Agent",
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 1.7,
      "position": [550, 300],
      "parameters": {
        "text": "={{ $json.body.message }}",
        "options": { "systemMessage": "You are a helpful assistant." }
      }
    },
    {
      "id": "llm1",
      "name": "OpenAI",
      "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
      "typeVersion": 1,
      "position": [550, 500],
      "parameters": {
        "model": "gpt-4o",
        "options": { "temperature": 0.7 }
      }
    },
    {
      "id": "respond1",
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [750, 300],
      "parameters": { "respondWith": "allIncomingItems" }
    }
  ],
  "connections": {
    "Chat Input": { "main": [[ { "node": "AI Agent", "type": "main", "index": 0 } ]] },
    "AI Agent": { "main": [[ { "node": "Respond", "type": "main", "index": 0 } ]] },
    "OpenAI": { "ai_languageModel": [[ { "node": "AI Agent", "type": "ai_languageModel", "index": 0 } ]] }
  },
  "settings": { "executionOrder": "v1" }
}
```

## Pattern 4: Database → Transform → Multi-Output

Read from DB, transform data, send to multiple destinations.

```json
{
  "name": "DB Sync",
  "nodes": [
    {
      "id": "trigger1",
      "name": "Every Day",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [250, 300],
      "parameters": {
        "rule": { "interval": [{ "field": "days", "daysInterval": 1 }] }
      }
    },
    {
      "id": "pg1",
      "name": "Query DB",
      "type": "n8n-nodes-base.postgres",
      "typeVersion": 2.5,
      "position": [450, 300],
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT * FROM leads WHERE status = 'new' AND created_at > NOW() - INTERVAL '1 day'"
      }
    },
    {
      "id": "set1",
      "name": "Transform",
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [650, 300],
      "parameters": {
        "mode": "manual",
        "fields": {
          "values": [
            { "name": "fullName", "stringValue": "={{ $json.first_name }} {{ $json.last_name }}" },
            { "name": "phone", "stringValue": "={{ $json.phone }}" }
          ]
        }
      }
    },
    {
      "id": "sheets1",
      "name": "Update Sheet",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4.5,
      "position": [850, 200],
      "parameters": {
        "operation": "append",
        "documentId": { "__rl": true, "mode": "url", "value": "https://docs.google.com/spreadsheets/d/xxx" },
        "sheetName": { "__rl": true, "mode": "list", "value": "Sheet1" }
      }
    },
    {
      "id": "slack1",
      "name": "Notify",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.2,
      "position": [850, 400],
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": "#leads",
        "text": "={{ $json.fullName }} - new lead added"
      }
    }
  ],
  "connections": {
    "Every Day": { "main": [[ { "node": "Query DB", "type": "main", "index": 0 } ]] },
    "Query DB": { "main": [[ { "node": "Transform", "type": "main", "index": 0 } ]] },
    "Transform": { "main": [[
      { "node": "Update Sheet", "type": "main", "index": 0 },
      { "node": "Notify", "type": "main", "index": 0 }
    ]] }
  },
  "settings": { "executionOrder": "v1" }
}
```

## Pattern 5: Error Handling

Wrap risky operations with error handling.

```json
{
  "nodes": [
    {
      "id": "trigger1",
      "name": "Start",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [250, 300],
      "parameters": {}
    },
    {
      "id": "http1",
      "name": "Risky Call",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.2,
      "position": [450, 300],
      "parameters": {
        "url": "https://api.example.com/fragile",
        "options": { "timeout": 10000 }
      },
      "continueOnFail": true
    },
    {
      "id": "if1",
      "name": "Check Error",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 300],
      "parameters": {
        "conditions": {
          "conditions": [
            { "leftValue": "={{ $json.error }}", "rightValue": "", "operator": { "type": "string", "operation": "exists" } }
          ],
          "combinator": "and"
        }
      }
    }
  ]
}
```

## Expression Syntax Quick Reference

- Access current item: `{{ $json.fieldName }}`
- Access input item: `{{ $input.item.json.field }}`
- Previous node: `{{ $('Node Name').item.json.field }}`
- All items from node: `{{ $('Node Name').all() }}`
- Environment variable: `{{ $env.MY_VAR }}`
- Execution ID: `{{ $execution.id }}`
- Workflow ID: `{{ $workflow.id }}`
- Current timestamp: `{{ $now.toISO() }}`
- Math: `{{ Math.round($json.price * 1.1) }}`
- Conditional: `{{ $json.status === 'active' ? 'Yes' : 'No' }}`
