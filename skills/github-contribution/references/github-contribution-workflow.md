# GitHub 开源项目贡献完整工作流程

## 1. Fork 和同步项目

### Fork 官方仓库
- 访问目标项目的 GitHub 页面（例如 `https://github.com/owner/repo`）
- 点击右上角的 "Fork" 按钮
- 选择你的 GitHub 账户作为 fork 目标

### 克隆你的 Fork
```bash
git clone https://github.com/your-username/repo.git
cd repo
```

### 添加上游远程仓库
```bash
git remote add upstream https://github formulate the official repository URL
git remote -v  # 验证远程仓库配置
```

### 同步 Fork 到最新状态
```bash
# 切换到 main/master 分支
git checkout main

# 获取上游仓库的最新更改
git fetch upstream

# 将上游的更改合并到本地
git merge upstream/main

# 推送到你的 fork
git push origin main
```

## 2. 创建功能分支

### 基于最新的 main 分支创建新分支
```bash
# 确保在 main 分支且已同步
git checkout main
git pull upstream main

# 创建新的功能分支（使用描述性名称）
git checkout -b fix/issue-description
# 或者
git checkout -b feature/new-functionality
```

### 分支命名约定
- `fix/` - 用于 bug 修复
- `feature/` - 用于新功能
- `docs/` - 用于文档更新
- `chore/` - 用于维护任务

## 3. 开发和测试

### 进行代码更改
- 在功能分支上进行所有开发工作
- 遵循项目的代码风格和规范
- 编写必要的测试用例
- 更新相关文档（如果需要）

### 提交更改
```bash
# 查看更改状态
git status

# 添加更改的文件
git add .

# 提交更改（使用清晰的提交信息）
git commit -m "fix: resolve issue with XYZ component"

# 推送到你的 fork
git push origin fix/issue-description
```

### 提交信息格式
遵循 conventional commits 格式：
- `fix:` - bug 修复
- `feat:` - 新功能
- `docs:` - 文档更新
- `style:` - 代码格式更改
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建过程或辅助工具的变动

## 4. 创建 Pull Request

### 通过 GitHub 网页界面创建 PR
1. 访问你的 fork 仓库页面
2. GitHub 通常会自动检测到新推送的分支并显示 "Compare & pull request" 按钮
3. 点击该按钮进入 PR 创建页面

### PR 标题和描述
- **标题**: 清晰描述更改的目的（例如："Fix null pointer exception in auth handler"）
- **描述**: 
  - 说明问题的背景
  - 描述解决方案
  - 提及相关的 issue（使用 `Closes #123` 或 `Fixes #123`）
  - 列出主要的更改点

### PR 检查清单
- [ ] 代码通过所有测试
- [ ] 遵循项目代码风格
- [ ] 包含必要的测试用例
- [ ] 更新了相关文档
- [ ] PR 描述清晰完整
- [ ] 关联了相关 issue

## 5. PR 审查和合并

### 处理审查反馈
- 及时响应审查者的评论
- 根据反馈进行必要的修改
- 使用新的提交来处理反馈（不要强制推送覆盖历史）

### 更新 PR
```bash
# 在功能分支上进行修改
git add .
git commit -m "address review feedback: improve error handling"
git push origin fix/issue-description
```

### PR 合并后清理
```bash
# 切换回 main 分支
git checkout main

# 删除本地功能分支
git branch -d fix/issue-description

# 删除远程功能分支（可选）
git push origin --delete fix/issue-description
```

## 常见问题和最佳实践

### 保持分支同步
如果 PR 审查时间较长，可能需要将最新的上游更改合并到你的功能分支：
```bash
git checkout main
git pull upstream main
git checkout fix/issue-description
git rebase main
git push --force-with-lease origin fix/issue-description
```

### 避免强制推送
除非必要（如 rebase 后），避免使用 `--force` 推送，使用 `--force-with-lease` 更安全。

### 小而专注的 PR
- 每个 PR 应该解决一个具体的问题
- 避免在一个 PR 中包含多个不相关的更改
- 这样更容易审查和合并

### 社区礼仪
- 保持礼貌和专业的沟通
- 及时响应审查反馈
- 感谢维护者的审查时间
- 遵循项目的贡献指南（CONTRIBUTING.md）