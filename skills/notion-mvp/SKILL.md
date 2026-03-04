---
name: notion-mvp
description: Create and list Notion tasks in a single database via Notion API. Use when the user asks to add tasks, list today tasks, or capture quick todos in Notion from chat.
---

# notion-mvp

Use this skill to write/read tasks across multiple Notion databases (aliases).

## Required env vars

- `NOTION_TOKEN` (integration token, `secret_...`)
- one of:
  - `NOTION_DATABASE_MAP` (JSON map alias -> database_id)
  - `NOTION_DATABASE_ID` (fallback default database)

Example `NOTION_DATABASE_MAP`:

```json
{"agenda":"db_id_1","tarefas":"db_id_2","crm":"db_id_3"}
```

## Command wrapper

Run:

```bash
bash {baseDir}/scripts/notion_mvp.sh <command> [args]
```

Commands:

- `add <alias> "<bloco>" [YYYY-MM-DD] [HH:MM] ["<local>"]` → create an item
  - defaults: `data=today`, `hora=09:00`, `local=""`
- `today <alias>` → list items with `Data = today`
- `query <alias> "<text>"` → search items by `Bloco` contains text
- `aliases` → list configured aliases

## Expected database properties

This skill expects these Notion properties in each target database:

- `Bloco` (title)
- `Data` (rich_text/text)
- `Hora` (rich_text)
- `Local` (rich_text)

## Usage pattern

1. Validate env vars and fail with clear message if missing.
2. Resolve the correct database alias (`agenda`, `tarefas`, etc.).
3. For schedule capture requests, call `add` with alias + Bloco/Data/Hora/Local.
4. For “hoje” / “today” requests, call `today <alias>`.
5. Return a concise summary after command output.

## Examples

```bash
bash {baseDir}/scripts/notion_mvp.sh aliases
bash {baseDir}/scripts/notion_mvp.sh add agenda "Ligar para dermatologista" 2026-02-14 10:00 "Barra"
bash {baseDir}/scripts/notion_mvp.sh add tarefas "Consertar tela do celular" 2026-02-14 15:30 "Centro"
bash {baseDir}/scripts/notion_mvp.sh today agenda
bash {baseDir}/scripts/notion_mvp.sh query agenda "dermatologista"
```
