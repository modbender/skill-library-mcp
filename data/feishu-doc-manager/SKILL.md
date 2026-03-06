---
name: feishu-doc-manager
description: |
  📄 Feishu Doc Manager | 飞书文档管理器
  
  Seamlessly publish Markdown content to Feishu Docs with automatic formatting.
  Solves key pain points: Markdown table conversion, permission management, batch writing.
  
  将 Markdown 内容无缝发布到飞书文档，自动渲染格式。
  解决核心痛点：Markdown 表格转换、权限管理、批量写入。
  
homepage: https://github.com/Shuai-DaiDai/feishu-doc-manager
---

# 📄 Feishu Doc Manager | 飞书文档管理器

> Seamlessly publish Markdown content to Feishu Docs with automatic formatting.
> 
> 将 Markdown 内容无缝发布到飞书文档，自动渲染格式。

## 🎯 Problems Solved | 解决的痛点

| Problem | Solution | 问题 | 解决方案 |
|---------|----------|------|----------|
| **Markdown tables not rendering** | Auto-convert tables to formatted lists | Markdown 表格无法渲染 | 自动转换为格式化列表 |
| **Permission management complexity** | One-click collaborator management | 权限管理复杂 | 一键协作者管理 |
| **400 errors on long content** | Auto-split long documents | 长内容 400 错误 | 自动分段写入 |
| **Inconsistent formatting** | `write`/`append` auto-render Markdown | 格式不一致 | write/append 自动渲染 |

## ✨ Key Features | 核心功能

### 1. 📝 Smart Markdown Publishing | 智能 Markdown 发布
- **Auto-render**: `write`/`append` actions automatically render Markdown
- **Table handling**: Tables auto-converted to formatted lists
- **Syntax support**: Headers, lists, bold, italic, code, quotes

### 2. 🔐 Permission Management | 权限管理
- Add/remove collaborators
- Update permission levels (view/edit/full_access)
- List current permissions

### 3. 📄 Document Operations | 文档操作
- Create new documents
- Write full content with Markdown
- Append to existing documents
- Update/delete specific blocks

## 🚀 Quick Start | 快速开始

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/Shuai-DaiDai/feishu-doc-manager.git
```

## 📋 Supported Markdown | 支持的 Markdown

| Markdown | Feishu Result |
|----------|---------------|
| `# Title` | Heading 1 |
| `- Item` | Bullet list |
| `**bold**` | Bold |
| `> quote` | Blockquote |

## 🔧 Important Distinctions | 重要区分

**`write`/`append` vs `update_block`**:

| Feature | `write`/`append` | `update_block` |
|---------|------------------|----------------|
| Markdown rendering | ✅ Yes | ❌ No (plain text) |

## 📦 Required Permissions | 必需权限

- `docx:document`
- `docx:document:write_only`
- `docs:permission.member`

## 📝 License | 许可证

MIT
