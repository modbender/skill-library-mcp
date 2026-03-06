---
name: chrome-extension-generator
description: 一键生成 Chrome 扩展程序模板，支持 Popup、Background Script、Content Script、Options 页面等多种类型。
metadata: {"clawdbot":{"emoji":"📦","requires":{},"primaryEnv":""}}
---

# Chrome Extension Generator

一键生成 Chrome 扩展程序模板，快速启动你的扩展开发。

## 功能

- ⚡ 快速生成项目结构
- 🎨 多种模板可选
- 📝 完整的配置文件
- 🧪 测试模板
- 📖 生成 README
- 🚀 支持 TypeScript

## 模板类型

| 模板 | 说明 |
|------|------|
| `basic` | 基础 Hello World |
| `popup` | 带 Popup 界面 |
| `options` | 设置页面 |
| `content-script` | 内容脚本 |
| `background` | 后台脚本 |
| `full` | 完整功能扩展 |

## 使用方法

### 生成扩展

```bash
# 基本用法
chrome-extension-generator "扩展名称" "描述"

# 指定模板
chrome-extension-generator "My Extension" "描述" --template popup

# 指定技术栈
chrome-extension-generator "扩展" "描述" --template full --stack typescript
```

### 选项

| 选项 | 说明 |
|------|------|
| `--template, -t` | 模板类型 |
| `--stack, -s` | JavaScript/TypeScript |
| `--output, -o` | 输出目录 |

## 输出结构

```
my-extension/
├── manifest.json
├── popup.html
├── popup.js
├── popup.css
├── background.js
├── content.js
├── options.html
├── options.js
├── icon.png
├── README.md
└── _locales/
    └── en/
        └── messages.json
```

## 示例

### Popup 扩展

```bash
chrome-extension-generator "Focus Timer" "Pomodoro timer extension" --template popup
```

### 内容脚本扩展

```bash
chrome-extension-generator "Page Highlighter" "Highlight text on pages" --template content-script
```

### 完整扩展

```bash
chrome-extension-generator "All-in-One Tool" "Ultimate browser tool" --template full
```

## manifest.json 示例

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "An amazing Chrome extension",
  "permissions": ["storage", "activeTab"],
  "action": {
    "default_popup": "popup.html"
  },
  "background": {
    "service_worker": "background.js"
  }
}
```

## 安装

```bash
# 无需依赖
```

## 开发流程

1. 生成模板
2. 修改 manifest.json
3. 编写功能代码
4. 本地加载扩展
5. 测试并发布

## 发布到 Chrome Web Store

生成模板包含：
- 发布检查清单
- 上传截图模板
- 商店描述模板

## 变现思路

1. **付费模板** - 专业版模板
2. **定制开发** - 为客户开发扩展
3. **插件市场** - 建立扩展市场
4. **广告收入** - 在扩展中展示广告
5. **联盟营销** - 推广产品获取佣金

## 示例扩展

- 广告拦截器
- 密码管理器
- 截图工具
- 笔记工具
- 社媒工具
- 开发辅助工具

## 常用权限

| 权限 | 说明 |
|------|------|
| `storage` | 本地存储 |
| `activeTab` | 当前标签页 |
| `tabs` | 标签页管理 |
| `bookmarks` | 书签管理 |
| `history` | 历史记录 |
| `cookies` | Cookie 管理 |
| `webRequest` | 网络请求 |
