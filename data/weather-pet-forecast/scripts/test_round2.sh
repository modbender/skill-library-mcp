#!/bin/bash
# Test weather analysis with retry mechanism

SCRIPT="/home/app/.openclaw/workspace/weather-forecast-analysis/scripts/weather_analysis.py"

test_city_with_retry() {
    local city="$1"
    local max_retries=3
    local retry=0
    local result=""
    
    while [ $retry -lt $max_retries ]; do
        result=$(curl -s --max-time 20 --retry 2 --retry-delay 3 "wttr.in/$city?format=j1" 2>&1)
        
        if [ $? -eq 0 ] && [ -n "$result" ] && echo "$result" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
            echo "$result" | python3 "$SCRIPT" "$city"
            return 0
        fi
        
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            echo "   重试中... ($retry/$max_retries)"
            sleep 2
        fi
    done
    
    echo "❌ 抱歉，尝试 $max_retries 次后仍无法获取 $city 的天气数据"
    echo "   可能是网络连接问题，建议稍后再试 ❤️"
    return 1
}

echo "========================================"
echo "🌤️ 天气分析第二轮测试"
echo "========================================"
echo ""

# Test failed cities from round 1
failed_cities=(
    "Beijing:北京"
    "Osaka:大阪"
    "Kyoto:京都"
    "New+York:纽约"
    "Los+Angeles:洛杉矶"
    "Chicago:芝加哥"
    "Toronto:多伦多"
    "Vancouver:温哥华"
    "London:伦敦"
    "Manchester:曼彻斯特"
    "Edinburgh:爱丁堡"
)

for city_info in "${failed_cities[@]}"; do
    IFS=':' read -r city name <<< "$city_info"
    echo "📍 测试 $name ($city)"
    echo "---"
    test_city_with_retry "$city"
    echo ""
    sleep 3
done

echo "========================================"
echo "✅ 第二轮测试完成"
echo "========================================"
