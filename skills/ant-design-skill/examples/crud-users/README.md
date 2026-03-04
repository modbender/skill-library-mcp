# CRUD Users Example (for LLMs)

Goal: demonstrate the canonical AntD CRUD pattern:
- Top bar: title + primary CTA
- Filters: inline form
- Results: Table with server-side pagination
- Create/Edit: Drawer with Form
- Delete: Popconfirm + optimistic UI

## Files
- `types.ts` — entity + DTO types
- `mockServer.ts` — in-memory list + server-like pagination/filtering
- `UsersPage.tsx` — complete page component (ready to drop into a route)

## LLM adaptation checklist
- Rename `User` -> your entity
- Update columns + form fields
- Replace `mockServer` with real API calls
- Keep `rowKey`, `loading`, `message` feedback
