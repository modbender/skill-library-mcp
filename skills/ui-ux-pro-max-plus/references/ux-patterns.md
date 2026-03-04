# UX 模式库 - 用户体验最佳实践

经过验证的交互模式和设计模式，解决常见 UX 问题。

---

## 🚪 导航模式

### 顶部导航（Top Navigation）
**适用：** 网站、SaaS 产品

**结构：**
```
[Logo]  [主导航项 × 3-5]  [搜索]  [用户菜单]
```

**设计要点：**
- 导航项不超过 7 个
- 当前页面高亮显示
- 支持下拉菜单（二级导航）
- 移动端转为汉堡菜单

**Tailwind 实现：**
```html
<nav class="bg-white border-b px-6 py-4">
  <div class="max-w-7xl mx-auto flex items-center justify-between">
    <div class="flex items-center gap-8">
      <a href="/" class="text-xl font-bold">Logo</a>
      <div class="hidden md:flex items-center gap-6">
        <a href="/features" class="text-gray-600 hover:text-gray-900">功能</a>
        <a href="/pricing" class="text-gray-600 hover:text-gray-900">价格</a>
        <a href="/about" class="text-gray-600 hover:text-gray-900">关于</a>
      </div>
    </div>
    <div class="flex items-center gap-4">
      <button class="md:hidden">☰</button>
      <button class="bg-blue-600 text-white px-4 py-2 rounded">开始使用</button>
    </div>
  </div>
</nav>
```

---

### 侧边导航（Sidebar Navigation）
**适用：** 仪表盘、管理系统

**结构：**
```
[Logo]
[首页]
[分析] →
[用户] →
[设置] →
------------
[用户头像 + 名称]
```

**设计要点：**
- 图标 + 文字标签
- 可折叠的子菜单
- 当前项高亮
- 底部放置用户区

---

### 标签导航（Tab Navigation）
**适用：** 内容分类、设置页面

**类型：**
- **水平标签：** 3-5 个，最常见
- **垂直标签：** 左侧，适合较多选项
- **下拉标签：** 移动端节省空间

---

## 📋 表单模式

### 表单布局

**单列布局（推荐）：**
```
[标签]
[输入框                    ]

[标签]
[输入框                    ]

[复选框] 选项说明

[提交按钮]
```

**设计要点：**
- 标签在输入框上方
- 标签与输入框间距 8px
- 输入框间距 24px
- 按钮与最后一个字段间距 32px

---

### 输入验证

**实时验证（推荐）：**
- 用户停止输入后验证
- 用颜色 + 图标表示状态
- 提供清晰的错误信息

```html
<div class="space-y-1">
  <label class="text-sm font-medium">邮箱</label>
  <input type="email" 
         class="w-full px-3 py-2 border rounded 
                focus:ring-2 focus:ring-blue-500
                invalid:border-red-500 invalid:text-red-600" />
  <p class="text-sm text-red-600">请输入有效的邮箱地址</p>
</div>
```

---

### 分步表单（Wizard）
**适用：** 复杂流程（注册、结账、配置）

**结构：**
```
[步骤1] → [步骤2] → [步骤3]
   ✓        ●         ○

[当前步骤内容]

[上一步]    [下一步]
```

**设计要点：**
- 显示进度（已完成/当前/待完成）
- 允许返回修改
- 显示步骤标题
- 最后一步确认汇总

---

## 🔔 反馈模式

### Toast 通知
**适用：** 操作成功/失败的轻量反馈

**位置：** 右上角或底部居中

**类型：**
```
✅ 成功 - 绿色
❌ 错误 - 红色
⚠️ 警告 - 黄色
ℹ️ 信息 - 蓝色
```

**行为：**
- 自动消失（3-5秒）
- 可手动关闭
- 支持操作按钮（撤销）

---

### Modal 对话框
**适用：** 需要用户确认或输入的打断式操作

**使用场景：**
- 删除确认
- 重要设置修改
- 表单提交确认

**设计要点：**
```
┌─────────────────────┐
│ 标题                │
│                     │
│ 内容说明...         │
│                     │
│ [取消]  [确认]      │
└─────────────────────┘
```

**实现：**
```html
<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
    <h3 class="text-lg font-semibold mb-2">确认删除？</h3>
    <p class="text-gray-600 mb-6">此操作无法撤销。</p>
    <div class="flex justify-end gap-3">
      <button class="px-4 py-2 text-gray-600">取消</button>
      <button class="px-4 py-2 bg-red-600 text-white rounded">删除</button>
    </div>
  </div>
</div>
```

---

### 空状态（Empty State）
**适用：** 无数据时的友好提示

**结构：**
```
[插图/图标]
[标题：暂无数据]
[说明：开始创建你的第一个项目]
[操作按钮：创建项目]
```

**设计要点：**
- 不要只显示"暂无数据"
- 解释为什么会出现空状态
- 提供明确的下一步操作
- 使用友好的插图

---

### 加载状态

**骨架屏（Skeleton）：**
```html
<div class="animate-pulse">
  <div class="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
  <div class="h-20 bg-gray-200 rounded mb-4"></div>
  <div class="h-20 bg-gray-200 rounded"></div>
</div>
```

**加载指示器：**
- 按钮内：Spinner
- 页面：进度条或骨架屏
- 列表：底部加载更多

---

## 🔍 搜索与筛选

### 搜索框

**基础版：**
```html
<div class="relative">
  <input type="text" 
         placeholder="搜索..."
         class="w-full pl-10 pr-4 py-2 border rounded-lg" />
  <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400">
    <!-- 搜索图标 -->
  </svg>
</div>
```

**增强版（自动完成）：**
```
[搜索框：输入中...]
┌──────────────────┐
│ 🔍 建议项 1      │
│ 🔍 建议项 2      │
│ 🔍 建议项 3      │
│ ──────────────── │
│ 📋 最近搜索      │
└──────────────────┘
```

---

### 筛选器

**水平筛选栏：**
```
[全部] [活跃] [未激活] [已归档]        [筛选 ▼] [排序 ▼]
```

**筛选面板（侧边）：**
```
筛选
├── 状态
│   ☑ 活跃
│   ☐ 未激活
│
├── 日期
│   [开始] - [结束]
│
└── 类别
    ☑ A类
    ☑ B类
```

---

## 📱 数据展示

### 表格

**基础表格：**
```
┌──────────┬──────────┬──────────┬──────────┐
│ 姓名  ▼  │ 邮箱     │ 状态     │ 操作     │
├──────────┼──────────┼──────────┼──────────┤
│ 张三     │ z@a.com  │ ● 活跃   │ 编辑 删除│
│ 李四     │ l@b.com  │ ○ 未激活 │ 编辑 删除│
└──────────┴──────────┴──────────┴──────────┘
```

**设计要点：**
- 表头加粗 + 排序功能
- 行 hover 效果
- 斑马纹（可选）
- 操作列居右
- 支持横向滚动

---

### 卡片网格

**标准卡片：**
```
┌─────────────────┐
│ [图片]          │
│                 │
│ 标题            │
│ 描述文字...     │
│                 │
│ [标签]    [按钮]│
└─────────────────┘
```

**Tailwind 网格：**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div class="bg-white rounded-lg shadow p-6">
    <!-- 卡片内容 -->
  </div>
</div>
```

---

### 列表

**简单列表：**
```
• 列表项 1
• 列表项 2
• 列表项 3
```

**复杂列表（带头像）：**
```
┌──────────────────────────┐
│ [图] 标题           [操作]│
│      描述               │
├──────────────────────────┤
│ [图] 标题           [操作]│
│      描述               │
└──────────────────────────┘
```

---

## 🎯 操作模式

### 按钮层级

**主要按钮（Primary）：**
- 每个页面/区域只有一个
- 实心填充、品牌色
- 最重要的操作

**次要按钮（Secondary）：**
- 描边样式
- 次要操作

**文字按钮（Text）：**
- 无背景
- 低优先级操作
- 通常是"取消"、"了解更多"

```html
<!-- 主要 -->
<button class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
  保存
</button>

<!-- 次要 -->
<button class="border border-gray-300 px-4 py-2 rounded hover:bg-gray-50">
  取消
</button>

<!-- 文字 -->
<button class="text-blue-600 hover:underline">
  了解更多
</button>
```

---

### 下拉菜单

```
[触发按钮 ▼]
     │
     ▼
┌──────────┐
│ 选项 1   │
│ 选项 2   │
│ ──────── │
│ 危险操作 │
└──────────┘
```

---

### 悬浮操作按钮（FAB）
**适用：** 移动端主要操作

```html
<button class="fixed bottom-6 right-6 w-14 h-14 
               bg-blue-600 text-white rounded-full 
               shadow-lg flex items-center justify-center
               hover:bg-blue-700">
  +
</button>
```

---

## ♿ 可访问性模式

### 键盘导航
- 所有交互元素可聚焦
- Tab 顺序符合视觉顺序
- Enter/Space 激活按钮
- Esc 关闭模态框

### 焦点样式
```css
/* 明显的焦点指示器 */
:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
```

### 语义化 HTML
```html
<!-- 好的 -->
<nav>...</nav>
<main>...</main>
<button>...</button>
<label for="email">邮箱</label>
<input id="email" type="email" aria-describedby="email-error" />
<p id="email-error" role="alert">...</p>

<!-- 避免 -->
<div onclick="...">...</div>
```

---

## 📊 常见场景解决方案

### 登录/注册流程

**登录页：**
```
┌─────────────────────────┐
│        [Logo]           │
│                         │
│      欢迎回来            │
│                         │
│  邮箱                   │
│  [________________]     │
│                         │
│  密码                   │
│  [________________]     │
│  忘记密码？              │
│                         │
│  [    登 录    ]        │
│                         │
│  ──── 或使用 ────       │
│  [G] [GitHub]           │
│                         │
│  还没有账号？立即注册    │
└─────────────────────────┘
```

### 设置页面

**布局：**
```
┌────────┬────────────────┐
│ 账户   │ 账户信息       │
│ 安全   │ ─────────────  │
│ 通知   │ 详细设置...    │
│ 支付   │                │
│ ────── │ [保存更改]     │
│ 退出   │                │
└────────┴────────────────┘
```

---

## 💡 设计原则

1. **一致性** - 相同元素在不同页面表现一致
2. **反馈** - 每个操作都有响应
3. **容错** - 允许撤销，防止误操作
4. **简洁** - 每页只展示必要信息
5. **可预测** - 符合用户心理模型

---

**记住：** 好的 UX 是看不见的，用户不会注意到 UX，只会注意到体验是否顺畅。
