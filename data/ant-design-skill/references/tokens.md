# Ant Design v5 Tokens Cookbook

Ant Design v5 theme is built on **design tokens**.

## 1) Where tokens live
- Global: `ConfigProvider theme.token`
- Per-component: `ConfigProvider theme.components.<ComponentName>`

```tsx
<ConfigProvider
  theme={{
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
/>
```

## 2) Tokens you usually want first (pragmatic)
Start small. In 80% of apps, these are enough:
- `colorPrimary`
- `colorSuccess`, `colorWarning`, `colorError` (optional)
- `borderRadius`
- `fontFamily`, `fontSize`

## 3) Dark mode
Use algorithm + keep your brand `colorPrimary`:

```tsx
import { theme } from 'antd';

const isDark = true;

<ConfigProvider
  theme={{
    algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
    token: { colorPrimary: '#7c3aed' },
  }}
/>
```

## 4) Component overrides examples

### Button
```tsx
components: {
  Button: {
    controlHeight: 40,
    borderRadius: 10,
  },
}
```

### Table
```tsx
components: {
  Table: {
    headerBg: '#fafafa',
    headerColor: '#111827',
    rowHoverBg: '#f3f4f6',
  },
}
```

### Layout
```tsx
components: {
  Layout: {
    headerBg: '#ffffff',
    siderBg: '#0b1220',
    bodyBg: '#f7f8fa',
  },
}
```

## 5) Old AntD v4 theming (Less variables)
If you find docs about `modifyVars` / Less variables, that's mainly AntD v4 era.
For v5, prefer `ConfigProvider` tokens.

If the project is v4, stop and decide:
- upgrade to v5
- or keep v4 theming via Less (webpack/vite plugin)
