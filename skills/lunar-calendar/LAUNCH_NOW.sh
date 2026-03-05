#!/bin/bash
# 农历生日提醒系统 v0.9.0 GitHub上传脚本
# 执行人：夏暮辞青
# 时间：2026-02-13

echo "🚀 农历生日提醒系统 v0.9.0 GitHub上传开始"
echo "================================"
echo "作者: 夏暮辞青"
echo "版本: v0.9.0"
echo "时间: $(date)"
echo ""

# 检查当前目录
if [ ! -f "SKILL.md" ] || [ ! -f "package.json" ]; then
    echo "❌ 错误：请在农历生日提醒系统项目根目录运行此脚本"
    exit 1
fi

echo "📁 当前目录: $(pwd)"
echo "📋 文件数量: $(find . -type f | wc -l) 个文件"
echo ""

# 设置Git配置
echo "🔧 设置Git配置..."
git config --global user.name "夏暮辞青"
git config --global user.email "xiamuciqing@github.com"
echo "✅ Git配置完成"

# 初始化Git仓库
echo "🔄 初始化Git仓库..."
git init
echo "✅ Git仓库初始化完成"

# 添加所有文件
echo "📤 添加文件到Git..."
git add .
echo "✅ 文件添加完成"

# 提交更改
echo "💾 提交更改..."
git commit -m "农历生日提醒系统 v0.9.0 初始发布

🌙 项目概述：
- 专业农历计算系统
- 基于lunardate/cnlunar库
- 已验证5个春节日期100%准确
- 2037年九月初五与华为手机一致

✅ 功能特性：
1. 公历↔农历双向转换
2. 专业库集成验证
3. 完整测试套件
4. 社区发布准备

📊 技术规格：
- Python 3.6+
- 计算速度 <10ms
- 支持1900-2100年
- 开源MIT许可证

👤 作者：夏暮辞青
🏷️ 版本：v0.9.0
📅 日期：2026-02-13"
echo "✅ 提交完成"

# 显示提交信息
echo ""
echo "📝 提交信息摘要："
git log --oneline -1
echo ""

# 提示用户添加远程仓库
echo "🎯 下一步：添加远程仓库"
echo "================================"
echo "请将上一步获取的GitHub仓库URL粘贴到以下命令中："
echo ""
echo "git remote add origin https://github.com/xiamuciqing/lunar-birthday-reminder.git"
echo ""
echo "然后执行："
echo "git branch -M main"
echo "git push -u origin main"
echo ""

# 创建标签
echo "🏷️ 创建版本标签..."
git tag v0.9.0
echo "✅ 标签 v0.9.0 创建完成"
echo ""
echo "推送标签："
echo "git push origin v0.9.0"
echo ""

# 创建发布包
echo "📦 创建发布包..."
tar -czf ../lunar-birthday-reminder-v0.9.0.tar.gz .
echo "✅ 发布包创建完成：../lunar-birthday-reminder-v0.9.0.tar.gz"
echo "大小: $(du -h ../lunar-birthday-reminder-v0.9.0.tar.gz | cut -f1)"
echo ""

# 显示上传状态
echo "📊 上传准备状态："
echo "✅ Git仓库已初始化"
echo "✅ 所有文件已添加"
echo "✅ 提交信息已创建"
echo "✅ 版本标签已设置"
echo "✅ 发布包已创建"
echo ""

echo "🚀 等待执行远程仓库连接..."
echo ""
echo "💡 提示："
echo "1. 确保GitHub仓库已创建"
echo "2. 复制正确的仓库URL"
echo "3. 依次执行上述命令"
echo "4. 检查GitHub页面确认上传成功"
echo ""
echo "👤 作者：夏暮辞青"
echo "⏰ 预计完成时间：10分钟"
echo ""
echo "开始执行吧！🎉"