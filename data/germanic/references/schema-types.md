# GERMANIC Schema Types

## Supported Field Types

| Type       | JSON Value       | FlatBuffer    | Example                   |
|------------|------------------|---------------|---------------------------|
| `string`   | `"text"`         | string offset | `"Dr. Anna Schmidt"`      |
| `bool`     | `true`/`false`   | bool (1 byte) | `true`                    |
| `int`      | `42`             | int32         | `450`                     |
| `float`    | `3.14`           | float32       | `4.8`                     |
| `[string]` | `["a", "b"]`     | string vector | `["Chirurgie", "Innere"]` |
| `[int]`    | `[1, 2, 3]`      | int32 vector  | `[100, 200, 300]`         |
| `table`    | `{ "key": ... }` | nested table  | `{ "strasse": "..." }`    |

## Schema-ID Convention

Format: `{locale}.{domain}.{name}.v{version}`

Examples:
- `de.gesundheit.praxis.v1` — German healthcare practice
- `en.dining.restaurant.v1` — English restaurant
- `com.example.product.v1` — Custom product schema

## Nesting

Tables can contain tables. Validation is recursive:

```json
{
  "schema_id": "example.nested.v1",
  "version": 1,
  "fields": {
    "name": { "type": "string", "required": true },
    "address": {
      "type": "table",
      "required": true,
      "fields": {
        "street": { "type": "string", "required": true },
        "city":   { "type": "string", "required": true },
        "zip":    { "type": "string", "required": true }
      }
    }
  }
}
```

## Required vs Optional

- `"required": true` — field MUST be present AND non-empty
- `"required": false` (default) — field may be absent or null
- Empty string `""` on a required field -> error
- `null` on a required field -> error

## Defaults

```json
{ "type": "string", "default": "DE" }
{ "type": "bool",   "default": "true" }
{ "type": "int",    "default": "0" }
```

Default values are used when the field is absent from input JSON.
