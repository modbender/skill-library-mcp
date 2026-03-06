#!/bin/bash
# 科研文献汇报系统一键安装脚本

echo "=========================================="
echo "科研文献汇报系统 - 一键安装"
echo "=========================================="

# 检查Python版本
echo ""
echo "[1/5] 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [ -z "$python_version" ]; then
    echo "❌ 未找到Python3，请先安装Python 3.8+"
    exit 1
fi
echo "✅ Python版本: $python_version"

# 安装依赖
echo ""
echo "[2/5] 安装Python依赖..."
echo "安装核心依赖..."
pip3 install -q feedparser requests pyyaml 2>&1 | grep -v "WARNING\|DEPRECATION" || true

echo "安装可选依赖（PDF生成）..."
pip3 install -q markdown weasyprint 2>&1 | grep -v "WARNING\|DEPRECATION" || true

echo "✅ 依赖安装完成"

# 创建目录
echo ""
echo "[3/5] 创建目录结构..."
mkdir -p data logs
echo "✅ 目录创建完成"

# 检查配置文件
echo ""
echo "[4/5] 检查配置文件..."
if [ ! -f "config.yaml" ]; then
    if [ -f "config.yaml.example" ]; then
        echo "⚠️  未找到config.yaml，正在从config.yaml.example创建..."
        cp config.yaml.example config.yaml
        echo "✅ 已创建config.yaml，请修改其中的API Key和用户ID"
    else
        echo "❌ 未找到config.yaml.example，请手动创建config.yaml"
    fi
else
    echo "✅ 配置文件已存在"
fi

# 验证安装
echo ""
echo "[5/5] 验证安装..."
if [ -f "scripts/verify_install.py" ]; then
    python3 scripts/verify_install.py
else
    echo "⚠️  verify_install.py不存在，跳过验证"
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 编辑config.yaml，填入你的API Key和用户ID"
echo "  2. 运行: python3 scripts/fetch_papers.py"
echo "  3. 设置定时任务: openclaw cron add literature-report --time '0 9 * * *'"
echo ""