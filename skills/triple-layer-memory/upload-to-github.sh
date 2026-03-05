#!/bin/bash
# 上传 triple-layer-memory skill 到 GitHub

echo "=== 上传 triple-layer-memory skill 到 GitHub ==="
echo ""

# 1. 手动创建 GitHub 仓库
echo "步骤 1: 创建 GitHub 仓库"
echo "----------------------------------------"
echo "1. 访问: https://github.com/new"
echo "2. 仓库名称: triple-layer-memory"
echo "3. 描述: 三层记忆系统 - 解决 AI Agent 长对话记忆丢失和上下文管理问题"
echo "4. 选择 Public（公开）"
echo "5. 不要勾选 'Initialize this repository with a README'"
echo "6. 点击 'Create repository'"
echo ""
read -p "创建完成后按回车继续..."

# 2. 初始化 Git 仓库
echo ""
echo "步骤 2: 初始化 Git 仓库"
echo "----------------------------------------"
cd /Users/vulcanx/Desktop/clawork/openclaw-workspace/skills/triple-layer-memory

if [ ! -d ".git" ]; then
    git init
    echo "✓ Git 仓库已初始化"
else
    echo "✓ Git 仓库已存在"
fi

# 3. 添加文件
echo ""
echo "步骤 3: 添加文件"
echo "----------------------------------------"
git add .
git status
echo ""
read -p "确认文件列表无误后按回车继续..."

# 4. 提交
echo ""
echo "步骤 4: 提交"
echo "----------------------------------------"
git commit -m "feat: 初始化三层记忆系统 skill

- Session 自动压缩（150k tokens 触发）
- 记忆写入时机优化（关键时机立即写入）
- 跨 Session 记忆连续性（智能加载）
- 记忆遗忘机制（语义去重、高频升权、低权归档）
- 频道级记忆隔离（Mem0 命名空间）

包含：
- SKILL.md：完整的使用文档
- README.md：快速开始指南
- scripts/：所有核心脚本
- templates/：架构文档模板
- docs/：配置指南
- init.sh：一键初始化脚本"

echo "✓ 提交完成"

# 5. 关联远程仓库
echo ""
echo "步骤 5: 关联远程仓库"
echo "----------------------------------------"
git remote add origin https://github.com/0range-x/triple-layer-memory.git
echo "✓ 远程仓库已关联"

# 6. 配置 Git 凭证
echo ""
echo "步骤 6: 配置 Git 凭证"
echo "----------------------------------------"
git config credential.helper store
echo "✓ Git 凭证助手已启用"

# 7. 推送到 GitHub
echo ""
echo "步骤 7: 推送到 GitHub"
echo "----------------------------------------"
echo "即将推送到 GitHub..."
echo "用户名: 0range-x"
echo "密码: 使用你的 Personal Access Token"
echo ""

git branch -M main
git push -u origin main

echo ""
echo "=== 上传完成！==="
echo ""
echo "仓库地址: https://github.com/0range-x/triple-layer-memory"
echo ""
echo "下一步（可选）："
echo "1. 发布到 ClawHub: https://clawhub.com/submit"
echo "2. 添加 Topics 标签: memory, openclaw, agent, session-management"
echo "3. 编辑仓库描述和 About 信息"
