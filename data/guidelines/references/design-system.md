# FTdesign 设计系统完整规范

本文档详细描述FTdesign设计系统的所有规范，包括色彩、排版、间距、组件等各个方面。

## 1. 色彩系统

### 1.1 品牌色

品牌色是FTdesign的核心色彩，用于主要按钮、链接、激活状态等关键交互元素。

```css
--ft-brand-color: #005DEB;         /* 品牌主色 */
--ft-brand-color-hover: #267DFF;   /* 悬停色 */
--ft-brand-color-active: #004BBF;  /* 激活色 */
--ft-brand-color-bg: #EFF0FA;      /* 品牌背景色 */
```

**使用场景**：
- 主按钮背景
- 链接文字颜色
- 激活状态的高亮
- 图标激活状态
- 火柴棍高亮条

### 1.2 中性色（10级灰阶）

中性色用于文本、边框、背景等非强调元素。

```css
--ft-grey-0: #FFFFFF;  /* 纯白 - 页面背景、卡片背景 */
--ft-grey-1: #F7F8FA;  /* 极浅灰 - 表头背景、输入框背景 */
--ft-grey-2: #F2F3F5;  /* 浅灰 - 分隔线、禁用背景 */
--ft-grey-3: #E6E8EC;  /* 中浅灰 - 边框、侧边栏右边框 */
--ft-grey-4: #D1D5DB;  /* 中灰 - 占位符、禁用文字 */
--ft-grey-5: #9CA3AF;  /* 中深灰 - 次要文字、图标 */
--ft-grey-6: #6B7280;  /* 深灰 - 辅助文字 */
--ft-grey-7: #39485E;  /* 较深灰 - 正文文字、菜单文字 */
--ft-grey-8: #1F2937;  /* 很深灰 - 标题文字 */
--ft-grey-9: #111827;  /* 最深灰 - 主标题、强调文字 */
```

**使用场景**：
- grey-0: 页面背景、卡片背景、按钮背景
- grey-1: 表头背景、分隔背景
- grey-2: 分隔线、禁用元素背景
- grey-3: 边框、分割线
- grey-4: 占位符文字、禁用文字
- grey-5: 次要文字、图标
- grey-6: 辅助文字、描述文字
- grey-7: 正文文字、菜单项文字
- grey-8: 标题文字
- grey-9: 主标题、强调文字

### 1.3 功能色

功能色用于表示不同状态和语义。

```css
--ft-success-color: #10B981;  /* 成功 - 绿色 */
--ft-warning-color: #F59E0B;  /* 警告 - 橙色 */
--ft-error-color: #EF4444;   /* 错误 - 红色 */
--ft-info-color: var(--ft-brand-color);  /* 信息 - 使用品牌色 */
```

**使用场景**：
- 成功色：操作成功提示、成功标签
- 警告色：待处理、警告提示、警告标签
- 错误色：操作失败、错误提示、错误标签、删除按钮
- 信息色：一般提示、信息标签

## 2. 排版系统

### 2.1 字体

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

### 2.2 字体大小

```css
--ft-font-size-xs: 12px;   /* 辅助文字 */
--ft-font-size-sm: 13px;  /* 说明文字 */
--ft-font-size-base: 14px; /* 正文文字 */
--ft-font-size-md: 15px;   /* 重要文字 */
--ft-font-size-lg: 16px;   /* 小标题 */
--ft-font-size-xl: 18px;   /* 副标题 */
--ft-font-size-2xl: 20px;  /* 页面标题 */
--ft-font-size-3xl: 24px;  /* 区块标题 */
--ft-font-size-4xl: 28px;   /* 详情页标题 */
--ft-font-size-5xl: 32px;  /* 主标题 */
```

**使用场景**：
- 12px: 菜单组标题、辅助说明
- 13px: 帮助文字、错误提示
- 14px: 正文、表单标签、按钮文字
- 15px: 详情内容
- 16px: 表单分组标题
- 18px: 详情页小节标题
- 20px: 页面标题
- 24px: 章节标题
- 28px: 详情页主标题
- 32px: 设计规范页面主标题

### 2.3 字重

```css
--ft-font-weight-normal: 400;   /* 常规 */
--ft-font-weight-medium: 500;  /* 中等 - 激活菜单、面包屑 */
--ft-font-weight-semibold: 600; /* 半粗 - 标题 */
```

### 2.4 行高

```css
--ft-line-height-tight: 1.4;  /* 紧凑 - 标题 */
--ft-line-height-base: 1.5;  /* 标准 - 正文 */
--ft-line-height-relaxed: 1.8; /* 宽松 - 文章内容 */
```

## 3. 间距系统

### 3.1 基础间距

```css
--ft-spacing-xs: 4px;
--ft-spacing-sm: 8px;
--ft-spacing-md: 12px;
--ft-spacing-lg: 16px;
--ft-spacing-xl: 24px;
--ft-spacing-2xl: 32px;
--ft-spacing-3xl: 48px;
```

**使用场景**：
- 4px: 图标与文字间距、标签padding
- 8px: 表单项间距、按钮间距
- 12px: 表格单元格padding、标签padding
- 16px: 组件间距、表单项间距
- 24px: 页面padding、卡片padding
- 32px: 表单操作按钮间距、卡片padding
- 48px: 页面顶部padding

### 3.2 布局尺寸

```css
--ft-sidebar-width: 240px;   /* 侧边栏宽度 */
--ft-header-height: 64px;   /* 页头高度 */
--ft-component-height: 32px; /* 组件统一高度 */
```

## 4. 阴影与圆角

### 4.1 阴影

```css
--ft-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--ft-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--ft-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
```

**使用场景**：
- shadow-sm: 卡片阴影、轻悬浮效果
- shadow-md: 下拉菜单、弹窗阴影
- shadow-lg: 模态框阴影

### 4.2 圆角

```css
--ft-radius-sm: 2px;  /* 小圆角 - 按钮、输入框 */
--ft-radius-md: 4px;  /* 中圆角 - 卡片、弹窗 */
--ft-radius-lg: 8px;  /* 大圆角 - 容器 */
```

**使用场景**：
- 2px: 按钮、输入框、表格单元格
- 4px: 卡片、标签、弹窗
- 8px: 大容器、特殊组件

## 5. 布局规范

### 5.1 固定侧边栏布局

```css
/* 侧边栏 */
.ft-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 240px;
    height: 100vh;
    background: #FFFFFF;
    border-right: 1px solid #E6E8EC;
    z-index: 1000;
    display: flex;
    flex-direction: column;
}

/* 主内容区 */
.ft-main {
    margin-left: 240px;
    min-height: 100vh;
}
```

**重要**：
- 禁止在React组件根元素使用display:flex
- 禁止在#root容器使用flex布局
- 主内容区使用margin-left而非flex布局

### 5.2 页头结构

```css
.ft-page-header {
    background: #FFFFFF;
    padding: 24px;
    border-bottom: 1px solid #F2F3F5;
}

.ft-page-title {
    font-size: 20px;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 8px;
}

.ft-breadcrumb {
    font-size: 14px;
    color: #9CA3AF;
}
```

### 5.3 内容卡片

```css
.ft-page-content {
    padding: 24px;
}

.ft-card {
    background: #FFFFFF;
    border-radius: 2px;
    padding: 32px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    border: 1px solid #F2F3F5;
}
```

### 5.4 筛选区和操作区

```css
.ft-filter-section {
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.ft-filter-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}
```

## 6. 侧边栏规范

### 6.1 浅色侧边栏（强制要求）

```css
.ft-sidebar {
    background: #FFFFFF;              /* var(--ft-grey-0) */
    border-right: 1px solid #E6E8EC; /* var(--ft-grey-3) */
}

.ft-menu-item {
    color: #39485E;                   /* var(--ft-grey-7) */
}

.ft-menu-item.active {
    background: #EFF0FA;              /* var(--ft-brand-color-bg) */
    color: #005DEB;                   /* var(--ft-brand-color) */
}

.ft-menu-item.active::before {
    width: 2px;
    height: 16px;
    background: #005DEB;              /* var(--ft-brand-color) */
}
```

### 6.2 侧边栏菜单图标

所有菜单项必须包含图标，参考图标映射：

| 菜单项 | 图标类名 |
|-------|---------|
| 仪表盘 | ri-dashboard-line |
| 用户管理 | ri-user-line |
| 角色管理 | ri-team-line |
| 权限管理 | ri-shield-check-line |
| 系统设置 | ri-settings-3-line |
| 文章管理 | ri-file-list-3-line |
| 分类管理 | ri-folder-line |
| 订单管理 | ri-shopping-cart-line |
| 商品管理 | ri-store-2-line |
| 财务管理 | ri-money-cny-circle-line |
| 数据统计 | ri-bar-chart-line |
| 日志管理 | ri-file-list-line |

## 7. 组件规范

### 7.1 按钮组件

#### 统一高度：32px

```css
.ft-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 32px;
    padding: 0 15px;
    font-size: 14px;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    background: transparent;
    color: #39485E;
    user-select: none;
    text-decoration: none;
}

.ft-btn i {
    margin-right: 4px;
}
```

#### 按钮类型

```css
/* 主按钮 */
.ft-btn-primary {
    background: #005DEB;
    color: #fff;
    border-color: #005DEB;
}
.ft-btn-primary:hover { background: #267DFF; border-color: #267DFF; }
.ft-btn-primary:active { background: #004BBF; border-color: #004BBF; }

/* 次按钮 */
.ft-btn-default {
    background: #fff;
    border-color: #E6E8EC;
    color: #39485E;
}
.ft-btn-default:hover { color: #005DEB; border-color: #005DEB; }

/* 虚线按钮 */
.ft-btn-dashed {
    background: #fff;
    border-color: #E6E8EC;
    border-style: dashed;
    color: #39485E;
}
.ft-btn-dashed:hover { color: #005DEB; border-color: #005DEB; }

/* 链接按钮 */
.ft-btn-link {
    color: #005DEB;
    padding: 0 4px;
    height: auto;
}
.ft-btn-link:hover { color: #267DFF; }
```

### 7.2 表单组件

#### 输入框（统一高度：32px）

```css
.ft-input {
    height: 32px;
    padding: 4px 12px;
    font-size: 14px;
    border: 1px solid #E6E8EC;
    border-radius: 2px;
    background-color: #fff;
    transition: all 0.3s;
    color: #39485E;
    outline: none;
    min-width: 200px;
}

.ft-input:hover { border-color: #005DEB; }
.ft-input:focus { 
    border-color: #005DEB; 
    box-shadow: 0 0 0 2px rgba(0, 93, 235, 0.1); 
}
.ft-input::placeholder { color: #D1D5DB; }
```

#### 选择框（统一高度：32px，箭头right:12px）

```css
.ft-select {
    position: relative;
    height: 32px;
    padding: 0 32px 0 12px;
    font-size: 14px;
    border: 1px solid #E6E8EC;
    border-radius: 2px;
    background-color: #fff;
    cursor: pointer;
    transition: all 0.3s;
    color: #39485E;
    appearance: none;
    min-width: 150px;
}

.ft-select:hover { border-color: #005DEB; }
.ft-select:focus { 
    border-color: #005DEB; 
    box-shadow: 0 0 0 2px rgba(0, 93, 235, 0.1); 
}
```

#### 文本域

```css
.ft-textarea {
    width: 100%;
    min-height: 120px;
    padding: 8px 12px;
    font-size: 14px;
    border: 1px solid #E6E8EC;
    border-radius: 2px;
    background-color: #fff;
    transition: all 0.3s;
    color: #39485E;
    outline: none;
    resize: vertical;
    font-family: inherit;
}

.ft-textarea:hover { border-color: #005DEB; }
.ft-textarea:focus { 
    border-color: #005DEB; 
    box-shadow: 0 0 0 2px rgba(0, 93, 235, 0.1); 
}
```

#### 表单标签

```css
.ft-label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
    color: #1F2937;
}

.ft-label-required::before {
    content: '*';
    color: #EF4444;
    margin-right: 4px;
}
```

### 7.3 表格组件

```css
.ft-table-wrapper {
    overflow-x: auto;
}

.ft-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background: #fff;
}

.ft-table th {
    background-color: #F7F8FA;
    color: #1F2937;
    font-weight: 500;
    text-align: left;
    padding: 12px 16px;
    border-bottom: 1px solid #E6E8EC;
}

.ft-table td {
    padding: 12px 16px;
    border-bottom: 1px solid #F2F3F5;
    color: #39485E;
}

.ft-table tr:hover td {
    background-color: #F7F8FA;
}
```

### 7.4 标签组件

```css
.ft-tag {
    display: inline-flex;
    align-items: center;
    padding: 0 8px;
    height: 22px;
    font-size: 12px;
    border-radius: 2px;
    border: 1px solid #E6E8EC;
    background: #F7F8FA;
    color: #39485E;
}

/* 成功标签 */
.ft-tag-success {
    background: #ECFDF5;
    border-color: #10B981;
    color: #10B981;
}

/* 警告标签 */
.ft-tag-warning {
    background: #FFFBEB;
    border-color: #F59E0B;
    color: #F59E0B;
}

/* 错误标签 */
.ft-tag-error {
    background: #FEF2F2;
    border-color: #EF4444;
    color: #EF4444;
}
```

### 7.5 分页组件

```css
.ft-pagination {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 8px;
    padding: 16px 24px;
    background: #FFFFFF;
    border-top: 1px solid #F2F3F5;
}

.ft-page-item {
    min-width: 32px;
    height: 32px;
    padding: 0 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #E6E8EC;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 14px;
    color: #39485E;
    background: #fff;
}

.ft-page-item:hover {
    border-color: #005DEB;
    color: #005DEB;
}

.ft-page-item.active {
    background: #005DEB;
    color: #fff;
    border-color: #005DEB;
}
```

## 8. 禁止事项

1. **禁止使用Emoji表情符号**：统一使用Remix Icon图标库
2. **禁止自定义组件尺寸**：组件高度统一为32px
3. **禁止混合技术栈**：纯CSS模式不得混用框架类名
4. **禁止深色侧边栏**：侧边栏必须使用浅色风格
5. **禁止缺失菜单图标**：所有侧边栏菜单项必须包含图标
6. **禁止在#root使用flex**：主内容区使用margin-left布局

## 9. 资源引用

### 9.1 Remix Icon

```html
<link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
```

### 9.2 Google Fonts

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

## 10. 版本信息

- 版本：1.0.0
- 最后更新：2024-02-26
- 适用FTdesign版本：完整版
