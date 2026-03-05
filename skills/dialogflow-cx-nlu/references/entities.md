# Entity Types API Reference

Define structured data extraction.

### System Entity Types (built-in)
- `sys.date` — Dates
- `sys.time` — Times
- `sys.number` — Numbers
- `sys.currency` — Currency amounts
- `sys.geo-city` — Cities
- `sys.geo-country` — Countries
- `sys.person` — Person names
- `sys.email` — Email addresses
- `sys.phone-number` — Phone numbers
- `sys.url` — URLs

### List Entity Types
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*}/entityTypes
```

### Create Entity Type
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/entityTypes

{
  "displayName": "string",
  "kind": "KIND_MAP" | "KIND_LIST" | "KIND_REGEXP",
  "autoExpansionMode": "AUTO_EXPANSION_MODE_DEFAULT" | "AUTO_EXPANSION_MODE_UNSPECIFIED",
  "entities": [
    {
      "value": "New York",
      "synonyms": ["NYC", "New York City", "Big Apple"]
    },
    {
      "value": "Los Angeles",
      "synonyms": ["LA", "L.A.", "City of Angels"]
    }
  ],
  "excludedPhrases": [
    { "value": "string" }
  ],
  "enableFuzzyExtraction": boolean,
  "redact": boolean
}
```

### Entity Type Kinds
| Kind | Description |
|------|-------------|
| `KIND_MAP` | Map entities to canonical values with synonyms |
| `KIND_LIST` | Simple list of values (no synonyms) |
| `KIND_REGEXP` | Regular expression matching |

### Get Entity Type
```
GET /v3beta1/{name=projects/*/locations/*/agents/*/entityTypes/*}
```

### Update Entity Type
```
PATCH /v3beta1/{entityType.name=projects/*/locations/*/agents/*/entityTypes/*}
```

### Delete Entity Type
```
DELETE /v3beta1/{name=projects/*/locations/*/agents/*/entityTypes/*}
```

### Export Entity Types
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/entityTypes:export

{
  "entityTypes": ["projects/.../entityTypes/et1"],
  "dataFormat": "BLOB" | "JSON"
}
```

### Import Entity Types
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/entityTypes:import
```

---

## Session Entity Types

Override entity types per-session.

### Create Session Entity Type
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*/sessions/*}/entityTypes

{
  "name": "...",
  "entityOverrideMode": "ENTITY_OVERRIDE_MODE_OVERRIDE" | "ENTITY_OVERRIDE_MODE_SUPPLEMENT",
  "entities": [...]
}
```

Use when you need user-specific or context-specific entities.