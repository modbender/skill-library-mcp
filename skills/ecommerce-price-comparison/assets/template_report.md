# 电商价格比较报告

**报告生成时间**: {{timestamp}}  
**查询商品**: {{product_name}}  
**搜索关键词**: {{search_keyword}}

---

## 执行摘要

**最佳选择**: {{best_choice.platform}}  
**推荐价格**: ¥{{best_choice.price}}  
**节省金额**: ¥{{savings}} (相比最高价)  
**综合评分**: {{best_choice.score}}/100

**购买建议**: {{best_choice.recommendation}}

---

## 平台对比详情

### 价格对比表

| 平台 | 价格 | 优惠后价 | 运费 | 总成本 | 评分 | 店铺 | 推荐等级 |
|------|------|----------|------|--------|------|------|----------|
{% for item in results %}
| {{item.platform}} | ¥{{item.price}} | ¥{{item.discounted_price}} | ¥{{item.shipping}} | ¥{{item.total_cost}} | {{item.rating}} | {{item.shop}} | {{item.recommendation_level}} |
{% endfor %}

### 价格趋势图

```
价格对比图（从低到高）：
拼多多  ████████████████████████ ¥5499
淘宝    ████████████████████ ¥5699
天猫    ██████████████████ ¥5799
京东    ████████████████ ¥5999
```

---

## 详细分析

### 1. 京东分析
- **价格**: ¥{{jd.price}}
- **优势**: {{jd.advantages}}
- **劣势**: {{jd.disadvantages}}
- **适合人群**: {{jd.target_audience}}

### 2. 淘宝分析
- **价格**: ¥{{taobao.price}}
- **优势**: {{taobao.advantages}}
- **劣势**: {{taobao.disadvantages}}
- **适合人群**: {{taobao.target_audience}}

### 3. 天猫分析
- **价格**: ¥{{tmall.price}}
- **优势**: {{tmall.advantages}}
- **劣势**: {{tmall.disadvantages}}
- **适合人群**: {{tmall.target_audience}}

### 4. 拼多多分析
- **价格**: ¥{{pdd.price}}
- **优势**: {{pdd.advantages}}
- **劣势**: {{pdd.disadvantages}}
- **适合人群**: {{pdd.target_audience}}

---

## 维度评分

### 各平台维度得分

| 维度 | 京东 | 淘宝 | 天猫 | 拼多多 | 权重 |
|------|------|------|------|--------|------|
| 价格 | {{jd.price_score}} | {{taobao.price_score}} | {{tmall.price_score}} | {{pdd.price_score}} | 40% |
| 成本 | {{jd.cost_score}} | {{taobao.cost_score}} | {{tmall.cost_score}} | {{pdd.cost_score}} | 20% |
| 信誉 | {{jd.reputation_score}} | {{taobao.reputation_score}} | {{tmall.reputation_score}} | {{pdd.reputation_score}} | 25% |
| 服务 | {{jd.service_score}} | {{taobao.service_score}} | {{tmall.service_score}} | {{pdd.service_score}} | 15% |
| **综合** | **{{jd.total_score}}** | **{{taobao.total_score}}** | **{{tmall.total_score}}** | **{{pdd.total_score}}** | **100%** |

### 评分说明
- **90-100分**: 优秀，强烈推荐
- **80-89分**: 良好，推荐购买
- **70-79分**: 中等，可考虑
- **60-69分**: 一般，需要谨慎
- **低于60分**: 不推荐

---

## 购买建议

### 按需求推荐

#### 追求性价比
**推荐平台**: {{best_for_value.platform}}  
**理由**: {{best_for_value.reason}}  
**预计节省**: ¥{{best_for_value.savings}}

#### 追求正品保障
**推荐平台**: {{best_for_authenticity.platform}}  
**理由**: {{best_for_authenticity.reason}}  
**额外保障**: {{best_for_authenticity.guarantee}}

#### 追求快速收货
**推荐平台**: {{best_for_speed.platform}}  
**理由**: {{best_for_speed.reason}}  
**预计到货**: {{best_for_speed.delivery_time}}

#### 追求售后服务
**推荐平台**: {{best_for_service.platform}}  
**理由**: {{best_for_service.reason}}  
**服务特点**: {{best_for_service.service_features}}

---

## 风险提示

### 注意事项
1. **价格波动**: 电商价格变化频繁，本报告价格仅供参考
2. **库存状态**: 低价商品可能库存有限或需要抢购
3. **地区差异**: 价格和运费可能因收货地区不同而变化
4. **账号差异**: 不同账号可能享受不同优惠（如会员价）

### 防骗提醒
1. **异常低价**: 价格远低于市场价需谨慎，可能是翻新机或假货
2. **新店铺**: 评价数量过少的新店铺需要更多验证
3. **支付安全**: 建议使用平台担保交易，避免直接转账

---

## 历史价格趋势

### 近期价格变化
```
近30天价格趋势：
京东:  5999 → 5899 → 5999 (平稳)
淘宝:  5799 → 5699 → 5699 (小幅下降)
天猫:  5899 → 5799 → 5799 (小幅下降)
拼多多: 5599 → 5499 → 5499 (下降)
```

### 购买时机建议
- **当前时机**: {{timing_advice.current}}
- **未来预测**: {{timing_advice.future}}
- **最佳购买时间**: {{timing_advice.best_time}}

---

## 数据来源与更新

### 数据抓取时间
- 京东: {{data_times.jd}}
- 淘宝: {{data_times.taobao}}
- 天猫: {{data_times.tmall}}
- 拼多多: {{data_times.pdd}}

### 下次更新建议
建议 {{next_update_time}} 后重新查询，获取最新价格信息。

---

## 附录

### 查询参数
- 搜索关键词: {{search_keyword}}
- 查询时间: {{query_time}}
- 地区设置: {{region}}
- 过滤条件: {{filters}}

### 技术信息
- 数据抓取方式: {{crawler_method}}
- 价格更新频率: {{update_frequency}}
- 报告版本: {{report_version}}

---

**免责声明**: 本报告仅供参考，不构成购买建议。实际购买时请以电商平台实时信息为准。价格可能因促销活动、库存状态等因素随时变化。