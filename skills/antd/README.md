# Ant Design 组件库

为 AI 助手提供 Ant Design 组件库的完整使用指南。AI 可以在任何 React 项目中使用 Ant Design 构建 UI。

## 快速开始

### 安装

```bash
npm install antd @ant-design/icons
# 或
yarn add antd @ant-design/icons
```

### 引入样式

```javascript
import 'antd/dist/reset.css';
```

### 使用组件

```javascript
import { Button } from 'antd';

<Button type="primary">按钮</Button>
```

## 核心组件

### 按钮 (Button)

```javascript
import { Button } from 'antd';

// 基础用法
<Button>默认按钮</Button>
<Button type="primary">主要按钮</Button>
<Button type="dashed">虚线按钮</Button>
<Button type="text">文本按钮</Button>
<Button danger>危险按钮</Button>

// 状态
<Button loading>加载中</Button>
<Button disabled>禁用</Button>
<Button size="small">小按钮</Button>
```

### 表单 (Form)

```javascript
import { Form, Input, Button } from 'antd';

<Form onFinish={handleSubmit}>
  <Form.Item 
    name="username" 
    label="用户名"
    rules={[{ required: true, message: '请输入用户名!' }]}
  >
    <Input placeholder="请输入用户名" />
  </Form.Item>
  
  <Button type="primary" htmlType="submit">提交</Button>
</Form>
```

### 表格 (Table)

```javascript
import { Table, Tag } from 'antd';

const columns = [
  { title: '姓名', dataIndex: 'name' },
  { title: '年龄', dataIndex: 'age' },
  { 
    title: '状态', 
    dataIndex: 'status',
    render: (status) => (
      <Tag color={status === 'active' ? 'green' : 'red'}>
        {status === 'active' ? '启用' : '禁用'}
      </Tag>
    )
  },
];

<Table dataSource={data} columns={columns} rowKey="id" />
```

### 模态框 (Modal)

```javascript
import { Modal, Button } from 'antd';

const [open, setOpen] = useState(false);

<Button onClick={() => setOpen(true)}>打开</Button>

<Modal
  title="标题"
  open={open}
  onOk={() => setOpen(false)}
  onCancel={() => setOpen(false)}
>
  内容
</Modal>
```

## 组件分类

| 分类 | 组件 |
|------|------|
| 通用 | Button, Icon, Typography, Space, Divider |
| 导航 | Menu, Tabs, Breadcrumb, Dropdown, Pagination, Steps |
| 数据录入 | Form, Input, Select, Radio, Checkbox, DatePicker, Upload, Switch |
| 数据展示 | Table, Card, List, Tree, Badge, Tag, Timeline, Avatar |
| 反馈 | Modal, Message, Notification, Result, Progress, Spin, Alert |
| 布局 | Layout, Row, Col, Grid |

## 最佳实践

1. **表单验证** - 使用 Form.Item 的 rules 属性
2. **响应式** - 使用栅格系统 (Row/Col)
3. **主题定制** - 使用 ConfigProvider
4. **国际化** - 配置 LocaleProvider
5. **按需加载** - 使用 babel-plugin-import

## 主题定制

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

## 资源

- 官方文档：https://ant.design
- 组件总览：https://ant.design/components/overview
- 图标库：https://ant.design/components/icon
- GitHub: https://github.com/ant-design/ant-design
