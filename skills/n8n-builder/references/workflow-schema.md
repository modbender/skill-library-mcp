# n8n Workflow JSON Schema Reference

## Root Structure

```json
{
  "name": "Workflow Name",
  "nodes": [],
  "connections": {},
  "settings": {},
  "active": false
}
```

## Node Object (Required Fields)

```json
{
  "id": "unique-id-string",
  "name": "Display Name",
  "type": "n8n-nodes-base.nodeType",
  "typeVersion": 1,
  "position": [x, y],
  "parameters": {}
}
```

Optional: `credentials`, `disabled`, `notes`, `notesInFlow`

## Connections Object

Connections map source node names to destination nodes:

```json
{
  "Source Node Name": {
    "main": [
      [
        { "node": "Target Node Name", "type": "main", "index": 0 }
      ]
    ]
  }
}
```

- `main` = array of output arrays (index 0 = first output, 1 = second for IF nodes, etc.)
- Each output array contains connection objects pointing to target nodes

### IF Node (two outputs)

```json
{
  "IF": {
    "main": [
      [ { "node": "True Branch", "type": "main", "index": 0 } ],
      [ { "node": "False Branch", "type": "main", "index": 0 } ]
    ]
  }
}
```

## Common Node Types

### Triggers
| Type | Description |
|------|-------------|
| `n8n-nodes-base.manualTrigger` | Manual execution |
| `n8n-nodes-base.webhook` | HTTP webhook (GET/POST/etc.) |
| `n8n-nodes-base.scheduleTrigger` | Cron/interval schedule |
| `n8n-nodes-base.emailTrigger` | IMAP email trigger |
| `n8n-nodes-base.n8nTrigger` | Triggered by another workflow |

### Core Nodes
| Type | Description |
|------|-------------|
| `n8n-nodes-base.set` | Set/transform values |
| `n8n-nodes-base.code` | JavaScript/Python code |
| `n8n-nodes-base.if` | Conditional branching |
| `n8n-nodes-base.switch` | Multi-branch routing |
| `n8n-nodes-base.merge` | Merge multiple inputs |
| `n8n-nodes-base.splitInBatches` | Process items in batches |
| `n8n-nodes-base.wait` | Delay/wait |
| `n8n-nodes-base.noOp` | No operation (passthrough) |
| `n8n-nodes-base.respondToWebhook` | Return webhook response |
| `n8n-nodes-base.executeWorkflow` | Call another workflow |
| `n8n-nodes-base.function` | Legacy code node |
| `n8n-nodes-base.filter` | Filter items by condition |
| `n8n-nodes-base.removeDuplicates` | Deduplicate items |
| `n8n-nodes-base.sort` | Sort items |
| `n8n-nodes-base.limit` | Limit number of items |
| `n8n-nodes-base.aggregate` | Aggregate items |
| `n8n-nodes-base.itemLists` | Split/concat/limit items |
| `n8n-nodes-base.dateTime` | Date/time operations |
| `n8n-nodes-base.crypto` | Hash, encrypt, etc. |
| `n8n-nodes-base.xml` | XML parse/generate |
| `n8n-nodes-base.html` | HTML extract/generate |
| `n8n-nodes-base.markdown` | Markdown convert |
| `n8n-nodes-base.errorTrigger` | Handle workflow errors |

### HTTP & API
| Type | Description |
|------|-------------|
| `n8n-nodes-base.httpRequest` | Generic HTTP request |
| `n8n-nodes-base.graphql` | GraphQL queries |
| `n8n-nodes-base.ftp` | FTP upload/download |
| `n8n-nodes-base.ssh` | SSH commands |

### Databases
| Type | Description |
|------|-------------|
| `n8n-nodes-base.postgres` | PostgreSQL |
| `n8n-nodes-base.mysql` | MySQL |
| `n8n-nodes-base.mongoDb` | MongoDB |
| `n8n-nodes-base.redis` | Redis |
| `n8n-nodes-base.sqlite` | SQLite |

### Communication
| Type | Description |
|------|-------------|
| `n8n-nodes-base.slack` | Slack |
| `n8n-nodes-base.discord` | Discord |
| `n8n-nodes-base.telegram` | Telegram |
| `n8n-nodes-base.twilio` | Twilio SMS/call |
| `n8n-nodes-base.sendGrid` | SendGrid email |
| `n8n-nodes-base.gmail` | Gmail |
| `n8n-nodes-base.microsoftOutlook` | Outlook |

### CRM & Sales
| Type | Description |
|------|-------------|
| `n8n-nodes-base.hubspot` | HubSpot |
| `n8n-nodes-base.salesforce` | Salesforce |
| `n8n-nodes-base.pipedrive` | Pipedrive |
| `n8n-nodes-base.airtable` | Airtable |

### AI Nodes
| Type | Description |
|------|-------------|
| `@n8n/n8n-nodes-langchain.openAi` | OpenAI API |
| `@n8n/n8n-nodes-langchain.agent` | AI Agent (LangChain) |
| `@n8n/n8n-nodes-langchain.chainLlm` | LLM Chain |
| `@n8n/n8n-nodes-langchain.chainSummarization` | Summarization Chain |
| `@n8n/n8n-nodes-langchain.toolWorkflow` | Tool (sub-workflow) |
| `@n8n/n8n-nodes-langchain.memoryBufferWindow` | Conversation memory |
| `@n8n/n8n-nodes-langchain.outputParserStructured` | Structured output |

### Files & Storage
| Type | Description |
|------|-------------|
| `n8n-nodes-base.googleSheets` | Google Sheets |
| `n8n-nodes-base.googleDrive` | Google Drive |
| `n8n-nodes-base.s3` | AWS S3 |
| `n8n-nodes-base.readWriteFile` | Local file read/write |
| `n8n-nodes-base.spreadsheetFile` | CSV/XLS processing |

### Other
| Type | Description |
|------|-------------|
| `n8n-nodes-base.googleCalendar` | Google Calendar |
| `n8n-nodes-base.stripe` | Stripe payments |
| `n8n-nodes-base.shopify` | Shopify |
| `n8n-nodes-base.notion` | Notion |
| `n8n-nodes-base.github` | GitHub |
| `n8n-nodes-base.jira` | Jira |

## Node Positioning Guidelines

- Start trigger at `[250, 300]`
- Space nodes ~200px apart horizontally
- Keep vertically aligned for linear flows
- Branch nodes offset vertically by ±150px

## Settings Object

```json
{
  "settings": {
    "executionOrder": "v1",
    "saveManualExecutions": true,
    "callerPolicy": "workflowsFromSameOwner"
  }
}
```

## Credentials Reference

Credentials are referenced by name and type in nodes:

```json
{
  "credentials": {
    "twilioApi": {
      "id": "cred_id",
      "name": "My Twilio"
    }
  }
}
```

Credentials must exist in the target n8n instance before workflow activation. The API cannot create credentials — set them up in the n8n UI first.
