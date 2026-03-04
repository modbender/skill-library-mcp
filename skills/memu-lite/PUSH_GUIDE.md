# GitHub 推送指南

## 本地状态

✅ 代码已提交到本地 Git 仓库
⚠️ 需要手动推送到 GitHub

## 推送步骤

### 方式一：命令行推送

```bash
cd ~/.openclaw/workspace/skills-pub/memu-lite

# 1. 确认当前状态
git status
git log --oneline -3

# 2. 推送到 GitHub
git push origin main
```

如果提示认证：
- **用户名**: yoo-unison
- **密码**: 使用 GitHub Personal Access Token

### 方式二：GitHub Desktop

1. 打开 GitHub Desktop
2. File → Add Local Repository → 选择 `~/.openclaw/workspace/skills-pub/memu-lite`
3. 点击 "Push origin"

### 方式三：浏览器上传（会丢失 Git 历史）

1. 打开 https://github.com/yoo-unison/memu-lite
2. 点击需要更新的文件
3. 点击编辑图标 ✏️
4. 手动更新内容
5. Commit changes

## 当前版本

- **ClawHub**: v1.0.3 ✅ 已发布
- **GitHub**: 需要推送到 main 分支

## 验证清单

推送后检查：
- [ ] GitHub 仓库显示最新提交
- [ ] SKILL.md 无"张程"等人名
- [ ] README.md 无"张程"等人名
- [ ] install.sh 使用通用示例
- [ ] memory/ 目录使用通用示例
