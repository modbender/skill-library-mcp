---
name: github-repo-mirror
description: 完整迁移 GitHub 仓库，保留所有提交记录、分支和标签。用于将仓库从一个 GitHub 账号完整搬迁到另一个账号。
---

# GitHub 仓库镜像同步

## 场景

将仓库从源账号完整搬迁到目标账号，保留：
- 所有提交历史 (Commits)
- 所有分支 (Branches)
- 所有标签 (Tags)
- 作者信息不变

## 核心命令

```bash
# 步骤 1: 裸克隆 (只下载 .git 目录)
git clone --bare https://github.com/源账号/仓库名.git

# 步骤 2: 镜像推送 (同步所有分支和标签)
cd 仓库名.git
git push --mirror https://github.com/目标账号/仓库名.git
```

## 完整流程

### 步骤 1: 确认访问权限

```bash
# 检查当前登录账号
gh auth status

# 切换到有权限访问源仓库的账号
gh auth switch -u 有权限的账号名
```

### 步骤 2: 裸克隆源仓库

```bash
# 用 HTTPS 克隆 (只读权限足够)
git clone --bare https://github.com/source_account/repo.git
```

### 步骤 3: 切换到目标账号

```bash
gh auth switch -u 目标账号名
```

### 步骤 4: 创建目标仓库

```bash
# 创建空私有仓库
gh repo create repo-name --private --description "仓库描述"
```

### 步骤 5: 镜像推送

```bash
# 重要：需要包含 workflow 权限的 Token
cd repo.git
git push --mirror https://github.com/target_account/repo.git
```

### 步骤 6: 清理

```bash
cd ..
rm -rf repo.git
```

## 实战经验总结

### ✅ 成功经验

| 步骤 | 经验 |
|------|------|
| **访问权限** | 必须用有源仓库访问权限的账号执行 clone |
| **克隆方式** | `git clone --bare` 比 `gh repo clone` 更可靠 |
| **Token 权限** | 包含 workflow 权限才能推送 GitHub Actions |
| **URL 格式** | 直接用 HTTPS URL 最简单 |

### ❌ 失败教训

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| "Repository not found" | 当前账号无访问权限 | `gh auth switch -u` 切换到有权限的账号 |
| "refusing to allow an OAuth App to create or update workflow" | Token 缺少 workflow 权限 | 使用带 workflow 权限的 Token |
| "Permission denied" | SSH key 未配置 | 使用 HTTPS + Token 方式 |

### ⚠️ 关键注意事项

| 事项 | 说明 |
|------|------|
| **目标仓库必须为空** | `--mirror` 会覆盖目标仓库所有内容 |
| **Token 需要 workflow 权限** | 否则无法推送 GitHub Actions workflows |
| **私有仓库搜索不到** | 不能用 GitHub API 搜索，必须直接访问 URL |
| **保留作者信息** | 提交者显示原始作者，非搬运者 |
| **Commit Hash 一致** | 搬迁后 Commit ID 与上游完全相同 |
| **网络要求** | 大仓库可能需要较长时间 |

## 验证搬迁结果

```bash
# 查看目标仓库信息
gh repo view target_account/repo --json name,defaultBranchRef,isPrivate

# 查看所有分支
gh api repos/target_account/repo/branches -q '.[].name'

# 查看标签数量
git push https://TOKEN@github.com/target_account/repo.git --tags --dry-run
```

## 常见问题

**Q: 搬迁后原仓库更新怎么办？**
A: 使用 upstream 远程持续同步：
```bash
git remote add upstream https://github.com/source_account/repo.git
git fetch upstream
git merge upstream/main
git push origin main
```

**Q: 私有仓库搜索不到？**
A: 私有仓库不能通过 API 搜索，必须直接访问 URL 或使用有权限的账号。

**Q: 包含 GitHub Actions 的仓库推送失败？**
A: Token 需要勾选 `workflow` 权限。

**Q: 大型仓库搬迁很慢？**
A: 可以使用 Git LFS 优化，或耐心等待（通常 1-5 分钟）。

**Q: 源仓库所有者不允许转移怎么办？**
A: 用有访问权限的账号克隆后，直接推送到目标账号的新仓库。
