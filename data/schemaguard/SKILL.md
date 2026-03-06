---
name: schemaguard
description: Detect breaking changes in OpenAPI specs. Use when reviewing API changes, validating PRs that modify API specs, checking backward compatibility, or linting OpenAPI spec quality. Provides diff, lint, and CI check tools.
metadata:
  clawdbot:
    requires:
      bins: ["npx"]
---

# SchemGuard — API Schema Drift Monitor

## Quick Start

```bash
# Diff two specs (breaking vs non-breaking)
npx @sethclawd/schemaguard diff old.yaml new.yaml

# CI check (exit 0=safe, 1=breaking, 2=error)
npx @sethclawd/schemaguard ci --spec ./openapi.yaml --baseline ./baseline.yaml

# Lint spec quality
npx @sethclawd/schemaguard lint ./openapi.yaml

# JSON output for programmatic use
npx @sethclawd/schemaguard diff old.yaml new.yaml --format json
```

## When to Use

- Before committing changes to an OpenAPI spec
- When reviewing PRs that modify API routes
- After generating/updating OpenAPI specs from code
- Before deploying API changes to production
- Validating that a migration maintains backward compatibility

## Breaking Changes Detected

| Rule | What It Catches |
|------|----------------|
| `endpoint-removed` | Deleted endpoints |
| `required-param-added` | New required parameters |
| `field-type-changed` | Changed field types |
| `response-field-removed` | Removed response fields |
| `enum-value-removed` | Narrowed enums |
| `auth-requirement-changed` | Changed security schemes |

## Non-Breaking (Info Only)

Added endpoints, optional params, response fields, widened enums, deprecations.

## MCP Server

For direct tool integration:
```bash
npx @sethclawd/schemaguard --mcp
```

Exposes: `schemaguard_diff`, `schemaguard_lint`, `schemaguard_check`
