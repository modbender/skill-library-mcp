---
name: comind
description: CoMind 人机协作平台 AI 成员操作手册。定义任务执行、Markdown 同步、对话协作、状态面板等全部工作流程。当 AI 成员接收到 CoMind 平台的任务推送、对话请求、定时调度或巡检指令时，应使用此 Skill 执行标准化操作。
comind_version: "2.2.4"
metadata: { "openclaw": { "always": true, "emoji": "🧠", "homepage": "https://github.com/comind", "requires": { "env": ["COMIND_BASE_URL", "COMIND_API_TOKEN"] } } }
---

# CoMind AI 成员操作手册

> **版本**: v2.2.4

作为 CoMind 协作平台的 AI 成员，按照本文档定义的流程执行所有操作。

## 环境变量

| 变量 | 说明 |
|------|------|
| `COMIND_BASE_URL` | CoMind 实例地址（如 `http://localhost:3000`） |
| `COMIND_API_TOKEN` | MCP External API 鉴权 Token |

### 配置获取方式

#### 方式一：WebSocket 主动请求（推荐）

当 CoMind 已与 OpenClaw Gateway 建立 WebSocket 连接时，Gateway 可主动请求 MCP 配置：

```javascript
// Gateway 发送事件请求配置
{ type: 'event', event: 'comind.config.request', id: 'req-xxx' }

// CoMind 响应
{ type: 'res', id: 'req-xxx', ok: true, payload: { baseUrl: 'http://localhost:3000', apiToken: 'xxx' } }
```

#### 方式二：手动配置

在 OpenClaw 的 systemd 服务文件或环境变量中配置：

```bash
# /etc/systemd/system/openclaw.service 或 .env
COMIND_BASE_URL=http://localhost:3000
COMIND_API_TOKEN=your_api_token_here
```

#### 获取 API Token

1. 登录 CoMind 平台
2. 进入「成员管理」页面
3. 找到对应的 AI 成员，点击编辑
4. 复制或生成 `openclawApiToken`

或通过 API 查询：
```bash
# 查询 AI 成员列表（需要管理员权限）
curl http://localhost:3000/api/members | jq '.[] | select(.type=="ai")'

# 为成员生成 Token
curl -X PUT http://localhost:3000/api/members/{member_id} \
  -H "Content-Type: application/json" \
  -d '{"openclawApiToken": "your-new-token"}'
```

---

## 🚨 关键：三种交互通道架构

CoMind 提供三种与 Agent 交互的通道，**MCP API 是核心通道和兜底保障**：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CoMind Agent 交互通道架构                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐       │
│   │  对话信道    │     │   MCP API    │     │  文档同步    │       │
│   │  (高效)      │     │  (可靠)      │     │  (便捷)      │       │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘       │
│          │                    │                    │                │
│          │     ┌──────────────┴──────────────┐     │                │
│          │     │         能力边界             │     │                │
│          │     │  • 依赖 WebSocket 连接       │     │                │
│          │     │  • 解析失败静默丢弃          │     │  • Front Matter 格式要求    │
│          │     │  • 无显式错误反馈            │     │  • 同步失败仅日志           │
│          │     │  • 能力子集                  │     │  • 无即时验证               │
│          └─────┴─────────────────────────────┴─────┘                │
│                              │                                      │
│                              ▼                                      │
│                    ┌─────────────────┐                              │
│                    │   MCP API 兜底   │ ← 最可靠的验证通道           │
│                    │   • 显式错误返回 │                              │
│                    │   • 审计日志    │                              │
│                    │   • 限流保护    │                              │
│                    │   • 独立 HTTP   │                              │
│                    └─────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 通道一：对话信道 Actions（高效，但有边界）

**触发方式**：AI 在对话回复末尾嵌入 `{"actions": [...]}` JSON 块

**执行链路**：
```
AI 回复 → Gateway 推送 chat 事件 → CoMind 解析 Actions → 执行 → SSE 广播结果
```

**可靠性机制**：
- ✅ 幂等性：`idempotencyKey` 防止重复执行
- ✅ 批量执行：多个 action 顺序执行，失败不影响后续
- ✅ 结果回传：执行结果自动回传给 AI（通过对话）

**能力边界**（重要！）：
- ❌ **依赖 WebSocket 连接**：Gateway 断连时 Actions 无法执行
- ❌ **解析失败静默丢弃**：JSON 格式错误时无显式错误反馈
- ❌ **操作子集**：仅支持写入操作，不支持查询
- ❌ **无验证机制**：无法确认操作是否真正成功

**适用场景**：
- 对话中更新任务状态、添加评论
- 与用户交互时即时反馈
- **不适合**：关键操作、需要确认的操作

---

### 通道二：MCP API（核心通道，可靠兜底）

**触发方式**：HTTP POST `/api/mcp/external`，Bearer Token 鉴权

**执行链路**：
```
AI 请求 → 鉴权 → 审计日志 → 执行 → 返回结果
```

**可靠性机制**（与其他通道的关键差异）：
- ✅ **显式错误返回**：`{ success: false, error: "具体错误原因" }`
- ✅ **审计日志**：所有调用记录到数据库，可追溯
- ✅ **限流保护**：防止滥用，自动降级
- ✅ **独立 HTTP 协议**：不依赖 WebSocket 连接状态
- ✅ **完整操作集**：支持所有查询和写入操作
- ✅ **身份自动注入**：`member_id` 自动填充，防止伪造

**为什么 MCP 是兜底通道**：

| 场景 | 其他通道问题 | MCP 兜底方案 |
|------|-------------|-------------|
| 文档同步创建任务后 | 无即时验证，不知道是否成功 | `get_task(task_id)` 确认存在 |
| Actions 执行后 | 无错误反馈，可能静默失败 | `get_task(task_id)` 验证状态 |
| 关键状态变更 | 可能因断连丢失 | MCP 独立请求，确保送达 |
| 批量操作验证 | 同步失败仅日志 | `list_my_tasks` 验证结果 |

---

### 通道三：文档自动扫描同步（便捷，需验证）

**触发方式**：创建/更新包含特殊 Front Matter 的 Markdown 文档

**执行链路**：
```
AI 创建文档 → API 保存 → syncMarkdownToDatabase() → 解析 Front Matter → 写入数据库
```

**支持的同步类型**：

| Front Matter type | 同步目标 | 说明 |
|-------------------|---------|------|
| `comind:tasks` / `task_list` | tasks 表 | 批量创建/更新任务 |
| `comind:schedules` | schedules 表 | 创建定时任务 |
| `delivery_status: pending` | deliveries 表 | 创建交付记录 |

**可靠性机制**：
- ✅ 防循环同步：标记正在同步的文档 ID
- ✅ 成员名自动匹配：`@成员名` → `memberId`
- ✅ 项目名自动匹配：项目名 → `projectId`

**能力边界**：
- ❌ **Front Matter 格式要求严格**：解析失败无反馈
- ❌ **同步失败仅记录日志**：AI 无法获知失败原因
- ❌ **无即时验证**：无法在创建时确认结果

**适用场景**：
- 批量创建任务（≥2 条）
- 批量提交交付物
- **必须配合 MCP 验证**：同步后调用 MCP 确认结果

---

### 三通道协同模式：便捷 + 验证

**模式一：文档同步 + MCP 验证**

```bash
# 1. 通过文档同步创建任务（便捷）
create_document({
  title: "任务看板",
  content: "---
type: comind:tasks
project: 项目名
---
- [ ] 任务1 @AI成员
- [ ] 任务2 @AI成员"
})

# 2. 通过 MCP 验证创建结果（可靠）
list_my_tasks(status: "todo") → 确认任务数量正确
get_task(task_id: "xxx") → 确认任务详情正确
```

**模式二：对话 Actions + MCP 验证**

```bash
# 1. 通过对话 Actions 更新状态（高效）
{"actions": [{"type": "update_task_status", "task_id": "xxx", "status": "in_progress"}]}

# 2. 通过 MCP 验证更新结果（可靠）
get_task(task_id: "xxx") → 确认 status 已变为 in_progress
```

**模式三：交付提交 + MCP 验证**

```bash
# 1. 通过 Front Matter 提交交付（便捷）
create_document({
  title: "技术方案",
  content: "---
delivery_status: pending
delivery_assignee: AI成员名
related_tasks: [task_xxx]
---
# 技术方案内容..."
})

# 2. 通过 MCP 验证交付记录（可靠）
get_delivery(delivery_id: "xxx") → 确认交付记录已创建
list_my_deliveries(status: "pending") → 确认在待审核队列中
```

---

### 方法选择决策树

```
需要执行操作
│
├─ 是否需要 100% 确认结果？
│   └─ YES → 使用 MCP API（唯一可靠通道）
│
├─ 是否在对话中回复用户？
│   ├─ YES → 操作是否支持对话信道 Actions？
│   │         ├─ YES → 使用 Actions（便捷）+ MCP 验证（可靠）
│   │         └─ NO  → 使用 MCP API
│   │
│   └─ NO → 是否批量写入 ≥2 条记录？
│             ├─ YES → Markdown 同步 + MCP 验证
│             └─ NO  → MCP API 单条操作
```

---

### ⚠️ 能力限制对比表

**对话信道 Actions 支持的操作**：
- ✅ `update_task_status` — 更新任务状态
- ✅ `add_comment` — 添加任务评论
- ✅ `create_check_item` — 创建检查项
- ✅ `complete_check_item` — 完成检查项
- ✅ `create_document` — 创建文档
- ✅ `update_document` — 更新文档
- ✅ `deliver_document` — 提交文档交付
- ✅ `update_status` — 更新 AI 状态
- ✅ `set_queue` — 设置任务队列
- ✅ `sync_identity` — 同步身份信息到 IDENTITY.md
- ✅ `get_mcp_token` — 获取 MCP API Token

**对话信道 Actions 不支持的操作**（必须用 MCP API）：
- ❌ `set_do_not_disturb` — 免打扰模式
- ❌ `create_schedule` / `update_schedule` / `delete_schedule` — 定时任务管理
- ❌ `review_delivery` — 审核交付（人类操作）
- ❌ `get_task` / `get_document` / `search_documents` — 查询操作
- ❌ `get_project` / `list_my_tasks` — 查询操作
- ❌ `register_member` — 成员注册

**对话信道 Actions 支持的操作**：
- ✅ `update_task_status` — 更新任务状态
- ✅ `add_comment` — 添加任务评论
- ✅ `create_check_item` — 创建检查项
- ✅ `complete_check_item` — 完成检查项
- ✅ `create_document` — 创建文档
- ✅ `update_document` — 更新文档
- ✅ `deliver_document` — 提交文档交付
- ✅ `update_status` — 更新 AI 状态
- ✅ `set_queue` — 设置任务队列
- ✅ `sync_identity` — 同步身份信息到 IDENTITY.md
- ✅ `get_mcp_token` — 获取 MCP API Token

**对话信道 Actions 不支持的操作**（必须用 MCP API）：
- ❌ `set_do_not_disturb` — 免打扰模式
- ❌ `create_schedule` / `update_schedule` / `delete_schedule` — 定时任务管理
- ❌ `review_delivery` — 审核交付（人类操作）
- ❌ `get_task` / `get_document` / `search_documents` — 查询操作
- ❌ `get_project` / `list_my_tasks` — 查询操作
- ❌ `register_member` — 成员注册
- ❌ `list_my_deliveries` / `get_delivery` — 交付查询

---

## 内置 MCP 调用脚本

为提高 Agent 调用 MCP API 的效率和可靠性，Skill 内置以下调用脚本模板：

### 基础调用模板

```bash
# 环境变量（由 Agent 自动注入）
COMIND_BASE_URL="${COMIND_BASE_URL:-http://localhost:3000}"
COMIND_API_TOKEN="${COMIND_API_TOKEN}"

# 通用调用函数
mcp_call() {
  local tool="$1"
  local params="$2"
  
  curl -s -X POST "${COMIND_BASE_URL}/api/mcp/external" \
    -H "Authorization: Bearer ${COMIND_API_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"tool\": \"${tool}\", \"parameters\": ${params}}"
}
```

### 高频操作脚本

#### 验证任务创建/更新

```bash
# 文档同步创建任务后验证
verify_task() {
  local task_id="$1"
  local expected_status="${2:-todo}"
  
  result=$(mcp_call "get_task" "{\"task_id\": \"${task_id}\"}")
  
  if echo "$result" | jq -e '.success == true' > /dev/null; then
    actual_status=$(echo "$result" | jq -r '.data.status')
    if [ "$actual_status" = "$expected_status" ]; then
      echo "✅ 任务验证成功: $task_id 状态为 $actual_status"
      return 0
    else
      echo "⚠️ 任务状态不符: 期望 $expected_status，实际 $actual_status"
      return 1
    fi
  else
    echo "❌ 任务验证失败: $(echo "$result" | jq -r '.error')"
    return 1
  fi
}
```

#### 验证交付记录创建

```bash
# Front Matter 提交交付后验证
verify_delivery() {
  local document_id="$1"
  
  # 先查询该文档关联的交付记录
  result=$(mcp_call "list_my_deliveries" "{\"status\": \"all\"}")
  
  delivery_id=$(echo "$result" | jq -r ".data.deliveries[] | select(.document_id == \"${document_id}\") | .id")
  
  if [ -n "$delivery_id" ]; then
    echo "✅ 交付记录已创建: $delivery_id"
    
    # 获取详情确认
    detail=$(mcp_call "get_delivery" "{\"delivery_id\": \"${delivery_id}\"}")
    echo "交付状态: $(echo "$detail" | jq -r '.data.status')"
    return 0
  else
    echo "❌ 未找到关联的交付记录"
    return 1
  fi
}
```

#### 批量操作验证

```bash
# 文档同步批量创建任务后验证
verify_bulk_tasks() {
  local expected_count="$1"
  local project_id="$2"
  
  result=$(mcp_call "list_my_tasks" "{\"status\": \"todo\"}")
  actual_count=$(echo "$result" | jq '.data.tasks | length')
  
  if [ "$actual_count" -ge "$expected_count" ]; then
    echo "✅ 批量任务验证成功: 创建了 $actual_count 个任务"
    return 0
  else
    echo "⚠️ 任务数量不足: 期望 $expected_count，实际 $actual_count"
    return 1
  fi
}
```

#### 状态更新验证

```bash
# Actions 更新状态后验证
verify_status_update() {
  local task_id="$1"
  local expected_status="$2"
  local max_retries=3
  local retry=0
  
  while [ $retry -lt $max_retries ]; do
    result=$(mcp_call "get_task" "{\"task_id\": \"${task_id}\"}")
    actual_status=$(echo "$result" | jq -r '.data.status // empty')
    
    if [ "$actual_status" = "$expected_status" ]; then
      echo "✅ 状态验证成功: $task_id → $actual_status"
      return 0
    fi
    
    retry=$((retry + 1))
    sleep 1
  done
  
  echo "❌ 状态验证失败: 期望 $expected_status，实际 $actual_status"
  return 1
}
```

### 错误处理模板

```bash
# 带重试的 MCP 调用
mcp_call_with_retry() {
  local tool="$1"
  local params="$2"
  local max_retries="${3:-3}"
  local retry=0
  
  while [ $retry -lt $max_retries ]; do
    result=$(mcp_call "$tool" "$params")
    
    if echo "$result" | jq -e '.success == true' > /dev/null; then
      echo "$result"
      return 0
    fi
    
    error=$(echo "$result" | jq -r '.error')
    
    # 限流错误，等待重试
    if echo "$error" | grep -q "rate limit"; then
      sleep $((2 ** retry))
      retry=$((retry + 1))
      continue
    fi
    
    # 其他错误，直接返回
    echo "$result"
    return 1
  done
  
  echo '{"success": false, "error": "Max retries exceeded"}'
  return 1
}
```

---

## 验证场景清单

以下场景**必须**使用 MCP 验证：

### 场景 1：文档同步创建任务

```yaml
操作: create_document({ type: "comind:tasks", ... })
验证: list_my_tasks() → 确认任务数量和内容
原因: Front Matter 解析失败静默，需显式验证
```

### 场景 2：文档同步创建交付

```yaml
操作: create_document({ delivery_status: "pending", ... })
验证: list_my_deliveries(status: "pending") → 确认交付记录存在
原因: 交付记录关联复杂，需确认 memberId、documentId 正确
```

### 场景 3：对话 Actions 更新状态

```yaml
操作: {"actions": [{"type": "update_task_status", ...}]}
验证: get_task(task_id) → 确认状态已变更
原因: WebSocket 断连时 Actions 可能丢失
```

### 场景 4：批量操作

```yaml
操作: 文档同步批量创建 N 条记录
验证: list_my_tasks() / list_my_deliveries() → 确认数量
原因: 部分记录可能因解析失败被跳过
```

### 场景 5：关键状态变更

```yaml
操作: 任务完成 / 交付提交 / 状态切换
验证: get_task() / get_delivery() → 确认状态
原因: 关键操作需 100% 确认成功
```

### 场景 6：跨系统同步

```yaml
操作: 外部文档系统同步到 CoMind
验证: search_documents(query) → 确认文档已同步
原因: 外部系统可能延迟或失败
```

---

## 决策流程图（更新版）

### 场景与方法映射

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 用户对话中更新任务状态 | 对话信道 Actions | 一次回复完成，无需额外请求 |
| 任务推送后更新状态 | 对话信道 Actions | 回复即执行，用户可见进度 |
| 用户对话中查询任务 | MCP API | 查询操作不支持 Actions |
| 批量创建任务 | Markdown 同步 | 一次调用创建多条记录 |
| 定时任务管理 | MCP API | Actions 不支持定时任务 |
| 获取待办任务列表 | MCP API (`list_my_tasks`) | 查询操作不支持 Actions |

---

## 决策树

```
收到指令
├─ task-push 模板 → 场景A: 执行任务（必须在对话中汇报进展）
├─ chat-* 模板   → 场景E: 对话协作
├─ 需要全局上下文 → 读取 references/system-info.md 模板格式，调 API 获取数据
└─ 自主巡检      → 场景D: 任务巡检

执行中:
├─ 批量写操作(≥2条) → Markdown 同步
├─ 单字段更新       → 对话信道 Actions 或 MCP API
├─ 状态面板         → 对话信道 Actions 或 MCP API
├─ 查询数据         → MCP API
├─ 关键进展         → 在对话中主动汇报
└─ 完成             → 在对话中汇报总结 + update_task_status(completed) + update_status(idle)
```

---

## 实体映射

Markdown 文档与 CoMind 数据库的自动映射规则：

| Markdown 元素 | CoMind 表 | 映射规则 |
|--------------|----------|---------|
| 文档 | documents | title 从 Front Matter 或 H1 解析 |
| 任务行 | tasks | 按标题匹配，自动创建/更新 |
| `@成员名` | members | 按名称模糊匹配，转 ID 存入 assignees |
| `[[文档名]]` | documents | 按标题匹配，建立关联关系 |
| `#task_xxx` | tasks | 精确 ID 引用或标题模糊匹配 |
| Front Matter | 各表字段 | 自动解析填充 |

### Front Matter 字段映射

```yaml
# 必填字段
title: 文档标题          # → documents.title
type: report            # → documents.docType
project: comind-v2      # → documents.projectId（按项目名匹配）
created: 2026-02-18     # → documents.createdAt
updated: 2026-02-18     # → documents.updatedAt

# 可选字段
tags: [标签]            # → documents.tags
related_tasks: [task_id] # → 关联任务
contains_tasks: true    # → 触发任务解析
task_assignees: [成员]   # → 任务默认分配

# 交付字段（有 delivery_status 即自动创建交付记录）
delivery_status: pending      # → deliveries.status（pending | approved | rejected | revision_needed）
delivery_assignee: AI成员名   # → deliveries.memberId（按成员名匹配）
delivery_platform: local      # → deliveries.platform（local | tencent-doc | feishu | notion | other）
delivery_version: 1           # → deliveries.version
delivery_reviewer: 人类成员名 # → deliveries.reviewerId（审核人填写）
delivery_comment: 审核意见    # → deliveries.reviewComment（审核人填写）
```

> **交付说明**：文档 Front Matter 中存在 `delivery_status` 字段时，系统自动创建/更新交付记录。
> - `pending`：进入交付中心待审核队列
> - `approved`：已通过审核
> - `rejected`：已驳回
> - `revision_needed`：需要修改

### 任务状态映射

| 语法 | 状态 | 优先级 |
|------|------|--------|
| `- [ ]` | todo | medium |
| `- [!]` | todo | high |
| `- [-]` | todo | low |
| `- [~]` | in_progress | - |
| `- [?]` | reviewing | - |
| `- [x]` | completed | - |

---

## 场景A: 执行任务

**触发**：收到 task-push 推送（含 task_id、title、description、项目上下文）

> ⚠️ **关键警告**
> - 开始执行前**必须**先更新状态为 `in_progress`
> - 完成工作后**必须**更新状态为 `completed` 或 `reviewing`
> - 仅创建笔记/文档 ≠ 完成任务，必须更新状态才能结束！
> - **必须在对话中主动汇报工作进展，不能默默执行！**
> - **关键操作后必须用 MCP 验证结果！**

### 汇报规范

| 阶段 | 要求 |
|------|------|
| 收到任务 | 在对话中确认收到，简述执行计划 |
| 执行过程 | 遇到关键节点或重要发现时，主动在对话中汇报 |
| 完成时 | 在对话中发送完成总结：做了什么、产出了什么 |
| 遇到问题 | 立即在对话中说明问题和处理方案 |

**回复风格**：简洁明了，像同事沟通，重要信息加粗。

**流程**：

### 1. 【必须】确认收到 + 接受任务 + 验证

先在对话中简短确认收到任务、说明执行计划，然后执行 Actions：

```json
{"actions": [
  {"type": "update_task_status", "task_id": "xxx", "status": "in_progress"},
  {"type": "update_status", "status": "working", "current_action": "开始执行", "task_id": "xxx"}
]}
```

**验证**（使用 MCP API 确认状态变更）：
```json
{"tool": "get_task", "parameters": {"task_id": "xxx"}}
// 确认返回的 status 为 "in_progress"
```

### 2. 获取上下文（可选）

**必须使用 MCP API**（查询操作不支持 Actions）

```json
{"tool": "get_task", "parameters": {"task_id": "xxx"}}
{"tool": "get_project", "parameters": {"project_id": "xxx"}}
```

### 3. 分解子任务 + 验证

- **≥2项**：Markdown 同步（`create_document` + `comind:tasks` frontmatter）**+ MCP 验证**
- **≤2项**：MCP API 或 Actions（`create_check_item`）

**批量创建任务后验证**：
```json
{"tool": "list_my_tasks", "parameters": {"status": "todo"}}
// 确认任务数量和内容正确
```

### 4. 执行 + 汇报

执行过程中如有重要进展，**在对话中主动汇报**，同时通过 Actions 记录：

```json
{"actions": [
  {"type": "add_comment", "task_id": "xxx", "content": "进展：正在分析需求..."},
  {"type": "update_status", "status": "working", "progress": 30}
]}
```

### 5. 产出交付物 + 验证

- **Markdown 同步**：`create_document` 写内容 + `comind:deliveries` 批量提交
- **单个交付**：Actions 或 MCP API `deliver_document`

**创建交付物后验证**：
```json
{"tool": "list_my_deliveries", "parameters": {"status": "pending"}}
// 确认交付记录已创建，document_id 正确关联
```

### 6. 【必须】完成任务 + 汇报结果 + 验证

**情况A：无需用户决策**

在对话中汇报完成总结，然后执行：

```json
{"actions": [
  {"type": "update_task_status", "task_id": "xxx", "status": "completed"},
  {"type": "add_comment", "task_id": "xxx", "content": "✅ 任务已完成！"},
  {"type": "update_status", "status": "idle"}
]}
```

**验证**：
```json
{"tool": "get_task", "parameters": {"task_id": "xxx"}}
// 确认 status 为 "completed"
```

**情况B：需要用户审核**（文档交付场景）

在对话中说明已提交交付、等待审核，然后执行：

```json
{"actions": [
  {"type": "deliver_document", "title": "技术方案", "platform": "local", "document_id": "doc_xxx", "task_id": "xxx"},
  {"type": "update_task_status", "task_id": "xxx", "status": "reviewing"},
  {"type": "add_comment", "task_id": "xxx", "content": "📄 已提交交付中心，等待审核"}
]}
```

**验证**：
```json
{"tool": "get_task", "parameters": {"task_id": "xxx"}}
// 确认 status 为 "reviewing"

{"tool": "list_my_deliveries", "parameters": {"status": "pending"}}
// 确认交付记录已创建
```

> ⚠️ **重要**：提交交付后状态必须设为 `reviewing`，不能设为 `completed`！

**完成标准检查清单**：
- [ ] 已在对话中确认收到任务
- [ ] 状态已更新为 `completed` 或 `reviewing`
- [ ] **已通过 MCP 验证状态变更成功**
- [ ] 交付物已提交（如有产出）
- [ ] **已通过 MCP 验证交付记录创建成功**
- [ ] 已在对话中汇报完成总结

---

## 场景A2: 文档交付

**何时需要提交文档交付？**

| 文档类型 | 说明 | 必须提交 |
|---------|------|---------|
| 决策文档 | 技术选型、架构方案 | ✅ 是 |
| 审核文档 | 预算报告、合同草案 | ✅ 是 |
| 外部发布 | 公众号文章、产品公告 | ✅ 是 |
| 临时笔记 | 学习笔记、过程记录 | ❌ 否 |
| 工作日志 | 过程记录、信息整理 | ❌ 否 |

### 创建交付物的方式 + 验证

**方式一：文档 Front Matter（推荐）+ MCP 验证**

在创建文档时添加 `delivery_status` 字段，系统自动创建交付记录：

```yaml
---
title: 技术方案
type: decision
project: 项目名
created: 2026-02-24T10:00:00Z
updated: 2026-02-24T10:00:00Z

# 交付字段
delivery_status: pending
delivery_assignee: 你的名字
delivery_platform: local
delivery_version: 1
related_tasks: [task_xxx]
---

# 技术方案内容...
```

**创建后验证**（必须）：
```json
// 验证交付记录已创建
{"tool": "list_my_deliveries", "parameters": {"status": "pending"}}

// 验证文档关联正确
{"tool": "get_delivery", "parameters": {"delivery_id": "从上面返回的 ID"}}
// 确认 document_id、task_id 关联正确
```

**方式二：对话信道 Actions + MCP 验证**

```json
{"actions": [
  {"type": "deliver_document", "title": "技术方案", "platform": "local", "document_id": "doc_xxx", "task_id": "xxx"}
]}
```

**创建后验证**（必须）：
```json
{"tool": "list_my_deliveries", "parameters": {"status": "pending"}}
// 确认交付记录存在，document_id 正确
```

**方式三：MCP API（自带验证）**

```json
{"tool": "deliver_document", "parameters": {
  "title": "技术方案",
  "platform": "local",
  "document_id": "doc_xxx",
  "task_id": "xxx"
}}

// 返回结果包含 delivery_id，可确认创建成功
```

### 用户审核

用户在交付中心审核后，系统自动更新文档 Front Matter 中的 `delivery_status`、`delivery_reviewer`、`delivery_comment` 字段。

**交付状态流转**：

```
pending → approved (用户批准) → 任务可 completed
        → rejected (用户拒绝)
        → revision_needed (需要修改)
```

**AI 感知审核结果**：心跳巡检时通过 MCP 查询交付状态：

```json
{"tool": "list_my_deliveries", "parameters": {"status": "revision_needed"}}
{"tool": "get_delivery", "parameters": {"delivery_id": "xxx"}}
// 获取 review_comment 了解审核意见
```

---

## 场景B: Markdown 同步 + MCP 验证

涉及 ≥2 条记录的写操作时，**必须**使用 Markdown 同步，**并使用 MCP 验证结果。

**模板文件位于 `references/` 目录**：

| 模板 | 用途 | 验证方式 |
|------|------|---------|
| `task-board.md` | 批量创建/更新任务 | `list_my_tasks` 确认数量 |
| `schedules.md` | 管理定时调度 | `list_schedules` 确认创建 |
| `deliveries.md` | 批量提交交付物 | `list_my_deliveries` 确认 |

**语法**：
- `@成员名` — 分配任务
- `[[文档名]]` — 关联文档
- `#task_xxx` — 引用任务

**同步后验证流程**：

```bash
# 1. 执行文档同步
create_document({ type: "comind:tasks", content: "..." })

# 2. 验证同步结果
list_my_tasks(status: "todo")
# 确认：
# - 任务数量正确
# - assignees 正确（@成员名 匹配成功）
# - project_id 正确（项目名匹配成功）

# 3. 如果验证失败
# - 检查 Front Matter 格式
# - 检查成员名/项目名是否存在
# - 手动通过 MCP API 补救
```

**常见验证失败原因**：

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 任务数量不足 | 部分行格式错误 | 检查 `- [ ]` 语法 |
| assignees 为空 | 成员名不存在 | 确认成员名拼写或手动分配 |
| project_id 为空 | 项目名不存在 | 使用项目 ID 或确认项目存在 |
| 交付记录未创建 | delivery_status 格式错误 | 确认 YAML 格式正确 |

---

## 场景D: 任务巡检

**触发**：自主检查待处理任务

**必须使用 MCP API**（查询操作不支持 Actions）

```json
// 获取待办任务
{"tool": "list_my_tasks", "parameters": {"status": "todo"}}

// 获取所有未完成任务
{"tool": "list_my_tasks", "parameters": {"status": "all"}}
```

> ⚠️ **不要**查看 HEARTBEAT.md — 那是定时任务执行记录，不是任务列表！

---

## 场景E: 对话协作

**触发**：用户在项目/任务/定时任务页面发起对话

**操作选择**：
- **单条更新** → 对话信道 Actions
- **批量写操作** → Markdown 同步
- **查询操作** → MCP API

### 对话信道 Actions 格式

**格式要求**：
- JSON 块必须位于消息**末尾**
- 格式：`{"actions": [action1, action2, ...]}`
- 每个 action 必须包含 `type` 字段
- JSON 会被解析并执行，**不会显示给用户**

**支持的 action 类型**：

| type | 必填字段 | 可选字段 | 说明 |
|------|---------|---------|------|
| `update_task_status` | task_id, status | progress, message | 更新任务状态 |
| `add_comment` | task_id, content | — | 添加任务评论 |
| `create_check_item` | task_id, text | — | 创建检查项 |
| `complete_check_item` | task_id, item_id | — | 完成检查项 |
| `create_document` | title, content | doc_type, project_id | 创建文档 |
| `update_document` | document_id, content | doc_type | 更新文档 |
| `deliver_document` | title, platform | document_id, external_url, task_id | 提交文档交付 |
| `update_status` | status | current_action, task_id, progress | 更新 AI 状态 |
| `set_queue` | queued_tasks | — | 设置任务队列 |
| `sync_identity` | — | name, creature, vibe, emoji, avatar | 同步身份信息 |
| `get_mcp_token` | member_id | — | 获取 MCP Token |

**字段定义**：

```typescript
// 任务状态
status: 'todo' | 'in_progress' | 'reviewing' | 'completed'

// AI 状态
status: 'idle' | 'working' | 'waiting' | 'offline'

// 文档类型
doc_type: 'note' | 'report' | 'decision' | 'scheduled_task' | 'task_list' | 'other'

// 交付平台
platform: 'tencent-doc' | 'feishu' | 'notion' | 'local' | 'other'

// 任务队列
queued_tasks: Array<{ id: string; title: string }>
```

**示例**：

开始任务：
```json
{"actions": [
  {"type": "update_task_status", "task_id": "GS4FcWg6twz", "status": "in_progress"},
  {"type": "add_comment", "task_id": "GS4FcWg6twz", "content": "开始执行任务"},
  {"type": "update_status", "status": "working", "task_id": "GS4FcWg6twz"}
]}
```

完成任务：
```json
{"actions": [
  {"type": "update_task_status", "task_id": "GS4FcWg6twz", "status": "completed"},
  {"type": "add_comment", "task_id": "GS4FcWg6twz", "content": "✅ 任务已完成！"},
  {"type": "update_status", "status": "idle"}
]}
```

提交审核：
```json
{"actions": [
  {"type": "deliver_document", "title": "技术方案", "platform": "local", "document_id": "doc_abc", "task_id": "GS4FcWg6twz"},
  {"type": "update_task_status", "task_id": "GS4FcWg6twz", "status": "reviewing"},
  {"type": "add_comment", "task_id": "GS4FcWg6twz", "content": "📄 已提交交付中心"}
]}
```

同步身份：
```json
{"actions": [
  {"type": "sync_identity", "name": "Scout", "creature": "智能助手", "vibe": "专业、高效", "emoji": "🤖"}
]}
```

获取 MCP Token：
```json
{"actions": [
  {"type": "get_mcp_token", "member_id": "member_xxx"}
]}
```

**注意事项**：
1. JSON 块必须是合法的 JSON 格式
2. 多个 action 按顺序执行
3. 某个 action 失败不影响后续执行
4. 执行结果通过 SSE 广播，前端自动刷新

---

## 场景F: 定时任务执行

**触发**：定时调度器按计划推送

**必须使用 MCP API**（Actions 不支持定时任务管理）

```json
{"tool": "create_schedule", "parameters": {
  "title": "每日报告",
  "task_type": "report",
  "schedule_type": "daily",
  "schedule_time": "09:00"
}}
```

---

## 场景G: AI 状态面板

### 工具

| 工具 | 必填参数 | 用途 | 支持方式 |
|------|---------|------|---------|
| `update_status` | status | 状态+进度 | Actions / MCP API |
| `set_queue` | queued_tasks | 任务队列 | Actions / MCP API |
| `set_do_not_disturb` | interruptible | 免打扰模式 | **仅 MCP API** |

### 状态值

| status | 含义 |
|--------|------|
| `idle` | 空闲，可接新任务 |
| `working` | 执行任务中 |
| `waiting` | 等待用户回复/外部资源 |
| `offline` | 离线 |

### 状态切换规则

- 接到任务 → `working`
- 执行中 → `working` + `progress`
- 需要提问 → `waiting`
- 完成任务 → `idle`

---

## API 调用方式

- **端点**：`POST ${COMIND_BASE_URL}/api/mcp/external`
- **鉴权**：`Authorization: Bearer ${COMIND_API_TOKEN}`
- **member_id** 自动注入

单个调用：
```json
{"tool": "update_task_status", "parameters": {"task_id": "xxx", "status": "in_progress"}}
```

批量调用：
```json
{"batch": [
  {"tool": "update_task_status", "parameters": {"task_id": "xxx", "status": "in_progress"}},
  {"tool": "update_status", "parameters": {"status": "working", "task_id": "xxx"}}
]}
```

---

## 工具速查

### 查询工具（仅 MCP API，用于验证）

| 工具 | 必填参数 | 用途 | 验证场景 |
|------|---------|------|---------|
| `list_my_tasks` | status (可选) | 获取分配给当前成员的任务 | 验证批量创建任务 |
| `get_task` | task_id | 获取任务详情 | 验证状态变更 |
| `get_document` | document_id 或 title | 获取文档 | 验证文档创建 |
| `search_documents` | query | 搜索文档 | 验证文档同步 |
| `get_project` | project_id | 获取项目详情 | 验证项目上下文 |
| `list_my_deliveries` | status (可选) | 获取当前成员的交付物列表 | **验证交付创建** |
| `get_delivery` | delivery_id | 获取交付物详情（含审核意见） | **验证交付状态** |

### 写入工具（Actions / MCP API）

| 工具 | 必填参数 | 支持方式 | 用途 | 是否需要验证 |
|------|---------|---------|------|-------------|
| `update_task_status` | task_id, status | Actions / MCP API | 更新任务状态 | ✅ `get_task` 验证 |
| `add_task_comment` | task_id, content | Actions / MCP API | 添加评论 | ❌ 不需要 |
| `create_check_item` | task_id, text | Actions / MCP API | 创建检查项 | ✅ `get_task` 验证 |
| `complete_check_item` | task_id, item_id | Actions / MCP API | 完成检查项 | ✅ `get_task` 验证 |
| `create_document` | title, content | Actions / MCP API | 创建文档 | ✅ `get_document` 验证 |
| `update_document` | document_id, content | Actions / MCP API | 更新文档 | ✅ `get_document` 验证 |
| `deliver_document` | title, platform | Actions / MCP API | 提交交付 | ✅ `list_my_deliveries` 验证 |
| `update_status` | status | Actions / MCP API | AI 状态面板 | ❌ 不需要 |
| `set_queue` | queued_tasks | Actions / MCP API | 任务队列 | ❌ 不需要 |
| `sync_identity` | — | Actions | 同步身份信息 | ❌ 不需要 |
| `get_mcp_token` | member_id | Actions | 获取 MCP Token | ❌ 不需要 |

### 管理/配置工具（仅 MCP API）

| 工具 | 必填参数 | 用途 |
|------|---------|------|
| `set_do_not_disturb` | interruptible | 免打扰模式 |
| `create_schedule` | title, task_type, schedule_type | 创建定时任务 |
| `list_schedules` | — | 列出定时任务 |
| `delete_schedule` | schedule_id | 删除定时任务 |
| `update_schedule` | schedule_id, ... | 更新定时任务 |
| `register_member` | name, endpoint | AI 自注册 |
| `review_delivery` | delivery_id, status | 审核交付（人类操作） |

### 验证工具选择指南

```
操作类型                    验证工具
─────────────────────────────────────────
状态变更 (update_task_status)  → get_task
批量创建任务                   → list_my_tasks
创建/更新文档                  → get_document / search_documents
提交交付                       → list_my_deliveries + get_delivery
定时任务                       → list_schedules
```

---

## 枚举值

| 字段 | 值 |
|------|---|
| 任务状态 | todo, in_progress, reviewing, completed |
| 优先级 | high, medium, low |
| AI 状态 | idle, working, waiting, offline |
| 文档类型 | note, report, decision, scheduled_task, task_list, other |
| 交付平台 | tencent-doc, feishu, notion, local, other |
| 审核结果 | approved, rejected, revision_needed |
| 定时周期 | once, daily, weekly, monthly |
| 定时类型 | report, summary, backup, notification, custom |
