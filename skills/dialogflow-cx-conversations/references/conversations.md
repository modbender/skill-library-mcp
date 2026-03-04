# Conversations & Testing API Reference

## Sessions (Detect Intent)

Send user messages and get agent responses.

### Detect Intent
```
POST /v3beta1/{session=projects/*/locations/*/agents/*/sessions/*}:detectIntent

{
  "queryParams": {
    "timeZone": "Asia/Kolkata",
    "geoLocation": { "latitude": 18.5, "longitude": 73.8 },
    "sessionEntityTypes": [...],
    "payload": { ... },
    "parameters": { ... },
    "currentPage": "projects/.../pages/page1",
    "disableWebhook": boolean,
    "analyzeQueryTextSentiment": boolean,
    "channel": "string"
  },
  "queryInput": {
    "text": { "text": "Hello" },
    // OR
    "intent": { "intent": "projects/.../intents/..." },
    // OR
    "audio": { "config": {...}, "audio": "base64" },
    // OR
    "event": { "event": "custom-event" },
    // OR
    "dtmf": { "digits": "1234", "finishDigit": "#" },
    "languageCode": "en"
  }
}
```

### Response Structure
```json
{
  "responseId": "string",
  "queryResult": {
    "text": "user input",
    "languageCode": "en",
    "parameters": { ... },
    "responseMessages": [
      { "text": { "text": ["Hello! How can I help?"] } }
    ],
    "webhookStatuses": [...],
    "webhookPayloads": [...],
    "currentPage": { "name": "...", "displayName": "..." },
    "currentFlow": { "name": "...", "displayName": "..." },
    "intent": { "name": "...", "displayName": "..." },
    "intentDetectionConfidence": 0.95,
    "match": { ... },
    "diagnosticInfo": { ... },
    "sentimentAnalysisResult": { ... }
  },
  "outputAudio": "base64",
  "outputAudioConfig": { ... }
}
```

### Server-Side Streaming Detect Intent
```
POST /v3beta1/{session}:serverStreamingDetectIntent
```
For real-time streaming responses.

### Match Intent (no side effects)
```
POST /v3beta1/{session}:matchIntent
```
Returns matching intents without advancing conversation state.

### Fulfill Intent
```
POST /v3beta1/{session}:fulfillIntent
```
Execute fulfillment after matching.

---

## Test Cases

Automated conversation testing.

### List Test Cases
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*}/testCases
```

### Create Test Case
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/testCases

{
  "displayName": "Greeting Test",
  "tags": ["regression", "greeting"],
  "notes": "Tests basic greeting flow",
  "testCaseConversationTurns": [
    {
      "userInput": {
        "input": { "text": { "text": "Hi" } },
        "isWebhookEnabled": true
      },
      "virtualAgentOutput": {
        "triggeredIntent": { "name": "projects/.../intents/greeting" },
        "currentPage": { "name": "projects/.../pages/welcome" },
        "textResponses": [
          { "text": ["Hello! Welcome!"] }
        ]
      }
    }
  ]
}
```

### Run Test Case
```
POST /v3beta1/{name}:run
```

### Batch Run Test Cases
```
POST /v3beta1/{parent}/testCases:batchRun

{
  "testCases": ["projects/.../testCases/tc1", "..."],
  "environment": "projects/.../environments/production"
}
```

### Get Test Case Result
```
GET /v3beta1/{parent}/testCases/{testCase}/results/{result}
```

### List Test Case Results
```
GET /v3beta1/{parent}/testCases/{testCase}/results
```

### Export Test Cases
```
POST /v3beta1/{parent}/testCases:export

{
  "dataFormat": "BLOB" | "JSON"
}
```

### Import Test Cases
```
POST /v3beta1/{parent}/testCases:import
```