#!/bin/bash
# 记录消费脚本
# 用法: record.sh "用户输入" [用户ID]

INPUT="$1"
USER_ID="${2:-default}"
DATA_DIR="$HOME/.expense-tracker"
RECORDS_FILE="$DATA_DIR/records.jsonl"
CONFIG_FILE="$DATA_DIR/config.json"

# 创建数据目录
mkdir -p "$DATA_DIR"

# 初始化配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    cat > "$CONFIG_FILE" << 'EOF'
{
  "monthlyBudget": 5000,
  "categories": {
    "food": "餐饮",
    "transport": "交通",
    "shopping": "购物",
    "entertainment": "娱乐",
    "medical": "医疗",
    "education": "教育",
    "other": "其他"
  }
}
EOF
fi

# 初始化记录文件
if [ ! -f "$RECORDS_FILE" ]; then
    touch "$RECORDS_FILE"
fi

# 提取金额（支持各种格式）
# 匹配：35元、35.5、35.50元、￥35、35块钱等
AMOUNT=$(echo "$INPUT" | grep -oE '[0-9]+\.?[0-9]*' | head -1)

if [ -z "$AMOUNT" ]; then
    echo '{"error": "未识别到金额，请输入如：午饭35元"}'
    exit 1
fi

# 智能分类
classify() {
    local text="$1"
    local category="other"
    
    # 餐饮
    if echo "$text" | grep -qiE '早饭|午饭|晚饭|外卖|奶茶|咖啡|零食|水果|夜宵|餐厅|吃饭|食堂|面|饭|餐|炸鸡|火锅|烧烤|披萨|汉堡|饮料'; then
        category="food"
    # 交通
    elif echo "$text" | grep -qiE '打车|滴滴|地铁|公交|加油|停车|高铁|机票|出租|单车|骑车|开车|车费|路费'; then
        category="transport"
    # 购物
    elif echo "$text" | grep -qiE '超市|网购|淘宝|京东|拼多多|衣服|鞋|日用品|洗衣|护肤|化妆|口红|面膜'; then
        category="shopping"
    # 娱乐
    elif echo "$text" | grep -qiE '电影|游戏|KTV|演唱会|会员|视频|音乐|剧本杀|密室|游乐园'; then
        category="entertainment"
    # 医疗
    elif echo "$text" | grep -qiE '药|医院|看病|体检|牙|眼镜|挂号'; then
        category="medical"
    # 教育
    elif echo "$text" | grep -qiE '书|课|培训|考试|学习|教材|文具'; then
        category="education"
    fi
    
    echo "$category"
}

CATEGORY=$(classify "$INPUT")

# 生成记录 ID
RECORD_ID=$(date +%Y%m%d%H%M%S)_$(shuf -i 1000-9999 -n 1)

# 获取当前时间
TIMESTAMP=$(date -Iseconds)

# 提取备注（去除金额部分）
NOTE=$(echo "$INPUT" | sed "s/[0-9]\+\.?[0-9]*//g" | sed 's/元\|块\|￥\|¥//g' | sed 's/花了\|花费\|消费\|买了\|买了\|共计//g' | sed 's/^\s*//;s/\s*$//' | head -c 50)

# 如果备注为空，使用分类名
if [ -z "$NOTE" ]; then
    case "$CATEGORY" in
        food) NOTE="餐饮消费" ;;
        transport) NOTE="交通支出" ;;
        shopping) NOTE="购物消费" ;;
        entertainment) NOTE="娱乐消费" ;;
        medical) NOTE="医疗支出" ;;
        education) NOTE="教育支出" ;;
        *) NOTE="其他支出" ;;
    esac
fi

# 写入记录
cat >> "$RECORDS_FILE" << EOF
{"id":"$RECORD_ID","userId":"$USER_ID","amount":$AMOUNT,"category":"$CATEGORY","note":"$NOTE","time":"$TIMESTAMP"}
EOF

# 获取分类中文名
CATEGORY_CN=$(jq -r ".categories.$CATEGORY // \"$CATEGORY\"" "$CONFIG_FILE" 2>/dev/null || echo "$CATEGORY")

# 获取今日汇总
TODAY=$(date +%Y-%m-%d)
TODAY_TOTAL=$(grep "$TODAY" "$RECORDS_FILE" 2>/dev/null | jq -s '[.[].amount] | add // 0' 2>/dev/null || echo "0")

# 输出结果
cat << EOF
{"success":true,"record":{"id":"$RECORD_ID","amount":$AMOUNT,"category":"$CATEGORY","categoryName":"$CATEGORY_CN","note":"$NOTE"},"summary":{"todayTotal":$TODAY_TOTAL}}
EOF
