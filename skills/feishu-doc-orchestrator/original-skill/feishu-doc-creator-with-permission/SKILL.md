---
name: feishu-doc-creator-with-permission
description: 文档创建+权限管理子技能 - 在飞书创建文档并自动完成权限分配（添加协作者+转移所有权），两步原子操作。
---

# 文档创建+权限管理子技能

## 职责
在飞书创建新文档，并**智能选择 Token 模式**完成权限管理，确保用户获得完全控制权。

## ⭐ 智能 Token 模式选择

### 自动判断逻辑

脚本会根据**文档标题**智能判断使用哪种 Token 模式：

| 标题包含关键词 | 使用的 Token 模式 | 说明 |
|---------------|------------------|------|
| `文件夹`、`用户`、`个人`、`我的` | **user_access_token** | 文档属于用户，可指定文件夹，无需权限转移 |
| 其他情况 | **tenant_access_token**（默认） | 文档属于应用，需添加协作者权限 |

### 示例

```bash
# 使用 Tenant Token（默认）
python scripts/doc_creator_with_permission.py "产品需求文档"
python scripts/doc_creator_with_permission.py "会议纪要-2026-02-10"

# 使用 User Token（检测到关键词）
python scripts/doc_creator_with_permission.py "我的个人笔记"
python scripts/doc_creator_with_permission.py "用户文件夹-测试文档"
python scripts/doc_creator_with_permission.py "放到文件夹里的文档"

# 强制使用 User Token
python scripts/doc_creator_with_permission.py "测试文档" --user-token
```

### 为什么需要智能选择？

创建文档和权限管理是**强关联的操作**：

**Tenant Token 模式（默认）**：
- 应用创建的文档，用户默认没有任何权限
- 必须添加协作者权限，用户才能编辑
- 适合自动化批量创建、团队文档

**User Token 模式（关键词触发）**：
- 文档直接属于用户
- 可指定文件夹位置
- 无需权限转移，用户有完全控制权
- 适合个人文档、需要指定文件夹的场景

## 输入
- 文档标题（必需）
- Markdown 文件路径（可选，用于确定标题）

## 输出
- `output/doc_with_permission.json` - 包含文档信息和权限状态

## 工作流程

### Tenant Token 模式（三步）

**第一步：创建文档**
使用 `tenant_access_token` 创建新文档，应用成为创建者。

**第二步：添加协作者权限**
使用 `tenant_access_token` 添加协作者，用户获得编辑权限。
- ⚠️ 只有 `tenant_token` 可以添加协作者

**第三步：转移所有权** ⭐
使用 `user_access_token` 转移所有权，用户获得完全控制权（可编辑+可删除）。
- ⚠️ 只有 `user_token` 可以转移所有权
- ⚠️ 这是必要步骤，不是可选的

### User Token 模式（一步）

**创建文档**
使用 `user_access_token` 创建文档，文档直接属于用户，无需权限转移。

### 最后一步：保存结果
保存文档信息和权限状态到 `output/doc_with_permission.json`。

## 数据格式

### doc_with_permission.json 格式
```json
{
  "document_id": "U2wNd2rMkot6fzxr67ScN7hJn7c",
  "document_url": "https://feishu.cn/docx/U2wNd2rMkot6fzxr67ScN7hJn7c",
  "title": "文档标题",
  "created_at": "2026-01-22T10:30:00",
  "token_mode": "tenant_access_token",  // 或 "user_access_token"
  "permission": {
    "collaborator_added": true,
    "owner_transferred": false,
    "user_has_full_control": true,
    "collaborator_id": "ou_xxx"
  },
  "errors": []
}
```

## 使用方式

### 命令行
```bash
# 默认模式（Tenant Token）
python scripts/doc_creator_with_permission.py "产品需求文档"

# User Token 模式（检测到关键词）
python scripts/doc_creator_with_permission.py "我的个人笔记"

# 强制使用 User Token
python scripts/doc_creator_with_permission.py "测试文档" --user-token
```

### 作为子技能被调用
```python
result = call_skill("feishu-doc-creator-with-permission", {
    "title": "文档标题",
    "output_dir": "workflow/step2_create_with_permission"
})
# 返回: {"doc_info_file": "workflow/step2_create_with_permission/doc_with_permission.json"}
```

## 与其他技能的协作
- 接收来自主编排技能的标题
- 输出给 `feishu-block-adder`、`feishu-doc-verifier`、`feishu-logger`
- 只传递文件路径，不传递内容

## 注意事项

1. **Token 类型必须一致**：文档创建和块添加必须使用相同类型的 Token
   - ❌ 创建用 user_token，添加用 tenant_token → Forbidden
   - ✅ 创建用 tenant_token，添加用 tenant_token → 成功
   - ✅ 创建用 user_token，添加用 user_token → 成功

2. **Tenant Token 创建后必须立即添加协作者**
   - 否则后续的块添加会因权限不足而失败

3. **User Token 需要先授权**
   - 确保 feishu-token.json 文件存在且有效
   - 使用 `auto_auth.py` 自动完成授权（推荐）

## OAuth 自动授权

运行自动化授权脚本，自动完成整个授权流程：

```bash
cd /path/to/your/project
python .claude/skills/feishu-doc-creator-with-permission/scripts/auto_auth.py
```

脚本会自动：
1. 启动本地服务器接收回调
2. 打开浏览器飞书授权页面
3. 自动捕获授权码
4. 获取并保存 token 到 `.claude/feishu-token.json`

**使用方法：** 运行脚本后，在浏览器中点击"同意"即可，其余全部自动完成。

### 正确的权限范围

```
drive:drive docs:doc docx:document docs:permission.member:create offline_access
```

**注意**：不要使用 `drive:drive.permission`，会报错 20043。
