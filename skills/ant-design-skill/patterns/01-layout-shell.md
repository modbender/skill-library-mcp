# Pattern: Layout Shell (Layout/Sider/Header/Menu)

## Problem / Context

Building a consistent application shell with navigation, header branding, and responsive behavior is a common requirement in admin dashboards and SaaS applications. Getting the layout structure right early prevents refactoring later.

## When to Use

- Admin dashboards with side navigation
- SaaS applications requiring consistent navigation structure
- Applications needing responsive collapse behavior on mobile

## When NOT to Use

- Simple landing pages (overkill)
- Single-page apps without navigation
- Mobile-first apps (prefer bottom navigation)

## AntD Components Involved

- `Layout` - Container component
- `Layout.Sider` - Collapsible sidebar
- `Layout.Header` - Top header bar
- `Layout.Content` - Main content area
- `Menu` - Navigation items

## React Implementation Notes

### State Management

```tsx
const [collapsed, setCollapsed] = useState(false);
const [mobileOpen, setMobileOpen] = useState(false);
const { token } = theme.useToken();
```

### Responsive Breakpoints

```tsx
const isMobile = useMediaQuery({ maxWidth: 768 });

// Auto-collapse on mobile
useEffect(() => {
  if (isMobile) setCollapsed(true);
}, [isMobile]);
```

### Composition Pattern

```tsx
<Layout style={{ minHeight: '100vh' }}>
  <Sider
    breakpoint="lg"
    collapsedWidth={isMobile ? 0 : 80}
    collapsible
    collapsed={collapsed}
    onCollapse={setCollapsed}
    trigger={null}
  >
    <div className="logo" />
    <Menu items={menuItems} mode="inline" />
  </Sider>
  <Layout>
    <Header style={{ padding: 0, background: token.colorBgContainer }}>
      <Button icon={collapsed ? <MenuUnfold /> : <MenuFold />} 
              onClick={() => setCollapsed(!collapsed)} />
    </Header>
    <Content style={{ margin: '24px 16px' }}>
      {children}
    </Content>
  </Layout>
</Layout>
```

## Accessibility / Keyboard

- Ensure Sider has `role="navigation"` when containing menu
- Focus trap mobile drawer when open
- Keyboard shortcut (e.g., `Cmd+\`) to toggle sidebar
- Skip link to main content for screen readers

## Do / Don't

**Do:**
- Keep Sider width consistent (200-256px standard)
- Use consistent collapse behavior across pages
- Persist collapse state in localStorage
- Show overlay on mobile when drawer is open

**Don't:**
- Nest multiple Layout.Sider components
- Put scrollable content directly in Header
- Use different breakpoint values on different pages

## Minimal Code Snippet

```tsx
import { Layout, Menu, Button } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { useState } from 'react';

const { Header, Sider, Content } = Layout;

function AppShell() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div className="logo" />
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['1']}
          items={[
            { key: '1', icon: <UserOutlined />, label: 'nav 1' },
            { key: '2', icon: <VideoCameraOutlined />, label: 'nav 2' },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: '#fff' }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24 }}>
          Content goes here
        </Content>
      </Layout>
    </Layout>
  );
}
```
