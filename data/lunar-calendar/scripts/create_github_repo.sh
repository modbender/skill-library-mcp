#!/bin/bash
# GitHub仓库创建和上传脚本
# 作者：夏暮辞青

echo "🚀 GitHub仓库创建与上传脚本"
echo "=============================="
echo "项目: 农历生日提醒系统 v0.9.0"
echo "作者: 夏暮辞青"
echo ""

# 检查必要的工具
echo "🔧 检查必要工具..."
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    echo "   Ubuntu/Debian: sudo apt install git"
    echo "   CentOS/RHEL: sudo yum install git"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "❌ curl未安装，请先安装curl"
    exit 1
fi

echo "✅ 必要工具检查通过"

# 设置变量
REPO_NAME="lunar-birthday-reminder"
REPO_DESC="农历生日提醒系统 - 专业农历计算系统 v0.9.0"
USERNAME="xiamuciqing"  # 需要用户提供
GITHUB_TOKEN=""  # 需要用户提供

echo ""
echo "📋 仓库信息:"
echo "  仓库名: $REPO_NAME"
echo "  描述: $REPO_DESC"
echo "  用户名: $USERNAME"
echo ""

# 检查是否在正确的目录
if [ ! -f "SKILL.md" ] || [ ! -f "package.json" ]; then
    echo "❌ 错误：请在农历生日提醒系统项目根目录运行此脚本"
    exit 1
fi

echo "📁 当前目录文件结构:"
ls -la

echo ""
echo "🎯 手动创建GitHub仓库步骤:"
echo "=============================="
echo "1. 登录GitHub: https://github.com"
echo "2. 点击右上角 '+' → 'New repository'"
echo "3. 填写仓库信息:"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: $REPO_DESC"
echo "   - Public (公开)"
echo "   - 不要初始化README、.gitignore、license"
echo "4. 点击 'Create repository'"
echo ""

echo "📤 上传代码到GitHub的步骤:"
echo "=============================="
echo "1. 初始化Git仓库:"
echo "   git init"
echo "   git add ."
echo "   git commit -m '农历生日提醒系统 v0.9.0 初始提交'"
echo ""
echo "2. 添加远程仓库:"
echo "   git remote add origin https://github.com/$USERNAME/$REPO_NAME.git"
echo ""
echo "3. 推送代码:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 创建v0.9.0标签:"
echo "   git tag v0.9.0"
echo "   git push origin v0.9.0"
echo ""

echo "📝 创建发布版本的步骤:"
echo "=============================="
echo "1. 在GitHub仓库页面，点击 'Releases'"
echo "2. 点击 'Draft a new release'"
echo "3. 填写发布信息:"
echo "   - Tag version: v0.9.0"
echo "   - Release title: 农历生日提醒系统 v0.9.0"
echo "   - 描述内容: 复制 RELEASE_v0.9.0.md 的内容"
echo "4. 上传发布包 (可选):"
echo "   tar -czf lunar-birthday-reminder-v0.9.0.tar.gz ."
echo "5. 点击 'Publish release'"
echo ""

echo "🔗 重要链接:"
echo "=============================="
echo "GitHub仓库URL: https://github.com/$USERNAME/$REPO_NAME"
echo "发布页面: https://github.com/$USERNAME/$REPO_NAME/releases"
echo "问题跟踪: https://github.com/$USERNAME/$REPO_NAME/issues"
echo ""

echo "📊 需要上传的文件清单:"
echo "=============================="
echo "核心文件:"
echo "  ✅ SKILL.md - 技能元数据"
echo "  ✅ README.md - 项目文档"
echo "  ✅ package.json - 项目配置"
echo "  ✅ RELEASE_v0.9.0.md - 发布说明"
echo ""
echo "脚本目录:"
echo "  ✅ scripts/lunar_calculator.py - 农历计算核心"
echo "  ✅ scripts/validate_lunar.py - 验证脚本"
echo "  ✅ scripts/simple_validator.py - 简化验证"
echo "  ✅ scripts/demo_lunar.py - 演示脚本"
echo "  ✅ scripts/publish.sh - 发布脚本"
echo ""
echo "参考文档:"
echo "  ✅ references/fortune_rules.md - 黄历宜忌"
echo "  ✅ references/solar_terms.md - 二十四节气"
echo ""
echo "其他文件:"
echo "  ✅ CLAWHUB_RELEASE.md - 小龙虾社区发布"
echo "  ✅ INSTALL.md - 安装指南"
echo "  ✅ UPDATED_SYSTEM.md - 系统更新报告"
echo ""

echo "🎯 自动化脚本 (如果配置了GitHub Token):"
echo "=============================="
cat > github_auto_setup.sh << 'EOF'
#!/bin/bash
# 自动化GitHub设置脚本
# 需要设置 GITHUB_TOKEN 环境变量

if [ -z "$GITHUB_TOKEN" ]; then
    echo "请设置 GITHUB_TOKEN 环境变量"
    exit 1
fi

# 创建仓库
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "lunar-birthday-reminder",
    "description": "农历生日提醒系统 - 专业农历计算系统 v0.9.0",
    "private": false
  }'

# 初始化本地仓库
git init
git add .
git commit -m "农历生日提醒系统 v0.9.0 初始提交"
git branch -M main
git remote add origin https://$GITHUB_TOKEN@github.com/xiamuciqing/lunar-birthday-reminder.git
git push -u origin main

# 创建标签
git tag v0.9.0
git push origin v0.9.0

echo "✅ GitHub仓库创建完成！"
EOF

chmod +x github_auto_setup.sh
echo "已创建自动化脚本: github_auto_setup.sh"
echo "使用方法: export GITHUB_TOKEN=你的token && ./github_auto_setup.sh"

echo ""
echo "💡 提示:"
echo "=============================="
echo "1. 首次使用建议手动创建仓库熟悉流程"
echo "2. 确保不要上传敏感信息（如API密钥）"
echo "3. 上传前运行测试确保一切正常"
echo "4. 创建仓库后立即设置README.md为首页"
echo ""

echo "👤 作者: 夏暮辞青"
echo "🏷️  版本: v0.9.0"
echo "📅 日期: $(date)"
echo ""
echo "🚀 开始你的GitHub发布之旅吧！"