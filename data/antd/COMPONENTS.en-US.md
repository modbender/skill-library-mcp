# Ant Design Components Reference

## General Components

### Button

```javascript
import { Button } from 'antd';

// Types
<Button type="primary">Primary</Button>
<Button type="secondary">Secondary</Button>
<Button type="dashed">Dashed</Button>
<Button type="text">Text</Button>
<Button type="link">Link</Button>

// States
<Button loading>Loading</Button>
<Button disabled>Disabled</Button>

// Sizes
<Button size="small">Small</Button>
<Button size="large">Large</Button>

// Danger
<Button danger>Danger</Button>

// Icon
<Button icon={<SearchOutlined />}>Search</Button>
```

### Typography

```javascript
import { Typography } from 'antd';

const { Title, Paragraph, Text, Link } = Typography;

<Title>Title</Title>
<Title level={2}>Heading 2</Title>
<Paragraph>Paragraph</Paragraph>
<Text>Text</Text>
<Text type="secondary">Secondary text</Text>
<Text mark>Marked</Text>
<Text code>Code</Text>
<Link href="#">Link</Link>
```

### Icon

```javascript
import { HomeOutlined, SettingFilled } from '@ant-design/icons';

<HomeOutlined />
<SettingFilled />
<HomeOutlined style={{ color: '#1890ff', fontSize: 24 }} />
```

---

## Form Components

### Input

```javascript
import { Input } from 'antd';

// Basic
<Input placeholder="Please input" />

// TextArea
<Input.TextArea rows={4} />

// Password
<Input.Password placeholder="Password" />

// Search
<Input.Search placeholder="Search" onSearch={handleSearch} />

// With prefix/suffix
<Input prefix={<UserOutlined />} suffix={<InfoCircleOutlined />} />

// Disabled/ReadOnly
<Input disabled />
<Input readOnly />
```

### Select

```javascript
import { Select } from 'antd';

const { Option } = Select;

// Single select
<Select placeholder="Please select" style={{ width: 200 }}>
  <Option value="1">Option 1</Option>
  <Option value="2">Option 2</Option>
</Select>

// Multiple select
<Select mode="multiple" placeholder="Please select">
  <Option value="1">Option 1</Option>
</Select>

// With search
<Select showSearch placeholder="Search options">
  <Option value="1">Option 1</Option>
</Select>

// Disabled
<Select disabled />
```

### Radio

```javascript
import { Radio } from 'antd';

// Radio Group
<Radio.Group>
  <Radio value={1}>Option 1</Radio>
  <Radio value={2}>Option 2</Radio>
</Radio.Group>

// Button style
<Radio.Group buttonStyle="solid">
  <Radio.Button value="large">Large</Radio.Button>
  <Radio.Button value="middle">Middle</Radio.Button>
</Radio.Group>
```

### Checkbox

```javascript
import { Checkbox } from 'antd';

// Single
<Checkbox>Option</Checkbox>

// Group
<Checkbox.Group>
  <Checkbox value="1">Option 1</Checkbox>
  <Checkbox value="2">Option 2</Checkbox>
</Checkbox.Group>

// Check all
const [checkedList, setCheckedList] = useState([]);

<Checkbox
  indeterminate={indeterminate}
  onChange={onCheckAllChange}
  checked={checkAll}
>
  Check all
</Checkbox>
```

### DatePicker

```javascript
import { DatePicker } from 'antd';

// Date
<DatePicker placeholder="Select date" />

// Date range
<DatePicker.RangePicker />

// With time
<DatePicker showTime placeholder="Select date time" />

// Month
<DatePicker picker="month" />

// Year
<DatePicker picker="year" />
```

### Form

```javascript
import { Form, Input, Button, Select } from 'antd';

const [form] = Form.useForm();

<Form
  form={form}
  layout="vertical"
  onFinish={handleSubmit}
  initialValues={{ name: 'Default' }}
>
  <Form.Item
    name="username"
    label="Username"
    rules={[
      { required: true, message: 'Please input username!' },
      { min: 3, message: 'At least 3 characters!' }
    ]}
  >
    <Input />
  </Form.Item>
  
  <Form.Item
    name="email"
    label="Email"
    rules={[
      { type: 'email', message: 'Invalid email!' }
    ]}
  >
    <Input />
  </Form.Item>
  
  <Button type="primary" htmlType="submit">Submit</Button>
  <Button onClick={() => form.resetFields()}>Reset</Button>
</Form>
```

---

## Data Display Components

### Table

```javascript
import { Table, Space, Tag, Button } from 'antd';

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    sorter: (a, b) => a.name.localeCompare(b.name),
  },
  {
    title: 'Age',
    dataIndex: 'age',
    key: 'age',
  },
  {
    title: 'Status',
    dataIndex: 'status',
    render: (status) => (
      <Tag color={status === 'active' ? 'green' : 'red'}>
        {status === 'active' ? 'Active' : 'Inactive'}
      </Tag>
    ),
  },
  {
    title: 'Action',
    render: (_, record) => (
      <Space>
        <Button type="link">Edit</Button>
        <Button type="link" danger>Delete</Button>
      </Space>
    ),
  },
];

<Table
  dataSource={data}
  columns={columns}
  rowKey="id"
  pagination={{ pageSize: 10, showSizeChanger: true }}
  loading={loading}
  bordered
/>
```

### Card

```javascript
import { Card, Avatar } from 'antd';

// Basic
<Card title="Title">Content</Card>

// With actions
<Card
  title="Title"
  extra={<a href="#">More</a>}
  actions={[
    <SettingOutlined key="setting" />,
    <EditOutlined key="edit" />,
  ]}
>
  Content
</Card>

// Hoverable
<Card hoverable cover={<img alt="cover" src="..." />}>
  Content
</Card>

// Statistic Card
<Card>
  <Statistic title="Users" value={1268} />
</Card>
```

### List

```javascript
import { List, Avatar } from 'antd';

<List
  itemLayout="horizontal"
  dataSource={data}
  renderItem={(item) => (
    <List.Item actions={[<a key="edit">Edit</a>]}>
      <List.Item.Meta
        avatar={<Avatar src={item.avatar} />}
        title={<a href="#">{item.title}</a>}
        description={item.description}
      />
    </List.Item>
  )}
/>
```

### Badge

```javascript
import { Badge } from 'antd';

<Badge count={5}>
  <div>Content</div>
</Badge>

<Badge count={100} overflowCount={99}>
  <div>Content</div>
</Badge>

<Badge dot>
  <div>Dot</div>
</Badge>
```

### Tag

```javascript
import { Tag } from 'antd';

<Tag>Default</Tag>
<Tag color="red">Red</Tag>
<Tag color="green">Green</Tag>
<Tag color="blue">Blue</Tag>

// Closable
<Tag closable onClose={handleClose}>Closable</Tag>
```

---

## Feedback Components

### Modal

```javascript
import { Modal, Button } from 'antd';

const [open, setOpen] = useState(false);

// Basic
<Modal
  title="Title"
  open={open}
  onOk={handleOk}
  onCancel={handleCancel}
>
  Content
</Modal>

// Confirm
Modal.confirm({
  title: 'Are you sure?',
  onOk: handleDelete,
});

// Success
Modal.success({ title: 'Success' });

// Error
Modal.error({ title: 'Error' });
```

### Message

```javascript
import { message } from 'antd';

message.success('Success');
message.error('Error');
message.warning('Warning');
message.info('Info');
message.loading('Loading...', 2);
```

### Notification

```javascript
import { notification } from 'antd';

notification.success({
  message: 'Notification Title',
  description: 'Notification description content',
  duration: 4.5,
});

notification.error({
  message: 'Error',
  description: 'Error details',
});
```

### Spin

```javascript
import { Spin } from 'antd';

// Basic
<Spin />

// With tip
<Spin tip="Loading..." />

// Sizes
<Spin size="small" />
<Spin size="large" />

// Wrap content
<Spin spinning={loading}>
  <Content />
</Spin>
```

---

## Navigation Components

### Menu

```javascript
import { Menu } from 'antd';

// Horizontal
<Menu mode="horizontal" selectedKeys={['1']}>
  <Menu.Item key="1">Navigation 1</Menu.Item>
  <Menu.Item key="2">Navigation 2</Menu.Item>
</Menu>

// Vertical
<Menu mode="vertical" selectedKeys={['1']}>
  <Menu.Item key="1">Menu 1</Menu.Item>
  <Menu.SubMenu title="Sub Menu">
    <Menu.Item key="3">Option 1</Menu.Item>
  </Menu.SubMenu>
</Menu>
```

### Tabs

```javascript
import { Tabs } from 'antd';

<Tabs>
  <Tabs.TabPane tab="Tab 1" key="1">Content 1</Tabs.TabPane>
  <Tabs.TabPane tab="Tab 2" key="2">Content 2</Tabs.TabPane>
</Tabs>

// Card style
<Tabs type="card">
  <Tabs.TabPane tab="Tab 1" key="1">Content</Tabs.TabPane>
</Tabs>
```

### Breadcrumb

```javascript
import { Breadcrumb } from 'antd';

<Breadcrumb>
  <Breadcrumb.Item>Home</Breadcrumb.Item>
  <Breadcrumb.Item>List</Breadcrumb.Item>
  <Breadcrumb.Item>Detail</Breadcrumb.Item>
</Breadcrumb>
```

---

## Layout Components

### Layout

```javascript
import { Layout, Menu } from 'antd';

const { Header, Sider, Content, Footer } = Layout;

<Layout style={{ minHeight: '100vh' }}>
  <Sider>Side</Sider>
  <Layout>
    <Header>Header</Header>
    <Content>Content</Content>
    <Footer>Footer</Footer>
  </Layout>
</Layout>
```

### Grid

```javascript
import { Row, Col } from 'antd';

// Basic
<Row>
  <Col span={6}>6 cols</Col>
  <Col span={6}>6 cols</Col>
  <Col span={12}>12 cols</Col>
</Row>

// Gutter
<Row gutter={16}>
  <Col span={6}>Content</Col>
</Row>

// Responsive
<Row>
  <Col xs={24} sm={12} md={8} lg={6}>Responsive</Col>
</Row>
```
