#!/bin/bash
# 每日天气推送 - 每天早上8点
# 使用 OpenClaw 消息接口发送

# 设置 PATH
export PATH=/usr/local/bin:/usr/bin:/bin:$HOME/.npm-global/bin

# 深圳坐标
LAT_LG=22.75
LON_LG=114.25
LAT_FT=22.54
LON_FT=114.06

# 天气代码转中文
get_weather_cond() {
    case $1 in
        0) echo "晴天" ;;
        1) echo "晴时多云" ;;
        2) echo "多云" ;;
        3) echo "阴天" ;;
        45|48) echo "雾" ;;
        51|53|55) echo "小雨" ;;
        56|57) echo "冻雨" ;;
        61|63|65) echo "雨" ;;
        66|67) echo "雨夹雪" ;;
        71|73|75) echo "雪" ;;
        77) echo "雪粒" ;;
        80|81|82) echo "阵雨" ;;
        85|86) echo "阵雪" ;;
        95|96|99) echo "雷暴" ;;
        *) echo "多云" ;;
    esac
}

# 用 Python 解析 JSON 更可靠
parse_weather_json() {
    LAT=$1
    LON=$2
    DATA=$(curl -s --max-time 10 "https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Asia/Shanghai&past_days=2" 2>/dev/null)
    
    python3 - << PYEOF
import json, sys, subprocess
try:
    d = json.loads('''$DATA''')
    times = d['daily']['time']
    maxes = d['daily']['temperature_2m_max']
    mins = d['daily']['temperature_2m_min']
    
    # 找昨天和今天
    import datetime
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    today_idx = times.index(today) if today in times else 2
    yest_idx = times.index(yesterday) if yesterday in times else 1
    
    print(f"{maxes[today_idx]}|{mins[today_idx]}|{maxes[yest_idx]}|{mins[yest_idx]}")
except:
    print("0|0|0|0")
PYEOF
}

# 解析龙岗
READ_LG=$(parse_weather_json $LAT_LG $LON_LG)
TODAY_MAX_LG=$(echo "$READ_LG" | cut -d'|' -f1)
TODAY_MIN_LG=$(echo "$READ_LG" | cut -d'|' -f2)
YEST_MAX_LG=$(echo "$READ_LG" | cut -d'|' -f3)
YEST_MIN_LG=$(echo "$READ_LG" | cut -d'|' -f4)

# 获取龙岗天气代码
CODE_LG=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT_LG&longitude=$LON_LG&current=weather_code&timezone=Asia/Shanghai" 2>/dev/null | grep -oP '"weather_code":\K[0-9]+')
COND_LG=$(get_weather_cond $CODE_LG)

# 解析福田
READ_FT=$(parse_weather_json $LAT_FT $LON_FT)
TODAY_MAX_FT=$(echo "$READ_FT" | cut -d'|' -f1)
TODAY_MIN_FT=$(echo "$READ_FT" | cut -d'|' -f2)
YEST_MAX_FT=$(echo "$READ_FT" | cut -d'|' -f3)
YEST_MIN_FT=$(echo "$READ_FT" | cut -d'|' -f4)

# 获取福田天气代码
CODE_FT=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=$LAT_FT&longitude=$LON_FT&current=weather_code&timezone=Asia/Shanghai" 2>/dev/null | grep -oP '"weather_code":\K[0-9]+')
COND_FT=$(get_weather_cond $CODE_FT)

# 计算温差
calc_diff() {
    DIFF=$(echo "$1 - $2" | bc 2>/dev/null)
    if [ "$DIFF" = "" ] || [ "$DIFF" = "0" ]; then
        echo "和昨天一样"
    elif (( $(echo "$DIFF > 0" | bc -l) )); then
        echo "比昨天热了${DIFF}°C"
    else
        echo "比昨天冷了${DIFF#-}°C"
    fi
}

DIFF_MAX_LG=$(calc_diff $TODAY_MAX_LG $YEST_MAX_LG)
DIFF_MIN_LG=$(calc_diff $TODAY_MIN_LG $YEST_MIN_LG)
DIFF_MAX_FT=$(calc_diff $TODAY_MAX_FT $YEST_MAX_FT)
DIFF_MIN_FT=$(calc_diff $TODAY_MIN_FT $YEST_MIN_FT)

# 日期
TODAY_DISPLAY=$(date +"%Y年%m月%d日")
WEEKDAY=$(date +%u)
case $WEEKDAY in
    1) WEEKDAY_NAME="周一" ;;
    2) WEEKDAY_NAME="周二" ;;
    3) WEEKDAY_NAME="周三" ;;
    4) WEEKDAY_NAME="周四" ;;
    5) WEEKDAY_NAME="周五" ;;
    6) WEEKDAY_NAME="周六" ;;
    7) WEEKDAY_NAME="周日" ;;
esac

# 农历（用本地 Python 库）
LUNAR=$(python3 - << 'PYEOF'
from lunarcalendar import Converter, Solar
import datetime
today = Solar(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
lunar = Converter.Solar2Lunar(today)
months = ['', '正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '冬月', '腊月']
days = ['', '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
        '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
        '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
month_str = months[lunar.month] if lunar.month <= 12 else f'{lunar.month}月'
if lunar.isleap:
    month_str = f'闰{month_str}'
day_str = days[lunar.day]
print(f'{month_str}{day_str}')
PYEOF
)

# 系统状态（远程检测 MiHoMo 服务器）
MIHOMO_STATUS=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no sulada2@10.144.1.3 "systemctl is-active mihomo 2>/dev/null" 2>/dev/null || echo "unknown")
if [ "$MIHOMO_STATUS" = "active" ]; then
    MIHOMO_STATUS_STR="✅ mihomo服务: active"
else
    MIHOMO_STATUS_STR="❌ mihomo服务: $MIHOMO_STATUS"
fi

# 日志检测（检测进程是否运行）
LOG_CHECK=$(ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no sulada2@10.144.1.3 "pgrep -f 'mihomo.*-d' >/dev/null && echo '运行状态正常'" 2>/dev/null)
if [ -n "$LOG_CHECK" ]; then
    LOG_STATUS_STR="✅ 日志检测: 运行状态正常"
else
    LOG_STATUS_STR="❌ 日志检测: 进程异常"
fi

# 构建消息
MESSAGE="**洪楷，早上好！**

【深圳龙岗天气】
今日概况: ${COND_LG}
温度范围: ${TODAY_MIN_LG}°C ~ ${TODAY_MAX_LG}°C

【深圳福田天气】
今日概况: ${COND_FT}
温度范围: ${TODAY_MIN_FT}°C ~ ${TODAY_MAX_FT}°C

【与昨日天气对比】
龙岗 - 最高温: ${DIFF_MAX_LG}, 最低温: ${DIFF_MIN_LG}
福田 - 最高温: ${DIFF_MAX_FT}, 最低温: ${DIFF_MIN_FT}

【系统服务状态】
${MIHOMO_STATUS_STR}
${LOG_STATUS_STR}

【温馨提示】
今天是 ${TODAY_DISPLAY} ${WEEKDAY_NAME}
农历 ${LUNAR}
祝您今天工作顺利！"

# 发送
/home/aisulada/.npm-global/bin/openclaw message send \
    --channel feishu \
    --target "ou_b07b92c096b2f0f7260a2ee106241605" \
    --message "$MESSAGE" >> /tmp/weather-push.log 2>&1

echo "$(date): 推送完成" >> /tmp/weather-push.log
