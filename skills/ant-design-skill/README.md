# ant_design_skill — Ant Design skill for OpenClaw

A practical skill to help an AI agent (OpenClaw/Codex-style) build **React UIs** using **Ant Design (antd)** with:
- reliable UI patterns (CRUD, Settings, Wizard)
- consistent layout/spacing
- Ant Design v5 **Design Tokens** (global + component overrides)

Repo purpose: when you ask “make a screen with Ant Design”, the agent follows the workflow/patterns here instead of generating random ugly UI.

## What is Ant Design?
Ant Design is a React UI library with a large set of enterprise-ready components.

- Official repo: https://github.com/ant-design/ant-design
- Docs: https://ant.design/

## Installation (React)

```bash
npm i antd
```

Add antd styles (depends on your setup):

### Vite / CRA / Next.js (typical)
```ts
import 'antd/dist/reset.css';
```

> Ant Design v5 recommends `reset.css`.

## Minimal App Example

```tsx
import 'antd/dist/reset.css';
import { Button, Space, Typography } from 'antd';

export default function App() {
  return (
    <div style={{ padding: 24 }}>
      <Typography.Title level={3}>Hello AntD</Typography.Title>
      <Space>
        <Button type="primary">Primary</Button>
        <Button>Default</Button>
      </Space>
    </div>
  );
}
```

## Theming / Tokens (Ant Design v5)
AntD v5 uses **design tokens** via `ConfigProvider`.

### Global theme tokens

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
          // spacing tokens exist too (padding, margin patterns are often via layout)
        },
      }}
    >
      {children}
    </ConfigProvider>
  );
}
```

### Dark mode

```tsx
const isDark = true;

<ConfigProvider
  theme={{
    algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: { colorPrimary: '#7c3aed' },
  }}
/>
```

### Component overrides
Use `components` to customize specific components:

```tsx
<ConfigProvider
  theme={{
    token: { colorPrimary: '#1677ff' },
    components: {
      Button: {
        controlHeight: 40,
        borderRadius: 10,
      },
      Table: {
        headerBg: '#fafafa',
      },
    },
  }}
/>
```

More token examples in: `references/tokens.md`.

## Practical page recipes (what to build)

### 1) CRUD list page (Table + Filters + Actions)
Key components:
- `Form` (filters)
- `Table` (results)
- `Modal` or `Drawer` (create/edit)
- `Popconfirm` (delete)

Pattern:
- Top bar: title + primary CTA
- Filters: collapsible or inline
- Table: server pagination

### 2) Settings page
Key components:
- `Card` + `Form`
- `Switch` toggles
- `Divider` sections

### 3) Wizard
Key components:
- `Steps`
- `Form` per step

More recipes in: `references/components.md`.

## Design rules (to avoid ugly UI)
- Constrain content width for readability (e.g. `maxWidth: 1100` in content).
- Use AntD spacing primitives: `Space`, `Row/Col`, `Flex`.
- Keep forms vertical.
- Never ship without:
  - loading skeleton/spinner
  - empty state
  - error feedback (`message`/`notification`)

## Patterns

LLM-first usage patterns for common UI scenarios. Each pattern includes problem context, when to use (and not use), AntD components involved, implementation notes, accessibility guidance, and working code snippets.

| Pattern | Description |
|---------|-------------|
| [01-layout-shell](./patterns/01-layout-shell.md) | Responsive Layout with Sider/Header/Menu and collapse behavior |
| [02-navigation-menus](./patterns/02-navigation-menus.md) | Menu with URL sync, selected keys, and deep-linking |
| [03-forms](./patterns/03-forms.md) | Form validation, async submit, loading states, error handling |
| [04-data-table](./patterns/04-data-table.md) | Table with pagination, sorting, filtering, and row actions |
| [05-modal-drawer](./patterns/05-modal-drawer.md) | Modal/Drawer for forms, confirmations, and detail views |
| [06-search](./patterns/06-search.md) | Debounced search with server-side filtering and results |
| [07-notifications](./patterns/07-notifications.md) | Message/notification patterns and error handling |
| [08-upload](./patterns/08-upload.md) | File upload with progress, preview, and validation |
| [09-theming](./patterns/09-theming.md) | ConfigProvider, design tokens, light/dark mode strategy |
| [10-accessibility](./patterns/10-accessibility.md) | Focus management, ARIA labels, keyboard navigation |

## Files
- `SKILL.md` — the skill instructions used by the agent
- `protocols/` — LLM-first contracts/specs (how to describe UIs as data)
- `references/tokens.md` — tokens cookbook
- `references/components.md` — CRUD/settings/wizard recipes
- `examples/` — copy-pasteable examples for LLMs (CRUD, etc.)
- `starter/` — runnable Vite + React + AntD starter for LLMs
- `patterns/` — LLM-first UI patterns (see Patterns section above)

## License
MIT
