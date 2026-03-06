# Pattern: Navigation Menus

## Problem / Context

Navigation menus need to stay in sync with the current URL, handle nested routes, and provide visual feedback for the active location. Without proper key management, menus lose state on refresh or fail to highlight the correct item.

## When to Use

- Side navigation in dashboards
- Top navigation bars
- Hierarchical navigation with nested items
- Breadcrumb companion navigation

## When NOT to Use

- Single-level navigation (simpler solutions exist)
- Navigation that changes based on user actions
- Context menus (use Dropdown instead)

## AntD Components Involved

- `Menu` - Main navigation component
- `Menu.Item` / `Menu.SubMenu` - Navigation items
- `Badge` - For notification counts

## React Implementation Notes

### URL Sync Pattern

```tsx
import { useLocation, useNavigate } from 'react-router-dom';

function Navigation() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Map paths to menu keys
  const selectedKeys = useMemo(() => {
    const path = location.pathname;
    if (path.startsWith('/users')) return ['users'];
    if (path.startsWith('/settings')) return ['settings'];
    return ['dashboard'];
  }, [location]);

  return (
    <Menu
      selectedKeys={selectedKeys}
      onClick={({ key }) => navigate(key)}
      items={menuItems}
    />
  );
}
```

### Nested Menu Structure

```tsx
const items: MenuItem[] = [
  {
    key: 'dashboard',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
  },
  {
    key: 'users',
    icon: <UserOutlined />,
    label: 'Users',
    children: [
      { key: 'users/list', label: 'All Users' },
      { key: 'users/roles', label: 'Roles' },
    ],
  },
];
```

### Open Keys Management

```tsx
const [openKeys, setOpenKeys] = useState<string[]>([]);

// Auto-expand parent based on current route
useEffect(() => {
  if (location.pathname.startsWith('/users')) {
    setOpenKeys(['users']);
  }
}, [location.pathname]);
```

## Accessibility / Keyboard

- Menu has proper `role="menu"` attributes
- Arrow keys navigate between items
- Enter/Space activates items
- Escape closes submenus

## Do / Don't

**Do:**
- Keep menu depth to 2 levels maximum
- Use consistent icon sizing
- Highlight parent when child is active
- Persist open state in URL or state

**Don't:**
- Mix navigation patterns (top + side inconsistently)
- Use click to expand on hover menus
- Put actions (buttons) inside menu items

## Minimal Code Snippet

```tsx
import { Menu } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import { DashboardOutlined, UserOutlined } from '@ant-design/icons';

function NavigationMenu() {
  const location = useLocation();
  const navigate = useNavigate();

  const items = [
    { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
    { 
      key: 'users', 
      icon: <UserOutlined />, 
      label: 'Users',
      children: [
        { key: '/users', label: 'List' },
        { key: '/users/new', label: 'Create' },
      ]
    },
  ];

  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      defaultOpenKeys={['users']}
      items={items}
      onClick={({ key }) => navigate(key)}
    />
  );
}
```
