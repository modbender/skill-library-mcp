# Collections — Postman

## Full Collection Structure

```json
{
  "info": {
    "name": "API Name",
    "description": "API description",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "auth": {
    "type": "bearer",
    "bearer": [{ "key": "token", "value": "{{token}}" }]
  },
  "variable": [
    { "key": "base_url", "value": "https://api.example.com" }
  ],
  "item": []
}
```

## Request Templates

### GET with Query Params
```json
{
  "name": "List Items",
  "request": {
    "method": "GET",
    "url": {
      "raw": "{{base_url}}/items?page={{page}}&limit={{limit}}",
      "host": ["{{base_url}}"],
      "path": ["items"],
      "query": [
        { "key": "page", "value": "{{page}}" },
        { "key": "limit", "value": "{{limit}}" }
      ]
    }
  }
}
```

### POST with JSON Body
```json
{
  "name": "Create Item",
  "request": {
    "method": "POST",
    "url": "{{base_url}}/items",
    "header": [
      { "key": "Content-Type", "value": "application/json" }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"name\": \"{{name}}\",\n  \"value\": {{value}}\n}",
      "options": { "raw": { "language": "json" } }
    }
  }
}
```

### PUT Update
```json
{
  "name": "Update Item",
  "request": {
    "method": "PUT",
    "url": "{{base_url}}/items/{{item_id}}",
    "header": [
      { "key": "Content-Type", "value": "application/json" }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"name\": \"{{name}}\"\n}"
    }
  }
}
```

### DELETE
```json
{
  "name": "Delete Item",
  "request": {
    "method": "DELETE",
    "url": "{{base_url}}/items/{{item_id}}"
  }
}
```

### File Upload
```json
{
  "name": "Upload File",
  "request": {
    "method": "POST",
    "url": "{{base_url}}/upload",
    "body": {
      "mode": "formdata",
      "formdata": [
        { "key": "file", "type": "file", "src": "/path/to/file.pdf" },
        { "key": "description", "value": "My file", "type": "text" }
      ]
    }
  }
}
```

## Folder Organization

```json
{
  "item": [
    {
      "name": "Auth",
      "item": [
        { "name": "Login", "request": {...} },
        { "name": "Refresh Token", "request": {...} }
      ]
    },
    {
      "name": "Users",
      "item": [
        { "name": "List Users", "request": {...} },
        { "name": "Get User", "request": {...} },
        { "name": "Create User", "request": {...} }
      ]
    }
  ]
}
```

## Collection Variables vs Environment Variables

| Type | Use For | Example |
|------|---------|---------|
| Collection | Constants across all envs | API version, content types |
| Environment | Values that change | base_url, tokens, test data |

## Auth Inheritance

Set auth at collection level, requests inherit:

```json
{
  "auth": {
    "type": "bearer",
    "bearer": [{ "key": "token", "value": "{{token}}" }]
  }
}
```

Override per-request if needed (e.g., public endpoints).
