#!/bin/bash
# Git仓库初始化脚本

echo "🚀 开始初始化Git仓库..."

# 检查是否已存在.git目录
if [ -d ".git" ]; then
    echo "⚠️  Git仓库已存在，跳过初始化"
    exit 0
fi

# 初始化Git仓库
echo "🔧 初始化Git仓库..."
git init

# 添加所有文件
echo "📦 添加文件到Git..."
git add .

# 提交初始版本
echo "💾 提交初始版本..."
git commit -m "初始版本: v1.0.0

- 中文分词功能 (jieba集成)
- 拼音转换功能 (pypinyin集成)
- 文本统计功能
- 关键词提取功能
- 中英文翻译功能
- 文本摘要功能
- OpenClaw集成接口
- 完整的文档和示例
- 单元测试框架"

echo ""
echo "✅ Git仓库初始化完成！"
echo ""
echo "📋 下一步:"
echo "1. 在GitHub创建新仓库: https://github.com/new"
echo "2. 添加远程仓库: git remote add origin <仓库URL>"
echo "3. 推送到GitHub: git push -u origin main"
echo ""
echo "💡 提示:"
echo "  仓库名称建议: openclaw-chinese-toolkit"
echo "  描述: OpenClaw中文处理工具包"
echo "  许可证: MIT"
echo "  .gitignore: Python"
echo ""
echo "🛠️  可选: 设置Git配置"
echo "  git config user.name '你的名字'"
echo "  git config user.email '你的邮箱'"
echo ""
echo "🎉 完成后，你的代码就托管在GitHub上了！"