# Intents API Reference

Intents classify user utterances.

### List Intents
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*}/intents
```

### Create Intent
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/intents

{
  "displayName": "string",
  "trainingPhrases": [
    {
      "parts": [
        { "text": "I want to book a " },
        { "text": "flight", "parameterId": "destination" }
      ],
      "repeatCount": 1
    }
  ],
  "parameters": [
    {
      "id": "destination",
      "entityType": "projects/-/locations/-/agents/-/entityTypes/sys.geo-city",
      "isList": false,
      "redact": false
    }
  ],
  "priority": 500000,
  "isFallback": false,
  "labels": {},
  "description": "string"
}
```

### Get Intent
```
GET /v3beta1/{name=projects/*/locations/*/agents/*/intents/*}
```

### Update Intent
```
PATCH /v3beta1/{intent.name=projects/*/locations/*/agents/*/intents/*}
```

### Delete Intent
```
DELETE /v3beta1/{name=projects/*/locations/*/agents/*/intents/*}
```

### Export Intents
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/intents:export

{
  "intents": ["projects/.../intents/intent1"],
  "dataFormat": "BLOB" | "JSON"
}
```

### Import Intents
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/intents:import

{
  "intentsUri": "gs://...",  // OR
  "intentsContent": { "intents": [...] }
}
```