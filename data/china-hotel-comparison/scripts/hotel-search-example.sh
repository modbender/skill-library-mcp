#!/bin/bash
# 国内酒店搜索示例脚本
# 这个脚本展示了如何使用命令行工具进行多平台酒店搜索

# 配置参数
CITY="上海"
CHECKIN_DATE="2026-03-15"
CHECKOUT_DATE="2026-03-17"
ROOMS=1
ADULTS=2
CHILDREN=0
BUDGET_MIN=300
BUDGET_MAX=800

# 输出文件
OUTPUT_FILE="hotel_search_results_$(date +%Y%m%d_%H%M%S).md"

# 创建输出文件
echo "# 酒店搜索结果" > "$OUTPUT_FILE"
echo "**搜索时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "**搜索条件**: $CITY, $CHECKIN_DATE 至 $CHECKOUT_DATE, $ROOMS间房, $ADULTS成人$CHILDREN儿童" >> "$OUTPUT_FILE"
echo "**预算范围**: ¥$BUDGET_MIN - ¥$BUDGET_MAX/晚" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "开始搜索酒店..."
echo "城市: $CITY"
echo "日期: $CHECKIN_DATE 至 $CHECKOUT_DATE"
echo "预算: ¥$BUDGET_MIN - ¥$BUDGET_MAX/晚"
echo ""

# 模拟搜索函数
simulate_search() {
    local platform=$1
    local query=$2
    
    echo "正在搜索 $platform..."
    
    # 模拟搜索延迟
    sleep 1
    
    # 生成模拟结果
    case $platform in
        "携程")
            echo "找到 15 家符合条件的酒店"
            echo "推荐: 上海外滩华尔道夫酒店 ¥750/晚"
            echo "      上海浦东香格里拉大酒店 ¥680/晚"
            echo "      上海静安昆仑大酒店 ¥550/晚"
            ;;
        "去哪儿")
            echo "找到 18 家符合条件的酒店"
            echo "推荐: 上海外滩茂悦大酒店 ¥720/晚"
            echo "      上海金茂君悦大酒店 ¥650/晚"
            echo "      上海新天地朗廷酒店 ¥530/晚"
            ;;
        "美团")
            echo "找到 12 家符合条件的酒店"
            echo "推荐: 上海外滩W酒店 ¥780/晚 (含¥50优惠券)"
            echo "      上海和平饭店 ¥700/晚 (本地人专享价)"
            echo "      上海锦江都城酒店 ¥480/晚"
            ;;
        "飞猪")
            echo "找到 10 家符合条件的酒店"
            echo "推荐: 上海迪士尼乐园酒店 ¥850/晚 (信用住)"
            echo "      上海苏宁环球万怡酒店 ¥600/晚 (F3会员价)"
            echo "      上海中星君亭酒店 ¥450/晚"
            ;;
        "途牛")
            echo "找到 8 家符合条件的酒店"
            echo "推荐: 上海佘山世茂洲际酒店 ¥1200/晚 (深坑酒店)"
            echo "      上海朱家角安麓酒店 ¥980/晚 (度假套餐)"
            echo "      上海崇明金茂凯悦酒店 ¥580/晚"
            ;;
    esac
    echo ""
}

# 执行各平台搜索
echo "## 各平台搜索结果" >> "$OUTPUT_FILE"

PLATFORMS=("携程" "去哪儿" "美团" "飞猪" "途牛")
for platform in "${PLATFORMS[@]}"; do
    echo "### $platform" >> "$OUTPUT_FILE"
    
    # 模拟搜索并捕获输出
    {
        echo "#### 搜索概况"
        simulate_search "$platform" "$CITY $CHECKIN_DATE"
        echo ""
        echo "#### 推荐酒店"
        case $platform in
            "携程")
                echo "1. **上海外滩华尔道夫酒店**"
                echo "   - 价格: ¥750/晚 (总价: ¥1,500)"
                echo "   - 评分: 4.8/5 (2,345条评价)"
                echo "   - 优势: 免费取消、含双早、历史建筑"
                echo "   - 位置: 外滩核心区，步行至南京路5分钟"
                echo ""
                echo "2. **上海浦东香格里拉大酒店**"
                echo "   - 价格: ¥680/晚 (总价: ¥1,360)"
                echo "   - 评分: 4.7/5 (1,890条评价)"
                echo "   - 优势: 江景房、行政酒廊、健身中心"
                echo "   - 位置: 陆家嘴金融区，东方明珠旁"
                echo ""
                echo "3. **上海静安昆仑大酒店**"
                echo "   - 价格: ¥550/晚 (总价: ¥1,100)"
                echo "   - 评分: 4.5/5 (1,234条评价)"
                echo "   - 优势: 性价比高、交通便利、服务好"
                echo "   - 位置: 静安寺商圈，地铁2/7号线交汇"
                ;;
            "去哪儿")
                echo "1. **上海外滩茂悦大酒店**"
                echo "   - 价格: ¥720/晚 (总价: ¥1,440)"
                echo "   - 评分: 4.6/5 (1,567条评价)"
                echo "   - 优势: 价格最低、江景绝佳、网红酒吧"
                echo "   - 位置: 北外滩，相对安静"
                echo ""
                echo "2. **上海金茂君悦大酒店**"
                echo "   - 价格: ¥650/晚 (总价: ¥1,300)"
                echo "   - 评分: 4.7/5 (1,890条评价)"
                echo "   - 优势: 54层以上高空酒店、云端体验"
                echo "   - 位置: 金茂大厦内，陆家嘴核心"
                echo ""
                echo "3. **上海新天地朗廷酒店**"
                echo "   - 价格: ¥530/晚 (总价: ¥1,060)"
                echo "   - 评分: 4.5/5 (1,123条评价)"
                echo "   - 优势: 英伦风格、下午茶出名、位置优越"
                echo "   - 位置: 新天地商圈，石库门建筑群"
                ;;
            "美团")
                echo "1. **上海外滩W酒店**"
                echo "   - 价格: ¥780/晚 (总价: ¥1,560，使用优惠券后¥1,510)"
                echo "   - 评分: 4.8/5 (2,100条评价)"
                echo "   - 优势: 时尚设计、潮人聚集、夜景超棒"
                echo "   - 位置: 北外滩，白玉兰广场"
                echo ""
                echo "2. **上海和平饭店**"
                echo "   - 价格: ¥700/晚 (总价: ¥1,400，本地人专享价)"
                echo "   - 评分: 4.9/5 (3,456条评价)"
                echo "   - 优势: 历史地标、爵士酒吧、文物建筑"
                echo "   - 位置: 外滩20号，南京东路路口"
                echo ""
                echo "3. **上海锦江都城酒店**"
                echo "   - 价格: ¥480/晚 (总价: ¥960)"
                echo "   - 评分: 4.3/5 (890条评价)"
                echo "   - 优势: 经济实惠、老牌国企、品质稳定"
                echo "   - 位置: 南京西路，多条地铁线交汇"
                ;;
            "飞猪")
                echo "1. **上海迪士尼乐园酒店**"
                echo "   - 价格: ¥850/晚 (总价: ¥1,700，信用住免押金)"
                echo "   - 评分: 4.7/5 (3,210条评价)"
                echo "   - 优势: 迪士尼主题、提前入园、角色互动"
                echo "   - 位置: 迪士尼度假区内"
                echo ""
                echo "2. **上海苏宁环球万怡酒店**"
                echo "   - 价格: ¥600/晚 (总价: ¥1,200，F3会员价)"
                echo "   - 评分: 4.4/5 (1,100条评价)"
                echo "   - 优势: 万豪旗下、商务设施齐全、积分累积"
                echo "   - 位置: 普陀区，近长风公园"
                echo ""
                echo "3. **上海中星君亭酒店**"
                echo "   - 价格: ¥450/晚 (总价: ¥900)"
                echo "   - 评分: 4.2/5 (780条评价)"
                echo "   - 优势: 设计酒店、小而精、服务贴心"
                echo "   - 位置: 浦东新区，近世纪公园"
                ;;
            "途牛")
                echo "1. **上海佘山世茂洲际酒店**"
                echo "   - 价格: ¥1200/晚 (总价: ¥2,400，深坑酒店体验)"
                echo "   - 评分: 4.9/5 (4,500条评价)"
                echo "   - 优势: 世界建筑奇迹、水下餐厅、悬崖景观"
                echo "   - 位置: 松江佘山，需驾车前往"
                echo ""
                echo "2. **上海朱家角安麓酒店**"
                echo "   - 价格: ¥980/晚 (总价: ¥1,960，古镇度假套餐)"
                echo "   - 评分: 4.8/5 (1,200条评价)"
                echo "   - 优势: 明清建筑、私人管家、禅意体验"
                echo "   - 位置: 青浦朱家角古镇"
                echo ""
                echo "3. **上海崇明金茂凯悦酒店**"
                echo "   - 价格: ¥580/晚 (总价: ¥1,160)"
                echo "   - 评分: 4.5/5 (950条评价)"
                echo "   - 优势: 生态度假、亲子设施、农家乐体验"
                echo "   - 位置: 崇明岛，适合自驾游"
                ;;
        esac
    } >> "$OUTPUT_FILE"
    
    echo "" >> "$OUTPUT_FILE"
done

# 价格对比分析
echo "## 价格对比分析" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### 同级别酒店跨平台价格对比" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| 酒店类型 | 携程 | 去哪儿 | 美团 | 飞猪 | 途牛 | 最低价平台 |" >> "$OUTPUT_FILE"
echo "|----------|------|--------|------|------|------|------------|" >> "$OUTPUT_FILE"
echo "| 奢华酒店 | ¥750 | ¥720 | ¥780 | ¥850 | ¥1200 | 去哪儿(¥720) |" >> "$OUTPUT_FILE"
echo "| 高端酒店 | ¥680 | ¥650 | ¥700 | ¥600 | ¥980 | 飞猪(¥600) |" >> "$OUTPUT_FILE"
echo "| 中端酒店 | ¥550 | ¥530 | ¥480 | ¥450 | ¥580 | 飞猪(¥450) |" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 平台特点总结" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **携程**：酒店选择最全，商务酒店专业，价格中等偏上" >> "$OUTPUT_FILE"
echo "2. **去哪儿**：比价功能强，价格通常有优势，适合价格敏感用户" >> "$OUTPUT_FILE"
echo "3. **美团**：本地优惠多，新用户优惠大，适合经济型选择" >> "$OUTPUT_FILE"
echo "4. **飞猪**：阿里生态整合，信用住方便，会员权益有价值" >> "$OUTPUT_FILE"
echo "5. **途牛**：度假套餐专业，特色酒店丰富，适合旅游度假" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 推荐建议
echo "## 综合推荐" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "### 按需求推荐" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**商务出行推荐**：" >> "$OUTPUT_FILE"
echo "- 首选：携程 - 上海浦东香格里拉大酒店 (¥680/晚)" >> "$OUTPUT_FILE"
echo "- 理由：商务设施齐全，位置优越，服务专业" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**旅游观光推荐**：" >> "$OUTPUT_FILE"
echo "- 首选：去哪儿 - 上海外滩茂悦大酒店 (¥720/晚)" >> "$OUTPUT_FILE"
echo "- 理由：江景绝佳，价格有优势，交通便利" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**性价比推荐**：" >> "$OUTPUT_FILE"
echo "- 首选：飞猪 - 上海中星君亭酒店 (¥450/晚)" >> "$OUTPUT_FILE"
echo "- 理由：价格最低，设计感强，服务好评" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**特色体验推荐**：" >> "$OUTPUT_FILE"
echo "- 首选：途牛 - 上海佘山世茂洲际酒店 (¥1200/晚)" >> "$OUTPUT_FILE"
echo "- 理由：世界级建筑奇迹，独特体验，值得一试" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 预订建议
echo "### 预订建议" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "1. **提前预订**：建议提前7-14天预订，价格更优惠" >> "$OUTPUT_FILE"
echo "2. **取消政策**：优先选择免费取消的订单，避免行程变动损失" >> "$OUTPUT_FILE"
echo "3. **支付方式**：建议使用平台担保交易，避免直接转账" >> "$OUTPUT_FILE"
echo "4. **评价参考**：务必查看最新用户评价，特别是带图片的评价" >> "$OUTPUT_FILE"
echo "5. **位置验证**：使用地图软件验证酒店实际位置和交通情况" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "搜索完成！结果已保存到: $OUTPUT_FILE"
echo ""
echo "你可以使用以下命令查看结果："
echo "cat $OUTPUT_FILE | less"
echo ""
echo "或者直接在编辑器中打开："
echo "code $OUTPUT_FILE"
echo ""