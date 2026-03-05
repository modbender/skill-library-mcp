# UI_SPEC (LLM-FIRST)

## PURPOSE
Define a UI as DATA. The LLM MUST generate React + Ant Design code from this spec.

## RULES (MUST)
- Treat this file as the source of truth.
- If a field is missing, DO NOT invent. Add a TODO block and stop.
- Prefer deterministic code patterns.
- Every generated screen MUST implement: loading, empty, error, success feedback.

## SPEC FORMAT
Use YAML. Keep keys stable.

```yaml
spec_version: 1
app:
  name: "YourApp"
  routing:
    strategy: "react-router"
  theme:
    default_mode: "light" # light|dark
    supports_toggle: true

entities:
  User:
    id_field: id
    fields:
      id: { type: "string", label: "ID", ui: { table: true, form: false } }
      name: { type: "string", label: "Name", ui: { table: true, form: true }, validation: { required: true, min: 2 } }
      email: { type: "string", label: "Email", ui: { table: true, form: true }, validation: { required: true, format: "email" } }
      status: { type: "enum", label: "Status", enum: ["active","inactive"], ui: { table: true, form: true } }

pages:
  - id: "users.list"
    kind: "crud"
    entity: "User"
    title: "Users"
    route: "/users"
    layout: "app"

    datasource:
      kind: "server"
      operations:
        list: { method: "GET", path: "/api/users" }
        create: { method: "POST", path: "/api/users" }
        update: { method: "PUT", path: "/api/users/:id" }
        delete: { method: "DELETE", path: "/api/users/:id" }

    crud:
      list:
        pagination: { mode: "server", page_param: "page", page_size_param: "pageSize" }
        sorting: { mode: "server", sort_param: "sort", order_param: "order" }
        filters:
          - { field: "q", type: "string", label: "Search" }
          - { field: "status", type: "enum", label: "Status", enum: ["active","inactive"] }

      form:
        mode: "drawer" # drawer|modal|page
        fields_order: ["name","email","status"]

      permissions:
        can_read: true
        can_create: true
        can_update: true
        can_delete: true

contracts:
  api:
    list_response:
      items_key: "items"   # e.g. { items: [], total: 123 }
      total_key: "total"
      id_key: "id"

  ui:
    notifications:
      success: "antd.message"
      error: "antd.notification"

notes:
  - "Add more pages and entities as needed"
```

## REQUIRED OUTPUTS (when generating code)
The LLM MUST output:
- File tree
- Each file content
- Exact imports (no pseudo-imports)
- No omitted code sections

## VALIDATION CHECKLIST (MUST)
- [ ] No missing keys vs spec
- [ ] All CRUD operations wired
- [ ] Server pagination + filters implemented
- [ ] Loading/empty/error states
- [ ] Form validation matches spec
- [ ] Success and error notifications
