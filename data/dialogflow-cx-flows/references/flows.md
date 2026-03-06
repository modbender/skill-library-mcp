# Flows & Pages API Reference

## Flows

Flows define conversation paths. Every agent has a "Default Start Flow".

### List Flows
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*}/flows
```

### Create Flow
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/flows

{
  "displayName": "string",
  "description": "string",
  "transitionRoutes": [...],
  "eventHandlers": [...],
  "transitionRouteGroups": [...],
  "nluSettings": { ... }
}
```

### Get Flow
```
GET /v3beta1/{name=projects/*/locations/*/agents/*/flows/*}
```

### Update Flow
```
PATCH /v3beta1/{flow.name=projects/*/locations/*/agents/*/flows/*}
```

### Delete Flow
```
DELETE /v3beta1/{name=projects/*/locations/*/agents/*/flows/*}
```

### Train Flow
```
POST /v3beta1/{name=projects/*/locations/*/agents/*/flows/*}:train
```

### Validate Flow
```
POST /v3beta1/{name=projects/*/locations/*/agents/*/flows/*}:validate
```

### Export Flow
```
POST /v3beta1/{name=projects/*/locations/*/agents/*/flows/*}:export
```

### Import Flow
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*}/flows:import
```

---

## Pages

Pages are states within a flow.

### List Pages
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*/flows/*}/pages
```

### Create Page
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*/flows/*}/pages

{
  "displayName": "string",
  "entryFulfillment": { ... },
  "form": { ... },
  "transitionRouteGroups": [...],
  "transitionRoutes": [...],
  "eventHandlers": [...]
}
```

### Get Page
```
GET /v3beta1/{name=projects/*/locations/*/agents/*/flows/*/pages/*}
```

### Update Page
```
PATCH /v3beta1/{page.name=projects/*/locations/*/agents/*/flows/*/pages/*}
```

### Delete Page
```
DELETE /v3beta1/{name=projects/*/locations/*/agents/*/flows/*/pages/*}
```

---

## Transition Route Groups

Reusable routing logic across pages.

### List
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*/flows/*}/transitionRouteGroups
```

### Create
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*/flows/*}/transitionRouteGroups

{
  "displayName": "string",
  "transitionRoutes": [...]
}
```

### Get/Update/Delete
Standard REST patterns apply.

---

## Versions

Immutable snapshots of flows.

### List Versions
```
GET /v3beta1/{parent=projects/*/locations/*/agents/*/flows/*}/versions
```

### Create Version
```
POST /v3beta1/{parent=projects/*/locations/*/agents/*/flows/*}/versions

{
  "displayName": "string",
  "description": "string"
}
```

### Load Version (restore flow to version)
```
POST /v3beta1/{name=projects/*/locations/*/agents/*/flows/*/versions/*}:load
```