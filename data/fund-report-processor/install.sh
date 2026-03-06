#!/bin/bash
# 安装资金日报处理器技能

echo "🚀 安装资金日报处理器技能..."
echo "================================"

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 设置执行权限
echo "🔧 设置脚本权限..."
chmod +x automated_fund_report_processor.py
chmod +x batch_process_fund_reports.py  
chmod +x extract_fund_data.py

echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "1. 处理最新邮件: python3 automated_fund_report_processor.py"
echo "2. 批量处理: python3 batch_process_fund_reports.py [目录]"
echo "3. 提取单个文件: python3 extract_fund_data.py [文件路径]"
echo ""
echo "注意: 首次使用前请编辑 automated_fund_report_processor.py"
echo "      配置邮箱账户信息"