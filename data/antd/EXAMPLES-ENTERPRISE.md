# Ant Design 企业级示例

## 示例 1：CRM 客户管理系统

完整的客户管理页面，包含列表、搜索、详情、编辑功能。

```javascript
import React, { useState } from 'react';
import { Table, Input, Button, Space, Tag, Modal, Form, Select, DatePicker, message, Popconfirm, Card, Row, Col, Descriptions, Avatar } from 'antd';
import { SearchOutlined, PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined, UserOutlined } from '@ant-design/icons';

const CRMSystem = () => {
  const [data, setData] = useState([
    { id: 1, name: '张三', company: '某某科技', phone: '13800138000', email: 'zhangsan@example.com', level: 'VIP', status: 'active', createTime: '2024-01-15' },
    { id: 2, name: '李四', company: '网络公司', phone: '13900139000', email: 'lisi@example.com', level: '普通', status: 'active', createTime: '2024-02-20' },
    { id: 3, name: '王五', company: '创新企业', phone: '13700137000', email: 'wangwu@example.com', level: '重要', status: 'inactive', createTime: '2024-03-10' },
  ]);
  const [searchText, setSearchText] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [form] = Form.useForm();

  const levelColors = { VIP: 'red', 重要：'orange', 普通：'blue' };

  const columns = [
    {
      title: '客户',
      dataIndex: 'name',
      render: (name, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <span>{name}</span>
        </Space>
      ),
    },
    { title: '公司', dataIndex: 'company' },
    { title: '电话', dataIndex: 'phone' },
    { title: '邮箱', dataIndex: 'email' },
    {
      title: '等级',
      dataIndex: 'level',
      render: (level) => <Tag color={levelColors[level]}>{level}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '活跃' : '沉睡'}
        </Tag>
      ),
    },
    { title: '创建时间', dataIndex: 'createTime' },
    {
      title: '操作',
      render: (_, record) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} onClick={() => handleView(record)}>详情</Button>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除吗？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleView = (customer) => {
    setEditingCustomer(customer);
    setViewModalOpen(true);
  };

  const handleEdit = (customer) => {
    setEditingCustomer(customer);
    form.setFieldsValue(customer);
    setModalOpen(true);
  };

  const handleDelete = (id) => {
    setData(data.filter(c => c.id !== id));
    message.success('删除成功');
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editingCustomer) {
        setData(data.map(c => c.id === editingCustomer.id ? { ...c, ...values } : c));
        message.success('更新成功');
      } else {
        setData([...data, { id: Date.now(), ...values, status: 'active', createTime: new Date().toISOString().split('T')[0] }]);
        message.success('添加成功');
      }
      setModalOpen(false);
      setEditingCustomer(null);
      form.resetFields();
    } catch (error) {
      console.error('验证失败:', error);
    }
  };

  const filteredData = data.filter(customer =>
    customer.name.toLowerCase().includes(searchText.toLowerCase()) ||
    customer.company.toLowerCase().includes(searchText.toLowerCase()) ||
    customer.phone.includes(searchText)
  );

  return (
    <div style={{ padding: 24 }}>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Input
            placeholder="搜索客户名称、公司或电话"
            prefix={<SearchOutlined />}
            style={{ width: 400 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
            添加客户
          </Button>
        </Space>
      </Card>

      <Table dataSource={filteredData} columns={columns} rowKey="id" />

      {/* 添加/编辑模态框 */}
      <Modal
        title={editingCustomer?.id ? '编辑客户' : '添加客户'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditingCustomer(null); form.resetFields(); }}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="name" label="姓名" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="company" label="公司" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="phone" label="电话" rules={[{ required: true, pattern: /^1[3-9]\d{9}$/ }]}>
                <Input />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email' }]}>
                <Input />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="level" label="等级" rules={[{ required: true }]}>
                <Select>
                  <Select.Option value="VIP">VIP</Select.Option>
                  <Select.Option value="重要">重要</Select.Option>
                  <Select.Option value="普通">普通</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="status" label="状态">
                <Select>
                  <Select.Option value="active">活跃</Select.Option>
                  <Select.Option value="inactive">沉睡</Select.Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 详情模态框 */}
      <Modal
        title="客户详情"
        open={viewModalOpen}
        onCancel={() => setViewModalOpen(false)}
        footer={null}
      >
        {editingCustomer && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="姓名">{editingCustomer.name}</Descriptions.Item>
            <Descriptions.Item label="公司">{editingCustomer.company}</Descriptions.Item>
            <Descriptions.Item label="电话">{editingCustomer.phone}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{editingCustomer.email}</Descriptions.Item>
            <Descriptions.Item label="等级">
              <Tag color={levelColors[editingCustomer.level]}>{editingCustomer.level}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={editingCustomer.status === 'active' ? 'green' : 'red'}>
                {editingCustomer.status === 'active' ? '活跃' : '沉睡'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="创建时间">{editingCustomer.createTime}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default CRMSystem;
```

---

## 示例 2：数据可视化仪表盘

带统计卡片和图表的数据展示仪表盘。

```javascript
import React from 'react';
import { Card, Row, Col, Statistic, Progress, Table, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, UserOutlined, ShoppingCartOutlined, DollarOutlined, EyeOutlined } from '@ant-design/icons';

const Dashboard = () => {
  // 统计数据
  const statsData = [
    { title: '总销售额', value: 126560, prefix: <DollarOutlined />, trend: 'up', trendValue: 12.5 },
    { title: '访问量', value: 8846, prefix: <EyeOutlined />, trend: 'up', trendValue: 8.2 },
    { title: '订单数', value: 1234, prefix: <ShoppingCartOutlined />, trend: 'down', trendValue: 3.1 },
    { title: '用户数', value: 5638, prefix: <UserOutlined />, trend: 'up', trendValue: 15.3 },
  ];

  // 订单表格数据
  const orderData = [
    { id: 'ORD001', customer: '张三', amount: 1200, status: 'completed', date: '2024-03-20' },
    { id: 'ORD002', customer: '李四', amount: 850, status: 'pending', date: '2024-03-21' },
    { id: 'ORD003', customer: '王五', amount: 2300, status: 'completed', date: '2024-03-21' },
    { id: 'ORD004', customer: '赵六', amount: 560, status: 'cancelled', date: '2024-03-22' },
  ];

  const orderColumns = [
    { title: '订单号', dataIndex: 'id' },
    { title: '客户', dataIndex: 'customer' },
    { title: '金额', dataIndex: 'amount', render: (amount) => `¥${amount}` },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status) => {
        const statusMap = {
          completed: { color: 'green', text: '已完成' },
          pending: { color: 'orange', text: '进行中' },
          cancelled: { color: 'red', text: '已取消' },
        };
        const { color, text } = statusMap[status];
        return <Tag color={color}>{text}</Tag>;
      },
    },
    { title: '日期', dataIndex: 'date' },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>数据仪表盘</h1>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {statsData.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card>
              <Statistic
                title={stat.title}
                value={stat.value}
                prefix={stat.prefix}
                valueStyle={{ color: stat.trend === 'up' ? '#3f8600' : '#cf1322' }}
              >
                <div style={{ marginTop: 8 }}>
                  {stat.trend === 'up' ? (
                    <ArrowUpOutlined style={{ color: '#3f8600' }} />
                  ) : (
                    <ArrowDownOutlined style={{ color: '#cf1322' }} />
                  )}
                  <span style={{ marginLeft: 8, color: stat.trend === 'up' ? '#3f8600' : '#cf1322' }}>
                    {stat.trendValue}%
                  </span>
                  <span style={{ marginLeft: 8, color: '#999' }}>较上周</span>
                </div>
              </Statistic>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 进度展示 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="销售目标进度">
            <Progress percent={75} status="active" />
            <Progress percent={85} strokeColor={{ '0%': '#108ee9', '100%': '#87d068' }} />
            <Progress percent={100} status="success" />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="任务完成情况">
            <Progress type="circle" percent={65} />
            <Progress type="circle" percent={80} strokeColor="#1890ff" style={{ marginLeft: 24 }} />
            <Progress type="circle" percent={100} status="success" strokeColor="#52c41a" style={{ marginLeft: 24 }} />
          </Card>
        </Col>
      </Row>

      {/* 订单表格 */}
      <Card title="最近订单">
        <Table dataSource={orderData} columns={orderColumns} rowKey="id" pagination={false} />
      </Card>
    </div>
  );
};

export default Dashboard;
```

---

## 示例 3：权限管理系统

带角色和权限控制的后台管理系统。

```javascript
import React, { useState } from 'react';
import { Table, Button, Switch, Modal, Form, Input, Tree, Checkbox, message, Tag, Space } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SettingOutlined } from '@ant-design/icons';

const PermissionSystem = () => {
  const [roles, setRoles] = useState([
    { id: 1, name: '超级管理员', description: '拥有所有权限', status: true },
    { id: 2, name: '管理员', description: '管理普通用户', status: true },
    { id: 3, name: '普通用户', description: '基本操作权限', status: true },
    { id: 4, name: '访客', description: '只读权限', status: false },
  ]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [form] = Form.useForm();

  // 权限树
  const permissionTree = [
    {
      title: '系统管理',
      key: 'system',
      children: [
        { title: '用户管理', key: 'user' },
        { title: '角色管理', key: 'role' },
        { title: '权限管理', key: 'permission' },
      ],
    },
    {
      title: '内容管理',
      key: 'content',
      children: [
        { title: '文章管理', key: 'article' },
        { title: '评论管理', key: 'comment' },
      ],
    },
  ];

  const columns = [
    { title: '角色名称', dataIndex: 'name' },
    { title: '描述', dataIndex: 'description' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status) => <Tag color={status ? 'green' : 'red'}>{status ? '启用' : '禁用'}</Tag>,
    },
    {
      title: '操作',
      render: (_, record) => (
        <Space>
          <Button icon={<SettingOutlined />} onClick={() => handlePermissions(record)}>权限</Button>
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>编辑</Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  const handlePermissions = (role) => {
    setEditingRole(role);
    // 打开权限配置模态框
    message.info(`配置 ${role.name} 的权限`);
  };

  const handleEdit = (role) => {
    setEditingRole(role);
    form.setFieldsValue(role);
    setModalOpen(true);
  };

  const handleDelete = (id) => {
    setRoles(roles.filter(r => r.id !== id));
    message.success('删除成功');
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      if (editingRole) {
        setRoles(roles.map(r => r.id === editingRole.id ? { ...r, ...values } : r));
        message.success('更新成功');
      } else {
        setRoles([...roles, { id: Date.now(), ...values, status: true }]);
        message.success('添加成功');
      }
      setModalOpen(false);
      setEditingRole(null);
      form.resetFields();
    } catch (error) {
      console.error('验证失败:', error);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)} style={{ marginBottom: 16 }}>
        添加角色
      </Button>

      <Table dataSource={roles} columns={columns} rowKey="id" />

      {/* 添加/编辑角色 */}
      <Modal
        title={editingRole?.id ? '编辑角色' : '添加角色'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => { setModalOpen(false); setEditingRole(null); form.resetFields(); }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="角色名称" rules={[{ required: true }]}>
            <Input placeholder="请输入角色名称" />
          </Form.Item>
          <Form.Item name="description" label="描述" rules={[{ required: true }]}>
            <Input.TextArea rows={3} placeholder="请输入角色描述" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 权限配置 */}
      <Modal
        title="权限配置"
        open={false}
        footer={null}
      >
        <Tree
          checkable
          defaultExpandAll
          treeData={permissionTree}
        />
      </Modal>
    </div>
  );
};

export default PermissionSystem;
```

---

## 示例 4：工单系统

完整的工单管理和跟踪系统。

```javascript
import React, { useState } from 'react';
import { Table, Input, Button, Select, Tag, Modal, Form, Upload, message, Steps, Timeline, Space } from 'antd';
import { PlusOutlined, SearchOutlined, PaperClipOutlined } from '@ant-design/icons';

const { Option } = Select;

const TicketSystem = () => {
  const [tickets, setTickets] = useState([
    { id: 'TKT001', title: '系统登录问题', priority: 'high', status: 'processing', category: '技术', createTime: '2024-03-20 10:00', updateTime: '2024-03-21 14:30' },
    { id: 'TKT002', title: '功能建议', priority: 'low', status: 'pending', category: '产品', createTime: '2024-03-21 09:00', updateTime: '2024-03-21 09:00' },
    { id: 'TKT003', title: '数据导出异常', priority: 'medium', status: 'resolved', category: '技术', createTime: '2024-03-19 15:00', updateTime: '2024-03-20 16:00' },
  ]);
  const [searchText, setSearchText] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [form] = Form.useForm();

  const priorityColors = { high: 'red', medium: 'orange', low: 'green' };
  const statusColors = { pending: 'default', processing: 'blue', resolved: 'green', closed: 'red' };
  const statusText = { pending: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭' };

  const columns = [
    { title: '工单号', dataIndex: 'id' },
    { title: '标题', dataIndex: 'title' },
    {
      title: '优先级',
      dataIndex: 'priority',
      render: (priority) => <Tag color={priorityColors[priority]}>{priority === 'high' ? '高' : priority === 'medium' ? '中' : '低'}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status) => <Tag color={statusColors[status]}>{statusText[status]}</Tag>,
    },
    { title: '分类', dataIndex: 'category' },
    { title: '创建时间', dataIndex: 'createTime' },
    { title: '更新时间', dataIndex: 'updateTime' },
  ];

  const filteredTickets = tickets.filter(ticket =>
    ticket.title.toLowerCase().includes(searchText.toLowerCase()) ||
    ticket.id.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <div style={{ padding: 24 }}>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索工单"
          prefix={<SearchOutlined />}
          style={{ width: 300 }}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>
          创建工单
        </Button>
      </Space>

      <Table dataSource={filteredTickets} columns={columns} rowKey="id" />

      <Modal
        title="创建工单"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input placeholder="请输入工单标题" />
          </Form.Item>
          <Form.Item name="category" label="分类" rules={[{ required: true }]}>
            <Select placeholder="请选择分类">
              <Option value="技术">技术问题</Option>
              <Option value="产品">产品建议</Option>
              <Option value="账单">账单问题</Option>
              <Option value="其他">其他</Option>
            </Select>
          </Form.Item>
          <Form.Item name="priority" label="优先级" rules={[{ required: true }]}>
            <Select placeholder="请选择优先级">
              <Option value="high">高</Option>
              <Option value="medium">中</Option>
              <Option value="low">低</Option>
            </Select>
          </Form.Item>
          <Form.Item name="description" label="描述" rules={[{ required: true }]}>
            <Input.TextArea rows={4} placeholder="请详细描述问题" />
          </Form.Item>
          <Form.Item name="attachment" label="附件">
            <Upload>
              <Button icon={<PaperClipOutlined />}>上传附件</Button>
            </Upload>
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={() => { setModalOpen(false); message.success('工单创建成功'); }}>提交</Button>
              <Button onClick={() => setModalOpen(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TicketSystem;
```
