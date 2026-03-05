# dev-board

Monorepo 风格的开发进度看板（前后端），用于配合 `team-dev` 查看主 Agent（编排者）和 subagent 的任务状态、日志、进度与运行情况。

## 结构

- `apps/api`：Node.js API 服务（无第三方依赖）
- `apps/web`：静态前端看板页面
- `packages/shared`：共享状态/进度计算逻辑
- `scripts/smoke-check.js`：本地烟雾检查脚本

## 启动

```bash
npm run dev
```

默认地址：`http://localhost:4310`

## API 简述

- `GET /api/health`：健康检查与 team-dev 目录信息
- `GET /api/summary`：主 Agent 摘要 + 统计口径（含 cleaned/done/failed/cancelled 等）
- `GET /api/tasks`：当前活跃任务列表（含派生字段，如 `statusLabel`、`statusCategory`、`phaseLabel`、`humanDuration`）
- `GET /api/board`：看板视角分组（active/recent completed/failed/cleaned 等）
- `GET /api/history?limit=200&file=xxx.jsonl`：归档历史任务（读取 `logs/archives/*.jsonl`）
- `GET /api/tasks/:id/log?lines=200`：任务日志尾部 + 文件元数据
- `GET /api/logs/orchestrator?type=cron|cleanup&lines=200`：编排日志尾部 + 文件元数据

## 与 team-dev 集成

服务默认读取：
- 若 `dev-board` 内置在 `dev-team/dev-board` 下，会自动读取其上级目录（即 `dev-team` skill 根目录）
- 否则回退到本机默认路径（可用环境变量覆盖）

可通过环境变量覆盖：

```bash
TEAM_DEV_SKILL_DIR=/path/to/dev-team npm run dev
```

## 本地操作台 (Local Ops Console)

前端任务详情页集成了“操作台”面板，允许开发者直接通过 Web 界面触发本地脚本和 Agent 动作。

### 启用方式

出于安全考虑，本地动作默认禁用。需设置环境变量开启：

```bash
# 启用本地动作 API，并指定 team-dev 路径
ENABLE_LOCAL_ACTIONS=1 TEAM_DEV_SKILL_DIR=/path/to/dev-team npm run dev
```

### 可用动作

- **Check**: 执行 `smoke-check.js` 或分片测试，验证当前分支代码质量。
- **AI Review**: 触发 AI 对当前任务产出进行代码审查。
- **Fixup**: 针对 Review 意见或测试失败，自动派发“修复”任务给 Agent。
- **Cleanup**: 清理本地临时分支、任务缓存或已合并的资源。

> [!CAUTION]
> **安全提示**：操作台动作会直接在运行 `dev-board` 的机器上执行本地脚本。**切勿将开启了 `ENABLE_LOCAL_ACTIONS` 的服务暴露在公网**。

## 典型开发流程 (Typical Workflow)

面向实际开发者/编排者的推荐链路：

1. **任务下发**：通过 `team-dev` 启动 subagent 进行功能开发。
2. **自动化检查 (Check)**：在看板点击 `Check`，确认基础功能无误。
3. **智能审查 (AI Review)**：点击 `AI Review` 获取初步反馈。
4. **迭代修复 (Fixup)**：若 Review 发现问题，点击 `Fixup` 让 Agent 自动完善。
5. **人工核对 (Approve)**：人工检查代码，确保符合预期。
6. **合并代码 (Merge)**：完成 PR 合并。
7. **资源回收 (Cleanup)**：点击 `Cleanup` 释放资源，保持环境整洁。

## 故障排查 (Troubleshooting)

1. **Team-Dev 路径错误**：若 API 报错 `ENOENT`，请检查 `TEAM_DEV_SKILL_DIR` 是否指向正确的 `skills/dev-team`（或你的实际 skill 目录） 。
2. **环境工具缺失**：`ai-review` 或 `fixup` 依赖 `gh` (GitHub CLI)、`cursor` 或 `gemini` 等工具。请确保它们已安装并配置在系统的 `$PATH` 中。
3. **Tmux 会话空壳/日志为空**：
   - 检查 Agent 是否因权限问题启动失败。
   - 确认 `team-dev` 的 `logs/` 目录是否有写入权限。
4. **操作 API 返回 501**：请确认启动时已设置 `ENABLE_LOCAL_ACTIONS=1`。
5. **按钮置灰禁用**：
   - 检查当前任务是否关联了有效的 Git 分支。
   - 部分动作（如 AI Review）需要检测到关联的 Pull Request 才会启用。

## 说明（作为 dev-team 测试项目）

`team-dev` 当前 `spawn-agent.sh` 默认假设仓库位于 skill 目录的上级目录下。若要直接对本项目派工，可使用：

- 在 `team-dev` 侧增强 `--repo-path`（推荐，后续可做）
- 或临时使用相对路径穿透（不够优雅）
- 或建立一个指向本项目的符号链接到 `team-dev` 所期望的 repos 根目录

---

**[PR flow smoke test]** 此行为 CI/review 流程验证而追加，可安全回滚。
