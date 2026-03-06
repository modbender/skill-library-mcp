# Ant Design 组件完整参考

## 通用组件

### Button 按钮

```javascript
import { Button } from 'antd';

// 类型
<Button type="primary">主要</Button>
<Button type="secondary">次要</Button>
<Button type="dashed">虚线</Button>
<Button type="text">文本</Button>
<Button type="link">链接</Button>

// 状态
<Button loading>加载</Button>
<Button disabled>禁用</Button>

// 尺寸
<Button size="small">小</Button>
<Button size="large">大</Button>

// 危险
<Button danger>危险</Button>

// 图标
<Button icon={<SearchOutlined />}>搜索</Button>
```

### Typography 排版

```javascript
import { Typography } from 'antd';

const { Title, Paragraph, Text, Link } = Typography;

<Title>标题</Title>
<Title level={2}>二级标题</Title>
<Paragraph>段落</Paragraph>
<Text>文本</Text>
<Text type="secondary">次要文本</Text>
<Text mark>标记</Text>
<Text code>代码</Text>
<Link href="#">链接</Link>
```

### Icon 图标

```javascript
import { HomeOutlined, SettingFilled } from '@ant-design/icons';

<HomeOutlined />
<SettingFilled />
<HomeOutlined style={{ color: '#1890ff', fontSize: 24 }} />
```

---

## 表单组件

### Input 输入框

```javascript
import { Input } from 'antd';

// 基础
<Input placeholder="请输入" />

// 文本域
<Input.TextArea rows={4} />

// 密码
<Input.Password placeholder="密码" />

// 搜索
<Input.Search placeholder="搜索" onSearch={handleSearch} />

// 带前缀/后缀
<Input prefix={<UserOutlined />} suffix={<InfoCircleOutlined />} />

// 禁用/只读
<Input disabled />
<Input readOnly />
```

### Select 选择器

```javascript
import { Select } from 'antd';

const { Option } = Select;

// 单选
<Select placeholder="请选择" style={{ width: 200 }}>
  <Option value="1">选项 1</Option>
  <Option value="2">选项 2</Option>
</Select>

// 多选
<Select mode="multiple" placeholder="多选">
  <Option value="1">选项 1</Option>
</Select>

// 搜索
<Select showSearch placeholder="搜索选项">
  <Option value="1">选项 1</Option>
</Select>

// 禁用
<Select disabled />
```

### Radio 单选框

```javascript
import { Radio } from 'antd';

// 单选组
<Radio.Group>
  <Radio value={1}>选项 1</Radio>
  <Radio value={2}>选项 2</Radio>
</Radio.Group>

// 按钮样式
<Radio.Group buttonStyle="solid">
  <Radio.Button value="large">大</Radio.Button>
  <Radio.Button value="middle">中</Radio.Button>
</Radio.Group>
```

### Checkbox 复选框

```javascript
import { Checkbox } from 'antd';

// 单个
<Checkbox>选项</Checkbox>

// 组
<Checkbox.Group>
  <Checkbox value="1">选项 1</Checkbox>
  <Checkbox value="2">选项 2</Checkbox>
</Checkbox.Group>

// 全选
const [checkedList, setCheckedList] = useState([]);

<Checkbox
  indeterminate={indeterminate}
  onChange={onCheckAllChange}
  checked={checkAll}
>
  全选
</Checkbox>
```

### DatePicker 日期选择器

```javascript
import { DatePicker } from 'antd';

// 日期
<DatePicker placeholder="选择日期" />

// 日期范围
<DatePicker.RangePicker />

// 带时间
<DatePicker showTime placeholder="选择日期时间" />

// 月份
<DatePicker picker="month" />

// 年份
<DatePicker picker="year" />
```

### Form 表单

```javascript
import { Form, Input, Button, Select } from 'antd';

const [form] = Form.useForm();

<Form
  form={form}
  layout="vertical"
  onFinish={handleSubmit}
  initialValues={{ name: '默认值' }}
>
  <Form.Item
    name="username"
    label="用户名"
    rules={[
      { required: true, message: '请输入用户名!' },
      { min: 3, message: '至少 3 个字符!' }
    ]}
  >
    <Input />
  </Form.Item>
  
  <Form.Item
    name="email"
    label="邮箱"
    rules={[
      { type: 'email', message: '邮箱格式不正确!' }
    ]}
  >
    <Input />
  </Form.Item>
  
  <Button type="primary" htmlType="submit">提交</Button>
  <Button onClick={() => form.resetFields()}>重置</Button>
</Form>
```

---

## 数据展示

### Table 表格

```javascript
import { Table, Space, Tag, Button } from 'antd';

const columns = [
  {
    title: '姓名',
    dataIndex: 'name',
    key: 'name',
    sorter: (a, b) => a.name.localeCompare(b.name),
  },
  {
    title: '年龄',
    dataIndex: 'age',
    key: 'age',
  },
  {
    title: '状态',
    dataIndex: 'status',
    render: (status) => (
      <Tag color={status === 'active' ? 'green' : 'red'}>
        {status === 'active' ? '启用' : '禁用'}
      </Tag>
    ),
  },
  {
    title: '操作',
    render: (_, record) => (
      <Space>
        <Button type="link">编辑</Button>
        <Button type="link" danger>删除</Button>
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

### Card 卡片

```javascript
import { Card, Avatar } from 'antd';

// 基础
<Card title="标题">内容</Card>

// 带操作
<Card
  title="标题"
  extra={<a href="#">更多</a>}
  actions={[
    <SettingOutlined key="setting" />,
    <EditOutlined key="edit" />,
  ]}
>
  内容
</Card>

// 可悬停
<Card hoverable cover={<img alt="封面" src="..." />}>
  内容
</Card>

// 统计卡片
<Card>
  <Statistic title="用户数" value={1268} />
</Card>
```

### List 列表

```javascript
import { List, Avatar } from 'antd';

<List
  itemLayout="horizontal"
  dataSource={data}
  renderItem={(item) => (
    <List.Item actions={[<a key="edit">编辑</a>]}>
      <List.Item.Meta
        avatar={<Avatar src={item.avatar} />}
        title={<a href="#">{item.title}</a>}
        description={item.description}
      />
    </List.Item>
  )}
/>
```

### Badge 徽章

```javascript
import { Badge } from 'antd';

<Badge count={5}>
  <div>内容</div>
</Badge>

<Badge count={100} overflowCount={99}>
  <div>内容</div>
</Badge>

<Badge dot>
  <div>红点</div>
</Badge>
```

### Tag 标签

```javascript
import { Tag } from 'antd';

<Tag>默认</Tag>
<Tag color="red">红色</Tag>
<Tag color="green">绿色</Tag>
<Tag color="blue">蓝色</Tag>

// 可关闭
<Tag closable onClose={handleClose}>可关闭</Tag>
```

---

## 反馈组件

### Modal 对话框

```javascript
import { Modal, Button } from 'antd';

const [open, setOpen] = useState(false);

// 基础
<Modal
  title="标题"
  open={open}
  onOk={handleOk}
  onCancel={handleCancel}
>
  内容
</Modal>

// 确认框
Modal.confirm({
  title: '确定删除吗？',
  onOk: handleDelete,
});

// 成功提示
Modal.success({ title: '操作成功' });

// 错误提示
Modal.error({ title: '操作失败' });
```

### Message 全局提示

```javascript
import { message } from 'antd';

message.success('操作成功');
message.error('操作失败');
message.warning('警告');
message.info('提示');
message.loading('加载中...', 2);
```

### Notification 通知提醒框

```javascript
import { notification } from 'antd';

notification.success({
  message: '通知标题',
  description: '通知详细内容',
  duration: 4.5,
});

notification.error({
  message: '错误',
  description: '错误详情',
});
```

### Spin 加载中

```javascript
import { Spin } from 'antd';

// 基础
<Spin />

// 带文字
<Spin tip="加载中..." />

// 尺寸
<Spin size="small" />
<Spin size="large" />

// 包裹内容
<Spin spinning={loading}>
  <Content />
</Spin>
```

---

## 导航组件

### Menu 导航菜单

```javascript
import { Menu } from 'antd';

// 水平菜单
<Menu mode="horizontal" selectedKeys={['1']}>
  <Menu.Item key="1">导航 1</Menu.Item>
  <Menu.Item key="2">导航 2</Menu.Item>
</Menu>

// 垂直菜单
<Menu mode="vertical" selectedKeys={['1']}>
  <Menu.Item key="1">菜单 1</Menu.Item>
  <Menu.SubMenu title="子菜单">
    <Menu.Item key="3">选项 1</Menu.Item>
  </Menu.SubMenu>
</Menu>
```

### Tabs 标签页

```javascript
import { Tabs } from 'antd';

<Tabs>
  <Tabs.TabPane tab="标签 1" key="1">内容 1</Tabs.TabPane>
  <Tabs.TabPane tab="标签 2" key="2">内容 2</Tabs.TabPane>
</Tabs>

// 卡片风格
<Tabs type="card">
  <Tabs.TabPane tab="标签 1" key="1">内容</Tabs.TabPane>
</Tabs>
```

### Breadcrumb 面包屑

```javascript
import { Breadcrumb } from 'antd';

<Breadcrumb>
  <Breadcrumb.Item>首页</Breadcrumb.Item>
  <Breadcrumb.Item>列表</Breadcrumb.Item>
  <Breadcrumb.Item>详情</Breadcrumb.Item>
</Breadcrumb>
```

---

## 布局组件

### Layout 布局

```javascript
import { Layout, Menu } from 'antd';

const { Header, Sider, Content, Footer } = Layout;

<Layout style={{ minHeight: '100vh' }}>
  <Sider>侧边栏</Sider>
  <Layout>
    <Header>顶部</Header>
    <Content>内容</Content>
    <Footer>底部</Footer>
  </Layout>
</Layout>
```

### Grid 栅格

```javascript
import { Row, Col } from 'antd';

// 基础
<Row>
  <Col span={6}>6 列</Col>
  <Col span={6}>6 列</Col>
  <Col span={12}>12 列</Col>
</Row>

// 间距
<Row gutter={16}>
  <Col span={6}>内容</Col>
</Row>

// 响应式
<Row>
  <Col xs={24} sm={12} md={8} lg={6}>响应式</Col>
</Row>
```
