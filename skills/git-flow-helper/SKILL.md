# Git Flow Helper

智能 Git 操作助手，帮助处理分支、合并、冲突等。

## 功能

- 分支管理
- 智能合并
- Cherry-pick
- 清理已合并分支
- Rebase 辅助

## 触发词

- "git操作"
- "git命令"
- "git flow"

## 命令示例

```bash
# 创建分支
git checkout -b feature/new-feature

# 合并分支
git merge feature/new-feature

# 变基
git rebase main

# Cherry-pick
git cherry-pick abc123

# 清理已合并分支
git branch --merged | grep -v '*' | xargs git branch -d
```

## 操作

- create-branch: 创建新分支
- merge: 合并分支
- rebase: 变基操作
- cherry-pick: 挑选提交
- clean-branches: 清理已合并分支
