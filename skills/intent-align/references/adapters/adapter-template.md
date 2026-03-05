# Adapter Template (Required for Ad-Hoc Adapters)

Use this template whenever an adapter is missing for a required capability.

```yaml
adapter_spec:
  id: string
  description: string
  capabilities: [string]

  auth:
    required: true|false
    method: token|session|filesystem|none|other
    scopes_or_permissions: [string]
    detection: string

  inputs:
    required: [string]
    optional: [string]

  outputs:
    result_schema:
      status: ok|partial|failed
      references: [string]
      notes: string

  failure_modes:
    - mode: string
      detection: string
      behavior: string

  fallbacks:
    - when: string
      action: string

  provenance:
    created_by: user|agent
    created_at: iso-8601
    environment_assumptions: [string]
    tool_access_required: [string]
```

## Minimal Validation Checklist
- `id` exists and is unique in current hub scope.
- At least one capability is declared.
- `auth` contains requirement + detection method.
- `inputs` and `outputs.result_schema` are defined.
- At least one failure mode and one fallback exist.
- `provenance` fields are complete.
- Adapter is registered in hub `adapters` and referenced by `capability_matrix.adapters_selected`.
