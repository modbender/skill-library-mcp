---
name: peter-ci-gate
description: CI 绿灯门禁。负责远端检查状态、失败定位、单次重跑策略，并输出“是否可合并”。
version: 1.1.0
---

# Peter CI Gate

## 30 秒简介
用于“PR 是否能合并”的远端 CI 判定。

它聚焦 3 件事：
1. 看清当前 checks 状态
2. 判断失败是代码问题还是偶发波动
3. 给出可执行动作（修复或单次重跑）

## 适用场景
- 用户提到“看下 CI”“为什么没过”“是否可以合并”
- PR 临近合并，需要明确 gate 结论

## 执行步骤
1. 获取 PR 与 checks 状态：
```bash
gh pr view <pr> --json number,title,url,state,mergeStateStatus,headRefName
gh pr checks <pr>
```

2. 失败时获取最近 workflow 详情：
```bash
branch=$(gh pr view <pr> --json headRefName --jq '.headRefName')
gh run list --branch "$branch" --limit 20
gh run view <run-id> --log-failed
```

3. 处理策略：
- 代码或测试真实失败：标记阻塞并给修复建议
- 明显偶发失败：允许重跑一次
```bash
gh run rerun <run-id>
```

4. 输出门禁结论：
- `可合并`：所有必需 checks 通过
- `暂不可合并`：存在阻塞项

## 护栏
- 不把“重跑成功”当作根因修复。
- 每个失败项必须给出证据（job/log）。
- 默认不跳过必需检查。
