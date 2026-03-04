# FTdesign 组件使用指南和API

本文档详细说明FTdesign各个组件的使用方法和API。

## 1. 按钮组件 (ft-btn)

### 基础用法

```html
<!-- 主按钮 -->
<button class="ft-btn ft-btn-primary">
    <i class="ri-save-line"></i>保存
</button>

<!-- 次按钮 -->
<button class="ft-btn ft-btn-default">
    <i class="ri-refresh-line"></i>重置
</button>

<!-- 虚线按钮 -->
<button class="ft-btn ft-btn-dashed">
    <i class="ri-add-line"></i>新建
</button>

<!-- 链接按钮 -->
<a href="#" class="ft-btn ft-btn-link">
    <i class="ri-eye-line"></i>查看
</a>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-btn` | 基础按钮类 |
| `ft-btn-primary` | 主按钮 |
| `ft-btn-default` | 次按钮 |
| `ft-btn-dashed` | 虚线按钮 |
| `ft-btn-link` | 链接按钮 |

### 注意事项

- 统一高度：32px
- 图标与文字间距：4px（`margin-right: 4px`）
- 必须包含图标（使用Remix Icon）

### 常用图标

```html
<!-- 操作类 -->
<i class="ri-add-line"></i>        <!-- 新建 -->
<i class="ri-edit-line"></i>        <!-- 编辑 -->
<i class="ri-delete-bin-line"></i>  <!-- 删除 -->
<i class="ri-save-line"></i>        <!-- 保存 -->
<i class="ri-refresh-line"></i>     <!-- 重置 -->
<i class="ri-search-line"></i>      <!-- 查询 -->
<i class="ri-eye-line"></i>         <!-- 查看 -->
<i class="ri-download-line"></i>    <!-- 下载 -->
<i class="ri-upload-line"></i>      <!-- 上传 -->

<!-- 导航类 -->
<i class="ri-arrow-left-line"></i>  <!-- 返回 -->
<i class="ri-arrow-right-line"></i> <!-- 下一步 -->
<i class="ri-arrow-up-line"></i>    <!-- 上一步 -->
<i class="ri-home-line"></i>        <!-- 首页 -->
```

## 2. 输入框组件 (ft-input)

### 基础用法

```html
<!-- 文本输入 -->
<input type="text" class="ft-input" placeholder="请输入用户名">

<!-- 邮箱输入 -->
<input type="email" class="ft-input" placeholder="请输入邮箱">

<!-- 数字输入 -->
<input type="number" class="ft-input" placeholder="请输入数量">

<!-- 日期输入 -->
<input type="date" class="ft-input">
```

### 带标签

```html
<div class="ft-form-item">
    <label class="ft-label">用户名</label>
    <input type="text" class="ft-input" placeholder="请输入用户名">
</div>
```

### 必填项

```html
<div class="ft-form-item">
    <label class="ft-label ft-label-required">用户名</label>
    <input type="text" class="ft-input" placeholder="请输入用户名">
</div>
```

### 带帮助文字

```html
<div class="ft-form-item">
    <label class="ft-label">用户名</label>
    <input type="text" class="ft-input" placeholder="请输入用户名">
    <div class="ft-form-help">用户名长度为4-20个字符</div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-input` | 输入框基础类 |
| `ft-label` | 标签 |
| `ft-label-required` | 必填标签 |
| `ft-form-item` | 表单项容器 |
| `ft-form-help` | 帮助文字 |

### 属性

| 属性 | 默认值 | 说明 |
|-----|--------|------|
| height | 32px | 输入框高度 |
| min-width | 200px | 最小宽度 |
| padding | 4px 12px | 内边距 |

## 3. 选择框组件 (ft-select)

### 基础用法

```html
<select class="ft-select">
    <option>请选择</option>
    <option>选项1</option>
    <option>选项2</option>
</select>
```

### 带标签

```html
<div class="ft-form-item">
    <label class="ft-label ft-label-required">角色</label>
    <select class="ft-select">
        <option>请选择角色</option>
        <option>管理员</option>
        <option>普通用户</option>
    </select>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-select` | 选择框基础类 |

### 属性

| 属性 | 默认值 | 说明 |
|-----|--------|------|
| height | 32px | 高度 |
| min-width | 150px | 最小宽度 |
| arrow-position | right 8px | 箭头位置 |

## 4. 文本域组件 (ft-textarea)

### 基础用法

```html
<textarea class="ft-textarea" placeholder="请输入描述"></textarea>
```

### 带标签

```html
<div class="ft-form-item">
    <label class="ft-label">描述</label>
    <textarea class="ft-textarea" placeholder="请输入描述"></textarea>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-textarea` | 文本域基础类 |

### 属性

| 属性 | 默认值 | 说明 |
|-----|--------|------|
| min-height | 120px | 最小高度 |
| resize | vertical | 可调整方向（vertical/horizontal/none） |

## 5. 单选框组件 (ft-radio)

### 基础用法

```html
<div class="ft-radio-group">
    <label class="ft-radio">
        <input type="radio" name="status" value="1">
        <span>启用</span>
    </label>
    <label class="ft-radio">
        <input type="radio" name="status" value="0">
        <span>禁用</span>
    </label>
</div>
```

### 默认选中

```html
<label class="ft-radio">
    <input type="radio" name="status" value="1" checked>
    <span>启用</span>
</label>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-radio-group` | 单选框组 |
| `ft-radio` | 单选项 |

## 6. 复选框组件 (ft-checkbox)

### 基础用法

```html
<div class="ft-checkbox-group">
    <label class="ft-checkbox">
        <input type="checkbox" checked>
        <span>允许评论</span>
    </label>
    <label class="ft-checkbox">
        <input type="checkbox">
        <span>推荐到首页</span>
    </label>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-checkbox-group` | 复选框组 |
| `ft-checkbox` | 复选项 |

## 7. 表格组件 (ft-table)

### 基础用法

```html
<div class="ft-table-wrapper">
    <table class="ft-table">
        <thead>
            <tr>
                <th style="width: 60px;">ID</th>
                <th>用户名</th>
                <th style="width: 180px;">操作</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1001</td>
                <td>张三</td>
                <td>
                    <div class="ft-table-actions">
                        <a href="#" class="ft-btn ft-btn-link">查看</a>
                        <a href="#" class="ft-btn ft-btn-link">编辑</a>
                        <button class="ft-btn ft-btn-link" style="color: #EF4444;">删除</button>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

### 带状态标签

```html
<tr>
    <td>1001</td>
    <td>张三</td>
    <td>
        <span class="ft-tag ft-tag-success">已启用</span>
    </td>
</tr>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-table-wrapper` | 表格外层容器（支持横向滚动） |
| `ft-table` | 表格基础类 |
| `ft-table-actions` | 操作按钮容器 |
| `ft-tag` | 标签基础类 |
| `ft-tag-success` | 成功标签（绿色） |
| `ft-tag-warning` | 警告标签（橙色） |
| `ft-tag-error` | 错误标签（红色） |

### 列宽建议

| 列类型 | 建议宽度 |
|-------|---------|
| ID列 | 60px |
| 状态列 | 100px |
| 时间列 | 160px |
| 操作列 | 180px |
| 其他列 | 自适应 |

## 8. 分页组件 (ft-pagination)

### 基础用法

```html
<div class="ft-pagination">
    <span style="color: #9CA3AF; margin-right: 16px;">共 47 条</span>
    <div class="ft-page-item">
        <i class="ri-arrow-left-s-line"></i>
    </div>
    <div class="ft-page-item active">1</div>
    <div class="ft-page-item">2</div>
    <div class="ft-page-item">3</div>
    <div class="ft-page-item">
        <i class="ri-arrow-right-s-line"></i>
    </div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-pagination` | 分页容器 |
| `ft-page-item` | 分页项 |
| `active` | 激活状态 |

## 9. 标签组件 (ft-tag)

### 基础用法

```html
<span class="ft-tag">默认</span>
<span class="ft-tag ft-tag-success">成功</span>
<span class="ft-tag ft-tag-warning">警告</span>
<span class="ft-tag ft-tag-error">错误</span>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-tag` | 标签基础类 |
| `ft-tag-success` | 成功标签（绿色） |
| `ft-tag-warning` | 警告标签（橙色） |
| `ft-tag-error` | 错误标签（红色） |

### 属性

| 属性 | 默认值 | 说明 |
|-----|--------|------|
| height | 22px | 标签高度 |
| padding | 0 8px | 内边距 |

## 10. 侧边栏组件 (ft-sidebar)

### 基础结构

```html
<aside class="ft-sidebar">
    <div class="ft-sidebar-logo">
        <i class="ri-box-3-fill"></i>
        <span>系统名称</span>
    </div>
    <nav class="ft-sidebar-menu">
        <div class="ft-menu-group">主菜单</div>
        <a href="#" class="ft-menu-item">
            <i class="ri-dashboard-line"></i>工作台
        </a>
        <a href="#" class="ft-menu-item active">
            <i class="ri-user-line"></i>用户管理
        </a>
    </nav>
</aside>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-sidebar` | 侧边栏容器 |
| `ft-sidebar-logo` | Logo区域 |
| `ft-sidebar-menu` | 菜单区域 |
| `ft-menu-group` | 菜单组标题 |
| `ft-menu-item` | 菜单项 |
| `active` | 激活状态 |

### 图标映射

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

## 11. 页头组件 (ft-page-header)

### 基础用法

```html
<div class="ft-page-header">
    <div class="ft-breadcrumb">
        <span>首页</span>
        <span style="margin: 0 8px;">/</span>
        <span>用户管理</span>
    </div>
    <div class="ft-page-title">用户列表</div>
</div>
```

### 带操作按钮

```html
<div class="ft-page-header">
    <div class="ft-breadcrumb">
        <span>首页</span>
        <span style="margin: 0 8px;">/</span>
        <span>用户管理</span>
    </div>
    <div class="ft-page-header-top">
        <div class="ft-page-title">用户详情</div>
        <div style="display: flex; gap: 8px;">
            <a href="#" class="ft-btn ft-btn-primary">
                <i class="ri-edit-line"></i>编辑
            </a>
            <a href="#" class="ft-btn ft-btn-default">
                <i class="ri-arrow-left-line"></i>返回列表
            </a>
        </div>
    </div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-page-header` | 页头容器 |
| `ft-page-header-top` | 页头顶部区域（用于带操作按钮） |
| `ft-breadcrumb` | 面包屑导航 |
| `ft-page-title` | 页面标题 |

## 12. 卡片组件 (ft-card)

### 基础用法

```html
<div class="ft-card">
    <h3 style="font-size: 18px; margin-bottom: 24px;">卡片标题</h3>
    <p>卡片内容...</p>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-card` | 卡片容器 |

### 属性

| 属性 | 默认值 | 说明 |
|-----|--------|------|
| padding | 32px | 内边距 |
| border-radius | 2px | 圆角 |

## 13. 详情页组件

### 信息网格

```html
<div class="ft-info-grid">
    <div class="ft-info-label">用户ID：</div>
    <div class="ft-info-value">1001</div>

    <div class="ft-info-label">用户名：</div>
    <div class="ft-info-value">张三</div>

    <div class="ft-info-label">邮箱：</div>
    <div class="ft-info-value">zhangsan@example.com</div>
</div>
```

### 详情头部

```html
<div class="ft-detail-header">
    <div class="ft-detail-title">如何构建高性能的前端应用</div>
    <div class="ft-detail-meta">
        <div class="ft-meta-item">
            <i class="ri-user-line"></i>
            <span>张三</span>
        </div>
        <div class="ft-meta-item">
            <i class="ri-time-line"></i>
            <span>2024-02-05 10:30</span>
        </div>
        <span class="ft-tag ft-tag-success">已发布</span>
    </div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-detail-header` | 详情头部 |
| `ft-detail-title` | 详情标题 |
| `ft-detail-meta` | 元数据区域 |
| `ft-meta-item` | 元数据项 |
| `ft-info-grid` | 信息网格 |
| `ft-info-label` | 信息标签 |
| `ft-info-value` | 信息值 |

## 14. 富文本编辑器（模拟）

```html
<div class="ft-editor">
    <div class="ft-editor-toolbar">
        <div class="ft-editor-btn"><i class="ri-bold"></i></div>
        <div class="ft-editor-btn"><i class="ri-italic"></i></div>
        <div class="ft-editor-btn"><i class="ri-underline"></i></div>
        <div style="width: 1px; height: 20px; background: #E6E8EC; margin: 0 4px;"></div>
        <div class="ft-editor-btn"><i class="ri-h-1"></i></div>
        <div class="ft-editor-btn"><i class="ri-h-2"></i></div>
        <div style="width: 1px; height: 20px; background: #E6E8EC; margin: 0 4px;"></div>
        <div class="ft-editor-btn"><i class="ri-list-unordered"></i></div>
        <div class="ft-editor-btn"><i class="ri-list-ordered"></i></div>
    </div>
    <div class="ft-editor-content" contenteditable="true">
        <p>编辑器内容...</p>
    </div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-editor` | 编辑器容器 |
| `ft-editor-toolbar` | 工具栏 |
| `ft-editor-btn` | 工具栏按钮 |
| `ft-editor-content` | 编辑区域 |

## 15. 文件上传组件

```html
<div class="ft-upload">
    <div class="ft-upload-btn">
        <i class="ri-image-add-line"></i>
    </div>
    <div class="ft-form-help">支持 JPG、PNG 格式</div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-upload` | 上传容器 |
| `ft-upload-btn` | 上传按钮区域 |

## 16. 筛选区组件

```html
<div class="ft-filter-section">
    <div class="ft-filter-row">
        <div class="ft-filter-item">
            <label>用户名：</label>
            <input type="text" class="ft-input" placeholder="请输入用户名">
        </div>
        <div class="ft-filter-item">
            <label>状态：</label>
            <select class="ft-select">
                <option>全部</option>
                <option>启用</option>
                <option>禁用</option>
            </select>
        </div>
    </div>
    <div class="ft-filter-row">
        <button class="ft-btn ft-btn-primary">
            <i class="ri-search-line"></i>查询
        </button>
        <button class="ft-btn ft-btn-default">
            <i class="ri-refresh-line"></i>重置
        </button>
        <div style="flex: 1;"></div>
        <a href="#" class="ft-btn ft-btn-primary">
            <i class="ri-add-line"></i>新建
        </a>
    </div>
</div>
```

### API

| 类名 | 说明 |
|-----|------|
| `ft-filter-section` | 筛选区容器 |
| `ft-filter-row` | 筛选行 |
| `ft-filter-item` | 筛选项 |

## 注意事项

1. **组件尺寸统一性**：所有按钮、输入框、选择框高度统一为32px
2. **图标完整性**：所有菜单项和按钮必须包含图标
3. **颜色规范**：必须使用CSS变量系统，禁止硬编码颜色
4. **禁止使用Emoji**：统一使用Remix Icon图标库
5. **交互状态**：组件必须包含hover、focus、active状态

## 版本信息

- 版本：1.0.0
- 最后更新：2024-02-26
