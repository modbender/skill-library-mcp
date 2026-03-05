# DECISIONS (LLM-FIRST)

## PURPOSE
Hard rules that keep generated Ant Design UIs consistent across pages.

## GLOBAL RULES (MUST)
1) React + TypeScript only.
2) Ant Design v5.
3) Prefer `antd` primitives over custom UI.
4) All API calls go through ONE wrapper (`apiClient`).
5) No silent failures. Every failure triggers a UI error surface.
6) No uncontrolled forms.

## STATE + DATA RULES
- Use React Query (preferred) OR a single local state pattern, but be consistent in one project.
- For lists: server pagination by default.
- For mutations: show optimistic UI ONLY if explicitly requested.

## CRUD CANONICAL PATTERN
- List page = Filters + Table + Actions.
- Create/Edit = Drawer with Form.
- Delete = Popconfirm.

## UX RULES
- Loading:
  - list: show table loading state + disable actions
  - form submit: show button loading + prevent double submit
- Empty state:
  - show `Empty` component, keep filters visible
- Errors:
  - list load error => `Alert` with retry
  - mutation error => `notification.error`
- Success:
  - mutation success => `message.success`

## ROUTING + LAYOUT RULES
- Layout: `Layout` with `Sider` + `Header` + `Content`.
- Page padding: 24.
- Page header: title + primary action on the right.

## THEMING RULES
- Use `ConfigProvider`.
- Support light/dark toggle if starter has it.
- Use tokens (no hard-coded colors unless in tokens).

## SECURITY / RBAC RULES
- If RBAC is enabled:
  - Menu items are derived from permissions.
  - Route guard redirects to a stable "not authorized" page.

## DO NOT DO (MUST NOT)
- Do not commit `node_modules/`.
- Do not commit build output (`dist/`).
- Do not mention "LLM" in user-facing UI copy.
