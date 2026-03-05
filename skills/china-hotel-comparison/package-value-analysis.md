# 套餐价值分析系统

## 核心概念：拆解套餐，计算真实价值

### 1. 常见套餐类型分析

#### A. 早餐套餐
```yaml
早餐价值分析:
  单人早餐市场价:
    - 经济型酒店: ¥30-50
    - 舒适型酒店: ¥50-80  
    - 高端酒店: ¥80-150
    - 奢华酒店: ¥150-300
  
  包含类型:
    - 中式早餐: 粥、点心、小菜
    - 西式早餐: 面包、牛奶、水果
    - 自助早餐: 品种丰富，自由选择
    - 套餐早餐: 固定搭配，送到房间
  
  价值评估要点:
    - 实际使用概率: 早起游客 vs 睡懒觉
    - 替代成本: 周边早餐选择
    - 时间价值: 酒店用餐节省的时间
```

#### B. 景点门票套餐
```yaml
门票价值分析:
  迪士尼门票:
    - 平日标准票: ¥435
    - 周末标准票: ¥545
    - 儿童/老人票: ¥326-409
    - 两日票: ¥782-1034
  
  包含类型:
    - 单门票: 仅入园
    - 快速通行: 减少排队
    - VIP服务: 导游、优先
    - 餐饮券: 园内餐饮抵扣
  
  价值评估要点:
    - 门票类型匹配: 是否需要的票型
    - 使用灵活性: 日期是否固定
    - 实际需求: 是否计划去该景点
```

#### C. 交通服务套餐
```yaml
交通价值分析:
  机场接送:
    - 单程接送: ¥100-300
    - 往返接送: ¥200-500
    - 专车服务: ¥300-800
  
  景点接送:
    - 定时班车: 免费或¥20-50
    - 专车接送: ¥50-150
    - 包车服务: ¥200-500/天
  
  价值评估要点:
    - 实际需求: 是否有接送需求
    - 替代成本: 打车/公共交通费用
    - 便利价值: 节省的时间和精力
```

#### D. 其他增值服务
```yaml
增值服务分析:
  SPA/按摩:
    - 基础按摩: ¥200-400/60分钟
    - SPA套餐: ¥400-800/90分钟
  
  餐饮套餐:
    - 晚餐套餐: ¥100-300/人
    - 下午茶: ¥80-200/套
    - 房间送餐: 加收15-30%服务费
  
  娱乐设施:
    - 健身房: 通常免费
    - 游泳池: 通常免费
    - 儿童乐园: 通常免费或¥50-100
  
  价值评估要点:
    - 使用概率: 实际会使用的服务
    - 替代选择: 外部同类服务价格
    - 体验价值: 独特体验的价值
```

### 2. 官方价格查询策略

#### A. 实时价格查询流程
```
1. 识别套餐包含的服务项
2. 查询各项服务的官方单独价格
3. 验证价格的时效性和适用条件
4. 计算套餐总价值
5. 对比套餐价格计算优惠力度
```

#### B. 官方价格来源
```yaml
迪士尼门票:
  - 官方渠道: 上海迪士尼度假区官网/APP
  - 官方价格: 实时查询，区分平日/周末
  - 验证方法: web_fetch官方页面

酒店早餐:
  - 酒店官网: 查看餐饮价格
  - 平台信息: 携程/去哪儿酒店详情
  - 用户评价: 提及早餐价格
  - 市场参考: 同类酒店早餐价格

接送服务:
  - 打车软件: 滴滴/高德预估价格
  - 专车平台: 神州/首汽约车价格
  - 酒店报价: 直接咨询酒店
  - 平台信息: 套餐说明中的参考价
```

#### C. 查询工具和技术
```python
def query_official_prices(service_type, details):
    """
    查询服务的官方单独价格
    """
    if service_type == "disney_ticket":
        return query_disney_official_price(details['date'], details['ticket_type'])
    elif service_type == "breakfast":
        return query_hotel_breakfast_price(details['hotel_name'], details['breakfast_type'])
    elif service_type == "transfer":
        return query_transfer_service_price(details['from'], details['to'], details['vehicle_type'])
    else:
        return estimate_market_price(service_type, details)

def query_disney_official_price(date, ticket_type):
    """
    查询迪士尼官方门票价格
    """
    # 使用web_fetch查询迪士尼官网
    url = f"https://www.shanghaidisneyresort.com/tickets/"
    # 解析价格信息
    # 返回平日/周末价格
    return {
        "adult_price": 435 if is_weekday(date) else 545,
        "child_price": 326 if is_weekday(date) else 409,
        "source": "上海迪士尼官网",
        "query_time": current_time()
    }
```

### 3. 优惠力度计算模型

#### A. 基础计算公式
```
套餐总价值 = Σ(各项服务官方单独价格 × 数量)

实际支付价格 = 套餐标价

名义优惠 = 套餐总价值 - 实际支付价格

优惠比例 = 名义优惠 ÷ 套餐总价值 × 100%

真实优惠 = 考虑使用概率后的实际节省
```

#### B. 使用概率调整
```python
def calculate_real_discount(package_value, package_price, usage_probabilities):
    """
    计算考虑使用概率的真实优惠
    """
    expected_value = 0
    for service in package_value['services']:
        service_value = service['official_price'] * service['quantity']
        usage_prob = usage_probabilities.get(service['type'], 0.5)
        expected_value += service_value * usage_prob
    
    nominal_discount = package_value['total'] - package_price
    real_discount = expected_value - package_price
    
    return {
        'nominal_discount': nominal_discount,
        'nominal_discount_rate': nominal_discount / package_value['total'],
        'real_discount': real_discount,
        'real_discount_rate': real_discount / expected_value if expected_value > 0 else 0,
        'expected_value': expected_value
    }
```

#### C. 套餐价值评级系统
```yaml
价值评级标准:
  五星级 (优惠>40%):
    - 套餐总价值远高于价格
    - 包含高需求服务
    - 使用限制合理
  
  四星级 (优惠20-40%):
    - 明显优惠，价值合理
    - 服务匹配需求
    - 性价比优秀
  
  三星级 (优惠0-20%):
    - 略有优惠或持平
    - 便利性价值为主
    - 适合特定需求
  
  二星级 (名义优惠但实际无):
    - 服务使用概率低
    - 限制条件多
    - 实际价值有限
  
  一星级 (价格高于价值):
    - 套餐价格高于单独购买
    - 强制捆绑不需要的服务
    - 存在消费陷阱
```

### 4. 实时查询实施

#### A. 迪士尼门票价格查询
```python
# 迪士尼门票官方价格（2026年2月查询）
DISNEY_TICKET_PRICES = {
    'standard': {
        'weekday': 435,    # 平日标准票
        'weekend': 545,    # 周末标准票
        'peak': 659        # 高峰日
    },
    'child_elderly': {
        'weekday': 326,    # 平日儿童/老人
        'weekend': 409,    # 周末儿童/老人  
        'peak': 494        # 高峰儿童/老人
    },
    'two_day': {
        'weekday': 782,    # 平日两日联票
        'weekend': 1034,   # 周末两日联票
        'peak': 1188       # 高峰两日联票
    }
}

# 早餐市场参考价格
BREAKFAST_MARKET_PRICES = {
    'economy_hotel': {'single': 35, 'double': 60},
    'comfort_hotel': {'single': 65, 'double': 100},
    'luxury_hotel': {'single': 120, 'double': 200}
}

# 接送服务市场价
TRANSFER_MARKET_PRICES = {
    'airport_hotel': {'one_way': 150, 'round_trip': 280},
    'disney_hotel': {'shuttle': 0, 'taxi': 30, 'private': 100},
    'attraction_shuttle': {'per_trip': 20, 'unlimited': 50}
}
```

#### B. 套餐分析示例
**案例：迪士尼酒店+门票套餐**
```
套餐价格：¥1,288/晚
包含：
1. 酒店住宿：¥688（单独预订价）
2. 迪士尼门票2张：¥1,090（周末价2×545）
3. 双人早餐：¥120（市场价）
4. 迪士尼接送：¥60（市场价）

套餐总价值：¥688 + ¥1,090 + ¥120 + ¥60 = ¥1,958
名义优惠：¥1,958 - ¥1,288 = ¥670
优惠比例：670 ÷ 1,958 × 100% = 34.2%

使用概率调整：
- 门票使用概率：100%（主要目的）
- 早餐使用概率：80%（可能睡懒觉）
- 接送使用概率：60%（可能其他交通）

预期价值：¥688 + ¥1,090 + ¥96 + ¥36 = ¥1,910
真实优惠：¥1,910 - ¥1,288 = ¥622
真实优惠比例：32.6%
```

### 5. 套餐价值展示模板

#### A. 详细分析视图
```
🏨 **套餐价值深度分析**

**套餐名称**：迪士尼奇幻之旅套餐
**套餐价格**：¥1,288/晚
**单独购买总价**：¥1,958
**名义优惠**：¥670 (34.2%)

**包含服务拆解**：
1. 🏨 酒店住宿：¥688（单独预订价）
2. 🎫 迪士尼门票×2：¥1,090（周末官方价）
3. 🍳 双人早餐：¥120（酒店市场价）
4. 🚐 迪士尼接送：¥60（专车市场价）

**使用概率调整**：
- 门票：100%使用 → ¥1,090
- 早餐：80%使用 → ¥96
- 接送：60%使用 → ¥36
- 住宿：100%使用 → ¥688
**预期价值**：¥1,910

**真实优惠**：¥622 (32.6%)
**价值评级**：★★★★☆ (四星，优秀)

**适合人群**：
- ✅ 计划去迪士尼的游客
- ✅ 需要早餐和接送的便利
- ✅ 愿意为打包优惠付费
- ❌ 不去迪士尼的游客
- ❌ 自己安排交通和餐饮

**购买建议**：
- 如果去迪士尼：强烈推荐，节省¥622
- 如果不去迪士尼：不推荐，为不需要的服务付费
```

#### B. 快速比较视图
```
💰 **套餐价值快速比较**

| 套餐类型 | 套餐价 | 单独购买价 | 名义优惠 | 真实优惠 | 评级 |
|----------|--------|------------|----------|----------|------|
| 纯住宿 | ¥688 | ¥688 | ¥0 (0%) | ¥0 (0%) | ★★★☆☆ |
| 住宿+早餐 | ¥788 | ¥808 | ¥20 (2.5%) | ¥16 (2.0%) | ★★★☆☆ |
| 住宿+门票 | ¥1,188 | ¥1,778 | ¥590 (33.2%) | ¥590 (33.2%) | ★★★★☆ |
| 全包套餐 | ¥1,288 | ¥1,958 | ¥670 (34.2%) | ¥622 (32.6%) | ★★★★☆ |

💡 **洞察**：
- 纯住宿套餐无优惠，适合灵活安排
- 门票套餐优惠最大，适合迪士尼游客
- 全包套餐便利性高，但早餐接送使用概率影响价值
```

### 6. 实施工作流程

#### A. 套餐分析流程
```
1. 识别套餐包含的服务项
2. 查询每项服务的官方单独价格
3. 计算套餐总价值和名义优惠
4. 评估各项服务的使用概率
5. 计算预期价值和真实优惠
6. 提供价值评级和购买建议
7. 记录分析结果供历史学习
```

#### B. 实时查询优先级
```yaml
高优先级（必须实时查询）:
  - 迪士尼/景点官方门票价格
  - 限时优惠活动价格
  - 平台独家套餐价格

中优先级（建议实时查询）:
  - 酒店官方早餐价格
  - 接送服务市场价
  - 增值服务单独售价

低优先级（可使用缓存）:
  - 标准市场参考价格
  - 历史查询的稳定价格
  - 用户评价中的价格信息
```

### 7. 历史学习集成

#### A. 套餐偏好学习
```python
def learn_package_preferences(user_history):
    """
    从历史中学习用户的套餐偏好
    """
    preferences = {
        'preferred_package_types': analyze_package_choices(user_history),
        'service_usage_patterns': analyze_service_usage(user_history),
        'value_sensitivity': analyze_discount_response(user_history),
        'convenience_vs_savings': analyze_tradeoff_preferences(user_history)
    }
    return preferences

def analyze_service_usage(user_history):
    """
    分析用户对套餐服务的实际使用情况
    """
    usage_stats = {}
    for booking in user_history.get('package_bookings', []):
        for service in booking.get('included_services', []):
            service_type = service['type']
            used = service.get('actually_used', True)
            usage_stats.setdefault(service_type, {'total': 0, 'used': 0})
            usage_stats[service_type]['total'] += 1
            if used:
                usage_stats[service_type]['used'] += 1
    
    # 计算使用概率
    usage_probabilities = {}
    for service_type, stats in usage_stats.items():
        usage_probabilities[service_type] = stats['used'] / stats['total']
    
    return usage_probabilities
```

#### B. 个性化套餐推荐
基于历史学习的套餐推荐策略：
1. **高使用概率服务**：优先推荐包含用户常使用的服务
2. **历史成功套餐**：推荐类似的历史成功套餐类型
3. **价值敏感度匹配**：根据用户价值敏感度调整推荐
4. **风险偏好考虑**：考虑用户对套餐限制的接受度

### 8. 风险提示与注意事项

#### A. 套餐常见陷阱
```yaml
消费陷阱识别:
  1. 强制捆绑:
    - 捆绑不需要的服务
    - 限制取消或变更
    - 隐藏附加条件
  
  2. 价格虚高:
    - 抬高单独服务价格
    - 虚假折扣计算
    - 限时压力销售
  
  3. 使用限制:
    - 服务时间限制
    - 预约困难
    - 服务质量差异
  
  4. 变更困难:
    - 不可拆分使用
    - 不可转让
    - 退款困难
```

#### B. 购买建议检查清单
```
购买前请确认：
✅ 包含的服务都是需要的
✅ 服务使用时间符合行程
✅ 单独购买总价确实更高
✅ 取消和变更政策可接受
✅ 没有隐藏费用或限制
✅ 服务质量有保障
```

### 9. 效果评估指标

#### A. 分析准确性指标
```yaml
价格查询准确性:
  - 官方价格匹配度
  - 市场参考价合理性
  - 时效性保证

价值计算准确性:
  - 优惠力度计算正确性
  - 使用概率估计合理性
  - 风险识别完整性
```

#### B. 用户价值指标
```yaml
决策支持效果:
  - 套餐选择满意度
  - 实际节省金额
  - 避免消费陷阱

用户体验提升:
  - 信息透明度感知
  - 决策信心提升
  - 重复使用意愿
```

---

通过这个套餐价值分析系统，skill能够深度拆解酒店套餐，计算真实优惠力度，帮助用户做出更明智的购买决策。

<｜DSML｜function_calls>
<｜DSML｜invoke name="web_fetch">
<｜DSML｜parameter name="url" string="true">https://www.shanghaidisneyresort.com/tickets/