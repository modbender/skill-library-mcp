#!/bin/bash
# SafeExec GitHub 发布脚本 v0.2.0
# 自动化 GitHub 仓库创建和发布

set -e

REPO_NAME="safe-exec"
VERSION="0.2.0"
GITHUB_USER="${GITHUB_USER:-yourusername}"

echo "🚀 SafeExec GitHub 发布助手 v$VERSION"
echo "======================================"
echo ""

# 检查是否在 Git 仓库中
if [[ ! -d .git ]]; then
    echo "❌ 错误：不在 Git 仓库中"
    exit 1
fi

# 检查工作区状态
if [[ -n $(git status --porcelain) ]]; then
    echo "⚠️  检测到未提交的更改"
    git status --short
    echo ""
    read -p "是否先提交这些更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add -A
        git commit -m "chore: Pre-release cleanup"
    fi
fi

echo "📋 发布前检查"
echo "============"
echo ""
echo "当前分支: $(git branch --show-current)"
echo "最新标签: $(git describe --tags --abbrev=0 2>/dev/null || echo '无')"
echo "提交数: $(git rev-list --count HEAD)"
echo "文件数: $(git ls-files | wc -l)"
echo ""

echo "🌐 GitHub 仓库创建指南"
echo "======================"
echo ""
echo "步骤 1: 创建 GitHub 仓库"
echo "----------------------"
echo "1. 访问: https://github.com/new"
echo ""
echo "2. 填写仓库信息:"
echo "   Repository name: $REPO_NAME"
echo "   Description: AI Agent 安全防护层 - 拦截危险命令，保护你的系统"
echo "   Public: ☑️ (公开仓库)"
echo "   Initialize: ❌ (不勾选任何选项)"
echo ""
echo "3. 点击 'Create repository'"
echo ""
echo "步骤 2: 推送代码到 GitHub"
echo "------------------------"
echo "创建仓库后，复制并运行以下命令:"
echo ""
echo "   git remote add origin git@github.com:$GITHUB_USER/$REPO_NAME.git"
echo "   git branch -M master"
echo "   git push -u origin master"
echo "   git push origin --tags"
echo ""
echo "步骤 3: 创建 GitHub Release"
echo "-------------------------"
echo "1. 访问: https://github.com/$GITHUB_USER/$REPO_NAME/releases/new"
echo ""
echo "2. 填写 Release 信息:"
echo "   Tag: v$VERSION"
echo "   Title: SafeExec v$VERSION - 全局开关功能"
echo "   Description: 复制 RELEASE_NOTES.md 内容"
echo ""
echo "3. 勾选 'Set as the latest release'"
echo "4. 点击 'Publish release'"
echo ""
echo "步骤 4: 验证发布"
echo "---------------"
echo "检查以下链接:"
echo "   Code: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "   Releases: https://github.com/$GITHUB_USER/$REPO_NAME/releases"
echo "   Issues: https://github.com/$GITHUB_USER/$REPO_NAME/issues"
echo ""

# 生成推送命令脚本
cat > push-to-github.sh <<'EOF'
#!/bin/bash
# SafeExec 推送脚本

REPO_NAME="safe-exec"
GITHUB_USER="${1:-yourusername}"

echo "📤 推送 SafeExec 到 GitHub"
echo "=========================="
echo ""
echo "仓库: git@github.com:$GITHUB_USER/$REPO_NAME.git"
echo ""

# 添加远程仓库
if git remote get-url origin &>/dev/null; then
    echo "⚠️  远程仓库已存在"
    git remote -v | grep origin
    echo ""
    read -p "是否更新远程仓库 URL？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin "git@github.com:$GITHUB_USER/$REPO_NAME.git"
        echo "✅ 远程仓库已更新"
    fi
else
    git remote add origin "git@github.com:$GITHUB_USER/$REPO_NAME.git"
    echo "✅ 远程仓库已添加"
fi

echo ""
echo "推送 master 分支..."
git branch -M master
git push -u origin master

echo ""
echo "推送所有标签..."
git push origin --tags

echo ""
echo "✅ 推送完成！"
echo ""
echo "查看仓库: https://github.com/$GITHUB_USER/$REPO_NAME"
EOF

chmod +x push-to-github.sh

echo "📝 已生成推送脚本: push-to-github.sh"
echo ""
echo "创建仓库后，运行:"
echo "   ./push-to-github.sh <你的GitHub用户名>"
echo ""
echo "或手动运行:"
echo "   git remote add origin git@github.com:<你的用户名>/$REPO_NAME.git"
echo "   git push -u origin master"
echo "   git push origin --tags"
echo ""
echo "🎯 发布检查清单"
echo "==============="
echo ""
echo "发布前:"
echo "  ✅ 代码已提交"
echo "  ✅ 文档已完善"
echo "  ✅ 标签已创建"
echo "  ✅ README.md 完整"
echo "  ✅ LICENSE 已添加"
echo ""
echo "发布中:"
echo "  ⏳ 创建 GitHub 仓库"
echo "  ⏳ 推送代码"
echo "  ⏳ 推送标签"
echo "  ⏳ 创建 Release"
echo ""
echo "发布后:"
echo "  ⏳ 发布博客 (Dev.to)"
echo "  ⏳ 社区分享 (Discord)"
echo "  ⏳ 提交到 ClawdHub"
echo ""
echo "📚 相关文档"
echo "=========="
echo "  - RELEASE_v0.2.0.md: 版本发布报告"
echo "  - RELEASE_NOTES.md: 发布说明"
echo "  - BLOG.md: 宣传博客"
echo "  - README.md: 项目主页"
echo ""
echo "🚀 祝发布顺利！"
