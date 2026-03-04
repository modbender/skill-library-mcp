# Pattern: Theming

## Problem / Context

Applications need consistent visual design across light/dark modes, brand customization, and component variants. Without proper theming, maintaining consistency becomes unmaintainable.

## When to Use

- Light/dark mode support
- White-label applications
- Brand customization
- Design system implementations

## When NOT to Use

- Single-theme apps with default AntD
- Rapid prototypes (use defaults)
- Apps without design system requirements

## AntD Components Involved

- `ConfigProvider` - Theme configuration
- `theme` - Token utilities (useToken, algorithm)
- CSS variables for runtime theming

## React Implementation Notes

### ConfigProvider Setup

```tsx
import { ConfigProvider, theme } from 'antd';

function App() {
  const [isDark, setIsDark] = useState(false);

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <YourApp />
    </ConfigProvider>
  );
}
```

### Custom Tokens

```tsx
const customTheme = {
  token: {
    colorPrimary: '#722ed1',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    fontSize: 14,
    borderRadius: 8,
    wireframe: false, // Rounded vs squared
  },
};
```

### Using Theme Tokens

```tsx
import { theme } from 'antd';

function MyComponent() {
  const { token } = theme.useToken();

  return (
    <div style={{ 
      background: token.colorBgContainer,
      color: token.colorText,
      padding: token.padding,
    }}>
      Content
    </div>
  );
}
```

### Theme Toggle Pattern

```tsx
const ThemeToggle = () => {
  const [isDark, setIsDark] = useState(() => 
    localStorage.getItem('theme') === 'dark'
  );

  useEffect(() => {
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  return (
    <Switch
      checked={isDark}
      onChange={setIsDark}
      checkedChildren="🌙"
      unCheckedChildren="☀️"
    />
  );
};
```

## Accessibility / Keyboard

- Ensure sufficient contrast ratios
- Don't rely on color alone for meaning
- Respect user `prefers-color-scheme`
- Test focus indicators in both modes

## Do / Don't

**Do:**
- Use design tokens consistently
- Test in both light and dark modes
- Store user preference
- Extend rather than override AntD defaults

**Don't:**
- Hardcode colors outside theme system
- Forget to test contrast ratios
- Use too many custom colors
- Ignore system preference

## Minimal Code Snippet

```tsx
import { ConfigProvider, theme, Button, Switch } from 'antd';
import { useState } from 'react';

function ThemedApp() {
  const [isDark, setIsDark] = useState(false);

  return (
    <ConfigProvider
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: { colorPrimary: '#722ed1' },
      }}
    >
      <div style={{ padding: 24 }}>
        <Switch
          checked={isDark}
          onChange={setIsDark}
          checkedChildren="🌙"
          unCheckedChildren="☀️"
        />
        <Button type="primary" style={{ marginLeft: 16 }}>
          Primary Button
        </Button>
      </div>
    </ConfigProvider>
  );
}
```
