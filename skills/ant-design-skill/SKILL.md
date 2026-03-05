---
name: ant_design_skill
description: Front-end design skill for building React UIs with Ant Design (antd): component patterns, layout, forms, tables, and theming/tokens via ConfigProvider.
---

# Ant Design (React) — Practical Front-end Design Skill

Use this skill when you are building a React UI with **Ant Design (antd)** and want **consistent, non-ugly** screens fast.

## When to use
- The project uses **React** + **Ant Design**
- You need to design/implement pages with: **Layout**, **Menu**, **Form**, **Table**, **Modal**, **Drawer**, **Steps**, **Tabs**, **Pagination**
- You need to implement **theme tokens** (colors, radius, typography, spacing)
- You want predictable UI patterns (CRUD screens, dashboards, settings pages)

## Default workflow (do this order)
1) Confirm stack: React + antd version (v5+ assumed).
2) Choose page pattern:
   - CRUD list (Table) + filters (Form) + actions (Modal/Drawer)
   - Wizard (Steps)
   - Settings (Form + Cards)
   - Dashboard (Grid + Cards + Charts)
3) Build layout skeleton first:
   - `Layout` + `Sider` + `Header` + `Content`
   - Navigation with `Menu`
4) Build the main interaction component:
   - Forms: `Form`, `Form.Item`, `Input`, `Select`, `DatePicker`, `Switch`
   - Tables: `Table` + column definitions + row actions
5) Add feedback loop:
   - `message`, `notification`, `Modal.confirm`
6) Apply theming/tokens via `ConfigProvider` (global) and component-level overrides.
7) Verify:
   - Empty states
   - Loading states
   - Error states
   - Mobile responsiveness (at least: 360px layout sanity)

## Component patterns (copy/paste mental models)
### Layout
- Use `Layout` with `Sider` (collapsible), `Header` for top actions, `Content` scroll.
- Put page title + primary CTA in a `Flex` (or `Space`) row.

### Forms
- Keep forms vertical; align labels consistently.
- Use `Form` + `Form.Item` rules for validation; avoid custom validation unless necessary.
- Use `Form.useForm()` and `form.setFieldsValue()` for edit flows.

### Tables (CRUD)
- Columns:
  - left: identifier/name
  - middle: important attributes
  - right: actions (Edit/Delete)
- Use `rowKey` always.
- Use server-side pagination for real apps.

### Modals/Drawers
- **Modal** for short forms.
- **Drawer** for longer forms or when you want context kept.

## Theming / Tokens (AntD v5)
Ant Design v5 uses **Design Tokens** and CSS-in-JS.

### Global theme
Wrap your app in `ConfigProvider`:

```tsx
import { ConfigProvider, theme } from 'antd';

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 10,
          fontSize: 14,
        },
        components: {
          Button: { controlHeight: 40 },
          Layout: { headerBg: '#ffffff' },
        },
      }}
    >
      {children}
    </ConfigProvider>
  );
}
```

### Dark mode
Use `theme.darkAlgorithm` and keep tokens consistent:

```tsx
const isDark = true;

<ConfigProvider
  theme={{
    algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: { colorPrimary: '#7c3aed' },
  }}
/>
```

### Component-level overrides
Use `components.<ComponentName>` for specific tweaks (Button, Input, Table, etc.).

## References
- Read **README.md** for the full “how-to” (setup + patterns + examples).
- Use `protocols/` when you want LLM-first contracts (describe UIs as data, then generate code deterministically).
- Read `references/tokens.md` for a tokens cookbook.
- Read `references/components.md` for practical page recipes (CRUD, Settings, Wizard).
- Use `examples/` when you want ready-to-copy AntD screens.
- Use `starter/` when you need a runnable Vite + React + AntD skeleton.

## Guardrails
- Assume Ant Design v5+ (tokens). If project is v4 (Less variables), stop and ask.
- Prefer built-in components and patterns over custom CSS.
- Avoid over-theming: set a small set of tokens and only override components when needed.
