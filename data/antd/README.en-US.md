# Ant Design Components

Complete guide for AI assistants to use Ant Design component library. AI can use Ant Design to build UI in any React project.

## Quick Start

### Installation

```bash
npm install antd @ant-design/icons
# or
yarn add antd @ant-design/icons
```

### Import Styles

```javascript
import 'antd/dist/reset.css';
```

### Use Components

```javascript
import { Button } from 'antd';

<Button type="primary">Button</Button>
```

## Core Components

### Button

```javascript
import { Button } from 'antd';

// Types
<Button>Default</Button>
<Button type="primary">Primary</Button>
<Button type="dashed">Dashed</Button>
<Button type="text">Text</Button>
<Button danger>Danger</Button>

// States
<Button loading>Loading</Button>
<Button disabled>Disabled</Button>
<Button size="small">Small</Button>
```

### Form

```javascript
import { Form, Input, Button } from 'antd';

<Form onFinish={handleSubmit}>
  <Form.Item 
    name="username" 
    label="Username"
    rules={[{ required: true, message: 'Please input username!' }]}
  >
    <Input placeholder="Please input username" />
  </Form.Item>
  
  <Button type="primary" htmlType="submit">Submit</Button>
</Form>
```

### Table

```javascript
import { Table, Tag } from 'antd';

const columns = [
  { title: 'Name', dataIndex: 'name' },
  { title: 'Age', dataIndex: 'age' },
  { 
    title: 'Status', 
    dataIndex: 'status',
    render: (status) => (
      <Tag color={status === 'active' ? 'green' : 'red'}>
        {status === 'active' ? 'Active' : 'Inactive'}
      </Tag>
    )
  },
];

<Table dataSource={data} columns={columns} rowKey="id" />
```

### Modal

```javascript
import { Modal, Button } from 'antd';

const [open, setOpen] = useState(false);

<Button onClick={() => setOpen(true)}>Open</Button>

<Modal
  title="Title"
  open={open}
  onOk={() => setOpen(false)}
  onCancel={() => setOpen(false)}
>
  Content
</Modal>
```

## Component Categories

| Category | Components |
|----------|------------|
| General | Button, Icon, Typography, Space, Divider |
| Navigation | Menu, Tabs, Breadcrumb, Dropdown, Pagination, Steps |
| Data Entry | Form, Input, Select, Radio, Checkbox, DatePicker, Upload, Switch |
| Data Display | Table, Card, List, Tree, Badge, Tag, Timeline, Avatar |
| Feedback | Modal, Message, Notification, Result, Progress, Spin, Alert |
| Layout | Layout, Row, Col, Grid |

## Best Practices

1. **Form Validation** - Use Form.Item rules property
2. **Responsive** - Use Grid system (Row/Col)
3. **Theme Customization** - Use ConfigProvider
4. **Internationalization** - Configure LocaleProvider
5. **On-demand Loading** - Use babel-plugin-import

## Theme Customization

```javascript
import { ConfigProvider } from 'antd';

<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
    },
  }}
>
  <App />
</ConfigProvider>
```

## Resources

- Official Docs: https://ant.design
- Components Overview: https://ant.design/components/overview
- Icons: https://ant.design/components/icon
- GitHub: https://github.com/ant-design/ant-design
