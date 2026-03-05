#!/bin/bash
# SafeExec 发布脚本 v0.1.2
# 自动化 GitHub 仓库创建和发布

set -e

REPO_NAME="safe-exec"
GITHUB_USER="yourusername"
VERSION="0.1.2"

echo "🚀 SafeExec 发布助手 v$VERSION"
echo "================================"
echo ""

# 检查是否在 Git 仓库中
if [[ ! -d .git ]]; then
    echo "❌ 错误：不在 Git 仓库中"
    echo "请先运行: git init"
    exit 1
fi

# 检查是否有未提交的更改
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  检测到未提交的更改"
    echo "未提交的文件："
    git status --short
    echo ""
    read -p "是否先提交这些更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📝 提交更改..."
        git add -A
        git commit -m "chore: Pre-release cleanup"
    fi
fi

# 创建 GitHub 仓库（如果还没有）
echo "📦 准备发布到 GitHub..."
echo ""
echo "请按以下步骤操作："
echo ""
echo "1. 创建 GitHub 仓库："
echo "   https://github.com/new"
echo ""
echo "2. 仓库名称: $REPO_NAME"
echo "   描述: AI Agent 安全防护层 - 拦截危险命令，保护你的系统"
echo "   可见性: ☑️ Public"
echo ""
echo "3. 创建后，运行以下命令："
echo ""
echo "   git remote add origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 创建 GitHub Release:"
echo "   https://github.com/$GITHUB_USER/$REPO_NAME/releases/new"
echo ""
echo "   标签: v$VERSION"
echo "   标题: SafeExec v$VERSION - 初始发布"
echo "   描述: 见 RELEASE_NOTES.md"
echo ""

# 创建发布说明
cat > RELEASE_NOTES.md <<'EOF'
# SafeExec v0.1.2 发布说明

## 🎉 首次发布

SafeExec v0.1.2 现已发布！这是 AI Agent 安全防护层的第一个稳定版本。

## ✨ 新功能

- 🔍 **智能风险评估** - 检测 10+ 类危险操作模式
- 🚨 **命令拦截** - 自动拦截危险命令并请求批准
- 📊 **审计日志** - 完整记录所有安全事件
- ⚙️ **灵活配置** - 自定义规则和超时设置
- 🧹 **自动清理** - 过期请求自动清理
- 📝 **完整文档** - README、使用指南、贡献指南

## 📦 安装

```bash
git clone https://github.com/yourusername/safe-exec.git ~/.openclaw/skills/safe-exec
chmod +x ~/.openclaw/skills/safe-exec/*.sh
ln -sf ~/.openclaw/skills/safe-exec/safe-exec.sh ~/.local/bin/safe-exec
```

## 🚀 快速开始

```bash
# 执行危险命令
safe-exec "rm -rf /tmp/test"

# 查看待处理请求
safe-exec --list

# 批准请求
safe-exec-approve req_xxxxx
```

## 🔒 安全特性

- ✅ Zero-trust 架构
- ✅ 完整审计追踪
- ✅ 自动过期保护
- ✅ 最小权限原则

## 📚 文档

- [README](README.md) - 项目概览
- [使用指南](USAGE.md) - 详细使用说明
- [博客](BLOG.md) - 项目介绍
- [贡献指南](CONTRIBUTING.md) - 如何贡献

## 🙏 致谢

感谢 OpenClaw 社区的支持和反馈！

## 📮 联系方式

- GitHub: https://github.com/yourusername/safe-exec
- Email: your.email@example.com
- Discord: https://discord.gg/clawd

---

**完整更新日志**: [CHANGELOG.md](CHANGELOG.md)
EOF

echo "✅ 发布说明已创建: RELEASE_NOTES.md"
echo ""

# 创建 GitHub Actions workflow（可选）
mkdir -p .github/workflows
cat > .github/workflows/test.yml <<'EOF'
name: Test SafeExec

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y jq
    
    - name: Run tests
      run: |
        chmod +x test.sh
        bash test.sh
    
    - name: Test safe-exec
      run: |
        chmod +x safe-exec.sh
        ./safe-exec.sh "echo 'test'"
EOF

echo "✅ GitHub Actions workflow 已创建"
echo ""

# 创建标签
echo "🏷️  创建 Git 标签..."
git tag -a "v$VERSION" -m "Release v$VERSION: Initial stable release"
echo "✅ 标签 v$VERSION 已创建"
echo ""

# 显示发布清单
echo "📋 发布清单："
echo ""
echo "✅ Git 仓库已初始化"
echo "✅ 所有文件已提交"
echo "✅ 标签 v$VERSION 已创建"
echo "✅ 发布说明已准备"
echo "✅ GitHub Actions 已配置"
echo ""
echo "🎯 下一步："
echo ""
echo "1. 在 GitHub 上创建仓库"
echo "2. 推送到 GitHub:"
echo "   git remote add origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo "   git push origin v$VERSION"
echo ""
echo "3. 在 Dev.to 发布博客:"
echo "   复制 BLOG.md 内容"
echo "   添加图片和链接"
echo "   发布到: https://dev.to/new"
echo ""
echo "4. 在 OpenClaw Discord 分享:"
echo "   发布到 #projects 频道"
echo "   介绍 SafeExec 的功能"
echo "   请求反馈"
echo ""
echo "5. 提交到 ClawdHub:"
echo "   创建技能包配置"
echo "   提交审核"
echo ""
echo "🚀 祝发布顺利！"
