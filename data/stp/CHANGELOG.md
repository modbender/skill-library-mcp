# STP Skill Changelog

## 2026-03-02

### 修复

1. **Cron Job 添加 channel 参数**
   - 问题：STP 创建 cron 时使用 `--announce` 但未指定 `--channel`
   - 解决：添加 `--channel webchat` 参数，避免 cron 执行报错

2. **task_step 输出清理信息**
   - 任务完成或中断时，`task_steps.md` 中增加清理信息区块
   - 记录：中断/完成时间、终止的子代理、删除的 cron、终止的进程

---

## 2026-02-28

### 核心架构升级：异步子代理模式

**最重要改动：将主会话改为非阻塞模式**

#### 背景
V1 版本在主会话运行，长任务会阻塞整个会话，无法响应用户其他请求。

#### V2 架构
```
主会话 (非阻塞)
    │
    ├── session_spawn (步骤执行) → 执行子代理 (isolated)
    │                              │
    │                              └──→ announce 完成/失败
    │
    ├── session_spawn (步骤检验) → 检验子代理 (LLM)
    │                              │
    │                              └──→ 返回通过/不通过
    │
    └── cron job (定时检查) → 监控子代理状态
```

#### 优势
1. **主会话非阻塞**：发起子任务后立即返回，可响应用户其他请求
2. **子任务独立运行**：每个步骤在独立子代理中运行，互不干扰
3. **通过 announce 通信**：子任务完成后主动通知主会话
4. **定时监控**：cron job 自动检查子任务状态，无需手动追踪

---

### 功能增强

1. **Cron Job 自动管理**
   - `start` 命令自动创建 cron job（`stp-heartbeat-{task_id}`），每 10 分钟检查子任务状态
   - `interrupt` 命令自动删除对应的 cron job
   - Heartbeat 检测到任务完成后自动清理 cron job

2. **Heartbeat 状态检测增强**
   - 新增 `is_running` 判断：基于 `is_waiting`（等待工具返回）或最近 5 分钟有活动
   - 新增 `tool_call_count` 和 `tool_result_count`：更准确判断子代理是否在工作中
   - 新增 `cleanup_reason`：自动清理时返回原因

3. **sessions_history_sync 增强**
   - 返回字段：`is_waiting`, `is_running`, `is_recent`, `tool_call_count`, `tool_result_count`, `last_msg_type`
   - 更准确判断子代理状态

### 架构变化

1. **移除 .current_task 文件**
   - 不再依赖 `.current_task` 文件存储当前任务
   - 改用 cron job 携带 task_id

2. **Heartbeat 触发方式变更**
   - 不再依赖内置 heartbeat + HEARTBEAT.md
   - 改用独立 cron job 定时触发

### 自动清理逻辑

Heartbeat 检测到以下情况会自动删除 cron job：
- 没有活跃子代理
- 所有子代理不在工作中（completed/idle）
- 所有子代理会话不存在（可能已手动清理）

### 使用方式

```bash
# 启动任务（自动创建 cron job）
python3 stp_orchestrator.py start <plan_file>

# 中断任务（自动删除 cron job）
python3 stp_orchestrator.py interrupt <task_id>

# 手动检查状态
python3 stp_orchestrator.py heartbeat <task_id>
```
