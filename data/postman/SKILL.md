---
name: Postman
slug: postman
version: 1.0.0
homepage: https://clawic.com/skills/postman
description: Build, test, and automate APIs with Postman collections, environments, and Newman CLI.
metadata: {"clawdbot":{"emoji":"📮","requires":{"bins":["newman"]},"os":["linux","darwin","win32"],"install":[{"id":"npm","kind":"npm","package":"newman","bins":["newman"],"label":"Install Newman (npm)"}]}}
changelog: Initial release with collections, environments, and Newman automation.
---

## Setup

If `~/postman/` doesn't exist, read `setup.md` silently and start naturally.

## When to Use

User needs to test APIs, create Postman collections, manage environments, or run automated API tests with Newman.

## Architecture

Data lives in `~/postman/`. See `memory-template.md` for structure.

```
~/postman/
├── memory.md           # Projects, preferences, common patterns
├── collections/        # Postman collection JSON files
└── environments/       # Environment JSON files
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup | `setup.md` |
| Memory template | `memory-template.md` |
| Collection format | `collections.md` |
| Newman automation | `newman.md` |

## Core Rules

### 1. Collection Structure First
Before creating requests, define the collection structure:
- Folder hierarchy reflects API organization
- Use descriptive names: `Users > Create User`, not `POST 1`
- Group related endpoints logically

### 2. Environment Variables Always
Never hardcode values that change between environments:
```json
{
  "key": "base_url",
  "value": "https://api.example.com",
  "enabled": true
}
```
Use `{{base_url}}` in requests. Environments: `dev`, `staging`, `prod`.

### 3. Pre-request Scripts for Auth
Handle authentication in pre-request scripts, not manually:
```javascript
// Get token and set for collection
pm.sendRequest({
    url: pm.environment.get("auth_url"),
    method: 'POST',
    body: { mode: 'raw', raw: JSON.stringify({...}) }
}, (err, res) => {
    pm.environment.set("token", res.json().access_token);
});
```

### 4. Test Assertions Required
Every request needs at least basic assertions:
```javascript
pm.test("Status 200", () => pm.response.to.have.status(200));
pm.test("Has data", () => pm.expect(pm.response.json()).to.have.property("data"));
```

### 5. Newman for CI/CD
Run collections headlessly with Newman:
```bash
newman run collection.json -e environment.json --reporters cli,json
```
Exit code 0 = all tests passed. Integrate into CI pipelines.

## Collection Format

### Minimal Collection
```json
{
  "info": {
    "name": "My API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Get Users",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/users",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ]
      }
    }
  ]
}
```

### With Tests
```json
{
  "name": "Create User",
  "request": {
    "method": "POST",
    "url": "{{base_url}}/users",
    "body": {
      "mode": "raw",
      "raw": "{\"name\": \"{{$randomFullName}}\", \"email\": \"{{$randomEmail}}\"}",
      "options": { "raw": { "language": "json" } }
    }
  },
  "event": [
    {
      "listen": "test",
      "script": {
        "exec": [
          "pm.test('Created', () => pm.response.to.have.status(201));",
          "pm.test('Has ID', () => pm.expect(pm.response.json().id).to.exist);"
        ]
      }
    }
  ]
}
```

## Environment Format

```json
{
  "name": "Development",
  "values": [
    { "key": "base_url", "value": "http://localhost:3000", "enabled": true },
    { "key": "token", "value": "", "enabled": true }
  ]
}
```

## Newman Commands

| Task | Command |
|------|---------|
| Basic run | `newman run collection.json` |
| With environment | `newman run collection.json -e dev.json` |
| Specific folder | `newman run collection.json --folder "Users"` |
| Iterations | `newman run collection.json -n 10` |
| Data file | `newman run collection.json -d data.csv` |
| HTML report | `newman run collection.json -r htmlextra` |
| Bail on fail | `newman run collection.json --bail` |

## Common Traps

- **Hardcoded URLs** → Tests break between environments. Always use `{{base_url}}`.
- **No assertions** → Tests "pass" but don't validate anything. Add status + body checks.
- **Secrets in collection** → Credentials leak. Use environment variables, gitignore env files.
- **Sequential dependencies** → Tests fail randomly. Use `setNextRequest()` explicitly or make tests independent.
- **Missing Content-Type** → POST/PUT fails silently. Always set `Content-Type: application/json`.

## Dynamic Variables

Postman built-in variables for test data:

| Variable | Example Output |
|----------|----------------|
| `{{$randomFullName}}` | "Jane Doe" |
| `{{$randomEmail}}` | "jane@example.com" |
| `{{$randomUUID}}` | "550e8400-e29b-..." |
| `{{$timestamp}}` | 1234567890 |
| `{{$randomInt}}` | 42 |

## OpenAPI to Postman

Import OpenAPI/Swagger specs:
1. Export OpenAPI JSON/YAML
2. In Postman: Import > File > Select spec
3. Collection auto-generated with all endpoints

Or via CLI:
```bash
npx openapi-to-postmanv2 -s openapi.yaml -o collection.json
```

## Security & Privacy

**Data that stays local:**
- Collections and environments in `~/postman/`
- Newman runs locally

**This skill does NOT:**
- Send collections to external services
- Store API credentials in memory.md

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — REST API consumption patterns
- `json` — JSON manipulation and validation
- `ci-cd` — Pipeline automation

## Feedback

- If useful: `clawhub star postman`
- Stay updated: `clawhub sync`
