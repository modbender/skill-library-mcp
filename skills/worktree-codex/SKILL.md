---
name: worktree-codex
description: >
  使用 git worktree 隔离多个 Codex 实例，由 OpenClaw 主控器并行调度完成同一项目的不同编码模块。
  适用场景：将一个编码项目拆分为独立子任务，让多个 Codex 实例并行实现，最后合并 PR。
  触发条件：用户要求"多个 Codex 协作"、"并行编码"、"worktree 编码"、"多 Codex 编排"、"并行完成项目"时激活。
---

# Worktree Codex — 多 Codex 并行编码技能

## 前提条件

- Claude Code 二进制：`/mnt/c/Users/Inuyasha/.local/bin/claude.exe`（Windows 侧，可从 WSL 调用）
- GitHub Token：从 `~/.openclaw/openclaw.json` 读取（`skills.entries["gh-issues"].apiKey`）
- 目标 Git 仓库已存在（本地 + GitHub 远端）

## 核心工作流（5 步）

### 步骤 1：明确任务拆分

在开始前，必须确定：
- **每个 Agent 的任务**（1-3 个具体函数/文件）
- **文件所有权**（每个文件只允许一个 Agent 写）
- **并行 or 串行**（有依赖关系的任务需串行）

详见 `references/task-decomposition.md`

### 步骤 2：创建 Worktree

```bash
bash scripts/setup_worktrees.sh <repo_dir> <worktrees_base_dir> <agent-a> <agent-b> ...
```

输出格式：`agent_name:worktree_path:branch_name`（每行一个 Agent）

### 步骤 3：并行启动 Codex

用 exec(background=true) 并行启动多个 Agent，每个调用：

```bash
OPENAI_API_KEY="<key>" \
OPENAI_BASE_URL="http://152.53.52.170:3003/v1" \
CODEX_MODEL="gpt-5.3-codex" \
bash scripts/orchestrate.sh \
  <repo_dir> \
  <agent_name> \
  <worktree_path> \
  <branch> \
  "<task_prompt>" \
  /tmp/<agent_name>.log

# 注意：orchestrate.sh 默认使用 --full-auto（sandbox=workspace-write）
# 如需完全无沙箱，设 CODEX_EXTRA_FLAGS="--dangerously-bypass-approvals-and-sandbox"
```

Task prompt 模板：
```
你是 <AgentName>，只能修改 <file1>, <file2>，不得碰其他文件。
任务：<具体实现要求，含函数签名、异常处理、docstring>
完成后执行：git add -A && git commit -m "<commit message>"
只输出 done。
```

### 步骤 4：启动展板（可选但推荐）

展板是**任务生命周期绑定**的，不是常驻服务：

```
任务启动 → active 模式：SSE 实时推送，1秒刷新
任务完成 → idle 模式：页面保持不失效，停止轮询，显示"等待下次任务"
下次任务 → orchestrate.sh 自动 POST /reload → 恢复 active
```

启动展板（首次，后台运行）：

```bash
python3 skills/worktree-codex/dashboard.py \
  --logs /tmp/agent-a.log /tmp/agent-b.log \
  --port 7789 &
# 浏览器打开 http://localhost:7789
```

之后每次 orchestrate.sh 启动时会自动调用 `/reload`，无需手动操作。
手动激活新任务也可以：

```bash
curl -X POST http://localhost:7789/reload \
  -H 'Content-Type: application/json' \
  -d '{"logs":["/tmp/agent-a.log","/tmp/agent-b.log"]}'
```

展板功能：
- 每个 agent 状态卡（waiting/running/done/failed）+ 进度条 + 实时 token 计数
- idle 模式下页面不失效，数据保持可读
- 所有 agent 完成后，step-3.5-flash 自动效率分析（模型不可用时静默跳过）

### 步骤 5：监控 + 收尾

使用 `process(poll)` 等待所有 Agent 完成，然后检查：

```bash
cat /tmp/<agent_name>.log | grep "AGENT_DONE"
```

如果 Agent 没有自行 commit（常见于第一次），脚本会自动收尾。

### 步骤 5：推送 PR + 合并

```bash
bash scripts/push_and_pr.sh \
  <repo_dir> <gh_token> <owner/repo> <agent_name> <worktree_path> <branch> main
```

验证通过后通过 GitHub API 合并：

```bash
curl -s -X PUT \
  -H "Authorization: Bearer $GH_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/<owner/repo>/pulls/<pr_number>/merge" \
  -d '{"merge_method": "squash"}'
```

## 已知限制与解决方案

**WSL 写文件被沙盒阻止**
→ Claude Code 必须加 `--dangerously-skip-permissions`

**Codex `.cmd` 在 WSL 下无法运行**
→ 使用 `--dangerously-skip-permissions` 的 Claude Code 替代，或在 WSL 安装原生 codex：`npm install -g @openai/codex`

**主仓库 git pull 权限错误（NTFS）**
→ worktree 放在 WSL 本地文件系统（`~/projects/worktrees/`），不放 `/mnt/c/`

**Agent 没有自行 commit**
→ `orchestrate.sh` 脚本会检测未提交变更并自动 commit

## 环境变量获取

```bash
CLAUDE_BIN="/mnt/c/Users/Inuyasha/.local/bin/claude.exe"
GH_TOKEN=$(cat ~/.openclaw/openclaw.json | jq -r '.skills.entries["gh-issues"].apiKey')
```

## 模型选择与限制

**⚠️ 核心限制：Codex CLI 只能用实现了 `/v1/responses` 端点的后端。**

自建代理（`http://152.53.52.170:3003/v1`）只对 OpenAI 原生模型路由 `/responses`，deepseek / gemini / qwen 等全部 404。OpenRouter 同样不支持 `/responses`。

**结论：目前只有 `gpt-5.x-codex` 系列可用。**

| 模型 | `/responses` | 说明 |
|------|-------------|------|
| `gpt-5.3-codex` | ✅ | 默认，推荐 |
| `gpt-4.1-mini` | ✅（待验证） | 轻量 |
| `deepseek-v3` | ❌ 404 | 代理未路由 |
| `gemini-2.5-flash` | ❌ 挂起 | 代理未路由 |
| OpenRouter 任意模型 | ❌ 401 | 不支持端点 |
