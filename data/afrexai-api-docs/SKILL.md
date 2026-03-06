---
name: API Documentation Generator
description: Generate production-ready API documentation from endpoint
  descriptions. Outputs OpenAPI 3.0, markdown reference docs, and SDK quickstart
  guides.
---

# API Documentation Generator

Generate production-ready API documentation from endpoint descriptions. Outputs OpenAPI 3.0, markdown reference docs, and SDK quickstart guides.

## Usage

Describe your API endpoints and this skill generates:

1. **OpenAPI 3.0 spec** — machine-readable, import into Swagger/Postman
2. **Markdown reference** — human-readable endpoint docs with examples
3. **SDK quickstart** — copy-paste integration guide for developers

## Instructions

When the user describes API endpoints (routes, methods, parameters, responses):

1. Generate a complete OpenAPI 3.0 YAML specification
2. Create markdown documentation with:
   - Authentication section
   - Each endpoint: method, path, description, parameters table, request/response examples
   - Error codes reference
   - Rate limiting notes
3. Generate a quickstart guide with curl examples and common language snippets (Python, JavaScript, Go)

### Output Format

```yaml
# openapi.yaml — full OpenAPI 3.0 spec
```

```markdown
# API Reference — human-readable docs
```

```markdown
# Quickstart Guide — integration examples
```

### Quality Standards
- Every endpoint must have request AND response examples
- Use realistic sample data, not "string" or "example"
- Include error responses (400, 401, 403, 404, 500)
- Document pagination, filtering, and sorting patterns
- Note breaking changes and versioning strategy

## Tips
- Paste your route files or controller code for automatic extraction
- Works with REST, GraphQL (schema-first), and gRPC (proto-first)
- Combine with CI/CD to auto-generate docs on every deploy

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI-powered business tools for teams that ship fast.
