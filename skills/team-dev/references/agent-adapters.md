# Agent Adapters (dev-team)

本文档与 **[AGENTS.md](AGENTS.md) §4（Agent 指派策略）、§7（状态机）** 互补：AGENTS 侧重编排流程与状态机，本文档侧重各 agent 的配置、角色与使用建议。

## 目标

- 在 `spawn -> coding -> PR -> CI -> AI review -> fixup -> merge -> cleanup` 全流程中合理分配 agent
- 降低 agent 行为差异带来的失败率（提示词适配、能力边界、工具约束）
- 通过配置项控制哪些 agent 允许使用

## 配置项（`config/user.json`）

新增 `agentPolicy`：

```json
{
  "agentPolicy": {
    "enabledAgents": ["codex", "claude", "gemini", "cursor"],
    "phaseAllowedAgents": {
      "build": ["codex", "claude", "cursor", "gemini"],
      "review": ["codex", "gemini", "claude"],
      "fixup": ["codex", "claude", "cursor", "gemini"]
    },
    "phasePreferredOrder": {
      "build": ["codex", "claude", "cursor", "gemini"],
      "review": ["codex", "gemini", "claude"],
      "fixup": ["codex", "claude", "cursor", "gemini"]
    }
  }
}
```

说明：

- `enabledAgents`: 全局启用开关（禁用后 `spawn-agent` / `recommend-agent` / `review-agent` 都会拦截）
- `phaseAllowedAgents`: 按阶段允许列表
  - `build`: 研发/实现阶段
  - `review`: AI 审核阶段
  - `fixup`: 审核后返工阶段
- `phasePreferredOrder`: 当前主要用于运营约定（后续可扩展为强路由排序）

## 脚本支持

- `scripts/spawn-agent.sh`
  - 新增 `--phase build|review|fixup`（默认 `build`）
  - 会校验 `agentPolicy.enabledAgents` 和 `agentPolicy.phaseAllowedAgents.<phase>`
  - `--agent auto` 会带 `--phase` 调用 `recommend-agent`
- `scripts/recommend-agent.sh`
  - 新增 `--phase build|review|fixup`
  - 推荐时会过滤掉禁用 agent / 阶段不允许 agent
- `scripts/review-agent.sh`
  - 会读取 `review.requiredReviewers`
  - 会按 `agentPolicy` 过滤 reviewer（例如禁用 `gemini`）

## 默认角色定位（建议）

### Codex

- 优势：复杂逻辑、后端、跨文件重构、边界条件、疑难 bug
- 建议用途：
  - `build`: 后端/API/脚本/状态机/并发与恢复逻辑
  - `review`: 主审（高权重）
  - `fixup`: 处理高风险/高复杂返工
- 提示词要点：
  - 明确 DoD、输出格式、必须提交 commit
  - 给出约束（只在当前仓库、不要离开 worktree）
  - 复杂任务优先让其做“最小可验证增量”

### Claude

- 优势：前端 UI、文案可读性、快速迭代、git 操作容错较好
- 建议用途：
  - `build`: 前端页面、交互、信息层级优化
  - `review`: 校验审（低权重，critical 才阻塞）
  - `fixup`: 中低风险 UI/交互返工
- 注意：
  - 某些环境下可能出现“静默执行/日志少”，不要只靠日志大小判断失败
  - 以产物/状态收口为准

### Gemini

- 优势：安全/扩展性/建议项视角、与其他 reviewer 差异互补
- 建议用途：
  - `review`: 副审（高价值）
  - `build`: 方案/规范/前端文案/轻量实现（当前环境已验证可执行本地文件操作）
  - `fixup`: 审核后小型返工、补充说明与低风险修改
- 当前环境说明（已验证）：
  - 你的 Gemini CLI 需要显式开启工具权限（`--approval-mode yolo` + `--allowed-tools ...`）
  - `dev-team` 已在 `config/agents.json` 为 Gemini 配置好默认参数

### Cursor (dev: composer-1.5 / plan: gpt-5.3-codex)

- 优势：前端产品化、UI polish、体验优化（在你的机器上 `composer-1.5` 已验证可跑）
- 建议用途：
  - `build`: UI/UX/产品化任务优先候选
  - `fixup`: 前端返工
  - `review`: 默认不建议（除非你验证过 reviewer 输出稳定）
- 注意：
  - 依赖登录态和运行环境（tmux 内已验证可用）
  - 开发模式建议模型：`composer-1.5`
  - plan 模式（版本前差异分析）建议模型：`gpt-5.3-codex`
  - `spawn-agent.sh` 支持 `--cursor-mode plan`，会自动注入 `cursor agent --mode plan`，并强制 `gpt-5.3-codex`

## 推荐的全流程编排策略

### 1. Build 阶段（实现）

- 后端/状态机/API：`codex`
- 前端 UI/产品化：`cursor` 或 `claude`
- 方案/规范/设计稿文字说明：`gemini`（可选）

命令示例：

```bash
./scripts/spawn-agent.sh \
  --agent auto \
  --phase build \
  --repo-path "/path/to/repo" \
  --branch "feat/xxx" \
  --description "..." \
  --completion-mode session \
  --prompt-file /tmp/task.prompt
```

### 2. Review 阶段（AI 三审）

- 默认：`codex,gemini,claude`
- 聚合规则：`codex` 主审、`gemini` 副审、`claude` 校验审

命令示例：

```bash
./scripts/review-agent.sh \
  --repo owner/repo \
  --branch 123 \
  --reviewers codex,gemini,claude
```

### 3. Fixup 阶段（返工）

- 优先回原 subagent（owner）
- 高复杂/高风险返工切回 `codex`
- 前端返工优先 `claude/cursor`

建议：

- 将聚合后的 `findings` 转成结构化 fix prompt
- 明确“继续同一分支修复，不要新建 PR”

## 提示词适配建议（按 agent）

### 通用要求（都要有）

- 仅在当前仓库工作，不要离开 worktree
- 明确允许改动文件范围
- 明确完成标准（DoD）
- 明确是否要创建 PR / commit
- 最终输出固定格式（Summary / 文件列表 / 验证步骤 / 风险）

### Gemini 特殊约束（建议）

- 优先给出明确文件范围和简短任务目标，减少它在工具选择上的犹豫
- 如果任务需要复杂多文件重构，优先 `codex`；Gemini 更适合轻量实现与 reviewer/修复建议
- 若将来 Gemini CLI 升级后工具权限行为变化，再回到 `config/agents.json` 调整参数（`--allowed-tools` 未来可能迁移到 Policy Engine）

### Claude/Cursor 特殊约束（长 prompt）

- 优先使用 `--prompt-file`，避免 shell 转义问题
- 如任务非常长，拆成两个子任务（数据契约 / UI 实现）

## 运行策略建议（推荐初始配置）

- `build`: `codex`, `claude`, `cursor`, `gemini`
- `review`: `codex`, `gemini`, `claude`
- `fixup`: `codex`, `claude`, `cursor`, `gemini`

## 排障清单

- `spawn-agent` 成功但日志 0 字节：
  - 先跑 `./scripts/check-agents.sh`
  - 查看是否被判定为空壳会话并重试
  - 查看 `assets/active-tasks.json` 的 `launchScript` / `checks.lastUnhealthySessionReason`
- agent 能启动但任务不完成：
  - 查看 `assets/logs/<session>.log`
  - 判断是“工具能力不匹配”还是“prompt 不清晰”
  - 对 Gemini：优先检查 `config/agents.json` 的 `--approval-mode yolo` 与 `--allowed-tools` 是否仍兼容当前 CLI 版本
