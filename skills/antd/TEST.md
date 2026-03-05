# Ant Design Skill 效率测试

## 测试场景

### 场景 1：基础组件使用

**用户**: 用 Ant Design 创建一个按钮

**预期输出**:
```javascript
import { Button } from 'antd';

<Button type="primary">按钮</Button>
```

**评估标准**:
- ✅ 正确的 import 语句
- ✅ 使用 Button 组件
- ✅ 包含 type 属性
- ✅ 代码简洁

---

### 场景 2：表单创建

**用户**: 帮我做一个登录表单，包含用户名和密码

**预期输出**:
```javascript
import { Form, Input, Button } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';

<Form name="login">
  <Form.Item name="username" rules={[{ required: true }]}>
    <Input prefix={<UserOutlined />} placeholder="用户名" />
  </Form.Item>
  <Form.Item name="password" rules={[{ required: true }]}>
    <Input.Password prefix={<LockOutlined />} placeholder="密码" />
  </Form.Item>
  <Button type="primary" htmlType="submit">登录</Button>
</Form>
```

**评估标准**:
- ✅ 使用 Form 组件
- ✅ 包含表单验证
- ✅ 使用图标
- ✅ 完整的提交按钮

---

### 场景 3：数据表格

**用户**: 用 Table 组件展示用户数据，包含姓名、邮箱、状态

**预期输出**:
```javascript
import { Table, Tag } from 'antd';

const columns = [
  { title: '姓名', dataIndex: 'name' },
  { title: '邮箱', dataIndex: 'email' },
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

**评估标准**:
- ✅ 正确的 columns 定义
- ✅ 使用 Tag 组件渲染状态
- ✅ 包含 rowKey
- ✅ 使用 render 函数

---

### 场景 4：模态框

**用户**: 添加一个 Modal 确认删除的对话框

**预期输出**:
```javascript
import { Modal, Button } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

Modal.confirm({
  title: '确定删除吗？',
  icon: <ExclamationCircleOutlined />,
  content: '此操作不可恢复',
  onOk: handleDelete,
});
```

**评估标准**:
- ✅ 使用 Modal.confirm
- ✅ 包含图标
- ✅ 有确认文案
- ✅ 包含 onOk 回调

---

### 场景 5：完整页面

**用户**: 创建一个用户管理页面，有表格、搜索、添加功能

**预期输出**: 应该包含
- ✅ Table 组件
- ✅ Input 搜索框
- ✅ Button 添加按钮
- ✅ 状态管理 (useState)
- ✅ 数据过滤功能

---

## 效率评估指标

### 1. 响应速度
- ⭐⭐⭐⭐⭐ 即时响应 (< 3 秒)
- ⭐⭐⭐⭐ 快速 (3-5 秒)
- ⭐⭐⭐ 一般 (5-10 秒)

### 2. 代码准确性
- ⭐⭐⭐⭐⭐ 完全正确，可直接使用
- ⭐⭐⭐⭐ 小幅修改即可使用
- ⭐⭐⭐ 需要调整

### 3. 组件使用规范性
- ⭐⭐⭐⭐⭐ 完全符合 Ant Design 规范
- ⭐⭐⭐⭐ 基本符合规范
- ⭐⭐⭐ 需要优化

### 4. 代码完整性
- ⭐⭐⭐⭐⭐ 包含 import、样式、完整功能
- ⭐⭐⭐⭐ 缺少部分 import
- ⭐⭐⭐ 需要补充代码

### 5. 最佳实践
- ⭐⭐⭐⭐⭐ 遵循所有最佳实践
- ⭐⭐⭐⭐ 大部分遵循
- ⭐⭐⭐ 需要改进

---

## 测试记录

### 测试 1: 基础按钮
**时间**: __________
**响应**: __________
**评分**: __________

### 测试 2: 登录表单
**时间**: __________
**响应**: __________
**评分**: __________

### 测试 3: 数据表格
**时间**: __________
**响应**: __________
**评分**: __________

### 测试 4: 模态框
**时间**: __________
**响应**: __________
**评分**: __________

### 测试 5: 完整页面
**时间**: __________
**响应**: __________
**评分**: __________

---

## 总体评分

| 指标 | 评分 | 说明 |
|------|------|------|
| 响应速度 | ⭐⭐⭐⭐⭐ | |
| 代码准确性 | ⭐⭐⭐⭐⭐ | |
| 组件规范性 | ⭐⭐⭐⭐⭐ | |
| 代码完整性 | ⭐⭐⭐⭐⭐ | |
| 最佳实践 | ⭐⭐⭐⭐⭐ | |

**总分**: _____ / 25 ⭐

---

## 改进建议

1. __________
2. __________
3. __________

---

**测试日期**: 2026-02-27  
**测试人员**: __________
