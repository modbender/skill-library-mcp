# Ant Design 组件库 - Clawhub Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ant Design 5.x](https://img.shields.io/badge/Ant_Design-5.x-blue)](https://ant.design)
[![React 18+](https://img.shields.io/badge/React-18+-61dafb)](https://react.dev)

为 OpenClaw AI 助手提供 Ant Design 组件库的完整使用指南。

## ✨ 特性

- 📚 **完整的组件文档** - 覆盖 38 个常用组件
- 🌐 **双语支持** - 中文 + English
- 💼 **企业级示例** - 9 个完整实战案例
- 🎨 **最佳实践** - 遵循 Ant Design 官方规范
- 📱 **响应式设计** - 适配各种屏幕尺寸
- ♿ **可访问性** - 符合无障碍标准

## 📦 安装

```bash
clawhub install antd-components
```

## 🚀 使用

在 OpenClaw 对话中直接使用：

```
用 Ant Design 创建一个登录表单
帮我添加一个 Table 组件展示用户数据
用 Modal 做一个确认删除的对话框
```

## 📖 文档结构

```
antd/
├── SKILL.md                  # Skill 描述
├── README.md                 # 快速开始（中文）
├── README.en-US.md           # 快速开始（英文）
├── COMPONENTS.md             # 组件参考（中文）
├── COMPONENTS.en-US.md       # 组件参考（英文）
├── EXAMPLES.md               # 基础示例
├── EXAMPLES-ENTERPRISE.md    # 企业级示例
└── SUMMARY.md                # 文档说明
```

## 📊 组件覆盖

| 分类 | 组件数量 |
|------|----------|
| 通用组件 | 5 |
| 表单组件 | 10 |
| 数据展示 | 8 |
| 反馈组件 | 6 |
| 导航组件 | 5 |
| 布局组件 | 4 |
| **总计** | **38** |

## 💼 示例代码

### 基础示例 (5 个)
1. 登录表单
2. 用户管理表格
3. 仪表盘布局
4. 搜索筛选表单
5. 确认对话框

### 企业级示例 (4 个)
1. CRM 客户管理系统
2. 数据可视化仪表盘
3. 权限管理系统
4. 工单系统

## 🎯 适用场景

- ✅ 快速原型开发
- ✅ 管理后台搭建
- ✅ 表单页面创建
- ✅ 数据展示页面
- ✅ 企业级应用开发

## 📝 示例代码

### 按钮

```javascript
import { Button } from 'antd';

<Button type="primary">主要按钮</Button>
<Button type="dashed">虚线按钮</Button>
<Button danger>危险按钮</Button>
```

### 表单

```javascript
import { Form, Input, Button } from 'antd';

<Form onFinish={handleSubmit}>
  <Form.Item name="username" rules={[{ required: true }]}>
    <Input placeholder="用户名" />
  </Form.Item>
  <Button type="primary" htmlType="submit">提交</Button>
</Form>
```

### 表格

```javascript
import { Table, Tag } from 'antd';

const columns = [
  { title: '姓名', dataIndex: 'name' },
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

## 🔗 相关链接

- [Ant Design 官网](https://ant.design)
- [组件总览](https://ant.design/components/overview)
- [图标库](https://ant.design/components/icon)
- [GitHub](https://github.com/ant-design/ant-design)

## 📄 License

MIT License © 2026 batype
