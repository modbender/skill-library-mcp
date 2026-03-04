#!/bin/bash
# 配置脚本

SERVICE="$1"

case "$SERVICE" in
    "baidu"|"-baidu")
        echo "🔐 配置百度Embedding API..."
        echo ""
        echo "为了使用百度Embedding进行语义搜索，请提供您的API凭证："
        echo ""
        echo "您需要在环境变量中设置以下值："
        echo "  export BAIDU_API_STRING='your_bce_v3_api_string'"
        echo "  export BAIDU_SECRET_KEY='your_secret_key'"
        echo ""
        echo "或者，如果您使用API Key/Secret形式："
        echo "  export BAIDU_API_KEY='your_api_key'"
        echo "  export BAIDU_SECRET_KEY='your_secret_key'"
        echo ""
        echo "💡 获取凭证："
        echo "  1. 访问 https://cloud.baidu.com/"
        echo "  2. 登录百度智能云账户"
        echo "  3. 进入千帆大模型平台"
        echo "  4. 获取Embedding-V1模型的API凭证"
        echo ""
        echo "设置完成后，重启系统使配置生效。"
        ;;
    "all"|"-all")
        echo "🔐 配置所有服务..."
        echo ""
        bash "$0" "baidu"
        ;;
    *)
        echo "❌ 未知服务: $SERVICE"
        echo "支持的服务: baidu, all"
        ;;
esac