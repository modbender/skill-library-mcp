# Feishu Smart Doc Writer

> **English**: Feishu/Lark Smart Document Writer. Solves API content limits by auto-chunking long documents and auto-transferring ownership. Guides OpenID config on first use.
> 
> **中文**: 飞书智能文档写入器，解决长文档API限制导致的空白问题，自动转移所有权。首次使用自动引导配置。

飞书智能文档写入器 - 解决长文档写入时的 API 限制问题，支持自动转移所有权。

## 认证说明

本 Skill 使用 OpenClaw 内置的飞书工具集，**无需手动获取 token**。

- `tenant_access_token` 由 OpenClaw 自动管理（通过配置好的 `appId` 和 `appSecret` 自动换取）
- 你**不需要**去飞书后台点击"获取 token"
- 本 Skill 唯一需要配置的是 **用户 OpenID**（用于文档所有权转移，见下方配置步骤）

## 核心功能

### 1. 智能分块写入
飞书 API 对单次写入有限制（创建~4000字符，追加~2000字符），超过会导致文档空白。本 Skill 自动将长内容分块写入，确保完整无丢失。

### 2. 自动转移所有权
应用创建的文档默认所有权属于应用，用户无法编辑。本 Skill 在创建文档后自动转移所有权给用户，用户拥有完全控制权。

### 3. 首次使用自动引导
首次使用时自动引导用户配置 OpenID，无需查阅文档。

## 使用流程

### 第1步：首次使用（自动引导）

当你第一次使用 `write_smart` 时，Skill 会自动提示配置指南。

### 第2步：获取你的 OpenID

**详细步骤（精确路径）：**

1. **登录飞书开放平台**
   - 网址：https://open.feishu.cn

2. **进入权限管理并前往调试台**
   - 进入你的**相关应用**
   - 点击 **"权限管理"**
   - 搜索权限：`im:message`
   - 鼠标移动到 **"相关API事件"**
   - 选择：**【API】发送消息**
   - 点击右下角：**"前往API调试台"**

3. **找到 "快速复制 open_id"**
   - 在页面中找到 **蓝色文字** "快速复制 open_id"
   - 点击这个链接

4. **选择用户并复制**
   - 在弹出的选择框中，**选择你的账号**
   - 点击 **"复制"** 按钮
   - 得到格式如：`ou_xxxxxxxx`

### 第3步：开通并发布权限

⚠️ **重要：需要开通权限并发布应用新版本**

1. **进入权限管理**
   - 登录 https://open.feishu.cn
   - 进入你的应用 → **权限管理**

2. **搜索并开通权限**
   - 搜索：`docs:permission.member:transfer`
   - 点击 **"开通"**

3. **发布新版本（关键！）**
   - 点击页面右上角的 **"发布"** 按钮
   - 等待发布完成
   - ⚠️ **不发布的话，权限不会生效！**

### 第4步：配置 Skill

根据引导，使用 `configure` 工具配置：

```python
await ctx.invoke_tool("feishu_smart_doc_writer.configure", {
    "openid": "ou_5b921cba0fd6e7c885276a02d730ec19",
    "permission_checked": true
})
```

### 第5步：创建文档（自动转移所有权）

配置完成后，直接创建文档：

```python
result = await ctx.invoke_tool("feishu_smart_doc_writer.write_smart", {
    "title": "项目报告",
    "content": "# 项目报告\n\n很长很长的内容...（支持10000+字）"
})

# 返回：
# {
#   "doc_url": "https://feishu.cn/docx/xxx",
#   "chunks_count": 5,
#   "owner_transferred": true,
#   "message": "✅ 文档创建成功，共分 5 块写入，所有权已转移"
# }
```

**配置一次，永久生效！** 之后创建文档会自动转移所有权。

## 工具列表

| 工具名 | 功能 |
|--------|------|
| `write_smart` | 创建文档，自动分块写入，自动转移所有权（首次使用引导配置） |
| `configure` | 配置 OpenID 和确认权限 |
| `append_smart` | 追加内容到已有文档（自动分块） |
| `transfer_ownership` | 转移已有文档的所有权 |
| `get_config_status` | 查看当前配置状态 |

## 为什么需要这个 Skill？

### 原生 feishu_doc 的问题

```python
# ❌ 原生方式 - 长内容会失败
feishu_doc.create(
    title="项目报告",
    content="# 很长很长的内容..." * 1000  # 超过4000字符
)
# 结果：文档创建，但内容空白或报错
```

### 使用本 Skill

```python
# ✅ 自动处理 - 内容分块写入，自动转移所有权
write_smart(
    title="项目报告",
    content="# 很长很长的内容..." * 1000,  # 10000字符
)
# 结果：自动分为5块写入，所有权转移给用户，文档完整
```

## License

MIT
