# Atlas Tracker Node Types Guide

## Property Types

| typeId     | Value format                        | Notes                              |
|------------|-------------------------------------|------------------------------------|
| htmltext   | HTML string `<p>text</p>`           | Rich text; use `<ul><li>` for lists |
| text       | Plain string                        | No HTML                            |
| enum       | One of the `icons[]` values exactly | Must match exactly — case sensitive |
| integer    | Integer or one of `icons[]` strings | Icons = allowed values if set      |
| real       | Numeric string `"3.5"`              | Decimal number                     |
| boolean    | `true` or `false`                   |                                    |
| date       | `"YYYY-MM-DD"`                      |                                    |
| datetime   | ISO string                          |                                    |
| user       | User email string                   | Must be a valid map member email   |
| file       | JSON string (managed by AT)         | Don't set manually                 |

## Setting typeProperties

`typeProperties` is a flat object: `{"Property Name": "value"}`.

Keys must **exactly match** property names returned by `at_get_node_types`. Example:
```json
{
  "typeProperties": {
    "Суть идеи": "<p>Description here</p>",
    "Статус": "В работе",
    "Исполнитель": "user@example.com"
  }
}
```

## Getting Type IDs

Call `at_get_node_types(nodeUrl)` once per map. Returns array of:
```json
{
  "id": "29f81dd5-...",
  "name": "Идея",
  "properties": [
    {"typeId": "htmltext", "name": "Суть идеи", ...},
    {"typeId": "enum", "name": "Статус", "icons": ["Предложена", "Тестируется", ...]}
  ]
}
```

Use `id` as `typeId` when creating nodes.

## Common Node Types (vary per map)

- **Категория** — container/folder, no special properties
- **Идея** — idea node; typically has Суть идеи (htmltext), Назначение (htmltext), Примечание (htmltext)
- **Задача** — task; has Статус (enum), Исполнитель (user), Трудозатраты (real)
- **Заметка** — note; has Содержимое (htmltext)
- **Проект** — project; has Статус (enum)
- **Заявка / Лид** — CRM-style nodes with sales pipeline properties

## Untyped Nodes

Omit `typeId` (or set to `null`) for plain nodes with no schema. They can still have `customProperties`:
```json
{
  "customProperties": [
    {"name": "My field", "value": "some value", "type": "htmltext"}
  ]
}
```
