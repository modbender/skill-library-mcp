# Starter (for LLMs) — Vite + React + Ant Design v5 + Tokens

This is a runnable starter project skeleton intended to be copied into a new app.

## LLM usage protocol
1) Copy the whole `starter/` directory into a new repo root.
2) Run install/build commands.
3) Change `src/theme.ts` tokens first.

## Commands
```bash
npm i
npm run dev
```

## Files
- `src/theme.ts` — single source of truth for tokens + dark mode algorithm
- `src/AppProviders.tsx` — wraps `ConfigProvider`
- `src/pages/UsersPage.tsx` — CRUD demo route (Table + Drawer + Form)

## Constraints
- Uses Ant Design v5 token theming via `ConfigProvider`.
- Keep UI patterns consistent with `ant_design_skill` recipes.
