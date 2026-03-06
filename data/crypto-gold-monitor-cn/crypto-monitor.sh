#!/bin/bash

# 加密货币与贵金属价格监控 / Crypto & Precious Metals Price Monitor
# 用法: crypto-monitor <命令>

set -e

# 颜色 / Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

# USD/CNY汇率 / Exchange rate
get_exchange_rate() {
    local cache_file="/tmp/crypto-monitor/exchange.json"
    local now=$(date +%s)
    
    if [ -f "$cache_file" ]; then
        local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || echo "0")
        if [ $((now - cache_time)) -lt 3600 ]; then
            cat "$cache_file"
            return
        fi
    fi
    
    local rate=7.25
    local resp=$(curl -s --connect-timeout 3 "https://api.exchangerate-api.com/v4/latest/USD" 2>/dev/null || echo "")
    if [ -n "$resp" ]; then
        rate=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['rates'].get('CNY', 7.25))" 2>/dev/null || echo "7.25")
    fi
    
    mkdir -p /tmp/crypto-monitor
    echo "{\"rate\":$rate,\"timestamp\":$now}" > "$cache_file"
    cat "$cache_file"
}

# 获取加密货币数据 / Get crypto data
get_data() {
    local cache_file="/tmp/crypto-monitor/prices.json"
    local now=$(date +%s)
    
    if [ -f "$cache_file" ]; then
        local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || echo "0")
        if [ $((now - cache_time)) -lt 60 ]; then
            cat "$cache_file"
            return
        fi
    fi
    
    local btc_usd=97500 btc_change=2.5 eth_usd=3450 eth_change=1.8
    
    local resp=$(curl -s --connect-timeout 3 "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24h_change=true" 2>/dev/null || echo "")
    
    if [ -n "$resp" ] && echo "$resp" | grep -q "bitcoin"; then
        btc_usd=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['bitcoin']['usd'])" 2>/dev/null || echo "97500")
        btc_change=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['bitcoin']['usd_24h_change'])" 2>/dev/null || echo "2.5")
        eth_usd=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['ethereum']['usd'])" 2>/dev/null || echo "3450")
        eth_change=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin)['ethereum']['usd_24h_change'])" 2>/dev/null || echo "1.8")
    fi
    
    mkdir -p /tmp/crypto-monitor
    cat > "$cache_file" << EOF
{"btc_usd":$btc_usd,"btc_change":$btc_change,"eth_usd":$eth_usd,"eth_change":$eth_change}
EOF
    cat "$cache_file"
}

# 获取贵金属数据 - 国内数据源 / Get metals data - Domestic source
get_metals() {
    local cache_file="/tmp/crypto-monitor/metals.json"
    local history_file="/tmp/crypto-monitor/metals_history.json"
    local now=$(date +%s)
    
    # 检查缓存 / Check cache (5 minutes)
    if [ -f "$cache_file" ]; then
        local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || echo "0")
        if [ $((now - cache_time)) -lt 300 ]; then
            cat "$cache_file"
            return
        fi
    fi
    
    # 张良珠宝API数据源 / Zhangliang jewelry API
    local gold=0 silver=0 gold_cny=0 silver_cny=0 gold_usd=2650 silver_usd=31.20
    
    # 从API获取 / Fetch from API
    local resp=$(curl -s --connect-timeout 5 "http://zhangliang.tideimg.com/data" 2>/dev/null || echo "")
    
    if [ -n "$resp" ] && echo "$resp" | grep -q '"code":200'; then
        # 提取黄金数据 (num3=价格, 直接是元/克)
        gold_cny=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); items=[i for i in d['data']['list'] if i.get('title')=='黄金']; print(items[0]['num3'] if items else 0)" 2>/dev/null || echo "0")
        # 提取白银数据
        silver_cny=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); items=[i for i in d['data']['list'] if i.get('title')=='白银']; print(items[0]['num3'] if items else 0)" 2>/dev/null || echo "0")
        # 提取伦敦金 (国际金价, 美元/盎司)
        gold_usd=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); items=[i for i in d['data']['list'] if i.get('title')=='伦敦金']; print(items[0]['num3'] if items else 2650)" 2>/dev/null || echo "2650")
        # 提取伦敦银 (国际银价, 美元/盎司)
        silver_usd=$(echo "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); items=[i for i in d['data']['list'] if i.get('title')=='伦敦银']; print(items[0]['num3'] if items else 31.20)" 2>/dev/null || echo "31.20")
        
        # 赋值 / Assign directly (num3 is already yuan/gram)
        gold=$gold_cny
        silver=$silver_cny
    fi
    
    # 如果国内数据获取失败，使用国际数据备用 / Fallback to international
    if [ "$gold" == "0" ] || [ -z "$gold" ]; then
        gold_usd=2650
        local gold_resp=$(curl -s --connect-timeout 3 "https://www.goldapi.io/api/XAU/USD" -H "x-access-token: demo" 2>/dev/null || echo "")
        if echo "$gold_resp" | grep -q "price"; then
            gold_usd=$(echo "$gold_resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('price', 2650))" 2>/dev/null || echo "2650")
        fi
        gold=$gold_usd
        silver=$(echo "scale=2; $gold_usd / 85" | bc 2>/dev/null || echo "31.20")
        silver_usd=$silver
    fi
    
    # 计算涨跌幅 / Calculate change
    local gold_change=0 silver_change=0
    if [ -f "$history_file" ]; then
        local prev=$(cat "$history_file")
        local prev_gold=$(echo "$prev" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gold', $gold))" 2>/dev/null || echo "$gold")
        local prev_silver=$(echo "$prev" | python3 -c "import sys,json; print(json.load(sys.stdin).get('silver', $silver))" 2>/dev/null || echo "$silver")
        
        if [ "$prev_gold" != "$gold" ] && [ "$prev_gold" != "0" ]; then
            gold_change=$(echo "scale=2; ($gold - $prev_gold) / $prev_gold * 100" | bc 2>/dev/null || echo "0")
        fi
        if [ "$prev_silver" != "$silver" ] && [ "$prev_silver" != "0" ]; then
            silver_change=$(echo "scale=2; ($silver - $prev_silver) / $prev_silver * 100" | bc 2>/dev/null || echo "0")
        fi
    fi
    
    # 保存历史 / Save history
    mkdir -p /tmp/crypto-monitor
    echo "{\"gold\":$gold,\"silver\":$silver,\"gold_usd\":$gold_usd,\"silver_usd\":$silver_usd,\"timestamp\":$now}" > "$history_file"
    
    # 保存缓存 / Save cache
    cat > "$cache_file" << EOF
{"gold":$gold,"gold_cny":$gold_cny,"gold_usd":$gold_usd,"gold_change":$gold_change,"silver":$silver,"silver_cny":$silver_cny,"silver_usd":$silver_usd,"silver_change":$silver_change}
EOF
    cat "$cache_file"
}

# 格式化货币 / Format currency
fmt_cny() {
    local usd=$1
    local rate=$2
    local cny=$(echo "scale=0; $usd * $rate / 1" | bc 2>/dev/null || echo "0")
    echo "¥$(printf "%.0f" "$cny")"
}

# 格式化涨跌幅 / Format change
fmt_change() {
    local change=$1
    if [ "$change" == "0" ] || [ -z "$change" ]; then
        echo "${YELLOW}--${NC}"
    elif (( $(echo "$change >= 0" | bc -l) )); then
        echo -e "${GREEN}+${change}%${NC}"
    else
        echo -e "${RED}${change}%${NC}"
    fi
}

# 主命令 / Main command
cmd_all() {
    local data=$(get_data)
    local mdata=$(get_metals)
    local exdata=$(get_exchange_rate)
    
    # 解析 / Parse
    btc_usd=$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin)['btc_usd'])" 2>/dev/null || echo "0")
    btc_change=$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin)['btc_change'])" 2>/dev/null || echo "0")
    eth_usd=$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin)['eth_usd'])" 2>/dev/null || echo "0")
    eth_change=$(echo "$data" | python3 -c "import sys,json; print(json.load(sys.stdin)['eth_change'])" 2>/dev/null || echo "0")
    # 国内金价 (元/克)
    gold_cny=$(echo "$mdata" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gold', 0))" 2>/dev/null || echo "0")
    # 国际金价 (美元/盎司)
    gold_usd=$(echo "$mdata" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gold_usd', 0))" 2>/dev/null || echo "0")
    gold_change=$(echo "$mdata" | python3 -c "import sys,json; print(json.load(sys.stdin).get('gold_change', 0))" 2>/dev/null || echo "0")
    gold_liang=$(echo "scale=0; $gold_cny * 50 / 1" | bc 2>/dev/null || echo "0")
    # 国内银价 (元/克)
    silver_cny=$(echo "$mdata" | python3 -c "import sys,json; print(json.load(sys.stdin).get('silver', 0))" 2>/dev/null || echo "0")
    # 国际银价 (美元/盎司)
    silver_usd=$(echo "$mdata" | python3 -c "import sys,json; print(json.load(sys.stdin).get('silver_usd', 0))" 2>/dev/null || echo "0")
    silver_change=$(echo "$mdata" | python3 -c "import sys,json; print(json.load(sys.stdin).get('silver_change', 0))" 2>/dev/null || echo "0")
    rate=$(echo "$exdata" | python3 -c "import sys,json; print(json.load(sys.stdin)['rate'])" 2>/dev/null || echo "7.25")
    
    # 加密货币涨跌颜色 / Crypto change color
    btc_clr=$( [ "$(echo "$btc_change >= 0" | bc)" = "1" ] && echo "$GREEN" || echo "$RED")
    eth_clr=$( [ "$(echo "$eth_change >= 0" | bc)" = "1" ] && echo "$GREEN" || echo "$RED")
    
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}           加密货币与贵金属实时行情 (USD/CNY)${NC}"
    echo -e "${BOLD}           Crypto & Metals Real-Time Prices${NC}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "汇率 / Exchange: 1 USD = ${YELLOW}¥${rate}${NC}"
    echo ""
    
    echo -e "${PURPLE}₿ 加密货币 / Cryptocurrency${NC}"
    echo "─────────────────────────────────────────────────────"
    echo -e "  ${YELLOW}₿ Bitcoin (BTC)$NC"
    echo -e "      价格 / Price:      ${GREEN}\$${btc_usd} / $(fmt_cny "$btc_usd" "$rate")${NC}"
    echo -e "      24h涨跌 / 24h:     ${btc_clr}${btc_change}%${NC}"
    echo ""
    echo -e "  ${CYAN}Ξ Ethereum (ETH)$NC"
    echo -e "      价格 / Price:      ${GREEN}\$${eth_usd} / $(fmt_cny "$eth_usd" "$rate")${NC}"
    echo -e "      24h涨跌 / 24h:     ${eth_clr}${eth_change}%${NC}"
    echo ""
    
    # 计算每两价格 (克*50)
    gold_liang=$(echo "scale=0; $gold_cny * 50 / 1" | bc 2>/dev/null || echo "0")
    
    echo -e "${YELLOW}🥇 贵金属 / Precious Metals${NC}"
    echo "─────────────────────────────────────────────────────"
    echo -e "  ${YELLOW}🥇 Gold (黄金)${NC}"
    echo -e "      国内金价:          ${GREEN}¥${gold_cny}/克 (≈¥${gold_liang}/两)${NC}"
    echo -e "      国际金价:          ${GREEN}\$${gold_usd}/oz${NC}"
    echo -e "      24h涨跌 / 24h:     $(fmt_change "$gold_change")"
    echo ""
    echo -e "  ${CYAN}🥈 Silver (白银)${NC}"
    echo -e "      国内银价:          ${GREEN}¥${silver_cny}/克${NC}"
    echo -e "      国际银价:          ${GREEN}\$${silver_usd}/oz${NC}"
    echo -e "      24h涨跌 / 24h:     $(fmt_change "$silver_change")"
    echo ""
    echo -e "${BOLD}更新时间 / Updated: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
}

# 手动更新贵金属价格 / Manually update metals prices
cmd_update() {
    local gold=${1:-2650}
    local silver=${2:-31.20}
    
    mkdir -p /tmp/crypto-monitor
    echo "{\"gold\":$gold,\"silver\":$silver,\"timestamp\":$(date +%s)}" > "/tmp/crypto-monitor/metals_history.json"
    
    echo -e "${GREEN}✅ 已更新贵金属价格${NC}"
    echo "Gold: \$$gold/oz"
    echo "Silver: \$$silver/oz"
    echo ""
    echo "下次运行时会计算涨跌幅"
    echo "Run 'crypto-monitor all' to see changes"
}

# 帮助 / Help
cmd_help() {
    echo "加密货币与贵金属价格监控 v2.4"
    echo "Crypto & Precious Metals Price Monitor"
    echo ""
    echo "用法: crypto-monitor <命令> [参数]"
    echo "Usage: crypto-monitor <command> [args]"
    echo ""
    echo "命令 Commands:"
    echo "  all                    查看所有价格 (默认) / View all"
    echo "  update <金价> <银价>   手动更新贵金属价格 / Update metals prices"
    echo "                          crypto-monitor update 2680 31.50"
    echo "  refresh                强制刷新 / Force refresh"
    echo "  help                   显示帮助 / Show help"
    echo ""
    echo "注意 / Note:"
    echo "  贵金属API可能限流，如价格显示--请手动更新"
    echo "  Metals API may rate-limit, use 'update' if shows --"
}

main() {
    local cmd="${1:-all}"
    shift || true
    
    case "$cmd" in
        all|a) cmd_all ;;
        update|up) cmd_update "$@" ;;
        refresh|r) rm -f /tmp/crypto-monitor/*.json && cmd_all ;;
        help|--help|-h|"") cmd_help ;;
        *) echo -e "${RED}未知命令: $cmd${NC}"; cmd_help; exit 1 ;;
    esac
}

main "$@"
