---
title: 文档交付模板
description: 用于 Markdown 双向同步的文档交付模板
type: comind:deliveries
---

# 文档交付中心

> 更新时间: {{current_date}} {{current_time}}

## 团队信息

**审核人（人类成员）**: {{human_member_names}}
**交付者（AI 成员）**: {{ai_member_names}}

---

## 创建交付物的方式

### 方式一：文档 Front Matter（推荐）

在任意文档的 Front Matter 中添加 `delivery_status` 字段即可：

```yaml
---
title: 技术方案
type: decision
project: 项目名
created: 2026-02-24T10:00:00Z
updated: 2026-02-24T10:00:00Z

# 交付字段
delivery_status: pending              # pending | approved | rejected | revision_needed
delivery_assignee: AI成员名           # 交付者
delivery_platform: local              # local | tencent-doc | feishu | notion | other
delivery_version: 1                   # 版本号
related_tasks: [task_xxx]             # 关联任务

# 审核人填写
delivery_reviewer: 人类成员名
delivery_comment: 审核意见
---

# 技术方案内容...
```

**优点**：文档内容与交付状态一体化管理，无需维护独立的交付列表。

### 方式二：交付中心文档（批量管理）

使用本模板格式，在下方列表中添加交付记录。

---

## 待审核

- 标题 | 交付者 | 平台 | 链接 | 关联任务 | 版本 | 描述

## 已通过

- 标题 | 交付者 | 审核人 | 审核意见 | 版本

## 已驳回 / 需修改

- 标题 | 交付者 | 审核人 | 审核意见 | 版本

---

## 格式说明

**待审核格式**: `- 标题 | 交付者 | 平台 | 链接 | 关联任务 | 版本 | 描述`

**已审核格式**: `- 标题 | 交付者 | 审核人 | 审核意见 | 版本`

| 平台 | 值 |
|------|---|
| 本地文档 | local（链接用 doc:文档ID） |
| 腾讯文档 | tencent-doc |
| 飞书 | feishu |
| Notion | notion |
| 其他 | other |

---

## 状态说明

| 状态 | 说明 |
|------|------|
| pending | 待审核 |
| approved | 已通过 |
| rejected | 已驳回 |
| revision_needed | 需修改 |

---

## ⚠️ 验证步骤（必须）

创建交付物后，**必须通过 MCP API 验证**：

```json
// 1. 验证交付记录已创建
{"tool": "list_my_deliveries", "parameters": {"status": "pending"}}

// 2. 验证详情（获取 delivery_id 后）
{"tool": "get_delivery", "parameters": {"delivery_id": "xxx"}}
// 确认 document_id、task_id 关联正确
```

**验证失败常见原因**：
- `delivery_status` 字段格式错误
- `delivery_assignee` 成员名不存在
- `related_tasks` 任务 ID 不存在
