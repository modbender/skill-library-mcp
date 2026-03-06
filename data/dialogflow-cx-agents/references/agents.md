# Agents API Reference

## Agents

### List Agents
```
GET /v3beta1/projects/{project}/locations/{location}/agents
```

### Create Agent
```
POST /v3beta1/projects/{project}/locations/{location}/agents

{
  "displayName": "string",
  "defaultLanguageCode": "string",
  "supportedLanguageCodes": ["string"],
  "timeZone": "string",
  "description": "string",
  "avatarUri": "string",
  "enableStackdriverLogging": boolean,
  "enableSpellCorrection": boolean,
  "advancedSettings": { ... },
  "gitIntegrationSettings": { ... },
  "textToSpeechSettings": { ... },
  "genAppBuilderSettings": { ... }
}
```

### Get Agent
```
GET /v3beta1/{name=projects/*/locations/*/agents/*}
```

### Update Agent
```
PATCH /v3beta1/{agent.name=projects/*/locations/*/agents/*}
```

### Delete Agent
```
DELETE /v3beta1/{name=projects/*/locations/*/agents/*}
```

### Export Agent
```
POST /v3beta1/{name=projects/*/locations/*/agents/*}:export

{
  "agentUri": "gs://bucket/path",  // OR
  "dataFormat": "BLOB" | "JSON_PACKAGE"
}
```

### Restore Agent
```
POST /v3beta1/{name=projects/*/locations/*/agents/*}:restore

{
  "agentUri": "gs://bucket/path",  // OR
  "agentContent": "base64-encoded"
}
```

### Validate Agent
```
POST /v3beta1/{name=projects/*/locations/*/agents/*}:validate
```