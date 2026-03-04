---
name: feishu-smart-doc-writer
description: |
  Feishu/Lark Smart Document Writer - 飞书智能文档写入器.
  
  核心功能：
  1. 智能分块写入 - 解决长文档API限制导致的空白问题
  2. 自动转移所有权 - 创建文档后自动转移给用户
  3. 自动索引管理 - 自动更新本地文档索引，支持搜索
  4. 首次使用引导 - 自动引导配置OpenID
---

# Feishu Smart Doc Writer v1.3.0

## 🚀 核心功能

### 1. 智能文档创建
- **自动分块**：长内容自动分割成小块，避免API限制导致的空白文档
- **自动转移所有权**：创建后自动使用 OpenID 转移给用户
- **自动索引更新**：文档信息自动添加到本地索引 `memory/feishu-docs-index.md`
- **智能分类**：根据内容自动打标签（AI技术、电商、健康运动等）

### 2. 文档管理
- **搜索文档**：按关键词搜索本地索引
- **列出文档**：按标签、状态筛选文档列表
- **追加内容**：向现有文档追加内容（自动分块）

---

## 📋 工具列表

### write_smart - 智能创建文档
创建文档，自动完成分块写入、所有权转移、索引更新。

```json
{
  "title": "文档标题",
  "content": "文档内容（支持长内容）",
  "folder_token": "可选的文件夹token"
}
```

**返回：**
```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "doc_token": "xxx",
  "chunks_count": 3,
  "owner_transferred": true,
  "index_updated": true
}
```

### append_smart - 追加内容
向现有文档追加内容（自动分块）。

```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "content": "要追加的内容"
}
```

### search_docs - 搜索文档
搜索本地索引中的文档。

```json
{
  "keyword": "搜索关键词",
  "search_in": ["name", "summary", "tags"]  // 可选，默认搜索所有字段
}
```

**返回：**
```json
{
  "results": [
    {
      "name": "文档名",
      "type": "docx",
      "link": "https://...",
      "summary": "摘要",
      "tags": "AI技术, OpenClaw"
    }
  ],
  "count": 1
}
```

### list_docs - 列出文档
列出所有文档，支持筛选。

```json
{
  "tag": "AI技术",      // 可选，按标签筛选
  "status": "已完成",   // 可选，按状态筛选
  "limit": 10          // 可选，限制数量
}
```

### transfer_ownership - 转移所有权
手动转移文档所有权（通常不需要，write_smart 已自动处理）。

```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "owner_openid": "ou_xxxxxxxx"
}
```

**注意：** 只需要提供 OpenID，tenant_access_token 由 Skill 自动获取。

### configure - 配置 OpenID
首次使用时配置 OpenID。

```json
{
  "openid": "ou_xxxxxxxx",
  "permission_checked": true
}
```

### get_config_status - 查看配置状态
查看当前配置状态。

---

## 🚀 快速开始

### 首次使用（3步配置）

**第1步：调用 write_smart**
```
/feishu-smart-doc-writer write_smart
title: 测试文档
content: 这是一个测试文档内容
```

**第2步：获取 OpenID**
如果未配置，会显示引导：
1. 登录 https://open.feishu.cn
2. 进入应用 → 权限管理 → 搜索 `im:message`
3. 点击【API】发送消息 → 前往API调试台
4. 点击"快速复制 open_id"，选择你的账号，复制

**第3步：配置并开通权限**
```
/feishu-smart-doc-writer configure
openid: ou_你的OpenID
permission_checked: true
```

然后到权限管理：
1. 搜索 `docs:permission.member:transfer`
2. 点击"开通"
3. **重要**：点击"发布"按钮发布新版本

配置完成后，以后创建文档会自动：
- ✅ 分块写入内容
- ✅ 转移所有权给你
- ✅ 更新本地索引

---

## 📊 索引管理

### 自动索引流程
```
write_smart 创建文档
    ↓
写入内容（自动分块）
    ↓
转移所有权
    ↓
自动更新索引 → memory/feishu-docs-index.md
    ↓
完成！
```

### 自动分类标签
根据内容自动识别：
- **AI技术** - AI、人工智能、模型、GPT、LLM
- **OpenClaw** - OpenClaw、skill、agent
- **飞书文档** - 飞书、文档、feishu
- **电商** - 电商、TikTok、Alibaba
- **健康运动** - Garmin、Strava、骑行、健康
- **每日归档** - 对话、归档、聊天记录

### 索引文件位置
`memory/feishu-docs-index.md`

格式：Markdown 表格，包含序号、名称、类型、链接、摘要、状态、标签、所有者

---

## 🔍 使用示例

### 示例1：创建技术文档
```
/feishu-smart-doc-writer write_smart
title: AI技术调研报告
content: # AI技术概述\n\n人工智能（AI）是...
```

结果：
- 文档创建成功
- 自动打上"AI技术"标签
- 索引已更新

### 示例2：搜索文档
```
/feishu-smart-doc-writer search_docs
keyword: AI技术
```

### 示例3：列出所有技术文档
```
/feishu-smart-doc-writer list_docs
tag: AI技术
```

---

## ⚙️ 配置说明

### 用户配置文件
位置：`skills/feishu-smart-doc-writer/user_config.json`

```json
{
  "owner_openid": "ou_5b921cba0fd6e7c885276a02d730ec19",
  "permission_noted": true,
  "first_time": false
}
```

### 必需权限
- `docx:document:create` - 创建文档
- `docx:document:write` - 写入内容
- `docs:permission.member:transfer` - 转移所有权 ⚠️ 关键权限

---

## 📝 版本历史

### v1.3.0 (2026-02-22)
- ✅ 新增自动索引管理（index_manager.py）
- ✅ 新增 search_docs 工具（搜索本地索引）
- ✅ 新增 list_docs 工具（列出文档）
- ✅ write_smart 自动更新索引（代码层面强制执行）
- ✅ 智能自动分类标签

### v1.2.0
- ✅ 自动分块写入
- ✅ 自动转移所有权
- ✅ 首次使用引导

### v1.1.0
- ✅ 基础文档创建和追加

---

## 🔧 故障排除

### "open_id is not exist" 错误
**原因**：使用了 user_id 而不是 openid
**解决**：使用以 `ou_` 开头的 openid

### "权限不足" 错误
**原因**：未开通 `docs:permission.member:transfer` 权限，或未发布应用
**解决**：
1. 权限管理 → 搜索 `docs:permission.member:transfer` → 开通
2. 点击"发布"按钮发布新版本（关键！）

### 索引未更新
**检查**：
1. 查看 `memory/feishu-docs-index.md` 是否存在
2. 检查 write_smart 返回的 `index_updated` 字段
3. 查看错误日志

---

## 📞 支持

如有问题，请检查：
1. OpenID 格式是否正确（ou_ 开头）
2. 权限是否已开通并发布
3. 索引文件路径是否正确
