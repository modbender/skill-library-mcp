---
name: peter-commit-ops
description: 提交与建 PR 桥接自动化。负责将“可提交”改动落成 commit、推送分支并创建 PR，衔接 peter-code-review 与 peter-pr-ops。用于用户提到“帮我提交”“推分支”“创建 PR”“从 review 到 merge 串起来”等场景。
version: 1.1.0
---

# Peter Commit Ops

## 30 秒简介
用于“把可提交改动变成可收口 PR”。

它聚焦 4 件事：
1. 检查是否满足提交前门禁
2. 原子化暂存并创建规范 commit
3. 推送分支并创建/更新 PR
4. 输出可继续交给 CI/PR 收口的状态

## 适用场景
- 用户提到“帮我 commit”“帮我 push”“创建 PR”
- 已完成 `peter-code-review`，结论为“可提交”或“可提交（高风险）”
- 需要把本地改动接入 `peter-ci-gate` 和 `peter-pr-ops`

## 执行步骤
1. 前置确认：
```bash
git status -s
git rev-parse --abbrev-ref HEAD
```
- 若工作区为空：停止并提示“无可提交改动”。
- 若上一步审查结论是“需修复后提交”：停止并要求先修复问题。
- 若上一步审查结论是“可提交（高风险）”：允许继续，但必须在交接输出中显式标注风险并建议优先执行 `peter-ci-gate`。

2. 分支策略：
```bash
git rev-parse --abbrev-ref HEAD
```
- 若在 `main`/`master`：创建并切换特性分支（例如 `feat/<topic>`、`fix/<topic>`）。
- 若已在特性分支：继续使用当前分支。

3. 原子暂存与提交：
```bash
git diff --name-only
git add <files>
```
- 默认只暂存当前任务相关文件，避免混入无关改动。
- 提交前执行（若存在）：
```bash
npm run workflow:check
# 若仓库未定义该命令，回退：
# tools/workflow-check.sh --staged 或 scripts/workflow-check --staged
```
- 提交：
```bash
git commit -m "feat: <summary>"
```
- 提交信息遵循仓库约定：`feat|fix|chore|docs: <简述>`。

4. 推送与 PR：
```bash
git push -u origin <branch>
gh pr create --fill
```
- 若已存在 PR：改为输出 PR 链接并提示进入 CI gate。
- 若 `gh` 不可用：输出手工创建 PR 的比较链接。

5. 交接输出：
- commit SHA
- branch 名称
- PR URL（或阻塞原因）
- 下一步建议：`peter-ci-gate` 或 `peter-pr-ops`
- 若审查为“可提交（高风险）”，必须附：
  - 风险摘要（例如 `GATE_DB_UNREACHABLE`）
  - 强制建议先执行 `peter-ci-gate` 再考虑合并

## 输出格式（固定）
1. `## 提交与 PR 报告`
2. `### 前置检查`（工作区/分支/门禁）
3. `### 执行动作`（add/commit/push/pr）
4. `### 产出物`（SHA、branch、PR）
5. `### 结论`（`已进入 CI 阶段` / `阻塞`）

## 护栏
- 审查未通过时，不提交。
- 默认不使用 `git add .`，除非用户明确要求。
- 禁止直接推送到 `main`/`master`。
- 推送或建 PR 失败时，必须给出错误摘要与下一步修复建议。
