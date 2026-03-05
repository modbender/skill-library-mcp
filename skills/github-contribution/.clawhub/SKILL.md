---
name: github-contribution
description: GitHub开源项目代码贡献完整工作流程。使用场景：当需要为开源项目解决issue或bug时，提供从fork、同步、开发到提交PR的完整指导。包含Chrome浏览器PR提交支持。
---

# GitHub 开源项目代码贡献技能

## 工作流程概述

为开源项目贡献代码的标准流程：
1. **Fork项目** - 创建官方仓库的个人副本
2. **同步Fork** - 确保与官方main/master分支保持一致  
3. **创建特性分支** - 基于最新代码创建专门的开发分支
4. **开发和测试** - 在特性分支上实现解决方案
5. **提交PR** - 向官方项目提交拉取请求

## 详细步骤指南

### 1. Fork项目并克隆

```bash
# 如果还没有fork，先在GitHub网页上fork项目
# 然后克隆你的fork到本地
git clone https://github.com/your-username/repository-name.git
cd repository-name
```

### 2. 设置上游远程并同步

```bash
# 添加官方仓库作为上游远程
git remote add upstream https://github.com/original-owner/repository-name.git

# 验证远程配置
git remote -v

# 切换到main分支（或master）
git checkout main

# 从上游获取最新更改
git fetch upstream

# 将上游更改合并到本地main
git merge upstream/main

# 推送到你的fork
git push origin main
```

### 3. 创建特性分支

```bash
# 基于最新的main创建新分支
# 分支命名建议：fix/issue-number-brief-description 或 feature/brief-description
git checkout -b fix/123-bug-description

# 验证当前分支
git branch
```

### 4. 开发和测试解决方案

- 在特性分支上编写代码修复issue
- 运行项目的测试套件确保没有破坏现有功能
- 遵循项目的代码风格和贡献指南
- 提交有意义的commit信息

```bash
# 添加更改的文件
git add .

# 提交更改（使用描述性提交信息）
git commit -m "Fix: brief description of what was fixed"

# 推送到你的fork的特性分支
git push origin fix/123-bug-description
```

### 5. 提交Pull Request

#### 使用Chrome浏览器提交PR

1. **访问你的fork页面**：`https://github.com/your-username/repository-name`
2. **切换到特性分支**：在分支选择器中选择你的特性分支
3. **点击"Compare & pull request"按钮**
4. **填写PR模板**：
   - 标题：清晰描述变更内容
   - 描述：详细说明问题和解决方案
   - 关联issue：使用`Closes #123`或`Fixes #123`语法
   - 检查项目：确认满足贡献要求
5. **提交PR**：点击"Create pull request"

#### PR最佳实践

- **标题格式**：使用语义化前缀如 `fix:`, `feat:`, `docs:`, `chore:`
- **描述内容**：
  - 问题背景和影响
  - 解决方案的技术细节  
  - 测试方法和结果
  - 相关issue链接
- **代码审查准备**：
  - 确保代码符合项目风格
  - 添加必要的注释和文档
  - 更新README或CHANGELOG（如果适用）

## 常见问题处理

### 同步冲突解决

如果在同步过程中遇到冲突：

```bash
# 在main分支上
git fetch upstream
git merge upstream/main

# 如果有冲突，手动解决后
git add .
git commit
git push origin main
```

### 特性分支更新

如果官方仓库有新提交，需要更新你的特性分支：

```bash
# 切换到main并同步
git checkout main
git fetch upstream
git merge upstream/main
git push origin main

# 切换回特性分支并rebase
git checkout your-feature-branch
git rebase main

# 如果有冲突，解决后继续
git add .
git rebase --continue

# 强制推送到你的fork（因为rebase改变了历史）
git push --force-with-lease origin your-feature-branch
```

## 贡献检查清单

在提交PR前，请确保：

- [ ] 代码通过所有测试
- [ ] 遵循项目代码风格指南  
- [ ] 添加了必要的测试用例
- [ ] 更新了相关文档
- [ ] PR描述清晰完整
- [ ] 关联了相关issue
- [ ] 本地测试验证通过

## 参考资源

- **GitHub官方贡献指南**：每个项目通常在CONTRIBUTING.md中有详细说明
- **项目特定要求**：检查项目的README、文档和已有PR的模式
- **社区规范**：了解项目的沟通方式和期望

使用此技能时，请根据具体项目的实际情况调整工作流程。