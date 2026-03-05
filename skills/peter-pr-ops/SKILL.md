---
name: peter-pr-ops
description: PR 收口自动化。单 PR 串行合并与多 PR 批量清理，减少重复人工操作。
version: 1.2.1
---

# Peter PR Ops

## 30 秒简介
用于“把 PR 处理完”。

默认优先复用仓库脚本：
- 单 PR：`scripts/automerge`
- 批量 PR：`scripts/massageprs`

脚本缺失时，优先补齐脚本；补齐失败再回退到 `gh` 命令流。

## 适用场景
- 用户提到“合并这个 PR”“批量清理 PR”“自动处理评论与 CI”

## 执行步骤
1. 识别处理模式：
- 单 PR：串行盯到结果
- 多 PR：批量配置自动合并

2. 优先脚本路径：
```bash
scripts/automerge <pr>
scripts/massageprs <pr1> <pr2>
```

3. 脚本缺失时优先补齐（再重试第 2 步）：
```bash
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if [ -x "$repo_root/scripts/ensure-workflow-docs" ]; then
  "$repo_root/scripts/ensure-workflow-docs" all
elif [ -x "$HOME/ai_code/study_peter/scripts/ensure-workflow-docs" ]; then
  "$HOME/ai_code/study_peter/scripts/ensure-workflow-docs" all
else
  echo "ensure-workflow-docs not found"
fi
```

4. 回退路径（补齐失败或不可用时）：
- 单 PR（默认 squash）：
```bash
gh pr view <pr> --json number,state,mergeStateStatus
gh pr checks <pr>
gh pr merge <pr> --auto --squash
```
- 批量 PR（默认不 squash，便于并发收口）：
```bash
gh pr list --author "@me" --state open --json number --jq '.[].number'
gh pr merge <pr> --auto --merge
```

5. 输出结果：
- 已完成合并
- 仍在等待 CI
- 被阻塞（含原因）
- 是否已刷新 `docs/SESSION-BOOTSTRAP.md`（`Last Updated` + `Last Merge Baseline`）

## 护栏
- CI 红灯不强合。
- 单 PR 默认 squash（与 Peter 的 `/automerge` 习惯一致）。
- 批量模式默认不强制 squash，避免破坏已有历史策略。
- 合并完成后，默认刷新一次 `docs/SESSION-BOOTSTRAP.md` 时间戳与 merge 基线。
- 每次只报告可执行下一步，不输出空泛状态。
