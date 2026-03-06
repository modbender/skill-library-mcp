# FTdesign 代码示例库

本文档提供FTdesign各个组件的实际代码示例，可直接复制使用。

## 1. 列表页完整示例

### 用户管理列表页

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用户管理</title>
    <link href="https://cdn.jsdelivr.net/npm/remixicon@3.5.0/fonts/remixicon.css" rel="stylesheet">
    <style>
        /* CSS变量和样式...（参考完整模板）*/
    </style>
</head>
<body>
    <!-- 侧边栏 -->
    <aside class="ft-sidebar">
        <div class="ft-sidebar-logo">
            <i class="ri-user-fill"></i>
            <span>用户管理系统</span>
        </div>
        <nav class="ft-sidebar-menu">
            <div class="ft-menu-group">主菜单</div>
            <a href="#" class="ft-menu-item"><i class="ri-dashboard-line"></i>工作台</a>
            <a href="#" class="ft-menu-item active"><i class="ri-user-line"></i>用户管理</a>
            <a href="#" class="ft-menu-item"><i class="ri-team-line"></i>角色管理</a>
            <a href="#" class="ft-menu-item"><i class="ri-shield-check-line"></i>权限管理</a>
        </nav>
    </aside>

    <!-- 主内容区 -->
    <main class="ft-main">
        <div class="ft-page-header">
            <div class="ft-breadcrumb">
                <span>首页</span>
                <span style="margin: 0 8px;">/</span>
                <span>用户管理</span>
            </div>
            <div class="ft-page-title">用户列表</div>
        </div>

        <div class="ft-page-content">
            <div class="ft-card">
                <!-- 筛选区 -->
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
                            <i class="ri-add-line"></i>新建用户
                        </a>
                    </div>
                </div>

                <!-- 表格 -->
                <div class="ft-table-wrapper">
                    <table class="ft-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">ID</th>
                                <th>用户名</th>
                                <th>邮箱</th>
                                <th>角色</th>
                                <th style="width: 100px;">状态</th>
                                <th style="width: 160px;">注册时间</th>
                                <th style="width: 180px;">操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>1001</td>
                                <td>张三</td>
                                <td>zhangsan@example.com</td>
                                <td>管理员</td>
                                <td><span class="ft-tag ft-tag-success">启用</span></td>
                                <td>2024-02-05 10:30</td>
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

                <!-- 分页 -->
                <div class="ft-pagination">
                    <span style="color: #9CA3AF; margin-right: 16px;">共 47 条</span>
                    <div class="ft-page-item"><i class="ri-arrow-left-s-line"></i></div>
                    <div class="ft-page-item active">1</div>
                    <div class="ft-page-item">2</div>
                    <div class="ft-page-item">3</div>
                    <div class="ft-page-item"><i class="ri-arrow-right-s-line"></i></div>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
```

## 2. 表单页完整示例

### 新建用户表单

```html
<!-- 表单区域 -->
<div class="ft-page-content">
    <div class="ft-card">
        <form>
            <h3 style="font-size: 16px; margin-bottom: 24px; color: #1F2937;">基础信息</h3>

            <div class="ft-form-item">
                <label class="ft-label ft-label-required">用户名</label>
                <input type="text" class="ft-input" placeholder="请输入用户名">
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="ft-form-item">
                    <label class="ft-label ft-label-required">邮箱</label>
                    <input type="email" class="ft-input" placeholder="请输入邮箱">
                </div>
                <div class="ft-form-item">
                    <label class="ft-label ft-label-required">手机号</label>
                    <input type="text" class="ft-input" placeholder="请输入手机号">
                </div>
            </div>

            <div class="ft-form-item">
                <label class="ft-label">角色</label>
                <select class="ft-select">
                    <option>请选择角色</option>
                    <option>管理员</option>
                    <option>普通用户</option>
                </select>
            </div>

            <div class="ft-form-item">
                <label class="ft-label">状态</label>
                <div class="ft-radio-group">
                    <label class="ft-radio">
                        <input type="radio" name="status" value="1" checked>
                        <span>启用</span>
                    </label>
                    <label class="ft-radio">
                        <input type="radio" name="status" value="0">
                        <span>禁用</span>
                    </label>
                </div>
            </div>

            <div class="ft-form-item">
                <label class="ft-label">备注</label>
                <textarea class="ft-textarea" placeholder="请输入备注"></textarea>
            </div>

            <div class="ft-form-actions">
                <button type="submit" class="ft-btn ft-btn-primary">
                    <i class="ri-save-line"></i>保存
                </button>
                <button type="button" class="ft-btn ft-btn-default">
                    <i class="ri-refresh-line"></i>重置
                </button>
                <a href="#" class="ft-btn ft-btn-default">取消</a>
            </div>
        </form>
    </div>
</div>
```

## 3. 详情页完整示例

### 用户详情页

```html
<div class="ft-page-content">
    <!-- 基本信息卡片 -->
    <div class="ft-card">
        <div class="ft-detail-header">
            <div class="ft-detail-title">张三</div>
            <div class="ft-detail-meta">
                <div class="ft-meta-item">
                    <i class="ri-user-line"></i>
                    <span>用户ID: 1001</span>
                </div>
                <div class="ft-meta-item">
                    <i class="ri-time-line"></i>
                    <span>注册时间: 2024-02-05 10:30</span>
                </div>
                <span class="ft-tag ft-tag-success">启用</span>
            </div>
        </div>

        <div class="ft-info-grid">
            <div class="ft-info-label">用户名：</div>
            <div class="ft-info-value">张三</div>

            <div class="ft-info-label">邮箱：</div>
            <div class="ft-info-value">zhangsan@example.com</div>

            <div class="ft-info-label">手机号：</div>
            <div class="ft-info-value">13800138000</div>

            <div class="ft-info-label">角色：</div>
            <div class="ft-info-value">管理员</div>

            <div class="ft-info-label">最后登录：</div>
            <div class="ft-info-value">2024-02-26 15:30:00</div>

            <div class="ft-info-label">备注：</div>
            <div class="ft-info-value">系统管理员</div>
        </div>
    </div>
</div>
```

## 4. 组件组合示例

### 带操作按钮的页头

```html
<div class="ft-page-header">
    <div class="ft-breadcrumb">
        <span>首页</span>
        <span style="margin: 0 8px;">/</span>
        <span>用户管理</span>
        <span style="margin: 0 8px;">/</span>
        <span>用户详情</span>
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

### 复杂的筛选区

```html
<div class="ft-filter-section">
    <div class="ft-filter-row">
        <div class="ft-filter-item">
            <label>用户名：</label>
            <input type="text" class="ft-input" placeholder="请输入用户名">
        </div>
        <div class="ft-filter-item">
            <label>邮箱：</label>
            <input type="email" class="ft-input" placeholder="请输入邮箱">
        </div>
        <div class="ft-filter-item">
            <label>角色：</label>
            <select class="ft-select">
                <option>全部</option>
                <option>管理员</option>
                <option>普通用户</option>
            </select>
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
        <div class="ft-filter-item">
            <label>注册时间：</label>
            <input type="date" class="ft-input">
        </div>
        <div class="ft-filter-item">
            <label>至</label>
            <input type="date" class="ft-input">
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
            <i class="ri-add-line"></i>新建用户
        </a>
        <button class="ft-btn ft-btn-default">
            <i class="ri-download-line"></i>导出
        </button>
    </div>
</div>
```

### 表格带多种操作按钮

```html
<table class="ft-table">
    <thead>
        <tr>
            <th style="width: 60px;">ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th style="width: 100px;">状态</th>
            <th style="width: 180px;">操作</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1001</td>
            <td>张三</td>
            <td>zhangsan@example.com</td>
            <td>管理员</td>
            <td><span class="ft-tag ft-tag-success">启用</span></td>
            <td>
                <div class="ft-table-actions">
                    <a href="#" class="ft-btn ft-btn-link">查看</a>
                    <a href="#" class="ft-btn ft-btn-link">编辑</a>
                    <button class="ft-btn ft-btn-link" style="color: #F59E0B;">禁用</button>
                    <button class="ft-btn ft-btn-link" style="color: #EF4444;">删除</button>
                </div>
            </td>
        </tr>
    </tbody>
</table>
```

### 表单分组

```html
<div class="ft-page-content">
    <div class="ft-card">
        <form>
            <!-- 基础信息 -->
            <h3 style="font-size: 16px; margin-bottom: 24px; color: #1F2937;">基础信息</h3>
            <div class="ft-form-item">
                <label class="ft-label ft-label-required">用户名</label>
                <input type="text" class="ft-input" placeholder="请输入用户名">
            </div>

            <!-- 联系信息 -->
            <h3 style="font-size: 16px; margin: 32px 0 24px; color: #1F2937;">联系信息</h3>
            <div class="ft-form-item">
                <label class="ft-label">邮箱</label>
                <input type="email" class="ft-input" placeholder="请输入邮箱">
            </div>

            <!-- 系统设置 -->
            <h3 style="font-size: 16px; margin: 32px 0 24px; color: #1F2937;">系统设置</h3>
            <div class="ft-form-item">
                <label class="ft-label">角色</label>
                <select class="ft-select">
                    <option>请选择角色</option>
                    <option>管理员</option>
                </select>
            </div>
        </form>
    </div>
</div>
```

### 详情页多卡片布局

```html
<div class="ft-page-content">
    <!-- 基本信息卡片 -->
    <div class="ft-card">
        <h3 style="font-size: 18px; margin-bottom: 24px;">基本信息</h3>
        <div class="ft-info-grid">
            <div class="ft-info-label">用户名：</div>
            <div class="ft-info-value">张三</div>
            <!-- 更多信息... -->
        </div>
    </div>

    <!-- 账户信息卡片 -->
    <div class="ft-card">
        <h3 style="font-size: 18px; margin-bottom: 24px;">账户信息</h3>
        <div class="ft-info-grid">
            <div class="ft-info-label">最后登录：</div>
            <div class="ft-info-value">2024-02-26 15:30:00</div>
            <!-- 更多信息... -->
        </div>
    </div>

    <!-- 操作历史卡片 -->
    <div class="ft-card">
        <h3 style="font-size: 18px; margin-bottom: 24px;">操作历史</h3>
        <div style="display: flex; flex-direction: column; gap: 12px;">
            <div style="display: flex; gap: 16px; padding: 12px; background: #F7F8FA; border-radius: 4px;">
                <div style="color: #9CA3AF; font-size: 13px; min-width: 140px;">2024-02-26 15:30</div>
                <div style="font-size: 14px; color: #39485E;">张三 更新了账户信息</div>
            </div>
        </div>
    </div>
</div>
```

## 5. 响应式布局示例

```css
/* 桌面端（默认） */
.ft-filter-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
}

/* 平板端 */
@media (max-width: 768px) {
    .ft-filter-row {
        flex-direction: column;
    }
    
    .ft-filter-item {
        width: 100%;
    }
    
    .ft-form-item {
        margin-bottom: 16px;
    }
}

/* 移动端 */
@media (max-width: 480px) {
    .ft-sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s;
    }
    
    .ft-main {
        margin-left: 0;
    }
    
    .ft-table-wrapper {
        overflow-x: auto;
    }
}
```

## 6. 常用代码片段

### 表格空状态

```html
<tr>
    <td colspan="7" style="text-align: center; padding: 48px; color: #9CA3AF;">
        <i class="ri-inbox-line" style="font-size: 48px; display: block; margin-bottom: 16px;"></i>
        <div>暂无数据</div>
    </td>
</tr>
```

### 加载状态

```html
<div style="text-align: center; padding: 48px;">
    <i class="ri-loader-4-line" style="font-size: 32px; color: #005DEB; animation: spin 1s linear infinite;"></i>
    <div style="color: #6B7280; margin-top: 8px;">加载中...</div>
</div>

<style>
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
</style>
```

### 确认删除对话框

```html
<div class="ft-card" style="padding: 24px;">
    <div style="text-align: center;">
        <i class="ri-error-warning-line" style="font-size: 48px; color: #F59E0B; margin-bottom: 16px;"></i>
        <h3 style="font-size: 18px; margin-bottom: 8px; color: #1F2937;">确认删除</h3>
        <p style="color: #6B7280; margin-bottom: 24px;">确定要删除这条数据吗？删除后无法恢复。</p>
        <div style="display: flex; justify-content: center; gap: 8px;">
            <button class="ft-btn ft-btn-primary">确定</button>
            <button class="ft-btn ft-btn-default">取消</button>
        </div>
    </div>
</div>
```

## 版本信息

- 版本：1.0.0
- 最后更新：2024-02-26
