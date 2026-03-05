# PM 工作流

小西在任务全生命周期中的操作指南。

## 一、规划与拆解

开始新一轮工作前：

1. 打开 `roadmap/roadmap.md`，确认当前推进的 Epic
2. 进入该 Epic 目录，阅读 `epic.md` 了解目标和验收标准
3. 按 `templates/task.md` 模板创建 Task 文件

### Task 质量检查

创建 Task 时确保以下必填项都能写清楚，写不清楚说明拆得不够细：

- **目标**：一句话说清交付什么
- **验收条件**：具体操作步骤 + 预期结果（不是"功能正常"）
- **预估工作量**：S / M / L

如果一个 Task 包含多个功能点，或者验收条件超过 5 条，考虑继续拆分。
更多拆解技巧见 [breakdown-guide.md](breakdown-guide.md)。

## 二、派发

1. 确认 TASK.md 为空
2. 将 Task 文件内容同步到 TASK.md，State 设为 `Assigned`
3. 通过 `sessions_send` 通知小栈

一次只派一个 Task。当前 Task 未结案不派新任务。

## 三、跟踪

任务进入 `In Progress` 后：

- 关注小栈的 Log 更新（Starting / Blocked / Clarify）
- 收到 `Clarify` → 补充说明或调整任务，回复小栈
- 收到 `Blocked` → 判断是否需要升级给西瓜粥
- 收到 `Handoff` → 进入验收

## 四、验收

1. 读取小栈的 Handoff 记录，了解做了什么、怎么验证
2. 用 Browser 亲自验证 UI 和功能
3. 验收通过 → 进入结案
4. 验收不通过 → 在 Log 写反馈，State 改回 `In Progress`，通知小栈修改

## 五、结案

按顺序执行，不可跳步：

1. 在 TASK.md Log 区写入 `[小西] Approved`
2. 更新 `epic.md` 的 Task 清单状态为 Done
3. 向 Charles 发送结案播报
4. 清空 TASK.md

Epic 下所有 Task 完成后，将 `epic.md` 状态改为"已完成"，更新 `roadmap.md`。
