#!/bin/bash
# 品牌监控 Skill 安装脚本

set -e

echo "================================"
echo "品牌监控 Skill 安装向导"
echo "================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python 3"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ 找到 Python $PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误：未找到 pip3"
    echo "请先安装 pip3"
    exit 1
fi

echo "✓ 找到 pip3"
echo ""

# 安装依赖
echo "正在安装 Python 依赖..."
cd crawler
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Python 依赖安装成功"
else
    echo "❌ Python 依赖安装失败"
    exit 1
fi

cd ..
echo ""

# 配置文件
if [ ! -f "config.json" ]; then
    echo "正在创建配置文件..."
    cp config.example.json config.json
    echo "✓ 已创建 config.json"
    echo ""
    echo "⚠️  请编辑 config.json 配置以下信息："
    echo "   - brand_name: 你的品牌名称"
    echo "   - feishu_webhook: 飞书机器人 Webhook URL"
    echo ""
else
    echo "✓ 配置文件已存在"
    echo ""
fi

# 测试爬虫
echo "正在测试爬虫（Mock 模式）..."
cd crawler
TEST_OUTPUT=$(python3 search_crawler_serpapi.py "测试" "weibo" 3 24 --mock 2>&1)

if [ $? -eq 0 ]; then
    echo "✓ 爬虫测试成功"
else
    echo "⚠️  爬虫测试失败"
    echo "   错误信息: $TEST_OUTPUT"
fi

cd ..
echo ""

# 检查 SerpAPI Key
echo "检查 SerpAPI 配置..."
if [ -z "$SERPAPI_KEY" ]; then
    echo "⚠️  未设置 SERPAPI_KEY 环境变量"
    echo ""
    echo "   SerpAPI 是推荐的搜索服务："
    echo "   - 免费额度：100 次/月"
    echo "   - 稳定可靠，无需维护"
    echo ""
    echo "   获取 API Key："
    echo "   1. 访问 https://serpapi.com/"
    echo "   2. 注册并获取免费 API Key"
    echo "   3. 设置环境变量："
    echo "      export SERPAPI_KEY='your_api_key'"
    echo ""
    echo "   或使用 Mock 模式测试（无需 API Key）："
    echo "      cd crawler"
    echo "      python3 search_crawler_serpapi.py '理想汽车' 'weibo' 5 24 --mock"
else
    echo "✓ SERPAPI_KEY 已设置"
    echo "  Key: ${SERPAPI_KEY:0:10}..."
fi
echo ""

# 完成
echo "================================"
echo "✓ 安装完成！"
echo "================================"
echo ""
echo "下一步："
echo "1. 编辑配置文件: nano config.json"
echo "2. 配置品牌名称和飞书 Webhook"
echo "3. 配置 SerpAPI Key（推荐）："
echo "   - 访问 https://serpapi.com/ 获取免费 API Key"
echo "   - 设置环境变量: export SERPAPI_KEY='your_key'"
echo "   - 或使用 Mock 模式测试（无需 API Key）"
echo "4. 运行监控: openclaw agent --message '执行品牌监控'"
echo ""
echo "文档："
echo "- SerpAPI 使用指南: cat crawler/SerpAPI使用指南.md"
echo "- 快速参考: cat 快速参考.md"
echo "- 项目总结: cat 项目状态总结.md"
echo ""
