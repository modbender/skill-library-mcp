# Advanced Features API Reference

## Environments

Manage deployment stages.

### List Environments
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*}/environments
```

### Create Environment
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/environments

{
  "displayName": "production",
  "description": "Production environment",
  "versionConfigs": [
    {
      "version": "projects/.../flows/.../versions/1"
    }
  ],
  "testCasesConfig": {
    "testCases": ["projects/.../testCases/..."],
    "enableContinuousRun": true,
    "enablePredeploymentRun": true
  }
}
```

### Deploy Flow to Environment
```
POST /v3beta1/{environment}:deployFlow

{
  "flowVersion": "projects/.../flows/.../versions/1"
}
```

### Lookup Environment History
```
GET /v3beta1/{name}:lookupEnvironmentHistory
```

---

## Continuous Test Results

Monitor ongoing test health.

### List Continuous Test Results
```
GET /v3beta1/{parent=.../environments/*}/continuousTestResults
```

### Run Continuous Test
```
POST /v3beta1/{environment}:runContinuousTest
```

---

## Webhooks

External fulfillment configuration.

### List Webhooks
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*}/webhooks
```

### Create Webhook
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/webhooks

{
  "displayName": "Order Fulfillment",
  "genericWebService": {
    "uri": "https://your-webhook.com/fulfill",
    "username": "user",
    "password": "pass",
    "requestHeaders": { "X-Custom": "value" },
    "allowedCaCerts": [...],
    "webhookType": "STANDARD" | "FLEXIBLE"
  },
  "timeout": "30s"
}
```

### Webhook Request Format (what your server receives)
```json
{
  "detectIntentResponseId": "string",
  "intentInfo": { ... },
  "pageInfo": { ... },
  "sessionInfo": {
    "session": "projects/.../sessions/...",
    "parameters": { ... }
  },
  "fulfillmentInfo": { "tag": "string" },
  "text": "user input",
  "languageCode": "en"
}
```

### Webhook Response Format (what your server returns)
```json
{
  "fulfillmentResponse": {
    "messages": [
      { "text": { "text": ["Response text"] } }
    ],
    "mergeBehavior": "APPEND" | "REPLACE"
  },
  "sessionInfo": {
    "parameters": { "order_id": "12345" }
  },
  "targetPage": "projects/.../pages/...",
  "targetFlow": "projects/.../flows/..."
}
```