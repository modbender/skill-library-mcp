# Ant Design 实战示例

## 示例 1：登录表单

完整的登录页面，包含表单验证。

```javascript
import React, { useState } from 'react';
import { Form, Input, Button, Card, message, Checkbox } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';

const LoginForm = () => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      // 调用登录 API
      console.log('登录信息:', values);
      message.success('登录成功');
    } catch (error) {
      message.error('登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f0f2f5'
    }}>
      <Card title="用户登录" style={{ width: 400 }}>
        <Form name="login" onFinish={onFinish} initialValues={{ remember: true }}>
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名!' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码!' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住我</Checkbox>
            </Form.Item>
            <a href="/forgot-password" style={{ float: 'right' }}>忘记密码？</a>
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            还没有账户？<a href="/register">立即注册</a>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default LoginForm;
```

---

## 示例 2：用户管理表格

带搜索、分页、编辑、删除的用户管理表格。

```javascript
import React, { useState } from 'react';
import { Table, Input, Button, Space, Tag, Modal, Form, message, Popconfirm } from 'antd';
import { SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';

const UserTable = () => {
  const [data, setData] = useState([
    { id: 1, name: '张三', age: 28, email: 'zhangsan@example.com', role: '管理员', status: 'active' },
    { id: 2, name: '李四', age: 32, email: 'lisi@example.com', role: '编辑', status: 'active' },
    { id: 3, name: '王五', age: 25, email: 'wangwu@example.com', role: '用户', status: 'inactive' },
  ]);
  const [searchText, setSearchText] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [form] = Form.useForm();

  const columns = [
    { title: '姓名', dataIndex: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
    { title: '年龄', dataIndex: 'age', sorter: (a, b) => a.age - b.age },
    { title: '邮箱', dataIndex: 'email' },
    {
      title: '角色',
      dataIndex: 'role',
      render: (role) => <Tag color={role === '管理员' ? 'red' : 'blue'}>{role}</Tag>,
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
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleEdit = (user) => {
    setEditingUser(user);
    form.setFieldsValue(user);
    setModalOpen(true);
  };

  const handleDelete = (id) => {
    setData(data.filter(u => u.id !== id));
    message.success('删除成功');
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editingUser) {
        setData(data.map(u => u.id === editingUser.id ? { ...u, ...values } : u));
        message.success('更新成功');
      } else {
        setData([...data, { id: Date.now(), ...values, status: 'active' }]);
        message.success('添加成功');
      }
      setModalOpen(false);
      setEditingUser(null);
      form.resetFields();
    } catch (error) {
      console.error('验证失败:', error);
    }
  };

  const filteredData = data.filter(user =>
    user.name.toLowerCase().includes(searchText.toLowerCase()) ||
    user.email.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索姓名或邮箱"
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          添加用户
        </Button>
      </Space>

      <Table dataSource={filteredData} columns={columns} rowKey="id" />

      <Modal
        title={editingUser ? '编辑用户' : '添加用户'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditingUser(null); form.resetFields(); }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="age" label="年龄" rules={[{ required: true }]}>
            <Input type="number" />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="role" label="角色" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="管理员">管理员</Select.Option>
              <Select.Option value="编辑">编辑</Select.Option>
              <Select.Option value="用户">用户</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default UserTable;
```

---

## 示例 3：仪表盘布局

完整的管理后台布局，包含侧边栏、顶部导航、内容区域。

```javascript
import React, { useState } from 'react';
import { Layout, Menu, Card, Row, Col, Statistic, Avatar, Dropdown, Badge, Breadcrumb } from 'antd';
import {
  DashboardOutlined, ProjectOutlined, TeamOutlined, UserOutlined, SettingOutlined,
  MenuFoldOutlined, MenuUnfoldOutlined, BellOutlined, HomeOutlined
} from '@ant-design/icons';

const { Header, Sider, Content, Footer } = Layout;

const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [currentMenu, setCurrentMenu] = useState('dashboard');

  const menuItems = [
    { key: 'dashboard', icon: <DashboardOutlined />, label: '仪表盘' },
    { key: 'projects', icon: <ProjectOutlined />, label: '项目管理' },
    { key: 'team', icon: <TeamOutlined />, label: '团队管理' },
    { key: 'users', icon: <UserOutlined />, label: '用户管理' },
    { key: 'settings', icon: <SettingOutlined />, label: '系统设置' },
  ];

  const userMenu = [
    { key: 'profile', label: '个人中心' },
    { key: 'settings', label: '账户设置' },
    { type: 'divider' },
    { key: 'logout', label: '退出登录' },
  ];

  const breadcrumbItems = {
    dashboard: ['首页', '仪表盘'],
    projects: ['首页', '项目管理'],
    team: ['首页', '团队管理'],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed} theme="dark">
        <div style={{
          height: 32, margin: 16, background: 'rgba(255,255,255,0.2)',
          borderRadius: 4, display: 'flex', alignItems: 'center',
          justifyContent: 'center', color: '#fff', fontWeight: 'bold'
        }}>
          {collapsed ? 'AI' : '管理系统'}
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[currentMenu]} items={menuItems} />
      </Sider>

      <Layout>
        <Header style={{
          background: '#fff', padding: '0 16px', display: 'flex',
          justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
            />
            <Breadcrumb style={{ marginLeft: 16 }} items={breadcrumbItems[currentMenu]} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Badge count={5}><BellOutlined style={{ fontSize: 18 }} /></Badge>
            <Dropdown menu={{ items: userMenu }}>
              <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1890ff' }} />
                <span style={{ marginLeft: 8 }}>管理员</span>
              </div>
            </Dropdown>
          </div>
        </Header>

        <Content style={{ margin: 16, padding: 24, background: '#fff', borderRadius: 4 }}>
          <h1>欢迎使用管理系统</h1>
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic title="总用户数" value={1268} prefix={<UserOutlined />} valueStyle={{ color: '#1890ff' }} />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic title="项目数量" value={42} prefix={<ProjectOutlined />} valueStyle={{ color: '#52c41a' }} />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic title="团队成员" value={28} prefix={<TeamOutlined />} valueStyle={{ color: '#faad14' }} />
              </Card>
            </Col>
          </Row>
        </Content>

        <Footer style={{ textAlign: 'center', color: '#999' }}>
          管理系统 ©{new Date().getFullYear()} Created with Ant Design
        </Footer>
      </Layout>
    </Layout>
  );
};

export default Dashboard;
```

---

## 示例 4：搜索筛选表单

带多条件筛选的搜索表单。

```javascript
import React from 'react';
import { Form, Input, Select, DatePicker, Button, Row, Col } from 'antd';

const { Option } = Select;

const SearchForm = ({ onSearch, onReset }) => {
  const [form] = Form.useForm();

  return (
    <Form form={form} layout="inline" onFinish={onSearch} style={{ marginBottom: 24 }}>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="keyword" label="关键词">
            <Input placeholder="请输入关键词" allowClear />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="status" label="状态">
            <Select placeholder="请选择" allowClear>
              <Option value="active">启用</Option>
              <Option value="inactive">禁用</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="date" label="日期范围">
            <DatePicker.RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item>
            <Button type="primary" htmlType="submit">搜索</Button>
            <Button style={{ marginLeft: 8 }} onClick={() => form.resetFields()}>重置</Button>
          </Form.Item>
        </Col>
      </Row>
    </Form>
  );
};

export default SearchForm;
```

---

## 示例 5：确认对话框

使用 Modal 的确认对话框。

```javascript
import React, { useState } from 'react';
import { Modal, Button, message } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

const ConfirmDialog = () => {
  const [modalApi, modalContextHolder] = Modal.useModal();

  const showDeleteConfirm = () => {
    modalApi.confirm({
      title: '确定要删除吗？',
      icon: <ExclamationCircleOutlined />,
      content: '此操作不可恢复，请谨慎操作！',
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk() {
        message.success('删除成功');
      },
      onCancel() {
        message.info('已取消');
      },
    });
  };

  return (
    <>
      <Button danger onClick={showDeleteConfirm}>删除</Button>
      {modalContextHolder}
    </>
  );
};

export default ConfirmDialog;
```
